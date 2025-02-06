import time

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
connection_string = 'com13'
baud = 4800
dron.connect(connection_string, baud)
print ('conectado')
dron.arm()
print ('ya he armado')
dron.takeOff (2)
time.sleep (5)
dron.go('North')
print ('ya he alcanzado al altitud indicada')
#dron.change_altitude(10)
print ('ya he alcanzado la nueva altitud')
#dron.go ('West')
time.sleep (5)
dron.Land()
print ('ya estoy en tierra')
dron.disconnect()