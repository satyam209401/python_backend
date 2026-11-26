import json
import base64
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey
)
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


def dscToken(path=None):
    if not path:
        raise ValueError("Key directory path is required")

    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)

    private_path = directory / "private.pem"
    public_path = directory / "public.pem"

    if private_path.exists() or public_path.exists():
        raise FileExistsError("Keys already exist")

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_path.write_bytes(
        private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        )
    )

    public_path.write_bytes(
        public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )

    return True




def dsc(data, private_path):
    private_key = serialization.load_pem_private_key(
        Path(private_path).read_bytes(),
        password=None
    )

    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("Invalid Ed25519 private key")

    raw = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")

    return {
        "data": base64.b64encode(raw).decode("ascii"),
        "token": base64.b64encode(
            private_key.sign(raw)
        ).decode("ascii")
    }



def dscVerify(data, token, public_path):
    try:
        if isinstance(token, dict):
            token = token.get("token")

        if not token or not isinstance(token, (str, bytes)):
            return False

        public_key = serialization.load_pem_public_key(
            Path(public_path).read_bytes()
        )

        if not isinstance(public_key, Ed25519PublicKey):
            return False

        raw = json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False
        ).encode("utf-8")

        signature = base64.b64decode(token, validate=True)

        public_key.verify(signature, raw)
        return True

    except (InvalidSignature, ValueError, TypeError, KeyError, OSError):
        return False
