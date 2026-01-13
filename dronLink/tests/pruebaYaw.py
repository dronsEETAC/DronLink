import time
import math
from pymavlink import mavutil

# ==========================
# CONFIGURACIÓN
# ==========================
CONNECTION_STRING = "tcp:127.0.0.1:5762"   # cambia si es necesario
TAKEOFF_ALT = 5.0                           # metros
YAW_RATE_DEG = 10                           # grados/seg (baja velocidad)
ROTATION_TIME = 5.0                         # segundos

# ==========================
# CONEXIÓN
# ==========================
print("Conectando al dron...")
master = mavutil.mavlink_connection(CONNECTION_STRING)

master.wait_heartbeat()
print(
    f"Heartbeat recibido "
    f"(sys={master.target_system}, comp={master.target_component})"
)

# ==========================
# CAMBIO A GUIDED
# ==========================
print("Cambiando a modo GUIDED...")
master.set_mode_apm("GUIDED")

# Esperar confirmación
while True:
    msg = master.recv_match(type="HEARTBEAT", blocking=True)
    if mavutil.mode_string_v10(msg) == "GUIDED":
        print("Modo GUIDED confirmado")
        break

# ==========================
# ARMAR
# ==========================
print("Armando motores...")
master.arducopter_arm()

master.motors_armed_wait()
print("Motores armados")

# ==========================
# DESPEGUE
# ==========================
print(f"Despegando a {TAKEOFF_ALT} metros...")
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0,
    0, 0, 0, 0,
    0, 0,
    TAKEOFF_ALT
)

'''# Esperar alcanzar altura
while True:
    msg = master.recv_match(type="GLOBAL_POSITION_INT", blocking=True)
    alt = msg.relative_alt / 1000.0  # mm → m
    print (alt)
    if alt >= TAKEOFF_ALT * 0.95:
        print(f"Altura alcanzada: {alt:.2f} m")
        break
'''
time.sleep(10)

# ==========================
# ROTACIÓN EN YAW
# ==========================
print("Rotando en sentido horario...")

yaw_rate = -math.radians(YAW_RATE_DEG)  # horario = negativo

type_mask = (
    mavutil.mavlink.POSITION_TARGET_TYPEMASK_X_IGNORE |
    mavutil.mavlink.POSITION_TARGET_TYPEMASK_Y_IGNORE |
    mavutil.mavlink.POSITION_TARGET_TYPEMASK_Z_IGNORE |
    mavutil.mavlink.POSITION_TARGET_TYPEMASK_VX_IGNORE |
    mavutil.mavlink.POSITION_TARGET_TYPEMASK_VY_IGNORE |
    mavutil.mavlink.POSITION_TARGET_TYPEMASK_VZ_IGNORE |
    mavutil.mavlink.POSITION_TARGET_TYPEMASK_AX_IGNORE |
    mavutil.mavlink.POSITION_TARGET_TYPEMASK_AY_IGNORE |
    mavutil.mavlink.POSITION_TARGET_TYPEMASK_AZ_IGNORE |
    mavutil.mavlink.POSITION_TARGET_TYPEMASK_YAW_IGNORE
)

start = time.time()

while time.time() - start < ROTATION_TIME:
    msg = mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
        time_boot_ms=0,
        target_system=master.target_system,
        target_component=master.target_component,
        coordinate_frame=mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        type_mask=type_mask,
        x=0, y=0, z=0,
        vx=0, vy=0, vz=0,
        afx=0, afy=0, afz=0,
        yaw=0,
        yaw_rate=yaw_rate
    )
    print ("Envio")
    master.mav.send(msg)
    time.sleep(0.1)  # 10 Hz

print("Parando rotación...")

# Detener yaw
msg_stop = mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
    time_boot_ms=0,
    target_system=master.target_system,
    target_component=master.target_component,
    coordinate_frame=mavutil.mavlink.MAV_FRAME_LOCAL_NED,
    type_mask=(
        type_mask |
        mavutil.mavlink.POSITION_TARGET_TYPEMASK_YAW_RATE_IGNORE
    ),
    x=0, y=0, z=0,
    vx=0, vy=0, vz=0,
    afx=0, afy=0, afz=0,
    yaw=0,
    yaw_rate=0
)

master.mav.send(msg_stop)
time.sleep(2)

# ==========================
# ATERRIZAJE
# ==========================
print("Aterrizando...")
master.set_mode_apm("LAND")

# Esperar desarmado
master.motors_disarmed_wait()
print("Aterrizaje completo y motores desarmados")

print("Programa finalizado correctamente")
