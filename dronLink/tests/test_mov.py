import json
import time
from dronLink.Dron import Dron

dron = Dron()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200

print ('voy a conectarme')
dron.connect (connection_string, baud)
print ('conectado')
dron.arm()
dron.takeOff (5)
print ('Voy al Norte 20 metros')
dron.move_distance ('North', 20)
print ('Voy al oeste 40 metros')
dron.move_distance ('West', 40)
print ('me muevo arriba 5 metros')
dron.move_distance ('Up', 5)
print ('Voy atras 20 metros')
dron.move_distance ('Back', 20)
print ('me muevo hacia adelante 50 metros')
dron.move_distance ('Forward', 50)
print ('cambio de heading')
dron.changeHeading(275)
print ('me muevo a la izquierda 40 metros')
dron.move_distance ('Left', 40)

dron.RTL()
dron.disconnect()

