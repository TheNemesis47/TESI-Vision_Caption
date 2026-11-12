"""Crea una modalità nuova descrivendola a parole, con un modello capace.

Le modalità del codice - lezione, museo, generale - sono state scritte e
tarate a mano. Le altre le scrive un modello più grande di quello che poi
descrive le immagini: scrivere un buon profilo è un lavoro di linguaggio che
si fa una volta sola, mentre descrivere i fotogrammi è un lavoro di vista che
si fa due volte al secondo. Costa di più e va benissimo: succede una volta.

Il modello non scrive un prompt. Riempie le caselle del template
(``ModeProfile``): a chi serve, quando parlare, cosa descrivere, cosa
ignorare, come trattare le scritte, quante parole. Lo scheletro che la
pipeline sa leggere resta nel codice, quindi un profilo sbagliato descrive
male ma non rompe la voce.

    uv run python scripts/crea_modalita.py "accompagni una persona cieca
        che va a pescare da riva, con canne, esche e secchielli"

    uv run python scripts/crea_modalita.py --id officina --modello \\
        openai/gpt-5 "una persona cieca che lavora in officina"

Poi si prova con CAPTION_CONTEXT=<id> e si corregge il file a mano: è un
JSON di dieci righe, non un prompt da riscrivere.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vision_caption.adapters.vlm.mode_profile_generator import (  # noqa: E402
    DEFAULT_MODEL,
    ModeProfileError,
    ModeProfileGenerator,
)
from vision_caption.adapters.vlm.prompts import (  # noqa: E402
    render_auto_prompt,
    render_pointing_context,
)
from vision_caption.infrastructure.mode_profiles import save_profile  # noqa: E402


DEFAULT_DIR = Path(__file__).resolve().parents[1] / "profili"


def _api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        for line in env_path.read_text("utf-8").splitlines():
            if line.strip().startswith("OPENROUTER_API_KEY"):
                _, _, value = line.partition("=")
                return value.strip().strip('"').strip("'")
    raise SystemExit("OPENROUTER_API_KEY assente da .env e dall'ambiente")


async def main(args: argparse.Namespace) -> int:
    generator = ModeProfileGenerator(
        api_key=_api_key(), model_name=args.modello
    )
    try:
        profile = await generator.generate(args.descrizione, args.id)
    except ModeProfileError as error:
        print(error, file=sys.stderr)
        return 1

    if args.prova:
        print(json.dumps(profile.model_dump(), ensure_ascii=False, indent=2))
    else:
        path = save_profile(profile, args.cartella)
        print(f"Modalità salvata in {path}")
        print(f"Provala con CAPTION_CONTEXT={profile.id}")

    print("\n--- prompt della modalità automatica ---")
    print(render_auto_prompt(profile))
    print("\n--- istruzioni per il puntamento ---")
    print(render_pointing_context(profile))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("descrizione", help="La situazione, a parole tue")
    parser.add_argument("--id", help="Forza l'id invece di lasciarlo al modello")
    parser.add_argument("--modello", default=DEFAULT_MODEL)
    parser.add_argument("--cartella", type=Path, default=DEFAULT_DIR)
    parser.add_argument(
        "--prova",
        action="store_true",
        help="Stampa il profilo senza salvarlo",
    )
    raise SystemExit(asyncio.run(main(parser.parse_args())))
