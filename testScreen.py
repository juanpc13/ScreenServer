import cv2
import numpy as np
import mss
import time
import threading
from flask import Flask, Response
from pynput import keyboard
import tkinter as tk
from waitress import serve

# Flask app
app = Flask(__name__)

# ---------------------------
# Captura de frames para streaming (con frame global)
# ---------------------------
last_frame = None
last_frame_lock = threading.Lock()

# Camara virtual de OBS u otro dispositivo
# Abrir la cámara virtual de OBS (usualmente es el dispositivo 0 o 1)

# --- Configuración de cámara virtual de OBS u otro dispositivo ---
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("No se pudo abrir la cámara virtual de OBS. Asegúrate de que esté activa.")
    raise SystemExit

# Mejorar calidad: establecer resolución (ajusta estos valores según tu cámara)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


# Task para crear un frame actual
def frame_producer():
    global last_frame, cap
    while True:
        with last_frame_lock:
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar el frame de la cámara.")
                continue
            
            # Convertir a formato JPEG con calidad alta
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]  # 95 es alta calidad
            _, buffer = cv2.imencode('.jpg', frame, encode_param)
            last_frame = buffer.tobytes()
        
        time.sleep(1 / 60)
        

def generate_frames():
    global last_frame
    while True:
        with last_frame_lock:
            frame_bytes = last_frame
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(1 / 32)

# ---------------------------
# Flask endpoints
# ---------------------------
@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Screen Stream</title>
        <style>
            html, body {
                margin: 0;
                padding: 0;
                width: 100vw;
                height: 100vh;
                background: #222;
            }
            img {
                width: 100vw;
                height: 100vh;
                object-fit: contain;
                border-radius: 0;
                box-shadow: none;
                background: #333;
                display: block;
            }
        </style>
    </head>
    <body>
        <img src="/video" alt="Screen Stream" />
    </body>
    </html>
    '''

@app.route('/video')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ---------------------------
# Main
# ---------------------------
if __name__ == '__main__':
    # Iniciar el hilo productor de frames
    threading.Thread(target=frame_producer, daemon=True).start()

    # Seleccionar región de captura
    print("🌐 Luego abre http://localhost:5000 en tu navegador")   

    # Iniciar servidor con Waitress para producción
    serve(app, host='0.0.0.0', port=5000)
