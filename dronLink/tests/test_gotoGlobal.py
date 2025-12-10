import time

from dronLink.Dron import Dron

dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200

dron.connect(connection_string, baud)
print ('conectado')
dron.arm()
print ('ya he armado')
dron.takeOff (5)
print ('ya he alcanzado al altitud indicada. Espero 5 segundos')
time.sleep (5)
print ("Vamos a la esquina noreste altura 5")
dron.goto(41.27663951815306, 1.9890274571031075, 5)
print ("Ya he llegado")
time.sleep (5)
print ("Aumentamos la velocidad a 8m/s")
dron.setMoveSpeed(8)
print ("Vamos a la esquina noroeste altura 15")
dron.goto(41.276433909392125, 1.9882201122301202,15)
print ("Ya he llegado")

time.sleep (5)
print ("Vamos a la esquina suroeste, altura 10")
dron.goto(41.27615774758619, 1.9883287416897746,10)
print ("Ya he llegado")
time.sleep (5)
print ("Reducimos la velocidad a 2m/s")
dron.setMoveSpeed(2)

print ("Vamos a la esquina sureste, altura 5")
dron.goto(41.27636839666066, 1.9891508387116044,5)
print ("Ya he llegado")
time.sleep (5)

dron.Land()
print ('ya estoy en tierra')
dron.disconnect()