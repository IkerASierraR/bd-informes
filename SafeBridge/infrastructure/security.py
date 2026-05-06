"""
Manejo seguro de credenciales con Fernet (cifrado simétrico).
"""

import os
import json
from cryptography.fernet import Fernet


KEY_FILE = os.path.expanduser("~/.safebridge/fernet_key.key")
CONNECTIONS_FILE = os.path.expanduser("~/.safebridge/connections.json.enc")


def _get_or_create_key() -> bytes:
    """Obtiene la clave Fernet o la genera una sola vez."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key


def encrypt_data(data: dict) -> bytes:
    """Cifra un diccionario convertido a JSON."""
    fernet = Fernet(_get_or_create_key())
    json_bytes = json.dumps(data).encode("utf-8")
    return fernet.encrypt(json_bytes)


def decrypt_data(encrypted_bytes: bytes) -> dict:
    """Descifra y devuelve el diccionario original."""
    fernet = Fernet(_get_or_create_key())
    decrypted = fernet.decrypt(encrypted_bytes)
    return json.loads(decrypted.decode("utf-8"))


def save_connections(connections: list[dict]) -> None:
    """Guarda lista de conexiones cifradas."""
    enc = encrypt_data(connections)
    with open(CONNECTIONS_FILE, "wb") as f:
        f.write(enc)


def load_connections() -> list[dict]:
    """Carga las conexiones guardadas o lista vacía."""
    if not os.path.exists(CONNECTIONS_FILE):
        return []
    with open(CONNECTIONS_FILE, "rb") as f:
        enc = f.read()
    try:
        return decrypt_data(enc)
    except Exception:
        return []