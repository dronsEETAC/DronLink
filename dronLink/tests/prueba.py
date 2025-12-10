from pymavlink import mavutil
import time

# ===============================
# CONFIGURACIÓN DE CONEXIÓN
# ===============================
# Ajusta el puerto según tu dispositivo:
#  - En Android con radio USB:  '/dev/ttyUSB0'
#  - En Windows: 'COM3' (por ejemplo)
#  - En Linux:   '/dev/ttyACM0' o '/dev/ttyUSB0'
PORT = 'com3'
BAUD = 57600

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
    msg = master.recv_match(type='SYS_STATUS', blocking=True, timeout=5)

    if not msg:
        print("⚠️ No se recibió SYS_STATUS (timeout).")
        continue

    # Extraer los campos del mensaje
    voltage = msg.voltage_battery / 1000.0        # en Voltios
    current = msg.current_battery / 100.0         # en Amperios
    remaining = msg.battery_remaining             # en %
    load = msg.load / 10.0                        # carga del sistema (%)
    drop_rate_comm = msg.drop_rate_comm / 100.0   # tasa de pérdida de paquetes (%)
    errors_comm = msg.errors_comm                 # errores de comunicación
    sensors_present = msg.onboard_control_sensors_present
    sensors_enabled = msg.onboard_control_sensors_enabled
    sensors_health = msg.onboard_control_sensors_health

    # Mostrar los valores
    print("────────────────────────────────────────────")
    print(f"🔋 Nivel batería: {remaining}%")
    print(f"⚡ Voltaje: {voltage:.2f} V")
    print(f"🔌 Corriente: {current:.2f} A")
    print(f"💻 Carga del sistema: {load:.1f}%")
    print(f"📶 Pérdida comunicación: {drop_rate_comm:.2f}%")
    print(f"❗ Errores comunicación: {errors_comm}")
    print(f"🧭 Sensores presentes: {sensors_present}")
    print(f"✅ Sensores habilitados: {sensors_enabled}")
    print(f"❤️ Salud sensores: {sensors_health}")
    print("────────────────────────────────────────────\n")

    time.sleep(1)

