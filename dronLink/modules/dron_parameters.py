import json
import threading
import pymavlink.dialects.v20.all as dialect

def _checkParameter (self, msg, param):
    if msg.param_id == param:
        return True
    else:
        return False


def _getParams(self,parameters,  callback=None):
    # esta es la nueva versión,
    # ahora primero encolamos el handler, luego pedimos el parámetro y después nos quedamos a la espera
    # de que llegue el parámetro. Así, cuando llegue el parámetro seguro que ya está encolado el handler.
    print ('vamos a leer los parámetros')
    result = []
    i =0
    for PARAM in parameters:
            # pido el valor del siguiente parámetro de la lista
            # entro en un bucle para repetir la petición hasta que llegue
            ready = False
            while not ready:
                # registro el handler pero no me quedo a esperar
                waiting = self.message_handler.wait_for_message(
                    'PARAM_VALUE',
                    condition=self._checkParameter,
                    params=PARAM,
                    wait=False
                )
                # pido el parámetro
                self.vehicle.mav.param_request_read_send(
                    self.vehicle.target_system, self.vehicle.target_component,
                    PARAM.encode(encoding="utf-8"),
                    -1
                )
                # ahora si que me espero a que llegue. Espero 5 segundos
                message = self.message_handler.wait_now(waiting, timeout=5)
                if message:
                    message = message.to_dict()
                    result.append({
                        message['param_id']: message["param_value"]
                    })
                    ready = True
                    i= i+1
                    print ('ya tengo parámetro '+str(i)+ ' de '+ str(len(parameters)))


    if callback != None:
        if self.id == None:
            callback(result)
        else:
            callback(self.id, result)
    else:
        return result


def _getParams2(self,parameters,  callback=None):
    # esta es una versión anterior que tiene un problema. Primero pedimos un parámetro y luego encolamos
    # el handler para procesar el mensaje cuando llegue. Pero en algunos casos ocurre que el mensaje
    # con el parámetro llega cuando aun no hemos encolado el handler, con lo cual el mensaje se pierde.
    # por eso es necesario el bucle que insiste en pedir el parámetro a ver si a la segunda hay más suerte.
    # por tanto, esta versión funciona, aunque con esa ineficiencia.
    # en la nueva versión eso se ha arreglado.
    print ('vamos a leer los parámetros')
    result = []
    for PARAM in parameters:
        # pido el valor del siguiente parámetro de la lista
        ready = False
        while not ready:
            print ('PIDO ', PARAM)
            self.vehicle.mav.param_request_read_send(
                self.vehicle.target_system, self.vehicle.target_component,
                PARAM.encode(encoding="utf-8"),
                -1
            )
            # y espero que llegue el valor
            message = self.message_handler.wait_for_message(
                'PARAM_VALUE',
                condition=self._checkParameter,
                params=PARAM,
                timeout = 5
            )
            print ('***** ', message)
            if message:
                message = message.to_dict()
                result.append({
                    message['param_id']: message["param_value"]
                })
                ready = True
                print ('ya tengo otro')

    if callback != None:
        if self.id == None:
            callback(result)
        else:
            callback(self.id, result)
    else:
        return result


def getParams(self, parameters, blocking=True, callback=None):
    if blocking:
        result = self._getParams(parameters)
        return result
    else:
        getParamsThread = threading.Thread(target=self._getParams, args=[parameters, callback,])
        getParamsThread.start()



def _setParams(self,parameters,  callback=None, params = None):
    for PARAM in parameters:

        message = dialect.MAVLink_param_set_message(target_system=self.vehicle.target_system,
                                                        target_component=self.vehicle.target_component, param_id=PARAM['ID'].encode("utf-8"),
                                                        param_value=PARAM['Value'], param_type=dialect.MAV_PARAM_TYPE_REAL32)
        self.vehicle.mav.send(message)

    if callback != None:
        if self.id == None:
            if params == None:
                callback()
            else:
                callback(params)
        else:
            if params == None:
                callback(self.id)
            else:
                callback(self.id, params)


def setParams(self, parameters, blocking=True, callback=None, params = None):
    if blocking:
        self._setParams(parameters)
    else:
        setParamsThread = threading.Thread(target=self._setParams, args=[parameters, callback, params])
        setParamsThread.start()

