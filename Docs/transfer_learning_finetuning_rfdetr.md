# Transfer Learning e Fine-Tuning di RF-DETR

> Guida operativa **e** teorica per estendere il vocabolario di oggetti riconosciuti da RF-DETR nel sistema Vision Caption.
> Nasce dal Problema **#9** di [`sfide_e_problemi.md`](./sfide_e_problemi.md): RF-DETR è *closed-set* su COCO (80 classi), quindi confonde oggetti fuori vocabolario (es. **stampante → "microonde"**). Obiettivo: aggiungere oggetti di uso quotidiano che il modello possa riconoscere, mantenendolo real-time.

---

## Indice

1. [Contesto e formulazione del problema](#1-contesto-e-formulazione-del-problema)
2. [Le due strade: closed-set vs open-vocabulary](#2-le-due-strade-closed-set-vs-open-vocabulary)
3. [Teoria del transfer learning e del fine-tuning](#3-teoria-del-transfer-learning-e-del-fine-tuning)
4. [Decisione critica: quale tassonomia di classi](#4-decisione-critica-quale-tassonomia-di-classi)
5. [Pipeline operativa end-to-end (con strumenti terzi)](#5-pipeline-operativa-end-to-end-con-strumenti-terzi)
6. [Ricetta di training RF-DETR (codice, v1.6.5)](#6-ricetta-di-training-rf-detr-codice-v165)
7. [Data augmentation](#7-data-augmentation)
8. [Valutazione del modello](#8-valutazione-del-modello)
9. [Reintegrazione del checkpoint nel backend](#9-reintegrazione-del-checkpoint-nel-backend)
10. [Approfondimenti accademici per la tesi](#10-approfondimenti-accademici-per-la-tesi)
11. [Checklist operativa](#11-checklist-operativa)
12. [Riferimenti](#12-riferimenti)

---

## 1. Contesto e formulazione del problema

RF-DETR (Roboflow-DETR, 2025) è un object detector real-time della famiglia **DETR** (DEtection TRansformer): architettura encoder-decoder transformer con **object queries** e **matching bipartito (Hungarian)**, backbone **DINOv2** (feature self-supervised), **senza anchor né NMS**. È distribuito pre-addestrato su **COCO (80 classi)** e Objects365.

Il punto chiave è che RF-DETR è un detector **closed-set**: la testa di classificazione ha un numero *fisso* di uscite (le 80 classi COCO), e per costruzione può emettere solo quelle etichette. Quando gli mostri un oggetto che non ha mai visto (una stampante), non ha l'opzione "non lo so": il classificatore assegna la classe con probabilità più alta tra quelle che conosce, tipicamente la più simile visivamente → **stampante ≈ microonde** (scatola rettangolare chiara con pannello frontale).

Questo non è un bug ma un limite intrinseco del vocabolario. La soluzione è **allargare il vocabolario** tramite fine-tuning, definendo le classi che ci servono. È rilevante perché nel sistema le etichette di RF-DETR alimentano a valle: (a) il **filtro semantico** dell'`HybridSceneDetectorAdapter` (confronto `Counter` di oggetti per sopprimere falsi positivi), e (b) potenzialmente il **contesto passato al VLM**. Etichette sbagliate degradano l'intera pipeline.

---

## 2. Le due strade: closed-set vs open-vocabulary

| | **A. Fine-tuning closed-set** *(scelta)* | **B. Open-vocabulary detection** |
|---|---|---|
| **Cosa fa** | Ri-addestra la testa su un insieme *finito* di classi definite da te | Rileva categorie *arbitrarie* da prompt testuale, zero-shot |
| **Modelli** | RF-DETR (fine-tuned) | GroundingDINO, YOLO-World, OWL-ViTv2, MM-GroundingDINO |
| **Velocità** | Real-time (RF-DETR resta com'è a livello di architettura) | Più lenti — spesso incompatibili col vincolo real-time |
| **Accuratezza sul dominio** | Alta se il dataset è buono | Media, generalista |
| **Costo** | Serve costruire un dataset annotato | Nessun training, ma prompt engineering |

**Per questo progetto la strada A è quella giusta**: il sistema è vincolato al real-time (RF-DETR è stato scelto proprio per la latenza ~48ms della scene detection), e gli oggetti da aggiungere sono un insieme *conosciuto e finito* di oggetti domestici quotidiani. L'open-vocabulary (B) resta comunque utile come **strumento di supporto** in fase di dataset building (vedi §5.3: auto-labeling con GroundingDINO). Pattern consigliato:

> **RF-DETR fine-tuned per l'inferenza real-time in produzione + GroundingDINO/Autodistill offline per scoprire e pre-etichettare gli oggetti nuovi**, che poi rientrano nel dataset di fine-tuning.

---

## 3. Teoria del transfer learning e del fine-tuning

**Transfer learning** = riutilizzare la conoscenza appresa da un modello su un compito "sorgente" (rilevamento su COCO/O365) per un compito "target" (i tuoi oggetti). Perché funziona:

- Il **backbone DINOv2** fornisce feature visive generali (bordi, texture, forme, parti di oggetti) già ottime, apprese in modo self-supervised su enormi quantità di immagini. Queste feature sono *riutilizzabili* per riconoscere oggetti nuovi.
- Il modello pre-addestrato è già un detector competente (sa "dove" sono gli oggetti, box regression, objectness). Il fine-tuning adatta soprattutto il "cosa" (la classificazione).
- Conseguenza pratica: servono **ordini di grandezza meno dati e meno epoche** rispetto al training from scratch. Poche centinaia/migliaia di *istanze* per classe possono bastare.

**La testa di classificazione.** Quando fai fine-tuning su un dataset con `N` categorie, RF-DETR ricostruisce la testa di classificazione con `N` uscite (il numero di classi è dedotto dalle `categories` del file `_annotations.coco.json`). Il modello risultante emetterà **quelle** classi. Questa è la leva con cui "allarghi il vocabolario".

**Feature extraction vs full fine-tuning.**
- *Feature extraction*: congeli il backbone, alleni solo la testa. Poco dato, veloce, ma adattamento limitato al dominio.
- *Full fine-tuning*: aggiorni anche il backbone. Migliore adattamento (utile perché il tuo dominio — camera del telefono, interni, blur — differisce da COCO), richiede più dato.
- Via di mezzo pratica in RF-DETR: **learning rate discriminativo** — LR più basso sul backbone (`lr_encoder`) rispetto al resto (`lr`), per adattare l'encoder in modo più conservativo (vedi §6).

**Catastrophic forgetting (dimenticanza catastrofica).** Se alleni *solo* sulle classi nuove, il modello **dimentica** le classi COCO: i pesi si specializzano sul nuovo dataset e le vecchie capacità si degradano. Mitigazioni:
1. **Includere nel dataset anche esempi delle classi vecchie** che vuoi mantenere (bilanciamento vecchio/nuovo).
2. Partire sempre dal **checkpoint pre-addestrato** (non da zero).
3. Per aggiunte incrementali nel tempo: **continual/class-incremental learning** (replay di esemplari + knowledge distillation dal modello vecchio) — vedi §10.

**Domain gap.** La differenza tra la distribuzione di training (foto COCO curate) e quella di deployment (frame mossi dalla webcam del telefono, luce di casa) è essa stessa una fonte di errore. Il modo migliore di chiuderla è **includere nel dataset immagini catturate dallo stesso setup di deployment** (vedi §5.2) e usare augmentation coerenti (blur, luce — §7).

---

## 4. Decisione critica: quale tassonomia di classi

Hai detto che ti servono oggetti quotidiani "che COCO in parte ha già". Questa è **la** decisione di progetto e va giustificata in tesi. Tre opzioni:

**Opzione 4a — Solo classi nuove (piccolo vocabolario dedicato).**
Definisci solo gli oggetti che ti mancano (es. `printer`, `router`, `keyboard_tray`, …). Semplice e veloce da annotare, ma il modello **dimentica COCO** → perdi `person`, `chair`, `laptop`, ecc. Sconsigliata se il sistema deve descrivere scene complete.

**Opzione 4b — COCO esteso (vocabolario unificato).** *(consigliata)*
Costruisci un dataset le cui `categories` includono **le classi COCO che ti servono davvero** (un sottoinsieme, es. person, chair, tv, laptop, bottle, cup…) **più** le nuove (printer, ecc.). Il modello mantiene le vecchie e impara le nuove. Costo: devi annotare (o riusare annotazioni esistenti) anche per le classi vecchie nelle tue immagini.
- Scorciatoia pratica: parti da un **dataset pubblico già annotato** che copre oggetti domestici (Roboflow Universe ne ha molti su "indoor/household objects") e **fondilo** con le tue classi nuove. Attento al *label space merging* (§10).

**Opzione 4c — Fine-tuning progressivo su COCO+delta.**
Prendi un dataset che è "COCO + le tue classi" e fai un solo fine-tuning. Concettualmente uguale a 4b, differisce solo per come assembli i dati.

**Raccomandazione operativa per il tuo caso:** parti da **4b** con un vocabolario ristretto e mirato — non ti servono tutte le 80 classi COCO, solo quelle che compaiono davvero nelle stanze dell'utente + gli oggetti mancanti che causano errori (stampante in primis). Un vocabolario di ~20-40 classi ben curate, addestrato su immagini del tuo dominio, batterà COCO-80 generico sul tuo compito.

**Hard negatives.** Per correggere specificamente la confusione stampante→microonde, includi nel dataset **immagini di microonde correttamente etichettate** *e* immagini di stampanti: così il modello impara il confine decisionale tra le due, invece di mapparle sulla stessa classe.

---

## 5. Pipeline operativa end-to-end (con strumenti terzi)

Sì, puoi (e conviene) usare strumenti terzi. Flusso consigliato: **Roboflow** (annotazione + hosting + export COCO) → **Google Colab** (GPU T4/L4 gratuita/economica per il training) → download del checkpoint → esecuzione **in locale** nel backend.

### 5.1 Definizione delle classi (ontologia)
- Elenca le classi in modo **mutuamente esclusivo** e a **granularità coerente** (non mischiare "sedia" con "mobile").
- Definisci per iscritto ogni classe (cos'è / cosa non è) → garantisce coerenza di annotazione (*inter-annotator agreement*).
- Parti dagli errori reali osservati (stampante, ecc.) e dagli oggetti effettivamente presenti nelle stanze target.

### 5.2 Raccolta immagini (matching col deployment)
- **Cattura frame dallo stesso setup reale**: camera del telefono, stanze reali, illuminazione domestica, **anche frame leggermente mossi** (il tuo sistema panoramica). Questo chiude il domain gap meglio di qualsiasi dataset pubblico.
- Copri la varianza: punti di vista, distanze/scale, occlusioni, luce diurna/notturna, sfondi diversi.
- Il tuo stesso sistema è una **sorgente di dati ideale**: puoi loggare i frame in produzione (vedi active learning, §10).

### 5.3 Annotazione (manuale + auto-labeling)
- **Manuale**: strumenti come **Roboflow Annotate**, CVAT, Label Studio, labelImg. Box aderenti, includi oggetti occlusi/troncati.
- **Auto-labeling (accelera moltissimo)**: usa un modello open-vocabulary per pre-etichettare, poi **verifica a mano**:
  - **Autodistill** + **GroundingDINO** (o Grounding DINO + **SAM** per box precisi): dai i nomi delle classi come prompt testuale, ottieni box automatici → correggi solo gli errori.
  - Questo è il modo più veloce di "allargare il dataset" ed è metodologicamente citabile (distillazione da foundation model).
- **Qualità > quantità**: il *label noise* degrada il training più di quanto sembri. Fai un passaggio di review.

### 5.4 Split e formato COCO
RF-DETR rileva automaticamente il formato dalla struttura delle cartelle. Serve **COCO** con tre split e un file `_annotations.coco.json` per split:

```
dataset/
├── train/
│   ├── _annotations.coco.json
│   ├── image1.jpg
│   └── ...
├── valid/
│   ├── _annotations.coco.json
│   └── ...
└── test/
    ├── _annotations.coco.json
    └── ...
```

Il JSON contiene `images`, `categories` (id + name → **qui vive il tuo vocabolario**) e `annotations` (bbox in formato `[x, y, width, height]`, con `category_id`).

**Regole sugli split (per non falsare le metriche):**
- **No leakage temporale**: frame dello stesso video/sessione sono correlati → devono stare *tutti* nello stesso split. Splitta per sessione, non per singolo frame.
- Split tipico 70/20/10 (train/valid/test), stratificato per classe.
- Roboflow gestisce split ed export COCO automaticamente.

### 5.5 (vedi §7 per la data augmentation)

---

## 6. Ricetta di training RF-DETR (codice, v1.6.5)

> API di alto livello `RFDETR.train()` — un'unica chiamata configura ed esegue tutto (sotto usa PyTorch Lightning). Riferimento: doc locale `Docs/rfdetr_1_6_5.md` e [notebook Roboflow](https://colab.research.google.com/github/roboflow-ai/notebooks/blob/main/notebooks/how-to-finetune-rf-detr-on-detection-dataset.ipynb).

### Installazione
```bash
pip install -q "rfdetr>=1.4.0" supervision roboflow
# per i logger (TensorBoard/W&B): pip install "rfdetr[loggers]"
```

### Training base
```python
from rfdetr import RFDETRMedium   # stessa variante usata nel backend

model = RFDETRMedium()            # parte dai pesi pre-addestrati COCO/O365

model.train(
    dataset_dir="path/to/dataset",   # cartella con train/ valid/ test/
    epochs=100,
    batch_size=4,                    # per-GPU
    grad_accum_steps=4,              # batch_size × grad_accum = effective batch
    lr=1e-4,                         # LR per la maggior parte del modello
    lr_encoder=1.5e-4,               # LR del backbone (puoi abbassarlo per FT conservativo)
    resolution=640,                  # DEVE essere divisibile per 14
    weight_decay=1e-4,               # regolarizzazione L2 (anti-overfitting)
    output_dir="output",
    device="cuda",                   # "cuda" | "cpu" | "mps"
    early_stopping=True,             # ferma quando la mAP di validazione non migliora
)
```

### Regola dell'effective batch size = 16
`effective_batch = batch_size × grad_accum_steps × num_gpus`. Mantienilo **~16**:

| GPU | `batch_size` | `grad_accum_steps` | Effective |
|---|---|---|---|
| T4 (Colab) | 4 | 4 | 16 |
| A100 | 16 | 1 | 16 |
| 2× GPU | 4 | 2 | 16 |

Il gradient accumulation permette di allenare con lo stesso batch efficace anche su GPU con poca VRAM (come la T4 gratuita di Colab).

### Early stopping (anti-overfitting)
```python
model.train(
    dataset_dir="path/to/dataset",
    epochs=200,
    early_stopping=True,
    early_stopping_patience=15,     # epoche senza miglioramento prima di fermarsi (default 10)
    early_stopping_min_delta=0.005, # miglioramento minimo di mAP che "conta" (default 0.001)
    early_stopping_use_ema=True,    # monitora la mAP del modello EMA
)
```

### Checkpoint prodotti (in `output_dir`)
- `checkpoint.pth` — ultimo checkpoint (con optimizer/scheduler → per **resume**).
- `checkpoint_<N>.pth` — periodici ogni `checkpoint_interval` epoche (default 10).
- `checkpoint_best_ema.pth` / `checkpoint_best_regular.pth` — migliori su validazione (pesi EMA / raw).
- **`checkpoint_best_total.pth`** — checkpoint finale "stripped" (solo pesi), scelto tra EMA e raw in base alla validazione → **questo è quello da usare per l'inferenza/deploy**.

### Riprendere un training interrotto
```python
model.train(..., resume="output/checkpoint.pth")   # ripristina anche optimizer/scheduler
```
Per **inizializzare** un nuovo training da pesi già fine-tuned usa invece `pretrain_weights="checkpoint_best_total.pth"` nel costruttore.

### Iperparametri principali (tabella)
| Parametro | Default | Note |
|---|---|---|
| `epochs` | 100 | Passate complete sul dataset |
| `batch_size` | 4 | Campioni per iterazione (↑ = più VRAM) |
| `grad_accum_steps` | 4 | Accumulo gradienti per batch efficace |
| `lr` | 1e-4 | LR generale |
| `lr_encoder` | 1.5e-4 | LR del backbone encoder |
| `resolution` | dipende dal modello | **divisibile per 14**; ↑ accuratezza, ↑ memoria/latenza |
| `weight_decay` | 1e-4 | Regolarizzazione L2 |
| `device` | "cuda" | cuda / cpu / mps |
| `checkpoint_interval` | 10 | Salva ogni N epoche |
| `tensorboard` | True | Logging locale (richiede `rfdetr[loggers]`) |
| `wandb` | False | Logging cloud (richiede `rfdetr[loggers]`) |

**Nota sulla risoluzione:** è il trade-off centrale **accuratezza ↔ latenza**, decisivo dato il vincolo real-time. Se addestri a `resolution` diversa da quella di inferenza, tienine conto: idealmente allena e inferisci alla stessa risoluzione (nel backend l'inferenza usa `RFDETRMedium` con `optimize_for_inference`).

**GPU e Colab:** una `RFDETRMedium` fine-tuned si allena comodamente su una **T4/L4 di Colab** con `batch_size=4, grad_accum_steps=4`. Training in Colab → scarichi `checkpoint_best_total.pth` → lo esegui in locale sul tuo backend (che già gira su `cuda`).

---

## 7. Data augmentation

RF-DETR applica di default un **horizontal flip (50%)**. Puoi passare augmentation custom via **Albumentations** (70+ trasformazioni, con gestione automatica dei bounding box) tramite `aug_config`:

```python
model.train(
    dataset_dir="path/to/dataset",
    aug_config={
        "HorizontalFlip": {"p": 0.5},
        "RandomBrightnessContrast": {"p": 0.3},
        "MotionBlur": {"blur_limit": 7, "p": 0.3},   # rilevante: i tuoi frame in panoramica sono mossi
    },
)
# aug_config={} disattiva tutte le augmentation
```

**Teoria (perché servono):**
- **Fotometriche** (brightness/contrast/HSV): robustezza alla luce domestica variabile.
- **Geometriche** (flip, scale, crop): invarianza a punto di vista/scala; i box vengono trasformati coerentemente.
- **Motion blur**: *specificamente utile qui* — addestrare con blur sintetico chiude il gap coi frame mossi delle panoramiche.
- **Random Erasing / Cutout**: robustezza alle occlusioni.
- **Copy-Paste / Mosaic**: potenti per **classi rare** (incolli istanze su nuovi sfondi → più esempi).

Regola pratica dai default RF-DETR: con **< 500 immagini** usa augmentation conservative (flip + lieve brightness/contrast); più aggressive man mano che il dataset cresce. Attenzione: i DETR sono più sensibili di YOLO ad augmentation troppo aggressive — parti conservativo.

---

## 8. Valutazione del modello

**Metriche COCO** (standard, citabili in tesi):
- **mAP@[.5:.95]** — metrica principale (media dell'AP su soglie IoU da 0.5 a 0.95).
- **AP50 / AP75** — AP a IoU 0.5 / 0.75.
- **AP small / medium / large** — per dimensione dell'oggetto.
- **AR** (Average Recall).

**Cosa guardare oltre al numero globale:**
- **AP per-classe**: individua le classi deboli (probabilmente quelle nuove con pochi dati) → dove raccogliere altri esempi.
- **Matrice di confusione**: verifica che stampante non venga più confusa con microonde. È la prova diretta che il fine-tuning ha risolto il Problema #9.
- **Test set che riflette il deployment reale** (tue stanze, tuo telefono): è ciò che rende credibile la valutazione. Non valutare solo su immagini "facili".
- **Latenza / FPS** misurati: per un sistema real-time l'accuratezza da sola non basta — documenta il trade-off.

---

## 9. Reintegrazione del checkpoint nel backend

Una volta ottenuto `checkpoint_best_total.pth`, caricalo nel modello del backend passando `pretrain_weights` al costruttore. Nel codice attuale (`app.py`) il modello è creato così:

```python
from rfdetr import RFDETRMedium
rfdetr_model = RFDETRMedium(device=device)
```

Diventa:

```python
rfdetr_model = RFDETRMedium(
    pretrain_weights="weights/checkpoint_best_total.pth",  # il tuo fine-tuned
    device=device,
)
rfdetr_model.optimize_for_inference(compile=..., batch_size=1, dtype=...)  # invariato
```

**Attenzione al mapping delle etichette.** L'`RfdetrSceneDetectorAdapter` legge `sv_detections.data["class_name"]`. Dopo il fine-tuning i nomi delle classi provengono dalle `categories` del **tuo** dataset, **non** più da COCO. Quindi:
- Il notebook Roboflow usa `COCO_CLASSES` per mappare gli id: dopo il fine-tuning **quella mappa non vale più**.
- Verifica che `data["class_name"]` riporti i nomi del tuo vocabolario (RF-DETR li propaga dal checkpoint). Se così non fosse, dovrai mappare `class_id → nome` con la lista di categorie del tuo dataset.
- Ricorda che il filtro semantico Hybrid (`Counter([d.class_name ...])`) e l'eventuale contesto al VLM ora ragionano sul **nuovo vocabolario** — è esattamente ciò che vogliamo.

---

## 10. Approfondimenti accademici per la tesi

**Set-prediction loss (DETR).** RF-DETR non usa anchor/NMS: predice un *insieme* fisso di box tramite **object queries** e li accoppia al ground truth con il **matching bipartito di Hungarian**. La loss combina *classification loss* + **L1** (coordinate) + **GIoU** (overlap). Il **numero di object queries** è il tetto massimo di oggetti rilevabili per immagine: in stanze affollate deve superare il massimo di oggetti attesi.

**Backbone DINOv2.** Feature self-supervised pre-addestrate senza etichette: è ciò che rende il transfer learning così efficace (rappresentazioni generali e trasferibili).

**Class imbalance / long-tail.** Se alcune classi hanno pochi esempi (tipico delle classi nuove), il modello le impara peggio. Rimedi: **oversampling**/**repeat-factor sampling** (stile dataset LVIS), **copy-paste augmentation**, **loss weighting**. Monitora l'AP per-classe.

**Active learning (il modo più efficiente di crescere nel tempo).** Loop ideale dato che il tuo sistema *già* streamma frame:
1. In produzione, **logga i frame** dove il modello è incerto (confidence bassa) o sbaglia.
2. Etichetta **solo quelli** (*uncertainty sampling*, *hard-negative mining*).
3. Ri-addestra (o fai `resume`).

Massimizza il guadagno per annotazione. La pipeline WebSocket è la sorgente perfetta di *hard cases* reali.

**Continual / class-incremental learning.** Per aggiungere classi *nel tempo* senza ri-addestrare tutto: **replay di esemplari** + **knowledge distillation** dal modello precedente, per limitare il catastrophic forgetting.

**Dati sintetici.** Rendering 3D di scene indoor (domain randomization) o **augmentation generativa** (diffusion/inpainting per inserire oggetti) per classi rare/costose. Attento al *sim-to-real gap*: miscela sempre con dati reali.

**Label space merging (se fondi più dataset).** Unificare tassonomie e rimappare gli id; risolvere definizioni in conflitto. Occhio al **partial annotation problem**: un'immagine etichettata solo per la classe X ma che contiene Y non annotata → Y trattato come *background* → penalizza il training. Soluzioni: **pseudo-labeling** delle annotazioni mancanti, training con dataset "federati".

**Dataset pubblici indoor/quotidiani da cui attingere:** Roboflow Universe (household/indoor), **LVIS** (1200 classi, long-tail), **Open Images** (600 classi), **Objects365**, **ADE20K / SUN RGB-D / ScanNet** (scene indoor).

---

## 11. Checklist operativa

- [ ] Definire il vocabolario di classi (Opzione **4b**: COCO ristretto + oggetti nuovi; includere microonde come hard negative).
- [ ] Raccogliere immagini dal setup reale (telefono, stanze, luce, frame mossi).
- [ ] Annotare (Roboflow Annotate) o pre-etichettare con Autodistill+GroundingDINO e verificare.
- [ ] Esportare in **COCO** con split `train/valid/test` (no leakage temporale) via Roboflow.
- [ ] Fine-tuning in **Colab** con `RFDETRMedium.train(...)` (effective batch 16, early stopping, motion-blur aug).
- [ ] Valutare: mAP, **AP per-classe**, **matrice di confusione** (stampante ≠ microonde), test set realistico, latenza.
- [ ] Scaricare `checkpoint_best_total.pth`.
- [ ] Caricarlo nel backend via `RFDETRMedium(pretrain_weights=...)` e verificare il mapping `class_name`.
- [ ] Impostare un loop di **active learning** loggando gli hard cases dalla pipeline.

---

## 12. Riferimenti

- **Doc RF-DETR (locale):** [`Docs/rfdetr_1_6_5.md`](./rfdetr_1_6_5.md) — sezioni *train*, *dataset-formats*, *advanced*, *augmentations*, *training-parameters*.
- **Notebook fine-tuning Roboflow:** <https://colab.research.google.com/github/roboflow-ai/notebooks/blob/main/notebooks/how-to-finetune-rf-detr-on-detection-dataset.ipynb>
- **Doc RF-DETR online:** <https://rfdetr.roboflow.com/>
- **Albumentations:** <https://albumentations.ai/>
- **Autodistill (auto-labeling):** <https://github.com/autodistill/autodistill>
- **Problema originale:** [`sfide_e_problemi.md`](./sfide_e_problemi.md) #9 (e #8 per il fix del trigger).
