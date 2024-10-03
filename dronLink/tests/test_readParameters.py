import time

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
connection_string = 'com21'
baud = 57600

dron.connect(connection_string, baud)
print ("conectado")
parameters = [
    "RTL_ALT",
    "PILOT_SPEED_UP",
    "FENCE_ACTION",
    "FENCE_ENABLE",
    "FENCE_MARGIN",
    "FENCE_ALT_MAX",
    "FLTMODE6"
]
result = dron.getParams(parameters)
print (result)
dron.disconnect()