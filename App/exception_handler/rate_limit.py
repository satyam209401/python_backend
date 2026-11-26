from slowapi.errors import RateLimitExceeded


async def rate_limit_handler(request, exc: RateLimitExceeded):
    return res.e("Rate limit exceeded", 429)
