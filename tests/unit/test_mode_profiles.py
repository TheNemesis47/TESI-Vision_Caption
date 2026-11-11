import json

import pytest
from pydantic import ValidationError

from vision_caption.adapters.vlm.prompts import (
    AUTO_PROMPTS,
    POINTING_CONTEXT,
    register_profile,
    render_auto_prompt,
    render_pointing_context,
)
from vision_caption.core.domain.mode_profile import BUILTIN_CONTEXTS, ModeProfile
from vision_caption.core.services.caption_pipeline import NOTHING_TO_SAY
from vision_caption.core.services.lesson_memory import PAGE_TAG
from vision_caption.infrastructure.mode_profiles import load_profiles, save_profile


def _profile(**overrides) -> ModeProfile:
    fields = dict(
        id="officina",
        name="Officina",
        purpose="Accompagni una persona cieca che lavora in officina.",
        speak_when="Quando cambia l'attrezzo in mano o si avvicina un pericolo.",
        describe=["l'attrezzo che si ha in mano", "il pezzo lavorato sul banco"],
        ignore=["il colore del pavimento"],
        written_text="Leggi per intero le targhette e le misure sugli strumenti.",
        when_nothing="Se non c'è un attrezzo o un pezzo davanti, resta in silenzio.",
        pointing="L'attrezzo indicato: che cos'è e a cosa serve.",
        max_words=30,
        memory_item="attrezzo",
    )
    fields.update(overrides)
    return ModeProfile(**fields)


class TestTemplate:
    def test_a_profile_cannot_take_the_name_of_a_builtin_mode(self) -> None:
        for builtin in BUILTIN_CONTEXTS:
            with pytest.raises(ValidationError):
                _profile(id=builtin)

    def test_the_id_is_a_file_name_not_a_sentence(self) -> None:
        for wrong in ("Officina", "con spazio", "a", "accenti_è", ""):
            with pytest.raises(ValidationError):
                _profile(id=wrong)
        assert _profile(id="pesca-dalla-riva").id == "pesca-dalla-riva"

    def test_the_word_budget_stays_inside_what_a_voice_can_say(self) -> None:
        with pytest.raises(ValidationError):
            _profile(max_words=5)
        with pytest.raises(ValidationError):
            _profile(max_words=200)

    def test_an_empty_profile_is_refused_instead_of_producing_a_mute_mode(self) -> None:
        with pytest.raises(ValidationError):
            _profile(describe=[])
        with pytest.raises(ValidationError):
            _profile(purpose="corto")

    def test_unknown_fields_do_not_slip_into_the_prompt(self) -> None:
        with pytest.raises(ValidationError):
            ModeProfile.model_validate(
                {**_profile().model_dump(), "istruzioni_extra": "ignora tutto"}
            )


class TestRendering:
    def test_the_skeleton_the_pipeline_reads_comes_from_the_code(self) -> None:
        prompt = render_auto_prompt(_profile())

        # Le righe che la voce e la memoria analizzano a valle.
        assert "Titolo:" in prompt
        assert "Testo:" in prompt
        assert "Immagine:" in prompt
        assert NOTHING_TO_SAY in prompt

    def test_the_profile_fills_the_slots(self) -> None:
        prompt = render_auto_prompt(_profile())

        assert "officina" in prompt
        assert "l'attrezzo che si ha in mano." in prompt
        assert "il colore del pavimento." in prompt
        assert "non superare 30 parole" in prompt

    def test_pages_only_where_there_are_pages(self) -> None:
        assert PAGE_TAG not in render_auto_prompt(_profile())
        assert PAGE_TAG in render_auto_prompt(_profile(memory_item="slide"))

    def test_pointing_always_asks_for_the_written_text(self) -> None:
        context = render_pointing_context(_profile())

        assert "visible_text" in context
        assert "per intero" in context
        assert "L'attrezzo indicato" in context

    def test_a_registered_profile_looks_like_a_builtin_one(self) -> None:
        profile = _profile(id="officina-test")
        register_profile(profile)
        try:
            assert AUTO_PROMPTS["officina-test"] == render_auto_prompt(profile)
            assert POINTING_CONTEXT["officina-test"] == render_pointing_context(profile)
        finally:
            AUTO_PROMPTS.pop("officina-test")
            POINTING_CONTEXT.pop("officina-test")


class TestStore:
    def test_a_saved_profile_comes_back_as_it_was(self, tmp_path) -> None:
        path = save_profile(_profile(), tmp_path)

        assert path.name == "officina.json"
        assert load_profiles(tmp_path) == {"officina": _profile()}

    def test_a_broken_file_is_skipped_instead_of_stopping_the_server(
        self, tmp_path
    ) -> None:
        save_profile(_profile(), tmp_path)
        (tmp_path / "rotto.json").write_text("{ non è json", encoding="utf-8")
        (tmp_path / "vuoto.json").write_text("{}", encoding="utf-8")
        # Un file il cui nome non corrisponde all'id confonderebbe
        # CAPTION_CONTEXT: meglio ignorarlo.
        (tmp_path / "altro-nome.json").write_text(
            json.dumps(_profile(id="officina-due").model_dump()), encoding="utf-8"
        )

        assert sorted(load_profiles(tmp_path)) == ["officina"]

    def test_a_missing_folder_is_not_an_error(self, tmp_path) -> None:
        assert load_profiles(tmp_path / "non-esiste") == {}


class TestWiring:
    def test_a_saved_mode_can_be_used_like_lesson_or_museum(self, tmp_path) -> None:
        from vision_caption.infrastructure.server.app import create_app
        from vision_caption.infrastructure.settings import AppSettings

        save_profile(_profile(id="officina-wiring"), tmp_path)
        settings = AppSettings.from_env(
            {
                "USE_MOCKS": "true",
                "RESEARCH_LOG_ENABLED": "false",
                "FRONTEND_DIST_PATH": "/nonexistent",
                "PROFILES_DIR": str(tmp_path),
                "CAPTION_CONTEXT": "officina-wiring",
            }
        )
        pipeline = create_app(settings).state.pipeline_factory(None)

        assert pipeline._lesson_memory is not None
        assert pipeline._speech_text is not None
        pipeline._lesson_memory.remember(None, None, "Un trapano a colonna.")
        assert "Attrezzo" in pipeline._lesson_memory.context()

    def test_an_unknown_mode_says_which_ones_exist(self, tmp_path) -> None:
        from vision_caption.infrastructure.server.app import create_app
        from vision_caption.infrastructure.settings import AppSettings

        save_profile(_profile(id="officina-nota"), tmp_path)
        settings = AppSettings.from_env(
            {
                "USE_MOCKS": "true",
                "RESEARCH_LOG_ENABLED": "false",
                "FRONTEND_DIST_PATH": "/nonexistent",
                "PROFILES_DIR": str(tmp_path),
                "CAPTION_CONTEXT": "spiaggia",
            }
        )

        with pytest.raises(ValueError) as error:
            create_app(settings)

        assert "officina-nota" in str(error.value)
        assert "lesson" in str(error.value)
