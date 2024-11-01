import threading
import time

from pymavlink import mavutil

# en el caso de control por radio de telemetria
def drop(self):
    self.vehicle.mav.command_long_send(
            self.vehicle.target_system, self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
            11,  # servo output number
            2006,  # PWM value
            0, 0, 0, 0, 0)

    time.sleep(1)
    self.vehicle.mav.command_long_send(
            0, 0, mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
            11,  # servo output number
            1000,  # PWM value
            0, 0, 0, 0, 0)

    time.sleep(2)
