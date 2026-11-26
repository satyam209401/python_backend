import asyncio
import aiosqlite

from pathlib import Path
from contextlib import asynccontextmanager


class SQLiteDB:

    _connections = {}
    _registry_lock = asyncio.Lock()

    def __init__(self, connection, path):
        self.connection = connection
        self.path = path
        self.lock = asyncio.Lock()
        self.owner = None
        self.closed = False

    @classmethod
    async def connect(cls, path):

        path = Path(path).expanduser()

        if not path.is_absolute():
            raise ValueError("Absolute database path required")

        path.parent.mkdir(parents=True, exist_ok=True)
        path = str(path.resolve())

        async with cls._registry_lock:
            if path in cls._connections:
                db = cls._connections[path]
                if not db.closed:
                    return db

            conn = await aiosqlite.connect(
                path, timeout=5, isolation_level=None
            )
            conn.row_factory = aiosqlite.Row

            try:
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
                    await conn.execute(f"PRAGMA {pragma}")

                db = cls(conn, path)
                cls._connections[path] = db
                return db

            except BaseException:
                await conn.close()
                raise

    async def _run(self, callback):
        if self.closed:
            raise RuntimeError("Database is closed")

        if self.owner is asyncio.current_task():
            return await callback()

        async with self.lock:
            if self.closed:
                raise RuntimeError("Database is closed")
            return await callback()

    async def raw(self, sql, params=()):

        async def execute():
            async with self.connection.execute(sql, params) as cur:
                if cur.description:
                    return [dict(row) for row in await cur.fetchall()]

                return {
                    "lastrowid": cur.lastrowid,
                    "rowcount": cur.rowcount,
                }

        return await self._run(execute)

    async def executemany(self, sql, params):

        async def execute():
            async with self.connection.executemany(sql, params) as cur:
                return {
                    "lastrowid": cur.lastrowid,
                    "rowcount": cur.rowcount,
                }

        return await self._run(execute)

    async def beginTransaction(self):
        if self.owner is asyncio.current_task():
            raise RuntimeError("Transaction already active")

        await self.lock.acquire()

        try:
            if self.closed:
                raise RuntimeError("Database is closed")

            await self.connection.execute("BEGIN")
            self.owner = asyncio.current_task()
            return True

        except BaseException:
            self.lock.release()
            raise

    async def commit(self):
        if self.owner is not asyncio.current_task():
            raise RuntimeError("Transaction not owned by current task")

        try:
            await self.connection.commit()
            return True
        finally:
            self.owner = None
            self.lock.release()

    async def rollBack(self):
        if self.owner is not asyncio.current_task():
            raise RuntimeError("Transaction not owned by current task")

        try:
            await self.connection.rollback()
            return True
        finally:
            self.owner = None
            self.lock.release()

    @asynccontextmanager
    async def transaction(self):
        await self.beginTransaction()
        try:
            yield self
            await self.commit()
        except BaseException:
            if self.owner is asyncio.current_task():
                await self.rollBack()
            raise

    async def isConnected(self):
        try:
            return bool(await self.raw("SELECT 1"))
        except Exception:
            return False

    async def close(self):
        if self.closed:
            return

        if self.owner is asyncio.current_task():
            await self.rollBack()

        async with self.lock:
            if self.closed:
                return

            self.closed = True
            await self.connection.close()

        async with self._registry_lock:
            if self._connections.get(self.path) is self:
                self._connections.pop(self.path, None)

    @classmethod
    async def shutdown(cls):
        for db in list(cls._connections.values()):
            await db.close()


sqlite = SQLiteDB
