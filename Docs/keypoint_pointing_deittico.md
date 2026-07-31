---
title: "Modalità POINTING: MediaPipe Hands come trigger deittico"
tipo: nota-teorica-tesi
tags: [mediapipe-hands, keypoint-detection, pointing, deissi, trigger, rf-detr, tesi]
related: ["[[CaptionPipeline]]", "[[Frame]]", "[[CaptionMode]]", "[[PointingCoordinates]]", "[[Detection]]", "[[SceneDetectorPort]]", "[[RfdetrSceneDetectorAdapter]]", "[[SsimSceneDetectorAdapter]]"]
---

# Modalità POINTING: MediaPipe Hands come trigger deittico

> Nota teorica per la tesi. Le formule sono in blocchi di codice per essere
> **sempre leggibili** in qualsiasi viewer (grafo, GitHub, editor). I collegamenti
> `[[...]]` agganciano la nota ai nodi del knowledge graph del progetto.

**Mappa concettuale:**
[[MediaPipe Hands]] · [[Scheletro della Mano]] · [[Vettore Deittico]] ·
[[Gesture Spotting]] · [[Trigger Gestuale]] · [[Risoluzione del Referente]] ·
[[RF-DETR Keypoint]] · [[CaptionMode]] · [[CaptionPipeline]] · [[Frame]] ·
[[Detection]] · [[RfdetrSceneDetectorAdapter]]

---

## 0. Sintesi dell'architettura

L'attributo inviato dal client nel pacchetto del webstream (`auto` / `pointing`)
**non è una coordinata**: è un **selettore di regime**, mappato su [[CaptionMode]].
Determina *come* il server tratta i frame, non *dove* guardare.

```
REGIME  AUTO      ->  invariato: SSIM (SsimSceneDetectorAdapter) + rate limiter -> VLM
                      il sistema decide da solo QUANDO descrivere

REGIME  POINTING  ->  il sistema resta SILENTE (nessuna descrizione automatica),
                      ma su OGNI frame gira MediaPipe Hands:
                        1. costruisce lo scheletro della mano (21 landmark)
                        2. riconosce se l'indice sta puntando  (gesture spotting)
                        3. calcola la DIREZIONE di puntamento
                        4. risolve le COORDINATE dell'oggetto puntato (via Detection)
                        5. -> TRIGGER: chiama il VLM con quelle coordinate
```

Il regime `POINTING` è un **regime a innesco gestuale**: il gesto deittico
sostituisce SSIM come segnale che fa partire la [[CaptionPipeline]]. Le
[[PointingCoordinates]] cambiano semantica: da *input dal client* a *output
calcolato dal server* (coordinate del referente).

**Scelta dei modelli** — due strumenti specializzati, ciascuno al meglio nel suo
compito:

```
MediaPipe Hands   ->  scheletro della mano -> vettore di puntamento  (il GESTO)
RF-DETR detection ->  oggetti della scena -> candidati referente      (il COSA)
```

---

## 1. Perché MediaPipe Hands (motivazione della scelta)
[[MediaPipe Hands]]

La domanda progettuale era: come ricavare lo **scheletro della mano** e la
**direzione dell'indice**? Tre opzioni valutate:

| Approccio | Scheletro mano | Real-time | Maturità | Costo per noi |
|---|---|---|---|---|
| **OpenCV puro** (skin + convex hull) | grezzo, fragile | sì | vecchio | fragile a luce/sfondo |
| **MediaPipe Hands** | 21 landmark, 2.5D | sì, su CPU | standard de-facto | **zero training** |
| **RF-DETR Keypoint** | da fine-tunare (default = corpo) | sì | preview | dataset + addestramento |

Nota terminologica: molti tutorial "hand tracking con OpenCV" usano in realtà
**MediaPipe** sotto, con OpenCV solo per acquisire e disegnare. OpenCV *puro*
(segmentazione pelle + convexity defects) è l'approccio storico, fragile.

**MediaPipe Hands** è la scelta primaria perché:

- **21 landmark pronti** — nessun addestramento; scheletro completo della mano.
- **2.5D** — ogni landmark ha `(x, y, z)` con `z` = profondità relativa al polso →
  direzione di puntamento più informativa del solo 2D.
- **Real-time su CPU** — latenza bassissima, adatto all'edge e ai timeout stretti
  del sistema (`VLM_TIMEOUT_S`, `MAX_FRAME_AGE_S` nella [[CaptionPipeline]]).
- **Maturo e documentato** — è il motivo per cui "lo fanno tutti così".
- **Apache 2.0**, deploy on-device.

Limiti (onesti): non fornisce ellissi di incertezza calibrate; è un modello a sé,
non unificato con lo stack RF-DETR. Entrambi i limiti sono accettabili per l'MVP e
tematizzabili come lavoro futuro (§9).

### Topologia dei 21 landmark

```
0  = polso (wrist)
1-4   pollice     (1=CMC, 2=MCP, 3=IP, 4=punta)
5-8   indice      (5=MCP, 6=PIP, 7=DIP, 8=punta)      <-- rilevanti per il puntamento
9-12  medio
13-16 anulare
17-20 mignolo
```

---

## 2. Fondamenti di keypoint detection (inquadramento teorico)
[[Scheletro della Mano]]

### 2.1 Definizione formale

Data un'immagine `I` (H x W x 3) e `K` keypoint semanticamente definiti, la stima
della posa è:

```
f_theta : I  ->  { (x_k, y_k, z_k, v_k) }   per k = 1..K

  (x_k, y_k)  posizione nel piano immagine (normalizzata in MediaPipe)
  z_k         profondità relativa al polso (2.5D)
  v_k         presenza / visibilità del landmark
```

La difficoltà non è classificare ma **localizzare sub-pixel entità prive di
apparenza propria**: una "nocca" non è un oggetto, è una relazione anatomica
inferita dal contesto strutturale.

### 2.2 Come lavora MediaPipe Hands (pipeline a due stadi)

MediaPipe adotta una pipeline **detector → landmark**:

```
1. Palm Detector      -> individua e ritaglia la mano (bounding box orientato)
2. Hand Landmark Model-> sul crip predice i 21 landmark (regressione diretta 2.5D)
   + smoothing/tracking temporale tra frame (riusa il box precedente)
```

È di fatto un approccio **top-down** (prima la mano, poi i keypoint), leggero e
ottimizzato per il tracking video. Per contesto teorico, i paradigmi alternativi:

- **Heatmap regression** (HRNet, Hourglass): una mappa gaussiana per keypoint, poi
  arg-max. Massima accuratezza, ma costo di decodifica e quantizzazione.

  ```
  H_k(p) = exp( - || p - p_k* ||^2 / (2 * sigma^2) )
  (x_k, y_k) = argmax_p  H_k(p)
  ```

- **Bottom-up + Part Affinity Fields** (OpenPose): tutti i keypoint + grouping via
  campi di affinità. Robusto in folla, meno accurato sul singolo.
- **Set-prediction alla DETR** (RF-DETR Keypoint, §9): keypoint per-oggetto in un
  forward pass, con incertezza calibrata.

MediaPipe sceglie la **regressione diretta su crop tracciato**: trade-off ottimale
per il nostro scenario (una mano, vicina, video real-time).

### 2.3 Perché la mano e non il braccio

La posa **corporea** (17 keypoint COCO) dà il macro-vettore del braccio ma **non**
la punta del dito. Gli umani puntano *con il dito*: serve il vettore fine
*MCP-indice → punta-indice*. La letteratura sul *pointing gesture recognition*
mostra inoltre che la retta **occhio–punta del dito** approssima l'intenzione
meglio dell'avambraccio (puntamento "allineato allo sguardo", non balistico).

---

## 3. Gesture spotting: distinguere il puntamento
[[Gesture Spotting]]

Non ogni mano visibile è un puntamento. Serve un piccolo classificatore geometrico
sui 21 landmark che riconosca la posa "indice esteso, altre dita chiuse":

```
indice esteso   : distanza(punta_8, polso_0) grande  AND  dita (8,7,6,5) ~collineari
altre chiuse    : punta_medio(12), punta_anulare(16), punta_mignolo(20) vicine al palmo
```

Robustezza tramite **dwell-time**: il gesto deve restare stabile per N frame
consecutivi prima di innescare. Sfrutta la natura streaming del sistema ed evita
falsi trigger, sostituendo di fatto il ruolo di "cambiamento significativo" che in
`AUTO` ha SSIM.

---

## 4. Dallo scheletro al vettore deittico
[[Vettore Deittico]]

Il puntamento è **geometria proiettiva**. La retta nel piano immagine da due
landmark dell'indice, es. MCP (5) e punta (8):

```
retta(t) = p5 + t * (p8 - p5),    t >= 0
direzione:  d = p8 - p5
```

Il `z` di MediaPipe permette una **direzione pseudo-3D** più fedele:

```
d_2.5D = (x8 - x5,  y8 - y5,  z8 - z5)
```

**Cono di incertezza** — a differenza di RF-DETR Keypoint, MediaPipe non dà una
covarianza calibrata. Il cono si modella empiricamente: un semi-angolo `theta`
fisso o funzione della confidenza del landmark, tarato sui dati.

**Pointing error** (errore angolare) e propagazione a distanza `D`:

```
eps = arccos( (d_hat . d_star) / (|d_hat| * |d_star|) )
errore_trasversale_sul_referente  ~=  D * tan(eps)
```

Ecco perché il puntamento è un **cono**, non un raggio.

---

## 5. Dalla direzione alle coordinate del referente
[[Risoluzione del Referente]] · [[Trigger Gestuale]]

Il trigger non è "c'è una mano" ma "**c'è un puntamento verso *questo* punto**". Il
raggio, con il suo cono, seleziona il referente tra i candidati — le [[Detection]]
prodotte da [[RfdetrSceneDetectorAdapter]] sulla scena — in modo probabilistico:

```
P(obj_i | gesto)  ∝  exp( -alpha * phi_i ) * g(d_i) * h(c_i)

  phi_i  distanza angolare tra raggio e centroide di obj_i (pesata dal cono)
  d_i    distanza lungo il raggio (prior "nearest-along-ray")
  c_i    confidenza della Detection
  alpha  sensibilita' angolare

referente = argmax_i P(obj_i | gesto)   (con soglia di rifiuto = "nessun oggetto")
```

Le **coordinate del referente** (centroide del box, o punto raggio-oggetto) sono il
contenuto del trigger passato al VLM. Modalità di condizionamento, dalla più
semplice alla più ricca:

```
(a) prompt testuale:  "descrivi l'oggetto in posizione (x, y): {class_name}"
(b) crop / ROI:       ritaglio attorno al referente passato come immagine al VLM
(c) marcatura visiva: marker sul referente + frame intero al VLM
```

Serve quindi, in regime POINTING, far girare **MediaPipe (mano) + RF-DETR
detection (oggetti scena)** sullo stesso frame. Se basta il punto proiettato senza
classificare il referente, si passa direttamente la coordinata come ROI.

---

## 6. Integrazione architetturale (disegno, non codice)

Architettura esagonale già presente → estensione pulita:

- **Dominio [[Frame]]** — mantiene [[CaptionMode]] (`AUTO`/`POINTING`). Le
  [[PointingCoordinates]] diventano *output del server* (referente risolto), non
  input del client. In `POINTING` il client invia solo il flag di modalità.
- **Nuovo adapter** dietro una porta dedicata (es. `PointingResolverPort`,
  simmetrica a [[SceneDetectorPort]]): incapsula MediaPipe Hands + gesture spotting
  + geometria del raggio + risoluzione del referente contro le [[Detection]]. Il
  core resta agnostico al modello concreto (MediaPipe oggi, RF-DETR Keypoint domani).
- **[[CaptionPipeline]]**, ramo `POINTING` — gira MediaPipe su ogni frame, applica
  gesture spotting + dwell-time, e **solo al gesto valido** innesca il VLM con le
  coordinate del referente. Niente più bypass che descrive l'intera scena.
- **Pipeline TTS invariata**: cambia *cosa* si descrive, non *come*.

---

## 7. Real-time, edge e trade-off

- MediaPipe Hands gira su **CPU** con latenza minima → margine ampio rispetto ai
  timeout della pipeline.
- **Cadenza asimmetrica** possibile: MediaPipe tracka già in modo efficiente tra
  frame (riusa il box precedente), quindi il costo per-frame è basso.
- RF-DETR detection per gli oggetti è il collo di bottiglia più pesante: valutare
  se farlo girare a ogni frame o solo all'atto del trigger.

---

## 8. Valutazione (capitolo sperimentale)

**Metriche di keypoint**

```
PCK    keypoint corretto se ||p_pred - p_gt|| <= tau * scala_mano
OKS    Object Keypoint Similarity (COCO-style)
```

**Metriche di puntamento** (il contributo originale della tesi)

```
- errore angolare medio del raggio deittico
- accuratezza di selezione del referente = (# gesti con oggetto corretto)/(# gesti)
- latenza gesto -> caption
- tasso di falsi trigger (gesti spuri interpretati come puntamento)
```

Dataset ideale: piccolo corpus **egocentrico** «gesto mano + oggetto target»,
legato a `Docs/costruzione_dataset_object_detection.md`.

---

## 9. Estensione di ricerca: RF-DETR Keypoint (lavoro futuro / confronto)
[[RF-DETR Keypoint]]

MediaPipe risolve l'MVP, ma **nessuno** in letteratura/community fa hand-pointing
con **RF-DETR Keypoint** — il che lo rende un ottimo **contributo originale** come
estensione comparativa, non come percorso critico. RF-DETR Keypoint (Roboflow,
preview 2026):

- Keypoint per-oggetto in **singolo forward pass** (no NMS, no heatmap, no grouping).
- **Ellisse di incertezza** per keypoint (covarianza 2D calibrata) → cono di
  puntamento *derivato dal modello*, non tarato a mano.
- **Scheletro arbitrario**: fine-tunabile sulla mano (21 kp) su qualsiasi classe.
- **Unifica lo stack** con [[RfdetrSceneDetectorAdapter]] e il workflow
  `Docs/transfer_learning_finetuning_rfdetr.md`.

Costo: richiede aggiornare il pacchetto `rfdetr` (l'1.6.5 installato espone solo
detection + segmentation) e **fine-tuning su dataset di mani**. Piano di tesi:
implementare l'MVP con MediaPipe, poi confrontare MediaPipe vs RF-DETR Keypoint su
latenza, accuratezza dello scheletro e calibrazione dell'incertezza.

---

## 10. Cosa manca operativamente

```
[ ] adapter MediaPipe Hands dietro PointingResolverPort
[ ] gesture spotting "indice esteso" + dwell-time
[ ] geometria raggio (2.5D) + risoluzione referente contro le Detection
[ ] ramo POINTING della CaptionPipeline: trigger su gesto + VLM condizionato su coord
[ ] Frame: PointingCoordinates come output server (referente risolto)
[ ] dataset egocentrico gesto->oggetto per la valutazione
[ ] (estensione) fine-tuning RF-DETR Keypoint su scheletro mano + confronto
```

---

## 11. Sfide aperte e limiti onesti

1. **Ambiguità in monoculare** — puntamento lungo l'asse ottico mal definito;
   oggetti collineari irrisolvibili in 2D (il `z` di MediaPipe mitiga in parte).
2. **Gap intenzione–geometria** — si punta "verso" più che "esattamente a"; la
   retta anatomica non coincide con l'intenzione (calibrazione del cono).
3. **Incertezza non calibrata** in MediaPipe — il cono è empirico (a differenza di
   RF-DETR Keypoint); tematizzabile nel confronto.
4. **Egocentrismo** — camera indossata vs camera che osserva l'utente: geometria
   diversa, da motivare.
5. **Trigger vs continuità** — coordinare gesto-innesco e cascata SSIM/rate-limiter
   senza conflitto tra regimi è un problema di *policy*.

---

## Sintesi

```
client invia flag di modalita' (auto/pointing) nel webstream
   |
   +-- AUTO      -> invariato: SSIM + rate limiter -> VLM (descrive la scena)
   |
   +-- POINTING  -> MediaPipe Hands su ogni frame
                       -> scheletro mano (21 kp) -> indice punta? (gesture spotting)
                          -> direzione 2.5D + cono empirico
                             -> risoluzione referente contro le Detection RF-DETR
                                -> coordinate oggetto puntato
                                   -> TRIGGER: VLM condizionato su quelle coord
```

Baricentro: **MediaPipe Hands come rilevatore del gesto deittico e generatore delle
coordinate del referente**; RF-DETR detection per i candidati; RF-DETR Keypoint
come estensione comparativa di ricerca. Materiale da capitolo di tesi: teoria
(deissi + keypoint detection + geometria proiettiva) e sperimentazione (metriche di
puntamento + confronto MediaPipe vs RF-DETR Keypoint).
