import time

from dronLink.Dron import Dron
dron = Dron()
connection_string = 'com3'
baud = 57600
'''connection_string = 'tcp:127.0.0.1:5763'
baud = 115200'''

dron.connect(connection_string, baud)
dron.ConfigureDistanceSensor('TFmini')
#dron.ConfigureDistanceSensor('RPLIDAR C1')
print ('conectado')
def procesarDistanceInfo (distanceInfo ):
    print ('distance info:', distanceInfo)

time.sleep (5)
input("Espera a que haya reiniciado el autopiloto y pulsa cualquier tecla...")
print("Seguimos")
dron.send_distance_sensor_info(procesarDistanceInfo, freq=10)
time.sleep (100)
dron.stop_sending_distance_sensor_info()
dron.disconnect()
print ('Fin')