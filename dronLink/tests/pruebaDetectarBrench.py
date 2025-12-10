from pymavlink import mavutil
import time

# ===============================
# CONFIGURACIÓN DE CONEXIÓN
# ===============================
# Ajusta el puerto según tu dispositivo:
#  - En Android con radio USB:  '/dev/ttyUSB0'
#  - En Windows: 'COM3' (por ejemplo)
#  - En Linux:   '/dev/ttyACM0' o '/dev/ttyUSB0'
PORT = "tcp:127.0.0.1:5763"
BAUD = 115200

print(f"Conectando a {PORT} a {BAUD} bps...")
master = mavutil.mavlink_connection(PORT, baud=BAUD)

print("Esperando al dron (HEARTBEAT)...")
master.wait_heartbeat()
print(f"✅ Conectado al sistema (System ID {master.target_system}, Component ID {master.target_component})\n")

# ===============================
# BUCLE PRINCIPAL
# ===============================
print("📡 Esperando mensajes SYS_STATUS...\n")

while True:
    msg = master.recv_match(type='FENCE_STATUS', blocking=True)
    print (msg)



    time.sleep(1)

