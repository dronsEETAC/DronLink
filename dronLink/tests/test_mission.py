import json

from dronLink.Dron import Dron

def informar ():
    global dron
    print ('Ya he cargado la misión')
    mission = dron.getMission()
    if mission:
        print ('esta es la missión que he descargado: ')
        print (json.dumps(mission, indent = 1))
        print ('Ahora la voy a ejecutar')
        dron.executeMission()
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

dron.uploadMission(mission, blocking = False, callback = informar)


