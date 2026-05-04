import time
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

print("Attack traffic simulator started...")

# Attack 1: MQTT flooding
print("Starting MQTT flooding attack...")
for i in range(150):
    payload = {
        "device": "attacker_01",
        "value": i,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    client.publish("home/temperature", str(payload))
    print(f"[ATTACK - FLOOD] Message {i+1} sent")
    time.sleep(0.05)

# Attack 2: Unauthorized topic access
print("Sending unauthorized topic message...")
unauthorized_payload = {
    "device": "attacker_01",
    "command": "turn_off_security",
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

client.publish("admin/control", str(unauthorized_payload))
print("[ATTACK - UNAUTHORIZED TOPIC] Published to admin/control")

print("Attack simulation completed.")