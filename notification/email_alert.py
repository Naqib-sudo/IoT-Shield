import smtplib
from email.message import EmailMessage

SENDER_EMAIL = "iotshieldproject@gmail.com"
APP_PASSWORD = "eytd qbzp bkll xqip"

RECEIVER_EMAIL = "iotshieldproject@gmail.com"


def send_email_alert(subject, body):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL

        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)

        print("[EMAIL] Alert email sent successfully.")

    except Exception as e:
        print(f"[EMAIL ERROR] {e}")