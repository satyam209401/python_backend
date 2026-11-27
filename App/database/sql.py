from __future__ import annotations

import builtins
import json
import os
import re
import sqlite3
from typing import Any

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    try:
        import psycopg2 as psycopg
        from psycopg2.extras import RealDictCursor as dict_row
    except ImportError:
        psycopg = None
        dict_row = None

try:
    import pymysql
    from pymysql.cursors import DictCursor
except ImportError:
    pymysql = None
    DictCursor = None

_NAMED_PARAM_RE = re.compile(r"(?<![:\w]):([A-Za-z_][A-Za-z0-9_]*)")
_SQL_QUOTE_RE = re.compile(r"('(?:''|[^'])*'|\"(?:\"\"|[^\"])*\")")


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


def _resolve_config(cfg: str | dict[str, Any] | None) -> tuple[str, dict[str, Any]]:
    if cfg is None:
        raise ValueError("Database configuration is missing.")

    if isinstance(cfg, str):
        trimmed = cfg.strip()
        if not trimmed.startswith("{"):
            env_val = os.getenv(trimmed)
            if not env_val:
                raise ValueError(f"Environment variable '{trimmed}' not found.")
            trimmed = env_val.strip()

        try:
            cfg = json.loads(trimmed)
        except Exception as exc:
            raise ValueError("Database configuration JSON is invalid.") from exc

    if not isinstance(cfg, dict) or not cfg:
        raise ValueError("Database configuration must be a non-empty dict.")

    raw_driver = str(cfg.get("DRIVER") or cfg.get("DB_DRIVER") or "").strip().lower()
    if raw_driver in ("pg", "postgres", "postgresql"):
        driver = "pg"
    elif raw_driver in ("mysql", "mariadb"):
        driver = "mysql"
    elif raw_driver in ("sqlite", "sqlite3"):
        driver = "sqlite"
    else:
        raise ValueError("Unsupported or missing DRIVER (use 'pg', 'mysql', or 'sqlite').")

    if driver == "sqlite":
        db_path = str(
            cfg.get("path") or cfg.get("DB_PATH") or cfg.get("DB_FILE") or cfg.get("DB_NAME") or ""
        ).strip()
        if not db_path:
            raise RuntimeError("Incomplete SQLite configuration: 'path' is required.")

        if db_path != ":memory:":
            parent_dir = os.path.dirname(db_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

        return driver, {"database": db_path}

    host = str(cfg.get("DB_HOST") or "").strip()
    port_raw = cfg.get("DB_PORT")
    db_name = str(cfg.get("DB_NAME") or cfg.get("DB_DATABASE") or "").strip()
    user = str(cfg.get("DB_USER") or cfg.get("DB_USERNAME") or "").strip()
    password = str(cfg.get("DB_PASS") or cfg.get("DB_PASSWORD") or "")

    if (
        not host
        or port_raw is None
        or isinstance(port_raw, bool)
        or not str(port_raw).isdigit()
        or int(port_raw) <= 0
        or not db_name
        or not user
    ):
        raise RuntimeError("Incomplete database configuration.")

    if driver == "pg":
        sslmode = str(cfg.get("DB_SSLMODE") or "require").strip()
        return driver, {
            "host": host,
            "port": int(port_raw),
            "dbname": db_name,
            "user": user,
            "password": password,
            "sslmode": sslmode or "require",
            "connect_timeout": 5,
        }

    charset = str(cfg.get("DB_CHARSET") or "utf8mb4").strip()
    return driver, {
        "host": host,
        "port": int(port_raw),
        "database": db_name,
        "user": user,
        "password": password,
        "charset": charset or "utf8mb4",
        "connect_timeout": 5,
        "cursorclass": DictCursor,
        "autocommit": True,
    }


class DB:
    @staticmethod
    def isConnected(cfg: str | dict[str, Any] | None) -> bool:
        try:
            driver, config = _resolve_config(cfg)

            if driver == "sqlite":
                conn = sqlite3.connect(config["database"], timeout=5, isolation_level=None)
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT 1")
                    return cur.fetchone() is not None
                finally:
                    conn.close()

            if driver == "pg":
                if psycopg is None:
                    return False
                with psycopg.connect(**config) as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1")
                        return cur.fetchone() is not None

            if driver == "mysql":
                if pymysql is None:
                    return False
                conn = pymysql.connect(**config)
                try:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1")
                        return cur.fetchone() is not None
                finally:
                    conn.close()

            return False
        except Exception:
            return False

    @staticmethod
    def raw(
        cfg: str | dict[str, Any] | None,
        sql: str,
        params: dict[str, Any] | list[Any] | tuple[Any, ...] | None = None,
    ) -> list[dict[str, Any]] | int:
        driver, config = _resolve_config(cfg)

        if driver == "sqlite":
            conn = sqlite3.connect(config["database"], isolation_level=None)
            conn.row_factory = sqlite3.Row
            try:
                cur = conn.cursor()
                for pragma in (
                    "page_size=65536",
                    "foreign_keys=ON",
                    "journal_mode=WAL",
                    "synchronous=NORMAL",
                    "locking_mode=NORMAL",
                    "temp_store=MEMORY",
                    "cache_size=-64000",
                    "mmap_size=2147483648",
                    "busy_timeout=5000",
                ):
                    cur.execute(f"PRAGMA {pragma}")
                cur.execute(sql, params if params is not None else ())
                if cur.description is not None:
                    return [dict(row) for row in cur.fetchall()]
                return cur.rowcount
            finally:
                conn.close()

        final_sql, final_params = _convert_colon_params(sql, params)

        if driver == "pg":
            with psycopg.connect(**config, row_factory=dict_row, autocommit=True) as conn:
                with conn.cursor() as cur:
                    cur.execute(final_sql, final_params)
                    if cur.description is not None:
                        return cur.fetchall()
                    return cur.rowcount

        conn = pymysql.connect(**config)
        try:
            with conn.cursor() as cur:
                cur.execute(final_sql, final_params)
                if cur.description is not None:
                    return cur.fetchall()
                return cur.rowcount
        finally:
            conn.close()

