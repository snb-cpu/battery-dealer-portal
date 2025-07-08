import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import pytz
import json
from encrypt_util import decrypt

# --- Load environment variables ---
firebase_cred_json = os.environ.get("FIREBASE_CRED_JSON")
fernet_key = os.environ.get("FERNET_KEY")
twilio_sid = os.environ.get("TWILIO_SID")
twilio_token = os.environ.get("TWILIO_TOKEN")
twilio_from = os.environ.get("TWILIO_FROM")

if not firebase_cred_json:
    raise ValueError("Missing FIREBASE_CRED_JSON")

# --- Initialize Firebase ---
cred_dict = json.loads(firebase_cred_json)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Timezone and current date ---
india_tz = pytz.timezone("Asia/Kolkata")
now = datetime.now(india_tz)
today = now.date()

# --- Load users from Firebase ---
def get_users():
    users_ref = db.collection("users")
    return [doc.to_dict() for doc in users_ref.stream()]

# --- Check and generate reminders ---
def check_reminders():
    users = get_users()
    for user in users:
        name = user.get("name", "Unknown")
        phone = user.get("phone")
        battery_date_str = user.get("battery_date")
        mode = user.get("mode", "SMS")
        encrypted = user.get("encrypted", True)

        if not phone or not battery_date_str:
            print(f"[-] Skipping incomplete user: {name}")
            continue

        if encrypted:
            try:
                phone = decrypt(phone, fernet_key)
                battery_date_str = decrypt(battery_date_str, fernet_key)
            except Exception as e:
                print(f"[!] Failed to decrypt for {name}: {e}")
                continue

        try:
            battery_date = datetime.strptime(battery_date_str, "%Y-%m-%d").date()
        except:
            print(f"[!] Invalid date for {name}: {battery_date_str}")
            continue

        # Reminder every 3 months
        delta = (today - battery_date).days
        if delta % 90 == 0:
            message = f"Reminder: Check water level of battery registered on {battery_date_str}."
            if mode == "SMS":
                send_sms(phone, message)
            elif mode == "WhatsApp":
                send_whatsapp(phone, message)
            else:
                print(f"[!] Unknown mode for {name}: {mode}")

# --- Twilio message functions ---
from twilio.rest import Client

def send_sms(to, body):
    client = Client(twilio_sid, twilio_token)
    try:
        client.messages.create(body=body, from_=twilio_from, to=to)
        print(f"[+] SMS sent to {to}")
    except Exception as e:
        print(f"[!] SMS failed to {to}: {e}")

def send_whatsapp(to, body):
    if not to.startswith("whatsapp:"):
        to = f"whatsapp:{to}"
    client = Client(twilio_sid, twilio_token)
    try:
        client.messages.create(body=body, from_=f"whatsapp:{twilio_from}", to=to)
        print(f"[+] WhatsApp sent to {to}")
    except Exception as e:
        print(f"[!] WhatsApp failed to {to}: {e}")

# --- Run if called directly ---
if __name__ == "__main__":
    check_reminders()
