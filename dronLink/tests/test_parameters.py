import time

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200

connection_string = 'com13'
baud = 4800

'''connection_string = 'com10'
baud = 57600'''

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
print ('ya los tengo')
print (result)
print ('Cambio algunos')
newParameters =[ {'ID': "FENCE_ENABLE", 'Value': 1}, {'ID': "FENCE_ACTION", 'Value': 3} ]
dron.setParams(newParameters)
print ('Los vuelvo a leer')
result = dron.getParams(parameters)
print ('ya los tengo')
print (result)
dron.disconnect()