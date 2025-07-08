import os
import json
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
from cryptography.fernet import Fernet
from twilio.rest import Client

# 🔐 Load Firebase credentials from secret
cred_json = os.getenv("FIREBASE_CRED_JSON")
if not cred_json:
    raise ValueError("Missing FIREBASE_CRED_JSON")

cred = credentials.Certificate(json.loads(cred_json))

# ✅ Initialize Firebase with Realtime Database URL
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv('DATABASE_URL')
})

# 🔐 Setup encryption
fernet_key = os.getenv("FERNET_KEY")
fernet = Fernet(fernet_key)

# 🔐 Twilio config
twilio_sid = os.getenv("TWILIO_SID")
twilio_token = os.getenv("TWILIO_TOKEN")
twilio_from = os.getenv("TWILIO_FROM")
client = Client(twilio_sid, twilio_token)


def send_message(phone_number, message):
    print(f"[✔] Sending to {phone_number}: {message}")
    client.messages.create(
        body=message,
        from_=twilio_from,
        to=phone_number
    )


def check_reminders():
    print("[✔] Reminder check started")
    ref = db.reference('customers')
    data = ref.get()

    if not data:
        print("[!] No customer data found.")
        return

    today = datetime.now().date()

    for key, customer in data.items():
        try:
            name = customer['name']
            phone = fernet.decrypt(customer['phone'].encode()).decode()
            buy_date = datetime.strptime(customer['buy_date'], '%Y-%m-%d').date()
            mode = customer['mode']  # 'SMS' or 'WhatsApp'

            # 📅 3-month reminder logic
            months_since = (today.year - buy_date.year) * 12 + (today.month - buy_date.month)
            if months_since % 3 == 0 and today.day == buy_date.day:
                msg = f"Dear {name}, please check your battery water level. - Megamp"
                if mode.lower() == 'sms':
                    send_message(phone, msg)
                elif mode.lower() == 'whatsapp':
                    send_message(f"whatsapp:{phone}", msg)
                else:
                    print(f"[!] Unknown mode for {name}: {mode}")

        except Exception as e:
            print(f"[!] Error processing {key}: {e}")
