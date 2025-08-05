from abc import ABC, abstractmethod
import threading
import time
import mss
import cv2
import numpy as np

class FrameProvider(ABC):
    def __init__(self, default_image_path=None):
        self.last_frame = None
        self.lock = threading.Lock()
        self.running = True
        self.default_frame = None
        if default_image_path:
            img = cv2.imread(default_image_path)
            if img is not None:
                _, buffer = cv2.imencode('.jpg', img)
                self.default_frame = buffer.tobytes()
        self.thread = threading.Thread(target=self._frame_producer, daemon=True)
        self.thread.start()

    @abstractmethod
    def _frame_producer(self):
        pass

    @abstractmethod
    def get_frame(self):
        pass

    def stop(self):
        self.running = False
        self.thread.join()

# FrameProviderCamera implementa su propio _frame_producer
class FrameProviderCamera(FrameProvider):
    def __init__(self, device_index=1, width=1280, height=720, default_image_path=None):
        self.cap = cv2.VideoCapture(device_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara. Asegúrate de que esté activa.")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        super().__init__(default_image_path=default_image_path)

    def _frame_producer(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Error al capturar el frame de la cámara.")
                continue
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            _, buffer = cv2.imencode('.jpg', frame, encode_param)
            frame_bytes = buffer.tobytes()
            with self.lock:
                self.last_frame = frame_bytes
            time.sleep(1 / 30)  # Puedes ajustar el FPS aquí

    def get_frame(self):
        with self.lock:
            if not self.running and self.default_frame is not None:
                return self.default_frame
            return self.last_frame

# FrameProviderScreenRegion implementa su propio _frame_producer
class FrameProviderScreenRegion(FrameProvider):
    def __init__(self, monitor_index=2, fps=60, default_image_path=None):
        self.monitor_index = monitor_index
        self.region = mss.mss().monitors[monitor_index]
        self.fps = fps
        super().__init__(default_image_path=default_image_path)

    def _frame_producer(self):
        with mss.mss() as sct:
            while self.running:
                img = sct.grab(self.region)
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                with self.lock:
                    self.last_frame = frame_bytes
                time.sleep(1 / self.fps)

    def get_frame(self):
        with self.lock:
            if not self.running and self.default_frame is not None:
                return self.default_frame
            return self.last_frame

    def set_region(self, region):
        self.region = region

    def restar(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._frame_producer, daemon=True)
            self.thread.start()