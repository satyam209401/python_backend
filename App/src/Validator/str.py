from __future__ import annotations

import re
import unicodedata
from typing import Any


class GuardString:
    MAX_BYTES = 65_536  # 64 KB

    _CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u0080-\u009f]")
    _INVISIBLE_RE = re.compile(
        r"[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff\u2028\u2029]"
    )
    _REPETITION_RE = re.compile(r"(.)\1{100,}", re.DOTALL)
    _MIXED_SCRIPT_RE = re.compile(
        r"\b(?=[a-zA-Z0-9_\u00c0-\u024f]*[\u0400-\u04ff\u0370-\u03ff])"
        r"(?=[\u0400-\u04ff\u0370-\u03ff0-9_]*[a-zA-Z\u00c0-\u024f])"
        r"[a-zA-Z0-9_\u00c0-\u024f\u0400-\u04ff\u0370-\u03ff]+\b"
    )

    @staticmethod
    def _fail(code: str, message: str) -> dict[str, Any]:
        return {
            "valid": False,
            "errors": [{"code": code, "message": message}],
        }

    @classmethod
    def str(
        cls,
        value: Any,
        strict: bool = True,
        trim: bool = True,
    ) -> dict[str, Any]:
        if not isinstance(value, str):
            return cls._fail("INVALID_STRING", "Value must be a string.")

        try:
            raw_bytes = value.encode("utf-8")
        except UnicodeEncodeError:
            return cls._fail("INVALID_UNICODE", "Invalid UTF-8 string.")

        if len(raw_bytes) > cls.MAX_BYTES:
            return cls._fail("STRING_TOO_LARGE", "Maximum size is 64KB.")

        if trim:
            value = value.strip()

        if not strict:
            return {"valid": True, "value": value}

        try:
            value = unicodedata.normalize("NFC", value)
        except Exception:
            return cls._fail("INVALID_UNICODE", "Normalization failed.")

        checks = [
            (cls._CONTROL_RE, "CONTROL_CHARACTERS", "Control characters are not allowed."),
            (
                cls._INVISIBLE_RE,
                "INVISIBLE_CHARACTERS",
                "Invisible or directional characters are not allowed.",
            ),
            (cls._REPETITION_RE, "SUSPICIOUS_REPETITION", "Excessive repeated characters."),
            (cls._MIXED_SCRIPT_RE, "MIXED_SCRIPTS", "Suspicious mixed scripts detected."),
        ]

        for pattern, code, message in checks:
            if pattern.search(value):
                return cls._fail(code, message)

        return {"valid": True, "value": value}
