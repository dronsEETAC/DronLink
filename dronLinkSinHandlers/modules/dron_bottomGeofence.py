import threading
import time
from pymavlink import mavutil

def _minAltChecking (self, processBreach = None):

    while self.checkMinAlt:
        print ('modo ', self.flightMode, 'state ', self.state)
        if self.state == 'flying' and self.flightMode != 'LAND' and self.flightMode != 'RTL':
            # si estoy retornando o aterrizando no quiero que actue el geofence
            msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=3)
            if msg:
                msg = msg.to_dict()
                alt = float(msg['relative_alt'] / 1000)
                if alt < self.minAltGeofence:
                    # se ha producido el breach
                    if processBreach != None:
                        processBreach ('breach')
                    # me guardo el modo de vuelo en el que estoy para recuperarlo luego
                    mode = self.flightMode

                    # me pongo en modo GUIDED
                    mode_id = self.vehicle.mode_mapping()['GUIDED']
                    self.vehicle.mav.set_mode_send(
                        self.vehicle.target_system,
                        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id)
                    msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
                    self.flightMode = 'GUIDED'
                    # preparo el comando para elevar la altura del dron 1 metro
                    cmd = mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
                            10,  # time_boot_ms (not used)
                            self.vehicle.target_system,
                            self.vehicle.target_component,
                            mavutil.mavlink.MAV_FRAME_LOCAL_OFFSET_NED,  # frame
                            0b110111111000,  # type_mask (only speeds enabled)
                            0,
                            0,
                            -1,  # x, y, z positions (not used)
                            0,
                            0,
                            0,  # x, y, z velocity in m/s
                            0,
                            0,
                            0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
                            0,
                            0,
                        )  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

                    alt = 0
                    while alt < self.minAltGeofence:
                        # le indico al dron que se eleve metro a metro hasta que esté por encima del límite
                        self.vehicle.mav.send(cmd)
                        time.sleep(0.25)
                        msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=3)
                        if msg:
                            msg = msg.to_dict()
                            alt = float(msg['relative_alt'] / 1000)
                            print ('ya estoy a ', alt)
                    print ('ya estoy arriba')
                    # reestablezco el modo de vuelo que teníamos
                    mode_id = self.vehicle.mode_mapping()['LOITER']
                    self.vehicle.mav.set_mode_send(
                        self.vehicle.target_system,
                        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id)
                    msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)

                    time.sleep(5)
                    self.flightMode = 'LOITER'
                    if processBreach != None:
                        processBreach('in')
        # esto lo hago con mucha frecuencia para disparar el breach justo cuando se produce
        time.sleep (0.25)


def _minAltChecking2 (self, processBreach = None):

    while self.checkMinAlt:
        print ('modo ', self.flightMode, 'state ', self.state)
        if self.state == 'flying' and self.flightMode != 'LAND' and self.flightMode != 'RTL':
            # si estoy retornando o aterrizando no quiero que actue el geofence

            if self.alt < self.minAltGeofence:
                # se ha producido el breach
                if processBreach != None:
                    processBreach ('out')
                # me guardo el modo de vuelo en el que estoy para recuperarlo luego
                mode = self.flightMode

                # me pongo en modo GUIDED
                mode_id = self.vehicle.mode_mapping()['GUIDED']
                self.vehicle.mav.set_mode_send(
                    self.vehicle.target_system,
                    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id)
                msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)

                # preparo el comando para elevar la altura del dron 1 metro
                cmd = mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
                            10,  # time_boot_ms (not used)
                            self.vehicle.target_system,
                            self.vehicle.target_component,
                            mavutil.mavlink.MAV_FRAME_LOCAL_OFFSET_NED,  # frame
                            0b110111111000,  # type_mask (only speeds enabled)
                            0,
                            0,
                            -1,  # x, y, z positions (not used)
                            0,
                            0,
                            0,  # x, y, z velocity in m/s
                            0,
                            0,
                            0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
                            0,
                            0,
                )  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)


                while self.alt < self.minAltGeofence:
                    # le indico al dron que se eleve metro a metro hasta que esté por encima del límite
                    self.vehicle.mav.send(cmd)
                    time.sleep(0.25)


                # reestablezco el modo de vuelo que teníamos
                mode_id = self.vehicle.mode_mapping()[mode]
                self.vehicle.mav.set_mode_send(
                    self.vehicle.target_system,
                    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id)
                msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
                processBreach('in')
        # esto lo hago con mucha frecuencia para disparar el breach justo cuando se produce
        time.sleep (0.25)


def startBottomGeofence (self, minAlt, processBreach = None):
    self.minAltGeofence = minAlt
    self.checkMinAlt = True
    minAltCheckingThreat= threading.Thread(target=self._minAltChecking, args = [processBreach,])
    minAltCheckingThreat.start()


def stopBottomGeofence (self):
    self.checkMinAlt = False
