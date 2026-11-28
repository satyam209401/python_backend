import json
from typing import Any
from fastapi.responses import JSONResponse

HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


class AppJSONResponse(JSONResponse):
    def __init__(self, payload: dict[str, Any], status_code: int = 200):
        self._payload = payload
        super().__init__(content=payload, status_code=status_code, headers=HEADERS)

    def __getitem__(self, key: str) -> Any:
        return self._payload[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._payload.get(key, default)


def _parse_json(val: Any) -> Any:
    if isinstance(val, str):
        s = val.strip()
        if s.startswith(("{", "[")) and s.endswith(("}", "]")):
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                pass
    return val


def _normalize_data(val: Any) -> Any:
    val = _parse_json(val)
    return [] if val is None or val is False else val


class Response:
    @classmethod
    def s(cls, message: Any = False, data: Any = None, code: int = 200) -> AppJSONResponse:
        msg = _parse_json(message)
        if isinstance(msg, dict) and "message" in msg:
            msg = msg["message"]

        payload = {
            "status": True,
            "status_code": code,
            "message": msg,
            "data": _normalize_data(data),
        }
        return AppJSONResponse(payload, status_code=200)

    @classmethod
    def e(cls, message: Any = "Error occurred", code: int = 400, data: Any = None) -> AppJSONResponse:
        msg = _parse_json(message)
        extra_data = data

        if isinstance(msg, dict):
            if "message" in msg:
                rest = {k: v for k, v in msg.items() if k != "message"}
                extra_data = rest or data
                msg = msg["message"]
            else:
                extra_data = msg
                msg = "Error occurred"

        http_status = code if 100 <= code <= 599 else 400
        payload = {
            "status": False,
            "status_code": code,
            "message": msg,
            "data": _normalize_data(extra_data),
        }
        return AppJSONResponse(payload, status_code=http_status)


res = Response