"""
Telemetry Service for parameter management and synchronization
"""

import random
from typing import Dict, List
from PySide6.QtCore import QObject, QTimer, Signal
from src.core.config import Config, ConfigManager


class TelemetryService(QObject):
    """Service for managing telemetry data and synchronization"""
    
    # Signals
    parameters_updated = Signal(dict)
    parameter_changed = Signal(str, float)
    connection_status_changed = Signal(bool)
    buffered_data_synced = Signal(int)
    
    def __init__(self, mqtt_service, database_manager):
        super().__init__()
        self.mqtt_service = mqtt_service
        self.db = database_manager
        self.config_manager = ConfigManager()
        self.parameters = self._initialize_parameters()
        self.push_timer = QTimer()
        self.heartbeat_timer = QTimer()
        self.is_streaming = False
        self.is_connected = False
        
        # Connect MQTT signals
        self.mqtt_service.connected.connect(self._on_mqtt_connected)
        self.mqtt_service.disconnected.connect(self._on_mqtt_disconnected)
        self.mqtt_service.parameter_update_received.connect(self._on_parameter_update)
        self.mqtt_service.config_update_received.connect(self._on_config_update)
        
        # Connect config manager signals
        self.config_manager.config_updated.connect(self._apply_config_update)
        
    def _initialize_parameters(self) -> Dict:
        """Initialize parameters from database"""
        enabled_params = self.db.get_enabled_parameters()
        parameters = {}
        
        # Default values and colors for parameters
        defaults = {
            'temp': {'value': 27.4, 'min': 20, 'max': 35, 'color': '#60a5fa'},
            'pressure': {'value': 21.5, 'min': 15, 'max': 30, 'color': '#a78bfa'},
            'flow': {'value': 35.8, 'min': 30, 'max': 45, 'color': '#c084fc'},
            'humidity': {'value': 26.5, 'min': 20, 'max': 35, 'color': '#f472b6'},
            'voltage': {'value': 26.8, 'min': 20, 'max': 35, 'color': '#fb923c'},
            'custom': {'value': 44.6, 'min': 35, 'max': 55, 'color': '#34d399'},
        }
        
        # Color palette for new parameters
        colors = ['#60a5fa', '#a78bfa', '#c084fc', '#f472b6', '#fb923c', '#34d399', '#fbbf24', '#f87171']
        
        for i, param in enumerate(enabled_params):
            param_id = param['id']
            default = defaults.get(param_id, {'value': 25.0, 'min': 0, 'max': 100, 'color': colors[i % len(colors)]})
            parameters[param_id] = {
                'id': param_id,
                'name': param['name'],
                'value': default['value'],
                'unit': param['unit'],
                'min': default['min'],
                'max': default['max'],
                'color': default['color']
            }
        
        return parameters
    
    def start_streaming(self, interval: int = 2):
        """Start streaming telemetry data"""
        self.is_streaming = True
        
        # Connect to MQTT if not connected
        if not self.mqtt_service.is_connected:
            self.mqtt_service.connect()
        
        # Push data every interval seconds
        self.push_timer.timeout.connect(self._push_data)
        self.push_timer.start(interval * 1000)
        
        # Send heartbeat periodically
        self.heartbeat_timer.timeout.connect(self._send_heartbeat)
        self.heartbeat_timer.start(Config.HEARTBEAT_INTERVAL * 1000)
        
        # Generate initial data
        self._generate_data()
        
    def stop_streaming(self):
        """Stop streaming telemetry data"""
        self.is_streaming = False
        self.push_timer.stop()
        self.heartbeat_timer.stop()
        
    def _generate_data(self):
        """Generate simulated sensor data"""
        for param_id, param in self.parameters.items():
            # Add small random variation to current value
            variation = (param['max'] - param['min']) * 0.05
            new_value = param['value'] + random.uniform(-variation, variation)
            new_value = max(param['min'], min(param['max'], new_value))
            param['value'] = round(new_value, 2)
            
    def _push_data(self):
        """Push telemetry data to backend"""
        self._generate_data()
        
        # Prepare data for transmission
        parameters = [
            {
                'id': p['id'],
                'name': p['name'],
                'value': p['value'],
                'unit': p['unit']
            }
            for p in self.parameters.values()
        ]
        
        print(f" Pushing {len(parameters)} parameters to MQTT...")
        
        # Try to push via MQTT
        if self.mqtt_service.is_connected:
            success = self.mqtt_service.publish_telemetry(parameters)
            if success:
                print(f" Telemetry published successfully")
                self.parameters_updated.emit(self.parameters)
            else:
                print(f" Failed to publish telemetry, buffering...")
                # Buffer data if publish fails
                self._buffer_data(parameters)
        else:
            print(f" MQTT not connected, buffering data...")
            # Buffer data when offline
            self._buffer_data(parameters)
    
    def _buffer_data(self, parameters: List[Dict]):
        """Buffer data to local database when offline"""
        for param in parameters:
            self.db.buffer_telemetry(param['id'], param['value'])
        print(f"Buffered {len(parameters)} parameters to local database")
    
    def _on_mqtt_connected(self):
        """Handle MQTT connection established"""
        self.is_connected = True
        self.connection_status_changed.emit(True)
        print("MQTT connected - syncing buffered data...")
        self._sync_buffered_data()
    
    def _on_mqtt_disconnected(self):
        """Handle MQTT disconnection"""
        self.is_connected = False
        self.connection_status_changed.emit(False)
        print("MQTT disconnected - buffering data locally")
    
    def _sync_buffered_data(self):
        """Sync buffered data after reconnection"""
        buffered = self.db.get_buffered_data()
        if buffered:
            print(f"Syncing {len(buffered)} buffered records...")
            success = self.mqtt_service.publish_buffered_data(buffered)
            if success:
                buffer_ids = [item['id'] for item in buffered]
                self.db.mark_data_synced(buffer_ids)
                self.buffered_data_synced.emit(len(buffered))
                print(f"Successfully synced {len(buffered)} buffered records")
    
    def _on_parameter_update(self, param_id: str, new_value: float):
        """Handle parameter update from web"""
        if param_id in self.parameters:
            print(f"Received parameter update: {param_id} = {new_value}")
            self.parameters[param_id]['value'] = float(new_value)
            self.parameter_changed.emit(param_id, float(new_value))
    
    def _send_heartbeat(self):
        """Send heartbeat to indicate device is alive"""
        if self.mqtt_service.is_connected:
            self.mqtt_service._send_heartbeat()
                        
    def refresh_parameters(self):
        """Refresh parameters from database"""
        self.parameters = self._initialize_parameters()
        self.parameters_updated.emit(self.parameters)
    
    def get_parameters(self) -> Dict:
        """Get current parameters"""
        return self.parameters
    
    def get_parameter(self, param_id: str) -> Dict:
        """Get specific parameter"""
        return self.parameters.get(param_id)
    
    def set_parameter_value(self, param_id: str, value: float):
        """Manually set parameter value"""
        if param_id in self.parameters:
            self.parameters[param_id]['value'] = value
            self.parameter_changed.emit(param_id, value)
    
    def _on_config_update(self, config_data: dict):
        """Handle configuration update from remote command"""
        print(f"Received config update: {config_data}")
        self.config_manager.update_config(config_data)
    
    def _apply_config_update(self, key: str, value: str):
        """Apply configuration update to running service"""
        if key == 'TELEMETRY_INTERVAL':
            new_interval = int(value)
            if self.is_streaming:
                self.push_timer.stop()
                self.push_timer.start(new_interval * 1000)
                print(f"Updated telemetry interval to {new_interval} seconds")
        
        elif key == 'HEARTBEAT_INTERVAL':
            new_interval = int(value)
            if self.is_streaming:
                self.heartbeat_timer.stop()
                self.heartbeat_timer.start(new_interval * 1000)
                print(f"Updated heartbeat interval to {new_interval} seconds")
