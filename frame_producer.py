import threading
import time

class FrameProducer:
    def __init__(self, frameGenerator):
        self._actual_frame = None
        self._lock = threading.Lock()
        self._frameGenerator = frameGenerator
        self._running = True
        self._thread = threading.Thread(target=self._update_frame_loop, daemon=True)
        self._thread.start()

    def _update_frame_loop(self):
        while self._running:
            new_frame = self._generate_frame()
            with self._lock:
                self._actual_frame = new_frame
            time.sleep(1/60)

    def _generate_frame(self):
        return self._frameGenerator.get_frame_bytes()
    
    def get_actual_frame(self):
        with self._lock:
            return self._actual_frame

    def stop(self):
        self._running = False
        self._thread.join()
    
    def restar(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._update_frame_loop, daemon=True)
            self._thread.start()
