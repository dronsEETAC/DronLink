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
print ('libero el heading')
dron.unfixHeading()
print ('Navego al norte 5 segundos')
dron.go('North')
time.sleep (5)
print ('cambio la velocidad a 3 m/s')
dron.changeNavSpeed(3)
print ('Navego al este 5 segundos')
dron.go('East')
time.sleep (5)
print ('cambio el heading a 270 grados')
dron.changeHeading(270)
print ('fijo el heading')
dron.fixHeading()
print ('Navego al sur 5 segundos')
dron.go('South')
time.sleep (5)
print ('Navego al noreste 5 segundos')
dron.go('NorthEast')
time.sleep (5)
print ('Retorno a casa')
dron.RTL()
dron.disconnect()

