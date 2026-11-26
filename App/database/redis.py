import os
import redis.asyncio as aioredis


def _env(key: str, default=None):
    if "env" in globals() and callable(globals()["env"]):
        return globals()["env"](key, default)
    import builtins
    if hasattr(builtins, "env") and callable(builtins.env):
        return builtins.env(key, default)
    return os.getenv(key, default)


class RedisDB:
    def __init__(self):
        self._clients: dict[int, aioredis.Redis] = {}

    def _default_db(self) -> int:
        try:
            return int(_env("REDIS_DB", 0))
        except (ValueError, TypeError):
            return 0

    def _create_client(self, db_num: int) -> aioredis.Redis:
        url = _env("REDIS_URL")
        if url:
            return aioredis.from_url(
                url,
                db=db_num,
                decode_responses=True,
                protocol=2,
            )
        return aioredis.Redis(
            host=_env("REDIS_HOST", "127.0.0.1"),
            port=int(_env("REDIS_PORT", 6379)),
            password=_env("REDIS_PASSWORD") or None,
            db=db_num,
            decode_responses=True,
            protocol=2,
        )

    def _get_client(self, db: int | str | None = None) -> aioredis.Redis:
        db_num = self._default_db() if db is None else int(db)
        if db_num not in self._clients:
            self._clients[db_num] = self._create_client(db_num)
        return self._clients[db_num]

    def db(self, db_num: int | str) -> aioredis.Redis:
        """Access a specific Redis database client, e.g. redis.db(1).set(...)"""
        return self._get_client(db_num)

    def __call__(self, db_num: int | str) -> aioredis.Redis:
        """Shorthand to access a specific Redis database client, e.g. redis(1).set(...)"""
        return self._get_client(db_num)

    def __getattr__(self, name):
        default_client = self._get_client()
        attr = getattr(default_client, name)
        if callable(attr):
            def wrapper(*args, **kwargs):
                target_db = kwargs.pop("db", None)
                if target_db is not None:
                    client = self._get_client(target_db)
                    return getattr(client, name)(*args, **kwargs)
                return attr(*args, **kwargs)
            return wrapper
        return attr

    async def connect(self, db: int | str | None = None):
        client = self._get_client(db)
        await client.ping()
        return client

    async def isConnected(self, db: int | str | None = None) -> bool:
        try:
            return bool(await self._get_client(db).ping())
        except Exception:
            return False

    async def close(self):
        for client in list(self._clients.values()):
            try:
                await client.aclose()
            except Exception:
                pass
        self._clients.clear()


redis = RedisDB()
