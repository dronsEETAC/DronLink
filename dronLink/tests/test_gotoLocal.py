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
print ("Vamos a (10,10,5)")
dron.gotoLocal(10,10,5)
print ("Ya he llegado")
print ("Aumentamos la velocidad a 8m/s")
dron.setMoveSpeed(8)
print ("Vamos a (10,-10,15)")
dron.gotoLocal(10,-10,15)
print ("Ya he llegado")


print ("Vamos a (-10,-10,10)")
dron.gotoLocal(-10,-10,10)
print ("Ya he llegado")
print ("Reducimos la velocidad a 2m/s")
dron.setMoveSpeed(2)
print ("Vamos a (-10,10,5)")
dron.gotoLocal(-10,10,5)
print ("Ya he llegado")


dron.Land()
print ('ya estoy en tierra')
dron.disconnect()