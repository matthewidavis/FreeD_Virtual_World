class CameraState:
    def __init__(self):
        self.x = 0      # Fixed position
        self.y = -10    # Fixed distance back
        self.z = 2      # Eye level
        self.pan = 0
        self.tilt = 0
        self.zoom = 0

    def update_from_freed(self, pan, tilt, zoom=0):
        self.pan = pan
        self.tilt = tilt
        self.zoom = zoom  # (optional – placeholder if you decide to scale FOV)

shared_camera = CameraState()
