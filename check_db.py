import sqlite3

conn = sqlite3.connect("database/iot_shield.db")
cursor = conn.cursor()

print("=== TABLES ===")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

for table in tables:
    print(table[0])

print("\n=== SETTINGS ===")

cursor.execute("SELECT * FROM settings")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()