import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import paho.mqtt.client as mqtt
from collections import defaultdict
from datetime import datetime
from detector.rule_engine import init_db, check_unauthorized_topic, check_flooding

BROKER = "localhost"
PORT = 1883

message_count = defaultdict(int)


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe("#")  # subscribe to ALL topics


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    device_id = "unknown"

    # Simple way to extract device_id from payload
    if "device" in payload:
        try:
            device_id = payload.split("'device': '")[1].split("'")[0]
        except:
            device_id = "unknown"

    print(f"[RECEIVED] {topic} -> {payload}")

    # Count messages per device
    message_count[device_id] += 1

    # Check rules
    check_unauthorized_topic(device_id, topic)
    check_flooding(device_id, topic, message_count[device_id])


if __name__ == "__main__":
    init_db()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)

    print("MQTT Listener started...")
    client.loop_forever()