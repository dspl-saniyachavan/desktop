#!/usr/bin/env python3
"""
Script to clear all parameters from both PostgreSQL and SQLite databases
while keeping the table structure intact.
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2 import sql

def clear_postgresql_parameters():
    """Clear parameters from PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="precision_pulse_db",
            user="precision_pulse_user",
            password="secure_password_123"
        )
        cursor = conn.cursor()
        
        # Delete all parameters
        cursor.execute("DELETE FROM parameters")
        conn.commit()
        
        # Reset auto-increment sequence
        cursor.execute("ALTER SEQUENCE parameters_id_seq RESTART WITH 1")
        conn.commit()
        
        cursor.close()
        conn.close()
        print("✓ PostgreSQL parameters table cleared")
        
    except Exception as e:
        print(f"✗ Error clearing PostgreSQL parameters: {e}")

def clear_sqlite_parameters():
    """Clear parameters from SQLite database"""
    try:
        # Find SQLite database file in desktop app directory
        sqlite_paths = [
            os.path.expanduser("~/.precisionpulse/app.db"),
            "./dspl-precision-pulse-desktop/data/app.db",
            "./dspl-precision-pulse-desktop/app.db"
        ]
        
        sqlite_path = None
        for path in sqlite_paths:
            if os.path.exists(path):
                sqlite_path = path
                break
                
        if not sqlite_path:
            print("✗ SQLite database not found in expected locations")
            return
            
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Check if parameters table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parameters'")
        if cursor.fetchone():
            # Delete all parameters
            cursor.execute("DELETE FROM parameters")
            conn.commit()
            print(f"✓ SQLite parameters table cleared from {sqlite_path}")
        else:
            print("✓ SQLite parameters table doesn't exist (already empty)")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error clearing SQLite parameters: {e}")

if __name__ == "__main__":
    print("Clearing parameter tables from both databases...")
    print("=" * 50)
    
    clear_postgresql_parameters()
    clear_sqlite_parameters()
    
    print("=" * 50)
    print("Parameter tables cleared. Table structures remain intact.")