from starlette.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded

from App.exception_handler.http import http_exception_handler
from App.exception_handler.validation import validation_exception_handler
from App.exception_handler.rate_limit import rate_limit_handler
from App.exception_handler.server import server_exception_handler


def register_exception_handlers(app):
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_exception_handler(Exception, server_exception_handler)
