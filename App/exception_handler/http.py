from starlette.exceptions import HTTPException


async def http_exception_handler(request, exc: HTTPException):
    return res.e(str(exc.detail), exc.status_code)
