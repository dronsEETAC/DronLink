import time
from pymavlink import mavutil
import threading


def _change_altitude(self, altitude, callback=None, params = None):
    # Change the altitude of the vehicle while flying
    self.reaching_waypoint = True
    self.vehicle.mav.send(
        mavutil.mavlink.MAVLink_set_position_target_global_int_message(1, self.vehicle.target_system,
                                                                       self.vehicle.target_component,
                                                                       mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                                                       int(0b110111111000), int(self.lat * 10 ** 7),
                                                                       int(self.lon * 10 ** 7), altitude, 0, 0, 0, 0, 0,
                                                                       0, 0,
                                                                       0))
    # espero hasta que el dron haya alcanzado la altura indicada

    msg = self.message_handler.wait_for_message(
        'GLOBAL_POSITION_INT',
        condition=self._checkAltitudeReached,
        params=altitude
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




def change_altitude(self, altitude, blocking=True, callback=None, params = None):
    # solo puedo cambiar la altura si estoy volando
    if self.state == "flying":
        if blocking:
            self._change_altitude(altitude)
        else:
            changeAltThread = threading.Thread(target=self._change_altitude, args=[altitude, callback, params])
            changeAltThread.start()
        return True
    else:
        return False