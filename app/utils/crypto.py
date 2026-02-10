import os
from cryptography.fernet import Fernet, InvalidToken

APP_SECRET_KEY = os.getenv("APP_SECRET_KEY", "changeme").encode()
fernet = Fernet(Fernet.generate_key() if APP_SECRET_KEY == b'changeme' else APP_SECRET_KEY)

def encrypt_secret(secret: str) -> str:
    return fernet.encrypt(secret.encode()).decode()

def decrypt_secret(token: str) -> str:
    try:
        return fernet.decrypt(token.encode()).decode()
    except InvalidToken:
        raise ValueError("Invalid encryption token")
