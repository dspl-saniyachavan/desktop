"""
MQTT Service for real-time bidirectional communication
"""

import json
import paho.mqtt.client as mqtt
from PySide6.QtCore import QObject, Signal
from src.core.config import Config
from datetime import datetime


class MQTTService(QObject):
    """Service for MQTT communication"""
    
    # Signals
    connected = Signal()
    disconnected = Signal()
    message_received = Signal(str, dict)
    parameter_update_received = Signal(str, float)
    config_update_received = Signal(dict)
    
    def __init__(self, device_id: str):
        super().__init__()
        self.device_id = device_id
        self.client = mqtt.Client(client_id=f"desktop_{device_id}")
        self.is_connected = False
        
        # Setup callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Configure TLS if needed
        if Config.MQTT_USE_TLS:
            self.client.tls_set()
        
        # Set credentials if provided
        if Config.MQTT_USERNAME and Config.MQTT_PASSWORD:
            self.client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)
        
        # Device-specific topics for backend compatibility
        self.telemetry_topic = f"precisionpulse/{device_id}/telemetry"
        self.command_topic = f"precisionpulse/{device_id}/command"
        self.heartbeat_topic = f"precisionpulse/{device_id}/heartbeat"
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(Config.MQTT_BROKER, Config.MQTT_PORT, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"MQTT connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker"""
        if rc == 0:
            print(f"Connected to MQTT broker")
            self.is_connected = True
            self.connected.emit()
            
            # Subscribe to device-specific command topic
            self.client.subscribe(self.command_topic)
            self.client.subscribe(f"{Config.MQTT_TOPIC_COMMANDS}/config/update")
            
            # Subscribe to ALL telemetry and heartbeat topics (for admin to receive from clients)
            self.client.subscribe("precisionpulse/+/telemetry")
            self.client.subscribe("precisionpulse/+/heartbeat")
            print(" Subscribed to all client telemetry topics")
            
            # Send heartbeat
            self._send_heartbeat()
        else:
            print(f"MQTT connection failed with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from broker"""
        print(f"Disconnected from MQTT broker")
        self.is_connected = False
        self.disconnected.emit()
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            print(f" MQTT Message - Topic: {topic}")
            print(f"   Payload: {payload}")
            
            # Handle telemetry from other clients
            if "telemetry" in topic and topic != self.telemetry_topic:
                print(f"Received telemetry from {payload.get('client_id')} on topic {topic}")
                print(f"   My topic: {self.telemetry_topic}")
                # Emit parameter updates so admin dashboard shows remote data
                if 'parameters' in payload:
                    print(f"   Emitting {len(payload['parameters'])} parameter updates")
                    for param in payload['parameters']:
                        print(f"   → {param['id']}: {param['value']}")
                        self.parameter_update_received.emit(param['id'], param['value'])
            
            # Handle parameter updates
            if 'parameters/update' in topic or payload.get('type') == 'parameter_update':
                param_id = payload.get('parameter_id')
                value = payload.get('value')
                if param_id and value is not None:
                    self.parameter_update_received.emit(param_id, float(value))
            
            # Handle configuration updates
            elif 'config/update' in topic or payload.get('type') == 'config_update':
                config_data = payload.get('config', {})
                if config_data:
                    self.config_update_received.emit(config_data)
                    if payload.get('command_id'):
                        self.acknowledge_command(payload['command_id'])
            
            # Emit general message
            self.message_received.emit(topic, payload)
            
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
    
    def publish_telemetry(self, parameters: list) -> bool:
        """Publish telemetry data"""
        if not self.is_connected:
            print(" Cannot publish: MQTT not connected")
            return False
        
        try:
            payload = {
                'client_id': self.device_id,
                'timestamp': datetime.utcnow().isoformat(),
                'parameters': parameters
            }
            
            print(f" Publishing to topic: {self.telemetry_topic}")
            print(f"   Device ID: {self.device_id}")
            print(f"   Parameters: {len(parameters)}")
            
            result = self.client.publish(
                self.telemetry_topic,
                json.dumps(payload),
                qos=1
            )
            
            success = result.rc == mqtt.MQTT_ERR_SUCCESS
            print(f"   Result: {' Success' if success else f' Failed (rc={result.rc})'}")
            return success
        except Exception as e:
            print(f"Error publishing telemetry: {e}")
            return False
    
    def publish_buffered_data(self, buffered_data: list) -> bool:
        """Publish buffered historical data"""
        if not self.is_connected:
            return False
        
        try:
            payload = {
                'device_id': self.device_id,
                'type': 'buffered_sync',
                'data': buffered_data
            }
            
            result = self.client.publish(
                f"{Config.MQTT_TOPIC_SYNC}/buffered",
                json.dumps(payload),
                qos=2  # Exactly once delivery
            )
            
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"Error publishing buffered data: {e}")
            return False
    
    def acknowledge_command(self, command_id: str) -> bool:
        """Acknowledge received command"""
        if not self.is_connected:
            return False
        
        try:
            payload = {
                'device_id': self.device_id,
                'command_id': command_id,
                'status': 'acknowledged',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
            result = self.client.publish(
                f"{Config.MQTT_TOPIC_COMMANDS}/ack",
                json.dumps(payload),
                qos=1
            )
            
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"Error acknowledging command: {e}")
            return False
    
    def _send_heartbeat(self):
        """Send heartbeat to indicate device is online"""
        if not self.is_connected:
            return
        
        try:
            payload = {
                'client_id': self.device_id,
                'status': 'online',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.client.publish(
                self.heartbeat_topic,
                json.dumps(payload),
                qos=1
            )
        except Exception as e:
            print(f"Error sending heartbeat: {e}")
