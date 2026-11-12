import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from vision_caption.adapters.vlm.mode_profile_generator import (
    ModeProfileError,
    extract_profile,
)
from vision_caption.infrastructure.server import modes as modes_module
from vision_caption.infrastructure.server.modes import router
from vision_caption.infrastructure.settings import AppSettings


PROFILO = {
    "id": "pesca",
    "name": "Pesca da riva",
    "purpose": "Accompagni una persona cieca che pesca da riva, da sola.",
    "speak_when": "Quando cambia l'attrezzo inquadrato o quando l'acqua si avvicina.",
    "describe": ["la canna e il mulinello", "il secchiello e le esche"],
    "ignore": ["il cielo", "le altre persone"],
    "written_text": "Leggi per intero le etichette delle esche e i cartelli di divieto.",
    "when_nothing": "Resta in silenzio.",
    "pointing": "Di' che attrezzo è e ogni scritta che porta.",
    "max_words": 25,
    "memory_item": "attrezzo",
}


def app_con(settings: AppSettings, cartella) -> TestClient:
    app = FastAPI()
    app.state.settings = settings
    app.state.available_modes = [{"id": "lesson", "label": "Lezione"}]
    app.include_router(router)
    modes_module._last_creation = None
    return TestClient(app)


def impostazioni(tmp_path, acceso: bool, attesa: float = 0.0) -> AppSettings:
    return AppSettings.from_env(
        {
            "MODE_CREATION_ENABLED": "true" if acceso else "false",
            "MODE_CREATION_COOLDOWN_SECONDS": str(attesa),
            "PROFILES_DIR": str(tmp_path),
        }
    )


def test_di_suo_e_chiuso(tmp_path) -> None:
    # Il server è pubblico dietro un tunnel: un endpoint aperto che chiama un
    # modello grande e scrive un file lo paga qualcun altro.
    client = app_con(impostazioni(tmp_path, acceso=False), tmp_path)

    risposta = client.post("/modes", json={"description": "una persona che va a pescare da riva"})

    assert risposta.status_code == 403
    assert "MODE_CREATION_ENABLED" in risposta.json()["detail"]


def test_l_elenco_dice_se_si_possono_creare(tmp_path) -> None:
    client = app_con(impostazioni(tmp_path, acceso=False), tmp_path)

    corpo = client.get("/modes").json()

    assert corpo["modes"] == [{"id": "lesson", "label": "Lezione"}]
    assert corpo["can_create"] is False


def test_una_frase_diventa_una_modalita_salvata(tmp_path, monkeypatch) -> None:
    async def finta_generazione(self, description, forced_id=None):
        assert "pescare" in description
        return extract_profile(__import__("json").dumps(PROFILO))

    monkeypatch.setattr(
        "vision_caption.infrastructure.server.modes.ModeProfileGenerator.generate",
        finta_generazione,
    )
    client = app_con(impostazioni(tmp_path, acceso=True), tmp_path)

    risposta = client.post(
        "/modes", json={"description": "una persona cieca che va a pescare da riva"}
    )

    assert risposta.status_code == 201
    assert risposta.json() == {"id": "pesca", "label": "Pesca da riva"}
    assert (tmp_path / "pesca.json").exists()
    # Vale subito per le sessioni che si aprono dopo, senza riavviare.
    assert {"id": "pesca", "label": "Pesca da riva"} in client.app.state.available_modes


def test_una_frase_troppo_corta_non_arriva_al_modello(tmp_path) -> None:
    client = app_con(impostazioni(tmp_path, acceso=True), tmp_path)

    assert client.post("/modes", json={"description": "pesca"}).status_code == 422


def test_un_tema_invece_di_una_frase_viene_rifiutato(tmp_path) -> None:
    client = app_con(impostazioni(tmp_path, acceso=True), tmp_path)

    risposta = client.post("/modes", json={"description": "a" * 500})

    assert risposta.status_code == 422


def test_una_modalita_alla_volta(tmp_path, monkeypatch) -> None:
    async def finta_generazione(self, description, forced_id=None):
        return extract_profile(__import__("json").dumps(PROFILO))

    monkeypatch.setattr(
        "vision_caption.infrastructure.server.modes.ModeProfileGenerator.generate",
        finta_generazione,
    )
    client = app_con(impostazioni(tmp_path, acceso=True, attesa=60.0), tmp_path)

    prima = client.post("/modes", json={"description": "una persona che pesca da riva, da sola"})
    seconda = client.post("/modes", json={"description": "una persona in officina con attrezzi"})

    assert prima.status_code == 201
    assert seconda.status_code == 429


def test_se_il_modello_riempie_male_il_modulo_lo_dice(tmp_path, monkeypatch) -> None:
    async def fallisce(self, description, forced_id=None):
        raise ModeProfileError("Il modello ha riempito male il modulo: id mancante")

    monkeypatch.setattr(
        "vision_caption.infrastructure.server.modes.ModeProfileGenerator.generate",
        fallisce,
    )
    client = app_con(impostazioni(tmp_path, acceso=True), tmp_path)

    risposta = client.post("/modes", json={"description": "una situazione descritta a parole"})

    # Errore del modello, non della persona: 502 e non 400.
    assert risposta.status_code == 502
    assert "riempito male" in risposta.json()["detail"]


def test_il_json_del_modello_dentro_un_blocco_di_codice_si_legge() -> None:
    import json

    contenuto = f"```json\n{json.dumps(PROFILO)}\n```"

    assert extract_profile(contenuto).id == "pesca"


def test_una_risposta_senza_modulo_e_un_errore_leggibile() -> None:
    with pytest.raises(ModeProfileError, match="non ha risposto con un modulo"):
        extract_profile("Mi dispiace, non posso aiutarti.")
