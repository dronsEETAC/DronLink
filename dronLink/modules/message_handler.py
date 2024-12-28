import threading
import queue
from pymavlink import mavutil

class MessageHandler:
    '''
    En esta clase centralizamos el tema de leer los mensajes, para que haya solo un punto en el que se leen
    los mensajes del dron y se reparte la información a los que la hayan pedido.
    En la versión anterior de la librería había varios puntos en los que se leian mensajes, lo cual provocaba
    bloqueos frecuentes que afectaban a la fluidez

    En principio esta clase solo la usan los métodos de la clase Dron.
    Hay dos tipos de peticiones. Por una parte están las peticiones síncronas. En ese caso, el método que sea
    necesita un dato, lo pide a este handler y se queda boqueado hasta que el handler le proporciona el dato.
    La sincronización entre el consumidor (el método que necesita el dato) y el productor (el handler) se
    implementa mediante una cola que entrega el consumidor en la que el productor pondrá el dato cuando
    disponga de el. El caso tipico es el método getParameters. Inmediatamente después de pedir el valor de un parámetro
    ese método ejecutará la siguiente instrucción:

    message = self.message_handler.wait_for_message('PARAM_VALUE', timeout=3)

    Esta instrucción espera un máximo de 3 segundos a que el handler le proporcione el valor del parámetro pedido.

    Es posible establecer una condición para el mensaje que esperamos. En ese caso tenemos que indicarle qué función
    es la que va a comprobar si se cumple la condición deseada. El caso típico es esperar a que el dron aterrice.
    La llamada en este caso seria así:

    def _check (self, msg):
       return msg.relative_alt < 500

    msg = self.message_handler.wait_for_message(
        'GLOBAL_POSITION_INT',
        condition=self._check,
    )
    La función que se indica (en este caso _check) recibe siempre como parámetro el mensaje. En este ejemplo,
    la función comprueba que la altitud es ya menor de medio metro, con lo que damos el dron por aterrizaro.

    La función que verifica la condición puede tener parámetros adicionales. Un ejemplo tipico es la comprobación
    de que el dron ha alcanzado la altura de despegue indicada. En este caso la llamada sería esta:

    def _check (self, msg, target):
       return msg.relative_alt > target*950

    msg = self.message_handler.wait_for_message(
        'GLOBAL_POSITION_INT',
        condition=self._check,
        params = aTargetAltitude
    )
    La funcion _check recibe como parámetro, además del mensaje, la altura objetivo (aTargerAltitude) y comprueba si
    la altura es ya superior a ese objetivo (con un error del 5%). Recordar que la altura objetivo se especifica en metros
    pero la altura relativa nos la dan en milimetros.

    Las peticiones sincronas pueden tener un problema. En circunstancias de saturación de la estación de tierra, por ejemplo,
    cuando se trabaja  con multiples drones, es posible que pidamos el mensaje que queramos y este llegue antes de que
    se haya llamado a la función wait_for_message, con lo que el mensaje se perderá. Eso pasa por ejemplo, cuando pedímos parámetros
    de varios drones.

    Para combatir esto se puede hacer que la función que pide el mensaje lo pida repetidamente hasta que el mensaje llegue.
    Muy improbable es que el problema se repita varias veces seguidas.

    La otra opción es cambiar ligeramente el orden de las cosas. Para ello, primero se llama a la función wait_for_message pero
    indicandole que solo registre el handler para el mensaje y no se quede esperandolo. Por ejemplo:

     waiting = self.message_handler.wait_for_message(
                'PARAM_VALUE',
                condition=self._checkParameter,
                params=PARAM,
                wait=False
            )
    Entonces hacemos la petición del mensaje, por ejemplo:

      self.vehicle.mav.param_request_read_send(
                self.vehicle.target_system, self.vehicle.target_component,
                PARAM.encode(encoding="utf-8"),
                -1
            )
    y despues esperamos la llegada del mensaje, que aunque llegue rápido ya encontrará
    la cola del handler preparada. Para ello llama a la función wait_now

    message = self.message_handler.wait_now(waiting, timeout=5)


    Por otra parte tenemos las peticiones asíncronas, del tipo "Cuando recibas un mensaje de este tipo ejecutaeste callback".
    Ese es el tipo de peticiones que necesitamos para recoger periódicamente os datos de telemetría.
    Para esas peticiones tenemos el método register_handler, al que le damos el tipo de mensaje y la función
    que queremos que se ejecute cada vez que llegue un mensaje de ese tipo.

    '''

    def __init__(self, vehicle):
        self.vehicle = vehicle
        # Aqui se encolan las peticiones asíncronas, es decir, se indica qué tipo de mensaje se quiere y cual es la
        # funcion (que podemos llamar callback o handler) que hay que ejecutar cada vez que llega un mensaje de ese tipo
        # la estructura es una lista de tipos de mensajes y para cada tipo de mensaje tenemos una lista de handlers (callbacks)
        self.handlers = {}
        self.lock = threading.Lock()
        self.running = True
        # en esta lista se guardan las peticiones síncronas, es decir, el que pide el mensaje se bloquea hasta
        # que llega lo que ha pedido
        self.waiting_threads = []
        # este es el thread en el que se leen y distribuyen los mensajes
        self.thread = threading.Thread(target=self._message_loop)
        self.thread.daemon = True
        self.thread.start()

    def _message_loop(self):
        while self.running:
            # espero un mensaje. Este es el único punto en el que espermos un mensaje
            #msg = self.vehicle.recv_match(blocking=True, timeout=3)
            msg = self.vehicle.recv_match(blocking=True)

            if msg:
                msg_type = msg.get_type()
                #print ('recibo ', msg_type)

                # primero miramos si hay alguna petición síncrona para este mensaje
                with self.lock:
                    sendMessage = False
                    for waiting in self.waiting_threads:
                        if waiting['msg_type'] == msg_type:
                            if not waiting['condition']:
                                sendMessage = True
                            elif waiting['params']:
                                sendMessage = waiting['condition'](msg, waiting['params'])
                            else:
                                sendMessage = waiting['condition'](msg)
                            # hemos encontrado a alguien que está esperando este mensaje en la cola que nos dió
                            # le pasamos el mensaje
                            if sendMessage:
                                waiting['queue'].put(msg)
                                # y lo quitamos de la cola porque ya ha sido atendido
                                #self.waiting_threads.remove(waiting)
                                break

                # ahora atendemos a las peticiones asíncronas
                if msg_type in self.handlers:
                    # vemos si este tipo de mensaje está en la lista de handlers
                    for callback in self.handlers[msg_type]:
                        # Ejecutamos todos los handlers asociados a este tipo de mensaje
                        callback(msg)

    def register_handler(self, msg_type, callback):
        with self.lock:
            # vemos si ese tipo de mensaje aun no esta en la lista de handlers
            if msg_type not in self.handlers:
                # creamos una entrada nueva para ese tipo de mensaje
                self.handlers[msg_type] = []
            # añadimos el nuevo handler a la cola de ese tipo de mensaje
            self.handlers[msg_type].append(callback)

    def unregister_handler(self, msg_type, callback):
        # eliminamos el handler de la lista de handlers de ese tipo de mensaje
        with self.lock:
            if msg_type in self.handlers and callback in self.handlers[msg_type]:
                self.handlers[msg_type].remove(callback)
                if not self.handlers[msg_type]:
                    del self.handlers[msg_type]
    def wait_for_message(self, msg_type, condition=None, params= None, timeout = None, wait = True):
        # Le indico al handler el mensaje que necesito (tipo y condicion)
        # Puedo indicarle que no espere
        # En el caso de que espere le indico  el timeout
        # Creo una cola en la que quiero que el handler me deje el mensaje que espero
        msg_queue = queue.Queue()
        # Preparo la información de lo que espero
        waiting = {
            'msg_type': msg_type,
            'condition': condition,
            'params': params,
            'queue': msg_queue
        }
        with self.lock:
            # Le envío al handles la información de lo que espero
            self.waiting_threads.append(waiting)
        if wait:
            # me quedo a esperar el mensaje
            try:
                # aqui espero que me ponga el mensaje en la cola que le he indicado
                msg = waiting['queue'].get(timeout=timeout)
            except queue.Empty:
                # si ha pasado el timeout retorno un mensaje vacio
                msg = None
            # elimino el registro del handler porque ya ha sido resuelto
            self.waiting_threads.remove(waiting)
            return msg
        else:
            # si no tengo que esperar devuelvo la estructura de datos que se necesitará para esperar más adelante
            return waiting



    def wait_now(self, waiting, timeout):
        # esta es la función que hay que llamar si no nos hemos parado a esperar en la llamada wait_for_message
        try:
            # aqui espero que me ponga el mensaje en la cola que le he indicado
            msg = waiting ['queue'].get(timeout=timeout)
        except queue.Empty:
            # si ha pasado el timeout retorno un mensaje vacio
            msg = None
        self.waiting_threads.remove(waiting)
        return msg

    def wait_for_message2(self, msg_type, condition=None, params= None, timeout=None):
        # Le indico al handler el mensaje que necesito (tipo y condicion) y me espero a recogerlo
        # tanto tiempo como indique el timeout
        # Creo una cola en la que quiero que el handler me deje el mensaje que espero
        msg_queue = queue.Queue()
        # Preparo la información de lo que espero
        waiting = {
            'msg_type': msg_type,
            'condition': condition,
            'params': params,
            'queue': msg_queue
        }
        #with self.lock:
        # Le envío al handles la información de lo que espero
        self.waiting_threads.append(waiting)
        try:
            # aqui espero que me ponga el mensaje en la cola que le he indicado
            print ('espero el mensaje')
            msg = msg_queue.get(timeout=timeout)
            print ('ya tengo el mensaje ', msg)
        except queue.Empty:
            # si ha pasado el timeout retorno un mensaje vacio
            print ('la cola esta vacia')
            msg = None
        self.waiting_threads.remove(waiting)
        return msg

    def stop(self):
        self.running = False
        self.thread.join()
