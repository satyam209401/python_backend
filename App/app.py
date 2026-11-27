import asyncio
import builtins
import os
import sys
from pathlib import Path

# Project root ko sys.path me add karein taaki direct run karne par bhi import fail na ho
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from contextlib import asynccontextmanager
import env as env_config
from fastapi import FastAPI


def get_env(key: str, default=None):
    return os.getenv(key, default)


get_env.is_loaded = getattr(env_config, "is_loaded", False)
get_env.env_path = str(getattr(env_config, "ENV_PATH", ".env"))
builtins.env = get_env

# --- Cache Cleaner Utility ---
from App.src.cleaner import clear_pycache

builtins.clear_pycache = clear_pycache

# --- Response Utility ---
from App.src.utils.response import res

builtins.res = res

# --- Body Utility ---
from App.src.utils.body import body

builtins.body = body

# --- Request Utility ---
from App.src.utils.req import req, set_current_request

builtins.req = req

# --- Logger Utility ---
from App.src.utils.log import log

builtins.log = log

# --- User Info Utility ---
from App.src.utils.user_info import user_info

builtins.user_info = user_info

# --- SQLite Web Utility ---
from App.database.sqlite_web import sqlite

builtins.sqlite = sqlite

# --- AES Encryption / Decryption ---
from App.security.aes import aes

builtins.aes = aes

# --- Base64 Encode / Decode ---
from App.security.base64 import base

builtins.base = base

# --- Password Utility (Argon2) ---
from App.security.password import Password

builtins.password = Password

# --- Token Manager ---
from App.security.token import TokenManager

builtins.token = TokenManager

# --- Digital Signature (DSC) ---
from App.src.dsc.dsc import dsc, dscToken, dscVerify

builtins.dsc = dsc
builtins.dscToken = dscToken
builtins.dsctoken = dscToken
builtins.dscVerify = dscVerify

# --- String Validator (GuardString) ---
from App.src.Validator.str import GuardString

builtins.GuardString = GuardString
builtins.validator = GuardString
builtins.Validator = GuardString

# --- Universal Database Raw (DB / sql) ---
from App.database.sql import DB

builtins.db = DB
builtins.DB = DB

# --- Redis Client ---
from App.database.redis import redis

builtins.redis = redis

# --- CORS Configuration ---
from App.security.cors import cors

builtins.cors = cors

# --- Rate Limiter (SlowAPI) ---
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
builtins.limiter = limiter

# --- Main API Entry Gate ---
from App.entry import entry

builtins.entry = entry

# --- Auto Route Discovery ---
from App.src.router import auto_sync_routes, sync_routes

builtins.auto_sync_routes = auto_sync_routes
builtins.sync_routes = sync_routes

# --- Exception Handlers ---
from App.exception_handler import register_exception_handlers

# --- Audit Logger Utility ---
from App.src.utils.audit_logger import AuditLogger, AuditLoggerMiddleware, AuditAppException

builtins.audit_logger = AuditLogger
builtins.AuditLogger = AuditLogger
builtins.AuditAppException = AuditAppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    # App startup / reload par automatically cache clean karein
    clear_pycache()
    # Redis start / connect
    try:
        await redis.connect()
    except Exception as e:
        log(f"Redis connect error: {e}")
    yield
    # App shutdown cleanup
    await redis.close()



def init(app: FastAPI):
    app.state.limiter = limiter
    cors(app)
    AuditLogger.init(app=app)
    app.add_middleware(AuditLoggerMiddleware)

    docs_enabled = str(env("DOCS", "true")).strip().lower() in ("true", "1", "yes")
    if not docs_enabled:
        docs_paths = {"/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"}
        app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) not in docs_paths]
        app.docs_url = None
        app.redoc_url = None
        app.openapi_url = None

    @app.middleware("http")
    async def request_context_middleware(request, call_next):
        set_current_request(request)

        if not getattr(env, "is_loaded", False):
            path = getattr(env, "env_path", "unknown")
            log(f"Server not configured: .env not found at {path}")
            return res.e(f"Server not configured (.env not found at {path})", 500)

        response = await call_next(request)
        if "server" in response.headers:
            del response.headers["server"]
        return response

    register_exception_handlers(app)


def run():
    import uvicorn

    clear_pycache()
    reload_val = str(env("APP_RELOAD", "true")).strip().lower() in ("true", "1", "yes")
    uvicorn.run(
        "main:app",
        host=env("HOST", "127.0.0.1"),
        port=int(env("PORT", 8000)),
        reload=reload_val,
        reload_dirs=["."],
        reload_includes=["*.py", ".env"],
        reload_excludes=["__pycache__", "*.pyc", "*.pyo", ".git"],
        server_header=False,
    )

