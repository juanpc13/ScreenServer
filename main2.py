import time
import cv2
import threading
from flask import Flask, Response

app = Flask(__name__)

last_frame = None
last_frame_lock = threading.Lock()
frame_thread_started = False

def frame_updater():
    global last_frame
    while True:
        cap = cv2.VideoCapture("udp://@:5000", cv2.CAP_FFMPEG)
        # Reduce buffer size (may help with delay)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        while True:
            success, frame = cap.read()
            if success:
                with last_frame_lock:
                    last_frame = frame
            else:
                cap.release()
                break

def generate_frames():
    global last_frame, frame_thread_started

    if not frame_thread_started:
        threading.Thread(target=frame_updater, daemon=True).start()
        frame_thread_started = True

    while True:
        frame_bytes = None
        with last_frame_lock:
            if last_frame is not None:
                ret, buffer = cv2.imencode('.jpg', last_frame)
                frame_bytes = buffer.tobytes()
        if frame_bytes is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(1/30)

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

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
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
