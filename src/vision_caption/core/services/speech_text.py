"""Testo pronto per la voce, in modalità lezione.

Il prompt chiede formule e simboli già scritti a parole, ma un modello locale
ogni tanto li copia dalla slide: la voce leggerebbe "x²" come "x due" o
salterebbe "≥". Qui i simboli rimasti diventano parole, e una descrizione
più lunga del previsto si ferma alla fine di una frase invece di occupare
mezzo minuto di lezione.
"""

import re


# Prima i simboli legati a ciò che li precede ("x^2", "x - 1"): vanno letti
# finché accanto c'è ancora il carattere originale, prima che "²" diventi
# "al quadrato". Il lookbehind di Python vuole una larghezza fissa.
_BEFORE = r"(?<=[\w)²³])"
_CONTEXTUAL = (
    # Il trattino è un meno solo fra operandi di una formula: un numero, una
    # lettera isolata, una parentesi. "Titolo - sottotitolo" e "semi-asse"
    # restano come sono. Va letto prima di "^", che toglie la cifra a sinistra.
    (
        re.compile(
            # Fra due numeri solo se spaziato: "2025-2026" è un intervallo.
            r"(?<=[\d)²³])\s+-\s+(?=[\d(])"
            r"|(?<=[)²³])-(?=[\d(])"
            r"|(?<=\b[a-zA-Z])\s*-\s*(?=\d)"
            r"|(?<=\b[a-zA-Z])\s+-\s+(?=[a-zA-Z(])"
            r"|(?<=\^2)\s+-\s+(?=[\w(])"
        ),
        " meno ",
    ),
    (re.compile(rf"{_BEFORE}\s*\^\s*2\b"), " al quadrato"),
    (re.compile(rf"{_BEFORE}\s*\^\s*3\b"), " al cubo"),
    (re.compile(rf"{_BEFORE}\s*\^\s*(?=\()"), " alla "),
    (re.compile(rf"{_BEFORE}\s*\^\s*(\w+)"), r" alla \1"),
    # La barra spaziata è una divisione; "2025/26" o "3/7" restano scritti.
    (re.compile(r"(?<=[\w)²³])\s+/\s+(?=[\w(])"), " diviso "),
)

# Simboli che hanno una sola lettura sensata, ovunque compaiano. Nelle
# descrizioni di una slide "+", "=", "<", ">" e "*" stanno solo nelle formule.
_SYMBOLS = (
    ("²", " al quadrato"),
    ("³", " al cubo"),
    ("√", " radice di "),
    ("±", " più o meno "),
    ("≠", " diverso da "),
    ("≤", " minore o uguale a "),
    ("≥", " maggiore o uguale a "),
    ("≈", " circa uguale a "),
    ("∞", " infinito "),
    ("π", " pi greco "),
    ("→", " tende a "),
    ("×", " per "),
    ("÷", " diviso "),
    ("−", " meno "),
    ("%", " per cento"),
    ("+", " più "),
    ("=", " uguale "),
    ("<", " minore di "),
    (">", " maggiore di "),
    ("*", " per "),
)

_SENTENCE_END = re.compile(r"[.!?](?=\s|$)")
_SLIDE_PREAMBLE = re.compile(
    r"(?i)^\s*(?:(?:un|uno|una|il|lo|la)\s+)?"
    r"(?:(?:pannello|schermo)\s+(?:con|che mostra)\s+(?:(?:una|la)\s+)?)?"
    r"(?:slide|diapositiva)\s+(?:con\s+(?:il\s+)?titolo|dal titolo|intitolata)\s*:?\s*"
)


def strip_lesson_preamble(text: str) -> str:
    # Solo involucri iniziali riconoscibili, mai parole nel contenuto.
    text = _SLIDE_PREAMBLE.sub("Titolo: ", text, count=1)
    text = re.sub(r"(?im)^Schermo con testo che dice\s+", "", text)
    return re.sub(r"(?im)^Schermo con immagine di\s+", "Immagine: ", text)
_LESSON_SECTION = re.compile(
    r"(?im)^[ \t]*(?P<label>titolo|testo|immagine|figura)\b(?::|(?= di\b))"
)


def lesson_sections(text: str) -> tuple[str, list[str]]:
    """Separa le figure marcate dal VLM, senza dedurne di inesistenti."""
    matches = list(_LESSON_SECTION.finditer(text))
    if not matches:
        return text, []
    content = [text[:matches[0].start()].strip()]
    figures = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[match.start():end].strip()
        if match.group("label").casefold() in ("immagine", "figura"):
            if text[match.end():end].strip():
                figures.append(section)
        else:
            content.append(section)
    return "\n".join(part for part in content if part), figures


def has_visual_description(text: str) -> bool:
    return bool(lesson_sections(text)[1])


def speakable_math(text: str) -> str:
    for pattern, words in _CONTEXTUAL:
        text = pattern.sub(words, text)
    for symbol, words in _SYMBOLS:
        text = text.replace(symbol, words)
    text = re.sub(r"\s+([.,;:!?)])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def limit_words(text: str, max_words: int) -> str:
    """Taglia alla fine dell'ultima frase completa entro max_words parole."""
    if max_words <= 0:
        return ""
    words = text.split()
    if len(words) <= max_words:
        return text
    head = " ".join(words[:max_words])
    ends = list(_SENTENCE_END.finditer(head))
    if ends:
        return head[: ends[-1].end()]
    return head.rstrip(",;:") + "."


def lesson_speech(max_words: int):
    """Il filtro completo della modalità lezione, da applicare prima della voce."""

    def prepare(text: str) -> str:
        text = strip_lesson_preamble(text)
        content, figures = lesson_sections(text)
        content = speakable_math(content)
        figures = [speakable_math(figure) for figure in figures]
        if not figures:
            return limit_words(content, max_words)
        if len((content + " " + " ".join(figures)).split()) <= max_words:
            return "\n".join(part for part in [content, *figures] if part)
        # Fino a metà del budget per le figure, al massimo dodici parole
        # riservate a ciascuna. Il testo inutilizzato torna alle immagini.
        quota = max(1, min(12, max_words // (2 * len(figures))))
        reserves = [min(quota, len(figure.split())) for figure in figures]
        body = limit_words(content, max(0, max_words - sum(reserves))) if content else ""
        remaining = max_words - len(body.split())
        kept = []
        for index, figure in enumerate(figures):
            budget = max(0, remaining - sum(reserves[index + 1:]))
            if budget:
                kept.append(limit_words(figure, budget))
                remaining -= len(kept[-1].split())
        return "\n".join(part for part in [body, *kept] if part)

    return prepare
