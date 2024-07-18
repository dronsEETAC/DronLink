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
        "takeOffAlt": 8,
        "waypoints": [
            {"lat": 41.38123932563867, "lon": 2.1222140385535795, 'alt': 5},
            {"lat": 41.38145667909462, "lon": 2.1229596926597196, 'alt': 15},
            {"lat": 41.380585248356525, "lon": 2.1234317614463407, 'alt': 9},
            {"lat": 41.38036587942569, "lon": 2.122678060713156, 'alt': 6}
        ]
}

dron.uploadMission(mission, blocking = False, callback = informar)


