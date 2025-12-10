import time

from dronLink.Dron import Dron
def avisoBreak(id, cod, nivel):
    # cuando el dron se salte los límites o se acerque peligrosamente la librería llamará a esta función
    # Nos pasan:
    #   el id del dron (que en esta aplicación no se usa),
    #   el codigo del tipo de límite que se ha saltado:
    #       -2: Altura mínima
    #       -1: Altura máxima
    #        0: fence de inclusion
    #        n: Obstaculo n_esimo
    #   el nivel de peligrosidad:
    #        0: Ya está de nuevo en zona segura
    #        1: Esta cerca (peligro)
    #        2: Está a punto de saltar el límite (no se usa en el caso de los límites de altura)


    if cod == 0:
        # poligono de inclusión
        if nivel == 2:
            print ("Rompo el fence. Me envían a casa")
        elif nivel == 1:
            print("Peligro")
        elif nivel == 0:
            print ("Vuelvo a zona segura")
    if cod == -1:
        if nivel == 1:
            print("Limite de altura")
        elif nivel == 0:
            print("Vuelvo por debajo del limite")



dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
dron.connect(connection_string, baud)
print ('conectado')
limites = {}
limites['maxAlt'] = 6
limites['inclusion'] = [(-20,20), (20,20), (20, -20), (-20,-20)]

# envio al dron la estructura de datos y le indico que función debe ejecutar en caso de que se salte
# los límites
dron.EstablecerLimites(limites, avisoBreak)
dron.ActivaLimitesIndoor()
newParameters = [{'ID': "LOIT_SPEED", 'Value': 300}]
dron.setParams(newParameters)

dron.arm()
print ('ya he armado')
dron.setFlightMode('LOITER')
print ("Subo pero no podrá superar los 6 metros. Lo intentará dos veces")
for i in range (300):
    dron.send_rc(1500,1500,2000,1500)
    time.sleep(0.1)

print ("Voy adelante. Entrará en peligro, reducirá, saldrá pero insistiremos y nos enviará a casa ")
for i in range (400):
    dron.send_rc(1500, 2000, 1500, 1500)
    time.sleep(0.1)
