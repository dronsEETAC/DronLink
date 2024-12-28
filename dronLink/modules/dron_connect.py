import math
import threading
import time

from dronLink.modules.message_handler import MessageHandler
from pymavlink import mavutil

''' Esta función sirve exclusivamente para detectar cuándo el dron se desarma porque 
ha pasado mucho tiempo desde que se armó sin despegar'''


def _handle_heartbeat(self, msg):
    if msg.base_mode == 89 and self.state == 'armed':
        self.state = 'connected'
        print ('Ne acabo de desarmar')
    mode = mavutil.mode_string_v10(msg)
    if not 'Mode(0x000000' in str(mode):
            self.flightMode = mode



def _record_telemetry_info(self, msg):
    if msg:
        msg = msg.to_dict()

        self.lat = float(msg['lat'] / 10 ** 7)
        self.lon = float(msg['lon'] / 10 ** 7)
        self.alt = float(msg['relative_alt'] / 1000)
        self.heading = float(msg['hdg'] / 100)
        if self.state == 'connected' and self.alt > 0.5:
            self.state = 'flying'
        if self.state == 'flying' and self.alt < 0.5:
            self.state = 'connected'
        vx = float(msg['vx'])
        vy = float(msg['vy'])
        self.groundSpeed = math.sqrt(vx * vx + vy * vy) / 100



def _record_local_telemetry_info(self, msg):
    if msg:
        self.position = [msg.x, msg.y, msg.z]

def _connect(self, connection_string, baud, callback=None, params=None):
    self.vehicle = mavutil.mavlink_connection(connection_string, baud)
    self.vehicle.wait_heartbeat()
    self.state = "connected"

    # pongo en marcha el gestor de mensaje
    self.message_handler = MessageHandler(self.vehicle)

    # le indico los tres tipos de mensajes que quiero recibir de forma asíncrona, con los handlers correspondientes
    # a cada uno de esos tipos de mensajes
    self.message_handler.register_handler('HEARTBEAT', self._handle_heartbeat)
    self.message_handler.register_handler('GLOBAL_POSITION_INT', self._record_telemetry_info)
    self.message_handler.register_handler('LOCAL_POSITION_NED', self._record_local_telemetry_info)

    # y ahora solicito los tipos de mensajes que quiero
    # Pido datos globales
    self.vehicle.mav.command_long_send(
        self.vehicle.target_system, self.vehicle.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
        mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,
        1e6 / self.frequency,  # frecuencia con la que queremos paquetes de telemetría
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
            freq=4,
            blocking=True,
            callback=None,
            params=None):
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


def disconnect(self):
    if self.state == 'connected':
        self.state = "disconnected"
        # paramos el envío de datos de telemetría
        self.stop_sending_telemetry_info()
        self.stop_sending_local_telemetry_info()
        time.sleep(1)
        self.vehicle.close()
        return True
    else:
        return False

def reboot (self):
    self.vehicle.mav.command_long_send(
        self.vehicle.target_system,  # ID del sistema
        self.vehicle.target_component,  # ID del componente
        mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN,  # Comando de reinicio
        0,  # Confirmación
        1,  # Parám 1: 1 para reiniciar el autopiloto
        0,  # Parám 2: no utilizado
        0,  # Parám 3: no utilizado
        0,  # Parám 4: no utilizado
        0,  # Parám 5: no utilizado
        0,  # Parám 6: no utilizado
        0   # Parám 7: no utilizado
    )