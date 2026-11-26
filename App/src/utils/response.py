from fastapi.responses import JSONResponse

HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

class Response:
    @staticmethod
    def _send(status, message=False, data=None, code=200):
        return JSONResponse(
            content={
                "status": status,
                "status_code": code,
                "message": message,
                "data": {"token": data} if isinstance(data, str) else ([] if data is None else data),
            },
            status_code=code,
            headers=HEADERS,
        )

    @classmethod
    def s(cls, message=False, data=None, code=200):
        return cls._send(True, message, data, code)

    @classmethod
    def e(cls, message="error", code=400, data=None):
        return cls._send(False, message, data, code)


res = Response