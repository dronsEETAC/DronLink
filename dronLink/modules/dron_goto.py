import math
import threading
import time
from pymavlink import mavutil

# Los métodos de uso interno tiene un _ al inicio del nombre
# La filosofía es poner en marcha un thread para que haga el trabajo
# y liberar lo antes posible on_message. Hasta que no se libere esa función
# no se va a recibir ni enviar nada (por ejemplo, no se van a enviar los datos de telemetría).

def _distanceToDestinationInMeters(self, lat,lon):
    dlat = self.lat - lat
    dlong = self.lon - lon
    return math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5

def _distancia_geografica(self, pos1, pos2):
    """
    Calcula la distancia 3D entre dos puntos geográficos (lat, lon, alt).
    Parámetros:
        pos1, pos2: tuplas (lat, lon, alt) en grados y metros
    Retorna:
        distancia en metros (float)
    """
    # Radio medio de la Tierra (en metros)
    R = 6371000.0

    lat1, lon1, alt1 = pos1
    lat2, lon2, alt2 = pos2

    # Convertir grados a radianes
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    # Fórmula de Haversine para distancia horizontal
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distancia_horizontal = R * c

    # Diferencia de altitud
    delta_alt = alt2 - alt1

    # Distancia total 3D
    distancia_total = math.sqrt(distancia_horizontal**2 + delta_alt**2)

    return distancia_total
def _checkGlobalArrived (self, msg, destino):
    posicion = [float(msg.lat / 10 ** 7),float(msg.lon / 10 ** 7),float(msg.relative_alt / 1000)  ]
    distancia = self._distancia_geografica(posicion, destino)

    print (distancia)
    return distancia < 0.5


def _goto (self, lat, lon, alt, callback=None, params = None):
    # detenemos el modo navegación
    self._stopGo()
    self.vehicle.mav.send(
        mavutil.mavlink.MAVLink_set_position_target_global_int_message(10, self.vehicle.target_system,
                                                                       self.vehicle.target_component,
                                                                       mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                                                       int(0b110111111000), int(lat * 10 ** 7),
                                                                       int(lon * 10 ** 7), alt, 0, 0, 0, 0, 0, 0, 0,
                                                                       0))

    msg = self.message_handler.wait_for_message(
        'GLOBAL_POSITION_INT',
        condition=self._checkGlobalArrived,
        params=(lat, lon, alt)
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


def goto(self, lat, lon, alt, blocking=True, callback=None, params = None):
    if blocking:
        self._goto(lat, lon, alt)
    else:
        gotoThread = threading.Thread(target=self._goto, args=[lat, lon, alt, callback, params])
        gotoThread.start()


def _checkLocalArrived (self, msg, destination):
    dx = msg.x - destination[0]
    dy = msg.y - destination[1]
    dz = -msg.z - destination[2]
    distance = math.sqrt(dx*dx+dy*dy+dz*dz)
    return distance < 0.5


def _gotoLocal (self, x, y, z,  callback=None, params = None):
    # detenemos el modo navegación
    self._stopGo()
    self.vehicle.mav.set_position_target_local_ned_send(
        10, self.vehicle.target_system,
        self.vehicle.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        int(0b0000111111111000),
        float(x),float(y), float(-z),
        0, 0, 0, 0, 0, 0, 0,0)

    msg = self.message_handler.wait_for_message(
        'LOCAL_POSITION_NED',
        condition=self._checkLocalArrived,
        params=(x,y,z)
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


def gotoLocal(self, x,y,z, blocking=True, callback=None, params = None):
    if blocking:
        self._gotoLocal(x,y,z)
    else:
        gotoThread = threading.Thread(target=self._gotoLocal, args=[x,y,z, callback, params])
        gotoThread.start()
