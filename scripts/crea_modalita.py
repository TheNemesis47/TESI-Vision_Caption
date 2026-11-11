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

import httpx
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vision_caption.adapters.vlm.prompts import (  # noqa: E402
    render_auto_prompt,
    render_pointing_context,
)
from vision_caption.core.domain.mode_profile import ModeProfile  # noqa: E402
from vision_caption.infrastructure.mode_profiles import save_profile  # noqa: E402


# Non è il modello che descrive i fotogrammi: qui serve capire una richiesta
# scritta male e trasformarla in istruzioni precise, una volta sola.
DEFAULT_MODEL = "google/gemini-2.5-pro"
DEFAULT_DIR = Path(__file__).resolve().parents[1] / "profili"

ESEMPIO = {
    "id": "supermercato",
    "name": "Spesa al supermercato",
    "purpose": (
        "Accompagni una persona cieca o ipovedente che fa la spesa da sola "
        "in un supermercato."
    ),
    "speak_when": (
        "Quando cambia il prodotto inquadrato, quando compare un cartello di "
        "reparto o di prezzo, quando davanti c'è un ostacolo o una cassa."
    ),
    "describe": [
        "il prodotto che si ha in mano o davanti: che cos'è, la marca, il formato",
        "il prezzo e le offerte, come stanno scritti sul cartellino",
        "il reparto e la direzione del corridoio",
        "ostacoli vicini: carrelli, pedane, scatoloni, scale",
    ],
    "ignore": [
        "gli altri clienti e il personale",
        "il colore degli scaffali e del pavimento",
    ],
    "written_text": (
        "Leggi per intero le scritte del prodotto - nome, marca, peso, "
        "scadenza, allergeni - e i cartellini del prezzo, senza riassumerli. "
        "Se la scritta è troppo piccola, dillo invece di indovinare."
    ),
    "when_nothing": (
        "Se nell'inquadratura non c'è né un prodotto né un cartello, resta "
        "in silenzio."
    ),
    "pointing": (
        "Il prodotto indicato col dito: nome, marca, formato e il prezzo del "
        "cartellino sotto, se si legge."
    ),
    "max_words": 40,
    "memory_item": "prodotto",
}

ISTRUZIONI = """Scrivi il profilo di una modalità per VisionCaption, un assistente vocale che descrive in tempo reale quello che la fotocamera di un telefono inquadra a una persona cieca o ipovedente.

Non scrivi un prompt: riempi le caselle di un modulo. Il server le monta dentro uno scheletro fisso che non devi riprodurre (la struttura della risposta, la memoria, i limiti di parole sono già nel codice).

Le caselle:
- id: una parola sola, minuscolo, senza spazi; è il nome del file e il valore di CAPTION_CONTEXT. Non può essere general, lesson o museum.
- name: il nome leggibile, due o tre parole.
- purpose: a chi serve e in che situazione, una frase che comincia con "Accompagni..." o "Assisti...".
- speak_when: che cosa conta come novità in questa situazione. Il sistema parla solo quando c'è qualcosa di nuovo e utile; qui dici cos'è "nuovo e utile" qui.
- describe: da due a sei voci, dalla più importante alla meno importante. Sono cose concrete e visibili, non categorie astratte.
- ignore: fino a sei cose da non nominare mai. Pensa a ciò che riempirebbe la descrizione senza aiutare: superfici, arredi di sfondo, persone estranee.
- written_text: come trattare scritte, etichette, cartelli e numeri in questa situazione. Ricorda che il testo scritto è l'informazione che una persona cieca non può procurarsi da sola: di norma va letto per intero, non riassunto.
- when_nothing: che cosa fare quando non c'è niente di utile. Nel dubbio: restare in silenzio.
- pointing: che cosa descrivere quando la persona indica col dito un bersaglio, in questa situazione.
- max_words: fra 15 e 60. Venticinque per situazioni in movimento, quaranta per situazioni ferme in cui si legge molto.
- memory_item: una parola singolare per "la cosa già descritta" (prodotto, opera, attrezzo, pianta, slide).

Regole:
- Italiano, frasi brevi, concrete, al presente. Niente markdown, niente elenchi dentro le singole caselle.
- Mai attribuire a una persona età, aspetto, etnia, stato di salute o abbigliamento.
- Mai inventare informazioni che la fotocamera non può vedere.
- Rispondi SOLO con l'oggetto JSON, senza spiegazioni e senza blocchi di codice.

Esempio di profilo completo, per capire il livello di dettaglio:
""" + json.dumps(ESEMPIO, ensure_ascii=False, indent=2)


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


def extract_profile(content: str, forced_id: str | None = None) -> ModeProfile:
    """Il JSON del modello diventa un profilo validato, o un errore chiaro."""
    text = content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        text = text.removeprefix("json").strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"Nessun JSON nella risposta: {content[:200]!r}")
    data = json.loads(text[start : end + 1])
    if forced_id:
        data["id"] = forced_id
    return ModeProfile.model_validate(data)


async def ask_model(description: str, model: str, forced_id: str | None) -> ModeProfile:
    payload = {
        "model": model,
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": ISTRUZIONI},
            {"role": "user", "content": f"La situazione: {description}"},
        ],
    }
    headers = {"Authorization": f"Bearer {_api_key()}"}
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
    return extract_profile(content, forced_id)


async def main(args: argparse.Namespace) -> int:
    try:
        profile = await ask_model(args.descrizione, args.modello, args.id)
    except ValidationError as error:
        print("Il modello ha riempito male il modulo:", error, file=sys.stderr)
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
