
class Dron(object):
    def __init__(self, id = None):
        print ("DronLink con Handlers")
        self.id = id

        self.state = "disconnected"
        ''' los otros estados son:
                  connected
                  arming
                  armed
                  takingOff
                  flying
                  returning
                  landing
              '''
        self.lat = 0
        self.lon = 0
        self.alt = 0
        self.groundSpeed = 0

        self.frequency = None  #numero de muestras de telemetría por segundo

        self.going = False # se usa en dron_nav
        self.navSpeed = 5 # se usa en dron_nav
        self.direction = 'Stop' # se usa en dron_nav

        self.sendTelemetryInfo = False #usado en dron_telemetry

        self.sendLocalTelemetryInfo = False  # usado en dron_local_telemetry

        self.step = 1 # se usa en dron_mov. Son los metros que mueve en cada paso

        self.position = [0,0,0] # se usa en dron_mov para identificar la posición del dron dentro del espacio
        self.heading = 0
        self.lastDirection = None
        self.flightMode = None
        self.minAltGeofence = 0
        self.takeTelemetry = False

        self.message_handler = None
        # se usa para parar la captura de datos de telemetria para que no molesten cuando quiero
        # leer parámetros

    # aqui se importan los métodos de la clase Dron, que están organizados en ficheros.
    # Así podría orgenizarse la aportación de futuros alumnos que necesitasen incorporar nuevos servicios
    # para sus aplicaciones. Crearían un fichero con sus nuevos métodos y lo importarían aquí
    # Lo que no me gusta mucho es que si esa contribución nueva requiere de algún nuevo atributo de clase
    # ese atributo hay que declararlo aqui y no en el fichero con los métodos nuevos.
    # Ese es el caso del atributo going, que lo tengo que declarar aqui y preferiría poder declararlo en el fichero dron_goto

    from dronLink.modules.dron_connect import connect, _connect, disconnect, _handle_heartbeat, _record_telemetry_info, _record_local_telemetry_info
    from dronLink.modules.dron_arm import arm, _arm
    from dronLink.modules.dron_takeOff import takeOff, _takeOff
    from dronLink.modules.dron_RTL_Land import  RTL, Land, _goDown
    from dronLink.modules.dron_nav import _prepare_command, go, _startGo, _stopGo, _goingTread, changeHeading, _changeHeading, unfixHeading, changeNavSpeed
    from dronLink.modules.dron_goto import goto, _goto, _distanceToDestinationInMeters
    from dronLink.modules.dron_parameters import getParams, _getParams, setParams, _setParams
    from dronLink.modules.dron_geofence import  setScenario, _setScenario, getScenario, _getScenario, _buildScenario
    from dronLink.modules.dron_telemetry import send_telemetry_info, _send_telemetry_info, stop_sending_telemetry_info

    from dronLink.modules.dron_local_telemetry import send_local_telemetry_info, _send_local_telemetry_info, stop_sending_local_telemetry_info
    from dronLink.modules.dron_mission import executeMission, _executeMission, uploadMission, _uploadMission, _getMission, getMission
    from dronLink.modules.dron_altitude import change_altitude, _change_altitude
    from dronLink.modules.dron_drop import drop
    from dronLink.modules.dron_move import move_distance, _move_distance, _prepare_command_mov,setMoveSpeed
    from dronLink.modules.dron_bottomGeofence  import startBottomGeofence, stopBottomGeofence,  _minAltChecking
    from dronLink.modules.message_handler import MessageHandler