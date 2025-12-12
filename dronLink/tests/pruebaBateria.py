'''from pymavlink import mavutil

master = mavutil.mavlink_connection( 'tcp:127.0.0.1:5763', baud=115200)
master.wait_heartbeat()

while True:
    msg = master.recv_match(type='BATTERY_STATUS', blocking=True)
    if msg:
        voltage = msg.voltages[0] / 1000.0   # en voltios (mV → V)
        current = msg.current_battery / 100.0  # en amperios (cA → A)
        level = msg.battery_remaining         # en %

        print(f"Voltaje: {voltage:.2f} V, Corriente: {current:.2f} A, Batería: {level}%")'''


from pymavlink import mavutil

master = mavutil.mavlink_connection('tcp:127.0.0.1:5763', baud=115200)
master.wait_heartbeat()
master.mav.request_data_stream_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL,
    10,
    1
)

while True:
    msg = master.recv_match(type='SYS_STATUS', blocking=True)
    if msg:
        voltage = msg.voltage_battery / 1000.0  # voltaicos en V
        current = msg.current_battery / 100.0   # amperios
        level = msg.battery_remaining           # %

        print(f"Voltaje: {voltage:.2f} V, Corriente: {current:.2f} A, Batería: {level}%")
