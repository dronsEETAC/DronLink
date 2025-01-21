from pymavlink import mavutil

def send_mission_item(master, seq, frame, command, param1, param2, param3, param4, x, y, z, autocontinue=1, current=0):
    """Función para enviar un mensaje MAVLink_mission_item_int_message."""
    message = mavutil.mavlink.MAVLink_mission_item_int_message(
        target_system=master.target_system,
        target_component=master.target_component,
        seq=seq,
        frame=frame,
        command=command,
        current=current,
        autocontinue=autocontinue,
        param1=param1,
        param2=param2,
        param3=param3,
        param4=param4,
        x=int(x * 1e7),  # Convertir latitud a formato entero
        y=int(y * 1e7),  # Convertir longitud a formato entero
        z=z
    )
    master.mav.send(message)

# Conectar al dron
master = mavutil.mavlink_connection('tcp:127.0.0.1:5763', baud=115200)

# Esperar al latido inicial
print("Esperando latidos...")
master.wait_heartbeat()
print(f"Latido recibido del sistema {master.target_system}, componente {master.target_component}")

# Iniciar la secuencia de escritura de misión
print("Iniciando la carga de la misión...")
master.mav.mission_count_send(master.target_system, master.target_component, 5)

# Enviar comandos de misión (DO_CHANGE_SPEED, waypoints y RTL)
seq = 0

# Establecer velocidad de navegación (1 m/s)
send_mission_item(
    master, seq, mavutil.mavlink.MAV_FRAME_MISSION,
    mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,
    param1=1, param2=1.0, param3=-1, param4=0,
    x=0, y=0, z=0, current=1
)
seq += 1

# Waypoint 1
send_mission_item(
    master, seq, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
    mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
    param1=0, param2=0, param3=0, param4=0,
    x=41.2764035, y=1.9883262, z=10
)
seq += 1

# Waypoint 2
send_mission_item(
    master, seq, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
    mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
    param1=0, param2=0, param3=0, param4=0,
    x=41.2762160, y=1.9883537, z=10
)
seq += 1

# Waypoint 3
send_mission_item(
    master, seq, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
    mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
    param1=0, param2=0, param3=0, param4=0,
    x=41.2762281, y=1.9884771, z=10
)
seq += 1

# RTL (Return to Launch)
send_mission_item(
    master, seq, mavutil.mavlink.MAV_FRAME_MISSION,
    mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
    param1=0, param2=0, param3=0, param4=0,
    x=0, y=0, z=0
)

print("Misión cargada. Asegúrate de iniciar la misión desde el controlador.")

# Finalizar la secuencia de carga
master.mav.mission_ack_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_MISSION_ACCEPTED
)
