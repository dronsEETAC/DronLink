import time

from dronLink.Dron import Dron
dron = Dron()
connection_string = 'com3'
baud = 57600
'''connection_string = 'tcp:127.0.0.1:5763'
baud = 115200'''

dron.connect(connection_string, baud)

def procesarRcInfo (rcInfo ):
    print ('distance info:', rcInfo)

time.sleep (5)

print("Seguimos")

dron.send_rc_info(procesarRcInfo, freq=10)
time.sleep (100)
dron.stop_sending_rc_info()
dron.disconnect()
print ('Fin')