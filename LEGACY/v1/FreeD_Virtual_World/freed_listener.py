import socket
import threading
from camera_state import shared_camera

def parse_freed_packet(data):
    print(f"Received FreeD packet ({len(data)} bytes): {data.hex()}")
    if len(data) < 26:
        print("⚠️ Packet too short.")
        return

    try:
        # D0 format: bytes [2:5] = pan, [5:8] = tilt, [21:24] = zoom
        raw_pan  = int.from_bytes(data[2:5], byteorder='big', signed=True)
        raw_tilt = int.from_bytes(data[5:8], byteorder='big', signed=True)

        # Extract FoV/Zoom (bytes 21–23)
        byte21 = data[21]
        byte22 = data[22]
        byte23 = data[23]
        raw_zoom = (byte21 << 16) | (byte22 << 8) | byte23

        # Normalize
        pan_deg = raw_pan / 32768.0 * 180
        tilt_deg = raw_tilt / 32768.0 * 90

        print(f"Parsed → Pan: {pan_deg:.2f}°, Tilt: {tilt_deg:.2f}°, Zoom Bytes: {byte21:02X} {byte22:02X} {byte23:02X} → Zoom Raw: {raw_zoom}")

        shared_camera.update_from_freed(pan_deg, tilt_deg, raw_zoom)

    except Exception as e:
        print(f"❌ Failed to parse FreeD: {e}")

def start_freed_listener(port=19148):
    def listen():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", port))
        print(f"✅ FreeD listener active on UDP port {port}")
        while True:
            data, _ = sock.recvfrom(1024)
            parse_freed_packet(data)

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()
