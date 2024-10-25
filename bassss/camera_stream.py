import cv2
import numpy as np
import asyncio
import json
import logging
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame

class CameraVideoStreamTrack(VideoStreamTrack):
    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.cap = None
        self.running = False
        self.frame_count = 0
        self._start_camera()

    def _start_camera(self):
        """Initialize the camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                raise RuntimeError(f"Could not open camera {self.camera_index}")
            self.running = True
            logging.info(f"Camera {self.camera_index} initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing camera: {str(e)}")
            raise

    async def recv(self):
        """Capture and return the next video frame"""
        if self.cap is None or not self.running:
            return None

        try:
            ret, frame = self.cap.read()
            if not ret:
                logging.warning("Failed to capture frame")
                return None

            # Convert the frame from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create VideoFrame object
            video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
            video_frame.pts = self.frame_count
            video_frame.time_base = 1/30  # 30 FPS
            
            self.frame_count += 1
            return video_frame

        except Exception as e:
            logging.error(f"Error capturing frame: {str(e)}")
            return None

    def stop(self):
        """Stop the camera capture"""
        self.running = False
        if self.cap:
            self.cap.release()
        self.cap = None
        logging.info("Camera stopped")

class CameraStream:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.peer_connections = set()
        self.video_track = None
        logging.basicConfig(level=logging.INFO)

    async def create_offer(self):
        """Create a new peer connection and offer"""
        try:
            pc = RTCPeerConnection()
            self.peer_connections.add(pc)

            if not self.video_track:
                self.video_track = CameraVideoStreamTrack(self.camera_index)

            pc.addTrack(self.video_track)

            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)

            return {
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            }

        except Exception as e:
            logging.error(f"Error creating offer: {str(e)}")
            raise

    async def handle_answer(self, pc, answer):
        """Handle the answer from the client"""
        try:
            await pc.setRemoteDescription(
                RTCSessionDescription(sdp=answer["sdp"], type=answer["type"])
            )
        except Exception as e:
            logging.error(f"Error handling answer: {str(e)}")
            raise

    async def handle_ice_candidate(self, pc, candidate):
        """Handle ICE candidate from the client"""
        try:
            await pc.addIceCandidate(candidate)
        except Exception as e:
            logging.error(f"Error handling ICE candidate: {str(e)}")
            raise

    def stop_all_connections(self):
        """Stop all peer connections and release resources"""
        if self.video_track:
            self.video_track.stop()

        for pc in self.peer_connections:
            pc.close()
        
        self.peer_connections.clear()
        logging.info("All connections stopped")

    async def get_connection_status(self):
        """Get the status of all peer connections"""
        status = {
            "active_connections": len(self.peer_connections),
            "camera_running": self.video_track is not None and self.video_track.running,
            "connection_states": [pc.connectionState for pc in self.peer_connections]
        }
        return status
