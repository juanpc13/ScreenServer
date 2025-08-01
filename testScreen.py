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

# Región de captura (inicialmente None)
monitor_region = None

# Flag de actualización
selection_done = threading.Event()

# ---------------------------
# Función para seleccionar región
# ---------------------------
def select_region():
    def on_mouse_down(event):
        nonlocal start_x, start_y
        start_x, start_y = event.x, event.y

    def on_mouse_drag(event):
        nonlocal rect_id
        canvas.delete(rect_id)
        rect_id = canvas.create_rectangle(start_x, start_y, event.x, event.y, outline='red')

    def on_mouse_up(event):
        global monitor_region
        x1, y1 = start_x, start_y
        x2, y2 = event.x, event.y
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        monitor_region = {
            "left": x1,
            "top": y1,
            "width": x2 - x1,
            "height": y2 - y1
        }
        root.destroy()
        selection_done.set()

    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.3)
    root.attributes("-topmost", True)
    canvas = tk.Canvas(root, cursor="cross")
    canvas.pack(fill=tk.BOTH, expand=True)

    start_x = start_y = 0
    rect_id = None

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

    root.mainloop()

# ---------------------------
# Captura de frames para streaming (con frame global)
# ---------------------------
last_frame = None
last_frame_lock = threading.Lock()

# create a default frame de la imagen que en esta raiz llamada logo.png
default_frame = cv2.imread('logo.png')
default_frame_bytes = cv2.imencode('.jpg', default_frame)[1].tobytes()

def frame_producer():
    global monitor_region, last_frame, default_frame
    with mss.mss() as sct:
        while True:
            if monitor_region:
                img = sct.grab(monitor_region)
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                with last_frame_lock:
                    last_frame = frame_bytes
                time.sleep(1 / 60)
            else:
                time.sleep(0.1)
                with last_frame_lock:
                    last_frame = default_frame_bytes

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
# Combinación de teclas para iniciar selección
# ---------------------------
def listen_for_hotkey():
    def on_press(key):
        global monitor_region
        if key == keyboard.Key.f2:
            print("🔴 Selección iniciada... Arrastra para seleccionar región.")
            select_region()
        elif key == keyboard.Key.f8:
            monitor_region = None
            print("🟡 Región limpiada. Mostrando imagen por defecto.")

    def on_release(key):
        if key in pressed_keys:
            pressed_keys.remove(key)

    pressed_keys = set()
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# ---------------------------
# Main
# ---------------------------
if __name__ == '__main__':
    # Iniciar el hilo productor de frames
    threading.Thread(target=frame_producer, daemon=True).start()
    
    # Escuchar teclas en un hilo separado
    threading.Thread(target=listen_for_hotkey, daemon=True).start()

    print("✅ Presiona F2 para seleccionar región")
    print("✅ Presiona F8 para limpiar la región y mostrar imagen por defecto")
    print("🌐 Luego abre http://localhost:5000 en tu navegador")    

    # Iniciar servidor con Waitress para producción
    serve(app, host='0.0.0.0', port=5000)
