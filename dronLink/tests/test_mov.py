import json
import time
from dronLink.Dron import Dron

dron = Dron()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
'''connection_string = 'com8'
baud = 57600'''


print ('voy a conectarme')
dron.connect (connection_string, baud)
print ('conectado')
dron.arm()
print ('despego a 15 metros')
dron.takeOff (15)
print ('pongo valocidad a 1 m/s')
dron.changeNavSpeed(1)
print ('Voy al Norte 20 metros')
dron.move_distance ('North', 20)
print ('Voy al oeste 10 metros')
dron.move_distance ('West', 40)
print ('me muevo arriba 5 metros')
dron.move_distance ('Up', 5)
print ('pongo valocidad a 5 m/s')
dron.changeNavSpeed(5)
print ('Voy atras 20 metros')
dron.move_distance ('Back', 20)
print ('me muevo hacia adelante 5 metros')
dron.move_distance ('Forward', 5)
print ('cambio de heading a 90 grados')
dron.changeHeading(90)
print ('me muevo a la izquierda 10 metros')
dron.move_distance ('Left', 10)
dron.RTL()
dron.disconnect()

