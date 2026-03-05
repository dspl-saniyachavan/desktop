"""
Database manager for local SQLite operations
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from argon2 import PasswordHasher
from src.core.config import Config

class DatabaseManager:
    """Manages local SQLite database operations"""
    
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.ph = PasswordHasher()
        
    def initialize_database(self):
        """Initialize database with required tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Telemetry buffer table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS telemetry_buffer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parameter_id TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    synced BOOLEAN DEFAULT 0
                )
            ''')
            
            # Configuration table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Parameters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parameters (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    unit TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    description TEXT
                )
            ''')
            
            # Permissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    action TEXT NOT NULL,
                    allowed BOOLEAN DEFAULT 1,
                    UNIQUE(role, resource, action)
                )
            ''')
            
            conn.commit()
            self._create_default_data()
    
    def _create_default_data(self):
        """Create default users and parameters"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if admin user exists
            cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('admin@precisionpulse.com',))
            if cursor.fetchone()[0] == 0:
                admin_hash = self.ph.hash('admin123')
                cursor.execute('''
                    INSERT INTO users (email, name, password_hash, role)
                    VALUES (?, ?, ?, ?)
                ''', ('admin@precisionpulse.com', 'Admin User', admin_hash, 'admin'))
            
            # Check if client user exists
            cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('client@precisionpulse.com',))
            if cursor.fetchone()[0] == 0:
                client_hash = self.ph.hash('client123')
                cursor.execute('''
                    INSERT INTO users (email, name, password_hash, role)
                    VALUES (?, ?, ?, ?)
                ''', ('client@precisionpulse.com', 'Client User', client_hash, 'client'))
            
            # Check if regular user exists
            cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('user@precisionpulse.com',))
            if cursor.fetchone()[0] == 0:
                user_hash = self.ph.hash('user123')
                cursor.execute('''
                    INSERT INTO users (email, name, password_hash, role)
                    VALUES (?, ?, ?, ?)
                ''', ('user@precisionpulse.com', 'Regular User', user_hash, 'user'))
            
            # Default parameters
            default_params = [
                ('temp', 'Temperature', '°C', 'Ambient temperature sensor'),
                ('pressure', 'Pressure', 'kPa', 'System pressure measurement'),
                ('flow', 'Flow Rate', 'L/s', 'Liquid flow rate'),
                ('humidity', 'Humidity', '%', 'Relative humidity'),
                ('voltage', 'Voltage', 'V', 'System voltage'),
                ('current', 'Current', 'A', 'System current')
            ]
            
            for param_id, name, unit, description in default_params:
                cursor.execute('''
                    INSERT OR IGNORE INTO parameters (id, name, unit, description)
                    VALUES (?, ?, ?, ?)
                ''', (param_id, name, unit, description))
            
            # Default permissions
            default_permissions = [
                # Admin - full access
                ('admin', 'users', 'read'), ('admin', 'users', 'write'),
                ('admin', 'roles', 'read'), ('admin', 'roles', 'write'),
                ('admin', 'config', 'read'), ('admin', 'config', 'write'),
                ('admin', 'parameters', 'read'), ('admin', 'parameters', 'write'),
                ('admin', 'livedata', 'read'), ('admin', 'livedata', 'write'),
                ('admin', 'reports', 'read'), ('admin', 'reports', 'export'),
                ('admin', 'web', 'login'), ('admin', 'desktop', 'login'),
                
                # Client - data sending and config reading
                ('client', 'config', 'read'), ('client', 'parameters', 'read'),
                ('client', 'livedata', 'write'), ('client', 'desktop', 'login'),
                
                # User - viewing only
                ('user', 'livedata', 'read'), ('user', 'reports', 'read'),
                ('user', 'web', 'login'), ('user', 'desktop', 'login'),
            ]
            
            for role, resource, action in default_permissions:
                cursor.execute('''
                    INSERT OR IGNORE INTO permissions (role, resource, action, allowed)
                    VALUES (?, ?, ?, 1)
                ''', (role, resource, action))
            
            conn.commit()
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user credentials"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, email, name, password_hash, role, is_active
                FROM users WHERE email = ? AND is_active = 1
            ''', (email,))
            
            user = cursor.fetchone()
            if user:
                try:
                    self.ph.verify(user[3], password)
                    return {
                        'id': user[0],
                        'email': user[1],
                        'name': user[2],
                        'role': user[4]
                    }
                except:
                    return None
            return None
    
    def get_enabled_parameters(self) -> List[Dict]:
        """Get all enabled parameters"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, unit, description
                FROM parameters WHERE enabled = 1
            ''')
            
            return [
                {'id': row[0], 'name': row[1], 'unit': row[2], 'description': row[3]}
                for row in cursor.fetchall()
            ]
    
    def buffer_telemetry(self, parameter_id: str, value: float):
        """Buffer telemetry data when offline"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO telemetry_buffer (parameter_id, value)
                VALUES (?, ?)
            ''', (parameter_id, value))
            conn.commit()
    
    def get_buffered_data(self) -> List[Dict]:
        """Get all unsynced buffered data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, parameter_id, value, timestamp
                FROM telemetry_buffer WHERE synced = 0
                ORDER BY timestamp ASC
            ''')
            
            return [
                {
                    'id': row[0],
                    'parameter_id': row[1],
                    'value': row[2],
                    'timestamp': row[3]
                }
                for row in cursor.fetchall()
            ]
    
    def mark_data_synced(self, buffer_ids: List[int]):
        """Mark buffered data as synced"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(buffer_ids))
            cursor.execute(f'''
                UPDATE telemetry_buffer 
                SET synced = 1 
                WHERE id IN ({placeholders})
            ''', buffer_ids)
            conn.commit()
    
    def clear_synced_data(self):
        """Clear old synced data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM telemetry_buffer 
                WHERE synced = 1 AND timestamp < datetime('now', '-1 day')
            ''')
            conn.commit()
    
    def check_permission(self, role: str, resource: str, action: str) -> bool:
        """Check if role has permission for resource action"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT allowed FROM permissions
                WHERE role = ? AND resource = ? AND action = ?
            ''', (role, resource, action))
            result = cursor.fetchone()
            return result[0] == 1 if result else False