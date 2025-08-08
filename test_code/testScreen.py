from flask import Flask, request, session, jsonify, render_template, Response
from waitress import serve
from datetime import datetime
import uuid

from frame_provider import FrameProviderScreenRegion, FrameProviderCamera  # Asegúrate de que este archivo esté en el mismo directorio
from access_logger import AccessLogger  # Si lo pones en otro archivo, si no, ignora esta línea
from test_code.websocket_server import WebSocketServer

from music_queue import MusicQueue  # Asegúrate de que este archivo esté en el mismo directorio

# Inicializar la cola de música
music_queue = MusicQueue()

# Flask app
app = Flask(__name__)
#md5 juan
app.secret_key = 'a94652aa97c7211ba8954dd15a3cf838'

access_logger = AccessLogger()  # Instancia global

frame_provider = FrameProviderScreenRegion(monitor_index=1, fps=60, default_image_path="logo.png")  # Usa la segunda pantalla
#frame_provider = FrameProviderCamera(device_index=0, width=1280, height=720, default_image_path="logo.png")  # Usa la cámara por defecto
#frame_provider.stop()  # Detener la captura de frames al iniciar

# Iniciar el servidor WebSocket en segundo plano para transmitir los frames
#ws_server = FrameWebSocketServer(frame_provider, host='0.0.0.0', port=8765, fps=20)
ws_server = WebSocketServer(frame_provider=frame_provider, fps=20)  # Instancia del servidor WebSocket
ws_server.add_message_type(b'\x01')  # Tipo de mensaje para texto
ws_server.start_in_thread()  # Iniciar el servidor WebSocket

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    session_id = session['session_id']

    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Registrar acceso usando la clase
    access_logger.log_access(session_id, ip, user_agent, now)
    # Imprimir en consola
    print(f"[{now}] GET / from {ip} | Session: {session_id} | User-Agent: {user_agent}")

    # Renderizar una plantilla HTML simple
    return render_template('index.html')

@app.route('/user_aliases')
def user_aliases():
    # Supón que access_logger tiene un método get_user_aliases() que devuelve una lista o dict
    aliases = access_logger.get_all_user_aliases()  # Debes implementar este método en AccessLogger
    return jsonify(aliases)

@app.route('/access_history')
def access_history():
    # Supón que access_logger tiene un método get_access_history() que devuelve una lista de accesos
    history = access_logger.get_access_history(limit=20)  # Devuelve los últimos 20 accesos
    return jsonify(history)

@app.route('/set_alias', methods=['POST'])
def set_alias():
    if 'session_id' not in session:
        return jsonify({"error": "No session found"}), 400
    data = request.get_json()
    alias = data.get('alias')
    if not alias:
        return jsonify({"error": "Alias is required"}), 400
    session_id = session['session_id']
    access_logger.set_user_alias(session_id, alias)
    return jsonify({"success": True, "session_id": session_id, "alias": alias})

# session_id is the metadata for the music queue
@app.route('/music_queue', methods=['POST'])
def add_to_music_queue():
    data = request.get_json()
    song = data.get('song')
    if 'session_id' not in session:
        return jsonify({"error": "No session found"}), 400
    session_id = session['session_id']
    item_id = music_queue.agregar(song, metadata=session_id)
    return jsonify({"success": True, "item_id": item_id})

print("Flask app running on http://localhost:5000")
serve(app, host='0.0.0.0', port=5000)