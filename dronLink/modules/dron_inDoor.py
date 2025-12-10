import threading
import time
import math

from pymavlink import mavutil



def EstablecerLimites (self,limites , callback = None):
    '''
    Los límites se especifican de la siguiente manera:
    limites = {
            'minAlt': 2,
            'maxAlt':10,
            'inclusion': [(3,5), (7,9), (-2,4)],
            'obstaculos': [
                [(2,9), (4,7), (8,8)],
                [(-1,3), (3,3), (10,10)]
            ]
    }
    Las coordenadas son del espacio NED
    '''
    # El callback es la función que hay que llamar en caso de acercarse peligrosamente a los límites

    if 'minAlt' in limites:
        # hay límite de altura mínima
        self.minAltLocal = limites['minAlt']
    else:
        self.minAltLocal = None
    if 'maxAlt' in limites:
        # hay límite de altura máxima
        self.maxAltLocal = limites['maxAlt']
    else:
        self.maxAltLocal = None

    if 'inclusion' in limites:
        # hay un poligono de inclusión. Convierto las coordenadas gráficas en coordenadas NED
        self.inclusion = limites['inclusion']

    else:
        self.inclusion = None

    if 'obstaculos' in limites:
        # hay obstáculos. Convierto también las coordenadas
        self.obstaculos = []
        for obstaculo in limites['obstaculos']:
            self.obstaculos.append(obstaculo)
    else:
        self.obstaculos = None

    self.callback  = callback
    print ('limites: ', self.inclusion)
    print ('obstaculos: ', self.obstaculos)


def _ActivaLimitesIndoor(self, callback = None):
    # Esta función se ejecuta en un thread y está pendiente de que el dron no se salte los límites
    SAFE_MODES = ['GUIDED', 'LOITER', 'ALT_HOLD', 'POSHOLD']
    # tomo nota de la velocidad de loites
    loiterSpeed = self.getParams(["LOIT_SPEED"])[0]['LOIT_SPEED']
    # preparo variables para tomar nota de si estoy en zona de peligro
    peligro = False
    if self.obstaculos:
        peligroObstaculo = [False]*len(self.obstaculos)
    while self.checkingInDoorLimits:
        # veamos si he superado el limite inferior
        if self.minAltLocal:
            if self.alt is not None and self.flightMode is not None:
                # la comprobación la hago si no estoy en land o RTL
                if self.alt < self.minAltLocal and self.flightMode in SAFE_MODES:
                    if callback:
                        callback(self.id,-2, 1)  # Aviso de que he superado la altura mínima
                    # guardo el modo que tengo en este momento
                    mode = self.flightMode
                    # pongo modo guiado
                    self.setFlightMode('GUIDED')
                    # subo 1 metro
                    self.move_distance('Up', 1)
                    # restauto el modo que tenía
                    self.setFlightMode(mode)
                    if callback:
                        callback(self.id, -2, 0)  # Aviso de que se ha recuperado la posición
        # veamos si he superado el limite superior
        if self.maxAltLocal:
            if self.alt is not None and self.flightMode is not None:
                if self.alt > self.maxAltLocal and self.flightMode in SAFE_MODES:
                    if callback:
                        callback(self.id, -1, 1)  # Aviso de que se ha detectado altura maxima
                    mode = self.flightMode
                    self.setFlightMode('GUIDED')
                    self.move_distance('Down', 1)
                    self.setFlightMode(mode)
                    if callback:
                        callback(self.id, -1, 0)  # Aviso de que ya se ha recuperado la posición


        if self.inclusion:
            # veamos en qué posición estamos (coordenadas NED)
            punto = (self.position[0], self.position[1])
            # y la distancia que me separa del fence de inclusión
            d = self._distancia_minima_punto_a_poligono(self.inclusion, punto)
            # considero que estoy en peligro si me he acercado a una distancia
            # que el dron puede recorrer en 1 segundo a la velocidad que lleva en ese momento
            # pero con un mínimo de 2 metros
            if d < max (self.groundSpeed, 2) and not peligro:
                print ('peligro')
                if callback:
                    callback(self.id, 0, 1)  # Aviso de que entro en zona de peligro

                peligro = True
                # tomo nota de la distancia a la que estoy justo al entrar en zona de peligro
                distanciaFuera = d
                # me guardo la velocidad Loiter para poder recuperarta despues
                loiterSpeed = self.getParams(["LOIT_SPEED"])[0]['LOIT_SPEED']
                # reduzco mucho la velocidad de loiter
                newParameters = [{'ID': "LOIT_SPEED", 'Value': 20}]
                self.setParams(newParameters)


            elif peligro:
                # estoy en zona de peligro
                if d > distanciaFuera:
                    # ha me he alejado lo suficiente
                    # recupero la velocidad de loiter que tenía al entrar en peligro
                    newParameters = [{'ID': "LOIT_SPEED", 'Value':loiterSpeed}]
                    self.setParams(newParameters)
                    peligro = False
                    callback(self.id, 0, 0)  # Aviso de que entro en zona segura'
                elif d < 0.2:
                    # estoy ya encima del límite
                    if callback:
                        callback(self.id, 0, 2)  # Aviso de que me he salido del fence
                    # ordeno RTL
                    self.setFlightMode("RTL")
                    # restauro la velocidad que tenía cuando entré en zona de peligro, por si quiero
                    # volver a despegar y seguir volando
                    newParameters = [{'ID': "LOIT_SPEED", 'Value': loiterSpeed}]
                    self.setParams(newParameters)


        # ahora miro los obstáculos. El proceso es exactamente el mismo
        if self.obstaculos:
            for i in range(len(self.obstaculos)):
                poligono = self.obstaculos[i]
                # veamos en qué posición estamos (coordenadas NED)
                punto = (self.position[0], self.position[1])
                # y la distancia que me separa del obstáculo
                d = self._distancia_minima_punto_a_poligono(poligono, punto)

                if d < max(self.groundSpeed, 2) and not peligroObstaculo[i]:
                    if callback:
                        callback(self.id, i + 1, 1)  # Aviso de que entro en peligro

                    peligroObstaculo [i] = True
                    distanciaFuera = d
                    loiterSpeed = self.getParams(["LOIT_SPEED"])[0]['LOIT_SPEED']
                    newParameters = [{'ID': "LOIT_SPEED", 'Value': 20}]
                    self.setParams(newParameters)

                elif peligroObstaculo[i]:
                    if d > distanciaFuera:
                        if callback:
                            callback(self.id, i + 1, 2)  # Aviso de que me he alejado lo suficiente del obstáculo
                        newParameters = [{'ID': "LOIT_SPEED", 'Value': loiterSpeed}]
                        self.setParams(newParameters)
                        peligroObstaculo[i] = False
                        callback(self.id, i+1, 0)  # Aviso de que entro en zona segura
                    elif d < 0.2:
                        # estoy encima del obstáculo. Ordeno RTL
                        self.setFlightMode("RTL")
                        # restauro la velocidad que tenía cuando entré en zona de peligro
                        newParameters = [{'ID': "LOIT_SPEED", 'Value': loiterSpeed}]
                        self.setParams(newParameters)

        time.sleep(0.1)


def ActivaLimitesIndoor (self):
    # inicio en un thread el bucle de control
    self.checkingInDoorLimits = True
    threading.Thread(target=self._ActivaLimitesIndoor, args=[self.callback]).start()

def DesactivaLimitesIndoor (self):
    self.checkingInDoorLimits = False

# Las dos funciones siguientes se necesitan para calcular la distancia de un punto a un polígono

def _distancia_punto_a_segmento(self, p, v1, v2):
    # Función auxiliar que calcula la distancia entre un punto p y el segmento [v1, v2]
    # p es el punto (px, py)
    # v1 y v2 son los puntos extremos del segmento (x1, y1) y (x2, y2)

    x0, y0 = p
    x1, y1 = v1
    x2, y2 = v2

    # Calcular las diferencias
    dx = x2 - x1
    dy = y2 - y1
    mag2 = dx**2 + dy**2  # magnitud al cuadrado del segmento

    if mag2 == 0:  # si el segmento es un punto
        return math.sqrt((x0 - x1 )**2 + (y0 - y1 )**2)

    # Proyección del punto p sobre el segmento
    t = ((x0 - x1) * dx + (y0 - y1) * dy) / mag2
    t = max(0, min(1, t))  # Asegurarse de que la proyección esté en el segmento [0, 1]

    # Coordenadas del punto proyectado sobre el segmento
    px = x1 + t * dx
    py = y1 + t * dy

    # Distancia entre el punto p y el punto proyectado (px, py)
    return math.sqrt((x0 - px )**2 + (y0 - py )**2)


def _distancia_minima_punto_a_poligono(self, poligono, punto):
    # Función que calcula la distancia mínima entre un punto y los lados de un polígono
    # poligono es una lista de tuplas [(x1, y1), (x2, y2), ...]
    # punto es un punto (px, py)

    # Inicializar la distancia mínima con un valor grande
    distancia_min = float('inf')

    # Recorrer cada par de puntos consecutivos en el polígono
    for i in range(len(poligono)):
        v1 = poligono[i]
        v2 = poligono[(i + 1) % len(poligono)]  # El siguiente vértice, considerando el cierre del polígono

        # Calcular la distancia del punto al segmento
        dist = self._distancia_punto_a_segmento(punto, v1, v2)

        # Actualizar la distancia mínima
        distancia_min = min(distancia_min, dist)

    return distancia_min


def ConfiguraVueloIndoor (self, posz=2):
    # posz indica si se usa altimetro laser (2) o si se usa barometro (1)
    newParameters = [
        {'ID': "AHRS_EKF_TYPE", 'Value': 3},
        {'ID': "EK3_ENABLE", 'Value': 1},
        {'ID': "EK3_SRC1_POSXY", 'Value': 0},
        {'ID': "EK3_SRC1_VELXY", 'Value': 5},
        {'ID': "EK3_SRC1_POSZ", 'Value': posz},
        {'ID': "EK3_SRC1_YAW", 'Value': 1},
        {'ID': "EK3_SRC_OPTIONS", 'Value': 0},
        {'ID': "ARMING_CHECK", 'Value': 1048054} # para que no espere señal gps para armar
    ]
    self.setParams(newParameters)

def ConfiguraVueloExterior (self, posz=2):
    # posz indica si se usa altimetro laser (2) o si se usa barometro (1)
    newParameters = [
        {'ID': "AHRS_EKF_TYPE", 'Value': 3},
        {'ID': "EK3_ENABLE", 'Value': 1},
        {'ID': "EK3_SRC1_POSXY", 'Value': 3},
        {'ID': "EK3_SRC1_VELXY", 'Value': 3},
        {'ID': "EK3_SRC1_POSZ", 'Value': posz},
        {'ID': "EK3_SRC1_YAW", 'Value': 1},
        {'ID': "EK3_SRC_OPTIONS", 'Value': 0},
        {'ID': "ARMING_CHECK", 'Value': 1},
    ]
    self.setParams(newParameters)

def SetHome (self):
    # Establecer home en la posición actual
    self.vehicle.mav.command_long_send(
        self.vehicle.target_system,  # target_system
        self.vehicle.target_component,  # target_component
        mavutil.mavlink.MAV_CMD_DO_SET_HOME,  # comando
        0,  # confirmation
        1,  # use_current = 1 → usar posición actual
        0, 0, 0, 0, 0, 0  # los demás parámetros no se usan en este modo
    )