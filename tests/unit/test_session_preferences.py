from vision_caption.core.services.session_preferences import (
    SessionPreferences,
    parse_session_preferences,
)


def test_le_scelte_buone_arrivano_come_sono() -> None:
    preferenze = parse_session_preferences(
        {"max_words": 25, "min_interval_seconds": 20, "mode": "museum"},
        allowed_modes=("lesson", "museum"),
    )

    assert preferenze == SessionPreferences(
        max_words=25, min_interval_seconds=20.0, mode="museum"
    )


def test_niente_scelte_vuol_dire_come_decide_il_server() -> None:
    assert parse_session_preferences(None).is_empty
    assert parse_session_preferences("tutto al massimo").is_empty
    assert parse_session_preferences({}).is_empty


def test_un_campo_illeggibile_non_invalida_gli_altri() -> None:
    preferenze = parse_session_preferences(
        {"max_words": "molte", "min_interval_seconds": 15}
    )

    # Per le parole decide il server, per l'intervallo la scelta vale.
    assert preferenze.max_words is None
    assert preferenze.min_interval_seconds == 15.0


def test_valori_assurdi_vengono_riportati_nei_limiti() -> None:
    # Zero parole renderebbe muta la descrizione, zero secondi farebbe parlare
    # l'applicazione sopra sé stessa.
    assert parse_session_preferences({"max_words": 0}).max_words == 10
    assert parse_session_preferences({"max_words": 5000}).max_words == 150
    assert parse_session_preferences({"min_interval_seconds": 0}).min_interval_seconds == 2.0
    assert (
        parse_session_preferences({"min_interval_seconds": 99999}).min_interval_seconds
        == 300.0
    )


def test_un_valore_non_numerico_non_diventa_zero() -> None:
    assert parse_session_preferences({"min_interval_seconds": float("nan")}).min_interval_seconds is None
    assert parse_session_preferences({"min_interval_seconds": float("inf")}).min_interval_seconds is None
    assert parse_session_preferences({"max_words": None}).max_words is None


def test_una_modalita_inventata_viene_ignorata_senza_fermare_la_sessione() -> None:
    # Il telefono può avere un elenco più vecchio di quello che il server ha
    # caricato: la sessione continua con la modalità del server.
    preferenze = parse_session_preferences(
        {"mode": "pescheria", "max_words": 30}, allowed_modes=("lesson",)
    )

    assert preferenze.mode is None
    assert preferenze.max_words == 30


def test_una_modalita_lunghissima_non_entra_nel_prompt() -> None:
    assert parse_session_preferences({"mode": "x" * 500}, allowed_modes=("lesson",)).mode is None


def test_gli_spazi_intorno_al_nome_non_contano() -> None:
    assert (
        parse_session_preferences({"mode": "  lesson "}, allowed_modes=("lesson",)).mode
        == "lesson"
    )
