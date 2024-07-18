import tkinter as tk

import tkintermapview

from dronLink.Dron import Dron
from tkinter import messagebox
from PIL import Image, ImageTk



################# gestion de parametros ******
class ParameterManager:
    def __init__(self, window, swarm, pos):
        self.window = window
        self.swarm = swarm
        self.pos = pos
        self.managementFrame = tk.LabelFrame (window, text = 'Dron '+str(pos+1))
        self.managementFrame.rowconfigure(0, weight=1)
        self.managementFrame.rowconfigure(1, weight=1)
        self.managementFrame.rowconfigure(2, weight=1)
        self.managementFrame.rowconfigure(3, weight=1)
        self.managementFrame.rowconfigure(4, weight=1)
        #if pos == 0:
        self.managementFrame.rowconfigure(5, weight=1)

        self.managementFrame.columnconfigure(0, weight=1)
        self.managementFrame.columnconfigure(1, weight=1)


        tk.Label (self.managementFrame, text = 'RTL_ALT')\
            .grid(row=0, column=0, padx=2, pady=2, sticky=tk.N  + tk.E + tk.W)

        self.RTL_ALT_Entry = tk.Entry (self.managementFrame)
        self.RTL_ALT_Entry.grid(row=0, column=1, padx=2, pady=2, sticky=tk.N  + tk.E + tk.W)

        tk.Label(self.managementFrame, text='FENCE_ENABLE') \
            .grid(row=1, column=0, padx=2, pady=2, sticky=tk.N  + tk.E + tk.W)
        self.FENCE_ENABLE_Entry = tk.Entry(self.managementFrame)
        self.FENCE_ENABLE_Entry.grid(row=1, column=1, padx=2, pady=2, sticky=tk.N + tk.E + tk.W)

        tk.Label(self.managementFrame, text='FENCE_ACTION') \
            .grid(row=2, column=0, padx=2, pady=2, sticky=tk.N + tk.E + tk.W)
        self.FENCE_ACTION_Entry = tk.Entry(self.managementFrame)
        self.FENCE_ACTION_Entry.grid(row=2, column=1, padx=2, pady=2, sticky=tk.N + tk.E + tk.W)

        tk.Label (self.managementFrame, text = 'PILOT_SPEED_UP')\
            .grid(row=3, column=0, padx=2, pady=2, sticky=tk.N  + tk.E + tk.W)
        self.PILOT_SPEED_UP_Entry = tk.Entry(self.managementFrame)
        self.PILOT_SPEED_UP_Entry.grid(row=3, column=1, padx=2, pady=2, sticky=tk.N  + tk.E + tk.W)

        tk.Button (self.managementFrame, text = 'Leer valores',  bg = "dark orange", command = self.read_params)\
            .grid(row=4, column=0, padx=2, pady=2, sticky=tk.N + tk.E + tk.W)
        tk.Button (self.managementFrame, text = 'Enviar valores' , bg = "dark orange", command = self.write_params)\
            .grid(row=4, column=1, padx=2, pady=2, sticky=tk.N + tk.E + tk.W)
        if pos == 0:
            tk.Button (self.managementFrame, text = 'Copiar valores en todos los drones',  bg = "dark orange", command = self.copy_params)\
                .grid(row=5, column=0, columnspan=2, padx=2, pady=2, sticky=tk.N  + tk.E + tk.W)
        else:
            b= tk.Button(self.managementFrame, state=tk.DISABLED, bd = 0)
            b.grid(row=5, column=0, columnspan=2, padx=2, pady=2, sticky=tk.N + tk.E + tk.W)




    def buildFrame (self):
        return self.managementFrame

    def setManagers (self, managers):
        self.managers = managers
    def read_params (self):
        parameters = [
            "RTL_ALT",
            "PILOT_SPEED_UP",
            "FENCE_ACTION",
            "FENCE_ENABLE"
        ]
        result = self.swarm[self.pos].getParams(parameters)
        self.RTL_ALT_Entry.delete (0, tk.END)
        self.RTL_ALT_Entry.insert (0,str(result[0]['RTL_ALT']))

        self.PILOT_SPEED_UP_Entry.delete(0, tk.END)
        self.PILOT_SPEED_UP_Entry.insert(0,str(result[1]['PILOT_SPEED_UP']))

        self.FENCE_ACTION_Entry.delete(0, tk.END)
        self.FENCE_ACTION_Entry.insert(0,str(result[2]['FENCE_ACTION']))

        self.FENCE_ENABLE_Entry.delete(0, tk.END)
        self.FENCE_ENABLE_Entry.insert(0,str(result[3]['FENCE_ENABLE']))

        pass
    def write_params (self):
        parameters = [
            {'ID': "FENCE_ENABLE", 'Value': float(self.FENCE_ENABLE_Entry.get())},
            {'ID': "FENCE_ACTION", 'Value': float(self.FENCE_ACTION_Entry.get())},
            {'ID': "PILOT_SPEED_UP", 'Value': float(self.PILOT_SPEED_UP_Entry.get())},
            {'ID': "RTL_ALT", 'Value': float(self.RTL_ALT_Entry.get())}
        ]
        self.swarm[self.pos].setParams(parameters)


    def copy_params (self):

        for i in range (1,len(self.swarm)):
            dronManager = self.managers[i]

            dronManager.RTL_ALT_Entry.delete(0, tk.END)
            dronManager.RTL_ALT_Entry.insert(0,self.RTL_ALT_Entry.get())

            dronManager.PILOT_SPEED_UP_Entry.delete(0, tk.END)
            dronManager.PILOT_SPEED_UP_Entry.insert(0, self.PILOT_SPEED_UP_Entry.get())

            dronManager.FENCE_ACTION_Entry.delete(0, tk.END)
            dronManager.FENCE_ACTION_Entry.insert(0, self.FENCE_ACTION_Entry.get())

            dronManager.FENCE_ENABLE_Entry.delete(0, tk.END)
            dronManager.FENCE_ENABLE_Entry.insert(0, self.FENCE_ENABLE_Entry.get())





# cuando llega un paquete de telemetría se activa esta función en la que se identifica el dron de donde proceden
# recordemos que los drones están identificados del 0 en adelante
def processTelemetryInfo (id, telemetry_info):
    global dronIcons
    # recupero la posición en la que está el dron
    lat = telemetry_info['lat']
    lon = telemetry_info['lon']

    # si es el primer paquete de este dron entonces ponemos en el mapa el icono de ese dron
    if not dronIcons[id]:
        dronIcons[id] = map_widget.set_marker(lat, lon,
                        icon=dronPictures[id],icon_anchor="center")
    # si no es el primer paquete entonces muevo el icono a la nueva posición
    else:
        dronIcons[id].set_position(lat,lon)

    # si el dron es el seleccionado para mostrar sus datos de telemetría pues los muestro en las etiquetas correspondientes
    if id  == telemetryOption.get() - 1:
        altShowLbl['text'] = round (telemetry_info['alt'],2)
        headingShowLbl['text'] =  round(telemetry_info['heading'],2)
        speedShowLbl['text'] = round (telemetry_info['groundSpeed'],2)



def connect ():
    # me conecto al simulador de cada uno de los drones del enjambre que estan seleccionados
    # los puertos son: 5763, 5773, 5783 y asi en adelante, sumando 10
    base = 5763
    for i in range(0, len(swarm)):
        if selected[i]:
            port = base+i*10
            connection_string ='tcp:127.0.0.1:'+str(port)
            baud = 115200
            # me conecto pidiendo 10 paquetes de telemetría por segundos
            # esto podría ser mucho si hay muchos drones, y saturar el computador
            # si el computador aguanta el movimiento de los drones en la pantalla será más fluido.
            # no obstante, con una frecuencia de 4 también es suficientemente fluido
            swarm[i].connect(connection_string,baud, freq=10)
            # pongo el estado de cada dron en verde
            canvasList[i].itemconfig(statusList[i], fill='green')
            # pido que empiece a enviar los daatos de telemetría
            swarm[i].send_telemetry_info(processTelemetryInfo)

    ###################### telemetry management
    parameterManagementWindow = tk.Tk()
    parameterManagementWindow.title("Gestión de parámetros")
    parameterManagementWindow.rowconfigure(0, weight=1)
    parameterManagementWindow.rowconfigure(1, weight=1)
    managers = []
    for i in range(0, len(swarm)):
        parameterManagementWindow.columnconfigure(i, weight=1)
        dronManager = ParameterManager (parameterManagementWindow, swarm, i)
        managers.append(dronManager)
        dronFrame = dronManager.buildFrame()
        dronFrame.grid(row=0, column=i, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)
    managers[0].setManagers(managers)
    tk.Button(parameterManagementWindow, text='Cerrar', bg="dark orange", command=lambda : parameterManagementWindow.destroy()) \
        .grid(row=1, column=0, columnspan = len(swarm), padx=2, pady=2, sticky=tk.N  + tk.E + tk.W)

    parameterManagementWindow.mainloop()



def close ():
    # desconecto todos los drones del enjambre y cierro
    error = False
    for i in range(0, len(swarm)):
            if not swarm[i].disconnect():
                error = True
                break
    if error:
        messagebox.showerror("Error",  'Algunos drones están en el aire')
    else:
        ventana.destroy()

# esta función se activará cuando el dron que se identifica haya completado el takeOff
def inTheAir (id):
    # simplemente señalo en nuevo estado
    canvasList[id].itemconfig(statusList[id], fill='blue')

# esta función se activará cuando el dron que se identifica haya completado el aterrizaje o el retorno
def onEarth (id):
    # simplemente señalo en nuevo estado
    canvasList[id].itemconfig(statusList[id], fill='green')

# esta función se activará cuando el dron que se identifica haya armado
def armed (id):
    # inicio inmediatamente el despegue (a 5 metros) indicando la función que debe activar cuando lo complete
    swarm[id].takeOff(5, blocking=False, callback= inTheAir)

# cuando clico el boton de armar y despagar vengo aquí
def arm_takeOff ():
    for i in range(0, len(swarm)):
        if selected[i]:
            # para cada dron seleccionado marco el estado (despegando) y le indico que arme (y la función que debe
            # ejecutar una vez armado)
            canvasList[i].itemconfig(statusList[i], fill='orange')
            swarm[i].arm(blocking=False, callback= armed)

# cuando clico el boton de aterrizar vengo aquí
def land ():
    for i in range(0, len(swarm)):
        if selected[i]:
            # para cada dron seleccionado marco el estado  y le indico que arme (y la función que debe
            # ejecutar una vez en tierra)
            canvasList[i].itemconfig(statusList[i], fill='red')
            swarm[i].Land(blocking = False, callback= onEarth)

# cuando clico el boton de retornar vengo aquí
def RTL():
    for i in range(0, len(swarm)):
        if selected[i]:
            # para cada dron seleccionado marco el estado  y le indico que arme (y la función que debe
            # ejecutar una vez en tierra)
            canvasList[i].itemconfig(statusList[i], fill='pink')
            swarm[i].RTL(blocking=False, callback= onEarth)

# cuando clico el boton derecho del raton vengo aquí
# la función recibe las coordenadas del punto marcado
def goto( coords):
    for i in range(0, len(swarm)):
        if selected[i]:
            # envio a cada dron seleccionado al punto indicado (manteniendo la altura de 5 metros)
            swarm[i].goto(coords[0], coords[1], 5, blocking = False)

# cuando clico uno de los botones del frame de navegación vengo aquí.
# recibo la dirección elegida
def go (direction):
    for i in range(0, len(swarm)):
        if selected[i]:
            swarm[i].go (direction)

# aqui vengo cuando clico en uno de los botones que representan los drones del enjambre, en el frame de selección
def selectDron (dron):
    global swarm, selected, dronIcons

    if swarm == None:
        # aún no he definido el tamaño del enjambre. En este caso, el parámetro dron indica el número de drone
        # que va a tener el enjambre
        swarm = []
        for i in range(0, dron):
            # para cada dron del enjambre cambio el color de su boton
            buttonList[i]['bg'] = 'orange'
            # modifico el estado
            canvasList[i].itemconfig(statusList[i], fill='yellow')
            # creo un dron que identifico a partir del 0 en adelante y lo meto en el enjambre
            swarm.append (Dron (i))

        # creo la lista donde indicaré los drones que tengo seleccionados en cada momento (inicialmente ninguno)
        selected = [False]*dron

        # pongo en gris el resto de los botones y deshabiloto los radiobutons correspondientes
        for i in range (dron, len(buttonList)):
            buttonList[i]['bg'] = 'gray'
            radioButtonsList[i].configure(state = tk.DISABLED)

        # creo la lista en la que colocaré los iconos de los drones (de momento no hay ninguno colocado en el mapa)
        dronIcons = [None] * dron

    else:
        # ya se creó el enjambre. En este caso el parámetro es el número de dron seleccionado (del 1 en adelante)
        if selected[dron-1]:
            # en realidad estoy deseleccionando el dron
            selected[dron-1] = False
            buttonList[dron-1]['bg'] = 'orange'
            buttonList[dron-1]['fg'] = 'black'
        else:
            # marco el dron como seleccionado
            selected[dron-1] = True
            buttonList[dron-1]['bg'] = 'green'
            buttonList[dron-1]['fg'] = 'white'


def selectAll():
    global selected
    # quiero seleccionar todos los drones del enjambre
    selected = [True]*len(swarm)
    for i in range(0, len(swarm)):
        buttonList[i]['bg'] = 'green'
        buttonList[i]['fg'] = 'white'

def UnselectAll():
    global selected
    # quiero deseleccionar todos los drones del enjambre
    selected = [False] * len(swarm)
    for i in range(0, len(swarm)):
        buttonList[i]['bg'] = 'orange'
        buttonList[i]['fg'] = 'black'


def crear_ventana():
    global dron
    global  altShowLbl, headingShowLbl, speedShowLbl
    global buttonList, statusList, radioButtonsList, telemetryOption, canvasList
    global swarm
    global map_widget
    global dronIcons, dronPictures
    global window


    swarm = None

    ventana = tk.Tk()
    ventana.title("Control de enjambre")
    # El panel principal tiene una fila y dos columnas
    ventana.rowconfigure(0, weight=1)
    ventana.columnconfigure(0, weight=1)
    ventana.columnconfigure(1, weight=1)

    controlFrame = tk.LabelFrame (ventana, text='Control')
    controlFrame.grid(row=0, column=0,  padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
    #El frame de control aparece en la primera columna

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

    # Primero hay un frame informativo, que indica el significado de los colores de estado
    statusInfoFrame = tk.LabelFrame(controlFrame, text="Estados")
    statusInfoFrame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # hay seis estados, que se muestran en dos filas y tres columnas
    statusInfoFrame.rowconfigure(0, weight=1)
    statusInfoFrame.rowconfigure(1, weight=1)

    statusInfoFrame.columnconfigure(0, weight=1)
    statusInfoFrame.columnconfigure(1, weight=1)
    statusInfoFrame.columnconfigure(2, weight=1)

    # para cada estado creamos un pequeño canvas con un circulo de color y el texto informativo
    canvas = tk.Canvas(statusInfoFrame, width=10, height=30)
    canvas.grid(row=0, column=0, padx=3, pady=0, sticky=tk.N + tk.S + tk.E + tk.W)
    canvas.create_oval(5, 5, 20, 20, fill='gray', outline="")
    canvas.create_text(60,15, text = 'Desconectado')

    canvas = tk.Canvas(statusInfoFrame, width=10, height=30)
    canvas.grid(row=0, column=1, padx=3, pady=0, sticky=tk.N + tk.S + tk.E + tk.W)
    canvas.create_oval(5, 5, 20, 20, fill='green', outline="")
    canvas.create_text(60,15, text='Conectado')

    canvas = tk.Canvas(statusInfoFrame, width=10, height=30)
    canvas.grid(row=0, column=2, padx=3, pady=0, sticky=tk.N + tk.S + tk.E + tk.W)
    canvas.create_oval(5, 5, 20, 20, fill='orange', outline="")
    canvas.create_text(60,15, text='Despagando')

    canvas = tk.Canvas(statusInfoFrame, width=10, height=30)
    canvas.grid(row=1, column=0, padx=3, pady=0, sticky=tk.N + tk.S + tk.E + tk.W)
    canvas.create_oval(5, 5, 20, 20, fill='blue', outline="")
    canvas.create_text(60,15, text='En el aire')

    canvas = tk.Canvas(statusInfoFrame, width=10, height=30)
    canvas.grid(row=1, column=1, padx=3, pady=0, sticky=tk.N + tk.S + tk.E + tk.W)
    canvas.create_oval(5, 5, 20, 20, fill='red', outline="")
    canvas.create_text(60,15, text='Aterrizando')

    canvas = tk.Canvas(statusInfoFrame, width=10, height=30)
    canvas.grid(row=1, column=2, padx=3, pady=0, sticky=tk.N + tk.S + tk.E + tk.W)
    canvas.create_oval(5, 5, 20, 20, fill='pink', outline="")
    canvas.create_text(60,15, text='Retornando')

    # Este es el frame en el seleccionamos el tamaño del enjambre y mostramos el estado de cada dron

    swarmFrame = tk.LabelFrame (controlFrame,text= "Enjambre")
    swarmFrame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # El frame tiene 9 columnas porque podemos trabajar hasta con 9 drones
    # Y tenemos tres filas: una para los botones de selección de dron, otra para mostrar el estado de cada dron
    # y otra para seleccionar/deseleccionar todos los drones del enjambre
    swarmFrame.rowconfigure(0, weight=1)
    swarmFrame.rowconfigure(1, weight=1)
    swarmFrame.rowconfigure(2, weight=1)

    swarmFrame.columnconfigure(0, weight=1)
    swarmFrame.columnconfigure(1, weight=1)
    swarmFrame.columnconfigure(2, weight=1)
    swarmFrame.columnconfigure(3, weight=1)
    swarmFrame.columnconfigure(4, weight=1)
    swarmFrame.columnconfigure(5, weight=1)
    swarmFrame.columnconfigure(6, weight=1)
    swarmFrame.columnconfigure(7, weight=1)
    swarmFrame.columnconfigure(8, weight=1)

    # creamos primero los 9 botones para seleccionar drones del emjambre
    # necesitaremos estas listas
    buttonList = []
    statusList = []
    canvasList = []
    for i in range (1,10):
        # para cada dron creamos un boton, que al ser clicado activa la función selectDron pasandole el número de dron
        # (los drones están numerados del 1 al 9)
        buttonList.append (tk.Button(swarmFrame, text= str(i), bg="yellow", width=3, command= lambda dron = i: selectDron(dron)))
        buttonList[-1].grid(row=0, column=i-1, padx=3, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
        # ahora creamos el canvas con el circulo en el que mostraremos el estado del dron
        canvas = tk.Canvas (swarmFrame, width=10, height=30)
        statusList.append(canvas.create_oval(5, 5, 20, 20, fill='gray', outline =""))
        canvas.grid(row=1, column=i - 1, padx=3, pady=0, sticky=tk.N + tk.S + tk.E + tk.W)
        canvasList.append(canvas)
        # tanto los botones como los canvas y los circulos los ponemos en listas para poder acceder a ellos en otros puntos del programa

    # ahora vienen los botones para seleccionar/deseleccionar todos los drones
    allBtn = tk.Button(swarmFrame, text="Selecciona todos", bg="dark orange", command = selectAll)
    allBtn.grid(row=2, column=0, columnspan = 5, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
    noneBtn = tk.Button(swarmFrame, text="Deselecciona todos", bg="dark orange", command = UnselectAll)
    noneBtn.grid(row=2, column=5, columnspan = 4, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)


    # Ahora definimos los diferentes botones que actuan sobre los drones seleccionados del enjambre
    connectBtn = tk.Button(controlFrame, text="Conectar", bg="dark orange", command = connect)
    connectBtn.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    armTakeOffBtn = tk.Button(controlFrame, text="Armar y despegar", bg="dark orange", command=arm_takeOff)
    armTakeOffBtn.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    landBtn = tk.Button(controlFrame, text="aterrizar", bg="dark orange", command=land)
    landBtn.grid(row=4, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    RTLBtn = tk.Button(controlFrame, text="RTL", bg="dark orange", command=RTL)
    RTLBtn.grid(row=4, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # este es el frame de navegación
    navFrame = tk.LabelFrame (controlFrame, text = "Navegación")
    navFrame.grid(row=5, column=0, columnspan = 2, padx=50, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)
    # es una pequeña matriz de 9 botones
    navFrame.rowconfigure(0, weight=1)
    navFrame.rowconfigure(1, weight=1)
    navFrame.rowconfigure(2, weight=1)

    navFrame.columnconfigure(0, weight=1)
    navFrame.columnconfigure(1, weight=1)
    navFrame.columnconfigure(2, weight=1)

    # al clicar cualquiera de los botones se activa la función go pasandole la dirección seleccionada
    NWBtn = tk.Button(navFrame, text="NW", bg="dark orange",
                        command= lambda: go("NorthWest"))
    NWBtn.grid(row=0, column=0, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    NoBtn = tk.Button(navFrame, text="No", bg="dark orange",
                        command= lambda: go("North"))
    NoBtn.grid(row=0, column=1, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    NEBtn = tk.Button(navFrame, text="NE", bg="dark orange",
                        command= lambda: go("NorthEast"))
    NEBtn.grid(row=0, column=2, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    WeBtn = tk.Button(navFrame, text="We", bg="dark orange",
                        command=lambda: go("West"))
    WeBtn.grid(row=1, column=0, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    StopBtn = tk.Button(navFrame, text="St", bg="dark orange",
                        command=lambda: go("Stop"))
    StopBtn.grid(row=1, column=1, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    EaBtn = tk.Button(navFrame, text="Ea", bg="dark orange",
                        command=lambda: go("East"))
    EaBtn.grid(row=1, column=2, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    SWBtn = tk.Button(navFrame, text="SW", bg="dark orange",
                        command=lambda: go("SouthWest"))
    SWBtn.grid(row=2, column=0, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    SoBtn = tk.Button(navFrame, text="So", bg="dark orange",
                        command=lambda: go("South"))
    SoBtn.grid(row=2, column=1, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    SEBtn = tk.Button(navFrame, text="SE", bg="dark orange",
                        command=lambda: go("SouthEast"))
    SEBtn.grid(row=2, column=2, padx=2, pady=2, sticky=tk.N + tk.S + tk.E + tk.W)

    # Este es el frame para mostrar los datos de telemetria
    telemetryFrame = tk.LabelFrame(controlFrame, text="Telemetría")
    telemetryFrame.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)

    telemetryFrame.rowconfigure(0, weight=1)
    telemetryFrame.rowconfigure(1, weight=1)
    telemetryFrame.rowconfigure(2, weight=1)

    telemetryFrame.columnconfigure(0, weight=1)
    telemetryFrame.columnconfigure(1, weight=1)
    telemetryFrame.columnconfigure(2, weight=1)

    # Primero tenemos un frame con 9 radio buttons para seleccionar el dron cuyos datos de telemetría queremos mostrar
    selectTelemetryFrame = tk.Frame (telemetryFrame)
    selectTelemetryFrame.grid(row=0, column=0,  columnspan= 3, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    telemetryOption = tk.IntVar()
    radioButtonsList = []
    for i in range(1, 10):
        radioButtonsList.append(tk.Radiobutton(selectTelemetryFrame, text=str(i), variable=telemetryOption, value = i))
        radioButtonsList[-1].pack(side = tk.LEFT)
    telemetryOption.set(0)

    # Ahora ponemos labels con titulos y espacios para los tres datos de telemetría que queremos mostrar
    altLbl = tk.Label(telemetryFrame, text='Altitud')
    altLbl.grid(row=1, column=0,  padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    headingLbl = tk.Label(telemetryFrame, text='Heading')
    headingLbl.grid(row=1, column=1,  padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    speedLbl = tk.Label(telemetryFrame, text='Speed')

    speedLbl.grid(row=1, column=2,  padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    altShowLbl = tk.Label(telemetryFrame, text='')
    altShowLbl.grid(row=2, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    headingShowLbl = tk.Label(telemetryFrame, text='',)
    headingShowLbl.grid(row=2, column=1,  padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    speedShowLbl = tk.Label(telemetryFrame, text='', )
    speedShowLbl.grid(row=2, column=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # boton para cerrar la ventana
    closeBtn = tk.Button(controlFrame, text="Cerrar", bg="dark orange", command=close)
    closeBtn.grid(row=7, column=0, columnspan=2, padx= 5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)


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

    # indicamos que queremos capturar el click sobre el boton derecho del mouse (para marcar el punto del mapa
    # al que queremos enviar a los drones seleccionados
    map_widget.add_right_click_menu_command(label="Ve aquí", command=goto, pass_coords=True)

    # ahora vamos a crear una lista con los iconos para los 9 drones
    dronPictures = []
    pic1 = Image.open("images/dron1.png")
    pic1_resized = pic1.resize((20, 20), Image.LANCZOS)
    dronPictures.append(ImageTk.PhotoImage(pic1_resized))

    pic1 = Image.open("images/dron2.png")
    pic1_resized = pic1.resize((20, 20), Image.LANCZOS)
    dronPictures.append(ImageTk.PhotoImage(pic1_resized))

    pic1 = Image.open("images/dron3.png")
    pic1_resized = pic1.resize((20, 20), Image.LANCZOS)
    dronPictures.append(ImageTk.PhotoImage(pic1_resized))

    pic1 = Image.open("images/dron4.png")
    pic1_resized = pic1.resize((20, 20), Image.LANCZOS)
    dronPictures.append(ImageTk.PhotoImage(pic1_resized))

    pic1 = Image.open("images/dron5.png")
    pic1_resized = pic1.resize((20, 20), Image.LANCZOS)
    dronPictures.append(ImageTk.PhotoImage(pic1_resized))

    pic1 = Image.open("images/dron6.png")
    pic1_resized = pic1.resize((20, 20), Image.LANCZOS)
    dronPictures.append(ImageTk.PhotoImage(pic1_resized))

    pic1 = Image.open("images/dron7.png")
    pic1_resized = pic1.resize((20, 20), Image.LANCZOS)
    dronPictures.append(ImageTk.PhotoImage(pic1_resized))

    pic1 = Image.open("images/dron8.png")
    pic1_resized = pic1.resize((20, 20), Image.LANCZOS)
    dronPictures.append(ImageTk.PhotoImage(pic1_resized))

    pic1 = Image.open("images/dron9.png")
    pic1_resized = pic1.resize((20, 20), Image.LANCZOS)
    dronPictures.append(ImageTk.PhotoImage(pic1_resized))

    return ventana


if __name__ == "__main__":
    ventana = crear_ventana()
    ventana.mainloop()
