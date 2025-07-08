from textwrap import dedent

# Full corrected scheduler.py content with consistent indentation (spaces only)
scheduler_py_content = dedent("""
    import os
    import firebase_admin
    from firebase_admin import credentials, db
    from datetime import datetime, timedelta
    import pytz
    from encrypt_util import decrypt_string
    from twilio.rest import Client

    # Load environment variables
    FIREBASE_CRED_JSON = os.getenv("FIREBASE_CRED_JSON")
    FERNET_KEY = os.getenv("FERNET_KEY")
    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
    TWILIO_FROM = os.getenv("TWILIO_FROM")

    if not FIREBASE_CRED_JSON:
        raise ValueError("Missing FIREBASE_CRED_JSON")

    # Initialize Firebase
    if not firebase_admin._apps:
        cred = credentials.Certificate(eval(FIREBASE_CRED_JSON))
        firebase_admin.initialize_app(cred, {
            'databaseURL': f"https://{cred.project_id}.firebaseio.com/"
        })

    # Timezone
    IST = pytz.timezone('Asia/Kolkata')

    def send_message(mode, to, body):
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        if mode == "sms":
            client.messages.create(body=body, from_=TWILIO_FROM, to=to)
        elif mode == "whatsapp":
            client.messages.create(body=body, from_=f"whatsapp:{TWILIO_FROM}", to=f"whatsapp:{to}")
        else:
            print(f"[!] Unknown mode for {to}: {mode}")

    def check_reminders():
        print("[✔] Reminder check started")
        ref = db.reference("customers")
        customers = ref.get() or {}

        today = datetime.now(IST).date()
        for key, c in customers.items():
            try:
                name = c.get("name", "Unknown")
                phone = c.get("phone")
                mode = c.get("mode", "sms")
                last_date_str = c.get("buy_date")

                if not (phone and last_date_str):
                    continue

                last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
                days_diff = (today - last_date).days

                if days_diff % 90 == 0:
                    msg = f"Dear {name}, please check your battery water level today."
                    send_message(mode, phone, msg)
                    print(f"[→] Sent reminder to {name}")
            except Exception as e:
                print(f"[✖] Error processing {key}: {e}")
""")

# Save the content to a file
scheduler_path = "/mnt/data/scheduler.py"
with open(scheduler_path, "w") as f:
    f.write(scheduler_py_content)

scheduler_path
