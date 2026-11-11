"""Le modalità salvate su disco, una per file.

Stanno in una cartella accanto al progetto (``profili/`` per impostazione
predefinita) perché devono poter nascere dopo il deploy: le crea lo script
``scripts/crea_modalita.py`` con un modello capace, o le scrive a mano chi
sa cosa gli serve. Un file illeggibile non ferma il server: viene segnalato
e saltato, e le modalità scritte nel codice restano comunque disponibili.
"""

import json
from pathlib import Path

from loguru import logger
from pydantic import ValidationError

from vision_caption.core.domain.mode_profile import ModeProfile


def load_profiles(directory: Path) -> dict[str, ModeProfile]:
    """Legge i profili validi nella cartella, saltando quelli rotti."""
    profiles: dict[str, ModeProfile] = {}
    if not directory.is_dir():
        return profiles

    for path in sorted(directory.glob("*.json")):
        try:
            profile = ModeProfile.model_validate_json(path.read_text("utf-8"))
        except (ValidationError, json.JSONDecodeError, OSError) as error:
            logger.warning(
                "Modalità ignorata, il file non è valido: {} ({})",
                path.name,
                type(error).__name__,
            )
            continue
        if profile.id != path.stem:
            logger.warning(
                "Modalità ignorata: il file {} contiene l'id '{}'",
                path.name,
                profile.id,
            )
            continue
        profiles[profile.id] = profile
    return profiles


def save_profile(profile: ModeProfile, directory: Path) -> Path:
    """Scrive il profilo come <id>.json, leggibile e modificabile a mano."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{profile.id}.json"
    path.write_text(
        json.dumps(profile.model_dump(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path
