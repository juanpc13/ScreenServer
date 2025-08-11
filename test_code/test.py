import cv2
import time

def open_stream():
    return cv2.VideoCapture("udp://@:5000", cv2.CAP_FFMPEG)

cap = open_stream()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Stream timeout. Reconnecting...")
        cap.release()
        time.sleep(2)  # Espera antes de reconectar
        cap = open_stream()
        continue
    cv2.imshow("Stream OBS VirtualCam", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
