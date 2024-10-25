import cv2
import logging
import asyncio
import argparse
from camera_stream import CameraStream, CameraVideoStreamTrack
import time
from datetime import datetime

class CameraDebugger:
    def __init__(self, camera_index=0, log_level=logging.DEBUG):
        """
        Initialize the camera debugger
        
        Args:
            camera_index (int): Index of the camera to test
            log_level (int): Logging level (default: logging.DEBUG)
        """
        # Setup logging
        self.setup_logging(log_level)
        self.logger = logging.getLogger(__name__)
        
        self.camera_index = camera_index
        self.camera_stream = None
        self.video_track = None

    def setup_logging(self, log_level):
        """Setup logging configuration"""
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'camera_debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )

    async def test_camera_initialization(self):
        """Test camera initialization"""
        try:
            self.logger.info(f"Testing camera initialization with index {self.camera_index}")
            self.camera_stream = CameraStream(self.camera_index)
            self.logger.info("CameraStream instance created successfully")
            
            # Test VideoTrack creation
            self.video_track = CameraVideoStreamTrack(self.camera_index)
            self.logger.info("CameraVideoStreamTrack created successfully")
            
            return True
        except Exception as e:
            self.logger.error(f"Camera initialization failed: {str(e)}")
            return False

    async def test_frame_capture(self, num_frames=100):
        """
        Test frame capture functionality
        
        Args:
            num_frames (int): Number of frames to capture for testing
        """
        if not self.video_track:
            self.logger.error("VideoTrack not initialized")
            return False

        try:
            self.logger.info(f"Testing frame capture: attempting to capture {num_frames} frames")
            frame_times = []
            failed_frames = 0

            for i in range(num_frames):
                start_time = time.time()
                
                frame = await self.video_track.recv()
                
                if frame is None:
                    failed_frames += 1
                    self.logger.warning(f"Failed to capture frame {i}")
                    continue

                frame_times.append(time.time() - start_time)

            # Calculate statistics
            if frame_times:
                avg_time = sum(frame_times) / len(frame_times)
                max_time = max(frame_times)
                min_time = min(frame_times)
                fps = 1.0 / avg_time if avg_time > 0 else 0

                self.logger.info(f"""Frame capture statistics:
                    Frames captured: {num_frames - failed_frames}/{num_frames}
                    Failed frames: {failed_frames}
                    Average capture time: {avg_time:.4f} seconds
                    Maximum capture time: {max_time:.4f} seconds
                    Minimum capture time: {min_time:.4f} seconds
                    Effective FPS: {fps:.2f}
                """)
            
            return failed_frames == 0
        except Exception as e:
            self.logger.error(f"Frame capture test failed: {str(e)}")
            return False

    async def test_webrtc_connection(self):
        """Test WebRTC connection establishment"""
        try:
            self.logger.info("Testing WebRTC connection setup")
            
            # Create offer
            offer = await self.camera_stream.create_offer()
            self.logger.info("Successfully created WebRTC offer")
            
            # Check peer connections
            num_connections = len(self.camera_stream.peer_connections)
            self.logger.info(f"Number of peer connections: {num_connections}")
            
            # Get connection status
            status = await self.camera_stream.get_connection_status()
            self.logger.info(f"Connection status: {status}")
            
            return True
        except Exception as e:
            self.logger.error(f"WebRTC connection test failed: {str(e)}")
            return False

    def test_camera_properties(self):
        """Test and log camera properties"""
        try:
            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                self.logger.error("Failed to open camera")
                return False

            # Get and log camera properties
            properties = {
                'Frame Width': cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                'Frame Height': cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
                'FPS': cap.get(cv2.CAP_PROP_FPS),
                'Format': cap.get(cv2.CAP_PROP_FORMAT),
                'Mode': cap.get(cv2.CAP_PROP_MODE),
                'Brightness': cap.get(cv2.CAP_PROP_BRIGHTNESS),
                'Contrast': cap.get(cv2.CAP_PROP_CONTRAST),
                'Saturation': cap.get(cv2.CAP_PROP_SATURATION),
                'Hue': cap.get(cv2.CAP_PROP_HUE),
                'Gain': cap.get(cv2.CAP_PROP_GAIN),
                'Exposure': cap.get(cv2.CAP_PROP_EXPOSURE)
            }

            self.logger.info("Camera properties:")
            for prop, value in properties.items():
                self.logger.info(f"{prop}: {value}")

            cap.release()
            return True
        except Exception as e:
            self.logger.error(f"Camera properties test failed: {str(e)}")
            return False

    def cleanup(self):
        """Cleanup resources"""
        try:
            self.logger.info("Cleaning up resources")
            if self.video_track:
                self.video_track.stop()
            if self.camera_stream:
                self.camera_stream.stop_all_connections()
            self.logger.info("Cleanup completed successfully")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")

async def main():
    parser = argparse.ArgumentParser(description='Camera Stream Debug Tool')
    parser.add_argument('--camera', type=int, default=0, help='Camera index to test')
    parser.add_argument('--frames', type=int, default=100, help='Number of frames to test')
    parser.add_argument('--log-level', type=str, default='DEBUG',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level')
    
    args = parser.parse_args()
    
    # Convert string log level to logging constant
    log_level = getattr(logging, args.log_level.upper())
    
    debugger = CameraDebugger(args.camera, log_level)
    
    try:
        # Run tests
        if await debugger.test_camera_initialization():
            debugger.test_camera_properties()
            await debugger.test_frame_capture(args.frames)
            await debugger.test_webrtc_connection()
    finally:
        debugger.cleanup()

if __name__ == "__main__":
    asyncio.run(main())