import json
import threading

import pymavlink
from pymavlink.mavutil import default_native
import pymavlink.dialects.v20.all as dialect
from pymavlink import mavutil
import time

def _setGEOFence(self, fence_waypoints, callback=None, params = None):
    fence_list = fence_waypoints
    #indico el número de waypints del fence
    FENCE_TOTAL = "FENCE_TOTAL".encode(encoding="utf-8")
    #El primero se envía tres veces (una como FENCE_RETURN_POINT, otra como primer punto del fence y otra como
    # último punto que cierra el fence
    fence_points = len(fence_list)+2

    # indico el número de puntos
    message = dialect.MAVLink_param_set_message(target_system=self.vehicle.target_system,
                                                    target_component=self.vehicle.target_component,
                                                    param_id=FENCE_TOTAL, param_value=fence_points,
                                                    param_type=dialect.MAV_PARAM_TYPE_REAL32)
    self.vehicle.mav.send(message)
    message = self.vehicle.recv_match(type="PARAM_VALUE", blocking=True, timeout=3)

    # el primer wp lo envio primero para que haga de FENCE_RETURN_POINT
    message = dialect.MAVLink_fence_point_message(target_system=self.vehicle.target_system,
                                                  target_component=self.vehicle.target_component,
                                                  idx=0, count=fence_points, lat=fence_list[0]['lat'],
                                                  lng=fence_list[0]['lon'])
    self.vehicle.mav.send(message)

    idx = 0
    while idx < len(fence_list):
        message = dialect.MAVLink_fence_point_message(target_system=self.vehicle.target_system,
                                                      target_component=self.vehicle.target_component,
                                                      idx=idx, count=fence_points, lat=fence_list[idx]['lat'],
                                                      lng=fence_list[idx]['lon'])
        self.vehicle.mav.send(message)
        idx = idx + 1

    # envio de nuevo el primero para que cierra el poligono
    message = dialect.MAVLink_fence_point_message(target_system=self.vehicle.target_system,
                                                      target_component=self.vehicle.target_component,
                                                      idx=idx, count=fence_points, lat=fence_list[0]['lat'],
                                                      lng=fence_list[0]['lon'])
    self.vehicle.mav.send(message)

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


def setGEOFence(self, fence_waypoints, blocking=True, callback=None, params = None):
    if blocking:
        self._setGEOFence(fence_waypoints)
    else:
        setGEOFenceThread= threading.Thread(target=self._setGEOFence, args=[fence_waypoints, callback, params])
        setGEOFenceThread.start()


def _getGEOFence(self, callback=None):
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
        fencePoints = None
    else:
        fencePoints = []
        idx = 0
        while idx < total:
            # solicito el punto siguiente
            message = dialect.MAVLink_fence_fetch_point_message(target_system=self.vehicle.target_system,
                                                                target_component=self.vehicle.target_component,
                                                                idx=idx)
            self.vehicle.mav.send(message)

            # espero que me llegue el punto solicitado
            message = self.vehicle.recv_match(type=dialect.MAVLink_fence_point_message.msgname,
                                        blocking=True)
            message = message.to_dict()
            latitude = message["lat"]
            longitude = message["lng"]
            fencePoints.append ({
                'lat': latitude,
                'lon': longitude
            })
            idx = idx + 1
    # elimino el primer punto y el último
    fencePoints = fencePoints[1:-1]
    if callback != None:
        if self.id == None:
            callback(fencePoints)
        else:
            callback(self.id, fencePoints)
    else:
        return fencePoints


def getGEOFence(self, blocking=True, callback=None):
    if blocking:
        return self._getGEOFence()
    else:
        getGEOFenceThread= threading.Thread(target=self._getGEOFence, args=[callback])
        getGEOFenceThread.start()

