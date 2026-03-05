"""
WebSocket Service for receiving real-time updates from backend
"""

import socketio
from PySide6.QtCore import QObject, Signal
import json


class WebSocketService(QObject):
    """Service for WebSocket communication with backend"""
    
    # Signals
    telemetry_received = Signal(dict)
    parameter_update_received = Signal(str, float)
    user_sync_received = Signal(dict)
    config_update_received = Signal(dict)
    connected = Signal()
    disconnected = Signal()
    
    def __init__(self, backend_url: str = "http://localhost:3000"):
        super().__init__()
        self.backend_url = backend_url
        self.sio = socketio.Client()
        self.is_connected = False
        
        # Setup event handlers
        self.sio.on('connect', self._on_connect)
        self.sio.on('disconnect', self._on_disconnect)
        self.sio.on('telemetry', self._on_telemetry)
        self.sio.on('parameter_update', self._on_parameter_update)
        self.sio.on('user_sync', self._on_user_sync)
        self.sio.on('config_update', self._on_config_update)
    
    def connect(self):
        """Connect to WebSocket server"""
        try:
            self.sio.connect(self.backend_url, wait_timeout=5)
            return True
        except Exception as e:
            print(f"WebSocket connection error (backend may not be running): {e}")
            return False
    
    def disconnect(self):
        """Disconnect from WebSocket server"""
        if self.is_connected:
            self.sio.disconnect()
    
    def _on_connect(self):
        """Handle connection"""
        print("WebSocket connected to backend")
        self.is_connected = True
        self.connected.emit()
    
    def _on_disconnect(self):
        """Handle disconnection"""
        print("WebSocket disconnected from backend")
        self.is_connected = False
        self.disconnected.emit()
    
    def _on_telemetry(self, data):
        """Handle incoming telemetry data"""
        try:
            self.telemetry_received.emit(data)
        except Exception as e:
            print(f"Error processing telemetry: {e}")
    
    def _on_parameter_update(self, data):
        """Handle parameter update"""
        try:
            param_id = data.get('parameter_id')
            value = data.get('value')
            if param_id and value is not None:
                self.parameter_update_received.emit(param_id, float(value))
        except Exception as e:
            print(f"Error processing parameter update: {e}")
    
    def _on_user_sync(self, data):
        """Handle user sync"""
        try:
            self.user_sync_received.emit(data)
        except Exception as e:
            print(f"Error processing user sync: {e}")
    
    def _on_config_update(self, data):
        """Handle config update"""
        try:
            self.config_update_received.emit(data)
        except Exception as e:
            print(f"Error processing config update: {e}")
    
    def emit_event(self, event: str, data: dict):
        """Emit event to server"""
        if self.is_connected:
            self.sio.emit(event, data)
