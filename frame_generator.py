
from abc import ABC, abstractmethod
import cv2
import numpy as np
import mss

class FrameGenerator(ABC):
    @abstractmethod
    def get_frame_bytes(self):
        pass

class FrameGeneratorCamera(FrameGenerator):
    def __init__(self, device_index=1, width=1280, height=720):
        self.cap = cv2.VideoCapture(device_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara. Asegúrate de que esté activa.")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def get_frame_bytes(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Error al capturar el frame de la cámara.")
            return None
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
        _, buffer = cv2.imencode('.jpg', frame, encode_param)
        return buffer.tobytes()

class FrameGeneratorScreenRegion(FrameGenerator):
    def __init__(self, region=None):
        self.sct = mss.mss()
        self.region = region or self.sct.monitors[1]

    def get_frame_bytes(self):
        sct_img = self.sct.grab(self.region)
        img = np.array(sct_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
        _, buffer = cv2.imencode('.jpg', img, encode_param)
        return buffer.tobytes()

    def set_region(self, region):
        self.region = region