import paho.mqtt.client as mqtt
import time
import json
import random

client = mqtt.Client()
client.connect("localhost", 1883)
client.loop_start()

while True:
    data = {
        "value": random.randint(1, 100)
    }
    client.publish("test/data", json.dumps(data))
    print("Sent:", data)
    time.sleep(1)
