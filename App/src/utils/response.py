from fastapi.responses import JSONResponse

HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


class Response:
    @staticmethod
    def _send(status, message=False, data=None, code=200, http_code=None):
        final_http_code = code if http_code is None else http_code
        return JSONResponse(
            content={
                "status": status,
                "status_code": code,
                "message": message,
                "data": {"token": data} if isinstance(data, str) else ([] if data is None else data),
            },
            status_code=final_http_code,
            headers=HEADERS,
        )

    @classmethod
    def s(cls, message=False, data=None, code=200):
        return cls._send(True, message, data, code, http_code=200)

    @classmethod
    def e(cls, message="error", code=400, data=None):
        return cls._send(False, message, data, code, http_code=code)


res = Response
