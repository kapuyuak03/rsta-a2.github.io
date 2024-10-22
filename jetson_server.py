import asyncio
import websockets
import json
from pixhawk_data import PixhawkData
from object_detection import ObjectDetection

pixhawk = PixhawkData()
object_detector = ObjectDetection()

async def send_data():
    uri = "ws://your-vps-ip-or-domain:8765"  # Ganti dengan alamat VPS Anda
    async with websockets.connect(uri) as websocket:
        while True:
            pixhawk_data = pixhawk.get_data()
            detection_data = object_detector.detect()

            if pixhawk_data and detection_data:
                combined_data = {
                    'pixhawk': pixhawk_data,
                    'object_detection': detection_data['detections']
                }

                await websocket.send(json.dumps(combined_data))

            await asyncio.sleep(0.1)  # Sesuaikan delay sesuai kebutuhan

async def main():
    while True:
        try:
            await send_data()
        except websockets.exceptions.ConnectionClosed:
            print("Koneksi ke server terputus. Mencoba kembali dalam 5 detik...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())