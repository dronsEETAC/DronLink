import time

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
dron.connect(connection_string, baud)
minAltBreak = False
def avisar (id):
    global minAltBreak
    if minAltBreak:
        print ('Ya has recuperado la posición')
        minAltBreak = False
    else:
        print('Has alcanzado la altura mínima')
        minAltBreak = True


dron.CheckMinAlt(aviso = avisar)
time.sleep (200)