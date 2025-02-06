import json
import time

from dronLink.Dron import Dron

def aqui (index, wp):
    print ('He llegado a: ', wp)
    print ('Que esta en la posición: ', index )

def ejecutar ():
    global dron, mission
    print ('Ya he cargado la misión')
    m = dron.getMission()
    if m:
        print ('esta es la missión que he descargado: ')
        print (json.dumps(m, indent = 1))
        print ('Ahora la voy a ejecutar')
        dron.executeMission()
        print ('Mision finalizada')
        time.sleep (10)
        print ('Ahora la ejecuto en modo fligh plan')

        dron.executeFlightPlan(mission, inWaypoint=aqui)
        print('Terminó el plan de vuelo')

    else:
        print ('No hay mision')



dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
dron.connect(connection_string, baud)

mission = {
        "speed": 7,
        "takeOffAlt": 8,
        "waypoints": [
            {'lat': 41.2764035, 'lon': 1.9883262, 'alt': 5},
            {'rotAbs': 90},
            {'lat': 41.2762160, 'lon': 1.9883537, 'alt': 15},
            {'rotRel': 90, 'dir': -1},
            {'lat': 41.2762281, 'lon': 1.9884771, 'alt': 9}
        ]
}

dron.uploadMission(mission, blocking = False, callback = ejecutar)

