import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "database", "iot_shield.db")


def get_setting(key):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT value FROM settings WHERE key = ?",
        (key,)
    )

    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None


def set_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
    """, (key, value))

    conn.commit()
    conn.close()


def get_all_settings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT key, value FROM settings")

    settings = {
        row[0]: row[1]
        for row in cursor.fetchall()
    }

    conn.close()

    return settings