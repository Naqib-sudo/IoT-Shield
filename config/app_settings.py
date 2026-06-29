import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SETTINGS_PATH = os.path.join(BASE_DIR, "config", "settings.json")


def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        return {
            "recipient_email": "naqib.dp@gmail.com"
        }

    with open(SETTINGS_PATH, "r") as file:
        return json.load(file)


def save_settings(settings):
    with open(SETTINGS_PATH, "w") as file:
        json.dump(settings, file, indent=4)


def get_recipient_email():
    settings = load_settings()
    return settings.get("recipient_email", "naqib.dp@gmail.com")


def update_recipient_email(email):
    settings = load_settings()
    settings["recipient_email"] = email
    save_settings(settings)