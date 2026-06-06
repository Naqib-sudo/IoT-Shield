from datetime import datetime
from notification.email_alert import send_email_alert
import sqlite3
import os
import ast

DB_PATH = "database/iot_shield.db"
ALERT_LOG_DIR = "logs/alerts"
os.makedirs(ALERT_LOG_DIR, exist_ok=True)

RESTRICTED_TOPICS = ["admin/control", "system/config"]

FLOOD_HIGH_THRESHOLD = 100
FLOOD_CRITICAL_THRESHOLD = 200

KNOWN_DEVICES = [
    "temp_sensor_01",
    "humidity_sensor_01",
    "attacker_flood_01",
    "attacker_unauthorized_01"
]


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
            description TEXT,
            status TEXT DEFAULT 'NEW'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS traffic_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            device_id TEXT,
            topic TEXT,
            payload TEXT,
            status TEXT DEFAULT 'NORMAL'
        )
    """)

    conn.commit()
    conn.close()


def save_traffic_log(device_id, topic, payload, status="NORMAL"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO traffic_logs (timestamp, device_id, topic, payload, status)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, device_id, topic, payload, status))

    conn.commit()
    conn.close()


def save_alert(device_id, topic, attack_type, severity, description):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alerts (timestamp, device_id, topic, attack_type, severity, description, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, device_id, topic, attack_type, severity, description, "NEW"))

    conn.commit()
    if severity in ["HIGH", "CRITICAL"]:
        send_email_alert(
            subject=f"🚨 IoT-Shield {severity} Alert",
            body=f"""
    Attack Type: {attack_type}

    Severity: {severity}

    Device: {device_id}

    Topic: {topic}

    Description:
    {description}

    Please review the IoT-Shield dashboard immediately.
    """
        )

        
    conn.close()

    log_file = os.path.join(
        ALERT_LOG_DIR,
        f"alerts_{datetime.now().strftime('%Y-%m-%d')}.log"
    )

    with open(log_file, "a") as f:
        f.write(f"{timestamp} | {severity} | {device_id} | {topic} | {attack_type} | {description}\n")

    print(f"[ALERT] {severity} - {attack_type}: {description}")


def parse_payload(payload):
    try:
        data = ast.literal_eval(payload)
        if isinstance(data, dict):
            return data, False
        return {}, True
    except Exception:
        return {}, True


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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    existing_alert = cursor.execute("""
        SELECT id FROM alerts
        WHERE device_id = ?
        AND attack_type = 'MQTT Flooding'
        AND status = 'NEW'
        ORDER BY id DESC
        LIMIT 1
    """, (device_id,)).fetchone()

    conn.close()

    if existing_alert:
        return

    if message_count > FLOOD_CRITICAL_THRESHOLD:
        save_alert(
            device_id=device_id,
            topic=topic,
            attack_type="MQTT Flooding",
            severity="CRITICAL",
            description=f"Device sent {message_count} messages, exceeding critical threshold {FLOOD_CRITICAL_THRESHOLD}"
        )

    elif message_count > FLOOD_HIGH_THRESHOLD:
        save_alert(
            device_id=device_id,
            topic=topic,
            attack_type="MQTT Flooding",
            severity="HIGH",
            description=f"Device sent {message_count} messages, exceeding threshold {FLOOD_HIGH_THRESHOLD}"
        )


def check_abnormal_value(device_id, topic, data):
    if "temperature" in data:
        try:
            temp = float(data["temperature"])
            if temp > 80:
                save_alert(
                    device_id=device_id,
                    topic=topic,
                    attack_type="Abnormal Sensor Value",
                    severity="MEDIUM",
                    description=f"Abnormal temperature detected: {temp}"
                )
        except Exception:
            pass


def check_malformed_payload(device_id, topic, is_malformed):
    if is_malformed:
        save_alert(
            device_id=device_id,
            topic=topic,
            attack_type="Malformed Payload",
            severity="LOW",
            description="Received malformed or unreadable payload"
        )


def check_unknown_device(device_id, topic):
    if device_id not in KNOWN_DEVICES and device_id != "unknown":
        save_alert(
            device_id=device_id,
            topic=topic,
            attack_type="Unknown Device",
            severity="MEDIUM",
            description=f"Message received from unregistered device: {device_id}"
        )


if __name__ == "__main__":
    init_db()
    print("Rule engine upgraded successfully.")