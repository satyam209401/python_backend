from __future__ import annotations

import os
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def _parse_list(val: Any, default: list[str]) -> list[str]:
    if val is None:
        return default
    if isinstance(val, (list, tuple, set)):
        return [str(x).strip() for x in val if str(x).strip()]
    if isinstance(val, str):
        trimmed = val.strip()
        if trimmed == "*" or trimmed == "":
            return ["*"]
        return [x.strip() for x in trimmed.split(",") if x.strip()]
    return default


def setup_cors(
    app: FastAPI,
    origins: list[str] | str | None = None,
    headers: list[str] | str | None = None,
    methods: list[str] | str | None = None,
    credentials: bool | None = None,
    max_age: int | None = None,
) -> None:
    """
    Configure Cross-Origin Resource Sharing (CORS) on FastAPI application.
    Reads values from .env if not explicitly provided.
    """
    env_origins = os.getenv("CORS_ORIGINS", "*") if origins is None else origins
    env_headers = os.getenv("CORS_HEADERS", "*") if headers is None else headers
    env_methods = os.getenv("CORS_METHODS", "*") if methods is None else methods

    allow_origins = _parse_list(env_origins, ["*"])
    allow_headers = _parse_list(env_headers, ["*"])
    allow_methods = _parse_list(env_methods, ["*"])

    if credentials is None:
        raw_cred = (os.getenv("CORS_CREDENTIALS") or "true").strip().lower()
        allow_credentials = raw_cred in ("true", "1", "yes")
    else:
        allow_credentials = bool(credentials)

    if max_age is None:
        try:
            cors_max_age = int(os.getenv("CORS_MAX_AGE", "600"))
        except ValueError:
            cors_max_age = 600
    else:
        cors_max_age = int(max_age)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        max_age=cors_max_age,
    )


# Alias
cors = setup_cors
