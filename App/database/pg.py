from __future__ import annotations

import hashlib
import json
import os
import re
import threading
from contextlib import contextmanager
from typing import Any, Iterator

import psycopg2
from psycopg2.extras import RealDictCursor

_NAMED_PARAM_RE = re.compile(r"(?<![:\w]):([A-Za-z_][A-Za-z0-9_]*)")
_SQL_QUOTE_RE = re.compile(r"('(?:''|\\'|[^'])*'|\"(?:\\\\\"|\\\\\"|[^\"])*\")")


def _env(key: str, default=None):
    if "env" in globals() and callable(globals()["env"]):
        return globals()["env"](key, default)
    import builtins

    if hasattr(builtins, "env") and callable(builtins.env):
        return builtins.env(key, default)
    return os.getenv(key, default)


def _convert_colon_params(sql: str, params: Any) -> tuple[str, Any]:
    if not isinstance(params, dict):
        return sql, params

    parts = _SQL_QUOTE_RE.split(sql)
    for i in range(0, len(parts), 2):
        parts[i] = _NAMED_PARAM_RE.sub(
            lambda m: f"%({m.group(1)})s" if m.group(1) in params else m.group(0),
            parts[i],
        )

    return "".join(parts), params


class PG:
    _connections: dict[str, Any] = {}
    _last_errors: dict[str, str] = {}
    _lock = threading.Lock()

    @classmethod
    def _resolve_config(cls, cfg: str | dict[str, Any]) -> tuple[str, dict[str, Any]]:
        if isinstance(cfg, str):
            trimmed = cfg.strip()
            if not trimmed.startswith("{"):
                env_val = _env(trimmed)
                if not env_val:
                    raise ValueError(f"Environment variable '{trimmed}' not found.")
                trimmed = env_val.strip()

            try:
                cfg = json.loads(trimmed)
            except Exception as exc:
                raise ValueError("Database configuration JSON is invalid.") from exc

        if not isinstance(cfg, dict) or not cfg:
            raise ValueError("Database configuration must be a non-empty dict.")

        host = str(cfg.get("DB_HOST") or cfg.get("PGHOST") or "").strip()
        port_raw = cfg.get("DB_PORT") or cfg.get("PGPORT") or 5432
        database = str(
            cfg.get("DB_NAME") or cfg.get("DB_DATABASE") or cfg.get("PGDATABASE") or ""
        ).strip()
        username = str(
            cfg.get("DB_USER") or cfg.get("DB_USERNAME") or cfg.get("PGUSER") or ""
        ).strip()
        password = str(
            cfg.get("DB_PASS") or cfg.get("DB_PASSWORD") or cfg.get("PGPASSWORD") or ""
        )
        sslmode = str(cfg.get("DB_SSLMODE") or cfg.get("PGSSLMODE") or "prefer").strip()

        if (
            not host
            or port_raw is None
            or isinstance(port_raw, bool)
            or not str(port_raw).isdigit()
            or int(port_raw) <= 0
            or not database
            or not username
        ):
            raise RuntimeError("Incomplete PostgreSQL database configuration.")

        normalized = {
            "host": host,
            "port": int(port_raw),
            "database": database,
            "username": username,
            "password": password,
            "sslmode": sslmode,
        }

        pool_key = hashlib.sha256(
            json.dumps(normalized, sort_keys=True).encode("utf-8")
        ).hexdigest()

        return pool_key, normalized

    @classmethod
    def connect(cls, cfg: str | dict[str, Any]) -> Any:
        try:
            pool_key, config = cls._resolve_config(cfg)

            with cls._lock:
                conn = cls._connections.get(pool_key)
                if conn is not None:
                    try:
                        if conn.closed == 0:
                            with conn.cursor() as cur:
                                cur.execute("SELECT 1")
                            cls._last_errors.pop(pool_key, None)
                            return conn
                        else:
                            cls._connections.pop(pool_key, None)
                    except Exception:
                        cls._connections.pop(pool_key, None)

                conn = psycopg2.connect(
                    host=config["host"],
                    port=config["port"],
                    user=config["username"],
                    password=config["password"],
                    dbname=config["database"],
                    sslmode=config["sslmode"],
                    connect_timeout=5,
                    cursor_factory=RealDictCursor,
                )
                conn.autocommit = True

                cls._connections[pool_key] = conn
                cls._last_errors.pop(pool_key, None)
                return conn
        except Exception as exc:
            cls._last_errors["default"] = str(exc)
            raise

    @classmethod
    def is_connected(cls, cfg: str | dict[str, Any]) -> tuple[bool, str | None]:
        try:
            conn = cls.connect(cfg)
            with conn.cursor() as cur:
                cur.execute("SELECT 1 AS ok")
                row = cur.fetchone()
                if row and int(row.get("ok", 0)) == 1:
                    return True, None
            return False, "Unexpected SELECT 1 result."
        except Exception as exc:
            return False, str(exc)

    @classmethod
    def get_last_error(cls, name: str = "default") -> str | None:
        return cls._last_errors.get(name)

    @classmethod
    def close_all(cls) -> None:
        with cls._lock:
            for conn in list(cls._connections.values()):
                try:
                    conn.close()
                except Exception:
                    pass
            cls._connections.clear()

    @staticmethod
    def raw(
        db: str | dict[str, Any],
        sql: str,
        params: dict[str, Any] | list[Any] | tuple[Any, ...] | None = None,
    ) -> list[dict[str, Any]] | int:
        final_sql, final_params = _convert_colon_params(sql, params)
        conn = PG.connect(db)
        with conn.cursor() as cur:
            cur.execute(final_sql, final_params or ())
            if cur.description is not None:
                return [dict(row) for row in cur.fetchall()]
            return cur.rowcount

    @staticmethod
    def begin_transaction(db: str | dict[str, Any]) -> None:
        conn = PG.connect(db)
        conn.autocommit = False

    @staticmethod
    def commit(db: str | dict[str, Any]) -> None:
        conn = PG.connect(db)
        conn.commit()
        conn.autocommit = True

    @staticmethod
    def rollback(db: str | dict[str, Any]) -> None:
        conn = PG.connect(db)
        conn.rollback()
        conn.autocommit = True

    @staticmethod
    @contextmanager
    def transaction(db: str | dict[str, Any]) -> Iterator[None]:
        PG.begin_transaction(db)
        try:
            yield
            PG.commit(db)
        except Exception:
            PG.rollback(db)
            raise


pg = PG
PGDB = PG
postgres = PG
PostgresDB = PG
