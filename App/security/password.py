from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import (
    Argon2Error,
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)


class Password:
    MAX_PASSWORD_BYTES = 4096

    _ph = PasswordHasher(
        memory_cost=65536,  # 64 MiB (same as PHP 65536 KiB)
        time_cost=4,
        parallelism=1,
    )

    def __init__(self) -> None:
        raise TypeError("Password class cannot be instantiated.")

    @classmethod
    def hash(cls, password: str) -> str:
        if not isinstance(password, str) or password == "":
            raise ValueError("Invalid password.")

        raw_bytes = password.encode("utf-8")
        if len(raw_bytes) > cls.MAX_PASSWORD_BYTES:
            raise ValueError("Invalid password.")

        try:
            return cls._ph.hash(password)
        except Argon2Error as exc:
            raise RuntimeError("Password hashing failed.") from exc

    @classmethod
    def verify(cls, password: str, password_hash: str) -> bool:
        if (
            not isinstance(password, str)
            or not isinstance(password_hash, str)
            or password == ""
            or password_hash == ""
        ):
            return False

        if len(password.encode("utf-8")) > cls.MAX_PASSWORD_BYTES:
            return False

        try:
            return cls._ph.verify(password_hash, password)
        except (
            VerifyMismatchError,
            VerificationError,
            Argon2Error,
            InvalidHashError,
            ValueError,
        ):
            return False


password = Password
