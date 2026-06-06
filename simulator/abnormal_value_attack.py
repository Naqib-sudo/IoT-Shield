from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "home/temperature"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

payload = {
    "device": "temp_sensor_01",
    "temperature": 999,
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

client.publish(TOPIC, str(payload))

print("[ABNORMAL VALUE ATTACK] Published abnormal temperature value: 999")