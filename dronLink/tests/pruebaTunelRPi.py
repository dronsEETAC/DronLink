from pymavlink import mavutil

# conexión al autopiloto por serial
autopilot = mavutil.mavlink_connection('tcp:127.0.0.1:5763', baud=115200)
# servidor UDP que recibe comandos desde el portátil
#udp = mavutil.mavlink_connection('udpin:0.0.0.0:14552')
#udp = mavutil.mavlink_connection('udpin:127.0.0.1:14552')
#udp = mavutil.mavlink_connection('udp:0.0.0.0:14552')
udp = mavutil.mavlink_connection('tcp:127.0.0.1:5800')
#udpout = mavutil.mavlink_connection('udpout:127.0.0.1:14553')


print("Esperando comandos MAVLink...")
while True:

    msg = udp.recv_msg()
    if msg:
        print ("recibo de la estación de tierra: ", msg)
        autopilot.mav.send(msg)

    msg2 = autopilot.recv_msg()
    if msg2:
        #print ("recibo de SITL: ", msg2)
        udp.mav.send(msg2)


