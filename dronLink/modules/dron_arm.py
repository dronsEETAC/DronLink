import logging
import threading
import time
from os import times_result

from pymavlink import mavutil

def setFlightMode (self,mode):
    # Get mode ID
    mode_id = self.vehicle.mode_mapping()[mode]
    self.vehicle.mav.set_mode_send(
        self.vehicle.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id)
    msg = self.message_handler.wait_for_message('COMMAND_ACK', timeout=3)
    if self.verbose:
        logging.info("Pongo el dron en modo %s", str(mode))

def _arm2(self, callback=None, params = None):
    self.state = "arming"
    self.setFlightMode ('GUIDED')
    self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component,
                                         mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

    msg = self.message_handler.wait_for_message('COMMAND_ACK', timeout=3)
    self.vehicle.motors_armed_wait()

    if self.verbose:
        logging.info("Dron armado")

    self.state = "armed"
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

def _arm(self, callback=None, params = None):
    self.state = "arming"
    self.setFlightMode ('GUIDED')
    self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component,
                                         mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
    msg = self.message_handler.wait_for_message('COMMAND_ACK', timeout=3)
    timeout = 10
    start_time = time.time()
    armed = False
    while time.time() - start_time < timeout:
        if self.vehicle.motors_armed():
            armed = True
            if self.verbose:
                logging.info("Dron armado")
            break
        time.sleep(0.1)
    if not armed:
        self.state = "connected"

        if self.verbose:
            logging.info("El dron no se ha armado: timeout superado")
        return

    self.state = "armed"
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


def arm(self, blocking=True, callback=None, params = None):
    if self.state == 'connected':
        if blocking:
            self._arm()
        else:
            armThread = threading.Thread(target=self._arm, args=[callback, params])
            armThread.start()
        return True
    else:
        return False

