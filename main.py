import eventlet
eventlet.monkey_patch()

import uuid
from datetime import datetime
from flask import Flask, request, session, render_template
from flask_socketio import SocketIO, send

from access_logger import AccessLogger
from frame_provider import FrameProviderScreenRegion, FrameProviderCamera

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a94652aa97c7211ba8954dd15a3cf838'

socketio = SocketIO(app)

access_logger = AccessLogger()  # Instancia global

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
    return render_template('index.html')

@socketio.on('message')
def handle_message(msg):
    print(f"Mensaje recibido: {msg}")
    send(f"Eco: {msg}")
    #send(f"Eco: {msg}", broadcast=True)

def broadcast_frame(frame_provider, fps=20):
    """Función para enviar frames en un hilo separado."""
    while True:
        frame = frame_provider.get_frame()
        socketio.emit('frame', frame)
        socketio.sleep(1 / fps)

if __name__ == '__main__':
    #frame_provider = FrameProviderScreenRegion(monitor_index=1, fps=60, default_image_path="logo.png")
    frame_provider = FrameProviderCamera(device_index=1, width=1280, height=720, default_image_path="logo.png")
    
    socketio.start_background_task(broadcast_frame, frame_provider=frame_provider, fps=20)

    #socketio.run(app, host='0.0.0.0', port=5000)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
