'''
Coleccion de métodos para la navegación según los puntos cardinales.
El dron debe estar en estado 'volando'
Para iniciar la navegación debe ejecutarse el método startGo,
que pone en marcha el thread que mantiene el rumbo.
El rumbo puede cambiar mediante el método go que recibe como parámetro
el nuevo rumbo (north, south, etc).
Para acabar la navegación hay que ejecutar el método stopGo

'''
import threading
import time
from pymavlink import mavutil
import pymavlink.dialects.v20.all as dialect

def _prepare_command(self, velocity_x, velocity_y, velocity_z, bodyRef = False):
    """
    Move vehicle in direction based on specified velocity vectors.
    """
    if bodyRef:
        msg = mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
            10,  # time_boot_ms (not used)
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,  # frame
            0b0000111111000111,  # type_mask (only speeds enabled)
            0,
            0,
            0,  # x, y, z positions (not used)
            velocity_x,
            velocity_y,
            velocity_z,  # x, y, z velocity in m/s
            0,
            0,
            0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0,
            0,
        )  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    else:
        msg =  mavutil.mavlink.MAVLink_set_position_target_global_int_message(
            10,  # time_boot_ms (not used)
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
            0b0000111111000111,  # type_mask (only speeds enabled)
            0,
            0,
            0,  # x, y, z positions (not used)
            velocity_x,
            velocity_y,
            velocity_z,  # x, y, z velocity in m/s
            0,
            0,
            0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0,
            0,
        )  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    return msg


def _goingTread(self):
    self.cmd = self._prepare_command(0, 0, 0)
    while self.going:
        self.vehicle.mav.send(self.cmd)
        time.sleep(1)
    self.cmd = self._prepare_command(0, 0, 0)
    time.sleep(1)

def _startGo(self):
    if self.state == 'flying':
        # ponemos en marcha el thread que va recordando al dron hacia dónde debe navegar
        self.going = True
        startGoThread = threading.Thread(target=self._goingTread)
        startGoThread.start()

def _stopGo(self):
    # detengo el thread de navegación
    self.going = False

def fixHeading (self):
    # al fijar el heading el dron no cambiará de heading sea cual sea la dirección de navegación
    message = dialect.MAVLink_param_set_message(target_system=self.vehicle.target_system,
                                                        target_component=self.vehicle.target_component, param_id='WP_YAW_BEHAVIOR'.encode("utf-8"),
                                                        param_value=0, param_type=dialect.MAV_PARAM_TYPE_REAL32)
    self.vehicle.mav.send(message)

def unfixHeading (self):
    # al des-fijar el heading el dron cambiará el heading según la dirección de navegación.
    message = dialect.MAVLink_param_set_message(target_system=self.vehicle.target_system,
                                                        target_component=self.vehicle.target_component, param_id='WP_YAW_BEHAVIOR'.encode("utf-8"),
                                                        param_value=1, param_type=dialect.MAV_PARAM_TYPE_REAL32)
    self.vehicle.mav.send(message)

def _changeHeading (self, absoluteDegrees, callback=None, params = None):
    # para cambiar el heading en necesario detener el modo navegación
    self._stopGo()
    self.vehicle.mav.command_long_send(
        self.vehicle.target_system,
        self.vehicle.target_component,
        mavutil.mavlink.MAV_CMD_CONDITION_YAW,
        0,
        absoluteDegrees,  # param 1, yaw in degrees
        25, # param 2, yaw speed deg/s
        1, # param 3, direction -1 ccw, 1 cw
        0, # param 4, relative offset 1, absolute angle 0
        0, 0, 0, 0) # not used

    while True:
        msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=3)
        if msg:
            msg = msg.to_dict()
            heading = float(msg['hdg'] / 100)
            if abs(heading-absoluteDegrees) < 5:
                break
            time.sleep(0.25)
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



def changeHeading (self, absoluteDegrees,blocking=True, callback=None, params = None):
    if self.state == 'flying':
        if blocking:
            self._changeHeading(absoluteDegrees)
        else:
            changeHeadingThread = threading.Thread(target=self.__changeHeading, args=[absoluteDegrees, callback, params])
            changeHeadingThread.start()
        return True
    else:
        return False




def changeNavSpeed (self, speed):
    self.navSpeed = speed
    # vuelvo a ordenar que navegue en la dirección en la que estaba navegando
    self.go (self.direction)

def go(self, direction):
    speed = self.navSpeed
    if not self.going:
        # pongo al dron en modo navegación
        self._startGo()
    self.direction = direction
    if self.going:
        if direction == "North":
            self.cmd = self._prepare_command(speed, 0, 0)  # NORTH
        if direction == "South":
            self.cmd = self._prepare_command(-speed, 0, 0)  # SOUTH
        if direction == "East":
            self.cmd = self._prepare_command(0, speed, 0)  # EAST
        if direction == "West":
            self.cmd = self._prepare_command(0, -speed, 0)  # WEST
        if direction == "NorthWest":
            self.cmd = self._prepare_command(speed, -speed, 0)  # NORTHWEST
        if direction == "NorthEast":
            self.cmd = self._prepare_command(speed, speed, 0)  # NORTHEST
        if direction == "SouthWest":
            self.cmd = self._prepare_command(-speed, -speed, 0)  # SOUTHWEST
        if direction == "SouthEast":
            self.cmd = self._prepare_command(-speed, speed, 0)  # SOUTHEST
        if direction == "Stop":
            self.cmd = self._prepare_command(0, 0, 0)  # STOP
        if direction == "Forward":
            self.cmd = self._prepare_command(speed, 0, 0, bodyRef = True)
        if direction == "Back":
            self.cmd = self._prepare_command(-speed, 0, 0, bodyRef=True)
        if direction == "Left":
            self.cmd = self._prepare_command(0, speed, 0, bodyRef=True)
        if direction == "Right":
            self.cmd = self._prepare_command(0, -speed, 0, bodyRef=True)
        if direction == "Up":
            self.cmd = self._prepare_command(0, 0, -speed, bodyRef=True)
        if direction == "Down":
            self.cmd = self._prepare_command(0, 0, speed, bodyRef=True)



