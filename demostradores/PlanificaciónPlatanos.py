import json
import tkinter as tk
import os

from tkinter import messagebox

import tkintermapview
from PIL import Image, ImageTk
import pyautogui
import win32gui
import glob
from dronLink.Dron import Dron
import geopy.distance
from geographiclib.geodesic import Geodesic

'''
Ejemplo de estructura de datos que representa un escenario
scenario = [
        {
            'type': 'polygon',
            'waypoints': [
                {'lat': 41.2764398, 'lon': 1.9882585},
                {'lat': 41.2761999, 'lon': 1.9883537},
                {'lat': 41.2763854, 'lon': 1.9890994},
                {'lat': 41.2766273, 'lon': 1.9889948}
            ]
        },
        {
            'type': 'polygon',
            'waypoints': [
                {'lat': 41.2764801, 'lon': 1.9886541},
                {'lat': 41.2764519, 'lon': 1.9889626},
                {'lat': 41.2763995, 'lon': 1.9887963},
            ]
        },
        {
            'type': 'polygon',
            'waypoints': [
                {'lat': 41.2764035, 'lon': 1.9883262},
                {'lat': 41.2762160, 'lon': 1.9883537},
                {'lat': 41.2762281, 'lon': 1.9884771}
            ]
        },
        {
            'type': 'circle',
            'radius': 2,
            'lat': 41.2763430,
            'lon': 1.9883953
        }
    ]

El escenario tiene 4 fences. El primero es el de inclusión, de tipo 'polygon'. 
Luego tiene 3 fences de exclusión que representan los obstáculos. Los dos primeros son de tipo 'polygon' 
y el tercero es de tipo 'circle'.
'''



# Funciones para crear escenario

def createBtnClick ():
    global scenario, polys, markers
    scenario = []
    # limpiamos el mapa de los elementos que tenga
    clear()
    # quitamos el frame de selección
    selectFrame.grid_forget()
    # visualizamos el frame de creación
    createFrame.grid(row=1, column=0,  columnspan=2, padx=5, pady=5, sticky=tk.N +  tk.E + tk.W)

    createBtn['text'] = 'Creando...'
    createBtn['fg'] = 'white'
    createBtn['bg'] = 'green'

    selectBtn['text'] = 'Seleccionar'
    selectBtn['fg'] = 'black'
    selectBtn['bg'] = 'dark orange'

# iniciamos la creación de un fence tipo polígono
def definePoly(type):
    global fence, paths, polys
    global fenceType

    fenceType = type # 1 es inclusión y 2 es exclusión

    paths = []
    fence = {
        'type' : 'polygon',
        'waypoints': []
    }
    # informo del tema de los botones del mouse para que el usuario no se despiste
    messagebox.showinfo("showinfo",
                        "Con el boton izquierdo del ratón señala los waypoints\nCon el boton derecho cierra el polígono")

# iniciamos la creación de un fence tipo círculo
def defineCircle(type):
    global fence, paths, polys
    global fenceType, centerFixed

    fenceType = type  # 1 es inclusión y 2 es exclusión
    paths = []
    fence = {
        'type': 'circle'
    }
    centerFixed = False
    # informo del tema de los botones del mouse para que el usuario no se despiste
    messagebox.showinfo("showinfo",
                        "Con el boton izquierdo señala el centro\nCon el boton derecho marca el límite del círculo")

# capturamos el siguiente click del mouse
def getFenceWaypoint (coords):
    global marker, centerFixed
    # acabo de clicar con el botón izquierdo
    # veamos si el fence es un polígono o un círculo
    if fence['type'] == 'polygon':
        if len(fence['waypoints']) == 0:
            # es el primer waypoint del fence. Pongo un marcador
            if fenceType == 1:
                # en el fence de inclusión (límites del escenario)
                marker = map_widget.set_marker(coords[0], coords[1], icon=i_wp, icon_anchor="center")
            else:
                # es un obstáculo
                marker = map_widget.set_marker(coords[0], coords[1], icon=e_wp, icon_anchor="center")

        if len(fence['waypoints']) > 0:
            # trazo una línea desde el anterior a este
            lat = fence['waypoints'][-1]['lat']
            lon = fence['waypoints'][-1]['lon']
            # elijo el color según si es de inclusión o un obstáculo
            if fenceType == 1:
                paths.append(map_widget.set_path([(lat,lon), coords], color='blue', width=3))
            else:
                paths.append(map_widget.set_path([(lat,lon), coords], color='red', width=3))
            # si es el segundo waypoint quito el marcador que señala la posición del primero
            if len(fence['waypoints']) == 1:
                marker.delete()

        # guardo el nuevo waypoint
        fence['waypoints'].append ({'lat': coords[0], 'lon': coords[1]})
    else:
        # es un círculo. El click indica la posición de centro del circulo
        if centerFixed:
            messagebox.showinfo("Error",
                                "Marca el límite con el botón derecho del mouse")

        else:
            # ponemos un marcador del color adecuado para indicar la posición del centro
            if fenceType == 1:
                marker = map_widget.set_marker(coords[0], coords[1], icon=i_wp, icon_anchor="center")
            else:
                marker = map_widget.set_marker(coords[0], coords[1], icon=e_wp, icon_anchor="center")
            # guardamos la posicion de centro
            fence['lat']= coords[0]
            fence['lon'] = coords[1]
            centerFixed = True

# cerramos el fence
def closeFence(coords):
    global poly, polys
    # estamos creando un fence y acabamos de darle al boton derecho del mouse para cerrar
    # el fence está listo
    if fence['type'] == 'polygon':
        scenario.append(fence)

        # substituyo los paths por un polígono
        for path in paths:
            path.delete()

        poly = []
        for point in  fence['waypoints']:
            poly.append((point['lat'], point['lon']))

        if fenceType == 1:
            # polígono de color azul
            polys.append(map_widget.set_polygon(poly,
                                        outline_color="blue",
                                        fill_color=None,
                                        border_width=3))
        else:
            # polígono de color rojo relleno de rojo
            polys.append(map_widget.set_polygon(poly,
                                                fill_color='red',
                                                outline_color="red",
                                                border_width=3))
    else:
        # Es un circulo y acabamos de marcar el límite del circulo
        # borro el marcador del centro
        marker.delete()
        center= (fence['lat'], fence['lon'])
        limit = (coords[0], coords[1])
        radius = geopy.distance.geodesic(center, limit).m
        # el radio del círculo es la distancia entre el centro y el punto clicado
        fence['radius'] = radius
        # ya tengo completa la definición del fence
        scenario.append(fence)
        # como no se puede dibujar un circulo con la librería tkintermapview, creo un poligono que aproxime al círculo
        points = getCircle(fence['lat'], fence['lon'], radius)

        # Dibujo en el mapa el polígono que aproxima al círculo, usando el color apropiado según el tipo
        if fenceType == 1:
            polys.append(map_widget.set_polygon(points,
                                                outline_color="blue",
                                                fill_color=None,
                                                border_width=3))
        else:
            polys.append(map_widget.set_polygon(points,
                                                fill_color='red',
                                                outline_color="red",
                                                border_width=3))


# La siguiente función crea una imagen capturando el contenido de una ventana
def screenshot(window_title=None):
    if window_title:
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            win32gui.SetForegroundWindow(hwnd)
            x, y, x1, y1 = win32gui.GetClientRect(hwnd)
            x, y = win32gui.ClientToScreen(hwnd, (x, y))
            x1, y1 = win32gui.ClientToScreen(hwnd, (x1 - x, y1 - y))
            # aquí le indico la zona de la ventana que me interesa, que es básicamente la zona del cesped del Camp Nou
            im = pyautogui.screenshot(region=(x+800, y+250, 530, 580))
            return im
        else:
            print('Window not found!')
    else:
        im = pyautogui.screenshot()
        return im

# guardamos los datos del escenario (imagen y fichero json)
def registerScenario ():
    global scenario

    # voy a guardar el escenario en el fichero con el nombre indicado en el momento de la creación
    jsonFilename = 'scenarios/' + name.get() + ".json"

    with open(jsonFilename, 'w') as f:
        json.dump(scenario, f)
    # aqui capturo el contenido de la ventana que muestra el Camp Nou (zona del cesped, que es dónde está el escenario)
    im = screenshot('Gestión de escenarios')
    imageFilename = 'scenarios/'+name.get()+".png"
    im.save(imageFilename)
    scenario = []
    # limpio la imagen del Camp Nou
    clear()

def getCircle ( lat, lon, radius):
    # aquí creo el polígono que aproxima al círculo
    geod = Geodesic.WGS84
    points = []
    for angle in range(0, 360, 5):  # 5 grados de separación para suavidad
        # me da las coordenadas del punto que esta a una distancia radius del centro (lat, lon) con el ángulo indicado
        g = geod.Direct(lat, lon, angle, radius)
        lat2 = float(g["lat2"])
        lon2 = float(g["lon2"])
        points.append((lat2, lon2))
    return points


# Funciones para seleccionar escenario
def selectBtnClick ():
    global scenarios, current, polys
    scenarios = []
    clear()
    # cargamos en una lista las imágenes de todos los escenarios disponibles
    for file in glob.glob("scenarios/*.png"):
        scene= Image.open(file)
        scene = scene.resize((300, 360))
        scenePic = ImageTk.PhotoImage(scene)
        # en la lista guardamos el nombre que se le dió al escenario y la imagen
        scenarios.append({'name': file.split('.')[0], 'pic':scenePic})

    if len (scenarios) > 0:
        # mostramos ya en el canvas la imagen del primer escenario
        scenarioCanvas.create_image(0,0, image=scenarios[0]['pic'], anchor=tk.NW)
        current = 0
        # hacemos desaparecer el frame de creación y mostramos el de selección
        createFrame.grid_forget()
        selectFrame.grid(row=1, column=0,  columnspan=2, padx=5, pady=5, sticky=tk.N +  tk.E + tk.W)

        selectBtn['text'] = 'Seleccionando...'
        selectBtn['fg'] = 'white'
        selectBtn['bg'] = 'green'

        createBtn['text'] = 'Crear'
        createBtn['fg'] = 'black'
        createBtn['bg'] = 'dark orange'
        # no podemos seleccionar el anterior porque no hay anterior
        prevBtn['state'] = tk.DISABLED
        # y si solo hay 1 escenario tampoco hay siguiente
        if len(scenarios) == 1:
            nextBtn['state'] = tk.DISABLED
        else:
            nextBtn['state'] = tk.NORMAL

        sendBtn['state'] = tk.DISABLED
    else:
        messagebox.showinfo("showinfo",
                            "No hay escenarios para elegir")

def showPrev ():
    global current
    current = current -1
    # mostramos el escenario anterior
    scenarioCanvas.create_image(0, 0, image=scenarios[current]['pic'], anchor=tk.NW)
    # deshabilitamos botones si no hay anterior o siguiente
    if current == 0:
        prevBtn['state'] = tk.DISABLED
    else:
        prevBtn['state'] = tk.NORMAL
    if current == len(scenarios) - 1:
        nextBtn['state'] = tk.DISABLED
    else:
        nextBtn['state'] = tk.NORMAL

def showNext ():
    global current
    current = current +1
    # muestro el siguiente
    scenarioCanvas.create_image(0, 0, image=scenarios[current]['pic'], anchor=tk.NW)
    # deshabilitamos botones si no hay anterior o siguiente
    if current == 0:
        prevBtn['state'] = tk.DISABLED
    else:
        prevBtn['state'] = tk.NORMAL
    if current == len(scenarios) - 1:
        nextBtn['state'] = tk.DISABLED
    else:
        nextBtn['state'] = tk.NORMAL

# Limpiamos el Camp Nou
def clear ():
    global paths, fence, polys
    name.set ("")
    for path in paths:
        path.delete()
    for poly in polys:
        poly.delete()

    paths = []
    polys = []
    '''fence = {
        'type': 'polygon',
        'waypoints': []
    }'''

def deleteScenario ():
    global current
    msg_box = messagebox.askquestion(
        "Atención",
        "¿Seguro que quieres eliminar este escenario?",
        icon="warning",
    )
    if msg_box == "yes":
        # borro los dos ficheros que representan el escenario seleccionado
        os.remove(scenarios[current]['name'] + '.png')
        os.remove(scenarios[current]['name'] + '.json')
        scenarios.remove (scenarios[current])
        # muestro el escenario anterior (o el siguiente si no hay anterior o ninguno si tampoco hay siguiente)
        if len (scenarios) != 0:
            if len (scenarios) == 1:
                # solo queda un escenario
                current = 0
                scenarioCanvas.create_image(0, 0, image=scenarios[current]['pic'], anchor=tk.NW)
                prevBtn['state'] = tk.DISABLED
                nextBtn['state'] = tk.DISABLED
            else:
                # quedan más escenarios
                if current == 0:
                    # hemos borrado el primer escenario de la lista. Mostramos el nuevo primero
                    scenarioCanvas.create_image(0, 0, image=scenarios[current]['pic'], anchor=tk.NW)
                    prevBtn['state'] = tk.DISABLED
                    if len (scenarios) > 1:
                        nextBtn['state'] = tk.NORMAL
                else:
                    # mostramos
                    scenarioCanvas.create_image(0, 0, image=scenarios[current]['pic'], anchor=tk.NW)
                    prevBtn['state'] = tk.NORMAL
                    if current == len (scenarios) -1:
                        nextBtn['state'] = tk.DISABLED
                    else:
                        nextBtn['state'] = tk.NORMAL




            clear()

def drawScenario (scenario):
    global polys

    # borro los elementos que haya en el mapa
    for poly in polys:
        poly.delete()


    # ahora dibujamos el escenario
    inclusion = scenario[0]
    if inclusion['type'] == 'polygon':
        poly = []
        for point in inclusion['waypoints']:
            poly.append((point['lat'], point['lon']))
        polys.append(map_widget.set_polygon(poly,
                                            outline_color="blue",
                                            fill_color=None,
                                            border_width=3))
    else:
        # creo el polígono que aproximará al círculo
        poly = getCircle(inclusion['lat'], inclusion['lon'], inclusion['radius'])
        polys.append(map_widget.set_polygon(poly,
                                            outline_color="blue",
                                            fill_color=None,
                                            border_width=3))
    # ahora voy a dibujar los obstáculos
    for i in range(1, len(scenario)):
        fence = scenario[i]
        if fence['type'] == 'polygon':
            poly = []
            for point in fence['waypoints']:
                poly.append((point['lat'], point['lon']))
            polys.append(map_widget.set_polygon(poly,
                                                outline_color="red",
                                                fill_color="red",
                                                border_width=3))
        else:
            poly = getCircle(fence['lat'], fence['lon'], fence['radius'])
            polys.append(map_widget.set_polygon(poly,
                                                outline_color="red",
                                                fill_color="red",
                                                border_width=3))
def selectScenario ():
    global polys, selectedScenario
    # limpio el mapa
    for poly in polys:
        poly.delete()
    # cargamos el fichero json con el escenario seleccionado
    f = open(scenarios[current]['name'] + '.json')
    selectedScenario = json.load (f)
    # dibujo el escenario
    drawScenario(selectedScenario)
    # habilito el botón para enviar el escenario al dron
    sendBtn['state'] = tk.NORMAL

def informar ():
    messagebox.showinfo("showinfo",
                        "Escenario enviado correctamente")

def draw_arrows(lat, lon):
        global arrows
        arrow_length = 0.00005  # Longitud de las flechas en grados de latitud/longitud

        # Puntos cardinales
        directions = {
            "N": (lat + arrow_length, lon),
            "S": (lat - arrow_length, lon),
            "E": (lat, lon + arrow_length),
            "W": (lat, lon - arrow_length),
        }
        arrows = []
        # Crear las flechas en el mapa
        for direction, (latitude, longitude) in directions.items():
            #map_widget.set_marker(lat, lon, text="•")
            #map_widget.set_marker(latitude, longitude, text=direction)
            arrows.append(map_widget.set_path([(lat, lon), (latitude, longitude)], color="black", width=2))


def processTelemetryInfo (telemetry_info):
    global dronIcon, myZone, myZoneWidget, arrows
    # recupero la posición en la que está el dron
    lat = telemetry_info['lat']
    lon = telemetry_info['lon']
    alt = telemetry_info['alt']

    # si es el primer paquete de este dron entonces ponemos en el mapa el icono de ese dron
    if not dronIcon:
        dronIcon = map_widget.set_marker(lat, lon,
                        icon=dronPicture,icon_anchor="center")
        draw_arrows(lat, lon)
    # si no es el primer paquete entonces muevo el icono a la nueva posición
    else:
        for item in arrows:
            item.delete()

        dronIcon.set_position(lat,lon)
        draw_arrows(lat, lon)


def sendScenario ():
    global connected, dron
    if not connected:
        # me conecto al dron
        dron = Dron ()
        connection_string = 'tcp:127.0.0.1:5763'
        baud = 115200
        dron.connect(connection_string, baud)
        connected = True
    # envío es escenario al dron y le pido que me informe cuando esté listo
    dron.setScenario(selectedScenario, blocking=False, callback=informar)
    dron.send_telemetry_info(processTelemetryInfo)


def loadScenario ():
    # voy a mostrar el escenario que hay cargado en el dron
    global connected, dron
    if not connected:
        dron = Dron()
        connection_string = 'tcp:127.0.0.1:5763'
        baud = 115200
        dron.connect(connection_string, baud)
        connected = True
    scenario = dron.getScenario()
    if scenario:
        drawScenario(scenario)
    else:
        messagebox.showinfo("showinfo",
                        "No hay ningún escenario cargado en el dron")




def crear_ventana():

    global map_widget
    global createBtn,selectBtn, createFrame, name, selectFrame, scene, scenePic,scenarios, current
    global prevBtn, nextBtn, sendBtn
    global scenarioCanvas
    global i_wp, e_wp
    global paths, fence, polys
    global connected
    global dronPicture, dronIcon, nene

    connected = False
    dronIcon = None

    # para guardar datos y luego poder borrarlos
    paths = []
    fence = []
    polys = []


    ventana = tk.Tk()
    ventana.title("Gestión de escenarios")
    ventana.geometry ('1900x1000')

    # El panel principal tiene una fila y dos columnas
    ventana.rowconfigure(0, weight=1)
    ventana.columnconfigure(0, weight=1)
    ventana.columnconfigure(1, weight=1)

    controlFrame = tk.LabelFrame(ventana, text = 'Control')
    controlFrame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
    # El frame de control aparece en la primera columna
    controlFrame.rowconfigure(0, weight=1)
    controlFrame.rowconfigure(1, weight=1)
    controlFrame.columnconfigure(0, weight=1)
    controlFrame.columnconfigure(1, weight=1)

    # botones para crear/seleccionar
    createBtn = tk.Button(controlFrame, text="Crear", bg="dark orange", command = createBtnClick)
    createBtn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
    selectBtn = tk.Button(controlFrame, text="Seleccionar", bg="dark orange", command = selectBtnClick)
    selectBtn.grid(row=0, column=1,  padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

    # frame para crear escenario
    createFrame = tk.LabelFrame(controlFrame, text='Crear escenario')
    # la visualización del frame se hace cuando se clica el botón de crear
    #createFrame.grid(row=1, column=0,  columnspan=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
    createFrame.rowconfigure(0, weight=1)
    createFrame.rowconfigure(1, weight=1)
    createFrame.rowconfigure(2, weight=1)
    createFrame.rowconfigure(3, weight=1)
    createFrame.rowconfigure(4, weight=1)
    createFrame.rowconfigure(5, weight=1)
    createFrame.columnconfigure(0, weight=1)

    tk.Label (createFrame, text='Escribe el nombre aquí')\
        .grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
    # el nombre se usará para poner nombre al fichero con la imagen y al fichero json con el escenario
    name = tk.StringVar()
    tk.Entry(createFrame, textvariable=name)\
        .grid(row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

    inclusionFenceFrame = tk.LabelFrame (createFrame, text ='Definición de los límites del escenario')
    inclusionFenceFrame.grid(row=2, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
    inclusionFenceFrame.rowconfigure(0, weight=1)
    inclusionFenceFrame.columnconfigure(0, weight=1)
    inclusionFenceFrame.columnconfigure(1, weight=1)
    # el fence de inclusión puede ser un poligono o un círculo
    # el parámetro 1 en el command indica que es fence de inclusion
    polyInclusionFenceBtn = tk.Button(inclusionFenceFrame, text="Polígono", bg="dark orange", command = lambda:  definePoly (1))
    polyInclusionFenceBtn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
    circleInclusionFenceBtn = tk.Button(inclusionFenceFrame, text="Círculo", bg="dark orange", command = lambda:  defineCircle (1))
    circleInclusionFenceBtn.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

    # los obstacilos son fences de exclusión y pueden ser también polígonos o círculos
    # el parámetro 2 en el command indica que son fences de exclusión
    obstacleFrame = tk.LabelFrame(createFrame, text='Definición de los obstaculos del escenario')
    obstacleFrame.grid(row=3, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
    obstacleFrame.rowconfigure(0, weight=1)
    obstacleFrame.columnconfigure(0, weight=1)
    obstacleFrame.columnconfigure(1, weight=1)

    polyObstacleBtn = tk.Button(obstacleFrame, text="Polígono", bg="dark orange", command = lambda: definePoly (2))
    polyObstacleBtn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
    circleObstacleBtn = tk.Button(obstacleFrame, text="Círculo", bg="dark orange", command=lambda: defineCircle(2))
    circleObstacleBtn.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

    registerBtn = tk.Button(createFrame, text="Registra escenario", bg="dark orange", command = registerScenario)
    registerBtn.grid(row=4, column=0, padx=5, pady=5, sticky=tk.N +tk.E + tk.W)

    clearBtn = tk.Button(createFrame, text="Limpiar", bg="dark orange", command=clear)
    clearBtn.grid(row=5, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

    # frame para seleccionar escenarios
    selectFrame = tk.LabelFrame(controlFrame, text='Selecciona escenario')
    # la visualización del frame se hace cuando se clica el botón de seleccionar
    #selectFrame.grid(row=1, column=0,  columnspan=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    selectFrame.rowconfigure(0, weight=1)
    selectFrame.rowconfigure(1, weight=1)
    selectFrame.rowconfigure(2, weight=1)
    selectFrame.rowconfigure(3, weight=1)
    selectFrame.rowconfigure(4, weight=1)
    selectFrame.columnconfigure(0, weight=1)
    selectFrame.columnconfigure(1, weight=1)
    selectFrame.columnconfigure(2, weight=1)
    selectFrame.columnconfigure(3, weight=1)

    # en este canvas se mostrarán las imágenes de los escenarios disponibles
    scenarioCanvas = tk.Canvas(selectFrame, width=300, height=360, bg='grey')
    scenarioCanvas.grid(row = 0, column=0, columnspan=4, padx=5, pady=5)

    prevBtn = tk.Button(selectFrame, text="<<", bg="dark orange", command = showPrev)
    prevBtn.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N +  tk.E + tk.W)
    selectScenarioBtn = tk.Button(selectFrame, text="Seleccionar", bg="dark orange", command = selectScenario)
    selectScenarioBtn.grid(row=1, column=1, columnspan = 2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
    nextBtn = tk.Button(selectFrame, text=">>", bg="dark orange", command = showNext)
    nextBtn.grid(row=1, column=3, padx=5, pady=5, sticky=tk.N +  tk.E + tk.W)

    loadBtn = tk.Button(selectFrame, text="Cargar el escenario que hay en el dron", bg="dark orange", command=loadScenario)
    loadBtn.grid(row=2, column=0,columnspan = 4, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

    sendBtn = tk.Button(selectFrame, text="Enviar escenario", bg="dark orange", command=sendScenario)
    sendBtn.grid(row=3, column=0,columnspan = 4, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

    deleteBtn = tk.Button(selectFrame, text="Eliminar escenario", bg="red", fg = 'white', command = deleteScenario)
    deleteBtn.grid(row=4, column=0, columnspan = 4, padx=5, pady=5, sticky=tk.N +  tk.E + tk.W)

    # Aquí tenemos el frame que se muestra en la columna de la derecha, que contiene el mapa
    mapaFrame = tk.LabelFrame(ventana, text='Mapa')
    mapaFrame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
    mapaFrame.rowconfigure(0, weight=1)
    mapaFrame.rowconfigure(1, weight=1)
    mapaFrame.columnconfigure(0, weight=1)

    # creamos el widget para el mapa
    map_widget = tkintermapview.TkinterMapView(mapaFrame, width=1400, height=1000, corner_radius=0)
    map_widget.grid(row=1, column=0, padx=5, pady=5)
    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                    max_zoom=22)
   #map_widget.set_position(41.3808982, 2.1228229)  # Coordenadas del Nou Camp
    map_widget.set_position(41.27641749670308, 1.9886734592081867)  # Coordenadas del dronLab
    map_widget.set_zoom(21)

    # indicamos que capture los eventos de click sobre el mouse
    map_widget.add_right_click_menu_command(label="Cierra el fence", command=closeFence, pass_coords=True)
    map_widget.add_left_click_map_command(getFenceWaypoint)

    # ahora cargamos las imagenes de los iconos que vamos a usar

    # icono para wp de inclusion
    im = Image.open("images/red.png")
    im_resized = im.resize((20, 20), Image.LANCZOS)
    dronPicture = ImageTk.PhotoImage(im_resized)

    # icono para wp de inclusion
    im = Image.open("images/i_wp.png")
    im_resized = im.resize((20, 20), Image.LANCZOS)
    i_wp = ImageTk.PhotoImage(im_resized)

    # icono para wp de exclusión
    im = Image.open("images/e_wp.png")
    im_resized = im.resize((20, 20), Image.LANCZOS)
    e_wp = ImageTk.PhotoImage(im_resized)

    im = Image.open("images/nene.png")
    im_resized = im.resize((25, 25), Image.LANCZOS)
    nene = ImageTk.PhotoImage(im_resized)

    return ventana


if __name__ == "__main__":
    ventana = crear_ventana()
    ventana.mainloop()
