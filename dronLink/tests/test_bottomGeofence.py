from dronLink.Dron import Dron
dron = Dron()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
connection_string = 'udp:127.0.0.1:14551'
baud = 57600
print ('voy a conectar')
dron.connect(connection_string, baud)
print ('conectado')
def procesar (state ):
    # state puede ser 'breach' o 'in'
    print (state)
dron.startBottomGeofence(3, procesar)
while True:
    pass
# ahora se puede mover el dron desde mission planner para verificar que al bajar de
# 5 metros se produce el breach y el dron asciende hasta volver a 'in'