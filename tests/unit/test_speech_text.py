import pytest

from vision_caption.core.services.speech_text import (
    lesson_speech,
    limit_words,
    speakable_math,
)


@pytest.mark.parametrize(
    ("written", "spoken"),
    [
        ("x² + 2x − 3 = 0", "x al quadrato più 2x meno 3 uguale 0"),
        ("y = x^2 - 4", "y uguale x al quadrato meno 4"),
        ("x^(n-1)", "x alla (n meno 1)"),
        ("(−b ± √(b² − 4ac)) / 2a", "(meno b più o meno radice di (b al quadrato meno 4ac)) diviso 2a"),
        ("Se b² − 4ac < 0", "Se b al quadrato meno 4ac minore di 0"),
        ("f(x) ≥ 0", "f(x) maggiore o uguale a 0"),
        ("Il gas vale 45%", "Il gas vale 45 per cento"),
        ("π ≈ 3,14", "pi greco circa uguale a 3,14"),
    ],
)
def test_formulas_become_words(written, spoken) -> None:
    assert speakable_math(written) == spoken


@pytest.mark.parametrize(
    "prose",
    [
        "Titolo - sottotitolo",
        "auto-mobile e semi-asse",
        "COVID-19",
        "anni 2025-2026",
        "slide 3/7",
    ],
)
def test_ordinary_text_is_left_alone(prose) -> None:
    assert speakable_math(prose) == prose


def test_long_text_stops_at_the_last_full_sentence() -> None:
    text = "Prima frase breve. Seconda frase lunga che non finisce entro il limite."

    assert limit_words(text, 6) == "Prima frase breve."
    assert limit_words(text, 50) == text


def test_long_sentence_without_full_stop_is_cut_cleanly() -> None:
    assert limit_words("uno due tre quattro cinque sei", 4) == "uno due tre quattro."


def test_lesson_speech_applies_both() -> None:
    prepare = lesson_speech(max_words=6)

    assert prepare("Formula: x² = 4. Poi molte altre parole qui.") == (
        "Formula: x al quadrato uguale 4."
    )
