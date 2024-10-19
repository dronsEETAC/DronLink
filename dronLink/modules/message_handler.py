import threading
import queue
from pymavlink import mavutil

class MessageHandler:
# en esta clase centralizamos el tema de leer los mensajes, para que haya solo un punto en el que se leen
# los mensajes del dron y se reparte la información a los que la hayan pedido.
# En la versión anterior de la librería había varios puntos en los que se leian mensajes, lo cual provocaba
# bloqueos frecuentes que afectaban a la fluidez d

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
            msg = self.vehicle.recv_match(blocking=True, timeout=1)
            if msg:
                msg_type = msg.get_type()

                # Handle synchronous waits
                # primero miramos si hay alguna petición síncrona para este mensaje
                with self.lock:
                    for waiting in self.waiting_threads:
                        if waiting['msg_type'] == msg_type and (waiting['condition'] is None or waiting['condition'](msg)):
                            # hemos encontrado a alguien que está esperando este mensaje en la cola que nos dió
                            # le pasamos el mensaje
                            waiting['queue'].put(msg)
                            # y lo quitamos de la cola porque ya ha sido atendido
                            self.waiting_threads.remove(waiting)
                            break  # Remove only one waiting thread per message

                # Dispatch message to registered handlers
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

    def wait_for_message(self, msg_type, condition=None, timeout=None):
        # Le indico al handler el mensaje que necesito (tipo y condicion) y me espero a recogerlo
        # tanto tiempo como indique el timeout
        # Creo una cola en la que quiero que el handler me deje el mensaje que espero
        msg_queue = queue.Queue()
        # Preparo la información de lo que espero
        waiting = {
            'msg_type': msg_type,
            'condition': condition,
            'queue': msg_queue
        }
        with self.lock:
            # Le envío al handles la información de lo que espero
            self.waiting_threads.append(waiting)
        try:
            # aqui espero que me ponga el mensaje en la cola que le he indicado
            msg = msg_queue.get(timeout=timeout)
        except queue.Empty:
            # si ha pasado el timeout retorno un mensaje vacio
            msg = None
        return msg

    def stop(self):
        self.running = False
        self.thread.join()
