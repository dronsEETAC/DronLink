# La librería DronLink
DronLink es una librería que pretende facilitar el desarrollo de aplicaciones de control del dron. Ofrece una amplia variedad de funcionalidades y se está diseñando con la mente puesta en las posibles necesidades del Drone Engineering Ecosystem (DEE).    

# Proyecto Ejemplo

Este es un proyecto de ejemplo que muestra cómo incluir una imagen alineada a la derecha en un archivo `README.md`.

<p align="left">
    Este texto está alineado a la izquierda y la imagen está a la derecha.
    Puedes usar HTML dentro de Markdown para lograr este efecto.
</p>

<p align="right">
    <img src="https://via.placeholder.com/150" alt="Ejemplo de imagen" width="150"/>
</p>

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/usuario/proyecto-ejemplo.git
   ```
2. Entra en el directorio del proyecto:
   ```bash
   cd proyecto-ejemplo
   ```
3. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

Ejecuta el script principal con:
```bash
python main.py

 
En este repositorio puede encontrarse el código de la librería y varias aplicaciones que demuestran su uso, en una variedad de contextos. Es importante tener presente que DronLink está en desarrollo y, por tanto, no exenta de errores.
## 1. Alternativa a DroneKit
Los primeros módulos del DEE se implementaron usando la librería DroneKit, que es la más usada y documentada. Sin embargo, DroneKit ya no está en mantenimiento y se han observado problemas de compatibilidad con las versiones más actuales de los interpretes de Python. Esta ha sido la motivación principal para iniciar el desarrollo de una librería alternativa, junto con la intención de que la nueva librería sea más simple de usar y orientada a las necesidades del DEE.
No obstante, DroneKit es operativa y existe mucha documentación. Además, existen soluciones sencillas para resolver algunos de los problemas de compatibilidad encontrados. En particular, el siguiente gif muestra cómo resolver el primer problema de compatibilidad que se observa al intentar usar DroneKit con versiones actuales del intérprete de Python.
<img src="https://github.com/dronsEETAC/Taller-de-Drones-TelecoRenta/assets/100842082/841e7a62-ef19-4841-be70-e6079cf7e9c4" width="400" height="200">
## 2. Modelo de programación de DronLink
DronLink esta implementada en forma de clase **(la clase Dron)** con sus atributos y una
variedad de métodos para operar con el dron. La clase con los atributos está definida en el
fichero _Dron.py_ y los métodos están en los diferentes ficheros de la carpeta _modules_
(connect.py, arm.py, etc.).

Muchos de los métodos pueden activarse **de forma bloqueante o de forma no bloqueante**. En
el primer caso, **el control no se devuelve al programa que hace la llamada hasta que la
operación ordenada haya acabado**. Si la llamada es no bloqueante entonces **el control se
devuelve inmediatamente** para que el programa pueda hacer otras cosas mientras se realiza la
operación.

Un buen ejemplo de método con estas dos opciones es _takeOff_, que tiene la siguiente cabecera:

```
def takeOff(self, aTargetAltitude, blocking=True, callback=None , params = None)
```

Al llamar a este método hay que pasarle como parámetro la **altura de despegue**. Por defecto la
operación es **bloqueante**. Por tanto, el programa que hace la llamada no se reanuda hasta que 
el dron esté a la altura indicada. En el caso de usar la opción no bloqueante se puede indicar el
nombre de la función que queremos que se ejecute cuando la operación haya acabado (función a la que
llamamos habitualmente **callback**). En el caso de  takeOff, cuando el dron  esté a la altura indicada
se activará la funcion callback. Incluso podemos indicar los parámetros que queremos que
se le pasen a ese callback  en el momento en que se active. **Recuerda que self no es ningún parámetro**. 
Simplemente **indica que este es un método de una clase** (en este caso, la clase Dron).

Los siguientes ejemplos aclararán estas cuestiones.

_Ejemplo 1_

```
from Dron import Dron
dron = Dron()
dron.connect ('tcp:127.0.0.1:5763', 115200) # me conecto al simulador
print (‘Conectado’)
dron.arm()
print (‘Armado’)
dron.takeOff (8)
print (‘En el aire a 8 metros de altura’)
```

En este ejemplo todas las llamadas son bloqueantes.


_Ejemplo 2_

```
from Dron import Dron
dron = Dron()
dron.connect ('tcp:127.0.0.1:5763', 115200) # me conecto al simulador
print (‘Conectado’)
dron.arm()
print (‘Armado’)
dron.takeOff (8, blocking = False) # llamada no bloqueante, sin callback
print (‘Hago otras cosas mientras se realiza el despegue’)
```
En este caso la llamada no es bloqueante. El programa continua su ejecución 
mientras el dron  realiza el despegue. 

_Ejemplo 3_

```
from Dron import Dron
dron = Dron()
dron.connect ('tcp:127.0.0.1:5763', 115200) # me conecto al simulador
print (‘Conectado’)
dron.arm()
print (‘Armado’)    
     
def enAire (): # esta es la función que se activa al acabar la operación (callback)
    print (‘Por fin ya estás en el aire a 8 metros de altura’)
      
# llamada no bloqueante con callback
dron.takeOff (8, blocking = False, callback= enAire)
print (‘Hago otras cosas mientras se realiza el despegue’)
```
De nuevo una llamada no bloqueante. Pero en este caso le estamos indicando que cuando 
el dron esté a la altura indicada ejecute la función enAire, que en este caso simplemente
nos informa del evento.     
       
_Ejemplo 4_

```
from Dron import Dron
dron = Dron()
dron.connect ('tcp:127.0.0.1:5763', 115200) # me conecto al simulador
print (‘Conectado’)
dron.arm()
print (‘Armado’)

def informar (param):
   print (‘Mensaje del dron: ‘, param)

# Llamada no bloqueante, con callback y parámetro para el callback
dron.takeOff (8, blocking = False, callback= informar, params= ‘En el aire a 8 metros de altura’)
print (‘Hago otras cosas mientras se realiza el despegue. Ya me avisarán’)
```
En este caso, en la llamada no bloqueante añadimos un parámetro que se le pasará al callback en 
en el momento de activarlo. De esta forma, la misma función _informar_ se puede usar  como callback
para otras llamadas no bloqueantes. Por ejemplo, podríamos llamar de forma no bloqueante al método 
para aterrizar y pasarle como callback también la función _informar_, pero ahora con el  parámetro
'Ya estoy en tierra', que es lo que escribiría en consola la función  _informar_ en el momento del aterrizaje.

_Ejemplo 5_

```
from Dron import Dron
dron = Dron()
# conexión con identificador del dron
dron.connect ('tcp:127.0.0.1:5763', 115200, id=1)
print (‘Conectado’)
dron.arm()
print (‘Armado’)
     
# La función del callback recibirá el id del dron como primer parámetro
def informar (id, param):
    print (‘Mensaje del dron ‘+str(id) + ‘: ‘ + param)
    
dron.takeOff (8, blocking = False, callback= informar,
params= ‘En el aire a 8 metros de altura’)
print (‘Hago otras cosas mientras se realiza el despegue. Ya me avisarán’)
```

En este ejemplo usamos la opción de identificar al dron **en el momento de la conexión**
(podríamos tener varios drones, cada uno con su identificador). Si usamos esa opción entonces
el método de la librería va a añadir siempre ese identificador como primer parámetro del
callback que le indiquemos.

La modalidad no bloqueante en las llamadas a la librería es especialmente útil **cuando
queremos interactuar con el dron mediante una interfaz gráfica**. Por ejemplo, no vamos a
querer que se bloquee la interfaz mientras el dron despega. Seguramente querremos seguir
procesando los datos de telemetría mientras el dron despega, para mostrar al usuario, por
ejemplo, la altura del dron en todo momento.     
   
En esta lista de distribución pueden encontrase varios vídeos que muestran estos conceptos en acción. Es importante tener en cuenta que en el momento de grabar esos vídeos la librería tenía el nombre provisional de DronLib, y no DronLink, que es el nombre actual. Incluso es posible que alguno de los métodos que se usan en los vídeos hayan cambiado. En la siguiente sección hay una descripción detallada de los métodos de la versión actual.    

[![](https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DryezfzIUBrE)](https://www.youtube.com/playlist?list=PLyAtSQhMsD4oc0kzDygK73o3wkhfJbiZs)



## 3. Métodos de la clase Dron
En la tabla que se enlaza más abajo se describen los métodos de la clase Dron de la versión actual de DronLink.
     
[Métodos de la clase Dron](dronLink/docs/tabla_dronLink.pdf)   

## 4. Instalación de dronLink
Para poder usar la librería dronLink en un proyecto Pycharm es necesario copiar la carpeta dronLink que hay en este repositorio en la carpeta del proyecto en el que se quiere usar. Para ello basta clonar este repositorio y luego copiar la carpeta dronLink (y posiblemente borrar después el repositorio clonado).     

Una alternativa es desacargar solamente la carpeta dronLink. El siguiente vídeo muestra cómo hacerlo.     
  
[![](https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DDr551YGz3QA)](https://www.youtube.com/watch?v=Dr551YGz3QA)     

## 5. Demostradores
En este repositorio se proporcionan cuatro aplicaciones que demuestran el uso de la librería DronLink en diferentes contextos (modo de comunicación directo, modo de comunicación global y enjambre de drones). Puede ser conveniente ver antes este video que aclara la cuestión de los modos de comunicación tierra-dron.      

[![](https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DfOmVdmOW8ag)](https://www.youtube.com/watch?v=fOmVdmOW8ag)


Los tres demostradores trabajan con el simulador SITL. Para trabajar con el dron real únicamente se necesita cambiar el string de conexión que se le pasa como parámetro al método connect.     
    
### Dashboard con comunicación directa
Se trata de una aplicación que presenta al usuario una interfaz basada en botones que permiten realizar las operaciones básicas de control del dron (conectar, armar, despegar, navegar en diferentes direcciones, aterrizar, etc.). Utiliza el modo de comunicación directa. Por tanto, es la propia aplicación la que usa la clase Dron para comunicarse con el dron a través de la radio de telemetría.      
   
En estos vídeos puede verse la aplicación en acción y el aspecto que tiene el código.   

[![](https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D3HwjL96IGyo)](https://www.youtube.com/watch?v=3HwjL96IGyo)

Es importante tener presente que para poner en marcha esta aplicación es necesario instalar la librería _pymavlink_, que es la que necesita DronLink (en realidad, cualquier aplicación que use DronLink necesita la instalacion previa de esa librería).   
  
### Dashboard con comunicación global
Esta aplicación usa el modo de comunicación global. Por tanto, se comunica a través de un bróker MQTT con un servicio de control del dron (AutopilotService), que es quién realmente se comunica con el dron. En un entorno de producción, trabajando con el dron real (y no con el simulador, como es el caso), el AutopilotService se ejecutaría a bordo del dron (por ejemplo, en una Raspberry Pi) o en el propio portátil (que estaría conectado al dron por la radio de telemetría), de manera que el AutopilotService podría aceptar peticiones también de otras aplicaciones externas (por ejemplo, una WebApp que se ejecuta en un teléfono móvil).      
  
La aplicación también presenta una interfaz con algunos botones. Además, muestra un mapa en el que podemos seguir los movimientos del dron. Junto con las operaciones más básicas, se puede crear un plan de vuelo (indicando los waypoints sobre el propio mapa) y ejecutarlo.     
 
En estos vídeos puede verse la aplicación en acción y el aspecto que tiene el código.     

[![](https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DUrnyuUyTqhk)](https://www.youtube.com/watch?v=UrnyuUyTqhk)
 
Para ejecutar esta aplicación será necesario instalar las librerías _tkintermapview_, _pillow_ y _paho_mqtt_ (ATENCIÓN: version 1.6.1), que permiten usar mapas y procesar imágenes.    

### Dashboard para enjambre de drones
Esta aplicación permite controlar un enjambre de hasta 9 drones (para lo cual hay que poner en marcha desde Mission Planner un enjambre de simuladores SITL). La aplicación permite elegir el número de drones del enjambre y seleccionar cuáles de los drones deben ejecutar las ordenes indicadas. Además, muestra en un mapa la posición de cada uno de los drones del enjambre. También es posible dirigir a los drones seleccionados a un punto señalado sobre el mapa.
 
Esta aplicación también usa el modo de comunicación directo. Para ello, necesita definir una lista de objetos de la clase Dron, cada uno de ellos para controlar uno de los drones. En el caso de llevar esta aplicación a un entorno de producción, sería necesario conectar al portátil tantas radios de telemetría como drones tuviera el enjambre.     
 
En estos vídeos puede verse la aplicación en acción y el aspecto que tiene el código.     

[![](https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3Dn9irtWyzfLc)](https://www.youtube.com/watch?v=n9irtWyzfLc)

Esta aplicación también necesita las librerías _tkintermapview_ y _pillow_.    

### Dashboard para gestionar escenarios
Esta aplicación permite diseñar y cargar en el dron escenarios. Un escenario no es más que un área denominada geofence de inclusión (de la que el dron no va a poder salir) y un conjunto de áreas denominadas geofences de exclusión (en las que el dron no puede entrar) y que están dentro del geofence de inclusión. Con estos elementos se pueden crear circuitos para el dron, que llamamos escenarios.    

En estos vídeos puede verse la aplicación en acción y el aspecto que tiene el código.     

[![](https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DNZRXXUbdXQ0)](https://www.youtube.com/watch?v=NZRXXUbdXQ0)     

La aplicación usa el modo de comunicación directo y pone a prueba los métodos _setScenario_ y _getScenario_ de la librería DronLink. Requiere la instalación de las librerías _geographiclib_, _geopy_, _pyscreenshot_ y _puautogui_.    

