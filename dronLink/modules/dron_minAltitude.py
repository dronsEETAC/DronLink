import threading

from pymavlink import mavutil
import time

import math


import math


def _CheckMinAlt (self, minAlt = 2, aviso = None):
    # Modos donde tiene sentido forzar altitud mínima
    SAFE_MODES = ['GUIDED', 'LOITER', 'ALT_HOLD', 'POSHOLD']
    self.checkingMinAltitude = True
    while self.checkingMinAltitude :
        if self.alt is not None and self.flightMode is not None:
            if self.alt < minAlt and self.flightMode in SAFE_MODES:
                if aviso:
                    aviso (self.id) # Aviso de que se ha detectado altura minima
                # guardo el modo que tengo en este momento
                mode = self.flightMode
                print ('voy a poner en modo guiado')
                self.setFlightMode('GUIDED')
                self.move_distance('Up', 2)
                # restauto el modo que tenía
                self.setFlightMode(mode)
                if aviso:
                    aviso(self.id)  # Segunda llamada que indica que ya se ha recuperado la posición

        time.sleep(0.2)

def CheckMinAlt (self, minAlt = 2, aviso = None):
    threading.Thread(target=self._CheckMinAlt, args=[ minAlt, aviso ]).start()


def StopCheckingMinAlt (self):
    self.checkingMinAltitude= False