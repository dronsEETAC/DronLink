import time

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
dron.connect(connection_string, baud)
print ('conectado')
dron.setFlightMode('GUIDED')
time.sleep (3)
dron.setFlightMode('LOITER')
time.sleep (3)

dron.setFlightMode('BRAKE')
time.sleep (3)
dron.setFlightMode('RTL')
time.sleep (3)
dron.setFlightMode('LAND')
time.sleep (3)

dron.disconnect()