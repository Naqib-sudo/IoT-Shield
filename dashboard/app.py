from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'iot_shield.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_alerts():
    conn = get_db_connection()
    alerts = conn.execute("""
        SELECT id, timestamp, device_id, topic, attack_type, severity, description, status
        FROM alerts
        ORDER BY id DESC
        LIMIT 50
    """).fetchall()
    conn.close()
    return alerts


def get_traffic_logs():
    conn = get_db_connection()
    traffic = conn.execute("""
        SELECT id, timestamp, device_id, topic, payload, status
        FROM traffic_logs
        ORDER BY id DESC
        LIMIT 50
    """).fetchall()
    conn.close()
    return traffic


def get_summary():
    conn = get_db_connection()

    total_messages = conn.execute("SELECT COUNT(*) FROM traffic_logs").fetchone()[0]
    total_alerts = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    high_critical_alerts = conn.execute("""
        SELECT COUNT(*) FROM alerts
        WHERE severity IN ('HIGH', 'CRITICAL')
    """).fetchone()[0]
    active_devices = conn.execute("SELECT COUNT(DISTINCT device_id) FROM traffic_logs").fetchone()[0]

    conn.close()

    return {
        "total_messages": total_messages,
        "total_alerts": total_alerts,
        "high_critical_alerts": high_critical_alerts,
        "active_devices": active_devices,
        "system_status": "ONLINE"
    }


@app.route("/")
def index():
    alerts = get_alerts()
    traffic = get_traffic_logs()
    summary = get_summary()

    return render_template(
        "index.html",
        alerts=alerts,
        traffic=traffic,
        summary=summary
    )


if __name__ == "__main__":
    app.run(debug=True)