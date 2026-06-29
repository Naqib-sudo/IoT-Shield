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

# Store system configuration/settings
cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
)
""")

# Insert sample known devices
cursor.execute("""
INSERT OR IGNORE INTO devices (device_id, device_name, device_type, status)
VALUES 
('temp_sensor_01', 'Temperature Sensor 01', 'Temperature Sensor', 'ACTIVE'),
('humidity_sensor_01', 'Humidity Sensor 01', 'Humidity Sensor', 'ACTIVE')
""")

# Insert default system settings
default_settings = {
    "recipient_email": "naqib.dp@gmail.com",
    "mqtt_host": "localhost",
    "mqtt_port": "1883",
    "flood_high_threshold": "100",
    "flood_critical_threshold": "200",
    "temperature_threshold": "80"
}

for key, value in default_settings.items():
    cursor.execute("""
        INSERT OR IGNORE INTO settings (key, value)
        VALUES (?, ?)
    """, (key, value))

conn.commit()
conn.close()

print("Database initialized successfully.")