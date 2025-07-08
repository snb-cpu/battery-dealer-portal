import os
import json
from firebase_admin import credentials, initialize_app, db
from datetime import datetime
import pytz

# Load Firebase credentials from environment variable
cred_json = os.getenv("FIREBASE_CRED_JSON")
if not cred_json:
    raise ValueError("Missing FIREBASE_CRED_JSON")

cred_dict = json.loads(cred_json)
cred = credentials.Certificate(cred_dict)

# Firebase Realtime Database URL
database_url = os.getenv("FIREBASE_DB_URL") or "https://battery-dealer-portal.firebaseio.com"

initialize_app(cred, {
    'databaseURL': database_url
})

def check_reminders():
    print("[✔] Reminder check started")

    india_tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(india_tz)

    ref = db.reference('customers')
    customers = ref.get() or {}

    for key, c in customers.items():
        name = c.get("name", "Unknown")
        mode = c.get("mode", "sms")
        phone = c.get("phone", "N/A")
        last_date = c.get("buy_date", "Unknown")

        if mode not in ["sms", "whatsapp"]:
            print(f"[!] Unknown mode for {name}: {mode}")

    print("[✔] Reminder check finished")
