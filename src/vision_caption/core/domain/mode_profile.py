"""Il template di una modalità: le caselle che un profilo deve riempire.

Una modalità non è un prompt scritto a mano. È un profilo con caselle fisse
- a chi serve, quando parlare, cosa descrivere, cosa ignorare, come trattare
le scritte, quante parole - che il server monta dentro uno scheletro
immutabile. Lo scheletro è ciò che il resto della pipeline sa leggere: le
righe ``Titolo:``, ``Testo:`` e ``Immagine:`` diventano voce, la riga della
pagina alimenta la memoria, la parola convenuta fa tacere il sistema.

Separare le due cose ha una conseguenza pratica: il testo scritto da un
modello - o da un insegnante dalle impostazioni - finisce solo dentro le
caselle, e non può rompere il formato che la pipeline analizza. Una modalità
sbagliata descrive male; non manda in pezzi la voce.
"""

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


SLUG = re.compile(r"^[a-z0-9]([a-z0-9-]{1,30}[a-z0-9])$")

# Le modalità scritte nel codice: un profilo non può sovrascriverle, perché
# sono quelle su cui sono stati fatti i test dello studio.
BUILTIN_CONTEXTS = ("general", "lesson", "museum")


class ModeProfile(BaseModel):
    """Una modalità descritta per caselle, non per prompt."""

    id: str = Field(description="Nome breve del file e valore di CAPTION_CONTEXT")
    name: str = Field(min_length=2, max_length=60, description="Nome leggibile")
    purpose: str = Field(
        min_length=10,
        max_length=300,
        description="A chi serve e in che situazione, in una riga",
    )
    speak_when: str = Field(
        min_length=10,
        max_length=400,
        description="Che cosa conta come novità da dire",
    )
    describe: list[str] = Field(
        min_length=2,
        max_length=6,
        description="Che cosa descrivere, dalla cosa più importante in giù",
    )
    ignore: list[str] = Field(
        default_factory=list,
        max_length=6,
        description="Che cosa non nominare mai",
    )
    written_text: str = Field(
        min_length=10,
        max_length=400,
        description="Come trattare scritte, etichette e cartelli",
    )
    when_nothing: str = Field(
        min_length=5,
        max_length=300,
        description="Che cosa fare quando non c'è niente di utile",
    )
    pointing: str = Field(
        min_length=10,
        max_length=600,
        description="Che cosa descrivere quando l'utente indica col dito",
    )
    max_words: int = Field(default=40, ge=15, le=60)
    memory_item: str = Field(
        default="scena",
        min_length=3,
        max_length=20,
        description="Come chiamare una cosa già descritta, al singolare",
    )

    model_config = ConfigDict(frozen=True, extra="forbid")

    @field_validator("id")
    @classmethod
    def _valid_id(cls, value: str) -> str:
        if not SLUG.match(value):
            raise ValueError(
                "L'id va in minuscolo, da due a trentadue caratteri, "
                "con trattini al posto degli spazi"
            )
        if value in BUILTIN_CONTEXTS:
            raise ValueError(
                f"'{value}' è una modalità del codice: scegli un altro nome"
            )
        return value

    @field_validator("describe", "ignore")
    @classmethod
    def _clean_lines(cls, value: list[str]) -> list[str]:
        lines = [line.strip().rstrip(".") for line in value if line.strip()]
        if any(len(line) > 200 for line in lines):
            raise ValueError("Ogni riga sta in duecento caratteri")
        return lines

    @field_validator("memory_item")
    @classmethod
    def _single_word(cls, value: str) -> str:
        word = value.strip().casefold()
        if " " in word:
            raise ValueError("memory_item è una parola sola, al singolare")
        return word
