from __future__ import annotations

import json as json_lib
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Union


class HttpResponse:
    """
    Standardized HTTP Response object returned by HttpClient.
    Supports dict-like subscription if the response payload is JSON.
    """

    def __init__(
        self,
        status_code: int,
        data: Any = None,
        text: str = "",
        headers: Optional[Dict[str, str]] = None,
        ok: bool = False,
        error: Optional[str] = None,
    ) -> None:
        self.status_code: int = status_code
        self.data: Any = data
        self.text: str = text
        self.headers: Dict[str, str] = headers or {}
        self.ok: bool = ok
        self.error: Optional[str] = error

    def json(self) -> Any:
        """Returns the parsed JSON response (dict or list)."""
        return self.data

    def to_dict(self) -> Dict[str, Any]:
        """Returns response summary as a clean dictionary."""
        return {
            "status_code": self.status_code,
            "ok": self.ok,
            "data": self.data,
            "error": self.error,
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Safe dict-like .get() on the parsed JSON body."""
        if isinstance(self.data, dict):
            return self.data.get(key, default)
        return default

    def __getitem__(self, key: Any) -> Any:
        """Allows direct subscription: res['key'] or res[0]."""
        if isinstance(self.data, (dict, list)):
            return self.data[key]
        raise TypeError(
            f"Response body is not subscriptable (type: {type(self.data).__name__}). "
            f"Raw text: {self.text[:100]}"
        )

    def __contains__(self, key: Any) -> bool:
        if isinstance(self.data, (dict, list)):
            return key in self.data
        return False

    def __bool__(self) -> bool:
        """Truthy if HTTP status is 2xx (self.ok)."""
        return self.ok

    def __repr__(self) -> str:
        tag = "OK" if self.ok else "Error"
        return f"<HttpResponse [{self.status_code} {tag}]>"


class HttpClient:
    """
    Lightweight, zero-dependency HTTP client built on Python's native urllib.
    Registered globally as `http` across all modules.
    """

    DEFAULT_TIMEOUT: int = 10
    DEFAULT_USER_AGENT: str = "Mozilla/5.0 (compatible; PythonBackend/1.0; +https://fastapi.local)"

    @classmethod
    def request(
        cls,
        method: str,
        url: str,
        data: Any = None,
        *,
        json: Any = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        verify: bool = True,
    ) -> HttpResponse:
        """
        Executes an HTTP request and returns an HttpResponse object.
        Never crashes unhandled on network or HTTP error status codes.
        """
        method = method.upper().strip()

        # 1. URL Query Parameters
        if params:
            clean_params = {
                k: (v if not isinstance(v, (dict, list)) else json_lib.dumps(v))
                for k, v in params.items()
                if v is not None
            }
            query_string = urllib.parse.urlencode(clean_params)
            delimiter = "&" if "?" in url else "?"
            url = f"{url}{delimiter}{query_string}"

        # 2. Prepare Headers (case-insensitive check)
        req_headers: Dict[str, str] = {}
        if headers:
            req_headers.update(headers)

        has_header = lambda name: any(k.lower() == name.lower() for k in req_headers)

        if not has_header("User-Agent"):
            req_headers["User-Agent"] = cls.DEFAULT_USER_AGENT

        # 3. Payload Serialization
        body_bytes: Optional[bytes] = None
        if json is not None:
            body_bytes = json_lib.dumps(json).encode("utf-8")
            if not has_header("Content-Type"):
                req_headers["Content-Type"] = "application/json"
        elif data is not None:
            if isinstance(data, (dict, list)):
                body_bytes = json_lib.dumps(data).encode("utf-8")
                if not has_header("Content-Type"):
                    req_headers["Content-Type"] = "application/json"
            elif isinstance(data, str):
                body_bytes = data.encode("utf-8")
                if not has_header("Content-Type"):
                    req_headers["Content-Type"] = "application/x-www-form-urlencoded"
            elif isinstance(data, (bytes, bytearray)):
                body_bytes = bytes(data)
                if not has_header("Content-Type"):
                    req_headers["Content-Type"] = "application/octet-stream"

        # 4. SSL Context
        if verify:
            ctx = ssl.create_default_context()
        else:
            ctx = ssl._create_unverified_context()

        # 5. Build urllib Request
        req = urllib.request.Request(
            url=url,
            data=body_bytes,
            headers=req_headers,
            method=method,
        )

        # 6. Execute Request safely
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
                status_code = response.getcode()
                raw_bytes = response.read()
                resp_headers = dict(response.info().items())
                text = raw_bytes.decode("utf-8", errors="replace")

                data_parsed = None
                try:
                    data_parsed = json_lib.loads(text)
                except Exception:
                    data_parsed = None

                return HttpResponse(
                    status_code=status_code,
                    data=data_parsed if data_parsed is not None else text,
                    text=text,
                    headers=resp_headers,
                    ok=(200 <= status_code < 300),
                    error=None,
                )

        except urllib.error.HTTPError as err:
            # Handles 4xx, 5xx without throwing an exception
            try:
                err_bytes = err.read()
                err_text = err_bytes.decode("utf-8", errors="replace")
                err_data = None
                try:
                    err_data = json_lib.loads(err_text)
                except Exception:
                    err_data = None
            except Exception:
                err_text = str(err)
                err_data = None

            return HttpResponse(
                status_code=err.code,
                data=err_data if err_data is not None else err_text,
                text=err_text,
                headers=dict(err.headers.items()) if err.headers else {},
                ok=False,
                error=f"HTTP {err.code}: {err.reason}",
            )

        except urllib.error.URLError as err:
            return HttpResponse(
                status_code=0,
                data=None,
                text="",
                headers={},
                ok=False,
                error=f"Connection Error: {err.reason}",
            )

        except TimeoutError:
            return HttpResponse(
                status_code=0,
                data=None,
                text="",
                headers={},
                ok=False,
                error=f"Request timed out after {timeout} seconds",
            )

        except Exception as exc:
            return HttpResponse(
                status_code=0,
                data=None,
                text="",
                headers={},
                ok=False,
                error=f"Request failed: {str(exc)}",
            )

    @classmethod
    def get(
        cls,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        verify: bool = True,
    ) -> HttpResponse:
        """HTTP GET request."""
        return cls.request("GET", url, params=params, headers=headers, timeout=timeout, verify=verify)

    @classmethod
    def post(
        cls,
        url: str,
        data: Any = None,
        *,
        json: Any = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        verify: bool = True,
    ) -> HttpResponse:
        """HTTP POST request with automatic dict/list JSON serialization."""
        return cls.request(
            "POST",
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
            timeout=timeout,
            verify=verify,
        )

    @classmethod
    def put(
        cls,
        url: str,
        data: Any = None,
        *,
        json: Any = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        verify: bool = True,
    ) -> HttpResponse:
        """HTTP PUT request."""
        return cls.request(
            "PUT",
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
            timeout=timeout,
            verify=verify,
        )

    @classmethod
    def patch(
        cls,
        url: str,
        data: Any = None,
        *,
        json: Any = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        verify: bool = True,
    ) -> HttpResponse:
        """HTTP PATCH request."""
        return cls.request(
            "PATCH",
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
            timeout=timeout,
            verify=verify,
        )

    @classmethod
    def delete(
        cls,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        verify: bool = True,
    ) -> HttpResponse:
        """HTTP DELETE request."""
        return cls.request(
            "DELETE",
            url,
            params=params,
            headers=headers,
            timeout=timeout,
            verify=verify,
        )


http = HttpClient
