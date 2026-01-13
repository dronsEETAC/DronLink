import logging
import math
import threading
import time


def _send_telemetry_info(self, process_telemetry_info):
    self.alt = 0
    self.sendTelemetryInfo = True

    if self.verbose:
        logging.info("Inicio envio de telemetría global")

    while self.sendTelemetryInfo:

        # preparo el paquete de datos de telemetria
        telemetry_info = {
            'lat': self.lat,
            'lon': self.lon,
            'alt': self.alt,
            'groundSpeed':  self.groundSpeed,
            'heading': self.heading,
            'state': self.state,
            'flightMode': self.flightMode,
            'voltage_battery': self.voltage_battery,
            'current_battery': self.current_battery,
            'battery_remaining': self.battery_remaining
        }
        # llamo al callback
        if self.id == None:
            process_telemetry_info (telemetry_info)
        else:
            process_telemetry_info (self.id, telemetry_info)
        time.sleep(1/self.frequency)

def send_telemetry_info(self, process_telemetry_info):
    telemetryThread = threading.Thread(target=self._send_telemetry_info, args=[process_telemetry_info,])
    telemetryThread.start()

def stop_sending_telemetry_info(self):
    self.sendTelemetryInfo = False
    if self.verbose:
        logging.info("Detengo envio de telemetría global")