import sqlite3
import os

DB_PATH = "database/iot_shield.db"

os.makedirs("database", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Store all MQTT traffic messages
cursor.execute("""
CREATE TABLE IF NOT EXISTS traffic_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    device_id TEXT,
    topic TEXT,
    payload TEXT,
    status TEXT DEFAULT 'NORMAL'
)
""")

# Store detected security alerts
cursor.execute("""
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    device_id TEXT,
    topic TEXT,
    attack_type TEXT,
    severity TEXT,
    description TEXT,
    status TEXT DEFAULT 'NEW'
)
""")

# Store registered / known IoT devices
cursor.execute("""
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT UNIQUE,
    device_name TEXT,
    device_type TEXT,
    status TEXT DEFAULT 'ACTIVE'
)
""")

# Insert sample known devices
cursor.execute("""
INSERT OR IGNORE INTO devices (device_id, device_name, device_type, status)
VALUES 
('temp_sensor_01', 'Temperature Sensor 01', 'Temperature Sensor', 'ACTIVE'),
('humidity_sensor_01', 'Humidity Sensor 01', 'Humidity Sensor', 'ACTIVE')
""")

conn.commit()
conn.close()

print("Database initialized successfully.")