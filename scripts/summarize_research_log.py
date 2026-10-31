#!/usr/bin/env python3
"""Riassume i log di ricerca, una riga per sessione.

Uso:
    python scripts/summarize_research_log.py logs/research/*.jsonl
    python scripts/summarize_research_log.py logs/research/*.jsonl --csv sessioni.csv

Per ogni sessione ricava quanto ha parlato il sistema, ogni quanto, con che
ritardo, e come sono andati i puntamenti. I file restano la fonte: per analisi
più fini si leggono direttamente, per esempio con pandas.read_json(lines=True).
"""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from statistics import median


def load(path: Path) -> list[dict]:
    events = []
    with path.open(encoding="utf-8", errors="replace") as source:
        for line in source:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def median_or_none(values: list[float]) -> float | None:
    return round(median(values), 1) if values else None


def summarize(events: list[dict]) -> dict:
    by_name: dict[str, list[dict]] = {}
    for event in events:
        by_name.setdefault(event["event"], []).append(event)

    start = (by_name.get("session_start") or [{}])[0]
    duration_s = events[-1]["t"] if events else 0.0
    utterances = by_name.get("utterance", [])
    speech_s = sum(item.get("audio_duration_s") or 0.0 for item in utterances)
    gaps = [
        later["t"] - earlier["t"]
        for earlier, later in zip(utterances, utterances[1:])
    ]
    skipped_reasons = Counter(
        item.get("reason") for item in by_name.get("utterance_skipped", [])
    )
    pointing = by_name.get("pointing_result", [])
    pointing_outcomes = Counter(item.get("outcome") for item in pointing)
    auto_outcomes = Counter(
        item.get("outcome") for item in by_name.get("auto_frame", [])
    )

    def latency(mode: str) -> float | None:
        return median_or_none(
            [
                item["frame_to_audio_ms"]
                for item in utterances
                if item.get("mode") == mode
            ]
        )

    minutes = duration_s / 60.0
    return {
        "session_id": events[0]["session_id"] if events else "",
        "participant_id": start.get("participant_id"),
        "task_id": start.get("task_id"),
        "app_version": start.get("app_version"),
        "duration_s": round(duration_s, 1),
        "utterances": len(utterances),
        "utterances_per_min": round(len(utterances) / minutes, 2) if minutes else None,
        "speech_ratio": round(speech_s / duration_s, 3) if duration_s else None,
        "median_gap_s": median_or_none(gaps),
        "auto_latency_ms": latency("AUTO"),
        "pointing_latency_ms": latency("POINTING"),
        "auto_frames": sum(auto_outcomes.values()),
        "auto_spoken": auto_outcomes.get("completed", 0),
        "auto_suppressed": sum(
            count
            for outcome, count in auto_outcomes.items()
            if outcome.startswith("suppressed")
        ),
        "pointing_activations": len(by_name.get("pointing_activation", [])),
        "pointing_retargets": sum(
            1 for item in by_name.get("pointing_activation", []) if item.get("retarget")
        ),
        "pointing_blocked": len(by_name.get("pointing_blocked", [])),
        "pointing_spoken": pointing_outcomes.get("spoken", 0),
        "pointing_failed": len(pointing) - pointing_outcomes.get("spoken", 0),
        "pointing_needs_repointing": sum(
            1 for item in pointing if item.get("needs_repointing")
        ),
        # Modalità lezione: quante slide, quante ripetizioni evitate, quanta
        # voce per slide. Restano a zero nelle sessioni in modalità general.
        "slides_described": len(by_name.get("slide_described", [])),
        "distinct_pages": len(
            {
                (item.get("page"), item.get("total"))
                for item in by_name.get("slide_described", [])
                if item.get("page") is not None
            }
        ),
        "repeats_avoided": skipped_reasons.get("same_slide", 0),
        "nothing_to_say": skipped_reasons.get("nothing_to_say", 0),
        "similar_skipped": skipped_reasons.get("similar_to_previous", 0),
        "blurry_frames": auto_outcomes.get("suppressed_blur", 0),
        "median_words": median_or_none(
            [len((item.get("text") or "").split()) for item in utterances if item.get("text")]
        ),
        "longest_audio_s": round(
            max((item.get("audio_duration_s") or 0.0 for item in utterances), default=0.0), 1
        ),
        "markers": len(by_name.get("marker", [])),
        "errors": len(by_name.get("error", [])),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", nargs="+", type=Path)
    parser.add_argument("--csv", type=Path, help="scrive il riepilogo in CSV")
    arguments = parser.parse_args()

    rows = [summarize(events) for events in map(load, sorted(arguments.log)) if events]
    if not rows:
        print("Nessun evento trovato.")
        return

    if arguments.csv:
        with arguments.csv.open("w", newline="", encoding="utf-8") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"{len(rows)} sessioni scritte in {arguments.csv}")
        return

    for row in rows:
        print(f"--- sessione {row['session_id']}")
        for key, value in row.items():
            if key != "session_id":
                print(f"  {key:28} {value}")


if __name__ == "__main__":
    main()
