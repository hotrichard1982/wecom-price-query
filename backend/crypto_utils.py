import os
import base64
import hashlib
from cryptography.fernet import Fernet


def _get_key():
    token = os.getenv('token', 'default-key-change-me')
    key = hashlib.sha256(token.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_password(plain_text):
    f = Fernet(_get_key())
    return f.encrypt(plain_text.encode()).decode()


def decrypt_password(encrypted_text):
    f = Fernet(_get_key())
    return f.decrypt(encrypted_text.encode()).decode()
