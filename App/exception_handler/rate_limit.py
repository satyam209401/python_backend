from slowapi.errors import RateLimitExceeded


async def rate_limit_handler(request, exc: RateLimitExceeded):
    return res.e("Too many requests. You have exceeded your rate limit. Please try again later.", 429)
