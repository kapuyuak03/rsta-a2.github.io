# pixhawk_data.py
from pymavlink import mavutil
import time

class PixhawkData:
    def __init__(self, connection_string='/dev/ttyACM0', baud=57600):
        self.connection_string = connection_string
        self.baud = baud
        self.master = None
        self.initial_lat = None
        self.initial_lon = None
        self.latitudes = []
        self.longitudes = []
        
    def connect(self):
        try:
            # Try to connect to Pixhawk
            self.master = mavutil.mavlink_connection(self.connection_string, baud=self.baud)
            print("Waiting for heartbeat...")
            self.master.wait_heartbeat()
            print(f"Connected to Pixhawk at {self.connection_string}")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
            
    def get_data(self):
        if not self.master and not self.connect():
            return None
            
        try:
            # Request data explicitly
            self.master.mav.request_data_stream_send(
                self.master.target_system,
                self.master.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,
                10,  # 10 Hz
                1    # Start
            )
            
            # Get messages with timeout
            msg_pos = self.master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=1)
            msg_att = self.master.recv_match(type='ATTITUDE', blocking=True, timeout=1)
            msg_vfr = self.master.recv_match(type='VFR_HUD', blocking=True, timeout=1)
            
            if all([msg_pos, msg_att, msg_vfr]):
                lat = msg_pos.lat / 1e7
                lon = msg_pos.lon / 1e7
                alt = msg_pos.alt / 1000.0  # Convert to meters
                rel_alt = msg_pos.relative_alt / 1000.0
                heading = msg_att.yaw * 57.2958  # Convert to degrees
                speed = msg_vfr.groundspeed
                
                # Initialize reference point
                if self.initial_lat is None:
                    self.initial_lat = lat
                    self.initial_lon = lon
                
                # Store trajectory
                self.latitudes.append(lat - self.initial_lat)
                self.longitudes.append(lon - self.initial_lon)
                
                # Keep only last 100 points
                if len(self.latitudes) > 100:
                    self.latitudes.pop(0)
                    self.longitudes.pop(0)
                
                return {
                    'latitude': lat,
                    'longitude': lon,
                    'altitude': alt,
                    'relative_altitude': rel_alt,
                    'heading': heading,
                    'speed': speed,
                    'trajectory': list(zip(self.longitudes, self.latitudes))
                }
                
        except Exception as e:
            print(f"Error reading data: {e}")
            self.master = None  # Force reconnection
            
        return None
        
    def close(self):
        if self.master:
            self.master.close()
            self.master = None
