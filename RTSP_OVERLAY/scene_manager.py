import cv2
import numpy as np
import os
import requests
import threading
import time
from panda3d.core import Filename, AmbientLight, DirectionalLight, LVector3, Vec3, loadPrcFileData, Loader, Texture, CardMaker, TransparencyAttrib
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import DirectEntry, DirectButton, OnscreenText
from camera_state import shared_camera
from freed_listener import start_freed_listener
from rtsp_stream import RTSPStream
from shared_state import shared_state

loadPrcFileData('', 'window-title FreeD Virtual Viewer')
loadPrcFileData('', 'win-size 1280 720')

class ViewerApp(ShowBase):
    def __init__(self):
        super().__init__()

        self.connected = False
        self.rtsp_stream = None
        self.bbox_api = None
        self.texture = Texture()
        self.last_bbox = None

        # Load scene
        model_path = next((os.path.join("scenes", f) for f in os.listdir("scenes")
                          if os.path.splitext(f)[1].lower() in [".obj", ".bam", ".glb"]), None)
        if not model_path:
            raise FileNotFoundError("No scene file found.")
        self.scene = self.loader.loadModel(Filename.fromOsSpecific(model_path))
        self.scene.reparentTo(self.render)
        self.scene.setScale(1, 1, 1)
        self.scene.setPos(0, 0, 0)

        # Lighting
        ambient = AmbientLight("ambient")
        ambient.setColor((0.4, 0.4, 0.4, 1))
        self.render.setLight(self.render.attachNewNode(ambient))
        directional = DirectionalLight("dirlight")
        directional.setDirection(LVector3(-1, -1, -2))
        directional.setColor((0.8, 0.8, 0.8, 1))
        self.render.setLight(self.render.attachNewNode(directional))

        self.disableMouse()

        # UI Elements
        self.ip_entry = DirectEntry(text="", scale=0.05, pos=(-0.5, 0, 0.9),
                                    initialText="192.168.12.8", numLines=1, focus=0)
        self.connect_btn = DirectButton(text="Connect", scale=0.05, pos=(0.3, 0, 0.9),
                                        command=self.connect)
        self.disconnect_btn = DirectButton(text="Disconnect", scale=0.05, pos=(0.6, 0, 0.9),
                                           command=self.disconnect)

        self.status_text = OnscreenText(text="Disconnected", pos=(0.0, 0.8), scale=0.05)

        self.card = None

    def connect(self):
        ip = self.ip_entry.get().strip()
        if not ip:
            return
        self.status_text.setText(f"Connecting to {ip}...")

        self.rtsp_stream = RTSPStream(f"rtsp://{ip}:554/2")
        self.bbox_api = f"http://{ip}/cgi-bin/param.cgi?get_tally_status"
        start_freed_listener(port=19148)

        cm = CardMaker("video_card")
        cm.setFrameFullscreenQuad()
        self.card = self.render2d.attachNewNode(cm.generate())
        self.card.setTransparency(TransparencyAttrib.MAlpha)
        self.card.setTexture(self.texture)

        self.taskMgr.add(self.update_overlay_task, "UpdateOverlay")
        self.taskMgr.add(self.update_camera_task, "UpdateCamera")
        self.connected = True
        self.status_text.setText(f"Connected to {ip}")

    def disconnect(self):
        self.connected = False
        self.status_text.setText("Disconnected")
        self.rtsp_stream = None
        self.bbox_api = None
        self.last_bbox = None
        if self.card:
            self.card.removeNode()
            self.card = None

    def fetch_bbox(self):
        try:
            response = requests.get(self.bbox_api, timeout=0.3)
            if response.ok:
                data = response.json()
                if data["data"]["objs"]:
                    obj = data["data"]["objs"][0]
                    return obj["X"], obj["Y"], obj["X"] + obj["Width"], obj["Y"] + obj["Height"]
        except Exception as e:
            print("[BBOX] Error:", e)
        return None

    def smooth_bbox(self, new_bbox, alpha=0.2):
        if self.last_bbox is None:
            self.last_bbox = new_bbox
        smoothed = tuple(
            int((1 - alpha) * old + alpha * new)
            for old, new in zip(self.last_bbox, new_bbox)
        )
        self.last_bbox = smoothed
        return smoothed

    def update_overlay_task(self, task):
        if not self.connected or not self.rtsp_stream:
            return Task.cont

        frame = self.rtsp_stream.get_frame()
        if frame is None:
            return Task.cont

        bbox = self.fetch_bbox()
        if bbox:
            x1, y1, x2, y2 = self.smooth_bbox(bbox)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
            if x2 > x1 and y2 > y1:
                cropped = frame[y1:y2, x1:x2]

                hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
                lower_green = np.array([35, 40, 40])
                upper_green = np.array([85, 255, 255])
                mask = cv2.inRange(hsv, lower_green, upper_green)

                if np.mean(mask) < 5:
                    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                    _, alpha = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
                else:
                    alpha = cv2.bitwise_not(mask)

                rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                bgra = cv2.merge((rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2], alpha))

                win_w, win_h = self.win.getXSize(), self.win.getYSize()
                target_h = win_h // 2
                scale = target_h / bgra.shape[0]
                new_w = int(bgra.shape[1] * scale)
                resized = cv2.resize(bgra, (new_w, target_h))

                padded = np.zeros((win_h, win_w, 4), dtype=np.uint8)
                offset_x = (win_w - new_w) // 2
                offset_y = (win_h - target_h) // 2
                padded[offset_y:offset_y + target_h, offset_x:offset_x + new_w] = resized

                flipped = cv2.flip(padded, 0)

                if not self.texture.getXSize():
                    self.texture.setup2dTexture(win_w, win_h, Texture.T_unsigned_byte, Texture.F_rgba)
                self.texture.setRamImageAs(flipped.flatten(), "RGBA")

        return Task.cont

    def update_camera_task(self, task):
        if not self.connected:
            return Task.cont

        # Handle idle animation
        if shared_camera.should_idle():
            elapsed = time.time() - shared_camera.last_idle_start
            shared_camera.pan = 20 * np.sin(elapsed * 0.5)
            shared_camera.tilt = 5 * np.cos(elapsed * 0.3)

        self.camera.setPos(shared_camera.x, shared_camera.y, shared_camera.z)
        current_hpr = self.camera.getHpr()
        target_hpr = Vec3(shared_camera.pan * 0.25, shared_camera.tilt * 0.25, 0)
        new_hpr = current_hpr + (target_hpr - current_hpr) * 0.1
        self.camera.setHpr(new_hpr)

        zoom_min_raw = 0x000000
        zoom_max_raw = 0x400000
        clamped_zoom = max(min(shared_camera.zoom, zoom_max_raw), zoom_min_raw)

        min_fov = 3.5
        max_fov = 60.7
        zoom_ratio = (clamped_zoom - zoom_min_raw) / (zoom_max_raw - zoom_min_raw)
        fov = max_fov - zoom_ratio * (max_fov - min_fov)
        self.camLens.setFov(fov)

        return Task.cont

def load_scene():
    start_freed_listener(port=19148)
    app = ViewerApp()
    app.run()
