import inspect
import re
from functools import wraps
from fastapi import Request, HTTPException
from App.src.utils.req import _request_ctx


class Body:

    @staticmethod
    def limit(size: str):
        if not isinstance(size, str):
            raise ValueError("Payload size must be a string like '1MB'")

        units = {
            "B": 1,
            "KB": 1024,
            "MB": 1024 ** 2,
            "GB": 1024 ** 3,
        }

        match = re.fullmatch(r"\s*(\d+)\s*(B|KB|MB|GB)\s*", size, re.I)
        if not match:
            raise ValueError("Invalid payload size")

        maximum = int(match.group(1)) * units[match.group(2).upper()]
        is_async = None

        def decorator(func):
            nonlocal is_async
            is_async = inspect.iscoroutinefunction(func)

            @wraps(func)
            async def wrapper(*args, **kwargs):
                request = kwargs.get("request")

                if request is None:
                    request = next(
                        (arg for arg in args if isinstance(arg, Request)),
                        None,
                    )

                if request is None:
                    request = _request_ctx.get()

                if request is None:
                    raise RuntimeError("Request parameter is required in endpoint")

                content_length = request.headers.get("content-length")
                if content_length is not None:
                    try:
                        parsed_length = int(content_length)
                    except ValueError:
                        raise HTTPException(400, "Invalid Content-Length.")

                    if parsed_length < 0:
                        raise HTTPException(400, "Invalid Content-Length.")

                    if parsed_length > maximum:
                        raise HTTPException(413, "Request payload too large.")

                body_bytes = await request.body()
                if len(body_bytes) > maximum:
                    raise HTTPException(413, "Request payload too large.")

                if is_async:
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)

            return wrapper

        return decorator


body = Body()