import json
import time
import tkinter as tk
import os

from tkinter import messagebox
import paho.mqtt.client as mqtt

import tkintermapview
from PIL import Image, ImageTk
import pyscreenshot as ImageGrab
import pygetwindow as gw
import pyautogui
import win32gui
import glob
from dronLink.Dron import Dron


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

# Funciones para crear escenario

def createBtnClick ():
    global scenario, polys, markers
    scenario = []
    clear()
    selectFrame.grid_forget()
    createFrame.grid(row=1, column=0,  columnspan=2, padx=5, pady=5, sticky=tk.N +  tk.E + tk.W)

    createBtn['text'] = 'Creando...'
    createBtn['fg'] = 'white'
    createBtn['bg'] = 'green'

    selectBtn['text'] = 'Seleccionar'
    selectBtn['fg'] = 'black'
    selectBtn['bg'] = 'dark orange'

# iniciamos la creación de un fence
def defineFence(type):
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

# capturamos el siguiente click del mouse
def getFenceWaypoint (coords):
    global marker
    # acabo de clicar con el botón izquierdo para fijar un waypoint del fence

    if len(fence['waypoints']) == 0:
        # es el primer waypoint del fence. Pongo un marcador
        if fenceType == 1:
            marker = map_widget.set_marker(coords[0], coords[1], icon=i_wp, icon_anchor="center")
        else:
            marker = map_widget.set_marker(coords[0], coords[1], icon=e_wp, icon_anchor="center")


    if len(fence['waypoints']) > 0:
        # trazo una línea desde el anterior a este
        lat = fence['waypoints'][-1]['lat']
        lon = fence['waypoints'][-1]['lon']
        if fenceType == 1:
            paths.append(map_widget.set_path([(lat,lon), coords], color='blue', width=3))
        else:
            paths.append(map_widget.set_path([(lat,lon), coords], color='red', width=3))
        if len(fence['waypoints']) == 1:
            # borro el marcador
            marker.delete()

    # guardo el nuevo waypoint
    fence['waypoints'].append ({'lat': coords[0], 'lon': coords[1]})

# cerramos el fence
def closeFence():
    global poly, polys
    # estamos creando un fence y acabamos de darle al boton derecho del mouse para cerrar
    # el fence está listo
    scenario.append(fence)

    # substituyo los paths por un polígono
    for path in paths:
        path.delete()

    poly = []
    for point in  fence['waypoints']:
        poly.append((point['lat'], point['lon']))

    if fenceType == 1:
        polys.append(map_widget.set_polygon(poly,
                                    outline_color="blue",
                                    fill_color=None,
                                    border_width=3))
    else:
        polys.append(map_widget.set_polygon(poly,
                                            fill_color='red',
                                            outline_color="red",
                                            border_width=3))

# para crear una imagen con el escenario creado
def screenshot(window_title=None):
    if window_title:
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            win32gui.SetForegroundWindow(hwnd)
            x, y, x1, y1 = win32gui.GetClientRect(hwnd)
            x, y = win32gui.ClientToScreen(hwnd, (x, y))
            x1, y1 = win32gui.ClientToScreen(hwnd, (x1 - x, y1 - y))
            im = pyautogui.screenshot(region=(x+800, y+250, 530, 580))
            return im
        else:
            print('Window not found!')
    else:
        im = pyautogui.screenshot()
        return im

# guardamos los datos del escenario (imagen y fichero json
def registerScenario ():
    global scenario
    print (json.dumps(scenario, indent = 1))

    jsonFilename = 'scenarios/' + name.get() + ".json"

    with open(jsonFilename, 'w') as f:
        json.dump(scenario, f)

    im = screenshot('Gestión de escenarios')
    imageFilename = 'scenarios/'+name.get()+".png"
    im.save(imageFilename)
    scenario = []
    clear()



# Funciones para seleccionar escenario
def selectBtnClick ():
    global scenarios, current, polys
    scenarios = []
    clear()
    for file in glob.glob("scenarios/*.png"):
        scene= Image.open(file)
        scene = scene.resize((300, 360))
        scenePic = ImageTk.PhotoImage(scene)
        scenarios.append({'name': file.split('.')[0], 'pic':scenePic})

    if len (scenarios) > 0:
        scenarioCanvas.create_image(0,0, image=scenarios[0]['pic'], anchor=tk.NW)
        current = 0

        createFrame.grid_forget()
        selectFrame.grid(row=1, column=0,  columnspan=2, padx=5, pady=5, sticky=tk.N +  tk.E + tk.W)

        selectBtn['text'] = 'Seleccionando...'
        selectBtn['fg'] = 'white'
        selectBtn['bg'] = 'green'

        createBtn['text'] = 'Crear'
        createBtn['fg'] = 'black'
        createBtn['bg'] = 'dark orange'

        prevBtn['state'] = tk.DISABLED
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
    scenarioCanvas.create_image(0, 0, image=scenarios[current]['pic'], anchor=tk.NW)
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
    scenarioCanvas.create_image(0, 0, image=scenarios[current]['pic'], anchor=tk.NW)

    if current == 0:
        prevBtn['state'] = tk.DISABLED
    else:
        prevBtn['state'] = tk.NORMAL
    if current == len(scenarios) - 1:
        nextBtn['state'] = tk.DISABLED
    else:
        nextBtn['state'] = tk.NORMAL

def clear ():
    global paths, fence, polys
    name.set ("")
    for path in paths:
        path.delete()
    for poly in polys:
        print ('borro poly')
        poly.delete()

    paths = []
    polys = []
    fence = {
        'type': 'polygon',
        'waypoints': []
    }

def deleteScenario ():
    global current
    msg_box = messagebox.askquestion(
        "Atención",
        "¿Seguro que quieres eliminar este escenario?",
        icon="warning",
    )
    if msg_box == "yes":
        print ('borro ', scenarios[current]['name'])
        os.remove(scenarios[current]['name'] + '.png')
        os.remove(scenarios[current]['name'] + '.json')
        scenarios.remove (scenarios[current])


        if current > 0:
            current = current -1
        else:
            current = current + 1
        if current in range (0, len(scenarios)):
            scenarioCanvas.create_image(0, 0, image=scenarios[current]['pic'], anchor=tk.NW)

        if current == 0:
            prevBtn['state'] = tk.DISABLED
        else:
            prevBtn['state'] = tk.NORMAL
        if current == len(scenarios) - 1:
            nextBtn['state'] = tk.DISABLED
        else:
            nextBtn['state'] = tk.NORMAL

def selectScenario ():
    global polys, selectedScenario

    for poly in polys:
        poly.delete()
    # cargamos el fichero json con el escenario seleccionado
    f = open(scenarios[current]['name'] + '.json')
    selectedScenario = json.load (f)
    print ('selected ', selectedScenario)

    # ahora dibujamos el escenario
    inclusion = selectedScenario [0]
    if inclusion['type'] == 'polygon':
        poly = []
        for point in inclusion['waypoints']:
            poly.append((point['lat'], point['lon']))
        polys.append(map_widget.set_polygon(poly,
                                                outline_color="blue",
                                                fill_color=None,
                                                border_width=3))
    for i in range (1,len (selectedScenario)):
        fence = selectedScenario[i]
        if fence['type'] == 'polygon':
            poly = []
            for point in fence['waypoints']:
                poly.append((point['lat'], point['lon']))
            polys.append(map_widget.set_polygon(poly,
                                                outline_color="red",
                                                fill_color="red",
                                                border_width=3))
    sendBtn['state'] = tk.NORMAL

def informar ():
    messagebox.showinfo("showinfo",
                        "Escenario enviado correctamente")

def sendScenario ():
    global connected, dron
    if not connected:
        dron = Dron ()
        connection_string = 'tcp:127.0.0.1:5763'
        baud = 115200
        dron.connect(connection_string, baud)
        connected = True
    dron.setScenario(selectedScenario, blocking=False, callback=informar)





def crear_ventana():

    global map_widget
    global createBtn,selectBtn, createFrame, name, selectFrame, scene, scenePic,scenarios, current
    global prevBtn, nextBtn, sendBtn
    global scenarioCanvas
    global i_wp, e_wp
    global paths, fence, polys
    global connected

    connected = False

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

    # botones para crear/cargar
    createBtn = tk.Button(controlFrame, text="Crear", bg="dark orange", command = createBtnClick)
    createBtn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)
    selectBtn = tk.Button(controlFrame, text="Seleccionar", bg="dark orange", command = selectBtnClick)
    selectBtn.grid(row=0, column=1,  padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

    # frame para crear escenario
    createFrame = tk.LabelFrame(controlFrame, text='Crear escenario')
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

    name = tk.StringVar()
    tk.Entry(createFrame, textvariable=name)\
        .grid(row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

    inclusionFenceBtn = tk.Button(createFrame, text="Define límites", bg="dark orange", command = lambda:  defineFence (1))
    inclusionFenceBtn.grid(row=2, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

    obstacleFenceBtn = tk.Button(createFrame, text="Define obstáculo", bg="dark orange", command = lambda: defineFence (2))
    obstacleFenceBtn.grid(row=3, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

    registerBtn = tk.Button(createFrame, text="Registra escenario", bg="dark orange", command = registerScenario)
    registerBtn.grid(row=4, column=0, padx=5, pady=5, sticky=tk.N +tk.E + tk.W)

    clearBtn = tk.Button(createFrame, text="Limpiar", bg="dark orange", command=clear)
    clearBtn.grid(row=5, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

    # frame para seleccionar escenarios
    selectFrame = tk.LabelFrame(controlFrame, text='Selecciona escenario')
    #selectFrame.grid(row=1, column=0,  columnspan=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    selectFrame.rowconfigure(0, weight=1)
    selectFrame.rowconfigure(1, weight=1)
    selectFrame.rowconfigure(2, weight=1)
    selectFrame.rowconfigure(3, weight=1)
    selectFrame.columnconfigure(0, weight=1)
    selectFrame.columnconfigure(1, weight=1)
    selectFrame.columnconfigure(2, weight=1)
    selectFrame.columnconfigure(3, weight=1)

    scenarioCanvas = tk.Canvas(selectFrame, width=300, height=360, bg='grey')
    #scenarioCanvas.grid(row = 0, column=0, columnspan=4, padx=5, pady=5,sticky=tk.N +tk.E + tk.W)
    scenarioCanvas.grid(row = 0, column=0, columnspan=4, padx=5, pady=5)



    prevBtn = tk.Button(selectFrame, text="<<", bg="dark orange", command = showPrev)
    prevBtn.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N +  tk.E + tk.W)
    selectScenarioBtn = tk.Button(selectFrame, text="Seleccionar", bg="dark orange", command = selectScenario)
    selectScenarioBtn.grid(row=1, column=1, columnspan = 2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
    nextBtn = tk.Button(selectFrame, text=">>", bg="dark orange", command = showNext)
    nextBtn.grid(row=1, column=3, padx=5, pady=5, sticky=tk.N +  tk.E + tk.W)

    sendBtn = tk.Button(selectFrame, text="Enviar escenario", bg="dark orange", command=sendScenario)
    sendBtn.grid(row=2, column=0,columnspan = 4, padx=5, pady=5, sticky=tk.N + tk.E + tk.W)

    deleteBtn = tk.Button(selectFrame, text="Eliminar escenario", bg="red", fg = 'white', command = deleteScenario)
    deleteBtn.grid(row=3, column=0, columnspan = 4, padx=5, pady=5, sticky=tk.N +  tk.E + tk.W)

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
    map_widget.set_position(41.3808982, 2.1228229)  # Coordenadas del Nou Camp
    map_widget.set_zoom(19)

    map_widget.add_right_click_menu_command(label="Cierra el camino", command=closeFence, pass_coords=False)
    map_widget.add_left_click_map_command(getFenceWaypoint)



    # ahora cargamos las imagenes de los iconos que vamos a usar

    # icono para wp de inclusion
    im = Image.open("images/i_wp.png")
    im_resized = im.resize((20, 20), Image.LANCZOS)
    i_wp = ImageTk.PhotoImage(im_resized)

    # icono para wp de exclusión
    im = Image.open("images/e_wp.png")
    im_resized = im.resize((20, 20), Image.LANCZOS)
    e_wp = ImageTk.PhotoImage(im_resized)


    return ventana


if __name__ == "__main__":
    ventana = crear_ventana()
    ventana.mainloop()
