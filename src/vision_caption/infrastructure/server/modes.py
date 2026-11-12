"""L'endpoint che trasforma una frase in una modalità.

«Adatta a tutti» non vuol dire configurabile da chi sa usare un terminale.
Lo script ``crea_modalita.py`` fa già questo lavoro, ma chiede una riga di
comando sulla macchina del server: una persona cieca che vuole la sua
modalità per l'officina o per la pesca deve poterla chiedere dal telefono,
con la sua voce, usando la dettatura della tastiera.

Spento di suo, per una ragione sola: creare una modalità costa una chiamata
a un modello grande e scrive un file nella cartella delle modalità. Se il
server è pubblico dietro un tunnel - come è questo - un endpoint aperto che
fa entrambe le cose lo paga qualcun altro. Si accende con
MODE_CREATION_ENABLED=true, da chi sa dove è esposto il server, e anche
allora c'è un'attesa fra una creazione e la successiva.
"""

import time

from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from pydantic import BaseModel, Field

from vision_caption.adapters.vlm.mode_profile_generator import (
    ModeProfileError,
    ModeProfileGenerator,
)
from vision_caption.adapters.vlm.prompts import register_profile
from vision_caption.infrastructure.mode_profiles import save_profile
from vision_caption.infrastructure.settings import AppSettings


router = APIRouter()

# Una frase, non un tema: oltre questa lunghezza non è più una situazione
# descritta a parole proprie ed è solo un modo per far scrivere al modello
# qualcosa d'altro.
DESCRIPTION_MAX_LENGTH = 400
DESCRIPTION_MIN_LENGTH = 15


class ModeRequest(BaseModel):
    description: str = Field(
        min_length=DESCRIPTION_MIN_LENGTH,
        max_length=DESCRIPTION_MAX_LENGTH,
    )


class ModeCreated(BaseModel):
    id: str
    label: str


_last_creation: float | None = None


def _settings(request: Request) -> AppSettings:
    settings = getattr(request.app.state, "settings", None)
    return settings if isinstance(settings, AppSettings) else AppSettings()


@router.get("/modes")
def list_modes(request: Request) -> dict:
    """Le modalità che questo server ha caricato, e se se ne possono creare."""
    return {
        "modes": getattr(request.app.state, "available_modes", []) or [],
        "can_create": _settings(request).server.mode_creation_enabled,
    }


@router.post("/modes", response_model=ModeCreated, status_code=201)
async def create_mode(payload: ModeRequest, request: Request) -> ModeCreated:
    global _last_creation
    settings = _settings(request)
    if not settings.server.mode_creation_enabled:
        raise HTTPException(
            status_code=403,
            detail=(
                "La creazione delle modalità è spenta su questo server. "
                "Si accende con MODE_CREATION_ENABLED=true."
            ),
        )

    attesa = settings.server.mode_creation_cooldown_seconds
    if _last_creation is not None:
        trascorso = time.monotonic() - _last_creation
        if trascorso < attesa:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Una modalità alla volta: riprova fra "
                    f"{round(attesa - trascorso)} secondi."
                ),
            )

    generator = ModeProfileGenerator(api_key=settings.vlm.api_key)
    try:
        profile = await generator.generate(payload.description)
    except ModeProfileError as error:
        # La frase era comprensibile ma il modello ha riempito male il
        # modulo: è un errore del modello, non della persona.
        logger.warning("Modalità non creata: {}", error)
        raise HTTPException(status_code=502, detail=str(error)) from error

    _last_creation = time.monotonic()
    path = save_profile(profile, settings.server.profiles_dir)
    # Da qui in giù la modalità nuova è indistinguibile da lesson o museum,
    # e vale per le sessioni che si apriranno dopo.
    register_profile(profile)
    modes = getattr(request.app.state, "available_modes", None)
    if isinstance(modes, list) and not any(
        mode.get("id") == profile.id for mode in modes
    ):
        modes.append({"id": profile.id, "label": profile.name})
    logger.info("Modalità '{}' creata e salvata in {}", profile.id, path)
    return ModeCreated(id=profile.id, label=profile.name)
