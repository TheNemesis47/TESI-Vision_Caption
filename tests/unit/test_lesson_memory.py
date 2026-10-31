import pytest

from vision_caption.core.services.lesson_memory import LessonMemory, split_page_tag


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("PAGINA: 3/7\nTitolo: Le derivate.", (3, 7, "Titolo: Le derivate.")),
        ("Pagina: 4 di 7\nUn grafico a barre.", (4, 7, "Un grafico a barre.")),
        ("PAGINA: 2\nTabella.", (2, None, "Tabella.")),
        ("PAGINA: nessuna\nUn libro aperto.", (None, None, "Un libro aperto.")),
        ("PAGINA: 3/7 Titolo: Le derivate.", (3, 7, "Titolo: Le derivate.")),
        ("PAGINA: 5/7\nNIENTE", (5, 7, "NIENTE")),
        ("Titolo: Le derivate.", (None, None, "Titolo: Le derivate.")),
        ("PAGINA: in basso a destra\nTabella.", (None, None, "Tabella.")),
    ],
)
def test_page_tag_is_split_from_the_spoken_text(text, expected) -> None:
    assert split_page_tag(text) == expected


def test_context_lists_remembered_slides_in_order() -> None:
    memory = LessonMemory(clock=lambda: 0.0)
    assert memory.context() is None

    memory.remember(2, 7, "Titolo: Popolazione italiana.")
    memory.remember(3, 7, "Grafico a linee in crescita.")

    context = memory.context()
    assert context.index("Slide 2 di 7: Titolo: Popolazione") < context.index(
        "Slide 3 di 7: Grafico"
    )


def test_same_page_replaces_the_old_note() -> None:
    memory = LessonMemory(clock=lambda: 0.0)
    memory.remember(3, 7, "Primo punto.")
    memory.remember(4, 7, "Tabella.")
    memory.remember(3, 7, "Primo e secondo punto.")

    assert [(note.page, note.text) for note in memory.notes] == [
        (4, "Tabella."),
        (3, "Primo e secondo punto."),
    ]


def test_a_different_total_starts_a_new_presentation() -> None:
    memory = LessonMemory(clock=lambda: 0.0)
    memory.remember(6, 7, "Ciclo dell'acqua.")
    memory.remember(1, 12, "Titolo: La fotosintesi.")

    assert [note.total for note in memory.notes] == [12]


def test_only_the_last_slides_are_kept() -> None:
    memory = LessonMemory(max_notes=2, clock=lambda: 0.0)
    for page in (1, 2, 3):
        memory.remember(page, 7, f"Slide {page}.")

    assert [note.page for note in memory.notes] == [2, 3]


def test_memory_is_forgotten_after_a_long_pause() -> None:
    now = [0.0]
    memory = LessonMemory(max_idle_seconds=900, clock=lambda: now[0])
    memory.remember(1, 7, "Titolo.")

    now[0] = 901.0

    assert memory.context() is None


def test_same_page_without_new_content_is_a_repeat() -> None:
    memory = LessonMemory(clock=lambda: 0.0)
    memory.remember(3, 7, "Titolo: Popolazione italiana. Crescita fino al 2010.")

    assert memory.is_repeat(3, 7, "Titolo: Popolazione. La curva sale fino al 2010.")
    assert not memory.is_repeat(4, 7, "Grafico a linee in crescita.")


def test_more_content_on_the_same_slide_is_not_a_repeat() -> None:
    memory = LessonMemory(clock=lambda: 0.0)
    memory.remember(3, 7, "Titolo: Le derivate. Primo punto.")

    assert not memory.is_repeat(
        3, 7, "Titolo: Le derivate. Primo punto. Secondo punto. Terzo punto nuovo."
    )


def test_same_title_without_page_numbers_is_a_repeat() -> None:
    memory = LessonMemory(clock=lambda: 0.0)
    memory.remember(None, None, "Titolo: Fonti di energia in Italia (%). Gas 45, rinnovabili 30.")

    assert memory.is_repeat(
        None, None, "Titolo: Fonti di energia in Italia percentuale. Barre: gas, rinnovabili."
    )
    assert not memory.is_repeat(None, None, "Titolo: Stati della materia. Tabella.")


def test_next_page_with_the_same_title_is_a_new_slide() -> None:
    memory = LessonMemory(clock=lambda: 0.0)
    memory.remember(3, 7, "Titolo: Popolazione italiana. Crescita fino al 2010.")

    assert not memory.is_repeat(4, 7, "Titolo: Popolazione italiana. Grafico a linee.")


def test_same_page_number_with_a_different_title_is_a_new_slide() -> None:
    memory = LessonMemory(clock=lambda: 0.0)
    memory.remember(3, 7, "Titolo: Le derivate. Regola della catena.")

    assert not memory.is_repeat(3, 7, "Titolo: Stati della materia. Tabella.")
