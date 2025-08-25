
import tkinter as tk
from dronLink.Dron import Dron
import math
from JoystickReal import Joystick
from tkinter import messagebox


def dibujar(px,py):
    global idDron, headingInicial, headingLine, movementLine
    if idDron:
        canvas.delete(idDron)
        canvas.delete(headingLine)
        canvas.delete(movementLine)

    radio = 10
    idDron = canvas.create_oval(px-radio, py-radio, px+radio, py+radio, fill="red")

    # Dibuja línea amarilla mostrado el heading (rotado)
    longitud_linea = 50  # en píxeles
    angulo_vertical_deg = dron.heading - headingInicial
    angulo_canvas_rad = math.radians(angulo_vertical_deg)

    # La vertical hacia arriba es -Y, así que:
    dx = longitud_linea * math.sin(angulo_canvas_rad)
    dy = -longitud_linea * math.cos(angulo_canvas_rad)

    headingLine = canvas.create_line(px, py, px + dx, py + dy, fill="yellow", width=2)


    angulo_rad = math.atan2(dron.speeds[1], dron.speeds[0])  # X = cateto horizontal, Y = cateto vertical
    angulo_deg = math.degrees(angulo_rad)

    # Dibuja línea amarilla mostrado el heading (rotado)
    longitud_linea = 50  # en píxeles
    angulo_vertical_deg = angulo_deg - headingInicial
    angulo_canvas_rad = math.radians(angulo_vertical_deg)

    # La vertical hacia arriba es -Y, así que:
    dx = longitud_linea * math.sin(angulo_canvas_rad)
    dy = -longitud_linea * math.cos(angulo_canvas_rad)
    movementLine = canvas.create_line(px, py, px + dx, py + dy, fill="black", width=2)

def procesarTelemetria (telemetryInfo):
    global dron, headingInicial
    # cuando recibo el primer dato de telemetria es cuando por fin se el heading inicial
    # y es cuando puedo crear el escenario
    if dron.conversor == None and dron.heading != None:
        ancho = canvas.winfo_width()
        alto = canvas.winfo_height()
        headingInicial = dron.heading
        # el escenario será un cuadradp de 20 metros de lado
        dron.CrearEscenarioInDoor(headingInicial, ancho, alto, 20,20)
    if dron.conversor:
        # el escenario ya está creado asi que solo hay que dibujar la nueva posición del dron
        x = telemetryInfo['posX']
        y = telemetryInfo['posY']
        px,py = dron.NED_a_Canvas(x,y)
        dibujar (px,py)

# Función para mostrar dimensiones del canvas en consola
def conectar():
    global  dron

    dron = Dron()
    connection_string = 'tcp:127.0.0.1:5763'
    baud = 115200
    dron.connect(connection_string, baud)
    dron.send_local_telemetry_info(procesarTelemetria)

def avisoGeofenceBreak (id, cod):
    global alarmaInclusion, alarmaExclusion
    if cod == 0:
        # se ha saltado los limites del geofence de inclusión.
        if not alarmaInclusion:
            alarmaInclusion = canvas.create_polygon(escenario[0],fill = "", outline="red", width=5)  # color pastel
        else:
            # es el segundo aviso, lo cual indica que ya está operativo de nuevo
            canvas.delete (alarmaInclusion)
            alarmaInclusion = None

    else:
        # se ha saltado los límites de un obstaculo
        if not alarmaExclusion:
            alarmaExclusion = canvas.create_polygon(escenario[cod], fill = "", outline="red", width=5)  # color pastel
        else:
            canvas.delete (alarmaExclusion)
            alarmaExclusion = None

def avisoMinAlt (id):
    global alarmaAltura
    if "Se" in alarmaAltura ['text']:
        # es el segundo aviso asi que ya estamos operativos de nuevo
        alarmaAltura['text'] = ""
    else:
        # alarma
        alarmaAltura ['text'] = "Se ha alcanzado la altura mínima"
        alarmaAltura['fg'] = 'red'

def ponerLimites ():
    global dron, poligono_cerrado, conversor, escenario
    if len(escenario ) ==  0:
        messagebox.showinfo("error",
                            "Primer tienes que dibujar los límites")

    else:
        dron.EstablecerGeofences(escenario)
        dron.ActivaGeofenceIndoor(callback=avisoGeofenceBreak)
        dron.CheckMinAlt(aviso=avisoMinAlt)

def distancia(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)


def dibujarPoly ():
    # Dibujar polígonos
    for i in range (len(escenario)):
        poligono = escenario[i]
        if i == 0:
            canvas.create_polygon(poligono, fill="#87CEFA", outline="blue", width=2)  # color pastel
        else:
            canvas.create_polygon(poligono, fill="#222222", outline="black", width=2)  # color pastel


    if puntos_poligono:
        for x, y in puntos_poligono:
            canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue")

        if len (puntos_poligono)> 1:
            if len(escenario) == 0:
                canvas.create_line(puntos_poligono, fill="blue", width=2)
            else:
                canvas.create_line(puntos_poligono, fill="black", width=2)


puntos_poligono = []
poligono_cerrado = False
escenario = []

def click_canvas(event):
    global poligono_cerrado, puntos_poligono


    if poligono_cerrado:
        print("Empezamos un obstaculo")

        poligono_cerrado = False

    if len(puntos_poligono)> 0  and distancia((event.x, event.y), puntos_poligono[0]) < 10:
        poligono_cerrado = True
        escenario.append (puntos_poligono)
        puntos_poligono = []


        print("Polígono cerrado.")
    else:
        puntos_poligono.append((event.x, event.y))
        print(f"Punto añadido: ({event.x}, {event.y})")

    dibujarPoly()

def ponVelocidad (event):
    global dron
    if not dron:
        messagebox.showinfo("error",
                            "Primer tienes que conectarte con el dron")
    else:
        velocidad = int(scale.get())*100
        newParameters = [{'ID': "LOIT_SPEED", 'Value': velocidad}]
        dron.setParams(newParameters)

def activarJoystick ():
    def identifica(id):
        print("Soy el joystick: ", id)

    Joystick(dron, identifica)

dron = None
conversor = None
idDron = None
alarmaInclusion = None
alarmaExclusion = None
# Crear ventana principal
root = tk.Tk()
root.title("Interfaz con Canvas y Botones")

# Frame para botones (izquierda)
frame_botones = tk.Frame(root, padx=10, pady=10)
frame_botones.pack(side=tk.LEFT, fill=tk.Y)

# Botones


btn1 = tk.Button(frame_botones, text="Conectar", command=conectar)
btn1.pack(pady=5, fill=tk.X)
btn2 = tk.Button(frame_botones, text="Poner limites", command=ponerLimites)
btn2.pack(pady=5, fill=tk.X)
btn3 = tk.Button(frame_botones, text="Activar Joystick", command=activarJoystick)
btn3.pack(pady=5, fill=tk.X)
alarmaAltura = tk.Button(frame_botones, text="")
alarmaAltura.pack(pady=5, fill=tk.X)



label = tk.Label(frame_botones, text="Velocidad", font=("Arial", 12))
label.pack(pady=(10, 0))

# Scale de 1 a 10 con valores marcados
scale = tk.Scale(
    frame_botones,
    from_=1,
    to=10,
    orient="horizontal",
    length=200,
    tickinterval=1  # marca cada valor
)
scale.pack(pady=10)


# Vincular evento al soltar el ratón
scale.bind("<ButtonRelease-1>", ponVelocidad)


# Canvas (derecha)
canvas_size = 400
canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, bg="white")
canvas.pack(side=tk.RIGHT, padx=10, pady=10)
canvas.bind("<Button-1>", click_canvas)

root.mainloop()
