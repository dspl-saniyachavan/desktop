#!/usr/bin/env python3
"""
Simple MQTT broker setup for backend with TLS and WebSocket support
"""

import asyncio
import json
import ssl
from gmqtt import Client as MQTTClient
from gmqtt.mqtt.constants import MQTTv311
import websockets
import threading
from flask_socketio import SocketIO

class SimpleMQTTBroker:
    def __init__(self, socketio: SocketIO = None):
        self.socketio = socketio
        self.clients = {}
        self.mqtt_client = None
        
    async def start_websocket_bridge(self):
        """Start WebSocket server for frontend connections"""
        async def handle_websocket(websocket, path):
            try:
                print(f"✓ WebSocket client connected: {websocket.remote_address}")
                
                # Subscribe to MQTT topics and forward to WebSocket
                client = MQTTClient("websocket_bridge")
                await client.connect('localhost', 1883)
                
                await client.subscribe('precisionpulse/+/telemetry', qos=1)
                await client.subscribe('precisionpulse/+/heartbeat', qos=1)
                
                def on_message(client, topic, payload, qos, properties):
                    asyncio.create_task(self.forward_to_websocket(websocket, topic, payload))
                
                client.on_message = on_message
                
                # Keep connection alive
                await websocket.wait_closed()
                print(f"✗ WebSocket client disconnected: {websocket.remote_address}")
                
            except Exception as e:
                print(f"WebSocket error: {e}")
        
        # Start WebSocket server on port 9001
        start_server = websockets.serve(handle_websocket, "localhost", 9001)
        await start_server
        print("✓ WebSocket bridge started on port 9001")
    
    async def forward_to_websocket(self, websocket, topic, payload):
        """Forward MQTT message to WebSocket"""
        try:
            message = {
                'topic': topic,
                'payload': json.loads(payload.decode('utf-8'))
            }
            await websocket.send(json.dumps(message))
            print(f"📤 Forwarded to WebSocket: {topic}")
        except Exception as e:
            print(f"Error forwarding to WebSocket: {e}")

def start_mqtt_broker():
    """Start MQTT broker with WebSocket bridge"""
    import subprocess
    import os
    
    # Start Mosquitto broker with TLS
    config = """
port 1883
listener 18883
cafile /tmp/ca.crt
certfile /tmp/server.crt
keyfile /tmp/server.key
allow_anonymous true
log_dest stdout
log_type all
"""
    
    with open('/tmp/mosquitto.conf', 'w') as f:
        f.write(config)
    
    # Generate self-signed certificates
    os.system("""
    openssl genrsa -out /tmp/ca.key 2048 2>/dev/null
    openssl req -new -x509 -days 365 -key /tmp/ca.key -out /tmp/ca.crt -subj "/C=US/ST=CA/L=SF/O=PrecisionPulse/CN=localhost" 2>/dev/null
    openssl genrsa -out /tmp/server.key 2048 2>/dev/null
    openssl req -new -key /tmp/server.key -out /tmp/server.csr -subj "/C=US/ST=CA/L=SF/O=PrecisionPulse/CN=localhost" 2>/dev/null
    openssl x509 -req -in /tmp/server.csr -CA /tmp/ca.crt -CAkey /tmp/ca.key -CAcreateserial -out /tmp/server.crt -days 365 2>/dev/null
    """)
    
    # Start Mosquitto
    subprocess.Popen(['mosquitto', '-c', '/tmp/mosquitto.conf'])
    print("✓ MQTT broker started on ports 1883 (plain) and 18883 (TLS)")

if __name__ == "__main__":
    start_mqtt_broker()
    
    # Start WebSocket bridge
    broker = SimpleMQTTBroker()
    asyncio.run(broker.start_websocket_bridge())