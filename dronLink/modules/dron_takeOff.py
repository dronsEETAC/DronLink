import threading
import time
from pymavlink import mavutil

def _checkAltitudeReached (self, msg, aTargetAltitude):
    if msg.relative_alt in range (aTargetAltitude  * 1000 -500,  aTargetAltitude  * 1000 +500):
        return True
    else:
        return False

def _takeOff(self, aTargetAltitude,callback=None, params = None):
    print ('empezamos a despegar')
    self.state = "takingOff"
    self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component,
                                         mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, aTargetAltitude)


    # Espero un mensaje que cumpla la condición que se evalua en _check, a la que le paso
    # como parametro la altura a alcanzar. El check solo mira que la altura actual sea la deseada
    print ('vamos a despegar')
    msg = self.message_handler.wait_for_message(
        'GLOBAL_POSITION_INT',
        condition = self._checkAltitudeReached,
        params = aTargetAltitude
    )

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
    print ('vamos a despegar')
    if self.state == 'armed':
        if blocking:
            self._takeOff(aTargetAltitude)
        else:
            takeOffThread = threading.Thread(target=self._takeOff, args=[aTargetAltitude, callback, params])
            takeOffThread.start()
        return True
    else:
        return False
