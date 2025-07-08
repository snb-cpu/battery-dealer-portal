import os
from dotenv import load_dotenv
load_dotenv()

import firebase_admin
from firebase_admin import credentials, db
from twilio.rest import Client
from datetime import datetime
from encrypt_util import decrypt

if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("FIREBASE_CRED_PATH"))
    firebase_admin.initialize_app(cred, {'databaseURL': os.getenv("DATABASE_URL")})

def send_sms(phone, message):
    try:
        client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))
        client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_FROM"),
            to="+91"+phone.strip()
        )
        print(f"[✔] SMS sent to {phone}")
    except Exception as e:
        print(f"[X] SMS failed to {phone}: {e}")

def check_reminders():
    print("[✔] Reminder check started")
    today = datetime.today().date()
    for key, c in (db.reference('customers').get() or {}).items():
        try:
            name = decrypt(c['name'])
            phone = decrypt(c['phone'])
            method = c['method']
            d = datetime.strptime(c['purchase_date'], "%Y-%m-%d").date()
            days = (today-d).days
            print(f"[Debug] {name}: {days} days")
            if days>0 and days%90==0:
                msg = f"Dear {name}, time to check water in your battery."
                if method=="sms":
                    send_sms(phone, msg)
            if days>=730:
                db.reference('customers').child(key).delete()
                print(f"[🗑️] Deleted: {name}")
        except Exception as e:
            print(f"[!] {e}, key={key}")

if __name__=="__main__":
    check_reminders()