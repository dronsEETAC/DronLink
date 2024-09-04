import json
import math
import threading
import time

from pymavlink import mavutil


def _send_local_telemetry_info(self, process_local_telemetry_info):
    self.sendLocalTelemetryInfo = True
    while self.sendLocalTelemetryInfo:
        local_telemetry_info = {
            'posX': self.position[0],
            'posY': self.position[1],
            'posZ': self.position[2]
        }
        if self.id == None:
            process_local_telemetry_info (local_telemetry_info)
        else:
            process_local_telemetry_info (self.id, local_telemetry_info)
        time.sleep (1/self.frequency)


def send_local_telemetry_info(self, process_local_telemetry_info):
    telemetryThread = threading.Thread(target=self._send_local_telemetry_info, args = [process_local_telemetry_info,] )
    telemetryThread.start()

def stop_sending_local_telemetry_info(self):
    self.sendLocalTelemetryInfo = False