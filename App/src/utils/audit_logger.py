from __future__ import annotations

from datetime import datetime
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import sys
import time
import traceback
from typing import Any, Callable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

APP_ERROR_MESSAGE = "An unexpected error occurred. Please try again later."
APP_ERROR_DATA = []
APP_ERROR_STATUS_CODE = 500
APP_ERROR_CODE = 999


class AuditAppException(Exception):
    """Raise karke error flow trigger kar sakte hain."""

    def __init__(
        self,
        message: str = APP_ERROR_MESSAGE,
        status_code: int = APP_ERROR_CODE,
        data: Any = APP_ERROR_DATA,
        code: str | int = APP_ERROR_CODE,
        skip_log: bool = False,
        internal_message: str | None = None,
    ) -> None:
        super().__init__(internal_message or message)
        self.message = message
        self.status_code = status_code
        self.data = data
        self.code = code
        self.skip_log = skip_log
        self.internal_message = internal_message or message


class res:
    """Standard API response helper: res.s(...) aur res.e(...)."""

    @staticmethod
    def s(
        message: str = "Success",
        data: Any = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ) -> JSONResponse:
        AuditLogger.mark_response_sent()
        payload = {
            "status": True,
            "status_code": status_code,
            "message": message,
            "data": {} if data is None else data,
        }
        return JSONResponse(
            status_code=status_code,
            content=AuditLogger.mask_sensitive_data(payload),
            headers=headers,
        )

    @staticmethod
    def e(
        message: str = "Error",
        status_code: int = 400,
        data: Any = None,
        code: str = "API_ERROR",
        log_error: bool = False,
        extra: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> JSONResponse:
        extra = extra or {}
        req = extra.get("request")
        req_id = AuditLogger.get_request_id(req)

        if log_error:
            AuditLogger.log("ERROR", code, message, extra)

        AuditLogger.mark_response_sent()
        payload = {
            "status": False,
            "status_code": status_code,
            "message": message,
            "error_id": req_id,
            "data": [] if data is None else data,
        }
        res_headers = dict(headers or {})
        if req_id:
            res_headers["X-Error-ID"] = req_id
        return JSONResponse(
            status_code=status_code,
            content=payload,
            headers=res_headers,
        )


def _app_error_response(
    req_id: str | None = None,
    headers: dict[str, str] | None = None,
    message: str = APP_ERROR_MESSAGE,
    error_code: int = 999,
) -> JSONResponse:
    if not req_id:
        req_id = AuditLogger.get_request_id()

    error_data: dict[str, Any] = {"error_id": req_id} if req_id else {}
    from App.src.utils.response import res as app_res

    resp = app_res.s(message, error_data, error_code)
    if req_id:
        resp.headers["X-Error-ID"] = req_id
        resp.headers["X-Request-ID"] = req_id
    if headers:
        for k, v in headers.items():
            resp.headers[k] = v
    return resp


class AuditLogger:
    _oom_reserve: bytearray | None = None
    _response_sent: bool = False
    _initialized: bool = False
    _timezone_name: str = "Asia/Kolkata"

    _sensitive_keys: tuple[str, ...] = (
        "password", "pass", "token", "access_token", "refresh_token",
        "secret", "client_secret", "otp", "pin", "mpin", "card",
        "card_number", "cvv", "cvc", "key", "api_key", "apikey",
        "authorization", "cookie", "session", "auth",
    )

    @classmethod
    def get_sqlite_db_path(cls) -> Path:
        base_root = Path(__file__).resolve().parents[3]
        env_path = None
        import builtins
        if hasattr(builtins, "env") and callable(builtins.env):
            try:
                env_path = builtins.env("runtime_time_log") or builtins.env("audit_logs")
            except Exception:
                pass
        if not env_path:
            env_path = os.getenv("runtime_time_log") or os.getenv("audit_logs")

        if env_path and str(env_path).strip():
            p = Path(str(env_path).strip())
            if not p.is_absolute():
                p = (base_root / p).resolve()
        else:
            p = (base_root / "db" / "runtime_time_log.sqlite").resolve()

        try:
            p.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        return p

    @classmethod
    def _ensure_sqlite_table(cls, db_path: Path) -> None:
        try:
            db_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        conn = sqlite3.connect(str(db_path), timeout=10.0)
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT,
                    ip TEXT,
                    error TEXT,
                    file TEXT,
                    line INTEGER,
                    datetime TEXT,
                    full_error_json TEXT,
                    occurrences INTEGER DEFAULT 1,
                    UNIQUE(ip, file, error)
                );
            """)
            cur.execute("""
                CREATE VIEW IF NOT EXISTS runtime_time_log AS SELECT * FROM audit_logs;
            """)
            conn.commit()
        finally:
            conn.close()

    @classmethod
    def _tz(cls) -> Any:
        try:
            return ZoneInfo(cls._timezone_name)
        except Exception:
            from datetime import timezone, timedelta
            return timezone(timedelta(hours=5, minutes=30))

    @classmethod
    def _now(cls) -> datetime:
        return datetime.now(cls._tz())

    @classmethod
    def new_request_id(cls) -> str:
        return f"{secrets.token_hex(8)}::{cls._now().strftime('%Y-%m-%d %H:%M:%S')}"

    @classmethod
    def mark_response_sent(cls) -> None:
        cls._response_sent = True

    @classmethod
    def reset_request_state(cls, request: Request | None = None) -> str:
        cls._response_sent = False
        req_id = cls.new_request_id()
        start_ts = time.perf_counter()

        if request is not None:
            request.state.request_id = req_id
            request.state.start_time = start_ts
            request.state.raw_body = b""
            request.state.client_ip = cls.get_client_ip(request)
            request.state.url = cls.get_safe_url(str(request.url))
            request.state.method = request.method
            request.state.user_agent = request.headers.get("user-agent", "")

        os.environ["CURRENT_REQUEST_ID"] = req_id
        return req_id

    @classmethod
    def get_request_id(cls, request: Request | None = None) -> str:
        if request is not None and getattr(request.state, "request_id", None):
            return str(request.state.request_id)
        return os.environ.get("CURRENT_REQUEST_ID") or cls.new_request_id()

    @classmethod
    def init(cls, timezone: str = "Asia/Kolkata", app: FastAPI | None = None) -> None:
        cls._timezone_name = timezone
        os.environ["TZ"] = timezone
        if hasattr(time, "tzset"):
            try:
                time.tzset()
            except OSError:
                pass

        if cls._initialized:
            if app is not None:
                cls.register_fastapi(app)
            return

        cls._initialized = True
        cls._oom_reserve = bytearray(262144)
        os.environ.setdefault("CURRENT_REQUEST_ID", cls.new_request_id())

        def _unhandled_excepthook(exc_type: type[BaseException], exc_val: BaseException, exc_tb: Any) -> None:
            cls._oom_reserve = None
            tb_list = traceback.extract_tb(exc_tb)
            last_frame = tb_list[-1] if tb_list else None
            cls.log(
                "CRITICAL",
                "UNHANDLED_EXCEPTION",
                str(exc_val),
                {
                    "file": last_frame.filename if last_frame else "",
                    "line": last_frame.lineno if last_frame else 0,
                    "trace": "".join(traceback.format_exception(exc_type, exc_val, exc_tb)),
                },
            )
            sys.__excepthook__(exc_type, exc_val, exc_tb)

        sys.excepthook = _unhandled_excepthook

        if app is not None:
            cls.register_fastapi(app)

    @classmethod
    def register_fastapi(cls, app: FastAPI) -> None:
        if getattr(app.state, "_audit_logger_registered", False):
            return
        app.state._audit_logger_registered = True

        @app.exception_handler(AuditAppException)
        async def _audit_app_exception_handler(request: Request, exc: AuditAppException) -> JSONResponse:
            client_ip = cls.get_client_ip(request)
            throttle = cls.check_error_throttle(client_ip, increment=True)
            if throttle["throttled"]:
                return cls.rate_limit_response(throttle["retry_after"], request)

            if not exc.skip_log:
                cls.log(
                    "ERROR",
                    exc.code,
                    exc.internal_message,
                    {
                        "trace": traceback.format_exc(),
                        "request": request,
                    },
                )

            req_id = cls.get_request_id(request)
            return _app_error_response(req_id=req_id, message=exc.message, error_code=999)

        @app.exception_handler(Exception)
        async def _global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
            return cls.handle_exception(exc, request=request)

    @classmethod
    def mask_sensitive_data(cls, data: Any) -> Any:
        if hasattr(data, "__dict__") and not isinstance(data, (dict, list, tuple, set)):
            data = vars(data)

        if isinstance(data, dict):
            masked: dict[Any, Any] = {}
            for k, v in data.items():
                k_str = str(k)
                is_sensitive = any(s in k_str.lower() for s in cls._sensitive_keys)
                if is_sensitive:
                    masked[k] = "********"
                elif isinstance(v, (dict, list, tuple, set)) or hasattr(v, "__dict__"):
                    masked[k] = cls.mask_sensitive_data(v)
                else:
                    masked[k] = v
            return masked

        if isinstance(data, list):
            return [cls.mask_sensitive_data(item) for item in data]

        if isinstance(data, tuple):
            return [cls.mask_sensitive_data(item) for item in data]

        if isinstance(data, set):
            return [cls.mask_sensitive_data(item) for item in data]

        return data

    @classmethod
    def get_safe_url(cls, url: str) -> str:
        if not url:
            return ""
        try:
            parts = urlsplit(url)
            if not parts.query:
                return url
            params = dict(parse_qsl(parts.query, keep_blank_values=True))
            masked_params = cls.mask_sensitive_data(params)
            safe_query = urlencode(masked_params, doseq=True)
            return urlunsplit((parts.scheme, parts.netloc, parts.path, safe_query, parts.fragment))
        except Exception:
            return url

    @classmethod
    def get_client_ip(cls, request: Request | None = None) -> str:
        if request is None:
            return "127.0.0.1"

        rate_limit_cls = globals().get("RateLimit")
        if rate_limit_cls is not None and hasattr(rate_limit_cls, "get_client_ip"):
            try:
                ip = rate_limit_cls.get_client_ip(request)
                if ip:
                    return str(ip)
            except Exception:
                pass

        direct_ip = (request.client.host if request.client else "127.0.0.1") or "127.0.0.1"
        direct_ip = direct_ip.strip()
        m = re.match(r"^(\d{1,3}(?:\.\d{1,3}){3})(?::\d+)?$", direct_ip)
        if m:
            direct_ip = m.group(1)

        if re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", direct_ip):
            parts = [int(x) for x in direct_ip.split(".")]
            if all(0 <= p <= 255 for p in parts):
                return direct_ip
        elif ":" in direct_ip:
            return direct_ip

        return "127.0.0.1"

    @classmethod
    def get_code_snippet(cls, file_path: str, line: int, radius: int = 5) -> dict[str, str] | None:
        if not file_path or line <= 0:
            return None
        p = Path(file_path)
        if not p.is_file():
            return None

        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return None

        start = max(0, line - radius - 1)
        end = min(len(lines), line + radius)
        snippet: dict[str, str] = {}
        for idx in range(start, end):
            line_num = idx + 1
            prefix = f"👉 [LINE {line_num}] " if line_num == line else f"   [LINE {line_num}] "
            snippet[prefix] = lines[idx].rstrip("\r\n")
        return snippet

    @classmethod
    def find_probable_culprit_line(cls, file_path: str, error_line: int) -> dict[str, Any] | None:
        if not file_path or error_line <= 1:
            return None
        p = Path(file_path)
        if not p.is_file():
            return None

        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return None

        for i in range(min(error_line - 2, len(lines) - 1), -1, -1):
            trimmed = lines[i].strip()
            if not trimmed:
                continue
            if trimmed.startswith(("#", "//", "/*", "*", '"""', "'''")) or trimmed.endswith("*/"):
                continue

            culprit_line_num = i + 1
            last_char = trimmed[-1]
            if last_char not in (";", "{", "}", ":", ")", "]", ","):
                return {
                    "line": culprit_line_num,
                    "code": trimmed,
                    "hint": f"Line {culprit_line_num} ('{trimmed}') statement incomplete ho sakta hai ya syntax/delimiter missing hai.",
                }
            break

        return None

    @staticmethod
    def _env_int(key: str, default: int) -> int:
        val = os.getenv(key)
        if val is None or val.strip() == "":
            return default
        try:
            return int(val)
        except ValueError:
            return default

    @classmethod
    def check_error_throttle(cls, ip: str, increment: bool = True) -> dict[str, Any]:
        max_errors = cls._env_int("LOG_MAX_ERRORS_PER_IP", 5)
        if max_errors <= 0:
            return {"throttled": False, "retry_after": 0, "hits": 0}

        seconds = 60
        driver = os.getenv("RATE_LIMIT_DRIVER", "redis").strip().lower()

        rate_limit_cls = globals().get("RateLimit")
        if driver == "redis" and rate_limit_cls is not None and hasattr(rate_limit_cls, "get_redis"):
            try:
                redis_client = rate_limit_cls.get_redis()
                if redis_client is not None:
                    redis_key = "rl:err:" + hashlib.md5(ip.encode("utf-8")).hexdigest()
                    if increment:
                        hits = int(redis_client.incr(redis_key))
                        if hits == 1:
                            redis_client.expire(redis_key, seconds)
                            ttl = seconds
                        else:
                            ttl = int(redis_client.ttl(redis_key))
                            if ttl <= 0:
                                redis_client.expire(redis_key, seconds)
                                ttl = seconds
                    else:
                        raw_hits = redis_client.get(redis_key)
                        hits = int(raw_hits) if raw_hits is not None else 0
                        ttl = int(redis_client.ttl(redis_key))
                        if ttl <= 0:
                            ttl = seconds

                    return {
                        "throttled": hits > max_errors,
                        "retry_after": max(1, ttl),
                        "hits": hits,
                    }
            except Exception:
                pass

        now = int(time.time())
        base_root = Path(__file__).resolve().parents[3]
        cache_dir = base_root / "cache" / "log_throttles"
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            return {"throttled": False, "retry_after": 0, "hits": 0}

        file_path = cache_dir / f"lt_{hashlib.md5(ip.encode('utf-8')).hexdigest()}.tmp"
        try:
            fp = open(file_path, "a+", encoding="utf-8")
        except OSError:
            return {"throttled": False, "retry_after": 0, "hits": 0}

        try:
            cls._lock_file(fp)
            fp.seek(0)
            content = fp.read()
            data = None
            if content:
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    data = None

            if not isinstance(data, dict) or "reset" not in data or now >= int(data["reset"]):
                hits = 1 if increment else 0
                reset = now + seconds
            else:
                hits = int(data.get("hits", 0)) + (1 if increment else 0)
                reset = int(data["reset"])

            if increment:
                fp.seek(0)
                fp.truncate()
                fp.write(json.dumps({"hits": hits, "reset": reset}))
                fp.flush()

            cls._unlock_file(fp)
        finally:
            fp.close()

        retry_after = max(1, reset - now)
        return {
            "throttled": hits > max_errors,
            "retry_after": retry_after,
            "hits": hits,
        }

    @classmethod
    def is_log_throttled(cls, ip: str) -> bool:
        return bool(cls.check_error_throttle(ip, increment=False)["throttled"])

    @classmethod
    def rate_limit_response(cls, retry_after: int = 60, request: Request | None = None) -> JSONResponse:
        cls.mark_response_sent()
        return JSONResponse(
            status_code=429,
            content={
                "status": False,
                "status_code": 429,
                "message": f"Too many errors. You have been temporarily rate limited. Please try again in {retry_after} seconds.",
                "data": [],
                "retry_after": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    @staticmethod
    def _lock_file(fp: Any) -> None:
        if os.name == "nt":
            import msvcrt

            fp.seek(0)
            retries = 0
            while retries < 20:
                try:
                    msvcrt.locking(fp.fileno(), msvcrt.LK_LOCK, 1)
                    break
                except OSError as exc:
                    if exc.errno not in (errno.EACCES, errno.EDEADLK):
                        break
                    time.sleep(0.005)
                    retries += 1
        else:
            import fcntl

            fcntl.flock(fp.fileno(), fcntl.LOCK_EX)

    @staticmethod
    def _unlock_file(fp: Any) -> None:
        if os.name == "nt":
            import msvcrt

            try:
                fp.seek(0)
                msvcrt.locking(fp.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
        else:
            import fcntl

            fcntl.flock(fp.fileno(), fcntl.LOCK_UN)

    @classmethod
    def log(cls, level: str, code: str, message: str, extra: dict[str, Any] | None = None) -> None:
        try:
            extra = extra or {}
            request: Request | None = extra.get("request")
            client_ip = cls.get_client_ip(request)

            if cls.is_log_throttled(client_ip):
                return

            now_dt = cls._now()
            base_root = Path(__file__).resolve().parents[3]
            log_dir = Path(os.getenv("AUDIT_LOG_DIR", str(base_root / "logs")))
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{now_dt.strftime('%d-%m-%Y')}.json"

            trace_str = extra.get("trace")
            if not trace_str:
                trace_str = "".join(traceback.format_stack())

            req_id = cls.get_request_id(request)
            raw_file = str(extra.get("file", ""))
            reported_line = int(extra.get("line", 0) or 0)

            if (not raw_file or reported_line <= 0) and request is None:
                tb = traceback.extract_stack()
                for frame in reversed(tb):
                    if frame.filename != __file__:
                        raw_file = raw_file or frame.filename
                        reported_line = reported_line or frame.lineno
                        break

            clean_file = raw_file.replace(str(base_root) + os.sep, "").replace(str(base_root) + "/", "").replace("\\", "/")

            culprit = cls.find_probable_culprit_line(raw_file, reported_line)
            target_line = int(culprit["line"]) if culprit else reported_line

            method = ""
            safe_url = ""
            user_agent = ""
            input_data: dict[str, Any] = {}

            if request is not None:
                method = request.method
                safe_url = cls.get_safe_url(str(request.url))
                user_agent = request.headers.get("user-agent", "")

                query_masked = cls.mask_sensitive_data(dict(request.query_params))
                if query_masked:
                    input_data["query"] = query_masked

                raw_body: bytes = getattr(request.state, "raw_body", b"")
                if raw_body:
                    trimmed_body = raw_body[:32768].decode("utf-8", errors="replace")
                    try:
                        parsed_json = json.loads(trimmed_body)
                        if isinstance(parsed_json, dict) and parsed_json:
                            input_data["json_body"] = cls.mask_sensitive_data(parsed_json)
                    except json.JSONDecodeError:
                        pass

            log_payload: dict[str, Any] = {
                "request_id": req_id,
                "time": now_dt.strftime("%H:%M:%S"),
                "date": now_dt.strftime("%Y-%m-%d"),
                "level": level,
                "code": code,
                "error": message,
                "file": clean_file,
                "line": target_line,
            }

            if culprit is not None:
                log_payload["reported_line"] = reported_line
                log_payload["cause"] = culprit["hint"]

            log_payload["code_snippet"] = cls.get_code_snippet(raw_file, target_line, radius=3)
            log_payload["method"] = method
            log_payload["url"] = safe_url
            log_payload["ip"] = client_ip
            log_payload["user_agent"] = user_agent
            log_payload["trace"] = [ln for ln in str(trace_str).splitlines() if ln.strip()][:5]

            if input_data:
                log_payload["input"] = input_data

            # 1. SQLite Storage with Deduplication (Same IP + File + Error will NOT duplicate)
            try:
                db_path = cls.get_sqlite_db_path()
                cls._ensure_sqlite_table(db_path)

                conn = sqlite3.connect(str(db_path), timeout=10.0)
                try:
                    cur = conn.cursor()
                    full_error_dict = {
                        "level": level,
                        "code": code,
                        "reported_line": reported_line,
                        "cause": culprit["hint"] if culprit else None,
                        "code_snippet": cls.get_code_snippet(raw_file, target_line, radius=3),
                        "method": method,
                        "url": safe_url,
                        "user_agent": user_agent,
                        "trace": [ln for ln in str(trace_str).splitlines() if ln.strip()][:10],
                        "input": input_data if input_data else None,
                    }
                    full_error_json = json.dumps(full_error_dict, ensure_ascii=False)
                    datetime_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")

                    cur.execute("""
                        INSERT INTO audit_logs (
                            request_id, ip, error, file, line, datetime, full_error_json, occurrences
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, 1
                        )
                        ON CONFLICT(ip, file, error) DO UPDATE SET
                            occurrences = occurrences + 1,
                            request_id = excluded.request_id,
                            line = excluded.line,
                            datetime = excluded.datetime,
                            full_error_json = excluded.full_error_json;
                    """, (
                        req_id,
                        client_ip,
                        message,
                        clean_file,
                        target_line,
                        datetime_str,
                        full_error_json,
                    ))
                    conn.commit()
                finally:
                    conn.close()
            except Exception:
                pass

            json_item = json.dumps(log_payload, indent=4, ensure_ascii=False)
            max_file_size = cls._env_int("LOG_MAX_FILE_SIZE_MB", 20) * 1024 * 1024

            indented_item = json_item.replace("\n", "\n    ")

            if not log_file.exists() or log_file.stat().st_size == 0:
                with open(log_file, "wb") as fp:
                    cls._lock_file(fp)
                    fp.write(f"[\n    {indented_item}\n]".encode("utf-8"))
                    cls._unlock_file(fp)
            else:
                with open(log_file, "r+b") as fp:
                    cls._lock_file(fp)
                    fp.seek(0, os.SEEK_END)
                    size = fp.tell()
                    if size < max_file_size:
                        read_len = min(size, 1024)
                        fp.seek(size - read_len)
                        chunk = fp.read(read_len)
                        bracket_pos = chunk.rfind(b"]")
                        if bracket_pos != -1:
                            target_offset = (size - read_len) + bracket_pos
                            fp.seek(target_offset)
                            fp.write(f",\n    {indented_item}\n]".encode("utf-8"))
                            fp.truncate()
                        else:
                            fp.seek(0, os.SEEK_END)
                            fp.write(f"\n// Next entry:\n{json_item}\n".encode("utf-8"))
                    cls._unlock_file(fp)

        except Exception:
            pass

    @classmethod
    def handle_exception(
        cls,
        exc: BaseException,
        request: Request | None = None,
        code: str = "EXCEPTION",
        http_status: int = 501,
        skip_log: bool = False,
        client_message: str | None = None,
    ) -> JSONResponse:
        client_ip = cls.get_client_ip(request)
        throttle = cls.check_error_throttle(client_ip, increment=True)
        if throttle["throttled"]:
            return cls.rate_limit_response(throttle["retry_after"], request)

        tb_list = traceback.extract_tb(exc.__traceback__)
        last_frame = tb_list[-1] if tb_list else None

        if not skip_log:
            cls.log(
                "ERROR",
                code,
                str(exc),
                {
                    "file": last_frame.filename if last_frame else "",
                    "line": last_frame.lineno if last_frame else 0,
                    "trace": "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
                    "request": request,
                },
            )

        req_id = cls.get_request_id(request)
        msg = client_message or APP_ERROR_MESSAGE
        return _app_error_response(req_id=req_id, message=msg, error_code=999)


class AuditLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        AuditLogger.init(timezone=AuditLogger._timezone_name)
        AuditLogger.reset_request_state(request)

        try:
            body_bytes = await request.body()
            request.state.raw_body = body_bytes
        except Exception:
            request.state.raw_body = b""

        try:
            response = await call_next(request)
            AuditLogger.mark_response_sent()
            return response
        except AuditAppException as exc:
            return AuditLogger.handle_exception(
                exc,
                request=request,
                code=exc.code,
                http_status=exc.status_code,
                skip_log=exc.skip_log,
                client_message=exc.message,
            )
        except Exception as exc:
            return AuditLogger.handle_exception(
                exc,
                request=request,
                code="MIDDLEWARE_EXCEPTION",
                http_status=500,
            )


def mask_sensitive_data(data: Any) -> Any:
    return AuditLogger.mask_sensitive_data(data)


def get_safe_url(url: str) -> str:
    return AuditLogger.get_safe_url(url)