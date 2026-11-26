from fastapi.exceptions import RequestValidationError


async def validation_exception_handler(request, exc: RequestValidationError):
    return res.e("Validation Error", 422, exc.errors())
