import threading
import time
from pymavlink import mavutil

def _takeOff(self, aTargetAltitude,callback=None, params = None):
    self.state = "takingOff"
    self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component,
                                         mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, aTargetAltitude)

    # espero en este bucle hasta que se ha alcanzado a altura indicada
    while True:
        msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=3)
        if msg:
            msg = msg.to_dict()
            alt = float(msg['relative_alt'] / 1000)
            if alt >= aTargetAltitude * 0.90:
                break
            time.sleep(0.25)


    self.state = "flying"
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



def takeOff(self, aTargetAltitude, blocking=True, callback=None, params = None):
    if self.state == 'armed':
        if blocking:
            self._takeOff(aTargetAltitude)
        else:
            takeOffThread = threading.Thread(target=self._takeOff, args=[aTargetAltitude, callback, params])
            takeOffThread.start()
        return True
    else:
        return False
