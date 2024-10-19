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



    dist = self._distanceToDestinationInMeters(lat ,lon)
    distanceThreshold = 0.5
    # esperamos hasta que estemos suficientemente cerca del destino
    while dist > distanceThreshold:
        time.sleep(0.1)
        dist = self._distanceToDestinationInMeters(lat, lon)

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

