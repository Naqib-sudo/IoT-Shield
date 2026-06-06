from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "home/temperature"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

# intentionally broken / malformed payload
payload = "{device: temp_sensor_01, temperature: "

client.publish(TOPIC, payload)

print("[MALFORMED PAYLOAD ATTACK] Published malformed payload.")