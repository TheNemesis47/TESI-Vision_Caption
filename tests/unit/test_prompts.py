from vision_caption.adapters.vlm.prompts import auto_prompt, pointing_context


def test_lesson_prompt_requires_concrete_pictures_after_text() -> None:
    prompt = auto_prompt("lesson")
    assert "Immagine:" in prompt
    assert "oggetti" in prompt and "colori" in prompt
    assert "prima il testo" in prompt
    assert "dentro" in prompt
    # Le superfici dell'aula restano escluse come nel contesto generale.
    assert "Non descrivere mai pavimento" in prompt
    assert "pavimento, pareti, soffitto" in auto_prompt("general")


def test_lesson_pointing_picture_has_its_own_description_budget() -> None:
    prompt = pointing_context("lesson")
    assert "fotografie" in prompt and "colori" in prompt
    assert "venti parole" in prompt
