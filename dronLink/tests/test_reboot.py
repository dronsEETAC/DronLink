import time

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
dron.connect(connection_string, baud)
print ('conectado')
time.sleep (5)

dron.reboot()
print ('ya he rebotado')
time.sleep (5)
dron.connect(connection_string, baud)
print ('conectado de nuevo')
time.sleep (5)

dron.disconnect()