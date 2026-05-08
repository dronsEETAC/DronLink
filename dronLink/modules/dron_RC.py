import threading
import time

from pymavlink import mavutil

def send_rc (self, roll, pitch, throttle, yaw ):

    self.vehicle.mav.rc_channels_override_send(
                self.vehicle.target_system,
                self.vehicle.target_component,
                roll, pitch, throttle, yaw,
                0, 0, 0, 0  # RC5–RC8 sin cambios
    )




def _record_rc_info(self, msg):
    if msg:
        self.rc_throttle =msg.chan3_raw
        self.rc_yaw =msg.chan4_raw
        self.rc_pitch =msg.chan2_raw
        self.rc_roll =msg.chan1_raw

def _send_rc_info(self, process_rc_info, freq):
    self.sendRcInfo = True
    while self.sendRcInfo:
        # preparo el paquete de datos de rc
        rc_info = {
            'throttle' : self.rc_throttle,
            'yaw': self.rc_yaw,
            'pitch': self.rc_pitch,
            'roll': self.rc_roll
        }
        # llamo al callback
        if self.id == None:
            process_rc_info (rc_info)
        else:
            process_rc_info  (self.id,rc_info)
        time.sleep(1/freq)

def send_rc_info (self, process_rc_info, freq=4):

    self.message_handler.register_handler('RC_CHANNELS', self._record_rc_info)
    # Pido datos del sensor de distancia
    self.vehicle.mav.request_data_stream_send(
        self.vehicle.target_system, self.vehicle.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_RC_CHANNELS,
        10,  # Hz
        1  # activar
    )
    rcThread = threading.Thread(target=self._send_rc_info, args=[process_rc_info,freq])
    rcThread.start()

def stop_sending_rc_info (self):
    self.sendRcInfo = False