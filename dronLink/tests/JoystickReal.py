import threading
import pygame
import time
import pywinusb.hid as hid

class Joystick:
    def __init__(self, dron, idCallback,  num = 0):
        ''' El usuario puede tener varios joystics conectados al portátil. El num es un valor mayor
        o igual a 0 que indica cuál de los joystics conectados va a controlar al dron que se recibe.
        Los joystics pueden ser conectados por cable o inalambricos. Es importante identificar qué tipo
        de joystick es porque el tratamiento es bastante distinto.
        '''

        self.dron = dron
        # este será el identificador de joystic
        self.id = num
        # guardo la funcion que hay que ejecutar cuando pulse el boton 4 (identificación)
        self.idCallBack = idCallback

        threading.Thread(target=self.control_loop).start()

    def codificador(self, joystick ):
        # Leer valores de los ejes
        axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        # Leer estado de botones
        buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]
        # Leer hats (crucetas digitales)
        hats = [joystick.get_hat(i) for i in range(joystick.get_numhats())]
        return axes, buttons, hats

    def inalambrico(self,data):
        # nuevo paquete de datos del joystick inalambrico
        # asegurarnos que el paquete tiene al menos 7 bytes
        if len(data) < 7:
            return

        # Sticks
        lx = data[3]
        ly = data[4]
        rx = data[2]
        ry = data[1]

        # Normalizar a -1..1
        def normalize(val):
            return (val - 128) / 128.0  # suponiendo rango 0–255

        axes = [normalize(lx), normalize(ly), normalize(rx), normalize(ry)]

        # Prepalo la lista de botones en el mismo formato que para el caso de los joystick por cable

        buttons = [0] * 12
        if data[5] == 31:
            buttons[0] = 1
        if data[5] == 47:
            buttons[1] = 1
        if data[5] == 79:
            buttons[2] = 1
        if data[5] == 143:
            buttons[3] = 1
        if data[6] == 1:
            buttons[4] = 1
        if data[6] == 2:
            buttons[5] = 1
        if data[6] == 4:
            buttons[6] = 1
        if data[6] == 8:
            buttons[7] = 1
        if data[6] == 16:
            buttons[8] = 1
        if data[6] == 32:
            buttons[9] = 1
        if data[6] == 64:
            buttons[10] = 1
        if data[6] == 128:
            buttons[11] = 1

        # Prepalo los hats en el mismo formato que para el caso de los joystick por cable
        hats = (0, 0)
        if data[5] == 6:
            hats = (-1, 0)
        if data[5] == 2:
            hats = (1, 0)
        if data[5] == 0:
            hats = (0, 1)
        if data[5] == 4:
            hats = (0, -1)

        self.procesar(axes, buttons, hats)

    def procesar (self, axes, buttons, hats):
        roll = self.map_axis(axes[3])  # RC1: Roll
        pitch = self.map_axis(axes [self.pitch])  # RC2: Pitch
        throttle = self.map_axis(-axes[1])  # RC3: Throttle
        yaw = self.map_axis(axes[0])  # RC4: Yaw
        self.dron.send_rc(roll, pitch, throttle, yaw)

        if buttons[8] == 1:
            print ('vamos a armar el dron ', self.id)
            self.dron.arm()
            print("Armado")
        if buttons[9] == 1:
            print('vamos a despegar el dron ', self.id)
            self.dron.takeOff(5, blocking=False)
            print("Despegando")

        if buttons[0] == 1:
            self.dron.RTL(blocking=False)
            print("Retornado")
        if buttons[1] == 1:
            ''' puesto que el cambio de modo es bloqueante, cuando se ha realizado el programa recibe
                       los mensajes retrasados del joystick inalambrico, lo cual bloquea el sistema. 
                       Por tanto solo hago caso al joystick si aun no estamos en Guided
                       '''
            if self.dron.flightMode != 'GUIDED':
                print('voy a poner modo ')
                self.dron.setFlightMode('GUIDED')
                print("Modo Guided")

        if buttons[2] == 1:
            self.dron.Land(blocking=False)
            print("Aterrizado")
        if buttons[3] == 1:
            ''' puesto que el cambio de modo es bloqueante, cuando se ha realizado el programa recibe
            los mensajes retrasados del joystick inalambrico, lo cual bloquea el sistema. 
            Por tanto solo hago caso al joystick si aun no estamos en loiter
            '''
            if self.dron.flightMode != 'LOITER':
                print('voy a poner modo ')
                self.dron.setFlightMode('LOITER')
                print("Modo Loiter")
        if buttons[4] == 1:
            self.idCallBack(self.id)
    def control_loop (self):
        # con este parametro hacemos que el dron no exija que el throttle esté al mínimo para armar
        params = [{'ID': "PILOT_THR_BHV", 'Value': 1}]
        self.dron.setParams(params)
        # Inicializar pygame y el módulo de joystick
        pygame.init()
        pygame.joystick.init()
        ''' Ahora vamos a obtener una lista con los joysticks conectados '''
        joysticks = []
        numCable = 0 # voy a contar cuántos joysticks tengo conectados por cable (los que no tienen Twin en el nombre
        for i in range (pygame.joystick.get_count()):
            joysticks.append( pygame.joystick.Joystick(i))
            if 'Twin' not in pygame.joystick.Joystick(i).get_name():
                numCable = numCable + 1


        # En la lista de joystics  los inalambricos estan al inicio y luego vienen los conectados por cable
        # Si hay inalambricos Siempre van a salir dos  aunque en realidad solo tenga uno conectado.
        # En cambio de conectados por cable salen tantos como tenga conectados.
        # Por esa razon me interesa invertir las listas para que los inalambricos quedan al final
        joysticks.reverse()

        # ahora ya puedo seleccionar el joysticks que me interesa, a partir del id

        self.joystick = joysticks[self.id]
        self.joystick.init()


        if self.joystick.get_name() == 'Twin USB Joystick':
            # Obtengo todos los dispositivos conectados de tipo Hid (entre ellos los inalambricoa)
            all_hids = hid.HidDeviceFilter().get_devices()
            if not all_hids:
                print("⚠ No hay dispositivos HID.")
                exit()
            devices = []
            for dev in all_hids:
                if 'Twin' in dev.vendor_name:
                    devices.append (dev)
            # aqui tengo todos los dispositivos tipo Hid, entre los que están los dos Joysticks,
            # uno de los cuales es el que necesito. Ahora tengo que averiguar en que posición esta en esa lista
            # El numero de jpoysticks con cable esta en numCable. Por tanto el id tiene que ser numCable (en cuyo
            # caso el device que me interesa es el primero de la lista) o numCable + 1 (en ese caso será el segundo)
            indice = self.id - numCable
            device = devices[indice]
            device.open()
            # tomo nota del eje que este joystick usa para el pitch
            self.pitch = 2
            # el joystick inalambrico activara con frecuencia la función self.inalambrico
            device.set_raw_data_handler(self.inalambrico)
            self.working = True
            while self.working:
                time.sleep(0.1)
            device.close()
            self.joystick.quit()
            pygame.quit()

        else:
            # veamos que tipo de joystick con cable es, porque hay dos tipos con comportamiento ligeramente distinto
            # la diferencia esta en el eje que usan para el pitch
            if self.joystick.get_name() == 'USB Gamepad':
                self.pitch = 2
            elif self.joystick.get_name() == 'Generic USB Joystick':
                self.pitch = 4


            self.working = True
            while self.working:
                pygame.event.pump()
                axes, buttons, hats = self.codificador(self.joystick)
                self.procesar(axes, buttons, hats)
                time.sleep(0.1)
        # Restauro el parámetro que cambié
        params = [{'ID': "PILOT_THR_BHV", 'Value': 0} ]
        self.dron.setParams(params)

    def map_axis(self, value):
        """Convierte valor del eje (-1 a 1) a rango RC (1000 a 2000)"""
        return int(1500 + value * 500)

    def stop (self):
        self.working = False