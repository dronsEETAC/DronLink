import threading
import time
import math



class TransformadorNEDCanvasEscalado:
    '''
    Esta clase permite hacer los cambios de coordenadas necesarios para pasar del espacio NED al espacio gráfico
    y viceversa.
    Las coordenadas x,y,z que da la telemetría local identifican la posición del dron en el espacio NED. Por tanto,
    la x indica la posición en el eje Norte (valores positivos) - Sur (valores negativos), la y indica la posición
    en el eje Este (positivos) - Oeste (negativos) y la z la posición en el eje Arriva (negativos) - Abajo (positivos).
    El origen de ese espacio es la posición (0,0,0) que corresponde al punto en el que está el dron en el momento de
    armar.
    Por otra parte, el espacio gráfico es un espacio de pixels en el que el eje X es la horizontal y el Y la vertica.
    El punto (0,0) corresponde a la esquina superior izquierda. Naturalmente, quieremos que la posición (0,0) del
    espacio NED corresponda con el centro del espacio gráfico de manera que el dron inicialmente se muestre en el
    centro del espacio grafico.
    Por otra parte, que los ejes para la representación gráfica sean los ejes de los puntos cardinales, como ocurre
    en el espacio NED puede ser poco intuitivo para volar el dron en interiores. Queremos mejor que el eje vertical
    del espacio gráfico se corresponda con el heading del dron en el momento de armar, es decir, con el eje
    alante-atras.
    Con todo esto vemos que para pasar de un punto del espacio NED a un pixel del espacio grafico hay que hacer
    tres transformaciones. Primero una rotación respeto al centro para alinear el heading inicial del dron con la
    vertical del grafico. Luego hay que hacer una traslacion para alinear el centro del espacio NED con el centro del
    grafico. Y también hay que hacer un escalado para ajustar el tamaño del espacio NED que se quiere representar
    con el tamaño del espacio gráfico.
    '''


    def __init__(self, heading_inicial_deg, ancho_canvas_px, alto_canvas_px, ancho_fisico_m, alto_fisico_m):
        """
        heading_inicial_deg: heading del dron en grados (0° = Norte) al conectar. Necesario para hacer la rotación
        ancho_canvas_px, alto_canvas_px: dimensiones del espacio grafico en píxeles.
        ancho_fisico_m, alto_fisico_m: dimensiones reales del espacio NED (en metros).
        """
        self.heading_inicial_rad = math.radians(heading_inicial_deg)

        self.ancho_canvas = ancho_canvas_px
        self.alto_canvas = alto_canvas_px

        self.ancho_fisico = ancho_fisico_m
        self.alto_fisico = alto_fisico_m

        # Centro del canvas en píxeles
        self.cx = ancho_canvas_px / 2.0
        self.cy = alto_canvas_px / 2.0

        # Escala (pixeles por metro)
        self.escala_x = ancho_canvas_px / ancho_fisico_m
        self.escala_y = alto_canvas_px / alto_fisico_m

    def ned_a_canvas(self, x_ned_m, y_ned_m):
        """
        Convierte posición NED (metros) a coordenadas canvas (píxeles)
        aplicando rotación, escalado y centrado.
        """
        # Rotar según heading inicial (transformar a referencia del dron)
        vertical_m =  x_ned_m * math.cos(self.heading_inicial_rad) + y_ned_m * math.sin(self.heading_inicial_rad)
        horizontal_m = -x_ned_m * math.sin(self.heading_inicial_rad) + y_ned_m * math.cos(self.heading_inicial_rad)

        # Escalar de metros a píxeles
        horizontal_px = horizontal_m * self.escala_x
        vertical_px = vertical_m * self.escala_y

        # Convertir a coordenadas canvas, con origen en centro y eje Y invertido para canvas
        canvas_x = self.cx + horizontal_px
        canvas_y = self.cy - vertical_px

        return canvas_x, canvas_y

    def canvas_a_ned(self, canvas_x_px, canvas_y_px):
        """
        Convierte coordenadas canvas (píxeles) a posición NED (metros)
        aplicando transformación inversa.
        """
        # Diferencia desde el centro del canvas
        horizontal_px = canvas_x_px - self.cx
        vertical_px = -(canvas_y_px - self.cy)

        # Escalar píxeles a metros
        horizontal_m = horizontal_px / self.escala_x
        vertical_m = vertical_px / self.escala_y

        # Rotación inversa para volver a NED
        x_ned_m = vertical_m * math.cos(self.heading_inicial_rad) - horizontal_m * math.sin(self.heading_inicial_rad)
        y_ned_m = vertical_m * math.sin(self.heading_inicial_rad) + horizontal_m * math.cos(self.heading_inicial_rad)

        return x_ned_m, y_ned_m



def CrearEscenarioInDoor (self, heading_inicial_deg, ancho_canvas_px, alto_canvas_px, ancho_fisico_m, alto_fisico_m ):
    self.conversor = TransformadorNEDCanvasEscalado ( heading_inicial_deg, ancho_canvas_px, alto_canvas_px, ancho_fisico_m, alto_fisico_m)


def EstablecerGeofences (self,geofences ):
    # En geofenes hay una lista de polígonos, todos ellos en coordenadas del espacio gráfico
    # El primer polígono es un geofences de inclusión y el resto representan obstáculos
    # Tengo que convertir las coordenadas gráficas a coordenadas NED
    self.escenarioReal = []
    for poligono in geofences:
        poligonoReal = []
        for punto in poligono:
            poligonoReal.append(self.conversor.canvas_a_ned(punto[0], punto[1]))
        self.escenarioReal.append(poligonoReal)

def Canvas_a_NED (self, canvas_x_px, canvas_y_px):
    return self.comversor.canvas_a_ned (canvas_x_px, canvas_y_px)

def NED_a_Canvas (self, x_ned_m, y_ned_m):
    return self.conversor.ned_a_canvas(x_ned_m, y_ned_m)


def _ActivaGeofenceIndoor(self, callback = None):
    self.checkingInDoorGeofence = True
    while self.checkingInDoorGeofence:
        # veamos en qué posición estamos (coordenadas NED)
        punto = (self.position[0], self.position[1])
        # miro si estoy en el primer polígono del escenario, que es el de inclusión
        poligono = self.escenarioReal[0]
        if not self._punto_en_poligono(poligono, punto):
            if callback:
                callback(self.id,0)  # Aviso de que se ha detectado fence inclusion
            # veo en qué dirección viene el dron para alejarlo 2 metros en la misma dirección, sentido contrario
            x = -self.speeds[0]
            y = -self.speeds[1]
            z = 2
            modo = self.flightMode
            self.setFlightMode('GUIDED')
            # para moverlo en sentido contrario al que traia, z metros tengo que calcular distancias en direcciones X,Y
            step_x, step_y = self._catetos_semejantes(x, y, z)
            self._move_distance_2(step_x, step_y)
            self.setFlightMode(modo)
            if callback:
                callback(self.id,0)  # Segundo aviso (vuelvo a situación normal)
        # ahora miro los poligonos de exclusión
        for i in range(1, len(self.escenarioReal)):
            poligono = self.escenarioReal[i]
            if self._punto_en_poligono(poligono, punto):
                if callback:
                    callback(self.id,i)  # Aviso de que se ha detectado obstaculo i
                x = -self.speeds[0]
                y = -self.speeds[1]
                z = 2
                modo = self.flightMode
                self.setFlightMode('GUIDED')
                step_x, step_y = self._catetos_semejantes(x, y, z)
                self._move_distance_2(step_x, step_y)
                self.setFlightMode(modo)
                if callback:
                    callback(self.id, i)  # Segundo aviso (vuelvo a situación normal)

        time.sleep(0.2)


def ActivaGeofenceIndoor (self, callback = None):
    threading.Thread(target=self._ActivaGeofenceIndoor, args=[callback]).start()

def _punto_en_poligono(self, poligono, punto):
    """
    Determina si un punto está dentro de un polígono.

    Parámetros:
        poligono: lista de tuplas (x, y) representando los vértices del polígono.
        punto: tupla (x, y) del punto a evaluar.

    Retorna:
        True si el punto está dentro o en el borde del polígono, False si está fuera.
    """

    x, y = punto
    dentro = False
    n = len(poligono)

    for i in range(n):
        x1, y1 = poligono[i]
        x2, y2 = poligono[(i + 1) % n]  # siguiente vértice (cerrando polígono)

        # Comprobamos si el punto está en un borde
        if ((y - y1) * (x2 - x1) == (x - x1) * (y2 - y1) and
                min(x1, x2) <= x <= max(x1, x2) and
                min(y1, y2) <= y <= max(y1, y2)):
            return True  # está sobre un borde

        # Algoritmo ray casting
        intersecta = ((y1 > y) != (y2 > y)) and \
                     (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1)
        if intersecta:
            dentro = not dentro

    return dentro

def _catetos_semejantes(self, x, y, z):
    """
    Calcula los catetos de un triángulo semejante al dado,
    pero cuya hipotenusa mide z.

    Parámetros:
        x (float): Cateto 1 del triángulo original
        y (float): Cateto 2 del triángulo original
        z (float): Hipotenusa deseada del nuevo triángulo

    Retorna:
        (float, float): Catetos del nuevo triángulo
    """
    h_original = math.sqrt(x ** 2 + y ** 2)
    if h_original == 0:
        raise ValueError("Los catetos originales no pueden ser ambos cero.")

    factor_escala = z / h_original
    return x * factor_escala, y * factor_escala

def DesactivaGeofenceIndoor (self):
    self.checkingInDoorGeofence = False