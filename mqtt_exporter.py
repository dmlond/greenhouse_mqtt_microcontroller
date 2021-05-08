from prometheus_client import start_http_server, Gauge
import random
import time
import paho.mqtt.client as mqtt

guage = { 
  "greenhouse/light": Gauge('light','light in lumens'),
  "greenhouse/temperature": Gauge('temperature', 'temperature in fahrenheit'),
  "greenhouse/humidity": Gauge('humidity','relative % humidity')
}

try:
    from mqtt_secrets import mqtt_secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("greenhouse/light")
    client.subscribe('greenhouse/temperature')
    client.subscribe('greenhouse/humidity')

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload
    guage[topic].set(payload)

client = mqtt.Client()
client.username_pw_set(mqtt_secrets["mqtt_user"],mqtt_secrets['mqtt_password'])
client.on_connect = on_connect
client.on_message = on_message
client.connect('localhost',1883,60)

if __name__ == '__main__':
    # Start up the server to expose the metrics.

    client = mqtt.Client()
    client.username_pw_set('london','abc123')
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('localhost',1883,60)

    start_http_server(8000)
    client.loop_forever()
