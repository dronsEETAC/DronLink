import time

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'udpout:localhost:12000'
connection_string = f'udpout:127.0.0.1:14552'
connection_string = f'udp:127.0.0.1:14551'
#connection_string = 'tcp:127.0.0.1:5763'
connection_string = f'udp:192.168.1.71:14550'
connection_string = "udpout:10.254.58.56:14550"
#connection_string = 'tcp:10.254.58.77:5763'
baud = 115200
'''connection_string = 'com13'
baud = 4800'''
print ("Voy a conectarme")
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
dron.land()
print ('ya estoy en tierra')
dron.disconnect()