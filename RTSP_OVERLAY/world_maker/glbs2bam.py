from panda3d.core import loadPrcFileData, Filename, NodePath
from direct.showbase.ShowBase import ShowBase
import os, sys

# Run offscreen
loadPrcFileData('', 'window-type offscreen')
loadPrcFileData('', 'audio-library-name null')

class GlbSceneBuilder(ShowBase):
    def __init__(self, glb_dir, output_bam):
        super().__init__()
        self.disableMouse()
        self.scene_root = NodePath("scene_root")
        self.build_scene(glb_dir)
        self.export_bam(output_bam)

    def build_scene(self, glb_dir):
        print(f"📦 Loading assets from: {glb_dir}")
        glb_files = [f for f in os.listdir(glb_dir) if f.endswith(".glb")]

        if not glb_files:
            print("⚠️ No .glb files found!")
            sys.exit(1)

        spacing = 5  # space between objects
        for i, fname in enumerate(sorted(glb_files)):
            path = Filename.fromOsSpecific(os.path.join(glb_dir, fname)).getFullpath()
            model = self.loader.loadModel(path)
            if not model:
                print(f"❌ Failed to load {fname}")
                continue

            # Auto-position to avoid overlap (grid pattern)
            row = i // 5
            col = i % 5
            model.setPos(col * spacing, row * spacing, 0)
            model.reparentTo(self.scene_root)
            print(f"✅ Loaded: {fname}")

    def export_bam(self, output_path):
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        self.scene_root.writeBamFile(output_path)
        print(f"\n✅ Exported combined scene to: {output_path}")

# Edit these paths as needed
glb_folder = "./GLB format"         # Unzipped directory
output_bam = "scenes/combined_world.bam"

GlbSceneBuilder(glb_folder, output_bam)
