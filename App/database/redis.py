import asyncio
import json
import os
from typing import Any, Coroutine
import redis.asyncio as aioredis


class _FlexResult:
    """Coroutine ko await karne ya bina await ke chalane dono ke liye wrapper."""

    def __init__(self, coro: Coroutine[Any, Any, Any]):
        self._coro = coro
        self._task: asyncio.Task | None = None
        self._done = False
        self._value: Any = None
        self._error: BaseException | None = None
        self._schedule_if_possible()

    def _schedule_if_possible(self) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Koi running event loop nahi hai: sync context mein turant run kar do
            try:
                self._value = asyncio.run(self._coro)
            except BaseException as exc:
                self._error = exc
            finally:
                self._done = True
            return

        # Running loop hai: background task bana kar schedule kar do
        self._task = loop.create_task(self._coro)

    def __await__(self):
        async def _resolve():
            if self._done:
                if self._error is not None:
                    raise self._error
                return self._value
            if self._task is not None:
                return await self._task
            return await self._coro

        return _resolve().__await__()


class RedisDB:
    def __init__(self):
        self._clients: dict[int, aioredis.Redis] = {}

    def _default_db(self) -> int:
        raw = (os.getenv("REDIS_DB") or "").strip()
        if not raw:
            return 0
        try:
            return int(raw)
        except ValueError:
            return 0

    def _create_client(self, db_num: int) -> aioredis.Redis:
        url = os.getenv("REDIS_URL")
        if url:
            return aioredis.from_url(url, db=db_num, decode_responses=True, protocol=2)

        return aioredis.Redis(
            host=os.getenv("REDIS_HOST", "127.0.0.1"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD") or None,
            db=db_num,
            decode_responses=True,
            protocol=2,
        )

    def client(self, db: int | str | None = None) -> aioredis.Redis:
        db_num = self._default_db() if db is None else int(db)
        if db_num not in self._clients:
            self._clients[db_num] = self._create_client(db_num)
        return self._clients[db_num]

    def __getattr__(self, name: str):
        return getattr(self.client(), name)

    async def _set_async(self, key: str, value: Any, ttl: int | None = None, db: int | str | None = None) -> bool:
        c = self.client(db)
        payload = value if isinstance(value, (str, bytes, int, float)) else json.dumps(value)
        if ttl is not None:
            return bool(await c.set(key, payload, ex=int(ttl)))
        return bool(await c.set(key, payload))

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        db: int | str | None = None,
    ) -> _FlexResult:
        return _FlexResult(self._set_async(key, value, ttl=ttl, db=db))

    async def _get_async(
        self,
        key: str,
        default: Any = None,
        as_json: bool = False,
        db: int | str | None = None,
    ) -> Any:
        c = self.client(db)
        val = await c.get(key)
        if val is None:
            return default
        if as_json and isinstance(val, str):
            try:
                return json.loads(val)
            except Exception:
                return val
        return val

    def get(
        self,
        key: str,
        default: Any = None,
        as_json: bool = False,
        db: int | str | None = None,
    ) -> _FlexResult:
        return _FlexResult(self._get_async(key, default=default, as_json=as_json, db=db))

    async def _delete_async(self, *keys: str, db: int | str | None = None) -> int:
        if not keys:
            return 0
        return int(await self.client(db).delete(*keys))

    def delete(self, *keys: str, db: int | str | None = None) -> _FlexResult:
        return _FlexResult(self._delete_async(*keys, db=db))

    async def _ttl_async(self, key: str, db: int | str | None = None) -> int:
        return int(await self.client(db).ttl(key))

    def ttl(self, key: str, db: int | str | None = None) -> _FlexResult:
        return _FlexResult(self._ttl_async(key, db=db))

    async def _lpush_async(
        self,
        key: str,
        *values: Any,
        ttl: int | None = None,
        db: int | str | None = None,
    ) -> int:
        if not values:
            return 0
        c = self.client(db)
        encoded = [
            v if isinstance(v, (str, bytes, int, float)) else json.dumps(v)
            for v in values
        ]
        length = int(await c.lpush(key, *encoded))
        if ttl is not None:
            await c.expire(key, int(ttl))
        return length

    def lpush(
        self,
        key: str,
        *values: Any,
        ttl: int | None = None,
        db: int | str | None = None,
    ) -> _FlexResult:
        return _FlexResult(self._lpush_async(key, *values, ttl=ttl, db=db))

    async def _lrange_async(
        self,
        key: str,
        start: int = 0,
        end: int = -1,
        as_json: bool = False,
        db: int | str | None = None,
    ) -> list[Any]:
        items = await self.client(db).lrange(key, start, end)
        if not as_json:
            return list(items)
        result = []
        for item in items:
            try:
                result.append(json.loads(item))
            except Exception:
                result.append(item)
        return result

    def lrange(
        self,
        key: str,
        start: int = 0,
        end: int = -1,
        as_json: bool = False,
        db: int | str | None = None,
    ) -> _FlexResult:
        return _FlexResult(self._lrange_async(key, start=start, end=end, as_json=as_json, db=db))

    async def connect(self, db: int | str | None = None):
        c = self.client(db)
        await c.ping()
        return c

    async def isConnected(self, db: int | str | None = None) -> bool:
        try:
            return bool(await self.client(db).ping())
        except Exception:
            return False

    async def close(self):
        for c in list(self._clients.values()):
            try:
                await c.aclose()
            except Exception:
                pass
        self._clients.clear()


redis = RedisDB()