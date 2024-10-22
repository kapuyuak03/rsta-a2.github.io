# camera_stream.py
import cv2
import base64
import json
import asyncio
import websockets

class CameraStream:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None
    
    def initialize(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.camera_id)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return self.cap.isOpened()
    
    def get_frame(self):
        if not self.initialize():
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        # Encode frame to JPG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        return frame_base64
    
    def close(self):
        if self.cap:
            self.cap.release()
            self.cap = None

# Integration with websocket client
async def send_data(camera, pixhawk):
    uri = "ws://localhost:8765"  # Change to your server address
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    # Get camera frame
                    frame = camera.get_frame()
                    
                    # Get Pixhawk data
                    pixhawk_data = pixhawk.get_data()
                    
                    if frame and pixhawk_data:
                        combined_data = {
                            'frame': frame,
                            'pixhawk': pixhawk_data
                        }
                        
                        await websocket.send(json.dumps(combined_data))
                    
                    await asyncio.sleep(0.1)  # Adjust delay as needed
                    
        except websockets.exceptions.ConnectionClosed:
            print("Connection lost. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)