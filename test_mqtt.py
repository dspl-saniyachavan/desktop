#!/usr/bin/env python3
"""
Quick test to verify MQTT broker connectivity
"""

import paho.mqtt.client as mqtt
import json
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
        client.subscribe("precisionpulse/+/telemetry")
    else:
        print(f"❌ Failed to connect: {rc}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"📨 Received: {msg.topic} - {len(data.get('parameters', []))} parameters")
    except:
        print(f"📨 Received: {msg.topic}")

def test_mqtt():
    client = mqtt.Client("test_client")
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect("localhost", 1883, 60)
        client.loop_start()
        
        # Publish test message
        test_data = {
            "client_id": "test",
            "parameters": [{"id": "1", "name": "test", "value": 42.0}]
        }
        client.publish("precisionpulse/test/telemetry", json.dumps(test_data))
        print("📤 Published test message")
        
        time.sleep(5)
        client.loop_stop()
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing MQTT connectivity...")
    test_mqtt()