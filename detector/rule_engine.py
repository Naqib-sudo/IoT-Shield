from datetime import datetime
import sqlite3
import os

DB_PATH = "database/iot_shield.db"
ALERT_LOG_DIR = "logs/alerts"
os.makedirs(ALERT_LOG_DIR, exist_ok=True)

RESTRICTED_TOPICS = ["admin/control", "system/config"]
FLOOD_THRESHOLD = 100

def init_db():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            device_id TEXT,
            topic TEXT,
            attack_type TEXT,
            severity TEXT,
            description TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_alert(device_id, topic, attack_type, severity, description):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alerts (timestamp, device_id, topic, attack_type, severity, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, device_id, topic, attack_type, severity, description))

    conn.commit()
    conn.close()

    log_file = os.path.join(
        ALERT_LOG_DIR,
        f"alerts_{datetime.now().strftime('%Y-%m-%d')}.log"
    )

    with open(log_file, "a") as f:
        f.write(f"{timestamp} | {severity} | {device_id} | {topic} | {attack_type} | {description}\n")

    print(f"[ALERT] {severity} - {attack_type}: {description}")


def check_unauthorized_topic(device_id, topic):
    if topic in RESTRICTED_TOPICS:
        save_alert(
            device_id=device_id,
            topic=topic,
            attack_type="Unauthorized Topic Access",
            severity="HIGH",
            description=f"Device published to restricted topic: {topic}"
        )

def check_flooding(device_id, topic, message_count):
    if message_count > FLOOD_THRESHOLD:
        save_alert(
            device_id=device_id,
            topic=topic,
            attack_type="MQTT Flooding",
            severity="HIGH",
            description=f"Device sent {message_count} messages, exceeding threshold {FLOOD_THRESHOLD}"
        )

if __name__ == "__main__":
    init_db()

    print("Testing rule engine...")

    check_unauthorized_topic("attacker_01", "admin/control")
    check_flooding("attacker_01", "home/temperature", 150)

    print("Rule engine test completed.")