from direct.showbase.ShowBase import ShowBase
from panda3d.core import Filename, AmbientLight, DirectionalLight, LVector3, Vec3, loadPrcFileData, Loader
loadPrcFileData('', 'window-title FreeD Virtual Viewer')
loadPrcFileData('', 'win-size 1280 720')
import os
from camera_state import shared_camera
from direct.task import Task
from freed_listener import start_freed_listener

class ViewerApp(ShowBase):
    def __init__(self):
        super().__init__()

        self.model_path = os.path.join("scenes")

        # Automatically find the first supported scene file
        model_path = None
        for file in os.listdir(self.model_path):
            ext = os.path.splitext(file)[1].lower()
            if ext in [".obj", ".bam", ".glb"]:
                model_path = os.path.join(self.model_path, file)
                break

        if not model_path:
            print("No supported scene file found in the 'scenes' directory.")
            print("Files in scenes directory:", os.listdir(self.model_path))
            raise FileNotFoundError("No .obj, .bam, or .glb file found in 'scenes'.")

        # Ensure materials load for OBJ
        if model_path.endswith(".obj"):
            self.loader.loadModel(Filename.fromOsSpecific(model_path))  # Preload
            mtl_path = model_path.replace(".obj", ".mtl")
            if os.path.exists(mtl_path):
                print(f"Found .mtl file: {mtl_path}")
            else:
                print("Warning: No .mtl file found, materials may be missing")

        # Load model
        self.scene = self.loader.loadModel(Filename.fromOsSpecific(model_path))
        self.scene.reparentTo(self.render)
        self.scene.setScale(1, 1, 1)
        self.scene.setPos(0, 0, 0)

        # Lighting setup
        ambient = AmbientLight("ambient")
        ambient.setColor((0.4, 0.4, 0.4, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        directional = DirectionalLight("dirlight")
        directional.setDirection(LVector3(-1, -1, -2))
        directional.setColor((0.8, 0.8, 0.8, 1))
        self.render.setLight(self.render.attachNewNode(directional))

        # Disable default camera control
        self.disableMouse()

        # Add task to update camera position and orientation
        self.taskMgr.add(self.update_camera_task, "UpdateCamera")

    def update_camera_task(self, task):
        # Apply scaled movement to reduce sensitivity
        self.camera.setPos(shared_camera.x, shared_camera.y, shared_camera.z)

        # Smooth transition for HPR using basic easing
        current_hpr = self.camera.getHpr()
        target_hpr = Vec3(shared_camera.pan * 0.25, shared_camera.tilt * 0.25, 0)
        new_hpr = current_hpr + (target_hpr - current_hpr) * 0.1
        self.camera.setHpr(new_hpr)

        # Normalize zoom using FreeD range: 0x000000 to 0x400000
        zoom_min_raw = 0x000000
        zoom_max_raw = 0x400000

        clamped_zoom = max(min(shared_camera.zoom, zoom_max_raw), zoom_min_raw)

        # Map to real FoV range: 60.7° (wide) to 3.5° (tele)
        min_fov = 3.5
        max_fov = 60.7

        zoom_ratio = (clamped_zoom - zoom_min_raw) / (zoom_max_raw - zoom_min_raw)
        fov = max_fov - zoom_ratio * (max_fov - min_fov)
        self.camLens.setFov(fov)

        print(f"[CAMERA] Pos: {self.camera.getPos()}, HPR: {self.camera.getHpr()}, Simulated FoV: {fov:.2f}°")
        return Task.cont

def load_scene():
    start_freed_listener(port=19148)
    app = ViewerApp()
    app.run()
