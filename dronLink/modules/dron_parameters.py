import json
import threading
import pymavlink.dialects.v20.all as dialect



def _getParams(self,parameters,  callback=None):
    # detengo la toma de datos de telemetria para que no interfiera con la lectura
    # de parametros, porque si no se hace asi, esa lectura puede ser muy lenta
    self.takeTelemetry = False
    result = []
    for PARAM in parameters:
        ready = False
        while not ready:
            # pido el valor del siguiente parámetro de la lista
            self.vehicle.mav.param_request_read_send(
                self.vehicle.target_system, self.vehicle.target_component,
                PARAM.encode(encoding="utf-8"),
                -1
            )
            # y espero que llegue el valor. Si no llega en 3 segundos insisto.
            # le pido al handler el mensaje
            message = self.message_handler.wait_for_message('PARAM_VALUE', timeout=3)
            if message:
                message = message.to_dict()
                if message['param_id'] == PARAM:
                    ready = True
        # añado el valor a la lista
        result.append({
            message['param_id']: message["param_value"]
        })
        print ('ya tengo otro')
    print (result)
    # reactivo la toma de datos de telemetria
    self.takeTelemetry = True

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

