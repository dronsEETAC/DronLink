import time
from dronLink.Dron import Dron

dron = Dron ()
'''connection_string = 'tcp:127.0.0.1:5763'
baud = 115200'''
connection_string = 'com3'
baud = 57600
dron.connect(connection_string, baud)
''' Configuro el dron para vuelo in Door (con optical flow)'''
dron.ConfiguraVueloIndoor()
print ('Preparado para vuelo in door')
# ahora el usuario vola
# rá el dron con la emisora hasta aterrizarlo en un sitio diferente al
# del despegue
# cuando lo haya hecho pulsará una tecla para que se ejecute la acción SetHome
# y entonces volvera a despegar. El dron deberá mantenerse estable en ese segundo despegue


input("Press Enter to continue...")
print("Seguimos")
dron.SetHome()
print ("Home estanlecido")
time.sleep (10)
dron.disconnect()
print ("Fin")