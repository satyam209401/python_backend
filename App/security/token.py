from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import time
from typing import Any


class TokenManager:
    CONTEXT = "SWARG-MARG-TOKEN-V1"
    JTI_LENGTH = 64
    MAX_PAYLOAD = 500_000
    VERSION = 1

    _keys: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Keys
    # ------------------------------------------------------------------

    @classmethod
    def set_keys(cls, keys: dict[str, str]) -> None:
        if not keys or not isinstance(keys, dict):
            raise ValueError("Token keys are required.")

        normalized: dict[str, str] = {}

        for kid, key in keys.items():
            if (
                not isinstance(kid, str)
                or not re.match(r"^[a-zA-Z0-9_-]{1,32}$", kid)
                or not isinstance(key, str)
                or len(key) < 32
            ):
                raise ValueError("Invalid token key configuration.")

            normalized[kid] = key

        cls._keys = normalized

    @classmethod
    def _load_keys(cls) -> None:
        if cls._keys:
            return

        env_raw = env("TOKEN_MANAGER_KEYS") or env("SECURE_VAULT_KEYS_TOKENMANAGER")
        if env_raw:
            try:
                parsed = json.loads(env_raw)
                if isinstance(parsed, dict) and parsed:
                    cls.set_keys(parsed)
                    return
            except Exception:
                pass

        raise RuntimeError("Token keys are not configured.")

    @classmethod
    def _active_kid(cls) -> str:
        cls._load_keys()
        return list(cls._keys.keys())[-1]

    @classmethod
    def _signing_key(cls, kid: str, purpose: str) -> bytes:
        if kid not in cls._keys:
            raise RuntimeError("Invalid token key.")

        return hmac.new(
            cls._keys[kid].encode("utf-8"),
            f"{cls.CONTEXT}|{kid}|{purpose}".encode("utf-8"),
            hashlib.sha256,
        ).digest()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _encode_b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

    @classmethod
    def ttl(cls, duration: str) -> int:
        cleaned = duration.strip().upper()

        if cleaned.isdigit():
            return int(cleaned)

        match = re.match(r"^(\d+)(MO|Y|D|H|M|S)$", cleaned)
        if match:
            value = int(match.group(1))
            unit = match.group(2)

            multipliers = {
                "MO": 2_592_000,
                "Y": 31_536_000,
                "D": 86_400,
                "H": 3_600,
                "M": 60,
                "S": 1,
            }
            return value * multipliers[unit]

        return 0

    @staticmethod
    def _client_ip() -> str:
        try:
            ip = user_info.info("ip")  # type: ignore[name-defined]
            return ip.strip() if isinstance(ip, str) else ""
        except Exception:
            return ""

    @staticmethod
    def _device_signal() -> str:
        try:
            info = user_info.info()  # type: ignore[name-defined]
            if isinstance(info, dict) and info:
                return json.dumps(info, sort_keys=True, separators=(",", ":"))

            parts = [
                user_info.info("browser"),  # type: ignore[name-defined]
                user_info.info("os"),       # type: ignore[name-defined]
                user_info.info("device"),   # type: ignore[name-defined]
            ]
            cleaned = [p.strip() for p in parts if isinstance(p, str) and p.strip()]
            return "|".join(cleaned)
        except Exception:
            return ""

    @classmethod
    def _fingerprint(
        cls,
        ip: str,
        device: str,
        use_ip: bool,
        use_device: bool,
        kid: str,
    ) -> str:
        fp_data = {
            "ip": ip if use_ip else None,
            "device": hashlib.sha256(device.encode("utf-8")).hexdigest() if use_device else None,
        }
        raw_fp = json.dumps(fp_data, separators=(",", ":"), sort_keys=True).encode("utf-8")

        return hmac.new(
            cls._signing_key(kid, "fingerprint"),
            raw_fp,
            hashlib.sha256,
        ).hexdigest()

    # ------------------------------------------------------------------
    # Generate Token
    # ------------------------------------------------------------------

    @classmethod
    def generate(
        cls,
        usecase: str,
        data: Any,
        expiry: str = "1H",
        use_ip: bool = False,
        use_device: bool = False,
        custom_ip: str | None = None,
        custom_device: str | None = None,
    ) -> dict[str, Any]:
        try:
            cls._load_keys()

            if not isinstance(usecase, str) or usecase.strip() == "":
                raise ValueError("Invalid token configuration.")

            seconds = cls.ttl(expiry)
            if seconds <= 0:
                raise ValueError("Invalid token expiry.")

            ip = custom_ip if custom_ip is not None else cls._client_ip()
            device = custom_device if custom_device is not None else cls._device_signal()

            if use_ip and not ip:
                raise ValueError("Invalid client IP.")

            if use_device and device == "":
                raise ValueError("Device signal missing.")

            kid = cls._active_kid()
            now = int(time.time())
            expires_at = now + seconds
            jti = cls._encode_b64url(os.urandom(cls.JTI_LENGTH))

            fp = cls._fingerprint(
                ip=ip,
                device=device,
                use_ip=use_ip,
                use_device=use_device,
                kid=kid,
            )

            payload = {
                "v": cls.VERSION,
                "kid": kid,
                "jti": jti,
                "uc": usecase,
                "iat": now,
                "exp": expires_at,
                "ip": ip if use_ip else None,
                "dev": hashlib.sha256(device.encode("utf-8")).hexdigest() if use_device else None,
                "fp": fp,
                "cfg": {
                    "ip": use_ip,
                    "device": use_device,
                },
                "data": data,
            }

            encoded_payload = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            if len(encoded_payload) > cls.MAX_PAYLOAD:
                raise ValueError("Token payload too large.")

            encrypted_part = aes.e(payload, cls._keys[kid])  # type: ignore[name-defined]
            if not encrypted_part:
                raise RuntimeError("Token encryption failed.")

            return {
                "status": True,
                "token": f"{kid}.{encrypted_part}",
                "jti": jti,
                "usecase": usecase,
                "expires_at": expires_at,
            }
        except Exception:
            return {
                "status": False,
                "error": "token_generation_failed",
            }

    # ------------------------------------------------------------------
    # Verify Token
    # ------------------------------------------------------------------

    @classmethod
    def verify(cls, token: str, expected_usecase: str) -> dict[str, Any]:
        try:
            cls._load_keys()

            if (
                not isinstance(token, str)
                or not isinstance(expected_usecase, str)
                or token == ""
                or expected_usecase.strip() == ""
                or "." not in token
            ):
                raise RuntimeError("invalid_token")

            kid, encrypted_part = token.split(".", 1)

            if not re.match(r"^[a-zA-Z0-9_-]{1,32}$", kid) or kid not in cls._keys or not encrypted_part:
                raise RuntimeError("invalid_token")

            p = aes.d(encrypted_part, cls._keys[kid], as_json=True)  # type: ignore[name-defined]
            if not isinstance(p, dict):
                raise RuntimeError("invalid_token")

            if (
                p.get("v") != cls.VERSION
                or p.get("kid") != kid
                or p.get("uc") != expected_usecase
                or not isinstance(p.get("jti"), str)
                or type(p.get("iat")) is not int
                or type(p.get("exp")) is not int
                or not isinstance(p.get("cfg"), dict)
                or "data" not in p
                or not isinstance(p.get("fp"), str)
            ):
                raise RuntimeError("invalid_token")

            now = int(time.time())
            if (
                p["exp"] <= p["iat"]
                or p["iat"] > now + 60
                or now >= p["exp"]
            ):
                raise RuntimeError("token_expired")

            use_ip = p["cfg"].get("ip", False)
            use_device = p["cfg"].get("device", False)

            if not isinstance(use_ip, bool) or not isinstance(use_device, bool):
                raise RuntimeError("invalid_token")

            ip = ""
            device = ""

            if use_ip:
                ip = cls._client_ip()
                stored_ip = p.get("ip")
                if not ip or not isinstance(stored_ip, str) or not hmac.compare_digest(stored_ip, ip):
                    raise RuntimeError("ip_mismatch")

            if use_device:
                device = cls._device_signal()
                stored_dev = p.get("dev")
                current_dev_hash = hashlib.sha256(device.encode("utf-8")).hexdigest()
                if not device or not isinstance(stored_dev, str) or not hmac.compare_digest(stored_dev, current_dev_hash):
                    raise RuntimeError("device_mismatch")

            expected_fp = cls._fingerprint(
                ip=ip,
                device=device,
                use_ip=use_ip,
                use_device=use_device,
                kid=kid,
            )

            if not hmac.compare_digest(p["fp"], expected_fp):
                raise RuntimeError("fingerprint_mismatch")

            return {
                "status": True,
                "jti": p["jti"],
                "usecase": p["uc"],
                "data": p["data"],
                "meta": {
                    "iat": p["iat"],
                    "exp": p["exp"],
                    "ip_bind": use_ip,
                    "device_bind": use_device,
                    "kid": kid,
                },
            }
        except Exception as exc:
            allowed_errors = {
                "invalid_token",
                "token_expired",
                "ip_mismatch",
                "device_mismatch",
                "fingerprint_mismatch",
            }
            msg = str(exc)
            error = msg if msg in allowed_errors else "token_verification_failed"

            return {
                "status": False,
                "error": error,
            }


token = TokenManager
