from direct.showbase.ShowBase import ShowBase
from panda3d.core import Filename, AmbientLight, DirectionalLight, LVector3, Vec3, loadPrcFileData, TextNode
loadPrcFileData('', 'window-title FreeDumb World')
loadPrcFileData('', 'win-size 1280 720')
from direct.gui.DirectGui import DirectEntry, DirectButton, DirectFrame
import os
import socket
import math
from camera_state import shared_camera
from direct.task import Task
from freed_listener import start_freed_listener, stop_freed_listener

class ViewerApp(ShowBase):
    def __init__(self):
        super().__init__()

        self.connected = False
        self.ip_address = "192.168.100.88"
        self.angle = 0.0

        self.model_path = os.path.join("scenes")
        self.setup_scene()
        self.setup_lights()
        self.setup_controls()
        self.disableMouse()
        self.taskMgr.add(self.update_camera_task, "UpdateCamera")

    def setup_scene(self):
        model_path = None
        for file in os.listdir(self.model_path):
            if file.lower().endswith((".obj", ".bam", ".glb")):
                model_path = os.path.join(self.model_path, file)
                break
        if not model_path:
            raise FileNotFoundError("No model found in scenes/")
        self.scene = self.loader.loadModel(Filename.fromOsSpecific(model_path))
        self.scene.reparentTo(self.render)
        self.scene.setScale(1, 1, 1)
        self.scene.setPos(0, 0, 0)

    def setup_lights(self):
        ambient = AmbientLight("ambient")
        ambient.setColor((0.4, 0.4, 0.4, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        directional = DirectionalLight("dirlight")
        directional.setDirection(LVector3(-1, -1, -2))
        directional.setColor((0.8, 0.8, 0.8, 1))
        self.render.setLight(self.render.attachNewNode(directional))

    def setup_controls(self):
        self.menu_frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.1, 1),
            frameSize=(-1.5, 1.5, -0.1, 0.1),
            pos=(0, 0, 0.92)
        )

        # Left-aligned layout
        base_x = -1.35
        spacing = 0.02

        self.ip_input = DirectEntry(
            text="",
            scale=0.045,
            pos=(base_x, 0, -0.035),
            initialText=self.ip_address,
            numLines=1,
            focus=0,
            parent=self.menu_frame
        )

        self.toggle_button = DirectButton(
            text="CONNECT",
            scale=0.06,  # good vertical and text size
            pos=(base_x + 0.65 + spacing, 0, -0.035),
            pad=(0.7, 0.15),  # (horizontal, vertical) padding
            command=self.toggle_connection,
            parent=self.menu_frame
        )

    def toggle_connection(self):
        ip = self.ip_input.get()
        self.ip_address = ip

        if self.connected:
            # DISCONNECT
            stop_freed_listener()
            self.send_hex_command("D0F5007BFF")
            self.send_hex_command("A4F500A7FF")
            self.toggle_button["text"] = "CONNECT"
            self.connected = False
            print("[FreeD] Disconnected and STOP commands sent.")
        else:
            # CONNECT
            self.send_hex_command("D0F5007BFF")
            self.send_hex_command("A4F500A7FF")
            self.send_hex_command("D0F5017AFF")
            start_freed_listener(port=19148)
            self.toggle_button["text"] = "DISCONNECT"
            self.connected = True
            print("[FreeD] Connected and START command sent.")

    def send_hex_command(self, hex_str):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(bytes.fromhex(hex_str), (self.ip_address, 1259))
            sock.close()
            print(f"Sent {hex_str} to {self.ip_address}:1259")
        except Exception as e:
            print(f"Error sending command: {e}")

    def update_camera_task(self, task):
        if self.connected:
            self.camera.setPos(shared_camera.x, shared_camera.y, shared_camera.z)
            target_hpr = Vec3(shared_camera.pan * 0.25, shared_camera.tilt * 0.25, 0)
        else:
            self.angle += 0.01
            shared_camera.zoom = int((0x400000 // 2) * (1 + math.sin(task.time)))
            target_hpr = Vec3(task.time * 10 % 360, 10 * math.sin(task.time), 0)
            self.camera.setPos(5 * math.sin(self.angle), -5 * math.cos(self.angle), 1)

        current_hpr = self.camera.getHpr()
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
    app = ViewerApp()
    app.run()
