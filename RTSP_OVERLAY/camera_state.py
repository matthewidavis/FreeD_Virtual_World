import time

class CameraState:
    def __init__(self):
        self.x = 0
        self.y = -10
        self.z = 2
        self.pan = 0
        self.tilt = 0
        self.zoom = 0

        self._raw_pan = 0
        self._raw_tilt = 0
        self._raw_zoom = 0

        self.last_freed_time = 0
        self.last_idle_start = time.time()

        self.tilt_buffer = []
        self.tilt_offset = 0
        self.collecting_tilt = False
        self.tilt_start_time = None
        self.auto_calibrate_tilt = True

    def should_idle(self, timeout=2.0):
        idle = (time.time() - self.last_freed_time) > timeout
        if idle and (time.time() - self.last_idle_start > timeout):
            self.last_idle_start = time.time()  # Reset to avoid drift
        return idle

    def mark_freed_received(self):
        self.last_freed_time = time.time()
        self.last_idle_start = time.time()

        if self.auto_calibrate_tilt:
            now = time.time()

            if not self.collecting_tilt:
                if self.tilt_start_time is None:
                    self.tilt_start_time = now
                elif now - self.tilt_start_time > 3:
                    self.collecting_tilt = True
                    self.tilt_buffer = []
                    print("[Tilt Calibration] Starting tilt capture window...")

            elif self.collecting_tilt:
                self.tilt_buffer.append(self._raw_tilt)
                if now - self.tilt_start_time > 8:
                    self.tilt_offset = sorted(self.tilt_buffer)[len(self.tilt_buffer) // 2]
                    print(f"[Tilt Calibration] Median tilt offset set to {self.tilt_offset:.2f}°")
                    self.collecting_tilt = False
                    self.tilt_start_time = None

    def update_from_freed(self, pan, tilt, zoom=0):
        self._raw_pan = pan
        self._raw_tilt = tilt
        self._raw_zoom = zoom

        if self.auto_calibrate_tilt:
            tilt -= self.tilt_offset

        pan = max(min(pan, 180), -180)
        tilt = max(min(tilt, 90), -30)

        pan = round(pan * 4) / 4
        tilt = round(tilt * 2) / 2

        zoom_ratio = (zoom - 0x000000) / float(0x400000)
        zoom_ratio = max(0.0, min(1.0, zoom_ratio))

        smoothing_pan = 0.15
        smoothing_tilt = max(0.05, 0.25 - zoom_ratio * 0.2)
        smoothing_zoom = 0.15

        self.pan = (1 - smoothing_pan) * self.pan + smoothing_pan * pan
        self.tilt = (1 - smoothing_tilt) * self.tilt + smoothing_tilt * tilt
        self.zoom = (1 - smoothing_zoom) * self.zoom + smoothing_zoom * zoom


shared_camera = CameraState()
