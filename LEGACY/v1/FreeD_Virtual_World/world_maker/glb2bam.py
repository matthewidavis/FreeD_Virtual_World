from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase
import sys

loadPrcFileData('', 'window-type offscreen')

class ModelConverter(ShowBase):
    def __init__(self):
        super().__init__()
        model = self.loader.loadModel("your_file.glb")
        model.flattenStrong()
        model.writeBamFile("scenes/your_file.bam")
        print("✅ Done.")
        sys.exit()

ModelConverter()
