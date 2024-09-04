import time

from dronLink.Dron import Dron
dron = Dron()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
dron.connect(connection_string, baud)
print ('conectado')
def procesarTelemetria (telemetryInfo ):
    print ('global:', telemetryInfo)
def procesarTelemetriaLocal (telemetryInfo ):
    print ('local:' , telemetryInfo)
dron.send_telemetry_info(procesarTelemetria)
time.sleep (10)
dron.send_local_telemetry_info(procesarTelemetriaLocal)
while True:
    pass