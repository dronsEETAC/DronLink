from pymavlink import mavutil
import time

RPI_IP = "127.0.0.1"   # IP de la Raspberry Pi

# conexión MAVLink UDP
#master = mavutil.mavlink_connection(f'udpout:127.0.0.1:14552')
#masterin = mavutil.mavlink_connection(f'udpin:127.0.0.1:14553')
master = mavutil.mavlink_connection(f'tcp:127.0.0.1:14552')
master.mav.heartbeat_send(
    mavutil.mavlink.MAV_TYPE_GCS,
    mavutil.mavlink.MAV_AUTOPILOT_INVALID,
    0,
    0,
    0
)

print("Esperando heartbeat...")


master.wait_heartbeat()

print("Heartbeat recibido")

# ------------------------
# ARM del dron
# ------------------------

master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    1, 0, 0, 0, 0, 0, 0
)

print("Arm enviado")

time.sleep(2)

# ------------------------
# TAKEOFF
# ------------------------

altitude = 5

master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0,
    0, 0, 0, 0, 0, 0,
    altitude
)

print("Takeoff enviado a", altitude, "metros")


print("Esperando comandos MAVLink...")
while True:

    msg = master.recv_msg()
    if msg:
        print ("recibo ", msg)





