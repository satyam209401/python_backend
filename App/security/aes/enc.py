import base64
import json
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

_AAD = b"SWARG-MARG-AESGCM-V1"


def _get_key(key) -> bytes:
    if not isinstance(key, (str, bytes)):
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


def e(data, key) -> str | None:
    if data is None:
        return None

    if isinstance(data, (dict, list, bool, int, float)):
        raw = json.dumps(
            data, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
    elif isinstance(data, str):
        raw = data.encode("utf-8")
    elif isinstance(data, (bytes, bytearray)):
        raw = bytes(data)
    else:
        raw = str(data).encode("utf-8")

    nonce = os.urandom(12)
    encrypted = AESGCM(_get_key(key)).encrypt(nonce, raw, _AAD)

    return base64.b64encode(nonce + encrypted).decode("ascii")