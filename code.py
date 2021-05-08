# https://learn.adafruit.com/mqtt-in-circuitpython/circuitpython-wifi-usage
# https://learn.adafruit.com/mqtt-in-circuitpython/connecting-to-a-mqtt-broker
# required from adafruit_bundle:
# - adafruit_requests
# - adafruit_minimqtt
# - adafruit_bus_device
# - adafruit_register
# - adafruit_si7021
import time
import ssl
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn
import adafruit_si7021

# Add a secrets.py to your filesystem that has a dictionary called secrets with "ssid" and
# "password" keys with your WiFi credentials. DO NOT share that file or commit it into Git or other
# source control.
# pylint: disable=no-name-in-module,wrong-import-order
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])
### Feeds ###
light_feed = "greenhouse/light"
temp_feed = "greenhouse/temperature"
humidity_feed = "greenhouse/humidity"

# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Connected to MQTT!")

def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from MQTT!")


def get_voltage(pin):
        return (pin.value * 3.3) / 65536

# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=secrets["broker"],
    port=secrets["port"],
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

# Setup the callback methods above
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected

# Connect the client to the MQTT broker.
print("Connecting to MQTT...")
mqtt_client.connect()

# Create library object using our Bus I2C port
sensor = adafruit_si7021.SI7021(board.I2C())
light_pin = AnalogIn(board.IO4)

while True:
    # Poll the message queue
    mqtt_client.loop()

    # get the current temperature
    light_val = get_voltage(light_pin)
    temp_val = ((sensor.temperature * 9)/5) + 32
    humidity_val = sensor.relative_humidity

    # Send a new messages
    mqtt_client.publish(light_feed, light_val)
    mqtt_client.publish(temp_feed, temp_val)
    mqtt_client.publish(humidity_feed, humidity_val)
    time.sleep(0.5)
