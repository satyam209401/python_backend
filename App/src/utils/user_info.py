import re
from contextvars import ContextVar
from ipaddress import ip_address
from starlette.requests import Request
from App.src.utils.req import _request_ctx


def set_user_request(request: Request):
    return _request_ctx.set(request)


def reset_user_request(token):
    _request_ctx.reset(token)


class UserInfo:

    @staticmethod
    def info(key=None, trusted_proxies=("127.0.0.1", "::1")):
        request = _request_ctx.get()

        if request is None:
            raise RuntimeError("No active HTTP request")

        ua = request.headers.get("user-agent", "").strip()

        data = {
            "ip": UserInfo.ip(request, trusted_proxies),
            "user_agent": ua or None,
            "browser": UserInfo.browser(ua),
            "os": UserInfo.os(ua),
            "device": UserInfo.device(ua),
            "platform": request.headers.get("sec-ch-ua-platform"),
            "model": request.headers.get("sec-ch-ua-model"),
            "mobile": request.headers.get("sec-ch-ua-mobile"),
            "language": request.headers.get("accept-language"),
            "referer": request.headers.get("referer"),
        }

        if key is None:
            return data

        return data.get(key.strip().lower()) if isinstance(key, str) else None

    @staticmethod
    def ip(request=None, trusted_proxies=("127.0.0.1", "::1")):
        if request is None:
            request = _request_ctx.get()

        if request is None:
            return "0.0.0.0"

        remote = request.client.host if request.client else ""

        try:
            remote = str(ip_address(remote))
        except ValueError:
            return "0.0.0.0"

        if remote in trusted_proxies:
            cf_ip = request.headers.get("cf-connecting-ip", "")

            try:
                return str(ip_address(cf_ip.strip()))
            except ValueError:
                pass

        return remote

    @staticmethod
    def browser(ua=None):
        if isinstance(ua, Request):
            ua = ua.headers.get("user-agent", "").strip()
        elif ua is None:
            req = _request_ctx.get()
            ua = req.headers.get("user-agent", "").strip() if req else ""

        patterns = [
            (r"Edg/", "Edge"),
            (r"OPR/", "Opera"),
            (r"Chrome/", "Chrome"),
            (r"Firefox/", "Firefox"),
            (r"Safari/", "Safari"),
        ]

        return next(
            (name for pattern, name in patterns if re.search(pattern, ua, re.I)),
            "Unknown" if ua else None
        )

    @staticmethod
    def os(ua=None):
        if isinstance(ua, Request):
            ua = ua.headers.get("user-agent", "").strip()
        elif ua is None:
            req = _request_ctx.get()
            ua = req.headers.get("user-agent", "").strip() if req else ""

        patterns = [
            (r"Windows", "Windows"),
            (r"Android", "Android"),
            (r"iPhone|iPad|iPod", "iOS"),
            (r"Mac OS", "macOS"),
            (r"Linux", "Linux"),
        ]

        return next(
            (name for pattern, name in patterns if re.search(pattern, ua, re.I)),
            "Unknown" if ua else None
        )

    @staticmethod
    def device(ua=None):
        if isinstance(ua, Request):
            ua = ua.headers.get("user-agent", "").strip()
        elif ua is None:
            req = _request_ctx.get()
            ua = req.headers.get("user-agent", "").strip() if req else ""
            req = _request_ctx.get()
            ua = req.headers.get("user-agent", "").strip() if req else ""

        if not ua:
            return "Unknown"

        if re.search(r"iPad|Tablet", ua, re.I):
            return "Tablet"

        if re.search(r"Mobile|Android|iPhone", ua, re.I):
            return "Mobile"

        return "Desktop"


user_info = UserInfo
user = UserInfo
