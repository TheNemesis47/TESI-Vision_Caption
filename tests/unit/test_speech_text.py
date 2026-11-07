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


def test_lesson_budget_keeps_the_picture_after_long_slide_text() -> None:
    text = "Titolo: Realtà virtuale.\nTesto: " + "contenuto " * 60
    image = "Immagine: stanza con tavolo nero, sedie rosse e mobile blu."
    spoken = lesson_speech(50)(text + ".\n" + image)
    assert "stanza con tavolo nero, sedie rosse e mobile blu." in spoken
    assert spoken.index("Il titolo è") < spoken.index("Nell'immagine")
    assert "Immagine:" not in spoken
    assert len(spoken.split()) <= 50


def test_lesson_budget_keeps_each_picture_and_puts_text_first() -> None:
    text = "Immagine: tavolo nero e sedie rosse.\nImmagine: persona con visore giallo.\nTesto: " + "parola " * 60
    spoken = lesson_speech(50)(text)
    assert "tavolo nero" in spoken and "visore giallo" in spoken
    assert spoken.startswith("parola ")
    assert len(spoken.split()) <= 50


@pytest.mark.parametrize("prefix", [
    "Un pannello con una slide con il titolo: ",
    "Una slide con il titolo ",
    "Schermo con una slide dal titolo ",
])
def test_lesson_preamble_goes_directly_to_the_title(prefix) -> None:
    assert lesson_speech(50)(prefix + "Realtà virtuale.\nTesto: Presentazione A.") == (
        "Il titolo è Realtà virtuale.\nPresentazione A."
    )


def test_content_that_mentions_a_screen_or_slide_is_preserved() -> None:
    text = "Titolo: Come costruire uno schermo.\nTesto: Una slide spiega i pixel."
    assert lesson_speech(50)(text) == (
        "Il titolo è Come costruire uno schermo.\nUna slide spiega i pixel."
    )


def test_lesson_sections_become_conversational_speech() -> None:
    text = (
        "Titolo: Entrare in una stanza virtuale\n"
        "Testo: Un visore pesa circa 500 grammi.\n"
        "Immagine: Una stanza con tavolo nero e sedie rosse."
    )
    spoken = lesson_speech(50)(text)
    assert spoken == (
        "Il titolo è Entrare in una stanza virtuale.\n"
        "Un visore pesa circa 500 grammi.\n"
        "Nell'immagine, una stanza con tavolo nero e sedie rosse."
    )


def test_text_only_slide_does_not_repeat_title_or_read_its_styling() -> None:
    # Risposta effettivamente letta nella sessione 9354113f2536, frame 23.
    text = (
        'Titolo: La realtà virtuale\n'
        'Testo: La slide mostra il titolo "La realtà virtuale" in bianco su '
        'sfondo blu scuro, preceduto da "Presentazione A" in testo più piccolo.'
    )
    assert lesson_speech(50)(text) == "Il titolo è La realtà virtuale.\nPresentazione A."


def test_repeated_title_in_the_text_is_said_once() -> None:
    assert lesson_speech(50)(
        "Titolo: La realtà virtuale\nTesto: La realtà virtuale."
    ) == "Il titolo è La realtà virtuale."


def test_natural_picture_and_its_position_are_preserved_without_another_prefix() -> None:
    from vision_caption.core.services.speech_text import has_visual_description

    text = "Titolo: Esempio\nImmagine: Nell'immagine si vede un tavolo nero.\nTesto: A destra è scritto: 500 grammi."
    spoken = lesson_speech(50)(text)
    assert spoken == "Il titolo è Esempio.\nA destra è scritto: 500 grammi.\nNell'immagine si vede un tavolo nero."
    assert has_visual_description(spoken)
    assert lesson_speech(50)(spoken) == spoken
