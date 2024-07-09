import json

from dronLink.Dron import Dron

def informar ():
    global dron
    print ('Comprueba ahora con Mission Planner que se ha cargado el escenario:\n'
           'un polígono de inclusion, y dos polígonos y un circulo de exclusión')
    scenario = dron.getScenario()
    print ('Este es el escenario que hay en este momento en el autopiloto')
    print (json.dumps(scenario, indent = 1))


dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
dron.connect(connection_string, baud)
#dron.getGEOFence()
scenario = [
     {
         'type': 'polygon',
         'waypoints': [
             {'lat': 41.2764398, 'lon': 1.9882585},
             {'lat': 41.2761999, 'lon': 1.9883537},
             {'lat': 41.2763854, 'lon': 1.9890994},
             {'lat': 41.2766273, 'lon': 1.9889948}
         ]
     },
     {
         'type': 'polygon',
         'waypoints': [
             {'lat': 41.2764801, 'lon': 1.9886541},
             {'lat': 41.2764519, 'lon': 1.9889626},
             {'lat': 41.2763995, 'lon': 1.9887963},
         ]
     },
     {
         'type': 'polygon',
         'waypoints': [
             {'lat': 41.2764035, 'lon': 1.9883262},
             {'lat': 41.2762160, 'lon': 1.9883537},
             {'lat': 41.2762281, 'lon': 1.9884771}
         ]
     },
     {
         'type': 'circle',
         'radius': 2,
         'lat': 41.2763430,
         'lon': 1.9883953
     }
]
dron.setScenario(scenario, blocking = False, callback = informar)
