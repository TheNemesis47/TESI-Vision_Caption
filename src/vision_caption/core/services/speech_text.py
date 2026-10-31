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
        return limit_words(speakable_math(text), max_words)

    return prepare
