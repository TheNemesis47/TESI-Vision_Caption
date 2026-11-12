from vision_caption.core.domain.audio import Audio, AudioFormat
from vision_caption.core.services.described_scene_cache import (
    DescribedSceneCache,
    normalize_key,
)


def voce(nome: str, durata: float = 5.0) -> Audio:
    return Audio(
        audio_format=AudioFormat.MP3,
        audio_bytes=nome.encode(),
        audio_duration=durata,
    )


def test_la_voce_gia_pronunciata_si_ritrova() -> None:
    cache = DescribedSceneCache()
    cache.remember("Titolo: Fonti di energia.", voce("energia"))

    trovata = cache.find("Titolo: Fonti di energia.")

    assert trovata is not None
    assert trovata.audio_bytes == b"energia"


def test_maiuscole_spazi_e_punto_finale_non_fanno_due_slide_diverse() -> None:
    cache = DescribedSceneCache()
    cache.remember("Titolo: Fonti di energia.", voce("energia"))

    assert cache.find("titolo:  fonti di energia") is not None


def test_una_slide_mai_descritta_non_ha_voce() -> None:
    cache = DescribedSceneCache()
    cache.remember("Titolo: Fonti.", voce("fonti"))

    assert cache.find("Titolo: Consumi.") is None
    assert DescribedSceneCache().find("qualunque cosa") is None


def test_un_testo_vuoto_non_entra_in_cache() -> None:
    cache = DescribedSceneCache()
    cache.remember("   ", voce("niente"))

    assert len(cache) == 0


def test_la_stessa_slide_descritta_meglio_sostituisce_la_voce_vecchia() -> None:
    cache = DescribedSceneCache()
    cache.remember("Titolo: Fonti.", voce("prima"))
    cache.remember("Titolo: Fonti.", voce("dopo"))

    assert len(cache) == 1
    assert cache.find("Titolo: Fonti.").audio_bytes == b"dopo"


def test_tiene_le_ultime_e_butta_le_piu_vecchie() -> None:
    cache = DescribedSceneCache(max_entries=2)
    cache.remember("una", voce("una"))
    cache.remember("due", voce("due"))
    cache.remember("tre", voce("tre"))

    assert len(cache) == 2
    assert cache.find("una") is None
    assert cache.find("tre") is not None


def test_una_slide_risentita_di_recente_non_viene_buttata() -> None:
    cache = DescribedSceneCache(max_entries=2)
    cache.remember("una", voce("una"))
    cache.remember("due", voce("due"))
    # Si torna sulla prima: da quel momento è la più recente.
    cache.find("una")
    cache.remember("tre", voce("tre"))

    assert cache.find("una") is not None
    assert cache.find("due") is None


def test_segue_la_finestra_della_memoria() -> None:
    cache = DescribedSceneCache()
    cache.remember("una", voce("una"))
    cache.remember("due", voce("due"))

    # La memoria della lezione ricorda solo la seconda: l'audio della prima
    # non verrebbe mai richiesto.
    cache.keep_only(["due"])

    assert len(cache) == 1
    assert cache.find("una") is None


def test_un_cambio_di_presentazione_azzera_tutto() -> None:
    cache = DescribedSceneCache()
    cache.remember("una", voce("una"))
    cache.keep_only([])

    assert len(cache) == 0


def test_l_avviso_di_ripetizione_si_sintetizza_una_volta_sola() -> None:
    cache = DescribedSceneCache()

    assert cache.cue is None
    cache.remember_cue(voce("avviso", durata=0.9))
    assert cache.cue.audio_bytes == b"avviso"


def test_la_chiave_normalizzata_e_quella_del_confronto() -> None:
    assert normalize_key("  Titolo: Fonti di energia.  ") == "titolo: fonti di energia"
