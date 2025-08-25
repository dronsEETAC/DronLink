import json
import time
from dronLink.Dron import Dron

dron = Dron()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200

print ('voy a conectarme')
dron.connect (connection_string, baud)
print ('conectado')
print ('despego a 15 metros')
dron.arm()
dron.takeOff (15)
print ('cambio la velocidad a 1 m/s')
dron.changeNavSpeed(1)
print ('Navego al norte 10 segundos')
dron.go('North')
time.sleep (10)
print ('cambio la velocidad a 3 m/s')
dron.changeNavSpeed(3)
print ('Navego al este 10 segundos')
dron.go('East')
time.sleep (10)
print ('Navego al sur 5 segundos')
dron.go('South')
time.sleep (5)
print ('Navego a la izquierda 10 segundos. No va a cambiar el heading')
dron.go('Left')
time.sleep (10)
print ('Navego hacia atras 5 segundos')
dron.go('Back')
time.sleep (5)
print ('Navego al norte 10 segundos. Ahora cambia el heading')
dron.go('North')
time.sleep (10)
print ('Retorno a casa')
dron.RTL()
dron.disconnect()

