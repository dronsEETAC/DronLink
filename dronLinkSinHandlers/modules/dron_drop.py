import threading
import time

from pymavlink import mavutil
'''import board
import neopixel
import RPi.GPIO as GPIO
pixels = neopixel.NeoPixel(board.D18, 5)
servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50)  # GPIO 17 for PWM with 50Hz
p.start(2)

# en el caso de control por RPi


if command == 'drop':
    print('drop real')
    p.ChangeDutyCycle(7.5)
    time.sleep(1)
    p.ChangeDutyCycle(2)

if command == 'reset':
    p.ChangeDutyCycle(2.5)'''

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
