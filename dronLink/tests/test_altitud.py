import time

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
dron.connect(connection_string, baud)
print ('conectado')
dron.arm()
dron.takeOff (25)
print ('ya he alcanzado los 25 metros')
dron.change_altitude(10)
print ('ya he bajado a los 10 metros')
dron.change_altitude(20)
print ('ya he subido a los 20 metros')

dron.Land()
print ('ya estoy en tierra')
dron.disconnect()