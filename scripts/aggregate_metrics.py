#!/usr/bin/env python3
"""Aggrega le righe PIPELINE_METRIC dei log nelle tabelle del Capitolo 8.

Uso:
    python scripts/aggregate_metrics.py logs/vision_caption_*.log
    python scripts/aggregate_metrics.py logs/*.log --latex

Senza --latex stampa un riepilogo leggibile; con --latex produce le righe
gia' pronte da incollare nelle tabelle tab:tempi-pipeline e
tab:efficacia-filtri della tesi.
"""

import argparse
import json
import re
from pathlib import Path
from statistics import median

PREFIX = "PIPELINE_METRIC"
LINE = re.compile(re.escape(PREFIX) + r"\s+(\{.*\})\s*$")

# Ordine dei livelli della cascata: ogni voce elenca gli esiti che si sono
# fermati a quel livello.
CASCATA = [
    ("Superano il filtro strutturale SSIM", {"suppressed_ssim"}),
    ("Superano il filtro semantico sulle classi", {"suppressed_semantic"}),
    ("Superano intervallo minimo e freschezza",
     {"rate_limited", "stale_pre_vlm"}),
    ("Producono audio", {"vlm_timeout", "stale_pre_tts",
                         "stale_post_tts", "no_audio"}),
]


def carica(percorsi: list[Path]) -> list[dict]:
    record = []
    for percorso in percorsi:
        with percorso.open(encoding="utf-8", errors="replace") as sorgente:
            for riga in sorgente:
                trovato = LINE.search(riga)
                if trovato:
                    try:
                        record.append(json.loads(trovato.group(1)))
                    except json.JSONDecodeError:
                        continue
    return record


def statistiche(valori: list[float]) -> tuple[str, str, str]:
    if not valori:
        return "--", "--", "--"
    return (
        f"{median(valori):.0f}",
        f"{min(valori):.0f}",
        f"{max(valori):.0f}",
    )


def colonna(record: list[dict], chiave: str) -> list[float]:
    return [r[chiave] for r in record if r.get(chiave) is not None]


def tts_piatti(record: list[dict]) -> list[float]:
    valori: list[float] = []
    for r in record:
        valori.extend(r.get("tts_ms") or [])
    return valori


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", nargs="+", type=Path)
    parser.add_argument("--latex", action="store_true",
                        help="stampa le righe pronte per le tabelle LaTeX")
    argomenti = parser.parse_args()

    record = carica(argomenti.log)
    if not record:
        print(f"Nessuna riga {PREFIX} trovata. "
              f"Verificare che LOG_LEVEL includa INFO.")
        return

    totale = len(record)
    con_detector = [r for r in record if r.get("outcome") != "suppressed_ssim"]
    completati = [r for r in record if r.get("first_audio_ms") is not None]

    fasi = [
        ("Decodifica e SSIM", colonna(record, "detect_ms")),
        ("RF-DETR (solo se attivato)", colonna(con_detector, "detect_ms")),
        ("VLM, primo frammento", colonna(record, "vlm_first_chunk_ms")),
        ("Sintesi vocale, per frammento", tts_piatti(record)),
        ("Totale fino al primo audio", colonna(record, "first_audio_ms")),
    ]

    print(f"\nFotogrammi elaborati: {totale}\n")
    print("--- Tempi per fase (ms) ---")
    print(f"{'Fase':<34}{'mediana':>10}{'min':>10}{'max':>10}{'n':>7}")
    for nome, valori in fasi:
        med, minimo, massimo = statistiche(valori)
        print(f"{nome:<34}{med:>10}{minimo:>10}{massimo:>10}{len(valori):>7}")

    print("\n--- Cascata dei filtri ---")
    print(f"{'Livello':<44}{'superati':>10}{'%':>8}")
    print(f"{'Fotogrammi ricevuti':<44}{totale:>10}{100.0:>8.1f}")
    rimasti = totale
    for etichetta, fermati_qui in CASCATA:
        rimasti -= sum(1 for r in record if r.get("outcome") in fermati_qui)
        quota = 100.0 * rimasti / totale if totale else 0.0
        print(f"{etichetta:<44}{rimasti:>10}{quota:>8.1f}")

    print("\n--- Esiti ---")
    esiti: dict[str, int] = {}
    for r in record:
        esiti[r.get("outcome", "unknown")] = (
            esiti.get(r.get("outcome", "unknown"), 0) + 1
        )
    for esito, quanti in sorted(esiti.items(), key=lambda x: -x[1]):
        print(f"{esito:<44}{quanti:>10}{100.0 * quanti / totale:>8.1f}")

    obsoleti = sum(
        1 for r in record
        if r.get("outcome", "").startswith("stale")
    )
    print(f"\nRNF-1, elaborazioni interrotte per obsolescenza: "
          f"{obsoleti} ({100.0 * obsoleti / totale:.1f}%)")
    eta = colonna(completati, "frame_age_at_first_audio_s")
    if eta:
        print(f"RNF-1, eta' massima di un audio consegnato: {max(eta):.2f} s")
    deduplicati = sum(r.get("chunks_deduplicated", 0) for r in record)
    print(f"RNF-3, frammenti soppressi dalla deduplicazione: {deduplicati}")

    if argomenti.latex:
        print("\n--- Righe per tab:tempi-pipeline ---")
        for nome, valori in fasi:
            med, minimo, massimo = statistiche(valori)
            print(f"{nome} & {med} & {minimo} & {massimo} \\\\")
        print("\n--- Righe per tab:efficacia-filtri ---")
        print(f"Fotogrammi ricevuti & {totale} & 100 \\\\")
        rimasti = totale
        for etichetta, fermati_qui in CASCATA:
            rimasti -= sum(1 for r in record if r.get("outcome") in fermati_qui)
            quota = 100.0 * rimasti / totale if totale else 0.0
            print(f"{etichetta} & {rimasti} & {quota:.1f} \\\\")


if __name__ == "__main__":
    main()
