from pymavlink import mavutil
from dronLink.Dron import Dron

#master = mavutil.mavlink_connection('tcp:127.0.0.1:5763', baud=115200)
#master = mavutil.mavlink_connection('udpin:127.0.0.1:14550')
master = mavutil.mavlink_connection('com3', baud=57600)
master.wait_heartbeat()

master.mav.request_data_stream_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_RC_CHANNELS,
    10,  # Hz
    1    # activar
)
print ("Conectado dron real")
'''dron = Dron ()
connection_string = 'tcp:127.0.0.1:5763'
baud = 115200
dron.connect(connection_string, baud)
print ('conectado dron simulado')
dron.setFlightMode('LOITER')'''
while True:
    msg = master.recv_match(type='RC_CHANNELS', blocking=True)

    if msg:
        print ("Throttle: ",msg.chan3_raw)
        print ("Yaw: ",msg.chan4_raw)
        print ("Pitch: ",msg.chan2_raw)
        print ("Roll: ",msg.chan1_raw)

        #dron.send_rc(msg.chan1_raw, msg.chan2_raw, msg.chan3_raw, msg.chan4_raw)
        '''current_value = msg.chan8_raw

        if last_value is None:
            last_value = current_value
            continue

        if current_value != last_value:
            print(f"Cambio detectado en canal 8: {last_value} -> {current_value}")
            last_value = current_value'''

