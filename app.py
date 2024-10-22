# web_server.py
from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import base64
import cv2
import numpy as np
import json
import asyncio
import websockets
from threading import Thread
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

class WebServer:
    def __init__(self, jetson_uri='ws://jetson-ip:8765'):
        self.jetson_uri = jetson_uri
        self.latest_data = {
            'frame': None,
            'surface_frame': None,
            'underwater_frame': None,
            'pixhawk': {
                'latitude': 0.0,
                'longitude': 0.0,
                'altitude': 0.0,
                'relative_altitude': 0.0,
                'heading': 0.0,
                'speed': 0.0,
                'battery': 100,
                'trajectory': []
            }
        }
        
    async def connect_to_jetson(self):
        while True:
            try:
                async with websockets.connect(self.jetson_uri) as websocket:
                    print(f"Connected to Jetson at {self.jetson_uri}")
                    
                    while True:
                        data = await websocket.recv()
                        data = json.loads(data)
                        
                        # Update latest data
                        if 'frame' in data:
                            self.latest_data['frame'] = data['frame']
                            # Assuming surface and underwater frames are also provided
                            self.latest_data['surface_frame'] = data.get('surface_frame', data['frame'])
                            self.latest_data['underwater_frame'] = data.get('underwater_frame', data['frame'])
                        
                        if 'pixhawk' in data:
                            self.latest_data['pixhawk'].update(data['pixhawk'])
                            
                        # Emit updates to all connected clients
                        socketio.emit('data_update', {
                            'video': {
                                'main': data.get('frame'),
                                'surface': data.get('surface_frame'),
                                'underwater': data.get('underwater_frame')
                            },
                            'telemetry': self.latest_data['pixhawk'],
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                            
            except websockets.exceptions.ConnectionClosed:
                print("Connection to Jetson lost. Reconnecting...")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(5)

    def start_websocket_client(self):
        asyncio.run(self.connect_to_jetson())

# Serve static files
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Main route
@app.route('/')
def index():
    return render_template('index.html')

# Data endpoint for initial load and polling fallback
@app.route('/data')
def get_data():
    return jsonify({
        'latitude': server.latest_data['pixhawk']['latitude'],
        'longitude': server.latest_data['pixhawk']['longitude'],
        'heading': server.latest_data['pixhawk']['heading'],
        'speed': server.latest_data['pixhawk']['speed'],
        'battery': server.latest_data['pixhawk']['battery'],
        'trajectory': server.latest_data['pixhawk']['trajectory'],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

# SocketIO events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send initial data
    emit('data_update', {
        'video': {
            'main': server.latest_data['frame'],
            'surface': server.latest_data['surface_frame'],
            'underwater': server.latest_data['underwater_frame']
        },
        'telemetry': server.latest_data['pixhawk'],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    server = WebServer()
    
    # Start websocket client in a separate thread
    websocket_thread = Thread(target=server.start_websocket_client)
    websocket_thread.daemon = True
    websocket_thread.start()
    
    # Start Flask-SocketIO server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
