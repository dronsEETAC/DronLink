import tkinter as tk
from dronLink.Dron import Dron
import math

from tkinter import messagebox
from PIL import Image, ImageTk
from Conversor_NED_pixels import TransformadorNEDCanvasEscalado


def dibujar(px, py):
    # muevo de posición el dron (muevo el circulo que representa al dron y las líneas de heading y de velocidad)
    global idDron, headingInicial, headingLine, movementLine
    if idDron:
        # borro icono y líneas
        canvas.delete(idDron)
        canvas.delete(headingLine)
        canvas.delete(movementLine)

    # dibujo el circulo rojo que representa el dron en la nueva posición
    radio = 10
    idDron = canvas.create_oval(px - radio, py - radio, px + radio, py + radio, fill="red")

    # Dibuja línea amarilla mostrado el heading (rotado)
    longitud_linea = 50  # en píxeles
    angulo_vertical_deg = dron.heading - headingInicial
    angulo_canvas_rad = math.radians(angulo_vertical_deg)
    # La vertical hacia arriba es -Y, así que:
    dx = longitud_linea * math.sin(angulo_canvas_rad)
    dy = -longitud_linea * math.cos(angulo_canvas_rad)
    headingLine = canvas.create_line(px, py, px + dx, py + dy, fill="yellow", width=2)

    # ahora dibujo la línea negra que indica la dirección que lleva el dron
    # para eso uso las componentes x e y de la velocidad, que están en el vector speeds
    angulo_rad = math.atan2(dron.speeds[1], dron.speeds[0])
    angulo_deg = math.degrees(angulo_rad)

    # Dibuja línea negra (con la rotación correspondiente
    angulo_vertical_deg = angulo_deg - headingInicial
    angulo_canvas_rad = math.radians(angulo_vertical_deg)

    # La vertical hacia arriba es -Y, así que:
    dx = longitud_linea * math.sin(angulo_canvas_rad)
    dy = -longitud_linea * math.cos(angulo_canvas_rad)
    movementLine = canvas.create_line(px, py, px + dx, py + dy, fill="black", width=2)


def procesarTelemetria(telemetryInfo):
    # aqui proceso cada paquete de telemetría

    global dron, headingInicial, estadoLbl, altLbl, modoLbl, velocidadLbk, conversor
    if "Conectado" in estadoLbl["text"] and dron.state == "armed":
        # el dron ya está armado
        estadoLbl["text"] = 'Armado'
        estadoLbl["fg"] = 'green'
    # cuando recibo el primer dato de telemetria es cuando por fin se el heading inicial
    # y es cuando puedo crear el escenario
    if conversor == None and dron.heading != None:
        # para crear el escenario inDoor tengo que indicarle al conversor:
        #       el heading inicial (para que con independencia de cómo esté el dron orientado inicialmente
        #           lo dibuje orientado en vertical hacia arriba de la pantalla)
        #       el número de pixeles (ancho y alto) del canvas que representa la zona de vuelo
        #       las dimensiones en metros (ancho y alto) de la zona real de vuelo
        # Con esa información el conversor puede trasladar coordenadas de pixles
        # a coordenadas NED y viceversa

        ancho = canvas.winfo_width()
        alto = canvas.winfo_height()
        headingInicial = dron.heading
        # el escenario real es un cuadrado de 100x100 metros
        print ('creo conversor')
        conversor = TransformadorNEDCanvasEscalado(headingInicial, ancho, alto, 100, 100)

    if conversor:
        # el escenario ya está creado asi que solo hay que dibujar la nueva posición del dron
        x = telemetryInfo['posX']
        y = telemetryInfo['posY']
        # hago la conversión de NED a pixels
        px, py = conversor.ned_a_canvas(x, y)
        # muevo el dron en la pantalla
        dibujar(px, py)

    # actualizo los datos de telemetría
    # Estos datos vienen en paquetes de telemetría global, pero como no le he pedido al dron que me envíe esos paquetes
    # accedo directamente a los atributos del dron en los que está la información.
    altLbl['text'] = dron.alt
    estadoLbl['text'] = dron.state
    modoLbl['text'] = dron.flightMode
    velocidadLbl['text'] = round(dron.groundSpeed, 2)


def conectar():
    global dron, conectarBtn, estadoLbl, modoLbl, altLbl

    dron = Dron()
    # me conecto al simulador
    connection_string = 'tcp:127.0.0.1:5763'
    baud = 115200

    # pero podría conectarme al dron real
    # connection_string = 'com3'
    # baud = 57600'

    # me conecto y le indico que quiero 10 paquetes de telemetria por segundo
    dron.connect(connection_string, baud, freq=10)
    conectarBtn["text"] = "Conectado"
    conectarBtn["bg"] = "green"
    conectarBtn["fg"] = "white"
    # le pongo la velocidad de loites inicial
    newParameters = [{'ID': "LOIT_SPEED", 'Value': 300}]
    dron.setParams(newParameters)
    # le pido los datos de telemetría
    dron.send_local_telemetry_info(procesarTelemetria)
    # informo del estado
    estadoLbl["text"] = 'Conectado'
    estadoLbl["fg"] = 'green'
    # del modo de vuelo en el que está inicialmente el dron
    modoLbl["text"] = dron.flightMode
    modoLbl["fg"] = 'red'
    # y de la altura a la que está
    altLbl["text"] = dron.alt
    altLbl["fg"] = 'red'


def avisoBreak(id, cod, nivel):
    # cuando el dron se salte los límites o se acerque peligrosamente la librería llamará a esta función
    # Nos pasan:
    #   el id del dron (que en esta aplicación no se usa),
    #   el codigo del tipo de límite que se ha saltado:
    #       -2: Altura mínima
    #       -1: Altura máxima
    #        0: fence de inclusion
    #        n: Obstaculo n_esimo
    #   el nivel de peligrosidad:
    #        0: Ya está de nuevo en zona segura
    #        1: Esta cerca (peligro)
    #        2: Está a punto de saltar el límite (no se usa en el caso de los límites de altura)

    global alarmaInclusion, alarmaExclusion, minAltLbl, maxAltLbl

    if cod == 0:
        # poligono de inclusión
        if nivel == 2:
            # peligro máximo. La librería habrá hecho que el dron retorne
            if alarmaInclusion:
                # Borro el color amarillo de los límites
                canvas.delete(alarmaInclusion)
            # Marco los límites en rojo
            alarmaInclusion = canvas.create_polygon(escenario[0], fill="", outline="red",
                                                    width=5)
        elif nivel == 1:
            # Se acerca peligrosamente
            # marco los límites en amarillo
            alarmaInclusion = canvas.create_polygon(escenario[0], fill="", outline="yellow",
                                                    width=5)
        elif nivel == 0:
            # He regresado a zona segura
            if alarmaInclusion:
                # borro el color que haya puesto en los límites
                canvas.delete(alarmaInclusion)
            alarmaInclusion = None

    elif cod > 0:
        # Se trata de un obstacilo. El tratamiendo es el mismo que el el caso anterior.
        # Solo cambia el polígono que coloreo, que es el indicado en cod
        if nivel == 2:
            if alarmaExclusion:
                canvas.delete(alarmaExclusion)
            alarmaExclusion = canvas.create_polygon(escenario[cod], fill="", outline="red",
                                                    width=5)
        elif nivel == 1:
            alarmaExclusion = canvas.create_polygon(escenario[cod], fill="", outline="yellow", width=5)

        elif nivel == 0:
            if alarmaExclusion:
                canvas.delete(alarmaExclusion)
            alarmaExclusion = None

    elif cod == -2:
        if nivel == 1:
            # Estoy cerca del límite de altura mínima
            minAltLbl['text'] = "Alarma"
            minAltLbl['fg'] = "red"

        else:
            # Ya estoy en un nivel de altura adecuado
            minAltLbl['text'] = "min Alt"
            minAltLbl['fg'] = "black"

    elif cod == -1:
        if nivel == 1:
            # stoy cerca del límite de altura máxima
            maxAltLbl['text'] = "Alarma"
            maxAltLbl['fg'] = 'red'
        else:
            # Se ha recuperado el nivel de altura adecuado
            maxAltLbl['text'] = "max Alt"
            maxAltLbl['fg'] = "black"


def toggleLimites():
    # Función para activar/desactivsar el control de límites
    global act_desact_btn, dron
    if "Activar" in act_desact_btn["text"]:
        dron.ActivaLimitesIndoor()
        act_desact_btn["text"] = "Desactivar"
        act_desact_btn["fg"] = "white"
        act_desact_btn["bg"] = "green"
        print("activados")
    else:
        dron.DesactivaLimitesIndoor()
        act_desact_btn["text"] = "Activar"
        act_desact_btn["fg"] = "black"
        act_desact_btn["bg"] = "dark orange"


def enviarLimites():
    global dron, poligono_cerrado, conversor, escenario, enviarBtn, limitesEstablecidos
    # para enviar los límites del escenario hay que haber definido algún polígono
    # o al menos una altura mínima o una máxima
    if len(escenario) == 0 and scaleAltMin.get() == 0 and scaleAltMax.get() == 0:
        messagebox.showinfo("error",
                            "Primer tienes que poner algunos límites")

    else:
        # ahora preparo la estructura de datos que necesita la librería para controlar
        limites = {}
        if scaleAltMin.get() != 0:
            limites['minAlt'] = scaleAltMin.get()
        if scaleAltMax.get() != 0:
            limites['maxAlt'] = scaleAltMax.get()
        if len(escenario) > 0:
            limites['inclusion'] = conversor.lista_canvas_a_ned (escenario[0])
            if len(escenario) > 1:
                limites['obstaculos'] = []
                for obstaculo in escenario[1:]:
                    limites['obstaculos'].append (conversor.lista_canvas_a_ned (obstaculo))
        # envio al dron la estructura de datos y le indico que función debe ejecutar en caso de que se salte
        # los límites
        dron.EstablecerLimites(limites, avisoBreak)
        enviarBtn["bg"] = "green"
        enviarBtn["fg"] = "white"
        limitesEstablecidos = True


def dibujarEscenario():
    # Dibujar polígonos
    for i in range(len(escenario)):
        poligono = escenario[i]
        if i == 0:
            # es el poligono de inclusión, que lo dibujo en azul
            canvas.create_polygon(poligono, fill="#87CEFA", outline="blue", width=2)  # color pastel
        else:
            # es un obstaculo, que lo dibujo en negro
            canvas.create_polygon(poligono, fill="#222222", outline="black", width=2)  # color pastel

    # dibujo también los lados del poligono que estoy definiendo y que aun no está acabado
    if puntos_poligono:
        for x, y in puntos_poligono:
            # dibujo un pequeño circulo en los puntos del polígono
            canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue")

        if len(puntos_poligono) > 1:
            # y ahora dibujo las líneas de los lados que tenga en ese momento
            if len(escenario) == 0:
                canvas.create_line(puntos_poligono, fill="blue", width=2)
            else:
                canvas.create_line(puntos_poligono, fill="black", width=2)


def distancia(p1, p2):
    # se usa en click_canvas
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def click_canvas(event):
    # acabo de clicar en el panel. Estoy definiendo un poligono de inclusion o un obstaculo
    global poligono_cerrado, puntos_poligono

    if poligono_cerrado:
        # Ya he acabado con el poligono anterior. Estoy empezando un nuevo obstaculo
        poligono_cerrado = False

    if len(puntos_poligono) > 0 and distancia((event.x, event.y), puntos_poligono[0]) < 10:
        # si he clicado muy cerca del primer punto del polígono que estoy definiendo es que estoy cerrando ese
        # poligono
        poligono_cerrado = True
        # lo añado a la lista de poligonos que constituyen el escenario
        escenario.append(puntos_poligono)
        # vacio la lista de puntos para el siguiente polígono
        puntos_poligono = []
    else:
        # nuevo punto del polígono en curso
        puntos_poligono.append((event.x, event.y))
    # dibujo el esccenario
    dibujarEscenario()


def ponVelocidad(event):
    global dron, limitesEstablecidos
    # hay que cambiar la velocidad de vuelo en loiter poniendo el valor seleccionado en la escala
    if not dron:
        messagebox.showinfo("error",
                            "Primer tienes que conectarte con el dron")
    else:
        velocidad = int(scaleVelocidad.get()) * 100  # la  velocidad en loiter se indica en cm/s
        newParameters = [{'ID': "LOIT_SPEED", 'Value': velocidad}]
        dron.setParams(newParameters)


def activarJoystickTeclado():
    # importo la librería adecuada
    from JoystickTeclado import Joystick
    global canvasInfo, joystickTecladoBtn
    # creo el Joystick y le paso el dron
    Joystick(dron)
    # Cargar la imagen informativa sobre el joystick por teclado
    imagen = Image.open("images/JoystickTeclado.png")
    imagen = imagen.resize((450, 375), Image.LANCZOS)
    imagen_tk = ImageTk.PhotoImage(imagen)
    canvasInfo.create_image(0, 0, anchor=tk.NW, image=imagen_tk)
    canvasInfo.image = imagen_tk
    joystickTecladoBtn['bg'] = 'green'
    joystickTecladoBtn['fg'] = 'white'


def activarJoystickReal():
    # importo la librería adecuada
    from JoystickReal import Joystick
    global canvasInfo, joystickRealBtn
    # creo el Joystick y le paso el dron
    Joystick(dron)
    # Cargo la imagen informativa sobre el Joystick real
    imagen = Image.open("images/JoystickReal.png")
    imagen = imagen.resize((450, 375), Image.LANCZOS)
    imagen_tk = ImageTk.PhotoImage(imagen)
    canvasInfo.create_image(0, 0, anchor=tk.NW, image=imagen_tk)
    canvasInfo.image = imagen_tk
    joystickRealBtn['bg'] = 'green'
    joystickRealBtn['fg'] = 'white'


# Variables para controlar el diseño del escenario (polígonos de inclusión y obstáculos)
puntos_poligono = []
poligono_cerrado = False
escenario = []

conversor = None # para convertir coordenadas NED a pixels y viceversa
dron = None
conversor = None
idDron = None
alarmaInclusion = None
alarmaExclusion = None
# Crear ventana principal
ventana = tk.Tk()
ventana.title("Interfaz para vuelo interior")
ventana.geometry('1900x1000')

# El panel principal tiene una fila y dos columnas
ventana.rowconfigure(0, weight=1)
ventana.columnconfigure(0, weight=1)
ventana.columnconfigure(1, weight=1)

# En la columna de la izquierda van los botones para controlarlo todo
controlFrame = tk.LabelFrame(ventana, text='Control')
controlFrame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

controlFrame.rowconfigure(0, weight=1)
controlFrame.rowconfigure(1, weight=1)
controlFrame.rowconfigure(2, weight=1)
controlFrame.rowconfigure(3, weight=1)
controlFrame.rowconfigure(4, weight=1)
controlFrame.rowconfigure(5, weight=1)
controlFrame.rowconfigure(6, weight=1)

controlFrame.columnconfigure(0, weight=1)
controlFrame.columnconfigure(1, weight=1)

conectarBtn = tk.Button(controlFrame, text="Conectar", bg="dark orange", fg="black", command=conectar)
conectarBtn.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

escalas = tk.Frame(controlFrame)
escalas.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
escalas.rowconfigure(1, weight=1)
escalas.rowconfigure(2, weight=1)
escalas.rowconfigure(3, weight=1)
escalas.columnconfigure(0, weight=1)
escalas.columnconfigure(1, weight=1)

label1 = tk.Label(escalas, text="Velocidad", font=("Arial", 12))
label1.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
scaleVelocidad = tk.Scale(
    escalas,
    from_=1,
    to=5,
    orient="horizontal",
    length=200,
    tickinterval=1  # marca cada valor
)
scaleVelocidad.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
# cuando suelto el control llamo a poner velocidad
scaleVelocidad.bind("<ButtonRelease-1>", ponVelocidad)
scaleVelocidad.set(3)  # 3m/s por defecto

minAltLbl = tk.Label(escalas, text="Alt min", font=("Arial", 12))
minAltLbl.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
scaleAltMin = tk.Scale(
    escalas,
    from_=0,
    to=5,
    orient="horizontal",
    length=200,
    tickinterval=1  # marca cada valor
)
scaleAltMin.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
scaleAltMin.set(0)  # Un 0 por defecto indica que no hay limite mínimo

maxAltLbl = tk.Label(escalas, text="Alt max", font=("Arial", 12))
maxAltLbl.grid(row=2, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
scaleAltMax = tk.Scale(
    escalas,
    from_=0,
    to=10,
    orient="horizontal",
    length=200,
    tickinterval=1  # marca cada valor
)
scaleAltMax.grid(row=2, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
scaleAltMax.set(0)  # tampoco hay limite máximo por defecto

enviarBtn = tk.Button(controlFrame, text="Enviar escenario", bg="dark orange", fg="black", command=enviarLimites)
enviarBtn.grid(row=2, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

act_desact_btn = tk.Button(controlFrame, text="Activar", bg="dark orange", fg="black", command=toggleLimites)
act_desact_btn.grid(row=2, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

infoEscenario = tk.Label(controlFrame, text="Para crear el esenario haz click\nen el panel para indicar los puntos\n "
                                            "que definen los polígonos y haz click \ncerca del primero para cerrar cada polígono.\n "
                                            "Primero crea el polígono correspondiente \nal fence de inclusión y luego \n"
                                            "los polígonos correspondientes a los obstáculos", font=("Arial", 10))
infoEscenario.grid(row=3, column=0, columnspan = 2, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

joystickRealBtn = tk.Button(controlFrame, text="Joystick Real", bg="dark orange", fg="black",
                            command=activarJoystickReal)
joystickRealBtn.grid(row=4, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

joystickTecladoBtn = tk.Button(controlFrame, text="Joystick Teclado", bg="dark orange", fg="black",
                               command=activarJoystickTeclado)
joystickTecladoBtn.grid(row=4, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

# Bloque con datos de telemetría
infoFrame = tk.LabelFrame(controlFrame, text='Info')
infoFrame.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

infoFrame.rowconfigure(0, weight=1)
infoFrame.columnconfigure(0, weight=1)
infoFrame.columnconfigure(1, weight=1)
infoFrame.columnconfigure(2, weight=1)
infoFrame.columnconfigure(3, weight=1)

estadoLbl = tk.Label(infoFrame, text="Estado", font=("Arial", 12))
estadoLbl.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

modoLbl = tk.Label(infoFrame, text="Modo", font=("Arial", 12))
modoLbl.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

altLbl = tk.Label(infoFrame, text="Altura", font=("Arial", 12))
altLbl.grid(row=0, column=2, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

velocidadLbl = tk.Label(infoFrame, text="Velocidad", font=("Arial", 12))
velocidadLbl.grid(row=0, column=3, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

# Aqui pondremos una imagen informativa sobre el joystick elegido (real o teclado)
canvasInfo = tk.Canvas(controlFrame, width=450, height=375, bg="white")
canvasInfo.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

# Cargamos una imagen inicial
imagen = Image.open("images/infoJoystick.png")
imagen = imagen.resize((450, 375), Image.LANCZOS)
imagen_tk = ImageTk.PhotoImage(imagen)
canvasInfo.create_image(0, 0, anchor=tk.NW, image=imagen_tk)
canvasInfo.image = imagen_tk

# En la columna de la derecha tenemos un canvas para mostrar los movimientos del dron
canvas_size = 1000
canvas = tk.Canvas(ventana, width=canvas_size, height=canvas_size, bg="white")
canvas.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)
# Los clicks de raton se usan para marcar los poligonos que hacen de fence de inclusión y obstaculos
canvas.bind("<Button-1>", click_canvas)

ventana.mainloop()
