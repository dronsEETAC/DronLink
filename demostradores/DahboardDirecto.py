import tkinter as tk
from dronLink.Dron import Dron



def showTelemetryInfo (telemetry_info):
    global heading, altitude, groundSpeed, state
    global altShowLbl, headingShowLbl, speedShowLbl
    altShowLbl['text'] = round (telemetry_info['alt'],2)
    headingShowLbl['text'] =  round(telemetry_info['heading'],2)
    speedShowLbl['text'] = round (telemetry_info['groundSpeed'],2)


def connect ():
    global dron, speedSldr
    connection_string ='tcp:127.0.0.1:5763'
    baud = 115200
    dron.connect(connection_string,baud)
    # cambiamos el color del boton
    connectBtn['text'] = 'Conectado'
    connectBtn['fg'] = 'white'
    connectBtn['bg'] = 'green'
    # fijamos la velocidad por defecto en el slider
    speedSldr.set(1)

def arm ():
    global dron
    dron.arm()
    armBtn['text'] = 'Armado'
    armBtn['fg'] = 'white'
    armBtn['bg'] = 'green'

def inTheAir ():
    # ya ha alcanzado la altura de despegue
    takeOffBtn['text'] = 'En el aire'
    takeOffBtn['fg'] = 'white'
    takeOffBtn['bg'] = 'green'


def takeoff ():
    global dron
    # despegamos a una altura de 5 metros
    # llamada no bloqueante. Cuando alcance la altura indicada ejecutará la función inTheAir
    dron.takeOff (5, blocking = False,  callback = inTheAir)
    takeOffBtn['text'] = 'Despegando...'
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
    global dron
    # llamada no bloqueante. El parámetro nos permitirá saber en onEarth que venimos de Land
    dron.Land(blocking = False,  callback = onEarth, params = 'land')
    landBtn['text'] = 'Aterrizando...'
    landBtn['fg'] = 'black'
    landBtn['bg'] = 'yellow'

def RTL():
    global dron
    # llamada no bloqueante. El parámetro nos permitirá saber en onEarth que venimos de RTL
    dron.RTL(blocking = False,  callback = onEarth, params = 'RTL')
    RTLBtn['text'] = 'Retornando...'
    RTLBtn['fg'] = 'black'
    RTLBtn['bg'] = 'yellow'

def go (direction, btn):
    global dron, previousBtn
    # cambio el color del anterior boton clicado (si lo hay)
    if previousBtn:
        previousBtn['fg'] = 'black'
        previousBtn['bg'] = 'dark orange'

    # navegamos en la dirección indicada
    dron.go (direction)
    # pongo en verde el boton clicado
    btn['fg'] = 'white'
    btn['bg'] = 'green'
    # tomo nota de que este es el último botón clicado
    previousBtn = btn


def startTelem():
    global dron
    # pedimos datos de telemetría que se procesarán en showTelemetryInfo a medida que vayan llegando
    dron.send_telemetry_info(showTelemetryInfo)

def stopTelem():
    global dron
    dron.stop_sending_telemetry_info()

def fixHeading ():
    global dron
    # asi fijamos el heading, que no cambiará sea la que sea la dirección de navegación
    dron.fixHeading()

def unfixHeading ():
    global dron
    # ahora el heading cambiará según sea la dirección de navegación
    dron.unfixHeading()

def changeHeading (heading):
    global dron
    global gradesSldr
    # cambiamos el heading según se haya seleccionado en el slider
    dron.changeHeading(int (heading))

def changeNavSpeed (speed):
    global dron
    global speedSldr
    # cambiamos la velocidad de navagación según se haya seleccionado en el slider
    dron.changeNavSpeed(float (speed))



def crear_ventana():
    global dron
    global  altShowLbl, headingShowLbl,  speedSldr, gradesSldr, speedShowLbl
    global connectBtn, armBtn, takeOffBtn, landBtn, RTLBtn
    global previousBtn # aqui guardaré el ultimo boton de navegación clicado

    dron = Dron()

    previousBtn = None

    ventana = tk.Tk()
    ventana.title("Dashboard con conexión directa")
    # la interfaz tiene 10 filas y dos columnas
    ventana.rowconfigure(0, weight=1)
    ventana.rowconfigure(1, weight=1)
    ventana.rowconfigure(2, weight=1)
    ventana.rowconfigure(3, weight=1)
    ventana.rowconfigure(4, weight=1)
    ventana.rowconfigure(5, weight=1)
    ventana.rowconfigure(6, weight=1)
    ventana.rowconfigure(7, weight=1)
    ventana.rowconfigure(8, weight=1)
    ventana.rowconfigure(9, weight=1)
    ventana.columnconfigure(0, weight=1)
    ventana.columnconfigure(1, weight=1)

    # Disponemos los botones, indicando qué función ejecutar cuando se clica cada uno de ellos
    # Los tres primeros ocupan las dos columnas de la fila en la que se colocan
    connectBtn = tk.Button(ventana, text="Conectar", bg="dark orange", command = connect)
    connectBtn.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    armBtn = tk.Button(ventana, text="Armar", bg="dark orange", command=arm)
    armBtn.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    takeOffBtn = tk.Button(ventana, text="Despegar", bg="dark orange", command=takeoff)
    takeOffBtn.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # Los dos botones siguientes están en la misma fila
    fixBtn = tk.Button(ventana, text="fijar heading", bg="dark orange", command=fixHeading)
    fixBtn.grid(row=3, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    unfixBtn = tk.Button(ventana, text="desfijar heading", bg="dark orange", command=unfixHeading)
    unfixBtn.grid(row=3, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # Slider para seleccionar el heading
    gradesSldr = tk.Scale(ventana, label="Grados:", resolution=5, from_=0, to=360, tickinterval=45,
                              orient=tk.HORIZONTAL, command = changeHeading)
    gradesSldr.grid(row=4, column=0, columnspan=2,padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # los dos siguientes también están en la misma fila
    landBtn = tk.Button(ventana, text="aterrizar", bg="dark orange", command=land)
    landBtn.grid(row=5, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    RTLBtn = tk.Button(ventana, text="RTL", bg="dark orange", command=RTL)
    RTLBtn.grid(row=5, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # este es el frame para la navegación. Pequeña matriz de 3 x 3 botones
    navFrame = tk.LabelFrame (ventana, text = "Navegación")
    navFrame.grid(row=6, column=0, columnspan = 2, padx=50, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

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


    # slider para elegir la velocidad de navegación
    speedSldr = tk.Scale(ventana, label="Velocidad (m/s):", resolution=1, from_=0, to=20, tickinterval=5,
                          orient=tk.HORIZONTAL, command = changeNavSpeed)
    speedSldr.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # botones para pedir/parar datos de telemetría
    StartTelemBtn = tk.Button(ventana, text="Empezar a enviar telemetría", bg="dark orange", command=startTelem)
    StartTelemBtn.grid(row=8, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    StopTelemBtn = tk.Button(ventana, text="Parar de enviar telemetría", bg="dark orange", command=stopTelem)
    StopTelemBtn.grid(row=8, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

    # Este es el frame para mostrar los datos de telemetría
    # Contiene etiquetas para informar de qué datos son y los valores. Solo nos interesan 3 datos de telemetría
    telemetryFrame = tk.LabelFrame(ventana, text="Telemetría")
    telemetryFrame.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky=tk.N + tk.S + tk.E + tk.W)

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

    return ventana


if __name__ == "__main__":
    ventana = crear_ventana()
    ventana.mainloop()
