
import threading
import time

from pymavlink import mavutil

''' Esta función sirve exclusivamente para detectar cuándo el dron se desarma porque 
ha pasado mucho tiempo desde que se armó sin despegar'''
def _handle_heartbeat(self):
    while self.state != 'disconnected':
        msg = self.vehicle.recv_match(type='HEARTBEAT', blocking=False)
        if msg:
            if msg.base_mode == 89 and self.state == 'armed':
                self.state = 'connected'

        time.sleep (1)



def _connect(self, connection_string, baud, callback=None, params=None):
    self.vehicle = mavutil.mavlink_connection(connection_string, baud)
    self.vehicle.wait_heartbeat()
    self.state = "connected"
    # pongo en marcha el thread para detectar el desarmado por innacción
    handleThread = threading.Thread (target = self._handle_heartbeat)
    handleThread.start()

    # Pido datos globales
    self.vehicle.mav.command_long_send(
        self.vehicle.target_system, self.vehicle.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
        mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,
        1e6 / self.frequency, # frecuencia con la que queremos paquetes de telemetría
        0, 0, 0, 0,  # Unused parameters
        0
    )
    # Pido también datos locales
    self.vehicle.mav.command_long_send(
        self.vehicle.target_system, self.vehicle.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
        mavutil.mavlink.MAVLINK_MSG_ID_LOCAL_POSITION_NED,  # The MAVLink message ID
        1e6 / self.frequency,
        0, 0, 0, 0,  # Unused parameters
        0
    )
    # compruebo si el dron está ya en el aire
    msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=3)
    if msg:
        msg = msg.to_dict()
        self.alt = float(msg['relative_alt'] / 1000)
        if self.alt > 0.5:
            self.state = 'flying'

    if callback != None:
        if self.id == None:
            if params == None:
                callback()
            else:
                callback(params)
        else:
            if params == None:
                callback(self.id)
            else:
                callback(self.id, params)


def connect(self,
            connection_string,
            baud,
            freq = 4,
            blocking=True,
            callback=None,
            params = None):
    if self.state == 'disconnected':
        self.frequency = freq
        if blocking:
            self._connect(connection_string, baud)
        else:
            connectThread = threading.Thread(target=self._connect, args=[connection_string, baud, callback, params, ])
            connectThread.start()
        return True
    else:
        return False

def disconnect (self):
    if self.state == 'connected':
        self.state = "disconnected"
        # paramos el envío de datos de telemetría
        self.stop_sending_telemetry_info()
        self.stop_sending_local_telemetry_info()
        time.sleep (1)
        self.vehicle.close()
        return True
    else:
        return False