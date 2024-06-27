import json
import time
import tkinter as tk

from tkinter import messagebox
import paho.mqtt.client as mqtt
import tkintermapview
from PIL import Image, ImageTk

# esta función espera 5 segundos y pone en los botones los colores correspondientes a la situación inicial
def restart ():
    time.sleep (5)

    armBtn['text'] = 'Armar'
    armBtn['fg'] = 'black'
    armBtn['bg'] = 'dark orange'

    takeOffBtn['text'] = 'Despegar'
    takeOffBtn['fg'] = 'black'
    takeOffBtn['bg'] = 'dark orange'

    landBtn['text'] = 'Aterrizar'
    landBtn['fg'] = 'black'
    landBtn['bg'] = 'dark orange'

    RTLBtn['text'] = 'RTL'
    RTLBtn['fg'] = 'black'
    RTLBtn['bg'] = 'dark orange'

    previousBtn['fg'] = 'black'
    previousBtn['bg'] = 'dark orange'

# ejecutaré esto cada vez que llegue un paquete de telemetría
def showTelemetryInfo (telemetry_info):
    '''global heading, altitude, groundSpeed, state
    global altShowLbl, headingShowLbl, speedShowLbl'''
    global dronIcon
    global home_lat, home_lon
    # recupero la posición en la que está el dron
    lat = telemetry_info['lat']
    lon = telemetry_info['lon']

    # si es el primer paquete  entonces ponemos en el mapa el icono de ese dron y la marca del home
    if not dronIcon:
        map_widget.set_marker(lat, lon,icon=homePicture, icon_anchor="center")
        dronIcon = map_widget.set_marker(lat, lon, icon=dronPicture, icon_anchor="center")
        # tomamos nota de las coordenadas de home
        home_lat = lat
        home_lon = lon

    # si no es el primer paquete entonces muevo el icono del dron a la nueva posición
    else:
        dronIcon.set_position(lat, lon)

    # pongo los tres datos de telemetría en sus etiquetas
    altShowLbl['text'] = round (telemetry_info['alt'],2)
    headingShowLbl['text'] =  round(telemetry_info['heading'],2)
    speedShowLbl['text'] = round (telemetry_info['groundSpeed'],2)

    # compruebo si el estado es 'connected' para poner en naranja el boton de armar
    # el dron de desarma automáticamente si, después de armar, pasa un tiempo sin despegar
    if telemetry_info['state'] == 'connected':
        armBtn['text'] = 'Armar'
        armBtn['fg'] = 'black'
        armBtn['bg'] = 'dark orange'


def connect ():
    client.publish('interfazGlobal/autopilotServiceDemo/connect')
    # cambiamos el color del boton
    connectBtn['text'] = 'conectando...'
    connectBtn['fg'] = 'black'
    connectBtn['bg'] = 'yellow'



def arm ():
    client.publish('interfazGlobal/autopilotServiceDemo/arm')
    armBtn['text'] = 'armando...'
    armBtn['fg'] = 'black'
    armBtn['bg'] = 'yellow'

def inTheAir ():
    # ya ha alcanzado la altura de despegue
    takeOffBtn['text'] = 'En el aire'
    takeOffBtn['fg'] = 'white'
    takeOffBtn['bg'] = 'green'


def takeoff ():
    client.publish('interfazGlobal/autopilotServiceDemo/takeOff')
    takeOffBtn['text'] = 'despegando...'
    takeOffBtn['fg'] = 'black'
    takeOffBtn['bg'] = 'yellow'

def onEarth (op):
    # estamos en tierra
    if op == 'land':
        # venimos de un aterrizaje
        landBtn['text'] = 'En tierra'
        landBtn['fg'] = 'white'
        landBtn['bg'] = 'green'
    else:
        # venimos de un RTL
        RTLBtn['text'] = 'En tierra'
        RTLBtn['fg'] = 'white'
        RTLBtn['bg'] = 'green'

def land ():
    client.publish('interfazGlobal/autopilotServiceDemo/Land')
    landBtn['text'] = 'aterrizando...'
    landBtn['fg'] = 'black'
    landBtn['bg'] = 'yellow'

def RTL():
    client.publish('interfazGlobal/autopilotServiceDemo/RTL')
    RTLBtn['text'] = 'retornando...'
    RTLBtn['fg'] = 'black'
    RTLBtn['bg'] = 'yellow'

def go (direction, btn):
    global dron, previousBtn
    # cambio el color del anterior boton clicado (si lo hay)
    if previousBtn:
        previousBtn['fg'] = 'black'
        previousBtn['bg'] = 'dark orange'

    # navegamos en la dirección indicada
    client.publish('interfazGlobal/autopilotServiceDemo/go', direction)
    # pongo en verde el boton clicado
    btn['fg'] = 'white'
    btn['bg'] = 'green'
    # tomo nota de que este es el último botón clicado
    previousBtn = btn


def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("connected OK Returned code=",rc)
    else:
        print("Bad connection Returned code=",rc)


def on_message(client, userdata, message):
    # aqui proceso los eventos que me envía el autopilot service
    # basicamente son las indicaciones de que se han ido completando las operaciones solicitadas
    # lo cual me permite ir cambiando los colores de los botones
    if message.topic == 'autopilotServiceDemo/interfazGlobal/telemetryInfo':
        # la telemetria llega en json
        # la envio a la función que procesa esa información
        telemetry_info = json.loads(message.payload)
        showTelemetryInfo (telemetry_info)
    if message.topic == 'autopilotServiceDemo/interfazGlobal/connected':
        connectBtn['text'] = 'Conectado'
        connectBtn['fg'] = 'white'
        connectBtn['bg'] = 'green'
        # una vez conectado pido que envíe datos de telemetría
        client.publish('interfazGlobal/autopilotServiceDemo/startTelemetry')
    if message.topic == 'autopilotServiceDemo/interfazGlobal/armed':
        armBtn['text'] = 'Armado'
        armBtn['fg'] = 'white'
        armBtn['bg'] = 'green'
    if message.topic == 'autopilotServiceDemo/interfazGlobal/flying':
        takeOffBtn['text'] = 'En el aire'
        takeOffBtn['fg'] = 'white'
        takeOffBtn['bg'] = 'green'

    if message.topic == 'autopilotServiceDemo/interfazGlobal/landed':
        landBtn['text'] = 'En tierra'
        landBtn['fg'] = 'white'
        landBtn['bg'] = 'green'
        restart()
    if message.topic == 'autopilotServiceDemo/interfazGlobal/atHome':
        RTLBtn['text'] = 'En tierra'
        RTLBtn['fg'] = 'white'
        RTLBtn['bg'] = 'green'
        restart()
    if message.topic == 'autopilotServiceDemo/interfazGlobal/missionUploaded':
        uploadMissionBtn['text'] = 'Misión preparada'
        uploadMissionBtn['fg'] = 'white'
        uploadMissionBtn['bg'] = 'green'
    if message.topic == 'autopilotServiceDemo/interfazGlobal/missionEnded':
        runMissionBtn['text'] = 'Misión finalizada'
        runMissionBtn['fg'] = 'white'
        runMissionBtn['bg'] = 'green'

def closePath():
    # estamos creando una misión y acabamos de darle al boton derecho del mouse para cerrar
    # dibujo el último tramo de la misión, que va del último waypoint introducido al home
    paths.append(map_widget.set_path([waypoints[-1], (home_lat, home_lon)], color='red', width=3))

def defineMission ():
    global waypoints, markers, paths
    # indicamos que queremos capturar el click sobre el boton izquierdo del mouse para marcar los waypoints de la misión
    # y el click sobre el derecho para indicar que cerramos la misión
    map_widget.add_right_click_menu_command(label="Cierra el camino", command=closePath, pass_coords=False)
    map_widget.add_left_click_map_command(getWaypoint)
    # necesitaremos guardaar los waypoints, marcadores y líneas para poder borrarlos cuando sea necesario
    waypoints = []
    markers = []
    paths = []
    # informo del tema de los botones del mouse para que el usuario no se despiste
    messagebox.showinfo("showinfo", "Con el boton izquierdo del ratón señala los waypoints\nCon el boton derecho cierra la misión")


def getWaypoint (coords):
    # acabo de clicar con el botón izquierdo para fijar un waypoint de la misión
    # observar que waypoints, marcadores y líneas los guardo en listas para poder recuperarlos cuando lo necesite
    if len(waypoints) == 0:
        # es el primero
        # hago una línea desde el home hasta el punto clicado
        paths.append (map_widget.set_path([(home_lat, home_lon), coords], color = 'red', width = 3))
    else:
        # si no es el primer waypoint trazo una línea desde el anterior a este
        paths.append(map_widget.set_path([waypoints[-1], coords], color='red', width=3))
    # guardo el nuevo waypoint
    waypoints.append (coords)
    # añado el icono del waypoint
    markers.append(
            map_widget.set_marker(coords[0], coords[1], icon=wpPicture, icon_anchor="center", text=str(len(waypoints))))


def runMission ():
    client.publish("interfazGlobal/autopilotServiceDemo/runMission")
    runMissionBtn['text'] = 'Ejecutando misión...'
    runMissionBtn['fg'] = 'black'
    runMissionBtn['bg'] = 'yellow'


def clearMission ():
    global waypoints
    global markers, paths
    # elimino marcadores y líneas del mapa
    for marker in markers:
        marker.delete()
    for path in paths:
        path.delete()
    # vacio las listas
    waypoints = []
    markers = []
    paths = []

def uploadMission ():
    # construyo la estrucutura con al misión en el formato que requiere la librería
    # primero la lista de waypoints
    waypointList = [{'lat': coord[0], 'lon': coord[1], 'alt': 5} for coord in waypoints]
    # y ahora los pongo junto a la altura de despegu
    mission = {"takeOffAlt": 5, "waypoints": waypointList}
    # paso la misión en formato json
    client.publish("interfazGlobal/autopilotServiceDemo/uploadMission", json.dumps(mission))
    uploadMissionBtn['text'] = 'Cargando misión...'
    uploadMissionBtn['fg'] = 'black'
    uploadMissionBtn['bg'] = 'yellow'


def crear_ventana():
    global client
    global  altShowLbl, headingShowLbl,  speedSldr, gradesSldr, speedShowLbl
    global connectBtn, armBtn, takeOffBtn, landBtn, RTLBtn, uploadMissionBtn, runMissionBtn
    global previousBtn # aqui guardaré el ultimo boton de navegación clicado
    global dronPicture, map_widget, dronIcon, wpPicture, homePicture
    global waypoints

    client = mqtt.Client("InterfazGlobal",transport="websockets")

    # me conecto al broker publico y gratuito
    broker_address = "broker.hivemq.com"
    broker_port = 8000

    '''# me conecto al broker privado 
    broker_address = "dronseetac.upc.edu"
    broker_port = 8000
    client.username_pw_set(
     'dronsEETAC', 'mimara1456.'
    )
    '''

    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(broker_address, broker_port)

    # me subscribo a cualquier mensaje  que venga del autopilot service
    client.subscribe('autopilotServiceDemo/interfazGlobal/#')
    client.loop_start()

    previousBtn = None

    ventana = tk.Tk()
    ventana.title("Dashboard con conexión global")

    # El panel principal tiene una fila y dos columnas
    ventana.rowconfigure(0, weight=1)
    ventana.columnconfigure(0, weight=1)
    ventana.columnconfigure(1, weight=1)

    controlFrame = tk.LabelFrame(ventana, text='Control')
    controlFrame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
    # El frame de control aparece en la primera columna

    # la interfaz tiene 8 filas y dos columnas
    controlFrame.rowconfigure(0, weight=1)
    controlFrame.rowconfigure(1, weight=1)
    controlFrame.rowconfigure(2, weight=1)
    controlFrame.rowconfigure(3, weight=1)
    controlFrame.rowconfigure(4, weight=1)
    controlFrame.rowconfigure(5, weight=1)
    controlFrame.rowconfigure(6, weight=1)
    controlFrame.rowconfigure(7, weight=1)

    controlFrame.columnconfigure(0, weight=1)
    controlFrame.columnconfigure(1, weight=1)

    # Disponemos los botones, indicando qué función ejecutar cuando se clica cada uno de ellos

    # El botón para conectar ocupa dos columnas
    connectBtn = tk.Button(controlFrame, text="Conectar", bg="dark orange", command = connect)
    connectBtn.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
    # aqui tenemos un frame para definir, cargar y ejecutar misiones
    # también ocupa dos columnas
    missionFrame = tk.LabelFrame (controlFrame, text= "Misión")
    missionFrame.grid(row=1, column=0, columnspan = 2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
    missionFrame.rowconfigure(0, weight=1)
    missionFrame.rowconfigure(1, weight=1)
    missionFrame.columnconfigure(0, weight=1)
    missionFrame.columnconfigure(1, weight=1)

    # los dos botones siguientes están en la misma fila
    defMissionBtn = tk.Button(missionFrame, text="Definir la misión", bg="dark orange", command=defineMission)
    defMissionBtn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    clearMissionBtn = tk.Button(missionFrame, text="Borrar", bg="dark orange", command=clearMission)
    clearMissionBtn.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # y estos dos en la fila siguiente
    uploadMissionBtn = tk.Button(missionFrame, text="Cargar la mision", bg="dark orange", command=uploadMission)
    uploadMissionBtn.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    runMissionBtn = tk.Button(missionFrame, text="Ejecuta la misión", bg="dark orange", command=runMission)
    runMissionBtn.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # ahora tenemos más botones para operaciones básicas
    armBtn = tk.Button(controlFrame, text="Armar", bg="dark orange", command=arm)
    armBtn.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    takeOffBtn = tk.Button(controlFrame, text="Despegar", bg="dark orange", command=takeoff)
    takeOffBtn.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)


    # los dos siguientes también están en la misma fila
    landBtn = tk.Button(controlFrame, text="Aterrizar", bg="dark orange", command=land)
    landBtn.grid(row=4, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    RTLBtn = tk.Button(controlFrame, text="RTL", bg="dark orange", command=RTL)
    RTLBtn.grid(row=4, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # este es el frame para la navegación. Pequeña matriz de 3 x 3 botones
    navFrame = tk.LabelFrame (controlFrame, text = "Navegación")
    navFrame.grid(row=5, column=0, columnspan = 2, padx=50, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    navFrame.rowconfigure(0, weight=1)
    navFrame.rowconfigure(1, weight=1)
    navFrame.rowconfigure(2, weight=1)
    navFrame.columnconfigure(0, weight=1)
    navFrame.columnconfigure(1, weight=1)
    navFrame.columnconfigure(2, weight=1)

    # al clicar en cualquiera de los botones se activa la función go a la que se le pasa la dirección
    # en la que hay que navegar y el boton clicado, para que la función le cambie el color
    NWBtn = tk.Button(navFrame, text="NW", bg="dark orange",
                        command= lambda: go("NorthWest", NWBtn))
    NWBtn.grid(row=0, column=0, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    NoBtn = tk.Button(navFrame, text="No", bg="dark orange",
                        command= lambda: go("North", NoBtn))
    NoBtn.grid(row=0, column=1, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    NEBtn = tk.Button(navFrame, text="NE", bg="dark orange",
                        command= lambda: go("NorthEast", NEBtn))
    NEBtn.grid(row=0, column=2, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    WeBtn = tk.Button(navFrame, text="We", bg="dark orange",
                        command=lambda: go("West", WeBtn))
    WeBtn.grid(row=1, column=0, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    StopBtn = tk.Button(navFrame, text="St", bg="dark orange",
                        command=lambda: go("Stop", StopBtn))
    StopBtn.grid(row=1, column=1, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    EaBtn = tk.Button(navFrame, text="Ea", bg="dark orange",
                        command=lambda: go("East", EaBtn))
    EaBtn.grid(row=1, column=2, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)


    SWBtn = tk.Button(navFrame, text="SW", bg="dark orange",
                        command=lambda: go("SouthWest", SWBtn))
    SWBtn.grid(row=2, column=0, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    SoBtn = tk.Button(navFrame, text="So", bg="dark orange",
                        command=lambda: go("South", SoBtn))
    SoBtn.grid(row=2, column=1, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    SEBtn = tk.Button(navFrame, text="SE", bg="dark orange",
                        command=lambda: go("SouthEast", SEBtn))
    SEBtn.grid(row=2, column=2, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    # Este es el frame para mostrar los datos de telemetría
    # Contiene etiquetas para informar de qué datos son y los valores. Solo nos interesan 3 datos de telemetría
    telemetryFrame = tk.LabelFrame(controlFrame, text="Telemetría")
    telemetryFrame.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)

    telemetryFrame.rowconfigure(0, weight=1)
    telemetryFrame.rowconfigure(1, weight=1)

    telemetryFrame.columnconfigure(0, weight=1)
    telemetryFrame.columnconfigure(1, weight=1)
    telemetryFrame.columnconfigure(2, weight=1)

    # etiquetas informativas
    altLbl = tk.Label(telemetryFrame, text='Altitud')
    altLbl.grid(row=0, column=0,  padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    headingLbl = tk.Label(telemetryFrame, text='Heading')
    headingLbl.grid(row=0, column=1,  padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    speedLbl = tk.Label(telemetryFrame, text='Speed')
    speedLbl.grid(row=0, column=2,  padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # etiquetas para colocar aqui los datos cuando se reciben
    altShowLbl = tk.Label(telemetryFrame, text='')
    altShowLbl.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    headingShowLbl = tk.Label(telemetryFrame, text='',)
    headingShowLbl.grid(row=1, column=1,  padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    speedShowLbl = tk.Label(telemetryFrame, text='', )
    speedShowLbl.grid(row=1, column=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)



    # Aquí tenemos el frame que se muestra en la columna de la derecha, que contiene el mapa
    mapaFrame = tk.LabelFrame(ventana, text='Mapa')
    mapaFrame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # creamos el widget para el mapa
    map_widget = tkintermapview.TkinterMapView(mapaFrame, width=900, height=600, corner_radius=0)
    map_widget.grid(row=0, column=0, padx=5, pady=5)
    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                    max_zoom=22)
    map_widget.set_position(41.3808982, 2.1228229)  # Coordenadas del Nou Camp
    map_widget.set_zoom(19)

    # ahora cargamos las imagenes de los iconos que vamos a usar

    # icono del dron
    pic1 = Image.open("images/drone.png")
    pic1_resized = pic1.resize((20, 20), Image.LANCZOS)
    dronPicture = ImageTk.PhotoImage(pic1_resized)
    dronIcon = None

    # icono para los waypoints
    pic1 = Image.open("images/wp.png")
    pic1_resized = pic1.resize((20, 20), Image.LANCZOS)
    wpPicture = ImageTk.PhotoImage(pic1_resized)

    # icono para marcar el home
    pic1 = Image.open("images/home.png")
    pic1_resized = pic1.resize((20, 20), Image.LANCZOS)
    homePicture = ImageTk.PhotoImage(pic1_resized)


    return ventana


if __name__ == "__main__":
    ventana = crear_ventana()
    ventana.mainloop()
