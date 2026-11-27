from __future__ import annotations

import builtins
import inspect
from typing import Any, Callable
from fastapi import APIRouter, Request
from fastapi.responses import Response as FastAPIResponse


class EntryGate(APIRouter):
    """
    Main API Entry Gate Router.
    All API endpoints flow through this gate to ensure centralized routing and middleware.
    """

    def __init__(
        self,
        prefix: str = "/api",
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            prefix=prefix,
            tags=tags or [],
            dependencies=dependencies or [],
            **kwargs,
        )
        self.api: bool = True
        self.gate_handler: Callable[..., Any] | None = None
        self._mounted_apps: set[int] = set()
        self._setup_default_routes()
        self.sync_routes()

    def sync_routes(self, routes_dir: str = "routes") -> list[dict[str, Any]]:
        from App.src.router import auto_sync_routes

        return auto_sync_routes(self, routes_dir=routes_dir)

    def _setup_default_routes(self) -> None:
        @self.get("", include_in_schema=True, tags=["API Gateway"])
        @self.get("/", include_in_schema=False)
        def gateway_root():
            return builtins.res.s(
                "API Entry Gate Active",
                {
                    "gateway": "online",
                    "prefix": self.prefix,
                },
            )

    def __call__(
        self,
        target: Any = None,
        *,
        handler: Callable[..., Any] | None = None,
        api: bool = True,
        prefix: str | None = None,
        routes_dir: str = "routes",
    ) -> Any:
        # Decorator usage: @entry(app) async def gate(request): ...
        if callable(target) and not hasattr(target, "routes"):
            self.gate_handler = target
            return target

        app = target
        self.api = api
        if handler is not None:
            self.gate_handler = handler

        target_prefix = prefix if prefix is not None else self.prefix

        if app is not None and hasattr(app, "include_router") and hasattr(app, "middleware"):
            app_id = id(app)
            if app_id not in self._mounted_apps:
                self.sync_routes()

                @app.middleware("http")
                async def entry_gate_middleware(request: Request, call_next):
                    from App.src.utils.req import set_current_request

                    set_current_request(request)

                    path = request.url.path
                    if path == target_prefix or path.startswith(f"{target_prefix}/"):
                        if self.gate_handler is not None:
                            try:
                                sig = inspect.signature(self.gate_handler)
                                if len(sig.parameters) == 0:
                                    res_val = (
                                        await self.gate_handler()
                                        if inspect.iscoroutinefunction(self.gate_handler)
                                        else self.gate_handler()
                                    )
                                else:
                                    res_val = (
                                        await self.gate_handler(request)
                                        if inspect.iscoroutinefunction(self.gate_handler)
                                        else self.gate_handler(request)
                                    )
                            except Exception as exc:
                                if hasattr(builtins, "log"):
                                    builtins.log(f"Gate handler error: {exc}")
                                return builtins.res.e(f"Gate verification error: {exc}", 500)

                            if isinstance(res_val, FastAPIResponse):
                                return res_val

                            if res_val is False:
                                return builtins.res.e("API is currently unavailable", 422)

                            return await call_next(request)

                        if self.api is True:
                            return await call_next(request)
                        return builtins.res.e("API is currently unavailable", 422)

                    return await call_next(request)

                if prefix is not None:
                    app.include_router(self, prefix=prefix)
                else:
                    app.include_router(self)
                self._mounted_apps.add(app_id)

        return self


entry = EntryGate()
