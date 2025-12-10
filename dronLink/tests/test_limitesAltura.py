import time
from dronLink.Dron import Dron


def avisoBreak(id, cod):
    if cod == -2:
        print("Se ha superado la altura mínima")

    elif cod == -1:
        print("Se ha superado la altura máxima")


dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
connection_string = 'com3'
baud = 57600
dron.connect(connection_string, baud)
''' Configuro el dron para vuelo indoor'''
dron.ConfiguraVueloIndoor()
print ('Preparado para vuelo in door')
# Configuro los limites de altura
limites = {
    'minAlt': 2,
    'maxAlt': 5,
}
dron.EstablecerLimites(limites)
# ahora el usuario despegará el dron y cuando este a más de 2 metros de altura pulsará una tecla
# para que se establezcan los limites
input("Press Enter to continue...")
print("Seguimos")

dron.ActivaLimitesIndoor(callback=avisoBreak)

time.sleep (100)
dron.disconnect()
print ("Fin")
