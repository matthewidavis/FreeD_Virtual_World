import socket
import threading
from camera_state import shared_camera

listener_thread = None
listener_active = False

def listen_to_freed(ip="0.0.0.0", port=19148):
    global listener_active
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    sock.settimeout(1)
    print(f"[FreeD] Listening on {ip}:{port}")
    while listener_active:
        try:
            data, _ = sock.recvfrom(1024)
            if len(data) >= 29:
                parse_freed_data(data)
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[FreeD] Error: {e}")
    sock.close()

def parse_freed_data(data):
    pan = int.from_bytes(data[0:3], byteorder='big', signed=True)
    tilt = int.from_bytes(data[3:6], byteorder='big', signed=True)
    zoom = int.from_bytes(data[6:9], byteorder='big', signed=False)
    x = int.from_bytes(data[9:12], byteorder='big', signed=True) / 1000.0
    y = int.from_bytes(data[12:15], byteorder='big', signed=True) / 1000.0
    z = int.from_bytes(data[15:18], byteorder='big', signed=True) / 1000.0

    shared_camera.pan = pan
    shared_camera.tilt = tilt
    shared_camera.zoom = zoom
    shared_camera.x = x
    shared_camera.y = y
    shared_camera.z = z

def start_freed_listener(port=19148):
    global listener_thread, listener_active
    if listener_thread and listener_thread.is_alive():
        return
    listener_active = True
    listener_thread = threading.Thread(target=listen_to_freed, args=("0.0.0.0", port), daemon=True)
    listener_thread.start()

def stop_freed_listener():
    global listener_active
    listener_active = False
