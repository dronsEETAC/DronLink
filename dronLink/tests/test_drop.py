import json

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
connection_string = 'com4'
baud = 57600
print ('voy a conectarme')
dron.connect(connection_string, baud)
print ('conectado')

dron.drop()
print ('fin')

