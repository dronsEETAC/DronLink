
import threading
from pymavlink import mavutil


def _buildScenario (self, fencePoints):
    scenario = []
    # el primer item de la lista debe ser el primer punto del fence de inclusión
    item = fencePoints[0]
    if item.command == 5001:
        # es un poligono de inclusión
        fence = {
            'type': 'polygon',
            'waypoints' : []
        }
        num = int (item.param1) # este es el número de puntos del polígono
        lat = float(item.x / 10 ** 7)
        lon = float(item.y / 10 ** 7)
        fence['waypoints'].append ({'lat': lat, 'lon': lon})
        for i in range (1,num):
            # vamos a por el resto de puntos del poligono de inclusión
            item = fencePoints[i]
            lat = float(item.x / 10 ** 7)
            lon = float(item.y / 10 ** 7)
            fence['waypoints'].append({'lat': lat, 'lon': lon})
        idx = num
    else:
        # es un circulo
        fence = {
            'type': 'circle',
            'radius': item.param1,
            'lat':  float(item.x / 10 ** 7),
            'lon': float(item.y / 10 ** 7)
        }
        idx = 1
    scenario.append (fence)
    if len (fencePoints) == num:
        # ya no hay fences de exclusión en el escenario
        return scenario
    else:
        # hay fences de exclusión (obstaculos)
        done = False
        while not done:
            item = fencePoints[idx]
            if item.command == 5002:
                # es un poligono de exclusión
                fence = {
                    'type': 'polygon',
                    'waypoints': []
                }

                num = int(item.param1)  # este es el número de puntos del polígono
                lat = float(item.x / 10 ** 7)
                lon = float(item.y / 10 ** 7)
                fence['waypoints'].append({'lat': lat, 'lon': lon})
                for i in range(idx+1, idx+num):
                    # vamos a por el resto de puntos del poligono de inclusión
                    item = fencePoints[i]
                    lat = float(item.x / 10 ** 7)
                    lon = float(item.y / 10 ** 7)
                    fence['waypoints'].append({'lat': lat, 'lon': lon})
                idx = idx + num
            else:
                # es un circulo
                fence = {
                    'type': 'circle',
                    'radius': item.param1,
                    'lat': float(item.x / 10 ** 7),
                    'lon': float(item.y / 10 ** 7)
                }
                idx = idx + 1
            scenario.append(fence)

            if idx == len(fencePoints):
                done = True

        return scenario


def _getScenario(self, callback=None):
    #pido el número de puntos del geofence
    self.vehicle.mav.param_request_read_send(
        self.vehicle.target_system,self.vehicle.target_component,
        'FENCE_TOTAL'.encode(encoding="utf-8"),
        -1
    )
    message = self.vehicle.recv_match(type='PARAM_VALUE', blocking=True).to_dict()

    total = int(message["param_value"])
    if total == 0:
        # no hay fence
        return None
    else:
        fencePoints = []
        idx = 0
        while idx < total:
            # solicito el punto siguiente
            self.vehicle.mav.mission_request_int_send(self.vehicle.target_system, self.vehicle.target_component, idx,
                                                mavutil.mavlink.MAV_MISSION_TYPE_FENCE)

            msg = self.vehicle.recv_match(type=['MISSION_ITEM_INT'], blocking=True, timeout=1)
            if msg is None:
                break
            fencePoints.append (msg)
            idx = idx + 1


    scenario = self._buildScenario (fencePoints)

    if callback != None:
        if self.id == None:
            callback(scenario)
        else:
            callback(self.id, scenario)
    else:
        return scenario


def getScenario(self, blocking=True, callback=None):
    if blocking:
        return self._getScenario()
    else:
        getScenarioThread= threading.Thread(target=self._getScenario, args=[callback])
        getScenarioThread.start()

def _setScenario(self, scenario, callback=None, params = None):
    '''
    El escenario se recibe en forma de lista. En cada posición hay un fence que representan areas.
    El primer elemento de la lista es un fence de inclusión, que representa el área de la que el dron no va a salir.
    El resto de elementos de la lista son fences de exclusión que representan obstaculos dentro del fence de inclusión,
    que el dron no puede sobrevolar. El escenario debe tener un fence de inclusión (solo uno y es el primer elemento
    de la lista) y un número variable de fences de exclusión, que puede ser 0.
    Un fence (tanto de inclusión como de exclusión) puede ser de tipo 'polygon' o de tipo 'circle'. En el primer caso
    el fence se caracteriza por un número variable de waypoints (lat, lon). Deben ser al menos 3 puesto que representan
    los vértices del poligono. Si el fence es de tipo 'circle' debe especificarse las coordenadas (lat, lon) del centro del
    círculo y el radio en metros.
    Un ejemplo de scenario en el formato correcto es este:
    scenario = [
            {
                'type': 'polygon',
                'waypoints': [
                    {'lat': 41.2764398, 'lon': 1.9882585},
                    {'lat': 41.2761999, 'lon': 1.9883537},
                    {'lat': 41.2763854, 'lon': 1.9890994},
                    {'lat': 41.2766273, 'lon': 1.9889948}
                ]
            },
            {
                'type': 'polygon',
                'waypoints': [
                    {'lat': 41.2764801, 'lon': 1.9886541},
                    {'lat': 41.2764519, 'lon': 1.9889626},
                    {'lat': 41.2763995, 'lon': 1.9887963},
                ]
            },
            {
                'type': 'polygon',
                'waypoints': [
                    {'lat': 41.2764035, 'lon': 1.9883262},
                    {'lat': 41.2762160, 'lon': 1.9883537},
                    {'lat': 41.2762281, 'lon': 1.9884771}
                ]
            },
            {
                'type': 'circle',
                'radius': 2,
                'lat': 41.2763430,
                'lon': 1.9883953
            }
        ]

    El escenario tiene 4 fences. El primero es el de inclusión, de tipo 'polygon'. Luego tiene 3 fences de exclusión que
    representan los obstaculos. Los dos primeros son de tipo 'polygon' y el tercero es de tipo 'circle'.

    '''
    wploader = [] # aqui prepararemos lo comandos correspondientes a cada item del escenario
    seq = 0
    # el fence de inclusión es el primero de la lista
    inclusionFence = scenario[0]
    if inclusionFence['type'] == 'polygon':
        waypoints = inclusionFence ['waypoints']

        for wp in waypoints:
            # para cada waypoint añadimos el comando corresponiente
            wploader.append(mavutil.mavlink.MAVLink_mission_item_int_message(
                self.vehicle.target_system,
                self.vehicle.target_component,
                seq,  # número de secuencia de los comandos que vamos a enviar para crear el escenario
                mavutil.mavlink.MAV_FRAME_GLOBAL,
                mavutil.mavlink.MAV_CMD_NAV_FENCE_POLYGON_VERTEX_INCLUSION,
                0,
                True,
                len(waypoints),  # aqui se indica el número de waypoints del fence
                0.0,  # param2,
                0.0,  # param3
                0.0,  # param4
                int(wp['lat'] * 1e7),  # x (latitude)
                int(wp['lon'] * 1e7),  # y (longitude)
                0,  # z (altitude)
                mavutil.mavlink.MAV_MISSION_TYPE_FENCE,
            ))

            seq += 1

    else:
        # en este caso solo hay que añadir un comando
        wploader.append(mavutil.mavlink.MAVLink_mission_item_int_message(
            self.vehicle.target_system,
            self.vehicle.target_component,
            0,  # seq
            mavutil.mavlink.MAV_FRAME_GLOBAL,  # frame
            mavutil.mavlink.MAV_CMD_NAV_FENCE_CIRCLE_EXCLUSION,  # command
            0,  # current
            0,  # autocontinue
            inclusionFence ['radius'],  # radio del circulo,
            0.0,  # param2,
            0.0,  # param3
            0.0,  # param4
            int( inclusionFence ['lat'] * 1e7),  # centro del círculo (lat)
            int( inclusionFence ['lon'] * 1e7),  # centro del círculo (lon)
            0,  # z (altitude)
            mavutil.mavlink.MAV_MISSION_TYPE_FENCE,
        ))
        seq = 1

    if len(scenario) > 1:
        # hay fences de exclusión
        for obstacle in scenario [1:]:
            if obstacle ['type'] == 'polygon':
                waypoints = obstacle['waypoints']
                for wp in waypoints:
                    wploader.append(mavutil.mavlink.MAVLink_mission_item_int_message(
                        self.vehicle.target_system,
                        self.vehicle.target_component,
                        seq,  # seq
                        mavutil.mavlink.MAV_FRAME_GLOBAL,
                        mavutil.mavlink.MAV_CMD_NAV_FENCE_POLYGON_VERTEX_EXCLUSION,
                        0,
                        True,
                        len(waypoints),  # param1,
                        0.0,  # param2,
                        0.0,  # param3
                        0.0,  # param4
                        int(wp['lat'] * 1e7),  # x (latitude)
                        int(wp['lon'] * 1e7),  # y (longitude)
                        0,  # z (altitude)
                        mavutil.mavlink.MAV_MISSION_TYPE_FENCE,
                    ))

                    seq += 1
            else:
                wploader.append(mavutil.mavlink.MAVLink_mission_item_int_message(
                    self.vehicle.target_system,
                    self.vehicle.target_component,
                    seq,  # seq
                    mavutil.mavlink.MAV_FRAME_GLOBAL,  # frame
                    mavutil.mavlink.MAV_CMD_NAV_FENCE_CIRCLE_EXCLUSION,  # command
                    0,  # current
                    0,  # autocontinue
                    obstacle['radius'],  # radio del circulo,
                    0.0,  # param2,
                    0.0,  # param3
                    0.0,  # param4
                    int(obstacle['lat'] * 1e7),
                    int(obstacle['lon'] * 1e7),
                    0,  # z (altitude)
                    mavutil.mavlink.MAV_MISSION_TYPE_FENCE,
                ))
                seq += 1

    # indicamos el número total de comandos que tenemos que enviar para crear el escenario
    self.vehicle.mav.mission_count_send(
        self.vehicle.target_system,
        self.vehicle.target_component,
        len (wploader),
        mission_type=mavutil.mavlink.MAV_MISSION_TYPE_FENCE
    )
    arm_msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
    # ahora enviamos los comandos
    while True:
        # esperamos a que nos pida el siguiente
        msg = self.vehicle.recv_match(type=['MISSION_REQUEST'], blocking=True)
        print(f'Sending waypoint {msg.seq}/{len(wploader) - 1}')
        self.vehicle.mav.send(wploader[msg.seq])
        if msg.seq == len(wploader) - 1:
            # ya los hemos enviado todos
            break

    msg = self.vehicle.recv_match(type='MISSION_ACK', blocking=True)


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

def setScenario (self,scenario, blocking=True, callback=None, params = None):
    if blocking:
        return self._setScenario(scenario)
    else:
        scenarioThread = threading.Thread(target=self._setScenario, args=[scenario,callback, params])
        scenarioThread.start()