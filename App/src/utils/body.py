import re
from functools import wraps
from fastapi import Request, HTTPException
from App.src.utils.req import _request_ctx


class Body:

    @staticmethod
    def limit(size: str):
        units = {
            "B": 1,
            "KB": 1024,
            "MB": 1024 ** 2,
            "GB": 1024 ** 3
        }

        match = re.fullmatch(r"(\d+)\s*(B|KB|MB|GB)", size.strip(), re.I)

        if not match:
            raise ValueError("Invalid payload size")

        maximum = int(match.group(1)) * units[match.group(2).upper()]

        def decorator(func):

            @wraps(func)
            async def wrapper(*args, **kwargs):
                request = kwargs.get("request")

                if request is None:
                    request = next(
                        (arg for arg in args if isinstance(arg, Request)),
                        None
                    )

                if request is None:
                    request = _request_ctx.get()

                if request is None:
                    raise RuntimeError(
                        "Request parameter is required in endpoint"
                    )

                content_length = request.headers.get("content-length")

                if content_length:
                    try:
                        if int(content_length) > maximum:
                            raise HTTPException(
                                413, "Request payload too large."
                            )
                    except ValueError:
                        raise HTTPException(
                            400, "Invalid Content-Length."
                        )

                body = await request.body()

                if len(body) > maximum:
                    raise HTTPException(
                        413, "Request payload too large."
                    )

                return await func(*args, **kwargs)

            return wrapper

        return decorator


body = Body()
