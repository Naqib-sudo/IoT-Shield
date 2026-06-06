import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import paho.mqtt.client as mqtt
from collections import defaultdict
from datetime import datetime
from detector.rule_engine import (
    init_db,
    save_traffic_log,
    parse_payload,
    check_unauthorized_topic,
    check_flooding,
    check_abnormal_value,
    check_malformed_payload,
    check_unknown_device
)

BROKER = "localhost"
PORT = 1883

message_count = defaultdict(int)


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe("#")  # subscribe to ALL topics


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode(errors="ignore")

    data, is_malformed = parse_payload(payload)

    device_id = data.get("device", "unknown")

    print(f"[RECEIVED] {topic} -> {payload}")

    message_count[device_id] += 1

    save_traffic_log(device_id, topic, payload, status="RECEIVED")

    check_malformed_payload(device_id, topic, is_malformed)

    if not is_malformed:
        check_unknown_device(device_id, topic)
        check_unauthorized_topic(device_id, topic)
        check_abnormal_value(device_id, topic, data)

    check_flooding(device_id, topic, message_count[device_id])


if __name__ == "__main__":
    init_db()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)

    print("MQTT Listener started...")

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nMQTT Listener stopped by user.")
        client.disconnect()