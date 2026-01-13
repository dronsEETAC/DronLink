import threading
import time
from pymavlink import mavutil


def _record_distance_info(self, msg):
    if msg:
        print (msg)
        self.distance = msg.current_distance
        if hasattr(msg, "orientation"):
            self.orientation = msg.orientation

def _send_info(self, process_distance_info, freq):
    self.sendDistanceInfo = True
    while self.sendDistanceInfo:
        # preparo el paquete de datos de distancia
        distance_info = {
            'distance': self.distance,
            'orientation': self.orientation,
        }
        # llamo al callback
        if self.id == None:
            process_distance_info (distance_info)
        else:
            process_distance_info  (self.id, distance_info)
        time.sleep(1/freq)

def send_distance_sensor_info (self, process_distance_info, freq = 4):

    self.message_handler.register_handler('DISTANCE_SENSOR', self._record_distance_info)
    # Pido datos del sensor de distancia
    self.vehicle.mav.command_long_send(
        self.vehicle.target_system, self.vehicle.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
        mavutil.mavlink.MAVLINK_MSG_ID_DISTANCE_SENSOR,  # The MAVLink message ID
        1e6 / freq,
        0, 0, 0, 0,  # Unused parameters
        0
    )
    sensorDistanvceThread = threading.Thread(target=self._send_info, args=[process_distance_info,freq ])
    sensorDistanvceThread.start()

def stop_sending_distance_sensor_info (self):
    self.sendDistanceInfo = False

def ConfigureDistanceSensor (self,sensor):

    if sensor == 'RPLIDAR C1':
        # posz indica si se usa altimetro laser (2) o si se usa barometro (1)
        newParameters = [
            {'ID': "SERIAL2_PROTOCOL", 'Value':11},
            {'ID': "SERIAL2_BAUD", 'Value': 460800},
            {'ID': "PRX1_TYPE", 'Value': 5},
            {'ID': "PRX1_ORIENT", 'Value': 0},
            {'ID': "RNGFND2_TYPE", 'Value': 0},
        ]
        self.setParams(newParameters)
    elif sensor == 'TFmini':
        newParameters = [
            {'ID': "SERIAL2_PROTOCOL", 'Value': 9},
            {'ID': "SERIAL2_BAUD", 'Value': 115200},
            {'ID': "RNGFND2_TYPE", 'Value': 20},
            {'ID': "RNGFND2_MIN_CM", 'Value': 30},
            {'ID': "RNGFND2_MAX_CM", 'Value': 600},
            {'ID': "RNGFND2_ORIENT", 'Value': 0},
            {'ID': "RNGFND2_ADDR", 'Value': 0},
        ]
        self.setParams(newParameters)
    self.reboot()