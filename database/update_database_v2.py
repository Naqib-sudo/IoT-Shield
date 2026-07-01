import sqlite3

DB_PATH = "database/iot_shield.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

columns = [row[1] for row in cursor.execute("PRAGMA table_info(alerts)").fetchall()]

if "occurrences" not in columns:
    cursor.execute("ALTER TABLE alerts ADD COLUMN occurrences INTEGER DEFAULT 1")

if "first_seen" not in columns:
    cursor.execute("ALTER TABLE alerts ADD COLUMN first_seen TEXT")

if "last_seen" not in columns:
    cursor.execute("ALTER TABLE alerts ADD COLUMN last_seen TEXT")

cursor.execute("""
UPDATE alerts
SET
    occurrences = COALESCE(occurrences,1),
    first_seen = COALESCE(first_seen,timestamp),
    last_seen = COALESCE(last_seen,timestamp)
""")

conn.commit()
conn.close()

print("Database upgraded successfully.")