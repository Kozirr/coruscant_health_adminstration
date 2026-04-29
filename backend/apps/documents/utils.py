import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings


def get_encryption_key():
    key = settings.ENCRYPTION_KEY
    if isinstance(key, str):
        key = key.encode('utf-8')
    if len(key) < 32:
        key = key.ljust(32, b'\0')
    return key[:32]


def encrypt_file(file_bytes: bytes) -> tuple:
    key = get_encryption_key()
    aesgcm = AESGCM(key)
    iv = os.urandom(12)
    ciphertext = aesgcm.encrypt(iv, file_bytes, None)
    return ciphertext, base64.b64encode(iv).decode('utf-8')


def decrypt_file(ciphertext: bytes, iv_b64: str) -> bytes:
    key = get_encryption_key()
    aesgcm = AESGCM(key)
    iv = base64.b64decode(iv_b64)
    return aesgcm.decrypt(iv, ciphertext, None)
