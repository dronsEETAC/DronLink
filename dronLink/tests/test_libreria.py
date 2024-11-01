import time

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
dron.connect(connection_string, baud)
print ('conectado')
dron.arm()
print ('ya he armado')
dron.takeOff (25)
print ('ya he alcanzado al altitud indicada')
dron.change_altitude(10)
print ('ya he alcanzado la nueva altitud')
dron.go ('West')
time.sleep (5)
dron.RTL()
print ('ya estoy en tierra')
dron.disconnect()