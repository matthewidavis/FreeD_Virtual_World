from panda3d.core import LVector3, AmbientLight, DirectionalLight, PointLight
from panda3d.core import TextureStage, Texture
from direct.showbase.ShowBase import ShowBase
import random

class DetailedWorld(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()
        self.camera.setPos(0, -60, 20)
        self.camera.lookAt(0, 0, 10)

        self.setup_lights()
        self.build_room()
        self.add_furniture()
        self.add_decor()

    def setup_lights(self):
        ambient = AmbientLight("ambient")
        ambient.setColor((0.3, 0.3, 0.3, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        dlight = DirectionalLight("dlight")
        dlight.setColor((0.8, 0.8, 0.7, 1))
        dlight.setDirection(LVector3(-1, -1, -2))
        self.render.setLight(self.render.attachNewNode(dlight))

        plight = PointLight("plight")
        plight.setColor((1, 1, 0.9, 1))
        plight_np = self.render.attachNewNode(plight)
        plight_np.setPos(0, 0, 25)
        self.render.setLight(plight_np)

    def build_room(self):
        # Floor
        floor = self.loader.loadModel("models/box")
        floor.setScale(40, 40, 0.1)
        floor.setPos(0, 0, 0)
        floor.setColor(0.5, 0.5, 0.5, 1)
        floor.reparentTo(self.render)

        # Walls
        for x, y, scale_x, scale_y, pos in [
            (-40, 0, 0.1, 80, (0, 0, 10)),
            (40, 0, 0.1, 80, (0, 0, 10)),
            (0, 40, 80, 0.1, (0, 0, 10)),
            (0, -40, 80, 0.1, (0, 0, 10)),
        ]:
            wall = self.loader.loadModel("models/box")
            wall.setScale(scale_x, scale_y, 20)
            wall.setPos(x, y, pos[2])
            wall.setColor(0.8, 0.85, 0.9, 1)
            wall.reparentTo(self.render)

        # Ceiling
        ceiling = self.loader.loadModel("models/box")
        ceiling.setScale(40, 40, 0.1)
        ceiling.setPos(0, 0, 20)
        ceiling.setColor(0.7, 0.7, 0.75, 1)
        ceiling.reparentTo(self.render)

    def add_furniture(self):
        for i in range(12):
            x, y = random.uniform(-30, 30), random.uniform(-30, 30)
            z = 0.5
            scale_x = random.uniform(1, 2)
            scale_y = random.uniform(1, 2)
            scale_z = random.uniform(1, 3)
            box = self.loader.loadModel("models/box")
            box.setScale(scale_x, scale_y, scale_z)
            box.setPos(x, y, z)
            box.setColor(random.uniform(0.4, 0.8), random.uniform(0.3, 0.7), random.uniform(0.3, 0.7), 1)
            box.reparentTo(self.render)

    def add_decor(self):
        for i in range(6):
            column = self.loader.loadModel("models/box")
            col_x, col_y = random.choice([(-35, 35)]), random.uniform(-30, 30)
            column.setScale(0.5, 0.5, 12)
            column.setPos(col_x, col_y, 6)
            column.setColor(0.6, 0.6, 0.6, 1)
            column.reparentTo(self.render)

        for i in range(10):
            lamp = self.loader.loadModel("models/box")
            lamp.setScale(0.3, 0.3, 1.2)
            lamp.setPos(random.uniform(-30, 30), random.uniform(-30, 30), 20)
            lamp.setColor(1.0, 0.95, 0.6, 1)
            lamp.reparentTo(self.render)

app = DetailedWorld()
app.run()
