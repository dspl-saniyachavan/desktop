import paho.mqtt.client as mqtt
from flask import current_app
from ..core.extensions import socketio

def create_mqtt_client():

    def on_connect(client, userdata, flags, reason_code, properties):
        print("MQTT connected")
        client.subscribe("telemetry/data")

    def on_message(client, userdata, msg):
        payload = msg.payload.decode()
        print("Received:", payload)

        # Forward to WebSocket
        socketio.emit("telemetry_update", payload)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("mqtt", 1883)
    client.loop_start()

    return client
