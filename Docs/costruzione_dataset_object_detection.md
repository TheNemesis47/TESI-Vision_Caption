# Costruzione e Allargamento di un Dataset per l'Object Detection

> Tutorial accademico sulla **preparazione dei dati** per il fine-tuning di RF-DETR nel sistema Vision Caption.
> È il companion metodologico di [`transfer_learning_finetuning_rfdetr.md`](./transfer_learning_finetuning_rfdetr.md): quel documento spiega *come si addestra*, questo spiega *come si costruisce e si allarga il dataset* che rende possibile l'addestramento.
> Nasce dalla necessità operativa emersa dal Problema **#9** ([`sfide_e_problemi.md`](./sfide_e_problemi.md)): far riconoscere a RF-DETR oggetti fuori dal vocabolario COCO (es. la stampante scambiata per "microonde").

---

## Indice

1. [Premessa concettuale: dato, annotazione, supervisione](#1-premessa-concettuale-dato-annotazione-supervisione)
2. [Anatomia formale di un dataset (formato COCO)](#2-anatomia-formale-di-un-dataset-formato-coco)
3. [Il ciclo di vita del dataset](#3-il-ciclo-di-vita-del-dataset)
4. [Cosa significa "allargare" un dataset](#4-cosa-significa-allargare-un-dataset)
5. [Strategia A — Raccolta propria e annotazione manuale](#5-strategia-a--raccolta-propria-e-annotazione-manuale)
6. [Strategia B — Auto-labeling (distillazione da foundation model)](#6-strategia-b--auto-labeling-distillazione-da-foundation-model)
7. [Strategia C — Riuso e fusione di dataset pubblici (Roboflow Universe)](#7-strategia-c--riuso-e-fusione-di-dataset-pubblici-roboflow-universe)
8. [Il problema della fusione: label space e annotazione parziale](#8-il-problema-della-fusione-label-space-e-annotazione-parziale)
9. [Qualità del dataset: rumore, bilanciamento, split](#9-qualità-del-dataset-rumore-bilanciamento-split)
10. [Quanto deve essere grande? (sufficienza statistica)](#10-quanto-deve-essere-grande-sufficienza-statistica)
11. [Sintesi operativa](#11-sintesi-operativa)
12. [Riferimenti](#12-riferimenti)

---

## 1. Premessa concettuale: dato, annotazione, supervisione

L'object detection basato su reti profonde è un problema di **apprendimento supervisionato**: il modello apprende una funzione `f: immagine → insieme di (box, classe)` a partire da **esempi già risolti**. Ogni esempio è una coppia

> (input, output atteso) = (immagine, elenco di oggetti con la loro posizione e la loro etichetta).

Il **dataset** è la collezione di questi esempi. Non è un contenitore neutro di immagini: è il *supervisore* del modello. Tutto ciò che il modello saprà riconoscere, e tutto ciò che sbaglierà sistematicamente, è determinato dalla distribuzione e dalla qualità del dataset. Da qui una massima ricorrente in letteratura (*data-centric AI*, Ng 2021): **a parità di architettura, migliorare i dati produce più guadagno che migliorare il modello**.

Tre termini vanno distinti con precisione, perché nel linguaggio comune si confondono:

- **Immagine (input)**: il dato grezzo, il pixel. Da sola non insegna nulla.
- **Annotazione (etichetta, *label*)**: l'informazione aggiunta da un supervisore umano (o da un modello) che dice *dove* sono gli oggetti e *cosa* sono. È il segnale di apprendimento.
- **Classe (categoria)**: il tipo di oggetto (`printer`, `person`…). L'insieme delle classi è il **vocabolario** del dataset, e diventa il vocabolario del modello dopo il fine-tuning.

**Conseguenza fondamentale.** Le classi *vivono nel dataset*, non nel modello. Il modello pre-addestrato RF-DETR "conosce" le 80 classi COCO solo perché è stato addestrato sul dataset COCO. Aggiungere una classe non è un'operazione sul modello: è un'operazione sui **dati**, seguita da un ri-addestramento che trasferisce quella conoscenza nei pesi (§3 di `transfer_learning_finetuning_rfdetr.md`).

---

## 2. Anatomia formale di un dataset (formato COCO)

RF-DETR consuma il dataset nel formato **COCO** (Common Objects in Context, Lin et al. 2014), lo standard *de facto* per la detection. La struttura su disco separa fisicamente i tre **split**, ciascuno con le proprie immagini e un unico file di annotazioni:

```
dataset/
├── train/
│   ├── _annotations.coco.json
│   ├── img_0001.jpg
│   └── ...
├── valid/
│   ├── _annotations.coco.json
│   └── ...
└── test/
    ├── _annotations.coco.json
    └── ...
```

### Il file di annotazioni

È un JSON con tre array collegati da chiavi relazionali (una struttura essenzialmente **relazionale**, normalizzata):

```jsonc
{
  "images": [
    { "id": 1, "file_name": "img_0001.jpg", "width": 1280, "height": 720 }
  ],

  "categories": [                     // il VOCABOLARIO — definisce lo spazio delle classi
    { "id": 1, "name": "printer",   "supercategory": "appliance" },
    { "id": 2, "name": "microwave", "supercategory": "appliance" },
    { "id": 3, "name": "person",    "supercategory": "person"    }
  ],

  "annotations": [                    // gli ESEMPI — un record per ogni oggetto in ogni immagine
    {
      "id": 1,
      "image_id": 1,                  // FK → images.id : in quale immagine
      "category_id": 1,               // FK → categories.id : quale classe (printer)
      "bbox": [340, 120, 200, 260],   // [x, y, larghezza, altezza] in pixel
      "area": 52000,                  // area del box (usata per le metriche AP small/medium/large)
      "iscrowd": 0                    // 0 = istanza singola, 1 = folla (annotazione approssimata)
    }
  ]
}
```

**Semantica dei tre array:**

| Array | Ruolo | Analogia |
|---|---|---|
| `images` | anagrafica dei file (dimensioni, nome) | la tabella "documenti" |
| `categories` | **definizione dello spazio delle classi** | il "vocabolario / dizionario" |
| `annotations` | i fatti supervisionati: *in questa immagine, in questa posizione, c'è questa classe* | le "righe di fatto" che collegano documento e vocabolario |

**Il formato del box.** COCO usa `[x, y, w, h]` con origine `(x, y)` nell'**angolo in alto a sinistra** del box e coordinate in **pixel assoluti**. È diverso da altre convenzioni (YOLO usa `[x_center, y_center, w, h]` **normalizzato** in `[0,1]`; Pascal VOC usa `[x_min, y_min, x_max, y_max]`). Nel *label space merging* (§8) le conversioni tra convenzioni sono una fonte tipica di bug silenziosi: un box giusto ma nel formato sbagliato produce annotazioni plausibili ma spostate.

**Dove si allarga il vocabolario.** Aggiungere una classe = aggiungere una voce in `categories` **e** produrre le relative `annotations` nelle immagini in cui quell'oggetto compare. Il numero di uscite della testa di classificazione di RF-DETR viene dedotto proprio dal numero di `categories`.

---

## 3. Il ciclo di vita del dataset

La costruzione di un dataset è un **processo iterativo**, non un evento singolo. Le fasi canoniche:

```
   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
   │ 1. Ontologia │ →  │ 2. Raccolta  │ →  │ 3. Annotaz.  │ →  │ 4. Split &   │
   │  (le classi) │    │  (immagini)  │    │  (box+label) │    │   export     │
   └──────────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘
          ↑                                                            │
          │                    ┌──────────────┐    ┌──────────────┐   │
          └────────────────────┤ 6. Analisi   │ ←  │ 5. Fine-tune │ ← ┘
             (active learning)  │  errori/AP   │    │  (GPU)       │
                                └──────────────┘    └──────────────┘
```

Il punto cruciale, e la risposta alla domanda che ha originato questo tutorial: **le fasi 1–4 non richiedono alcun addestramento né GPU**. Sono lavoro sui *dati*. L'addestramento (fase 5) è un momento separato e successivo. "Allargare il dataset" significa operare nelle fasi 1–4; **il dataset allargato non modifica il comportamento del modello finché non si ri-esegue la fase 5**.

Il ciclo si chiude (fase 6 → 1) con l'**active learning**: gli errori osservati in produzione indicano quali classi rinforzare, generando una nuova iterazione di raccolta.

---

## 4. Cosa significa "allargare" un dataset

"Allargare" (*dataset expansion / enrichment*) può significare due cose distinte, spesso combinate:

1. **Allargamento del vocabolario** (*label space expansion*): aggiungere **classi nuove** (es. `printer`). Aumenta *cosa* il modello sa distinguere.
2. **Allargamento della copertura** (*sample expansion*): aggiungere **più esempi** di classi già presenti, coprendo più variabilità (angolazioni, luci, sfondi, occlusioni). Aumenta *quanto bene* il modello generalizza su classi che già conosce.

Entrambi si realizzano con quattro **strategie** non mutuamente esclusive, in ordine crescente di automazione:

| Strategia | Cosa aggiunge | Costo umano | Qualità | Sezione |
|---|---|---|---|---|
| **A. Raccolta + annotazione manuale** | dati del proprio dominio | alto | altissima | §5 |
| **B. Auto-labeling** (foundation model) | dati pre-etichettati da correggere | medio | alta (con review) | §6 |
| **C. Riuso di dataset pubblici** | dati già annotati da terzi | basso | variabile | §7 |
| **D. Data augmentation / dati sintetici** | varianti di dati esistenti | quasi nullo | dipende | vedi §7 di `transfer_learning_finetuning_rfdetr.md` |

La strategia matura combina le quattro: **C** per partire in fretta (base ampia), **A** per il proprio dominio (il segnale più prezioso), **B** per accelerare A, **D** per irrobustire e bilanciare le classi rare.

---

## 5. Strategia A — Raccolta propria e annotazione manuale

È la fonte di dati **più preziosa** perché è l'unica che chiude il *domain gap* (la differenza tra la distribuzione di training e quella di deployment). Un modello valutato su foto "facili" ma usato su frame mossi di una webcam fallirà: il dataset deve *assomigliare* al deployment.

### 5.1 Principio di rappresentatività

Il dataset deve campionare la stessa distribuzione dei dati che il modello incontrerà in produzione. In pratica, per Vision Caption:

- **Stessa sorgente**: fotocamera del telefono, non una reflex.
- **Stesso ambiente**: stanze reali, illuminazione domestica (diurna e artificiale).
- **Stesse condizioni degradate**: frame leggermente mossi (il sistema panoramica), sfocature, occlusioni parziali, oggetti troncati dal bordo.
- **Varianza controllata**: ogni oggetto va fotografato da più punti di vista, a più distanze (scale diverse), su più sfondi.

Questo è **campionamento stratificato** applicato ai dati: si vuole coprire deliberatamente le dimensioni di variabilità, non accumulare foto ridondanti della stessa scena.

### 5.2 L'annotazione come atto di definizione

Annotare non è "cerchiare oggetti": è **operazionalizzare una definizione**. Prima di annotare si scrive una **guida di annotazione** (*annotation guidelines*) che per ogni classe stabilisce cos'è e cosa non è. Esempi di decisioni non banali:

- Una stampante multifunzione (stampante + scanner) è `printer`? E se è integrata in un mobile?
- Un oggetto occluso al 70% va annotato o ignorato?
- Il box include l'ombra? I cavi? Il vassoio della carta estratto?

La coerenza di queste scelte si misura con l'**inter-annotator agreement** (accordo tra annotatori diversi sullo stesso dato): se due persone annotano in modo incoerente, il modello riceve un segnale rumoroso. Regola pratica del box: **aderente** all'oggetto (*tight bounding box*), includendo le parti visibili anche se occluse parzialmente.

### 5.3 Strumenti

Editor di annotazione (nessuno richiede GPU): **Roboflow Annotate**, **CVAT**, **Label Studio**, **labelImg**. Producono direttamente (o esportano in) formato COCO. Roboflow in più fa hosting, versioning del dataset, split ed export automatici.

---

## 6. Strategia B — Auto-labeling (distillazione da foundation model)

Annotare a mano è il collo di bottiglia. L'**auto-labeling** lo attenua usando un **modello open-vocabulary** (che rileva oggetti da un prompt testuale, senza essere stato addestrato su quelle classi) per **pre-annotare**, lasciando all'umano solo la **revisione**.

### 6.1 Il principio: distillazione dei dati

Si dà a un *foundation model* (es. **GroundingDINO**, eventualmente con **SAM** per box precisi) l'elenco testuale delle classi come prompt (`"printer . microwave . router"`); il modello restituisce box candidati. Questi diventano annotazioni provvisorie che l'umano **accetta, corregge o rifiuta**. È una forma di **knowledge distillation a livello di dati**: si trasferisce la conoscenza generalista del foundation model dentro il proprio dataset specializzato, che poi addestrerà un modello più piccolo e veloce (RF-DETR).

Framework tipico: **Autodistill** orchestra "modello che etichetta" (*base model*, es. GroundingDINO) → dataset → "modello che si addestra" (*target model*, es. RF-DETR).

### 6.2 Perché serve comunque la revisione umana

I foundation model open-vocabulary sono **generalisti**: sbagliano sul dominio specifico, hanno *bias* di prompt, mancano oggetti piccoli o inusuali. Usare le loro annotazioni **senza verifica** inietta *label noise* sistematico (§9). La regola metodologica è: **auto-label per la velocità, review umana per la qualità**. È anche il punto che rende la procedura *citabile* in tesi (distillazione da foundation model con *human-in-the-loop*).

> Nota: l'auto-labeling è **inferenza**, non training. Gira su GPU per velocità ma non è un fine-tuning; può girare anche in locale o (lentamente) su CPU.

---

## 7. Strategia C — Riuso e fusione di dataset pubblici (Roboflow Universe)

Non serve ricominciare da zero: esistono grandi cataloghi di dataset già annotati.

### 7.1 Le fonti

- **Roboflow Universe** (`universe.roboflow.com`): catalogo con centinaia di migliaia di dataset pubblici, cercabili per classe/dominio, scaricabili **in formato COCO** (o YOLO, VOC…) con un click o via API/SDK. È la fonte più immediata per il tuo caso (cerca "printer", "office objects", "household/indoor objects").
- **Dataset accademici di riferimento**: **COCO** (80 classi), **LVIS** (1200+ classi, distribuzione *long-tail*), **Open Images** (600 classi), **Objects365** (365 classi), e per scene indoor **ADE20K**, **SUN RGB-D**, **ScanNet**.

### 7.2 Sì, puoi scaricarli e fonderli col tuo dataset

È una pratica standard (**dataset pooling / merging**). Concretamente: scarichi un dataset di stampanti in formato COCO e ne unisci `images`, `categories` e `annotations` al tuo. Ma la fusione **non è una semplice concatenazione di file**: richiede di riconciliare i vocabolari e gli identificatori. È il tema della sezione seguente, ed è la parte metodologicamente delicata.

---

## 8. Il problema della fusione: label space e annotazione parziale

Fondere dataset eterogenei introduce due problemi tecnici che, se ignorati, **degradano silenziosamente** il training (le metriche sembrano ok, il modello no).

### 8.1 Riconciliazione degli identificatori e dei nomi (*label space merging*)

Ogni dataset numera le proprie `categories` e `images` a partire da `id: 1`. Unendo due dataset si hanno **collisioni di id**: la `image_id: 1` di entrambi, la `category_id: 1` che nell'uno è `printer` e nell'altro `person`. La fusione corretta richiede di:

1. **Ri-mappare gli id** in modo globale e coerente (rinumerare immagini e annotazioni).
2. **Unificare l'ontologia dei nomi**: `printer` / `Printer` / `stampante` / `laser_printer` devono collassare (o no) su un'unica classe, secondo una scelta *esplicita* di granularità. Sinonimi vanno uniti; distinzioni volute (`printer` vs `3d_printer`) vanno mantenute. Questa è una **decisione di progetto** da giustificare, non un dettaglio tecnico.

Roboflow offre una funzione di *merge* che assiste l'unificazione dei nomi; concettualmente, però, la scelta ontologica resta tua.

### 8.2 Il problema dell'annotazione parziale (*partial / missing annotations*) ⚠️

È l'insidia più grave e meno intuitiva. Un dataset di sole stampanti annota **solo** le stampanti. Se una di quelle immagini contiene *anche* una persona, quella persona **non è annotata**. Durante il training il modello interpreta ogni regione non annotata come **sfondo** (*background / negative*): sta quindi imparando attivamente che "quella persona è NON-persona". Fondendo quel dataset con uno che invece annota le persone, si inviano al modello segnali **contraddittori** sulla stessa apparenza visiva → l'AP della classe `person` peggiora.

Formalmente: la detection assume immagini **esaustivamente annotate** (ogni istanza di ogni classe del vocabolario è etichettata). La fusione di dataset a vocabolario diverso viola questa assunzione. Contromisure (crescenti in complessità):

- **Scegliere dataset a vocabolario compatibile / disgiunto** dove il problema non emerge.
- **Pseudo-labeling**: usare un modello per etichettare le classi mancanti nelle immagini importate, poi verificare (di nuovo *human-in-the-loop*).
- **Training con dataset "federati"** / *loss* che ignora le regioni potenzialmente non annotate (tecniche da *partially-annotated detection*, es. Open Images).

### 8.3 Il rischio a monte: distribuzione e domain shift

Anche a fusione tecnicamente corretta, un dataset pubblico di stampanti (foto da e-commerce, sfondo bianco, ben illuminate) ha una distribuzione **diversa** dal tuo deployment (stanza, luce calda, frame mosso). Aiuta a insegnare "che aspetto ha una stampante" ma **non** chiude il domain gap. Da qui la gerarchia di valore dei dati: **dati pubblici per la quantità, dati propri per l'aderenza al dominio**. Idealmente si combinano.

---

## 9. Qualità del dataset: rumore, bilanciamento, split

Tre proprietà determinano se un dataset produrrà un buon modello, a prescindere dalla dimensione.

### 9.1 Rumore delle etichette (*label noise*)

Box imprecisi, classi sbagliate, oggetti dimenticati. La letteratura mostra che il *label noise* danneggia le prestazioni **più di quanto intuitivamente si creda**, e più dell'aggiunta di altri dati rumorosi. Un passaggio di **review** della qualità è tempo ben speso: **qualità > quantità**.

### 9.2 Sbilanciamento delle classi (*class imbalance / long-tail*)

Le classi nuove hanno tipicamente **pochi** esempi rispetto a quelle COCO ereditate: distribuzione *long-tail*. Un modello addestrato su dati sbilanciati impara bene le classi frequenti e male quelle rare. Rimedi (dettagli in §10 di `transfer_learning_finetuning_rfdetr.md`): **oversampling / repeat-factor sampling** (stile LVIS), **copy-paste augmentation**, **loss weighting**. Diagnosi: si guarda l'**AP per-classe**, non solo la mAP globale.

### 9.3 Split corretti (evitare il *data leakage*)

Il dataset si divide in **train** (per apprendere), **valid** (per regolare il training e fare early stopping) e **test** (per la valutazione finale, mai visto durante il training). Split tipico **70/20/10**, stratificato per classe. La regola critica per dati video:

> **No leakage temporale.** Frame consecutivi dello stesso video/sessione sono quasi identici (fortemente correlati). Se finiscono in split diversi, il test contiene di fatto copie del train → le metriche risultano **gonfiate** e non predicono la performance reale. Regola: **si splitta per sessione/video, non per singolo frame** — tutti i frame di una registrazione stanno nello stesso split.

---

## 10. Quanto deve essere grande? (sufficienza statistica)

Non esiste una soglia universale, ma alcuni principi guida:

- Grazie al **transfer learning** (backbone DINOv2 pre-addestrato), servono **ordini di grandezza meno dati** del training from-scratch: **poche centinaia di istanze per classe** possono bastare per un fine-tuning utile (non migliaia obbligatorie).
- Ciò che conta non è il numero di **immagini** ma il numero di **istanze annotate per classe** e la loro **diversità** (100 istanze varie > 500 quasi identiche).
- **Criterio empirico, non a priori**: si addestra su ciò che si ha, si guarda l'**AP per-classe** e la **matrice di confusione**; le classi deboli indicano *dove* raccogliere altri dati. È esattamente il loop di **active learning** (§3, fase 6). Il dataset "abbastanza grande" è quello oltre il quale aggiungere dati non muove più le metriche (rendimenti decrescenti).

Per il caso Vision Caption: ~100–300 immagini per classe nuova, catturate dal setup reale e integrate con qualche dataset pubblico, sono un punto di partenza ragionevole per la prima iterazione.

---

## 11. Sintesi operativa

1. **Il dataset contiene le classi** (nell'array `categories` del JSON COCO); il modello le impara solo dopo il fine-tuning.
2. **Allargare il dataset = fasi 1–4 del ciclo (ontologia → raccolta → annotazione → split)**: nessuna GPU, nessun addestramento. Il dataset allargato non cambia il modello finché non si ri-esegue il fine-tuning.
3. **Quattro strategie combinabili**: raccolta propria (dominio), auto-labeling (velocità), riuso di dataset pubblici (quantità), augmentation (robustezza).
4. **Roboflow Universe** offre dataset già annotati scaricabili in COCO; **puoi fonderli** col tuo, ma gestendo *label space merging* e soprattutto l'**annotazione parziale** (§8.2), la trappola principale.
5. **Qualità prima della quantità**: controllare *label noise*, bilanciare le classi rare, splittare senza *leakage* temporale.
6. Il dataset è **iterativo**: si parte piccolo, si valuta l'AP per-classe, si allarga dove il modello sbaglia (active learning).

---

## 12. Riferimenti

- **Companion sul training:** [`transfer_learning_finetuning_rfdetr.md`](./transfer_learning_finetuning_rfdetr.md) (§5 pipeline, §7 augmentation, §8 valutazione, §10 approfondimenti).
- **Problema originale:** [`sfide_e_problemi.md`](./sfide_e_problemi.md) #9.
- **Formato COCO:** Lin et al., *Microsoft COCO: Common Objects in Context*, ECCV 2014.
- **Roboflow Universe:** <https://universe.roboflow.com/>
- **Autodistill (auto-labeling):** <https://github.com/autodistill/autodistill>
- **GroundingDINO:** Liu et al., *Grounding DINO: Marrying DINO with Grounded Pre-Training for Open-Set Object Detection*, 2023.
- **LVIS (long-tail):** Gupta et al., *LVIS: A Dataset for Large Vocabulary Instance Segmentation*, CVPR 2019.
- **Data-centric AI:** A. Ng, *MLOps: From Model-centric to Data-centric AI*, 2021.
