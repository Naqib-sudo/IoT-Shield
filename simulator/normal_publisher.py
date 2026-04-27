import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "home/temperature"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

print("Normal IoT temperature sensor started...")
print("Publishing normal temperature data every 5 seconds.")

while True:
    temperature = round(random.uniform(25.0, 32.0), 2)
    payload = {
        "device": "temp_sensor_01",
        "temperature": temperature,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    message = str(payload)
    client.publish(TOPIC, message)

    print(f"[NORMAL] Published to {TOPIC}: {message}")
    time.sleep(5)