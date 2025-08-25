import time

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
'''connection_string = 'com13'
baud = 4800'''
dron.connect(connection_string, baud)
print ('conectado')
dron.arm()
print ('ya he armado')
dron.takeOff (12)
print ('ya he alcanzado al altitud indicada. Espero 5 segundos')
time.sleep (5)
print ('vamos hacia delante durante 5 segundos')
dron.go('Forward')
time.sleep (5)
print ('voy a rotar 90 en sentido horario')
dron.rotate(90)

print ('vamos hacia delante durante 5 segundos')
dron.go('Forward')
time.sleep (5)
print ('vamos a rotar 45 grados antihorario')
dron.rotate(45, 'ccw')

print ('vamos hacia delante durante 5 segundos')
dron.go('Forward')
time.sleep (5)
print ('vamos a aterrizar')
dron.Land()
print ('ya estoy en tierra')
dron.disconnect()