"""Campioni per la valutazione: una cartella per ogni chiamata al modello.

    <output_dir>/<sessione>/<nome>/
        frame.jpg              (AUTO) l'immagine descritta
        01_context.jpg ...     (POINTING) le tre immagini inviate al modello
        caption.json           descrizione, esito, tempi, rilevazioni

La sessione è la stessa del log di ricerca, così ogni riga ``utterance`` o
``pointing_result`` porta alla sua immagine.
"""

import json
from pathlib import Path
from typing import Any

from loguru import logger


class FileCaptionSampleStore:
    def __init__(self, session_dir: Path) -> None:
        self._session_dir = session_dir

    def save(
        self,
        name: str,
        images: dict[str, bytes],
        record: dict[str, Any],
    ) -> None:
        sample_dir = self._session_dir / name
        try:
            sample_dir.mkdir(parents=True, exist_ok=True)
            for file_name, content in images.items():
                (sample_dir / file_name).write_bytes(content)
            (sample_dir / "caption.json").write_text(
                json.dumps(record, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
        except OSError as error:
            logger.warning(f"Campione non salvato in {sample_dir}: {error}")
