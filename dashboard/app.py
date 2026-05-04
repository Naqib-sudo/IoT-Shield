from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'iot_shield.db')


def get_alerts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT timestamp, device_id, topic, attack_type, severity FROM alerts ORDER BY id DESC")
    data = cursor.fetchall()

    conn.close()
    return data


@app.route("/")
def index():
    alerts = get_alerts()
    return render_template("index.html", alerts=alerts)


if __name__ == "__main__":
    app.run(debug=True)