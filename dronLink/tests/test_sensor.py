from pymavlink import mavutil

# Conéctate al puerto donde recibes MAVLink del Cube (ajusta COM o UDP)
# Ejemplo: telemetría USB en Windows
master = mavutil.mavlink_connection('COM3', baud=57600)

# Esperar al heartbeat (para sincronizar con el autopiloto)
master.wait_heartbeat()
print(f"Conectado al sistema {master.target_system}, componente {master.target_component}")
frequency = 1
# Pido también datos locales
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
    mavutil.mavlink.MAVLINK_MSG_ID_DISTANCE_SENSOR,  # The MAVLink message ID
    1e6 / frequency,
    0, 0, 0, 0,  # Unused parameters
    0
)
print("Esperando datos DISTANCE_SENSOR ...")

while True:
    # Recibir mensajes MAVLink (filtramos por tipo)
    msg = master.recv_match(type='DISTANCE_SENSOR', blocking=True)
    if not msg:
        continue

    # Extraer campos relevantes
    distancia = msg.current_distance   # distancia medida en cm
    min_dist  = msg.min_distance       # rango mínimo del sensor
    max_dist  = msg.max_distance       # rango máximo del sensor
    orient    = msg.orientation        # orientación reportada por el sensor
    cov       = msg.covariance         # calidad de la medida (si la reporta)

    print(f"[DIST_SENSOR] Distancia: {distancia} cm | Rango: {min_dist}-{max_dist} cm | Orient: {orient} | Cov: {cov}")
