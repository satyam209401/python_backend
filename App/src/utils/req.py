from contextvars import ContextVar
from starlette.requests import Request

_request_ctx = ContextVar("request_ctx", default=None)


def set_current_request(request: Request):
    _request_ctx.set(request)


class Req:

    @staticmethod
    def _get(args):
        if args and isinstance(args[0], Request):
            return args[0], args[1] if len(args) > 1 else None
        request = _request_ctx.get()
        if request is None:
            raise RuntimeError("No active HTTP request")
        return request, args[0] if args else None

    @classmethod
    async def b(cls, *args, default=None):
        request, key = cls._get(args)
        body = getattr(request.state, "_cached_body_data", None)
        if body is None:
            try:
                body = await request.json()
            except Exception:
                try:
                    body = dict(await request.form())
                except Exception:
                    body = {}
            request.state._cached_body_data = body
        return body if key is None else body.get(key, default)

    @classmethod
    async def h(cls, *args, default=None):
        request, key = cls._get(args)
        headers = request.headers
        return dict(headers) if key is None else headers.get(key, default)

    @classmethod
    async def q(cls, *args, default=None):
        request, key = cls._get(args)
        query = request.query_params
        return dict(query) if key is None else query.get(key, default)


req = Req
