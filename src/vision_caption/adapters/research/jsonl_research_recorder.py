"""Log di ricerca: un file JSON Lines per sessione, un evento per riga.

Il file è separato dal log tecnico. Contiene soltanto ciò che serve all'analisi
dello studio: cosa ha detto il sistema, quando, perché ha taciuto e quanto ci
ha messo. Non contiene immagini, e i partecipanti compaiono con il codice
pseudonimo che passa il client.

Ogni riga ha sempre gli stessi campi di testa:

    schema_version  versione di questo formato
    session_id      identificativo della connessione WebSocket
    seq             numero progressivo dell'evento nella sessione
    ts              istante UTC in formato ISO 8601
    t               secondi dall'inizio della sessione (orologio monotono)
    event           nome dell'evento
"""

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from typing import Any
from uuid import uuid4

from loguru import logger


SCHEMA_VERSION = 1

# Campi che possono contenere testo letto dalla scena o detto al
# partecipante. Con include_text=False restano le lunghezze ma non il testo.
TEXT_FIELDS = frozenset(
    {
        "text",
        "target",
        "description",
        "visible_text",
        "alternatives",
        "candidate_labels",
    }
)


class JsonlResearchRecorder:
    def __init__(
        self,
        path: Path,
        session_id: str,
        include_text: bool = True,
        clock: Callable[[], float] = monotonic,
        wall_clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.path = path
        self.session_id = session_id
        self._include_text = include_text
        self._clock = clock
        self._wall_clock = wall_clock
        self._started_at = clock()
        self._seq = 0
        self._failed = False
        path.parent.mkdir(parents=True, exist_ok=True)
        self._file = path.open("a", encoding="utf-8")

    @classmethod
    def open_session(
        cls,
        output_dir: Path,
        include_text: bool = True,
    ) -> "JsonlResearchRecorder":
        session_id = uuid4().hex[:12]
        started = datetime.now(UTC)
        path = output_dir / f"{started:%Y%m%d-%H%M%S}_{session_id}.jsonl"
        return cls(path=path, session_id=session_id, include_text=include_text)

    def record(self, event: str, **fields: Any) -> None:
        if self._file.closed:
            return
        if not self._include_text:
            fields = {
                key: None if key in TEXT_FIELDS else value
                for key, value in fields.items()
            }
        self._seq += 1
        line = {
            "schema_version": SCHEMA_VERSION,
            "session_id": self.session_id,
            "seq": self._seq,
            "ts": self._wall_clock().isoformat(timespec="milliseconds"),
            "t": round(self._clock() - self._started_at, 3),
            "event": event,
            **fields,
        }
        try:
            self._file.write(
                json.dumps(line, ensure_ascii=False, default=str) + "\n"
            )
            # Una riga alla volta su disco: se il server cade a metà sessione
            # gli eventi già avvenuti restano.
            self._file.flush()
        except (OSError, TypeError, ValueError) as error:
            if not self._failed:
                logger.warning(
                    f"Log di ricerca non scrivibile ({self.path}): {error}"
                )
            self._failed = True

    def close(self) -> None:
        if not self._file.closed:
            self._file.close()
