import threading
import pygame
import time
import pywinusb.hid as hid
from pynput import keyboard
import sys
import time


class Joystick:
    def __init__(self, dron):
        self.dron = dron
        # Conjunto que guardatá las teclas pulsadas
        self.pressed_keys = set()
        # pongo en marcha el thread que estará pendiente de las teclas que se pulsen
        threading.Thread(target=self.control_loop).start()

    def clamp(self,value, vmin=1000, vmax=2000):
        # limita el valor recibido al rango 1000-2000 que es el rango de valores para
        # throttle, yaw, pitch y roll
        if value < vmin:
            return vmin
        elif value > vmax:
            return vmax
        else:
            return value


    def on_press(self, key):
        # guardo la tecla pulsada
        self.pressed_keys.add(key)

    def on_release(self, key):
        # suelto la tecla
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
            # si he soltado las teclas de pitch o roll, coloco los valores intermedios
            if key == keyboard.Key.up or key == keyboard.Key.down:
                self.pitch = 1500
            elif key == keyboard.Key.left or key == keyboard.Key.right:
                self.roll = 1500

            else:
                key = key.char.lower()
                # tambien pongo valores intermedios en caso de soltar las teclas de yaw o de throttle
                if key == 'q' or key == 'e':
                        self.yaw = 1500
                elif key == 'r' or key == 'f':
                        self.throttle = 1500
        # Salir con ESC
        if key == keyboard.Key.esc:
            print("\nSaliendo...")
            return False

    def control_loop (self):
        # con este parametro hacemos que el dron no exija que el throttle esté al mínimo para armar
        params = [{'ID': "PILOT_THR_BHV", 'Value': 1}]
        self.dron.setParams(params)
        # Ejes del joystick con los valores intermedios
        self.roll = 1500
        self.pitch = 1500
        self.yaw = 1500
        self.throttle = 1500
        STEP = 10 # incremento de valores cada vez que pulso una tecla
        # inicio el código que estará pendientes de coger las teclas que se pulsan o se sueltan
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()

        try:
            while listener.is_alive():
                # Aplicar cambios según teclas presionadas
                for key in  list(self.pressed_keys):
                    # proceso cada una de las teclas pendientes
                    if key == keyboard.Key.up:
                        self.pitch = self.clamp(self.pitch - STEP)
                    elif key == keyboard.Key.down:
                        self.pitch = self.clamp(self.pitch + STEP)
                    elif key == keyboard.Key.left:
                        self.roll = self.clamp(self.roll - STEP)
                    elif key == keyboard.Key.right:
                        self.roll = self.clamp(self.roll + STEP)
                    elif hasattr(key, 'char'):
                        k = key.char.lower()
                        if k == '1':
                            # tecla para armar
                            self.dron.arm()
                            # y me pongo en Loiter
                            self.dron.setFlightMode("LOITER")
                        if k == '3':
                            # tecla para aterrizar
                            self.dron.Land(blocking=False)
                        if k == '4':
                            # tecla para retornar
                            self.dron.RTL(blocking=False)
                        # teclas para yaw y throttle
                        if k == 'q':
                            self.yaw = self.clamp(self.yaw - STEP)
                        elif k == 'e':
                            self.yaw =self.clamp(self.yaw + STEP)
                        elif k == 'r':
                            self.throttle = self.clamp(self.throttle + STEP)
                        elif k == 'f':
                            self.throttle = self.clamp(self.throttle - STEP)

                if self.dron.flightMode == 'LOITER':
                    # envio los valores al dron
                    self.dron.send_rc(self.roll, self.pitch, self.throttle, self.yaw)
                time.sleep(0.1)

        except KeyboardInterrupt:
            pass

        listener.stop()
        print("\nCerrado correctamente.")
        # Restauro el parámetro que cambié
        params = [{'ID': "PILOT_THR_BHV", 'Value': 0} ]
        self.dron.setParams(params)

