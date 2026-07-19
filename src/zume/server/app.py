"""FastAPI application factory. Binds to localhost by default."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from zume import __version__
from zume.doctor import collect_doctor_report

_VERSION = __version__


def create_app(root: Path | None = None, *, review_mode: bool = False) -> FastAPI:
    root = root or Path.cwd()
    app = FastAPI(
        title="Zume Local API",
        version=_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.state.root = root.resolve()
    app.state.review_mode = bool(review_mode)

    @app.middleware("http")
    async def localhost_docs_only(request: Request, call_next):  # type: ignore[no-untyped-def]
        from zume.server.runtime import bind_root, reset_root

        token = bind_root(Path(request.app.state.root))
        try:
            response = await call_next(request)
        finally:
            reset_root(token)
        if getattr(request.app.state, "review_mode", False):
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
            response.headers["X-Zume-Review-Mode"] = "1"
        return response

    @app.get("/api/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "review_mode": bool(getattr(app.state, "review_mode", False)),
        }

    @app.get("/api/version")
    def version() -> dict[str, str]:
        return {"name": "zume", "version": _VERSION}

    @app.get("/api/build-info")
    def build_info() -> dict[str, Any]:
        from zume.build_info import collect_build_info

        return collect_build_info(Path(app.state.root))

    @app.get("/api/doctor")
    def doctor() -> dict[str, Any]:
        return collect_doctor_report()

    @app.get("/api/knowledge/stats")
    def knowledge_stats() -> dict[str, Any]:
        try:
            from zume.knowledge.stats import collect_stats

            return collect_stats(Path(app.state.root))
        except Exception as exc:  # noqa: BLE001 — empty library before Phase 2 seed is OK
            return {"available": False, "error": type(exc).__name__, "questions": 0, "exercises": 0}

    # Additional routers registered when modules exist.
    try:
        from zume.server.routes_workspace import router as workspace_router

        app.include_router(workspace_router, prefix="/api")
    except ImportError:
        pass

    static_dir = _resolve_static_dir(Path(app.state.root))
    if static_dir is not None:

        @app.get("/")
        def index() -> FileResponse:
            return FileResponse(static_dir / "index.html")

        app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

        @app.get("/{full_path:path}")
        def spa_fallback(full_path: str) -> FileResponse:
            if full_path.startswith("api/") or full_path in {"docs", "redoc", "openapi.json"}:
                raise HTTPException(status_code=404)
            candidate = static_dir / full_path
            if candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(static_dir / "index.html")

    @app.exception_handler(HTTPException)
    async def http_error(_request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


def _resolve_static_dir(root: Path) -> Path | None:
    candidates = [
        root / "apps" / "web" / "dist",
        root / "src" / "zume" / "server" / "static",
    ]
    for path in candidates:
        if (path / "index.html").is_file():
            return path
    return None
