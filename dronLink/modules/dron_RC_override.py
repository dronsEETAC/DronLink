def send_rc (self, roll, pitch, throttle, yaw ):

    self.vehicle.mav.rc_channels_override_send(
                self.vehicle.target_system,
                self.vehicle.target_component,
                roll, pitch, throttle, yaw,
                0, 0, 0, 0  # RC5–RC8 sin cambios
    )

