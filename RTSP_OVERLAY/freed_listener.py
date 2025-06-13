import socket
import threading
from camera_state import shared_camera

def parse_freed_packet(data):
    print(f"Received FreeD packet ({len(data)} bytes): {data.hex()}")
    if len(data) < 26:
        print("⚠️ Packet too short.")
        return

    try:
        raw_pan = int.from_bytes(data[3:6], byteorder='big', signed=True)
        raw_tilt = int.from_bytes(data[6:9], byteorder='big', signed=True)
        raw_zoom = int.from_bytes(data[21:24], byteorder='big', signed=False)

        pan_deg = raw_pan / 32768.0 * 180
        tilt_deg = raw_tilt / 32768.0 * 120

        print(f"Parsed → Pan: {pan_deg:.2f}°, Tilt: {tilt_deg:.2f}°, Zoom Raw: {raw_zoom}")
        shared_camera.update_from_freed(pan_deg, tilt_deg, raw_zoom)
        shared_camera.mark_freed_received()

    except Exception as e:
        print(f"❌ Failed to parse FreeD: {e}")

def start_freed_listener(ip='0.0.0.0', port=19148):
    def listen():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((ip, port))
            print(f"[FreeD] Listening on {ip}:{port}")

            while True:
                data, _ = sock.recvfrom(1024)
                parse_freed_packet(data)

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()
