import builtins
import os
import env as env_config


def get_env(key: str, default=None):
    return os.getenv(key, default)


get_env.is_loaded = env_config.is_loaded
builtins.env = get_env

from App.src.utils.log import log
from App.src.utils.req import req, set_current_request
from App.src.utils.body import body
from App.src.utils.user_info import user_info
from App.src.dsc.dsc import dsc, dscToken, dscVerify
from App.database.redis import redis
from App.database.sqlite import sqlite
from App.database.mysql import MySQLDB, DB, mysql, db
from App.database.pg import pg
from App.security.base64 import base
from App.security.aes import aes
from App.security.token import token, TokenManager
from App.security.password import password, Password
from App.src.Validator.str import GuardString
from App.src.utils.audit_logger import (
    AuditAppException,
    res,
    AuditLogger,
    AuditLoggerMiddleware,
    mask_sensitive_data,
    get_safe_url,
)
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from App.exception_handler import register_exception_handlers

# Register global utilities and helpers for the application
builtins.log = log
builtins.res = res
builtins.dsc = dsc
builtins.dscToken = dscToken
builtins.dsctoken = dscToken
builtins.dscVerify = dscVerify
builtins.req = req
builtins.base = base
builtins.aes = aes
builtins.body = body
builtins.user_info = user_info
builtins.redis = redis
builtins.sqlite = sqlite
builtins.MySQLDB = MySQLDB
builtins.DB = DB
builtins.mysql = mysql
builtins.db = db

builtins.pg = pg

builtins.token = token
builtins.TokenManager = TokenManager
builtins.password = password
builtins.Password = Password
builtins.GuardString = GuardString

builtins.AuditAppException = AuditAppException
builtins.AuditLogger = AuditLogger
builtins.AuditLoggerMiddleware = AuditLoggerMiddleware
builtins.mask_sensitive_data = mask_sensitive_data
builtins.get_safe_url = get_safe_url


async def check_env_middleware(request: Request, call_next):
    set_current_request(request)
    if not env.is_loaded:
        log("Server not configured .env not found")
        return res.e("Server not configured", 500)
    return await call_next(request)


def init(app):
    AuditLogger.init(app=app)
    app.add_middleware(AuditLoggerMiddleware)
    app.middleware("http")(check_env_middleware)
    register_exception_handlers(app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis.connect()
    yield
    await sqlite.shutdown()
    await redis.close()
    pg.close_all()
