import time

from dronLink.Dron import Dron

dron = Dron (verbose= True)
connection_string = 'tcp:127.0.0.1:5762'
baud = 115200
'''connection_string = 'com13'
baud = 4800'''
dron.connect(connection_string, baud)
print ('conectado')
dron.arm()
print ('ya he armado')
dron.takeOff (10)
print ('ya he alcanzado al altitud indicada. Espero 5 segundos')
#time.sleep (5)
#dron.fixHeading()
print ('vamos hacia delante durante 5 segundos')
dron.go('Forward')
time.sleep (10)
dron.go('Left')
time.sleep (15)
dron.changeNavSpeed(0.5)
dron.go('Forward')
time.sleep (15)
'''print ('voy a rotar 90')
dron.rotate(90)
print ('ya he girado. Ahora espero 15 segundos')
time.sleep (15)
print ('vamos hacia delante durante 5 segundos')
dron.go('Forward')
time.sleep (5)
print ('vamos a rotar 180')
dron.rotate(180)
print ('vamos a aterrizar')'''
dron.Land()
print ('ya estoy en tierra')
dron.disconnect()