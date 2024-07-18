import threading
import time
from pymavlink import mavutil

def _goDown(self, mode, callback=None, params = None):
    # detemenos el modo navegación
    self._stopGo()

    # Get mode ID
    mode_id = self.vehicle.mode_mapping()[mode]
    self.vehicle.mav.set_mode_send(
        self.vehicle.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id)
    # esperamos a que el dron esté en tierra
    while True:
        msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout = 3)
        if msg:
            msg = msg.to_dict()
            alt = float(msg['relative_alt'] / 1000)
            if alt < 0.5:
                break
            time.sleep(0.1)

    self.vehicle.motors_disarmed_wait()
    self.state = "connected"
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


def RTL (self, blocking=True, callback=None, params = None):
    if self.state == 'flying':
        self.state = 'returning'
        if blocking:
            self._goDown('RTL')
        else:
            goingDownThread = threading.Thread(target=self._goDown, args=['RTL', callback, params])
            goingDownThread.start()
        return True
    else:
        return False

def Land (self, blocking=True, callback=None, params = None):
    if self.state == 'flying':
        self.state = 'landing'
        if blocking:
            self._goDown('LAND')
        else:
            print ('aterrizo el dron ', self.id)
            goingDownThread = threading.Thread(target=self._goDown, args=['LAND', callback, params])
            goingDownThread.start()
        return True
    else:
        return False

