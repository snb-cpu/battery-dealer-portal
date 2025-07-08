from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("FERNET_KEY")
if not key:
    raise RuntimeError("FERNET_KEY not set")

f = Fernet(key.encode())

def encrypt(text):
    return f.encrypt(text.encode()).decode()

def decrypt(token):
    return f.decrypt(token.encode()).decode()