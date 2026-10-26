"""Sessioni del log di ricerca: una per ogni connessione WebSocket.

Il ricercatore può aggiungere dei marcatori ("inizio compito 2", "errore
osservato") da un secondo dispositivo con una POST su
``/api/research/marker``: finiscono in tutte le sessioni aperte, così il
log si allinea alle note di osservazione e alle registrazioni video.
"""

import subprocess
from functools import cache
from os import environ
from typing import Any

from fastapi import APIRouter, Request
from loguru import logger
from pydantic import BaseModel, Field

from vision_caption.adapters.research.jsonl_research_recorder import (
    JsonlResearchRecorder,
)
from vision_caption.core.ports.research_recorder_port import (
    NullResearchRecorder,
)
from vision_caption.infrastructure.settings import AppSettings, BACKEND_ROOT


router = APIRouter()


@cache
def app_version() -> str:
    """Commit del codice in esecuzione, per legare ogni sessione al codice.

    Nell'immagine Docker non c'è la cartella .git: lì il commit arriva da
    GIT_COMMIT, impostata durante la build.
    """
    from_env = environ.get("GIT_COMMIT", "").strip()
    if from_env:
        return from_env
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=BACKEND_ROOT,
            capture_output=True,
            text=True,
            timeout=2,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def config_snapshot(settings: AppSettings) -> dict[str, Any]:
    """Tutte le soglie in uso, senza le chiavi delle API."""
    snapshot = settings.model_dump(
        mode="json",
        exclude={
            "vlm": {"api_key"},
            "tts": {"elevenlabs_api_key"},
        },
    )
    snapshot["resolved"] = {
        "vlm_provider": settings.vlm.resolved_provider,
        "vlm_model": settings.vlm.resolved_model_name,
        "tts_provider": settings.tts.resolved_provider,
    }
    return snapshot


class ResearchSessions:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._open: set[JsonlResearchRecorder] = set()

    def open(
        self,
        participant_id: str | None = None,
        task_id: str | None = None,
        user_agent: str | None = None,
    ) -> JsonlResearchRecorder | NullResearchRecorder:
        research = self._settings.research
        if not research.enabled:
            return NullResearchRecorder()
        try:
            recorder = JsonlResearchRecorder.open_session(
                research.output_dir,
                include_text=research.include_text,
            )
        except OSError as error:
            logger.warning(f"Log di ricerca non disponibile: {error}")
            return NullResearchRecorder()

        self._open.add(recorder)
        recorder.record(
            "session_start",
            participant_id=participant_id,
            task_id=task_id,
            user_agent=user_agent,
            app_version=app_version(),
            config=config_snapshot(self._settings),
        )
        logger.info(
            f"Sessione di ricerca {recorder.session_id} aperta: {recorder.path}"
        )
        return recorder

    def close(self, recorder: JsonlResearchRecorder | NullResearchRecorder) -> None:
        if isinstance(recorder, JsonlResearchRecorder):
            self._open.discard(recorder)
        recorder.close()

    def mark(self, label: str, note: str | None = None) -> list[str]:
        for recorder in self._open:
            recorder.record("marker", label=label, note=note)
        return [recorder.session_id for recorder in self._open]


class MarkerRequest(BaseModel):
    label: str = Field(min_length=1, max_length=200)
    note: str | None = Field(default=None, max_length=2000)


@router.post("/api/research/marker")
def add_marker(marker: MarkerRequest, request: Request) -> dict:
    sessions: ResearchSessions = request.app.state.research_sessions
    return {"sessions": sessions.mark(marker.label, marker.note)}
