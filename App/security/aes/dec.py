import base64
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

_AAD = b"SWARG-MARG-AESGCM-V1"


def _get_key(key) -> bytes:
    if not isinstance(key, (str, bytes)) or not key:
        raise ValueError("AES key is required")

    raw_key = key.encode("utf-8") if isinstance(key, str) else key
    if not raw_key:
        raise ValueError("AES key cannot be empty")

    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"aes-256-gcm-key",
    ).derive(raw_key)


def d(token, key, as_json=False):
    if not token or not key:
        return None

    try:
        if not isinstance(token, str):
            return None

        raw = base64.b64decode(token.strip(), validate=True)

        # 12 bytes nonce + at least 16 bytes GCM tag
        if len(raw) < 28:
            return None

        nonce, ciphertext = raw[:12], raw[12:]
        decrypted = AESGCM(_get_key(key)).decrypt(nonce, ciphertext, _AAD)

        try:
            text = decrypted.decode("utf-8")
            return json.loads(text) if as_json else text
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None if as_json else decrypted

    except Exception:
        return None