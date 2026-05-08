from pymavlink import mavutil
import time

# --- Configuración ---
AUTOPILOT_ADDR = "127.0.0.1"
AUTOPILOT_PORT = 14540     # puerto SITL
ROUTER_LISTEN_PORT = 14552 # puerto que escucha la estación de tierra

# --- Conexiones ---
# 1. Conexión al autopiloto (SITL o real)
autopilot = mavutil.mavlink_connection('tcp:127.0.0.1:5763', baud=115200)

# 2. Socket que escucha estaciones de tierra
station = mavutil.mavlink_connection(f"udpin:0.0.0.0:{ROUTER_LISTEN_PORT}")

print("Router MAVLink iniciado...")
print(f"Escuchando estaciones en udp:{ROUTER_LISTEN_PORT}")
print(f"Conectado al autopiloto en udp:{AUTOPILOT_ADDR}:{AUTOPILOT_PORT}")

# --- Bucle principal ---
while True:
    # Mensajes desde la estación
    msg = station.recv_msg()
    if msg:
        # reenviar al autopiloto
        autopilot.mav.send(msg)
        print("Estación -> Autopiloto:", msg.get_type())

    # Mensajes desde el autopiloto
    msg2 = autopilot.recv_msg()
    if msg2:
        # reenviar a la estación
        station.mav.send(msg2)
        #print("Autopiloto -> Estación:", msg2.get_type())

    time.sleep(0.001)  # evita bloquear el hilo