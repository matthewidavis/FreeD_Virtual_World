# FreeDumb World

**FreeDumb World** is a real-time 3D visualization tool that simulates a camera moving inside a virtual world using FreeD tracking data. It is ideal for testing and demonstrating PTZ camera motion and FreeD integration in AR/VR environments.

<img width="642" alt="image" src="https://github.com/user-attachments/assets/67ef898f-de2a-4501-b56d-84a0d843d960" />


---

## Features

- **Live FreeD Packet Listener**  
  Listens for FreeD tracking data over UDP (default port: `19148`) and parses pan, tilt, and zoom values in real-time.

- **Virtual Camera Simulation**  
  A Panda3D-powered virtual camera mimics physical camera movements and zoom (FoV) dynamically.

- **3D Scene Integration**  
  Automatically loads a `.glb`, `.obj`, or `.bam` scene from the `scenes/` directory. Includes lighting, scaling, and material handling.

- **Real FoV Support**  
  Simulates lens behavior from wide angle (`60.7°`) to telephoto (`3.5°`) based on FreeD zoom values (`0x000000` to `0x400000`).

- **Modular & Extensible**  
  Code is separated by responsibility (`main.py`, `camera_state.py`, `freed_listener.py`, `scene_manager.py`) and easy to expand.

---

## Requirements

- Python 3.10+
- [Panda3D](https://www.panda3d.org/)
- (Optional) [Blender](https://www.blender.org/) — to generate detailed `.glb` scenes

---

## File Structure

```
freed_virtual_viewer/
├── camera_state.py         # Stores current pan, tilt, zoom state
├── freed_listener.py       # Listens for and parses FreeD packets
├── scene_manager.py        # Renders and updates the 3D camera
├── main.py                 # Entry point
├── scenes/
│   └── virtual_world.glb   # 3D world used for visualization
└── generate_virtual_world.py  # (Optional) Scene generator using Blender
```

---

## Usage

To launch the viewer:

```bash
python main.py
```

To generate a `.glb` world (requires Blender):

```bash
"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" --background --python generate_virtual_world.py
```

---

## Use Cases

- Simulate and test FreeD-compatible PTZ camera tracking
- Visualize real-world camera control systems
- Develop and demonstrate AR/VR pipelines without a physical studio
- Educational environments for understanding FreeD and camera optics
