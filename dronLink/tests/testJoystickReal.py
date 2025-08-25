from JoystickReal import *

from dronLink.Dron import Dron
import keyboard # instalar keyboard

def identifica (id):
    print ("Soy el joystick: ", id)

print ('vamos a empezar')
dron = Dron ()
dron.connect ('tcp:127.0.0.1:5762', 115200)

joystick = Joystic (0, dron, identifica)
print ("Conectado al dron")
while True:
    #time.sleep(1)
    if keyboard.is_pressed('p'):
        break
joystick.stop()
print ("Fin")