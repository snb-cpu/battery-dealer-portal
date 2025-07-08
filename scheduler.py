import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pytz
import json
from encrypt_util import decrypt
from twilio.rest import Client

# --- ENV Variables ---
firebase_cred_json = os.environ.get("FIREBASE_CRED_JSON")
fernet_key = os.environ.get("FERNET_KEY")
twilio_sid = os.environ.get("TWILIO_SID")
twilio_token = os.environ.get("TWILIO_TOKEN")
twilio_from = os.environ.get("TWILIO_FROM")

if not firebase_cred_json:
    raise ValueError("Missing FIREBASE_CRED_JSON")

# --- Firebase Init ---
cred_dict = json.loads(firebase_cred_json)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Timezone ---
india_tz = pytz.timezone("Asia/Kolkata")
today = datetime.now(india_tz).date()

def send_sms(to, body):
    client = Client(twilio_sid, twilio_token)
    client.messages.create(body=body, from_=twilio_from, to=to)
    print(f"[+] SMS sent to {to}")

def send_whatsapp(to, body):
    if not to.startswith("whatsapp:"):
        to = f"whatsapp:{to}"
    client = Client(twilio_sid, twilio_token)
    client.messages.create(body=body, from_=f"whatsapp:{twilio_from}", to=to)
    print(f"[+] WhatsApp sent to {to}")

def get_users():
    return [doc.to_dict() for doc in db.collection("users").stream()]

def check_reminders():
    users = get_users()
    for user in users:
        name = user.get("name", "Unknown")
        phone = user.get("phone")
        date_str = user.get("battery_date")
        mode = user.get("mode", "SMS")
        encrypted = user.get("encrypted", True)

        if not phone or not date_str:
            print(f"[-] Skipping incomplete: {name}")
            continue

        try:
            if encrypted:
                phone = decrypt(phone, fernet_key)
                date_str = decrypt(date_str, fernet_key)
            battery_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception as e:
            print(f"[!] Error parsing user {name}: {e}")
            continue

        if (today - battery_date).days % 90 == 0:
            msg = f"Reminder: Check battery water registered on {date_str}"
            try:
                if mode.lower() == "sms":
                    send_sms(phone, msg)
                elif mode.lower() == "whatsapp":
                    send_whatsapp(phone, msg)
                else:
                    print(f"[!] Unknown mode {mode} for {name}")
            except Exception as e:
                print(f"[!] Failed sending to {name}: {e}")

if __name__ == "__main__":
    check_reminders()
