import json
import math
import threading
import time
from pymavlink import mavutil

from pymavlink import mavutil



def _getMission (self, callback=None, params = None):
    mission = None
    # Solicitar la misión (waypoints) al autopiloto
    self.vehicle.mav.mission_request_list_send( self.vehicle.target_system,  self.vehicle.target_component)
    # espero el numero de waypoints
    msg = self.message_handler.wait_for_message('MISSION_COUNT')
    count = msg.count
    print ('count: ', count)
    if count < 2:
        # no hay misión
            return None
    # Solicitar cada waypoint
    for i in range(count):
        self.vehicle.mav.mission_request_int_send( self.vehicle.target_system,  self.vehicle.target_component, i)
    mission = {
        'takeOffAlt': None,
        'waypoints': []
    }
    # ahora espero los waypoints
    fin = False
    while not fin:
        msg = self.message_handler.wait_for_message('MISSION_ITEM_INT')
        if msg.seq == 1:
            # este es el waypoint que indica la altura de despeque
            mission['takeOffAlt'] =  msg.z,
        elif msg.seq in range (2, count-1):
             # este es uno waypoints que hay que volar
                mission ['waypoints'].append ({'lat':msg.x * 1e-7, 'lon':msg.y * 1e-7, 'alt':msg.z })
        elif msg.seq == count-1:
            # este waypoint es el RTL
            fin = True

    if callback != None:
        if self.id == None:
            callback(mission)
        else:
            callback(self.id, mission)
    else:
        return mission


def _uploadMission (self, mission, callback=None, params = None):
    '''La mision debe especificarse con el formato de este ejemplo:
        {
            "speed": 7,
            "takeOffAlt": 5,
            "waypoints":
                [
                    {
                        'lat': 41.2763410,
                        'lon': 1.9888285,
                        'alt': 12
                    },
                    {'rotAbs': 90},
                    {
                        'lat': 41.27623,
                        'lon': 1.987,
                        'alt': 14
                    }
                    {'rotRel': 90, 'dir': -1},
                ]

        }
        El dron armará, despegara hasta la altura indicada, navegará por los waypoints y acabará
        con un RTL
        '''



    takOffAlt = mission['takeOffAlt']

    waypoints = mission['waypoints']

    # preparamos la misión para cargarla en el dron

    wploader = []
    seq = 0  # Waypoint sequence begins at 0


    # El primer wp debe ser la home position.
    # Averiguamos la home position
    self.vehicle.mav.command_long_send(
        self.vehicle.target_system,
        self.vehicle.target_component,
        mavutil.mavlink.MAV_CMD_GET_HOME_POSITION,
        0, 0, 0, 0, 0, 0, 0, 0)
    print ('voy a pedir el home')
    msg = self.message_handler.wait_for_message('HOME_POSITION')
    #msg = self.vehicle.recv_match(type='HOME_POSITION', blocking=True)
    msg = msg.to_dict()
    lat = msg['latitude']
    lon = msg['longitude']
    alt = msg['altitude']

    print ('ya tengo el home')

    # añadimos este primer waypoint a la mision
    wploader.append(mavutil.mavlink.MAVLink_mission_item_int_message(
        0, 0, seq, 0, 16, 0, 0, 0, 0, 0, 0,
        lat,
        lon,
        alt
    ))
    seq += 1

    # El siguiente elemento de la mision debe ser el comando de takeOff, en el que debemos indicar una posición
    # que será también la home position

    wploader.append(mavutil.mavlink.MAVLink_mission_item_int_message(
        self.vehicle.target_system, self.vehicle.target_component, seq,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, True,
        0, 0, 0, 0,
        lat, alt, takOffAlt
    ))
    seq += 1

    # Ahora añadimos los waypoints de la ruta
    for wp in waypoints:
        if 'lat' in list(wp.keys()):
            wploader.append(mavutil.mavlink.MAVLink_mission_item_int_message(
                self.vehicle.target_system, self.vehicle.target_component, seq,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, True,
                0, 0, 0, 0,
                int(wp["lat"] * 10 ** 7), int(wp["lon"] * 10 ** 7), int(wp["alt"])
            ))
            seq += 1  # Increase waypoint sequence for the next waypoint
        if 'rotAbs' in list(wp.keys()):
            heading = wp['rotAbs']
            print ('heading ', heading)
            wploader.append(mavutil.mavlink.MAVLink_mission_item_int_message(
                self.vehicle.target_system, self.vehicle.target_component, seq,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0, True,
                int(heading), # heading
                int (45), # velocidad de rotacion
                int (1), # -1 ccw, 1 cw
                int (0), # 0 absoluto, 1 relativo
                0,0,0
            ))
            seq += 1  # Increase waypoint sequence for the next waypoint'''
            wploader.append(mavutil.mavlink.MAVLink_mission_item_int_message(
                self.vehicle.target_system, self.vehicle.target_component, seq,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                93, 0, True,
                int(5),  # segundos
                0,0,0,
                0, 0, 0
            ))
            seq += 1  # Increase waypoint sequence for the next waypoint'''

        if 'rotRel' in list(wp.keys()):
            angle = wp['rotRel']
            dir = wp['dir']
            wploader.append(mavutil.mavlink.MAVLink_mission_item_int_message(
                self.vehicle.target_system, self.vehicle.target_component, seq,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0, True,
                int(angle),
                int(45),  # velocidad de rotacion
                int(dir),  # -1 ccw, 1 cw
                int(1),  # 0 absoluto, 1 relativo
                0, 0, 0
            ))
            seq += 1  # Increase waypoint sequence for the next waypoint'''
            wploader.append(mavutil.mavlink.MAVLink_mission_item_int_message(
                self.vehicle.target_system, self.vehicle.target_component, seq,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                93, 0, True,
                int(5),  # segundos
                0, 0, 0,
                0, 0, 0
            ))
            seq += 1  # Increase waypoint sequence for the next waypoint'''

    # añadimos para acabar un RTL
    wploader.append(mavutil.mavlink.MAVLink_mission_item_int_message(
        self.vehicle.target_system, self.vehicle.target_component, seq,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, True,
        0, 0, 0, 0,
        0, 0, 0
    ))
    # borramos la misión que tiene ahora el autopiloto
    self.vehicle.mav.mission_clear_all_send( self.vehicle.target_system,  self.vehicle.target_component)
    '''msg = None
    while not msg:
        msg = self.vehicle.recv_match(type='MISSION_ACK', blocking=True, timeout = 3)'''
    msg = self.message_handler.wait_for_message('MISSION_ACK', timeout=3)
    # miro si tengo que fijar la velocidad de navegación
    if 'speed' in list(mission.keys()):
        speed = mission['speed']*100    # la velocidad viene en m y hay que indicarla en cm
        speedParameter = [{'ID': "WPNAV_SPEED", 'Value': speed}]
        self.setParams(speedParameter)


    # Enviamos el numero de items de la nueva misión
    self.vehicle.waypoint_count_send(len(wploader))

    # Enviamos los items
    print ('vamos a enviar los items')

    for i in range(len(wploader)):
        msg = self.message_handler.wait_for_message('MISSION_REQUEST')
        #msg = self.vehicle.recv_match(type=['MISSION_REQUEST_INT', 'MISSION_REQUEST'], blocking=True, timeout = 3)
        print(f'Sending waypoint {msg.seq}/{len(wploader) - 1}')
        self.vehicle.mav.send(wploader[msg.seq])

        if msg.seq == len(wploader) - 1:
            break


    msg = self.message_handler.wait_for_message('MISSION_ACK', timeout=3)

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




def _executeMission (self, callback=None, params = None):

    mode = 'GUIDED'
    # Get mode ID
    mode_id = self.vehicle.mode_mapping()[mode]
    self.vehicle.mav.set_mode_send(
        self.vehicle.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id)
    #arm_msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True, timeout =3)
    msg = self.message_handler.wait_for_message('COMMAND_ACK', timeout=3)


    self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component,
                                         mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
    self.vehicle.motors_armed_wait()

    self.vehicle.mav.command_long_send(
        self.vehicle.target_system,
        self.vehicle.target_component,
        mavutil.mavlink.MAV_CMD_MISSION_START,
        0, 0, 0, 0, 0, 0, 0, 0)

    self.state = 'flying'
    # esperamos a que acabe la mision
    time.sleep(10)
    msg = self.message_handler.wait_for_message(
        'GLOBAL_POSITION_INT',
        condition=self._checkOnHearth,
    )
    '''while True:
        msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout = 3)
        if msg:
            msg = msg.to_dict()
            alt = float(msg['relative_alt'] / 1000)
            if alt < 0.5:
                break
        time.sleep(0.1)'''
    self.state = 'connected'
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


def uploadMission(self,mission, blocking=True, callback=None, params = None):
    if blocking:
        self._uploadMission(mission)
    else:
        missionThread = threading.Thread(target=self._uploadMission, args=[mission, callback, params])
        missionThread.start()


def executeMission(self, blocking=True, callback=None, params = None):
    if blocking:
        self._executeMission()
    else:
        missionThread = threading.Thread(target=self._executeMission, args=[callback, params])
        missionThread.start()

def getMission(self, blocking=True, callback=None, params = None):
    if blocking:
        return self._getMission()
    else:
        getMissionThread = threading.Thread(target=self._getMission, args=[callback, params])
        getMissionThread.start()