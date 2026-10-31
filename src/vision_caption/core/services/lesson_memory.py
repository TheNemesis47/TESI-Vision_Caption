"""Memoria a breve termine delle slide già descritte, per la modalità lezione.

Una slide si capisce meglio sapendo cosa c'era prima: un grafico senza titolo
appartiene all'argomento della slide precedente, e ciò che è già stato detto
non va ripetuto. Il server ricorda le ultime slide descritte e le passa al
modello visivo insieme alla nuova immagine.

Il modello scrive nella prima riga il numero della slide, se lo vede
("PAGINA: 3/7"). Il numero serve a due cose: dire al modello quale slide ha
già descritto e capire quando la presentazione è cambiata (un totale diverso)
e la memoria va azzerata.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass
from difflib import SequenceMatcher
from time import monotonic


PAGE_TAG = "PAGINA"

# "PAGINA:" seguito da 3/7, 3 di 7, 3, oppure da una parola che dice che il
# numero non c'è. Quello che segue sulla stessa riga è già testo da leggere.
_PAGE_PREFIX = re.compile(
    rf"^\s*{PAGE_TAG}\s*:\s*"
    r"(?:(?P<page>\d+)\s*(?:/|di|su)\s*(?P<total>\d+)"
    r"|(?P<lone>\d+)"
    r"|(?:nessuna|nessun numero|non visibile|assente|n/?d|-|\?))"
    r"[\s.,;:]*",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SlideNote:
    page: int | None
    total: int | None
    text: str
    at: float


def split_page_tag(text: str) -> tuple[int | None, int | None, str]:
    """Separa il numero di pagina dal testo da leggere.

    Restituisce pagina, totale e testo. Senza il prefisso, pagina e totale
    sono None e il testo resta com'è: vale per il contesto generale e per i
    modelli che dimenticano la riga.
    """
    stripped = text.strip()
    match = _PAGE_PREFIX.match(stripped)
    if match is None:
        first_line, newline, rest = stripped.partition("\n")
        if newline and first_line.strip().upper().startswith(PAGE_TAG):
            # Una riga PAGINA scritta in un modo imprevisto non va letta.
            return None, None, rest.strip()
        return None, None, stripped
    body = stripped[match.end():].strip()
    if match.group("page") is not None:
        return int(match.group("page")), int(match.group("total")), body
    if match.group("lone") is not None:
        return int(match.group("lone")), None, body
    return None, None, body


_TITLE = re.compile(r"^\s*Titolo\s*:\s*([^\n.]+)", re.IGNORECASE)

# Lo stesso titolo riformulato ("Fonti di energia (%)" e "Fonti di energia
# percentuale") resta sopra questa somiglianza; due slide diverse no.
SAME_TITLE_SIMILARITY = 0.8
# Una descrizione di almeno un terzo più lunga della precedente, sulla stessa
# slide, vuol dire che sono comparsi contenuti nuovi (un'animazione).
NEW_CONTENT_GROWTH = 1.35
# Sotto questa somiglianza due titoli appartengono a slide diverse.
DIFFERENT_TITLE_SIMILARITY = 0.5


def slide_title(text: str) -> str | None:
    match = _TITLE.match(text)
    if match is None:
        return None
    title = re.sub(r"[^\w\s]", " ", match.group(1).casefold())
    return " ".join(title.split()) or None


def _label(note: SlideNote) -> str:
    if note.page is None:
        return "Slide senza numero"
    if note.total is None:
        return f"Slide {note.page}"
    return f"Slide {note.page} di {note.total}"


class LessonMemory:
    def __init__(
        self,
        max_notes: int = 5,
        max_idle_seconds: float = 900.0,
        max_note_chars: int = 400,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._max_notes = max_notes
        self._max_idle_seconds = max_idle_seconds
        self._max_note_chars = max_note_chars
        self._clock = clock
        self._notes: list[SlideNote] = []

    @property
    def notes(self) -> tuple[SlideNote, ...]:
        self._forget_if_idle()
        return tuple(self._notes)

    def context(self) -> str | None:
        """Le slide ricordate, come testo da aggiungere al prompt."""
        notes = self.notes
        if not notes:
            return None
        lines = [
            "Slide già descritte allo studente, dalla meno recente alla più recente:"
        ]
        lines.extend(f"- {_label(note)}: {note.text}" for note in notes)
        return "\n".join(lines)

    def is_repeat(self, page: int | None, total: int | None, text: str) -> bool:
        """Vero se la slide è già stata descritta e non ha contenuti nuovi.

        Il testo da solo non basta: lo stesso grafico descritto due volte può
        avere parole diversissime. Contano il numero di pagina e, quando
        manca, il titolo dell'ultima slide descritta.
        """
        notes = self.notes
        if not notes:
            return False
        previous: SlideNote | None = None
        if page is not None:
            previous = next(
                (
                    note
                    for note in notes
                    if note.page == page and (total is None or note.total in (None, total))
                ),
                None,
            )
        # Il titolo decide solo quando i numeri di pagina mancano: con i numeri,
        # una slide che continua l'argomento (stesso titolo, pagina diversa)
        # è una slide nuova.
        if previous is None and page is None and notes[-1].page is None:
            title = slide_title(text)
            last_title = slide_title(notes[-1].text)
            if title and last_title and SequenceMatcher(
                None, title, last_title
            ).ratio() >= SAME_TITLE_SIMILARITY:
                previous = notes[-1]
        if previous is None:
            return False
        # Un numero di pagina può essere letto male o inventato: due titoli
        # chiaramente diversi sono due slide, qualunque numero porti la pagina.
        title, previous_title = slide_title(text), slide_title(previous.text)
        if title and previous_title and SequenceMatcher(
            None, title, previous_title
        ).ratio() < DIFFERENT_TITLE_SIMILARITY:
            return False
        return len(text.split()) < NEW_CONTENT_GROWTH * len(previous.text.split())

    def remember(self, page: int | None, total: int | None, text: str) -> None:
        self._forget_if_idle()
        last_total = next(
            (note.total for note in reversed(self._notes) if note.total), None
        )
        if total is not None and last_total is not None and total != last_total:
            # Un totale diverso è un'altra presentazione: il contesto vecchio
            # confonderebbe il modello invece di aiutarlo.
            self._notes.clear()
        if page is not None:
            self._notes = [note for note in self._notes if note.page != page]
        self._notes.append(
            SlideNote(
                page=page,
                total=total,
                text=text[: self._max_note_chars],
                at=self._clock(),
            )
        )
        del self._notes[: -self._max_notes]

    def clear(self) -> None:
        self._notes.clear()

    def _forget_if_idle(self) -> None:
        if self._notes and (
            self._clock() - self._notes[-1].at > self._max_idle_seconds
        ):
            self._notes.clear()
