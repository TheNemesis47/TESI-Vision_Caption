from pathlib import Path, PurePosixPath

from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope


_BACKEND_PREFIXES = {
    "api",
    "docs",
    "health",
    "openapi.json",
    "redoc",
    "ws",
}


class SpaStaticFiles(StaticFiles):
    """Serve a Vite build and falls back to index.html for client routes."""

    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            return await super().get_response(path, scope)
        except HTTPException as exc:
            if exc.status_code != 404 or not self._is_client_route(path):
                raise
            return await super().get_response("index.html", scope)

    @staticmethod
    def _is_client_route(path: str) -> bool:
        normalized = PurePosixPath(path.lstrip("/"))
        first_part = normalized.parts[0] if normalized.parts else ""
        return first_part not in _BACKEND_PREFIXES and not normalized.suffix


def mount_frontend(app: FastAPI, dist_path: Path) -> bool:
    """Mount the frontend last, leaving the backend usable without a build."""
    index_path = dist_path / "index.html"
    if not index_path.is_file():
        return False

    app.mount(
        "/",
        SpaStaticFiles(directory=dist_path, html=True),
        name="frontend",
    )
    return True
