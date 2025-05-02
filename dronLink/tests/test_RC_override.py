import time

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
dron.connect(connection_string, baud)
print ('conectado')
dron.arm()
print ('ya he armado')
dron.takeOff (2)
print ('En el aire')
time.sleep (5)
print ('Pongo en modo Loiter')
dron.setFlightMode('LOITER')
print ("Reposo")
for i in range (100):
    dron.send_rc(1500,1500,1500,1500)
    time.sleep(0.1)
print ("Subo")
for i in range (100):
    dron.send_rc(1500,1500,2000,1500)
    time.sleep(0.1)
print("Voy a girar")
for i in range (100):
    dron.send_rc(1500, 1500, 1500, 1600)
    time.sleep(0.1)
print ("Voy al lado")
for i in range (100):
    dron.send_rc(2000, 1500, 1500, 1500)
    time.sleep(0.1)
print ("Voy adelante (depende de como esté configurado el pitch")
for i in range (100):
    dron.send_rc(1500, 2000, 1500, 1500)
    time.sleep(0.1)
dron.Land()
print ("En tierra")