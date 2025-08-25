import threading
from pymavlink import mavutil
import pymavlink.dialects.v20.all as dialect

def _checkHeadingReached (self, msg, absoluteDegrees):
    heading =float (msg.hdg/ 100)
    if abs(heading-absoluteDegrees) < 5:
        return True
    else:
        return False


def fixHeading (self):
    # al fijar el heading el dron no cambiará de heading sea cual sea la dirección de navegación
    message = dialect.MAVLink_param_set_message(target_system=self.vehicle.target_system,
                                                        target_component=self.vehicle.target_component, param_id='WP_YAW_BEHAVIOR'.encode("utf-8"),
                                                        param_value=0, param_type=dialect.MAV_PARAM_TYPE_REAL32)
    self.vehicle.mav.send(message)

def unfixHeading (self):
    # al des-fijar el heading el dron cambiará el heading según la dirección de navegación.
    message = dialect.MAVLink_param_set_message(target_system=self.vehicle.target_system,
                                                        target_component=self.vehicle.target_component, param_id='WP_YAW_BEHAVIOR'.encode("utf-8"),
                                                        param_value=1, param_type=dialect.MAV_PARAM_TYPE_REAL32)
    self.vehicle.mav.send(message)


def _changeHeading (self, absoluteDegrees, callback=None, params = None):
    # para cambiar el heading en necesario detener el modo navegación
    self._stopGo()
    self.vehicle.mav.command_long_send(
        self.vehicle.target_system,
        self.vehicle.target_component,
        mavutil.mavlink.MAV_CMD_CONDITION_YAW,
        0,
        absoluteDegrees,  # param 1, yaw in degrees
        15, # param 2, yaw speed deg/s
        1, # param 3, direction -1 ccw, 1 cw
        0, # param 4, relative offset 1, absolute angle 0
        0, 0, 0, 0) # not used

    # espero hasta que haya alcanzado la orientación indicada
    msg = self.message_handler.wait_for_message(
        'GLOBAL_POSITION_INT',
        condition = self._checkHeadingReached,
        params = absoluteDegrees
    )
    '''while True:
        msg = self.message_handler.wait_for_message('GLOBAL_POSITION_INT', timeout=3)
        if msg:
            msg = msg.to_dict()
            heading = float(msg['hdg'] / 100)
            if abs(heading-absoluteDegrees) < 5:
                break
            time.sleep(0.25)'''
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

def _rotate (self, offset,direction = 'cw', callback=None, params = None):
    # para cambiar el heading en necesario detener el modo navegación
    self._stopGo()
    if direction == 'cw':
        dir = 1
        finalHeading = self.heading + offset
        if finalHeading > 360:
            finalHeading = finalHeading - 360
    else:
        dir = -1
        finalHeading = self.heading - offset
        if finalHeading < 0:
            finalHeading = finalHeading + 360
    self.vehicle.mav.command_long_send(
        self.vehicle.target_system,
        self.vehicle.target_component,
        mavutil.mavlink.MAV_CMD_CONDITION_YAW,
        0,
        offset,  # param 1, yaw in degrees
        15, # param 2, yaw speed deg/s
        dir, # param 3, direction -1 ccw, 1 cw
        1, # param 4, relative offset 1, absolute angle 0
        0, 0, 0, 0) # not used

    # espero hasta que haya alcanzado la orientación indicada
    msg = self.message_handler.wait_for_message(
        'GLOBAL_POSITION_INT',
        condition = self._checkHeadingReached,
        params = finalHeading
    )
    '''while True:
        msg = self.message_handler.wait_for_message('GLOBAL_POSITION_INT', timeout=3)
        if msg:
            msg = msg.to_dict()
            heading = float(msg['hdg'] / 100)
            if abs(heading-absoluteDegrees) < 5:
                break
            time.sleep(0.25)'''
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



def changeHeading (self, absoluteDegrees,blocking=True, callback=None, params = None):
    if self.state == 'flying':
        if blocking:
            self._changeHeading(absoluteDegrees)
        else:
            changeHeadingThread = threading.Thread(target=self._changeHeading, args=[absoluteDegrees, callback, params])
            changeHeadingThread.start()
        return True
    else:
        return False

def rotate (self,offset, direction = 'cw', blocking=True, callback=None, params = None):
    if self.state == 'flying':
        if blocking:
            self._rotate(offset, direction)
        else:
            changeHeadingThread = threading.Thread(target=self._rotate, args=[offset,direction, callback, params])
            changeHeadingThread.start()
        return True
    else:
        return False


