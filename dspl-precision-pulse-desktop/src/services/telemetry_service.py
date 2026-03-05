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
        self.previous_values = {}  # Track previous values
        self.last_print_time = 0  # Track last print time
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
        
        print(f"📊 Initializing parameters: found {len(enabled_params)} enabled parameters")
        
        # Color palette for parameters
        colors = ['#60a5fa', '#a78bfa', '#c084fc', '#f472b6', '#fb923c', '#34d399', '#fbbf24', '#f87171']
        
        for i, param in enumerate(enabled_params):
            param_id = param['id']
            parameters[param_id] = {
                'id': param_id,
                'name': param['name'],
                'value': 25.0,  # Default starting value
                'unit': param['unit'],
                'min': 0,
                'max': 100,
                'color': colors[i % len(colors)]
            }
            print(f"  ✓ {param['name']} ({param['unit']})")
        
        if not parameters:
            print("⚠️ No parameters found - check backend connection")
        
        return parameters
    
    def start_streaming(self, interval: int = 2):
        """Start streaming telemetry data"""
        print(f"🚀 Starting telemetry streaming (interval: {interval}s)")
        self.is_streaming = True
        
        # Connect to MQTT if not connected
        if not self.mqtt_service.client.is_connected():
            print(f"🔗 Connecting to MQTT broker...")
            self.mqtt_service.connect()
        
        # Ensure we have parameters
        if not self.parameters:
            print(f"🔄 No parameters found, refreshing...")
            self.refresh_parameters()
        
        # Push data every interval seconds
        self.push_timer.timeout.connect(self._push_data)
        self.push_timer.start(interval * 1000)
        
        # Send heartbeat periodically
        self.heartbeat_timer.timeout.connect(self._send_heartbeat)
        self.heartbeat_timer.start(Config.HEARTBEAT_INTERVAL * 1000)
        
        # Generate initial data
        self._generate_data()
        print(f"✅ Telemetry streaming started with {len(self.parameters)} parameters")
        
    def stop_streaming(self):
        """Stop streaming telemetry data"""
        self.is_streaming = False
        self.push_timer.stop()
        self.heartbeat_timer.stop()
        
    def _generate_data(self):
        """Generate simulated sensor data"""
        import time
        current_time = time.time()
        
        # Update all parameter values
        for param_id, param in self.parameters.items():
            # Add small random variation to current value
            variation = (param['max'] - param['min']) * 0.05
            new_value = param['value'] + random.uniform(-variation, variation)
            new_value = max(param['min'], min(param['max'], new_value))
            param['value'] = round(new_value, 2)
        
        # Print all parameters every 3 seconds (same as push interval)
        if current_time - self.last_print_time >= 3:
            param_values = [f"{p['name']}={p['value']}" for p in self.parameters.values()]
            print(f"[DATA] {', '.join(param_values)}")
            self.last_print_time = current_time
            
    def _push_data(self):
        """Push telemetry data to backend"""
        # Ensure we have parameters
        if not self.parameters:
            print(f"[TELEMETRY] No parameters available, skipping data push")
            return
            
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
        
        # Always emit to update UI locally
        self.parameters_updated.emit(self.parameters)
        
        # Try to push via MQTT if connected (check client directly)
        if self.mqtt_service.client.is_connected():
            print(f"[MQTT] 📤 Publishing {len(parameters)} parameters...")
            success = self.mqtt_service.publish_telemetry(parameters)
            if success:
                print(f"[MQTT] ✅ Published telemetry data")
            else:
                print(f"[MQTT] ❌ Failed to publish telemetry")
                self._buffer_data(parameters)
        else:
            print(f"[MQTT] 💾 Not connected - buffering {len(parameters)} parameters")
            self._buffer_data(parameters)
    
    def _buffer_data(self, parameters: List[Dict]):
        """Buffer data to local database when offline"""
        for param in parameters:
            self.db.buffer_telemetry(
                param['id'], 
                param['name'], 
                param['value'], 
                param['unit']
            )
        print(f"[BUFFER] 💾 Stored {len(parameters)} parameters locally")
    
    def _on_mqtt_connected(self):
        """Handle MQTT connection established"""
        self.is_connected = True
        self.connection_status_changed.emit(True)
        print(f"[MQTT] Status: CONNECTED")
        self._sync_buffered_data()
        
        # Refresh parameters after MQTT connection
        self.refresh_parameters()
        
        # Start generating data if we have parameters
        if self.parameters:
            print(f"[TELEMETRY] Starting data generation for {len(self.parameters)} parameters")
            self._generate_data()
        else:
            print(f"[TELEMETRY] No parameters available for data generation")
    
    def _on_mqtt_disconnected(self):
        """Handle MQTT disconnection"""
        self.is_connected = False
        self.connection_status_changed.emit(False)
        print(f"[MQTT] Status: DISCONNECTED - Buffering data locally")
    
    def _sync_buffered_data(self):
        """Sync buffered data after reconnection"""
        buffered = self.db.get_buffered_data()
        if buffered:
            print(f"[SYNC] 🔄 Syncing {len(buffered)} buffered records...")
            
            # Convert buffered data to telemetry format
            parameters = [
                {
                    'id': item['parameter_id'],
                    'name': item['parameter_name'],
                    'value': item['value'],
                    'unit': item['unit']
                }
                for item in buffered
            ]
            
            success = self.mqtt_service.publish_telemetry(parameters)
            if success:
                buffer_ids = [item['id'] for item in buffered]
                self.db.mark_data_synced(buffer_ids)
                self.buffered_data_synced.emit(len(buffered))
                print(f"[SYNC] ✅ Successfully synced {len(buffered)} records")
            else:
                print(f"[SYNC] ❌ Failed to sync buffered data")
    
    def _on_parameter_update(self, param_id: str, new_value: float):
        """Handle parameter update from web"""
        if param_id in self.parameters:
            self.parameters[param_id]['value'] = float(new_value)
            self.parameter_changed.emit(param_id, float(new_value))
    
    def _send_heartbeat(self):
        """Send heartbeat to indicate device is alive"""
        if self.mqtt_service.client.is_connected():
            self.mqtt_service._send_heartbeat()
                        
    def refresh_parameters(self):
        """Refresh parameters from database"""
        old_params = set(self.parameters.keys())
        self.parameters = self._initialize_parameters()
        new_params = set(self.parameters.keys())
        
        # Log added parameters
        added = new_params - old_params
        for param_id in added:
            print(f"[PARAM] Added: {self.parameters[param_id]['name']}")
        
        # Log removed parameters
        removed = old_params - new_params
        for param_id in removed:
            print(f"[PARAM] Removed: {param_id}")
        
        # Always emit signal to update UI
        self.parameters_updated.emit(self.parameters)
        print(f"[PARAM] Refreshed {len(self.parameters)} parameters")
    
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
        self.config_manager.update_config(config_data)
    
    def _apply_config_update(self, key: str, value: str):
        """Apply configuration update to running service"""
        if key == 'TELEMETRY_INTERVAL':
            new_interval = int(value)
            if self.is_streaming:
                self.push_timer.stop()
                self.push_timer.start(new_interval * 1000)
        
        elif key == 'HEARTBEAT_INTERVAL':
            new_interval = int(value)
            if self.is_streaming:
                self.heartbeat_timer.stop()
                self.heartbeat_timer.start(new_interval * 1000)
