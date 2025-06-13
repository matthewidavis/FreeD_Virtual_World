import cv2
import threading
import time

class RTSPStream:
    def __init__(self, url, reconnect_delay=5):
        self.url = url
        self.cap = None
        self.frame = None
        self.lock = threading.Lock()
        self.running = True
        self.reconnect_delay = reconnect_delay

        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()

    def _connect(self):
        print(f"[RTSP] Connecting to {self.url}...")
        cap = cv2.VideoCapture(self.url)
        if not cap.isOpened():
            print(f"[RTSP] Failed to connect to {self.url}")
            return None
        print(f"[RTSP] Connected.")
        return cap

    def _reader(self):
        while self.running:
            if self.cap is None or not self.cap.isOpened():
                self.cap = self._connect()
                if self.cap is None:
                    time.sleep(self.reconnect_delay)
                    continue

            ret, frame = self.cap.read()
            if not ret:
                print("[RTSP] Frame grab failed. Reconnecting...")
                self.cap.release()
                self.cap = None
                time.sleep(self.reconnect_delay)
                continue

            with self.lock:
                self.frame = frame

    def get_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        print("[RTSP] Stopping stream...")
        self.running = False
        if self.cap:
            self.cap.release()
