# jetson_server.py
import asyncio
import websockets
import json
from Camera_Stream import CameraStream
from pixhawk_data import PixhawkData

class JetsonServer:
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.camera = CameraStream(camera_id=0)
        self.pixhawk = PixhawkData()
        self.clients = set()
        
    async def register(self, websocket):
        self.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
            
    async def broadcast_data(self):
        while True:
            try:
                # Get camera frame
                frame = self.camera.get_frame()
                
                # Get Pixhawk data
                pixhawk_data = self.pixhawk.get_data()
                
                if frame and pixhawk_data:
                    data = {
                        'frame': frame,
                        'pixhawk': pixhawk_data
                    }
                    
                    # Broadcast to all connected clients
                    websockets_tasks = []
                    for websocket in self.clients:
                        try:
                            websockets_tasks.append(
                                asyncio.create_task(
                                    websocket.send(json.dumps(data))
                                )
                            )
                        except websockets.exceptions.ConnectionClosed:
                            self.clients.remove(websocket)
                    
                    if websockets_tasks:
                        await asyncio.gather(*websockets_tasks)
                        
            except Exception as e:
                print(f"Broadcast error: {e}")
                
            await asyncio.sleep(0.1)  # Adjust rate as needed
            
    async def start(self):
        async with websockets.serve(self.register, self.host, self.port):
            await self.broadcast_data()
            
    def run(self):
        # Initialize camera and Pixhawk
        if not self.camera.initialize():
            print("Failed to initialize camera")
            return
            
        if not self.pixhawk.connect():
            print("Failed to connect to Pixhawk")
            return
            
        print(f"Starting Jetson server on ws://{self.host}:{self.port}")
        
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            self.camera.close()
            self.pixhawk.close()

if __name__ == "__main__":
    server = JetsonServer()
    server.run()
