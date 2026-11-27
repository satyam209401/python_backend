from __future__ import annotations

from contextvars import ContextVar
from typing import Any
from starlette.requests import Request

_request_ctx: ContextVar[Request | None] = ContextVar("request_ctx", default=None)


def set_current_request(request: Request) -> None:
    _request_ctx.set(request)


class Req:

    @staticmethod
    def _get(args: tuple[Any, ...]) -> tuple[Request, str | None]:
        if len(args) > 2:
            raise TypeError("Expected at most 2 positional arguments: (request, key) or (key).")

        if args and isinstance(args[0], Request):
            return args[0], args[1] if len(args) > 1 else None

        if len(args) > 1:
            raise TypeError("Expected at most 1 positional argument (key) when request is not passed.")

        request = _request_ctx.get()
        if request is None:
            raise RuntimeError("No active HTTP request")

        return request, args[0] if args else None

    @classmethod
    async def b(cls, *args: Any, default: Any = None) -> Any:
        request, key = cls._get(args)

        if not getattr(request.state, "_body_parsed", False):
            content_type = (request.headers.get("content-type") or "").lower()
            raw_body = await request.body()

            if not raw_body:
                body: Any = {}
            elif "application/json" in content_type or content_type.endswith("+json"):
                try:
                    body = await request.json()
                except Exception:
                    body = {}
            elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                form_data = await request.form()
                body = dict(form_data)
            else:
                try:
                    body = await request.json()
                except Exception:
                    body = raw_body.decode("utf-8", errors="replace")

            request.state._cached_body_data = body
            request.state._body_parsed = True
        else:
            body = request.state._cached_body_data

        if key is None:
            return body
        if isinstance(body, dict):
            return body.get(key, default)
        return default

    @classmethod
    async def h(cls, *args: Any, default: Any = None) -> Any:
        request, key = cls._get(args)
        headers = request.headers
        if key is None:
            return dict(headers)
        return headers.get(key, default)

    @classmethod
    async def q(cls, *args: Any, default: Any = None) -> Any:
        request, key = cls._get(args)
        query = request.query_params
        if key is None:
            return dict(query)
        return query.get(key, default)


req = Req