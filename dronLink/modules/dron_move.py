
import math
import threading
import time
from pymavlink import mavutil
import pymavlink.dialects.v20.all as dialect


def _prepare_command_mov(self, step_x, step_y, step_z, bodyRef = False):
    if bodyRef:
        msg =  mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
            10,  # time_boot_ms (not used)
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,  # frame
            0b110111111000,  # type_mask (only speeds enabled)
            step_x,
            step_y,
            step_z,  # x, y, z positions (not used)
            0,
            0,
            0,  # x, y, z velocity in m/s
            0,
            0,
            0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0,
            0,
        )  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
    else:
        msg = mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
            10,  # time_boot_ms (not used)
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_OFFSET_NED,  # frame
            0b110111111000,  # type_mask (only speeds enabled)
            step_x,
            step_y,
            step_z,  # x, y, z positions (not used)
            0,
            0,
            0,  # x, y, z velocity in m/s
            0,
            0,
            0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0,
            0,
        )  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    return msg

def _move_distance (self, direction, distance, callback=None, params = None):
    self._stopGo()
    step = distance
    if direction == "Forward":
        self.cmd = self._prepare_command_mov(step, 0, 0, bodyRef = True)
    if direction == "Back":
        self.cmd = self._prepare_command_mov(-step, 0, 0, bodyRef = True)
    if direction == "Left":
        self.cmd = self._prepare_command_mov(0, -step, 0, bodyRef = True)
    if direction == "Right":
        self.cmd = self._prepare_command_mov(0, step, 0, bodyRef = True)
    if direction == "Up":
        self.cmd = self._prepare_command_mov(0, 0, -step, bodyRef = True)
    if direction == "Down":
        self.cmd = self._prepare_command_mov(0, 0, step, bodyRef = True)
    if direction == "Stop":
        self.cmd = self._prepare_command_mov(0, 0, 0, bodyRef = True)

    if direction == "North":
        self.cmd = self._prepare_command_mov(step, 0, 0)
    if direction == "South":
        self.cmd = self._prepare_command_mov(-step, 0, 0)
    if direction == "West":
        print ('voy al west')
        self.cmd = self._prepare_command_mov(0, -step, 0)
    if direction == "East":
        self.cmd = self._prepare_command_mov(0, step, 0)

    self.vehicle.mav.send(self.cmd)
    time.sleep (5)
    # espero en este bucle hasta que se ha alcanzado a altura indicada
    while True:
        msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=3)
        if msg:
            msg = msg.to_dict()
            vx =  float(msg['vx'])
            vy = float(msg['vy'])
            vz = float(msg['vz'])
            speed = math.sqrt( vx*vx+vy*vy+vz*vz)/100
            if speed < 0.1:
                break
            time.sleep(0.25)

    # meter aqui un bucle esperando hasta que haya llegado
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

def move_distance(self, direction, distance, blocking=True, callback=None, params = None):
    if blocking:
        self._move_distance(direction, distance)
    else:
        moveThread = threading.Thread(target=self._move_distance, args=[direction, distance, callback, params,])
        moveThread.start()
        return True




def setMoveSpeed (self, speed):
    print ('fijamos la velocidad ya ', speed)
    msg = self.vehicle.mav.command_long_encode(
        0, 0,  # Sistema y componente (0 para sistema no tripulado)
        mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,  # Comando para cambiar la velocidad de navegación
        0,  # Confirmando
        0,  # Velocidad vertical (sin cambios)
        speed,  # Velocidad de navegación (m/s)
        -1,  # Velocidad máxima (-1 para no limitar)
        0, 0, 0, 0)  # Parámetros adicionales (no utilizados)
    self.vehicle.mav.send(msg)

