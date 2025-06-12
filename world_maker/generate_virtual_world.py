import bpy
import os

# Clear existing scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Correct and clean absolute path for GLB export
output_path = r"C:\Users\Matt\Downloads\freed_virtual_viewer\scenes\virtual_world.glb"

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
bsdf = ground_mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.2, 0.6, 0.2, 1)
ground.data.materials.append(ground_mat)

# Add buildings with camera buffer zone cleared
for i in range(-3, 4):
    for j in range(-3, 4):
        x, y = i * 5, j * 5
        if -2 <= x <= 2 and -12 <= y <= -6:
            continue  # Skip near-camera zone
        if (i + j) % 2 == 0:
            bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, 1))
            cube = bpy.context.active_object
            cube.scale[2] = 2
            cube.location[2] = 2

            mat = bpy.data.materials.new(name=f"BuildingMaterial_{i}_{j}")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1)
            cube.data.materials.append(mat)

# Add trees
for x in range(-20, 25, 10):
    for y in range(-20, 25, 10):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=2, location=(x, y, 1))
        trunk = bpy.context.active_object
        trunk_mat = bpy.data.materials.new(name="TrunkMaterial")
        trunk_mat.use_nodes = True
        bsdf = trunk_mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (0.4, 0.25, 0.1, 1)
        trunk.data.materials.append(trunk_mat)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(x, y, 2.5))
        leaves = bpy.context.active_object
        leaves_mat = bpy.data.materials.new(name="LeavesMaterial")
        leaves_mat.use_nodes = True
        bsdf = leaves_mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (0.1, 0.5, 0.1, 1)
        leaves.data.materials.append(leaves_mat)

# Lighting
bpy.ops.object.light_add(type='SUN', location=(10, -10, 20))
bpy.context.active_object.data.energy = 5

# Camera
bpy.ops.object.camera_add(location=(0, -30, 15), rotation=(1.1, 0, 0))
bpy.context.scene.camera = bpy.context.active_object

# Export to GLB
bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')
print("✅ Exported to:", output_path)
