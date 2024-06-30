import json
import math
import threading
import time

from pymavlink import mavutil


def _send_local_telemetry_info(self, process_local_telemetry_info):
    self.sendLocalTelemetryInfo = True
    while self.sendLocalTelemetryInfo:
        msg = self.vehicle.recv_match(type='LOCAL_POSITION_NED', blocking=True, timeout = 3)

        if msg:
            # La posición viene en formato NED, es decir:
            #   msg.x indica el desplazamiento hacia el norte desde el home (o hacia el sur
            #   si es un valor negativo
            #   msg.y es el desplazamiento hacia el Este (u oeste si el número es negativo)
            #   msg.z es el desplazamiento hacia abajo (down) o hacia arriga si es negativo

            self.position = [msg.x, msg.y, msg.z]
            local_telemetry_info = {
                'posX': msg.x ,
                'posY': msg.y,
                'posZ': msg.z,
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