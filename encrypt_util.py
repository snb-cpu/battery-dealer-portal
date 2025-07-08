from cryptography.fernet import Fernet
import base64

def decrypt(token: str, key: str) -> str:
    f = Fernet(key.encode())
    return f.decrypt(token.encode()).decode()
