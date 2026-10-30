import json
import logging
import math
import threading
import pymavlink.dialects.v20.all as dialect

import time

# Nombres de los parámetros en las diferentes versiones de ardupilor

PARAM_ALIASES = {

    "RTL_ALT": ("RTL_ALT_M", "RTL_ALT"),
    "RTL_ALT_FINAL": ("RTL_ALT_FINAL_M", "RTL_ALT_FINAL"),
    "RTL_SPEED": ("RTL_SPEED_MS", "RTL_SPEED"),
    "RTL_CLIMB_MIN": ("RTL_CLIMB_MIN_M", "RTL_CLIMB_MIN"),

    "WPNAV_SPEED": ("WP_SPD", "WPNAV_SPEED"),
    "WPNAV_SPEED_UP": ("WP_SPD_UP", "WPNAV_SPEED_UP"),
    "WPNAV_SPEED_DN": ("WP_SPD_DN", "WPNAV_SPEED_DN"),
    "WPNAV_RADIUS": ("WP_RADIUS_M", "WPNAV_RADIUS"),
    "WPNAV_ACCEL": ("WP_ACC", "WPNAV_ACCEL"),
    "WPNAV_ACCEL_Z": ("WP_ACC_Z", "WPNAV_ACCEL_Z"),
    "WPNAV_ACCEL_C": ("WP_ACC_CNR", "WPNAV_ACCEL_C"),

    "LAND_SPEED": ("LAND_SPD_MS", "LAND_SPEED"),
    "LAND_SPEED_HIGH": ("LAND_SPD_HIGH_MS", "LAND_SPEED_HIGH"),

    "PILOT_SPEED_UP": ("PILOT_SPD_UP", "PILOT_SPEED_UP"),
    "PILOT_SPEED_DN": ("PILOT_SPD_DN", "PILOT_SPEED_DN"),
    "PILOT_TKOFF_ALT": ("PILOT_TKO_ALT_M", "PILOT_TKOFF_ALT")
}

def _descargarTodosLosParametros(self):

    params = {}

    self.vehicle.mav.param_request_list_send(
        self.vehicle.target_system,
        self.vehicle.target_component
    )

    last = time.time()

    while True:

        msg = self.vehicle.recv_match(
            type='PARAM_VALUE',
            blocking=True,
            timeout=1
        )

        if msg is None:

            # llevamos un segundo sin recibir parámetros
            if time.time() - last > 1:
                break

            continue

        last = time.time()

        name = msg.param_id

        if isinstance(name, bytes):
            name = name.decode()

        name = name.rstrip('\x00')

        params[name] = msg.param_value

    return params

def _normalizaParametros(self, raw_params):

    database = {}

    # Primero copiamos todos los parámetros sin cambios
    for name, value in raw_params.items():

        database[name] = {
            "real_name": name,
            "value": value
        }

    # Ahora añadimos los nombres lógicos
    for logical_name, aliases in PARAM_ALIASES.items():

        for real_name in aliases:

            if real_name in raw_params:

                database[logical_name] = {
                    "real_name": real_name,
                    "value": raw_params[real_name]
                }

                break

    return database



def _checkParameter (self, msg, param):
    if msg.param_id == param:
        return True
    else:
        return False

def _getParams(self, parameters, callback=None):
    result = []

    for name in parameters:

        if name in self.parametros:
            result.append({
                name: self.parametros[name]["value"]
            })

    if callback != None:
        if self.id == None:
            callback(result)
        else:
            callback(self.id, result)
    return result


def getParams(self, parameters, blocking=True, callback=None):
    if blocking:
        result = self._getParams(parameters)
        return result
    else:
        getParamsThread = threading.Thread(target=self._getParams, args=[parameters, callback,])
        getParamsThread.start()

def _setParams(self, parameters, callback=None, params=None):

    for PARAM in parameters:

        logical_name = PARAM["ID"]
        value = PARAM["Value"]

        if logical_name not in self.parametros:
            logging.warning("Parámetro %s desconocido", logical_name)
            continue

        info = self.parametros[logical_name]

        real_name = info["real_name"]
        param_type = dialect.MAV_PARAM_TYPE_REAL32

        if self.verbose:
            logging.info(
                "Escribiendo %s (%s) = %s",
                logical_name,
                real_name,
                value
            )

        # Primero registramos la espera para evitar perder la respuesta
        waiting = self.message_handler.wait_for_message(
            'PARAM_VALUE',
            condition=self._checkParameter,
            params=real_name,
            wait=False
        )

        # Enviamos el PARAM_SET
        message = dialect.MAVLink_param_set_message(
            target_system=self.vehicle.target_system,
            target_component=self.vehicle.target_component,
            param_id=real_name.encode("utf-8"),
            param_value=value,
            param_type=param_type
        )

        self.vehicle.mav.send(message)

        # Esperamos la confirmación
        reply = self.message_handler.wait_now(waiting, timeout=5)

        if reply is None:
            logging.warning(
                "Timeout esperando confirmación de %s",
                logical_name
            )
            continue

        reply = reply.to_dict()

        returned_value = reply["param_value"]

        # Comparación robusta para float
        if math.isclose(returned_value, value,
                        rel_tol=1e-6,
                        abs_tol=1e-6):

            info["value"] = returned_value

            if self.verbose:
                logging.info(
                    "Parámetro %s actualizado correctamente",
                    logical_name
                )

        else:

            logging.warning(
                "El autopiloto ha devuelto %s=%s en lugar de %s",
                logical_name,
                returned_value,
                value
            )

    if callback is not None:

        if self.id is None:

            if params is None:
                callback()
            else:
                callback(params)

        else:

            if params is None:
                callback(self.id)
            else:
                callback(self.id, params)


def setParams(self, parameters, blocking=True, callback=None, params = None):
    if blocking:
        self._setParams(parameters)
    else:
        setParamsThread = threading.Thread(target=self._setParams, args=[parameters, callback, params])
        setParamsThread.start()

