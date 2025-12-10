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

    def lista_canvas_a_ned (self, lista):
        resultado = []
        for punto in lista:
            resultado.append ((self.canvas_a_ned (punto[0], punto  [1])))
        return resultado
