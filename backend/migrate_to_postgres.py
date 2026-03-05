import sqlite3
import psycopg2
from psycopg2.extras import execute_values

# Connect to SQLite
sqlite_conn = sqlite3.connect('/home/saniyachavani/Documents/Precision_Pulse/backend/instance/precision_pulse.db')
sqlite_cursor = sqlite_conn.cursor()

# Get data from SQLite
sqlite_cursor.execute('SELECT * FROM users')
users = sqlite_cursor.fetchall()

# Connect to PostgreSQL
try:
    pg_conn = psycopg2.connect(
        host='localhost',
        database='precision_pulse',
        user='postgres',
        password='postgres'
    )
    pg_cursor = pg_conn.cursor()
    
    # Create table
    pg_cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(120) UNIQUE NOT NULL,
            name VARCHAR(120) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'user',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert data
    for user in users:
        pg_cursor.execute('''
            INSERT INTO users (id, email, name, password_hash, role, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        ''', user)
    
    pg_conn.commit()
    print(f"✓ Migrated {len(users)} users to PostgreSQL")
    pg_cursor.close()
    pg_conn.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    print("Make sure PostgreSQL is running and database 'precision_pulse' exists")

sqlite_conn.close()
