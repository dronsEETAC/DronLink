import time

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
dron.connect(connection_string, baud)
print ('conectado')
dron.arm()
time.sleep (50)
dron.takeOff (25)
print ('ya he llegado a los 25 metros')
dron.change_altitude (15)
print ('ya he bajado a los metros')
dron.go ('West')
time.sleep (5)
dron.RTL()
dron.disconnect()