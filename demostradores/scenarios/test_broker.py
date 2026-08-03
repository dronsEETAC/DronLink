
import paho.mqtt.client as mqtt
from paho.mqtt.client import ssl
client = mqtt.Client("Dashboard", transport="websockets")
client.tls_set(
    ca_certs=None,
    certfile=None,
    keyfile=None,
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS,
    ciphers=None,
)
client.connect("dronseetac.upc.edu", 8883)
print("Connected to dronseetac.upc.edu:8883")