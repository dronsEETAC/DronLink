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
dron.takeOff (15)
print ('ya he alcanzado al altitud indicada. Espero 5 segundos')
time.sleep (5)
print ('rotamos 90 grados en sentido horario')
dron.rotate (90)
print ('Fijamos heading')
dron.fixHeading()
print ('vamos hacia el este durante 10 segundos')
dron.go('East')
time.sleep (10)
print ('Liberamos heading')
dron.unfixHeading()
print ('vamos hacia el oeste durante 10 segundos')
dron.go('West')
time.sleep (10)
print ('Fijamos el heading a 180')
dron.changeHeading(180)
print ('Esperamos 10 segundos')
time.sleep (10)
print ('rotamos 90 grados en sentido horario')
dron.rotate (90)
print ('rotamos 45 grados en sentido anti horario')
dron.rotate (45, 'ccw')
print ('vamos a aterrizar')
dron.Land()
print ('ya estoy en tierra')
dron.disconnect()