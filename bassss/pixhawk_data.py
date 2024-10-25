import serial
from pymavlink import mavutil
import time

class PixhawkData:
    def __init__(self, connection_string='COM7', baud=115200):
        self.connection_string = connection_string
        self.baud = baud
        self.master = None
        self.initial_lat = None
        self.initial_lon = None
        self.prev_lat = None
        self.prev_lon = None
        self.latitudes = []
        self.longitudes = []
        self.THRESHOLD_MOVEMENT = 0.000001  # Increased precision for Here3+ GPS

    def connect(self):
        try:
            # Connect to Pixhawk Cube Orange+ via mavutil
            self.master = mavutil.mavlink_connection(self.connection_string, baud=self.baud)
            self.master.wait_heartbeat(timeout=10)
            print(f"Connected to Pixhawk Cube Orange+ at {self.connection_string}")
            return True
        except (serial.SerialException, Exception) as e:
            print(f"Error connecting to Pixhawk Cube Orange+: {str(e)}")
            return False

    def get_data(self):
        if not self.master:
            if not self.connect():
                return None

        try:
            # Read data from MAVLink
            msg_position = self.master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=5)
            msg_attitude = self.master.recv_match(type='ATTITUDE', blocking=True, timeout=5)
            msg_vfr = self.master.recv_match(type='VFR_HUD', blocking=True, timeout=5)
            msg_gps = self.master.recv_match(type='GPS_RAW_INT', blocking=True, timeout=5)
            
            if msg_position and msg_attitude and msg_vfr and msg_gps:
                if msg_position.lat != 0 and msg_position.lon != 0:
                    lat = msg_position.lat / 1e7
                    lon = msg_position.lon / 1e7
                    alt = msg_position.alt / 1000  # Convert mm to meters
                    relative_alt = msg_position.relative_alt / 1000  # Convert mm to meters
                    speed = msg_vfr.groundspeed * 1.94384  # Convert m/s to knots
                    heading = msg_attitude.yaw * (180.0 / 3.14159)  # Convert yaw to degrees
                    gps_fix = msg_gps.fix_type
                    satellites_visible = msg_gps.satellites_visible

                    if self.initial_lat is None or self.initial_lon is None:
                        self.initial_lat = lat
                        self.initial_lon = lon
                        self.prev_lat = lat
                        self.prev_lon = lon

                    delta_lat = lat - self.prev_lat
                    delta_lon = lon - self.prev_lon

                    if abs(delta_lat) >= self.THRESHOLD_MOVEMENT or abs(delta_lon) >= self.THRESHOLD_MOVEMENT:
                        self.latitudes.append(lat - self.initial_lat)
                        self.longitudes.append(lon - self.initial_lon)
                        self.prev_lat = lat
                        self.prev_lon = lon

                    return {
                        'latitude': lat - self.initial_lat,
                        'longitude': lon - self.initial_lon,
                        'altitude': alt,
                        'relative_altitude': relative_alt,
                        'speed': speed,
                        'heading': heading,
                        'gps_fix': gps_fix,
                        'satellites_visible': satellites_visible,
                        'trajectory': list(zip(self.longitudes, self.latitudes))
                    }
        except Exception as e:
            print(f"Error reading data: {str(e)}")
            self.master = None  # Reset connection on error

        return None

    def close(self):
        if self.master:
            print("Closing connection to Pixhawk Cube Orange+...")
            self.master.close()
            self.master = None