async def server_exception_handler(request, exc: Exception):
    return res.e("Internal Server Error", 500)
