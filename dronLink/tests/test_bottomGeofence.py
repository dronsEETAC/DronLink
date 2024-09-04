from dronLink.Dron import Dron
dron = Dron()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
dron.connect(connection_string, baud)
print ('conectado')
def procesar (state ):
    # state puede ser 'breach' o 'in'
    print (state)
dron.startBottomGeofence(5, procesar)
while True:
    pass
# ahora se puede mover el dron desde mission planner para verificar que al bajar de
# 5 metros se produce el breach y el dron asciende hasta volver a 'in'