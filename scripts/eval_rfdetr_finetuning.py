#!/usr/bin/env python3
"""Confronta il modello COCO pre-addestrato con quello adattato al dominio.

Valuta entrambi sullo stesso insieme di prova indipendente --- il file
``test/_annotations.coco.json`` prodotto dalla costruzione del dataset, che non
e' mai stato usato ne' per l'addestramento ne' per la selezione del checkpoint
--- e riporta le metriche COCO standard separando due domande:

1. le 73 categorie che i due modelli condividono, per stabilire se
   l'adattamento abbia degradato cio' che il modello gia' sapeva;
2. le 4 categorie assenti da COCO, per stabilire se le abbia imparate.

Produce inoltre il conteggio delle stampanti classificate correttamente, che e'
la verifica diretta dell'errore osservato all'origine del problema.

Uso::

    python scripts/eval_rfdetr_finetuning.py \\
        --dataset ~/Documents/fineTuning/data/rfdetr/daisy_coco_v1/test \\
        --checkpoint models/rfdetr/checkpoint_best_total.pth
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

RADICE = Path(__file__).resolve().parents[1]

CLASSI_NUOVE = ("printer", "3d_printer", "f1_car", "vape")

# Soglia bassa: la mAP integra sulla confidenza, quindi tagliare presto
# falserebbe il richiamo. Il limite di 100 rilevazioni per immagine e' quello
# del protocollo COCO.
SOGLIA_INFERENZA = 0.001
MAX_RILEVAZIONI = 100


def normalizza(nome: str) -> str:
    """Riconduce alla stessa forma i nomi COCO e quelli del dataset."""
    return nome.strip().lower().replace(" ", "_").replace("-", "_")


# ---------------------------------------------------------------------------
# Inferenza
# ---------------------------------------------------------------------------

def prevedi(modello, cartella: Path, immagini: list[dict],
            nome_a_categoria: dict[str, int]) -> list[dict]:
    """Esegue il modello su ogni immagine e restituisce rilevazioni COCO.

    Le classi sono riconciliate per nome, non per indice: i due modelli hanno
    spazi di etichette diversi e un confronto per indice sarebbe scorretto.
    """
    risultati: list[dict] = []
    ignorate: set[str] = set()

    for posizione, voce in enumerate(immagini, start=1):
        # ``file_name`` puo' gia' contenere il prefisso della sottocartella:
        # in quel caso va risolto rispetto alla radice dello split.
        percorso = cartella / voce["file_name"]
        if not percorso.is_file():
            percorso = cartella.parent / voce["file_name"]
        if not percorso.is_file():
            percorso = cartella / Path(voce["file_name"]).name
        immagine = cv2.imread(str(percorso))
        if immagine is None:
            print(f"  ! immagine illeggibile: {percorso.name}", file=sys.stderr)
            continue

        rilevazioni = modello.predict(
            cv2.cvtColor(immagine, cv2.COLOR_BGR2RGB),
            threshold=SOGLIA_INFERENZA,
        )

        nomi = rilevazioni.data.get("class_name")
        ordine = np.argsort(-rilevazioni.confidence)[:MAX_RILEVAZIONI]

        for indice in ordine:
            if nomi is None:
                continue
            nome = normalizza(str(nomi[indice]))
            categoria = nome_a_categoria.get(nome)
            if categoria is None:
                ignorate.add(nome)
                continue

            x_min, y_min, x_max, y_max = rilevazioni.xyxy[indice]
            risultati.append({
                "image_id": voce["id"],
                "category_id": categoria,
                "bbox": [float(x_min), float(y_min),
                         float(x_max - x_min), float(y_max - y_min)],
                "score": float(rilevazioni.confidence[indice]),
            })

        if posizione % 50 == 0:
            print(f"  {posizione}/{len(immagini)} immagini")

    if ignorate:
        print(f"  classi previste ma assenti dal dataset, ignorate: "
              f"{sorted(ignorate)}")
    return risultati


# ---------------------------------------------------------------------------
# Valutazione
# ---------------------------------------------------------------------------

def valuta(coco: COCO, rilevazioni: list[dict], categorie: list[int],
           immagini: list[int] | None = None) -> dict[str, float]:
    """Calcola le metriche COCO su categorie e, se indicate, immagini date."""
    pertinenti = [r for r in rilevazioni if r["category_id"] in categorie]
    if immagini is not None:
        ammesse = set(immagini)
        pertinenti = [r for r in pertinenti if r["image_id"] in ammesse]
    if not pertinenti:
        return {"mAP": float("nan"), "AP50": float("nan"),
                "AR100": float("nan")}

    with contextlib.redirect_stdout(io.StringIO()):
        previsioni = coco.loadRes(pertinenti)
        valutatore = COCOeval(coco, previsioni, "bbox")
        valutatore.params.catIds = categorie
        if immagini is not None:
            valutatore.params.imgIds = list(immagini)
        valutatore.evaluate()
        valutatore.accumulate()
        valutatore.summarize()

    return {
        "mAP": float(valutatore.stats[0]),
        "AP50": float(valutatore.stats[1]),
        "AR100": float(valutatore.stats[8]),
    }


def stampanti_corrette(coco: COCO, rilevazioni: list[dict],
                       id_stampante: int, soglia_iou: float = 0.5,
                       soglia_score: float = 0.30) -> tuple[int, int]:
    """Quante stampanti annotate ricevono un riquadro etichettato stampante."""
    annotazioni = [
        a for a in coco.dataset["annotations"]
        if a["category_id"] == id_stampante
    ]
    per_immagine: dict[int, list[dict]] = {}
    for r in rilevazioni:
        if r["score"] >= soglia_score:
            per_immagine.setdefault(r["image_id"], []).append(r)

    trovate = 0
    for annotazione in annotazioni:
        ax, ay, aw, ah = annotazione["bbox"]
        for previsione in per_immagine.get(annotazione["image_id"], []):
            if previsione["category_id"] != id_stampante:
                continue
            px, py, pw, ph = previsione["bbox"]
            sx = max(0.0, min(ax + aw, px + pw) - max(ax, px))
            sy = max(0.0, min(ay + ah, py + ph) - max(ay, py))
            intersezione = sx * sy
            unione = aw * ah + pw * ph - intersezione
            if unione > 0 and intersezione / unione >= soglia_iou:
                trovate += 1
                break
    return trovate, len(annotazioni)


# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True,
                        help="cartella dello split di prova")
    parser.add_argument("--checkpoint", type=Path,
                        default=RADICE / "models/rfdetr/checkpoint_best_total.pth")
    parser.add_argument("--uscita", type=Path,
                        default=RADICE / "artifacts/benchmark")
    args = parser.parse_args()

    annotazioni = args.dataset / "_annotations.coco.json"
    cartella_immagini = args.dataset / "images"
    if not cartella_immagini.is_dir():
        cartella_immagini = args.dataset

    with contextlib.redirect_stdout(io.StringIO()):
        coco = COCO(str(annotazioni))

    categorie = coco.loadCats(coco.getCatIds())
    nome_a_categoria = {normalizza(c["name"]): c["id"] for c in categorie}
    nuove = [nome_a_categoria[n] for n in CLASSI_NUOVE if n in nome_a_categoria]
    condivise = [c["id"] for c in categorie
                 if normalizza(c["name"]) not in CLASSI_NUOVE]

    immagini = coco.loadImgs(coco.getImgIds())

    # Le immagini importate dai dataset delle classi nuove sono annotate
    # soltanto per quella classe: un oggetto COCO presente ma non annotato
    # conterebbe come falso positivo e penalizzerebbe il modello che lo rileva.
    # Il confronto sulle classi condivise viene percio' ripetuto sul solo
    # sottoinsieme proveniente da COCO 2017, che e' annotato in modo esaustivo.
    esaustive = [v["id"] for v in immagini if "coco2017" in v["file_name"]]

    print(f"Insieme di prova: {len(immagini)} immagini, "
          f"{len(coco.dataset['annotations'])} annotazioni")
    print(f"  di cui esaustivamente annotate (COCO 2017): {len(esaustive)}")
    print(f"Categorie condivise: {len(condivise)}   nuove: {len(nuove)}\n")

    from rfdetr import RFDETRMedium

    esiti: dict[str, dict] = {}

    for etichetta, costruttore in (
        ("coco", lambda: RFDETRMedium()),
        ("adattato", lambda: RFDETRMedium.from_checkpoint(str(args.checkpoint))),
    ):
        print(f"--- modello {etichetta} ---")
        modello = costruttore()
        rilevazioni = prevedi(modello, cartella_immagini, immagini,
                              nome_a_categoria)
        print(f"  rilevazioni prodotte: {len(rilevazioni)}")

        esito = {
            "condivise": valuta(coco, rilevazioni, condivise),
            "condivise_esaustive": valuta(coco, rilevazioni, condivise,
                                          esaustive),
            "nuove": (valuta(coco, rilevazioni, nuove)
                      if etichetta == "adattato" else None),
        }
        if "printer" in nome_a_categoria:
            trovate, totali = stampanti_corrette(
                coco, rilevazioni, nome_a_categoria["printer"]
            )
            esito["stampanti"] = {"corrette": trovate, "totali": totali}
        esiti[etichetta] = esito
        del modello
        print()

    # --- riepilogo ---------------------------------------------------------
    print("=" * 66)
    print(f"{'Metrica':<40}{'COCO':>12}{'Adattato':>12}")
    print("-" * 66)
    for gruppo, suffisso in (("condivise", "tutte le immagini"),
                             ("condivise_esaustive", "solo COCO 2017")):
        for chiave, nome in (("mAP", "mAP 50:95"), ("AP50", "AP50"),
                             ("AR100", "AR100")):
            a = esiti["coco"][gruppo][chiave]
            b = esiti["adattato"][gruppo][chiave]
            print(f"{nome + ' condivise, ' + suffisso:<40}{a:>12.3f}{b:>12.3f}")
        print("-" * 66)
    nuove_map = esiti["adattato"]["nuove"]
    print(f"{'mAP 50:95 sulle quattro classi nuove':<40}"
          f"{'n/a':>12}{nuove_map['mAP']:>12.3f}")
    sc, sa = esiti["coco"]["stampanti"], esiti["adattato"]["stampanti"]
    print(f"{'Stampanti classificate correttamente':<40}"
          f"{sc['corrette']:>7}/{sc['totali']:<4}"
          f"{sa['corrette']:>7}/{sa['totali']:<4}")
    print("=" * 66)

    args.uscita.mkdir(parents=True, exist_ok=True)
    destinazione = args.uscita / "confronto_finetuning.json"
    destinazione.write_text(
        json.dumps({
            "immagini": len(immagini),
            "annotazioni": len(coco.dataset["annotations"]),
            "categorie_condivise": len(condivise),
            "categorie_nuove": len(nuove),
            "soglia_inferenza": SOGLIA_INFERENZA,
            "esiti": esiti,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nRisultati salvati in {destinazione}")


if __name__ == "__main__":
    main()
