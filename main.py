import os
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
import uuid

app = Flask(__name__)
app.secret_key = "clave_super_secreta"
socketio = SocketIO(app)

# Detectar entorno (default: development)
ENV = os.getenv("FLASK_ENV", "development").lower()
DEBUG_MODE = ENV != "production"  # True si no es producción

queue = []

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["username"] = request.form["username"]
        session["user_id"] = str(uuid.uuid4())[:8]
        return redirect(url_for("index"))
    if "username" in session:
        return redirect(url_for("index"))
    return render_template('login_template.html')

@app.route("/cola")
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template('index.html', username=session["username"])

# Endpoint oculto para eliminar posición específica
@app.route("/admin/remove/<int:pos>/<secret>")
def remove_song(pos, secret):
    if secret == "clave123":  # Cambia esta clave para seguridad
        if 0 <= pos < len(queue):
            removed = queue.pop(pos)
            socketio.emit("update_queue", queue)
            return f"Canción '{removed['song']}' de {removed['artist']} eliminada."
        return "Posición inválida."
    return "Acceso denegado."

@socketio.on("get_queue")
def send_queue():
    emit("update_queue", queue)

@socketio.on("new_song")
def add_song(data):
    song_name = data.get("song")
    artist_name = data.get("artist")
    if song_name and artist_name:
        queue.append({
            "song": song_name,
            "artist": artist_name,
            "user": session["username"]
        })
        socketio.emit("update_queue", queue)

import cv2
def broadcast_frame(video_source="udp://@:5000", fps=20):
    """Función para enviar frames en un hilo separado."""
    while True:
        try:
            cap = cv2.VideoCapture(video_source)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            while True:
                success, frame = cap.read()
                if success:
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
                    _, buffer = cv2.imencode('.jpg', frame, encode_param)
                    frame_bytes = buffer.tobytes()
                    socketio.emit("frame", frame_bytes)
                    socketio.sleep(1 / fps)
                else:
                    cap.release()
                    break
        except Exception as e:
            print(f"Error en la captura de video: {e}")

if __name__ == "__main__":
    # Iniciar tarea en segundo plano para el frame
    socketio.start_background_task(broadcast_frame, video_source="udp://@:5000", fps=20)

    if ENV == "production":
        try:
            import eventlet
            socketio.run(app, debug=DEBUG_MODE, host="0.0.0.0")
        except ImportError:
            print("Eventlet not installed, falling back to default server.")
            socketio.run(app, debug=DEBUG_MODE, host="0.0.0.0", allow_unsafe_werkzeug=True)
    else:
        socketio.run(app, debug=DEBUG_MODE, host="0.0.0.0", allow_unsafe_werkzeug=True)
        