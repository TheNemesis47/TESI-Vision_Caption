#!/usr/bin/env python3
"""Banco di prova offline della modalita' AUTO.

Fa passare un corpus di fotogrammi attraverso gli stessi adapter che il server
monta in produzione e ne misura le fasi. Serve a produrre le tabelle del
capitolo di valutazione sperimentale senza dipendere da una sessione dal vivo,
che non sarebbe ripetibile.

Due modalita':

``fasi``
    Misura ogni fase separatamente, con riscaldamento e ripetizioni. Le fasi
    locali (decodifica + SSIM, RF-DETR) non hanno costo; quelle remote (modello
    visivo-linguistico, sintesi vocale) consumano credito ed e' possibile
    escluderle con ``--senza-api``. Alimenta ``tab:tempi-pipeline``.

``sequenza``
    Replica una sequenza attraverso la ``CaptionPipeline`` reale, alla cadenza
    di acquisizione configurata, e registra l'esito di ogni fotogramma. Alimenta
    ``tab:efficacia-filtri``.

Esempi::

    python scripts/benchmark_pipeline.py fasi --senza-api
    python scripts/benchmark_pipeline.py fasi --ripetizioni 30 --ripetizioni-api 3
    python scripts/benchmark_pipeline.py sequenza --video prove/corridoio.mp4
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from loguru import logger

RADICE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RADICE / "src"))

from vision_caption.adapters.scene.HybridSceneDetectorAdapter import (  # noqa: E402
    HybridSceneDetectorAdapter,
)
from vision_caption.adapters.scene.RfdetrCustomSceneDetectorAdapter import (  # noqa: E402
    RfdetrCustomSceneDetectorAdapter,
)
from vision_caption.adapters.scene.RfdetrSceneDetectorAdapter import (  # noqa: E402
    RfdetrSceneDetectorAdapter,
)
from vision_caption.adapters.scene.SsimSceneDetectorAdapter import (  # noqa: E402
    SsimSceneDetectorAdapter,
)
from vision_caption.adapters.tts.ChatterboxSynthesizer import (  # noqa: E402
    ChatterboxSynthesizer,
)
from vision_caption.adapters.tts.ElevenLabsSynthesizer import (  # noqa: E402
    ElevenLabsSynthesizer,
)
from vision_caption.adapters.vlm.OpenRouterCaptionGenerator import (  # noqa: E402
    OpenRouterCaptionGenerator,
)
from vision_caption.core.domain.frame import CaptionMode, Frame  # noqa: E402
from vision_caption.core.services.caption_pipeline import CaptionPipeline  # noqa: E402
from vision_caption.core.services.rate_limiter import RateLimiter  # noqa: E402
from vision_caption.infrastructure.settings import AppSettings  # noqa: E402

CORPUS_PREDEFINITO = RADICE / "artifacts" / "pointing_debug"
USCITA_PREDEFINITA = RADICE / "artifacts" / "benchmark"


# ---------------------------------------------------------------------------
# Configurazione
# ---------------------------------------------------------------------------

def carica_dotenv(percorso: Path) -> None:
    """Popola ``os.environ`` dal file .env, senza sovrascrivere l'ambiente."""
    import os

    if not percorso.exists():
        return
    for riga in percorso.read_text(encoding="utf-8").splitlines():
        riga = riga.strip()
        if not riga or riga.startswith("#") or "=" not in riga:
            continue
        chiave, _, valore = riga.partition("=")
        chiave = chiave.strip()
        valore = valore.strip().strip('"').strip("'")
        os.environ.setdefault(chiave, valore)


# ---------------------------------------------------------------------------
# Corpus
# ---------------------------------------------------------------------------

ESTENSIONI = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def fotogrammi_da_cartella(cartella: Path, filtro: str | None) -> list[bytes]:
    """Legge i JPEG di una cartella in ordine di nome, ricorsivamente."""
    percorsi = sorted(
        p for p in cartella.rglob("*")
        if p.suffix.lower() in ESTENSIONI
        and (filtro is None or filtro in p.name)
    )
    return [p.read_bytes() for p in percorsi]


def fotogrammi_da_video(video: Path, passo: int) -> list[bytes]:
    """Estrae un fotogramma ogni ``passo`` e lo codifica in JPEG.

    La codifica riproduce cio' che il client invia sul WebSocket, cosi' che la
    fase di decodifica misurata sia quella reale e non una lettura da disco.
    """
    cattura = cv2.VideoCapture(str(video))
    if not cattura.isOpened():
        raise SystemExit(f"Impossibile aprire il video: {video}")

    fotogrammi: list[bytes] = []
    indice = 0
    while True:
        letto, immagine = cattura.read()
        if not letto:
            break
        if indice % passo == 0:
            ok, buffer = cv2.imencode(".jpg", immagine, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if ok:
                fotogrammi.append(buffer.tobytes())
        indice += 1
    cattura.release()
    return fotogrammi


def costruisci_corpus(argomenti) -> list[bytes]:
    fotogrammi: list[bytes] = []
    if argomenti.video:
        fotogrammi.extend(fotogrammi_da_video(argomenti.video, argomenti.passo))
    if argomenti.immagini:
        fotogrammi.extend(
            fotogrammi_da_cartella(argomenti.immagini, argomenti.filtro_nome)
        )
    if not fotogrammi:
        fotogrammi.extend(
            fotogrammi_da_cartella(CORPUS_PREDEFINITO, "03_clean_original")
        )
    if not fotogrammi:
        raise SystemExit(
            "Corpus vuoto. Indicare --video o --immagini, oppure popolare "
            f"{CORPUS_PREDEFINITO}."
        )
    return fotogrammi


def in_frame(dati: bytes, identificativo: int) -> Frame:
    return Frame(
        frame_id=identificativo,
        image_bytes=dati,
        caption_mode=CaptionMode.AUTO,
        timestamp=datetime.now(),
    )


# ---------------------------------------------------------------------------
# Adapter, montati come in app.py
# ---------------------------------------------------------------------------

def monta_rilevatore(impostazioni: AppSettings):
    auto = impostazioni.auto
    ssim_detector = SsimSceneDetectorAdapter(threshold=auto.ssim.threshold)
    device = impostazioni.runtime.device

    if auto.rfdetr.checkpoint_path:
        logger.info(f"Checkpoint RF-DETR personalizzato: {auto.rfdetr.checkpoint_path}")
        rfdetr_detector = RfdetrCustomSceneDetectorAdapter.from_checkpoint(
            checkpoint_path=auto.rfdetr.checkpoint_path,
            device=device,
            threshold=auto.rfdetr.custom_confidence_threshold,
            optimize=auto.rfdetr.optimize_for_inference,
        )
    else:
        from rfdetr import RFDETRMedium

        logger.info("Checkpoint assente: si usa il modello COCO pre-addestrato.")
        modello = RFDETRMedium(device=device)
        su_gpu = device.lower() != "cpu"
        if auto.rfdetr.optimize_for_inference:
            modello.optimize_for_inference(
                compile=su_gpu,
                batch_size=1,
                dtype="float16" if su_gpu else "float32",
            )
        rfdetr_detector = RfdetrSceneDetectorAdapter(
            model=modello,
            threshold=auto.rfdetr.confidence_threshold,
        )

    if auto.rfdetr.warmup_enabled:
        rfdetr_detector.warm_up(
            width=auto.rfdetr.warmup_width,
            height=auto.rfdetr.warmup_height,
        )

    ibrido = HybridSceneDetectorAdapter(
        ssim_detector=ssim_detector,
        rfdetr_detector=rfdetr_detector,
        suppress_unchanged_class_counts=auto.suppress_unchanged_class_counts,
        semantic_box_iou_threshold=auto.semantic_box_iou_threshold,
    )
    return ssim_detector, rfdetr_detector, ibrido


def monta_vlm(impostazioni: AppSettings) -> OpenRouterCaptionGenerator:
    if (
        impostazioni.vlm.resolved_provider == "openrouter"
        and not impostazioni.vlm.api_key
    ):
        raise SystemExit("OPENROUTER_API_KEY assente: usare --senza-api.")
    return OpenRouterCaptionGenerator(
        api_key=impostazioni.vlm.api_key,
        model_name=impostazioni.vlm.resolved_model_name,
        base_url=impostazioni.vlm.resolved_base_url,
        max_tokens=impostazioni.auto.vlm.max_output_tokens,
        temperature=impostazioni.auto.vlm.temperature,
        timeout_seconds=impostazioni.auto.vlm.http_timeout_seconds,
    )


def monta_tts(impostazioni: AppSettings):
    tts = impostazioni.tts
    if tts.elevenlabs_api_key:
        return ElevenLabsSynthesizer(
            api_key=tts.elevenlabs_api_key,
            voice_id=tts.elevenlabs_voice_id,
            model_id=tts.elevenlabs_model_id,
            timeout_seconds=tts.elevenlabs_timeout_seconds,
        )
    return ChatterboxSynthesizer(
        base_url=tts.chatterbox_url,
        timeout_seconds=tts.chatterbox_timeout_seconds,
        voice=tts.chatterbox_voice,
        speed=tts.chatterbox_speed,
        exaggeration=tts.chatterbox_exaggeration,
        cfg_weight=tts.chatterbox_cfg_weight,
        temperature=tts.chatterbox_temperature,
    )


# ---------------------------------------------------------------------------
# Modalita' "fasi"
# ---------------------------------------------------------------------------

async def misura_fasi(argomenti, impostazioni: AppSettings) -> dict:
    corpus = costruisci_corpus(argomenti)
    logger.info(f"Corpus: {len(corpus)} fotogrammi.")

    ssim_detector, rfdetr_detector, _ = monta_rilevatore(impostazioni)
    soglia_ssim = impostazioni.auto.ssim.threshold

    misure: dict[str, list[float]] = {
        "decodifica_ssim_ms": [],
        "rfdetr_ms": [],
        "vlm_primo_chunk_ms": [],
        "tts_primo_chunk_ms": [],
        "totale_primo_audio_ms": [],
    }

    # Riscaldamento: esclude il costo di caricamento e la prima compilazione
    # dei kernel, che non rappresentano il funzionamento a regime.
    logger.info(f"Riscaldamento su {argomenti.riscaldamento} iterazioni...")
    for indice in range(argomenti.riscaldamento):
        dati = corpus[indice % len(corpus)]
        grigi = cv2.imdecode(np.frombuffer(dati, np.uint8), cv2.IMREAD_GRAYSCALE)
        ssim_detector.old_img = grigi
        await ssim_detector.analyze(grigi)
        await rfdetr_detector.analyze(in_frame(dati, -1))

    # --- Fasi locali -------------------------------------------------------
    logger.info(f"Fasi locali: {argomenti.ripetizioni} ripetizioni sul corpus.")
    for ripetizione in range(argomenti.ripetizioni):
        precedente = None
        for posizione, dati in enumerate(corpus):
            inizio = time.perf_counter()
            grigi = cv2.imdecode(
                np.frombuffer(dati, np.uint8), cv2.IMREAD_GRAYSCALE
            )
            confrontabile = (
                precedente is not None and precedente.shape == grigi.shape
            )
            if confrontabile:
                from skimage.metrics import structural_similarity

                structural_similarity(precedente, grigi)
            trascorso = (time.perf_counter() - inizio) * 1000.0
            # Il primo fotogramma di ogni ripetizione non ha un predecessore:
            # misurerebbe la sola decodifica e abbasserebbe il minimo senza
            # rappresentare un'elaborazione reale.
            if confrontabile:
                misure["decodifica_ssim_ms"].append(trascorso)
            precedente = grigi

            inizio = time.perf_counter()
            await rfdetr_detector.analyze(in_frame(dati, posizione))
            misure["rfdetr_ms"].append((time.perf_counter() - inizio) * 1000.0)

    # --- Fasi remote -------------------------------------------------------
    dettagli: list[dict] = []
    if not argomenti.senza_api:
        vlm = monta_vlm(impostazioni)
        tts = monta_tts(impostazioni)
        logger.info(
            f"Fasi remote: {argomenti.ripetizioni_api} ripetizioni "
            f"su {len(corpus)} fotogrammi."
        )
        # Il fotogramma precedente fa da riferimento strutturale, cosi' che
        # l'SSIM venga davvero calcolato anche nel totale end-to-end.
        riferimento = cv2.imdecode(
            np.frombuffer(corpus[-1], np.uint8), cv2.IMREAD_GRAYSCALE
        )
        for ripetizione in range(argomenti.ripetizioni_api):
            for posizione, dati in enumerate(corpus):
                frame = in_frame(dati, posizione)
                inizio_totale = time.perf_counter()

                # Decodifica e SSIM, come li esegue il rilevatore ibrido.
                grigi = cv2.imdecode(
                    np.frombuffer(dati, np.uint8), cv2.IMREAD_GRAYSCALE
                )
                ssim_detector.old_img = riferimento
                await ssim_detector.analyze(grigi)
                riferimento = grigi
                risultato = await rfdetr_detector.analyze(frame)

                inizio_vlm = time.perf_counter()
                primo_chunk = None
                generatore = vlm.generate(frame)
                try:
                    async for chunk in generatore:
                        if chunk:
                            primo_chunk = chunk
                            break
                finally:
                    await generatore.aclose()
                vlm_ms = (time.perf_counter() - inizio_vlm) * 1000.0

                if primo_chunk is None:
                    logger.warning(f"Nessuna caption per il fotogramma {posizione}.")
                    continue
                misure["vlm_primo_chunk_ms"].append(vlm_ms)

                inizio_tts = time.perf_counter()
                audio = await tts.synthesize(primo_chunk)
                tts_ms = (time.perf_counter() - inizio_tts) * 1000.0
                misure["tts_primo_chunk_ms"].append(tts_ms)

                totale_ms = (time.perf_counter() - inizio_totale) * 1000.0
                misure["totale_primo_audio_ms"].append(totale_ms)

                dettagli.append({
                    "ripetizione": ripetizione,
                    "fotogramma": posizione,
                    "caption": primo_chunk,
                    "oggetti": [d.class_name for d in risultato.detections],
                    "vlm_primo_chunk_ms": round(vlm_ms, 1),
                    "tts_primo_chunk_ms": round(tts_ms, 1),
                    "totale_primo_audio_ms": round(totale_ms, 1),
                    "byte_audio": len(audio.audio_bytes),
                })

    return {
        "modalita": "fasi",
        "istante": datetime.now().isoformat(timespec="seconds"),
        "fotogrammi_nel_corpus": len(corpus),
        "ripetizioni_locali": argomenti.ripetizioni,
        "ripetizioni_api": 0 if argomenti.senza_api else argomenti.ripetizioni_api,
        "riscaldamento": argomenti.riscaldamento,
        "soglia_ssim": soglia_ssim,
        "misure": misure,
        "dettagli": dettagli,
    }


# ---------------------------------------------------------------------------
# Modalita' "sequenza"
# ---------------------------------------------------------------------------

async def misura_sequenza(argomenti, impostazioni: AppSettings) -> dict:
    corpus = costruisci_corpus(argomenti)
    logger.info(f"Sequenza: {len(corpus)} fotogrammi.")

    _, _, ibrido = monta_rilevatore(impostazioni)
    pipeline = CaptionPipeline(
        scene_detector=ibrido,
        caption_generator=monta_vlm(impostazioni),
        speech_synthesizer=monta_tts(impostazioni),
        rate_limiter=RateLimiter(
            min_interval_seconds=impostazioni.auto.min_caption_interval_seconds
        ),
        max_frame_age_seconds=impostazioni.auto.max_frame_age_seconds,
        vlm_chunk_timeout_seconds=impostazioni.auto.vlm.chunk_timeout_seconds,
        caption_similarity_threshold=impostazioni.auto.caption_similarity_threshold,
    )

    intervallo = 1.0 / impostazioni.server.auto_input_fps
    logger.info(
        f"Cadenza di acquisizione: {impostazioni.server.auto_input_fps} Hz "
        f"({intervallo * 1000:.0f} ms fra fotogrammi)."
    )

    prodotti = 0
    inizio = time.perf_counter()
    for posizione, dati in enumerate(corpus):
        atteso = inizio + posizione * intervallo
        ritardo = atteso - time.perf_counter()
        if ritardo > 0:
            await asyncio.sleep(ritardo)
        async for _ in pipeline.process(in_frame(dati, posizione)):
            prodotti += 1

    await pipeline.close()
    return {
        "modalita": "sequenza",
        "istante": datetime.now().isoformat(timespec="seconds"),
        "fotogrammi_inviati": len(corpus),
        "frequenza_hz": impostazioni.server.auto_input_fps,
        "frammenti_audio_prodotti": prodotti,
        "nota": (
            "Le righe PIPELINE_METRIC finiscono nel log: aggregarle con "
            "scripts/aggregate_metrics.py."
        ),
    }


# ---------------------------------------------------------------------------
# Riepilogo
# ---------------------------------------------------------------------------

def riepiloga(valori: list[float]) -> dict | None:
    if not valori:
        return None
    return {
        "n": len(valori),
        "mediana": round(statistics.median(valori), 1),
        "minimo": round(min(valori), 1),
        "massimo": round(max(valori), 1),
        "media": round(statistics.fmean(valori), 1),
    }


ETICHETTE = [
    ("decodifica_ssim_ms", "Decodifica e SSIM"),
    ("rfdetr_ms", "RF-DETR (solo se attivato)"),
    ("vlm_primo_chunk_ms", "Modello visivo-linguistico, primo frammento"),
    ("tts_primo_chunk_ms", "Sintesi vocale, primo frammento"),
    ("totale_primo_audio_ms", "Totale fino al primo audio"),
]


def stampa_risultati(esito: dict, latex: bool) -> None:
    misure = esito.get("misure")
    if not misure:
        print(json.dumps(esito, indent=2, ensure_ascii=False))
        return

    print(f"\nFotogrammi nel corpus: {esito['fotogrammi_nel_corpus']}")
    print(f"Ripetizioni locali: {esito['ripetizioni_locali']}   "
          f"ripetizioni con API: {esito['ripetizioni_api']}\n")
    print(f"{'Fase':<44}{'mediana':>9}{'min':>9}{'max':>9}{'n':>7}")
    for chiave, etichetta in ETICHETTE:
        sintesi = riepiloga(misure[chiave])
        if sintesi is None:
            print(f"{etichetta:<44}{'--':>9}{'--':>9}{'--':>9}{0:>7}")
            continue
        print(f"{etichetta:<44}{sintesi['mediana']:>9.0f}"
              f"{sintesi['minimo']:>9.0f}{sintesi['massimo']:>9.0f}"
              f"{sintesi['n']:>7}")

    if latex:
        print("\n--- Righe per tab:tempi-pipeline ---")
        for chiave, etichetta in ETICHETTE:
            sintesi = riepiloga(misure[chiave])
            if sintesi is None:
                print(f"{etichetta} & -- & -- & -- \\\\")
                continue
            nome = (f"\\textbf{{{etichetta}}}"
                    if chiave == "totale_primo_audio_ms" else etichetta)
            print(f"{nome} & {sintesi['mediana']:.0f} & "
                  f"{sintesi['minimo']:.0f} & {sintesi['massimo']:.0f} \\\\")


# ---------------------------------------------------------------------------

def analizza_argomenti():
    comune = argparse.ArgumentParser(add_help=False)
    comune.add_argument("--video", type=Path, help="file video da campionare")
    comune.add_argument("--immagini", type=Path, help="cartella di fotogrammi")
    comune.add_argument("--filtro-nome", default=None,
                        help="tiene solo i file il cui nome contiene questa stringa")
    comune.add_argument("--passo", type=int, default=15,
                        help="un fotogramma ogni N nel video (predefinito 15)")
    comune.add_argument("--uscita", type=Path, default=USCITA_PREDEFINITA)
    comune.add_argument("--latex", action="store_true",
                        help="stampa le righe pronte per le tabelle")

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sotto = parser.add_subparsers(dest="modalita", required=True)

    fasi = sotto.add_parser("fasi", parents=[comune],
                            help="misura le singole fasi con ripetizioni")
    fasi.add_argument("--ripetizioni", type=int, default=30,
                      help="ripetizioni delle fasi locali (predefinito 30)")
    fasi.add_argument("--ripetizioni-api", type=int, default=3,
                      help="ripetizioni delle fasi remote (predefinito 3)")
    fasi.add_argument("--riscaldamento", type=int, default=10,
                      help="iterazioni di riscaldamento scartate (predefinito 10)")
    fasi.add_argument("--senza-api", action="store_true",
                      help="salta VLM e TTS: nessun consumo di credito")

    sotto.add_parser("sequenza", parents=[comune],
                     help="replica una sequenza attraverso la pipeline reale")

    return parser.parse_args()


def main() -> None:
    argomenti = analizza_argomenti()
    carica_dotenv(RADICE / ".env")
    impostazioni = AppSettings.from_env()

    logger.remove()
    logger.add(sys.stderr, level=impostazioni.server.log_level)
    percorso_log = impostazioni.server.log_dir
    percorso_log.mkdir(parents=True, exist_ok=True)
    logger.add(
        str(percorso_log / "benchmark_{time:YYYY-MM-DD}.log"),
        level="DEBUG",
        enqueue=True,
    )

    if argomenti.modalita == "fasi":
        esito = asyncio.run(misura_fasi(argomenti, impostazioni))
    else:
        esito = asyncio.run(misura_sequenza(argomenti, impostazioni))

    argomenti.uscita.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%dT%H%M%S")
    destinazione = argomenti.uscita / f"{argomenti.modalita}_{marca}.json"
    destinazione.write_text(
        json.dumps(esito, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    stampa_risultati(esito, argomenti.latex)
    print(f"\nMisure salvate in {destinazione}")


if __name__ == "__main__":
    main()
