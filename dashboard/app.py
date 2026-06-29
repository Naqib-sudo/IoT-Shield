import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, render_template, redirect, url_for, request
from config.config_manager import get_all_settings, set_setting
from notification.email_alert import send_test_email

import sqlite3
import os
import subprocess
import sys

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "database", "iot_shield.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_alerts(filter_type=None):
    conn = get_db_connection()

    if filter_type in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        alerts = conn.execute("""
            SELECT id, timestamp, device_id, topic, attack_type, severity, description, status
            FROM alerts
            WHERE severity = ?
            ORDER BY id DESC
            LIMIT 50
        """, (filter_type,)).fetchall()

    elif filter_type in ["NEW", "ACKNOWLEDGED", "RESOLVED"]:
        alerts = conn.execute("""
            SELECT id, timestamp, device_id, topic, attack_type, severity, description, status
            FROM alerts
            WHERE status = ?
            ORDER BY id DESC
            LIMIT 50
        """, (filter_type,)).fetchall()

    else:
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


def get_chart_data():
    conn = get_db_connection()

    severity_rows = conn.execute("""
        SELECT severity, COUNT(*) as count
        FROM alerts
        GROUP BY severity
    """).fetchall()

    attack_rows = conn.execute("""
        SELECT attack_type, COUNT(*) as count
        FROM alerts
        GROUP BY attack_type
    """).fetchall()

    conn.close()

    severity_data = {
        "labels": [row["severity"] for row in severity_rows],
        "values": [row["count"] for row in severity_rows]
    }

    attack_data = {
        "labels": [row["attack_type"] for row in attack_rows],
        "values": [row["count"] for row in attack_rows]
    }

    return severity_data, attack_data

def get_latest_critical_alert():
    conn = get_db_connection()

    alert = conn.execute("""
        SELECT id, timestamp, device_id, attack_type, severity, description
        FROM alerts
        WHERE severity IN ('HIGH', 'CRITICAL')
        AND status = 'NEW'
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    conn.close()
    return alert

@app.route("/")
def index():
    filter_type = request.args.get("filter")

    alerts = get_alerts(filter_type)
    traffic = get_traffic_logs()
    summary = get_summary()
    severity_data, attack_data = get_chart_data()
    latest_critical_alert = get_latest_critical_alert()
    settings = get_all_settings()
    message = request.args.get("message")

    return render_template(
        "index.html",
        alerts=alerts,
        traffic=traffic,
        summary=summary,
        severity_data=severity_data,
        attack_data=attack_data,
        current_filter=filter_type,
        latest_critical_alert=latest_critical_alert,
        settings=settings,
        message=message
    )


def run_script(script_path):
    full_path = os.path.join(BASE_DIR, script_path)

    print(f"Running script: {full_path}")

    subprocess.Popen(
        [sys.executable, full_path],
        cwd=BASE_DIR
    )

@app.route("/simulate/normal")
def simulate_normal():
    run_script("simulator/normal_publisher.py")
    return redirect(url_for("index") + "#simulation")


@app.route("/simulate/flood")
def simulate_flood():
    run_script("simulator/flood_attack.py")
    return redirect(url_for("index") + "#simulation")


@app.route("/simulate/unauthorized")
def simulate_unauthorized():
    run_script("simulator/unauthorized_topic_attack.py")
    return redirect(url_for("index") + "#simulation")


@app.route("/simulate/abnormal")
def simulate_abnormal():
    run_script("simulator/abnormal_value_attack.py")
    return redirect(url_for("index") + "#simulation")


@app.route("/simulate/malformed")
def simulate_malformed():
    run_script("simulator/malformed_payload_attack.py")
    return redirect(url_for("index") + "#simulation")


@app.route("/alert/<int:alert_id>/acknowledge")
def acknowledge_alert(alert_id):
    conn = get_db_connection()
    conn.execute(
        "UPDATE alerts SET status = ? WHERE id = ?",
        ("ACKNOWLEDGED", alert_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index") + "#alerts")


@app.route("/alert/<int:alert_id>/resolve")
def resolve_alert(alert_id):
    conn = get_db_connection()
    conn.execute(
        "UPDATE alerts SET status = ? WHERE id = ?",
        ("RESOLVED", alert_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index") + "#alerts")


@app.route("/alerts/clear")
def clear_alerts():
    conn = get_db_connection()
    conn.execute("DELETE FROM alerts")
    conn.execute("DELETE FROM traffic_logs")
    conn.commit()
    conn.close()
    return redirect(url_for("index") + "#alerts")


@app.route("/settings/notification", methods=["POST"])
def update_notification_settings():
    recipient_email = request.form.get("recipient_email")

    if recipient_email:
        set_setting("recipient_email", recipient_email)

    return redirect(url_for("index") + "#settings")


@app.route("/settings/test-email")
def test_email_notification():
    success = send_test_email()

    if success:
        return redirect(url_for("index", message="test_email_sent") + "#settings")
    else:
        return redirect(url_for("index", message="test_email_failed") + "#settings")


if __name__ == "__main__":
    app.run(debug=True)