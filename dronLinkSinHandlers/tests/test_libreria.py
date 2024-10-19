import time

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
dron.connect(connection_string, baud)
dron.arm()
dron.takeOff (5)
dron.go ('West')
time.sleep (5)
dron.RTL()
dron.disconnect()