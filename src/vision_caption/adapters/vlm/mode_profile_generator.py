"""Una modalità nuova a partire da una frase detta a parole proprie.

Le modalità del codice - lezione, museo, generale - sono state scritte e
tarate a mano. Le altre le scrive un modello più grande di quello che poi
descrive le immagini: scrivere un buon profilo è un lavoro di linguaggio che
si fa una volta sola, mentre descrivere i fotogrammi è un lavoro di vista che
si fa due volte al secondo. Costa di più e va benissimo: succede una volta.

Il modello non scrive un prompt. Riempie le caselle del template
(``ModeProfile``), e lo scheletro che la pipeline sa leggere resta nel
codice: un profilo sbagliato descrive male, non rompe la voce.

Questo modulo è la parte riusabile - la usano sia lo script da terminale sia
l'endpoint che riceve la frase dal telefono, perché «adatta a tutti» non
vuol dire configurabile da chi sa usare un terminale.
"""

import json

import httpx
from pydantic import ValidationError

from vision_caption.core.domain.mode_profile import ModeProfile


# Non è il modello che descrive i fotogrammi: qui serve capire una richiesta
# scritta male e trasformarla in istruzioni precise, una volta sola.
DEFAULT_MODEL = "google/gemini-2.5-pro"

EXAMPLE = {
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
        "il prodotto inquadrato, con marca e formato se si leggono",
        "i cartelli di reparto, di prezzo e di offerta",
        "gli ostacoli sul percorso: carrelli, pedane, pilastri",
    ],
    "ignore": [
        "il pavimento e il soffitto",
        "gli altri clienti",
        "la decorazione degli scaffali",
    ],
    "written_text": (
        "Leggi per intero marca, formato, prezzo e scadenza: sono le "
        "informazioni che una persona cieca non può procurarsi da sola."
    ),
    "when_nothing": "Resta in silenzio: in un corridoio vuoto non c'è niente da dire.",
    "pointing": (
        "Di' che prodotto è, quanto costa e ogni scritta che porta: nome, "
        "formato, peso, scadenza."
    ),
    "max_words": 25,
    "memory_item": "prodotto",
}

INSTRUCTIONS = """Sei un progettista di assistenti vocali per persone cieche e ipovedenti.

Ricevi la descrizione di una situazione e riempi un modulo in JSON con queste
caselle. Non scrivi un prompt: riempi il modulo, e qualcun altro lo monta.

- id: una parola sola, minuscola, senza accenti, 3-30 caratteri (es. officina, pesca, supermercato).
- name: il nome leggibile della modalità, 2-60 caratteri.
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
""" + json.dumps(EXAMPLE, ensure_ascii=False, indent=2)


class ModeProfileError(RuntimeError):
    """La frase non è diventata una modalità, con un motivo da leggere."""


def extract_profile(content: str, forced_id: str | None = None) -> ModeProfile:
    """Il JSON del modello diventa un profilo validato, o un errore chiaro."""
    text = content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        text = text.removeprefix("json").strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ModeProfileError(
            f"Il modello non ha risposto con un modulo: {content[:200]!r}"
        )
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError as error:
        raise ModeProfileError(f"Modulo illeggibile: {error}") from error
    if forced_id:
        data["id"] = forced_id
    try:
        return ModeProfile.model_validate(data)
    except ValidationError as error:
        raise ModeProfileError(
            f"Il modello ha riempito male il modulo: {error}"
        ) from error


class ModeProfileGenerator:
    """Chiede a un modello capace di riempire il modulo di una modalità."""

    def __init__(
        self,
        api_key: str,
        model_name: str = DEFAULT_MODEL,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout_seconds: float = 180.0,
    ) -> None:
        self._api_key = api_key
        self._model_name = model_name
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    async def generate(
        self,
        description: str,
        forced_id: str | None = None,
    ) -> ModeProfile:
        payload = {
            "model": self._model_name,
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": INSTRUCTIONS},
                {"role": "user", "content": f"La situazione: {description}"},
            ],
        }
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPError as error:
            raise ModeProfileError(
                f"Il modello non ha risposto: {error}"
            ) from error
        except (KeyError, IndexError, ValueError) as error:
            raise ModeProfileError(
                f"Risposta del modello inattesa: {error}"
            ) from error
        return extract_profile(content, forced_id)
