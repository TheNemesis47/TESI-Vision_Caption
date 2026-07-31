---
title: "Piano di integrazione Hand Tracking per la modalità POINTING"
tipo: working-plan
stato: MVP-implementato
data: 2026-07-28
tags: [hand-tracking, mediapipe, pointing, ports-and-adapters, testing, tesi]
related:
  - "[[CaptionPipeline]]"
  - "[[CaptionMode]]"
  - "[[Frame]]"
  - "[[MediaPipe Hands]]"
  - "[[PointingEvent]]"
  - "[[OpenRouterCaptionGenerator]]"
---

# Piano di integrazione Hand Tracking per la modalità POINTING

> Stato al 2026-07-28: fasi 1–7 implementate e coperte da unit test. La fase 8
> resta la fase di collaudo con sequenze reali, taratura sul dispositivo e
> futura valutazione dell'integrazione RF-DETR.

## 1. Obiettivo

Integrare nel progetto `visionCaption-TESI` il comportamento sperimentato nel
prototipo `handTracking/main.py`, senza trasferire il prototipo come singolo file
e rispettando l'architettura Ports & Adapters.

Il risultato deve rispettare queste regole:

- la modalità `AUTO` mantiene il comportamento attuale;
- MediaPipe viene inizializzato e chiamato soltanto durante una sessione
  `POINTING`;
- un frame `POINTING` non attiva automaticamente il VLM;
- il VLM viene chiamato soltanto quando la gesture è stata riconosciuta e
  confermata;
- mantenere la posa non produce richieste VLM ripetute;
- lo stato temporale del gesto appartiene alla singola connessione WebSocket;
- i tipi MediaPipe, OpenCV e HTTP non entrano nel core;
- la risposta strutturata del VLM viene validata prima di arrivare al TTS.

## 2. Decisione per l'MVP

Il prototipo e la nota teorica descrivono due strategie diverse.

Il prototipo implementa:

```text
MediaPipe -> gesture -> raggio/corridoio -> tre immagini -> VLM
```

La nota teorica `keypoint_pointing_deittico.md` propone:

```text
MediaPipe -> gesture -> raggio -> RF-DETR -> referente -> VLM
```

Per la prima integrazione la sorgente di verità è il comportamento realmente
implementato e provato nel prototipo: selezione del bersaglio mediante corridoio
e VLM multimodale. L'intersezione con le detection RF-DETR è una seconda
iterazione, successiva al funzionamento dell'MVP.

## 3. Flusso runtime target

```text
Frame ricevuto dal WebSocket
        |
        v
  selezione CaptionMode
        |
        +-- AUTO
        |     |
        |     +--> flusso attuale:
        |          scene detector -> rate limiter -> VLM AUTO -> TTS
        |
        +-- POINTING
              |
              +--> inizializzazione lazy della sessione MediaPipe
              +--> stima dei landmark della mano
              +--> riconoscimento e stabilizzazione della gesture
              |
              +-- gesto non confermato --> nessun VLM e nessun TTS
              |
              +-- evento confermato
                    |
                    +--> calcolo raggio e corridoio
                    +--> context + focus + clean
                    +--> VLM POINTING
                    +--> validazione della risposta
                    +--> composizione della caption accessibile
                    +--> TTS
```

## 4. Suddivisione architetturale proposta

```text
core/
├── domain/
│   ├── hand_pose.py
│   ├── pointing.py
│   └── pointing_caption.py
├── ports/
│   ├── hand_pose_estimator_port.py
│   ├── pointing_image_preparer_port.py
│   └── pointing_caption_generator_port.py
└── services/
    ├── auto_caption_pipeline.py
    ├── caption_pipeline.py
    └── pointing/
        ├── gesture_recognizer.py
        ├── pointing_geometry.py
        ├── pointing_event_gate.py
        └── pointing_pipeline.py

adapters/
├── hand_tracking/
│   └── mediapipe_hand_pose_estimator.py
├── pointing/
│   └── opencv_pointing_image_preparer.py
└── vlm/
    └── openrouter_pointing_caption_generator.py

infrastructure/
├── settings/
│   └── pointing_settings.py
└── server/
    ├── app.py
    ├── ws_handler.py
    └── caption_session.py
```

I nomi sono indicativi. Il vincolo importante è mantenere separate:

- logica geometrica e temporale;
- inferenza MediaPipe;
- trasformazioni OpenCV;
- trasporto e formato OpenRouter;
- ciclo di vita della connessione WebSocket.

## 5. Mappatura delle responsabilità del prototipo

| Parte di `handTracking/main.py` | Destinazione | Decisione |
|---|---|---|
| `FingerAngles`, `PointingVector`, `PointingRay`, `PointingEvent` | Domain pointing | Trasferire senza tipi MediaPipe/OpenCV |
| EMA, angoli 3D, rapporto pollice/palmo, vettore e proiezione | Servizio di geometria | Rendere logica pura e testabile |
| `PointingGestureTracker` | Gesture recognizer | Mantenere latch, conferma e rilascio |
| `PointingEventGate` | Event gate | Stato e cooldown per sessione |
| Creazione `HandLandmarker` ed estrazione landmark | Adapter MediaPipe | Incapsulare completamente MediaPipe |
| Corridoio, context, focus, clean e JPEG | Adapter OpenCV | Eseguire solo all'attivazione |
| Prompt, payload, HTTP e parsing JSON pointing | Adapter VLM pointing | Separare dal generatore AUTO |
| `process_hands` | Pointing pipeline | Scomporre in orchestrazione |
| Camera, orientamento, preview, FPS e `imshow` | Non trasferire | Il frame arriva dal WebSocket |
| `VLMDispatcher` | Non trasferire | Il server possiede già un flusso asincrono |
| Overlay realtime | Opzionale | Sostituire con stato WebSocket o debug artifact |

## 6. Working plan

### Fase 0 — Congelare e caratterizzare il comportamento AUTO

#### Obiettivo

Creare una rete di sicurezza prima di estrarre o modificare
`CaptionPipeline`. "AUTO rimane uguale" deve essere dimostrabile tramite test,
non affidato al confronto manuale.

#### Situazione rilevata il 2026-07-28

- non esiste ancora una suite di unit test della pipeline;
- `src/vision_caption/tests/` contiene soltanto `__init__.py`;
- `pytest` non è installato nell'ambiente del progetto;
- il comando di raccolta dei test termina con `No module named pytest`;
- `MockCaptionGenerator.generate()` è una coroutine che restituisce una stringa,
  mentre la pipeline lo consuma come async generator;
- la pipeline, il rate limiter, il scene detector e `_last_caption` sono
  assemblati come stato condiviso dell'applicazione, non per connessione;
- il client di test attende audio binario, ma il server risponde con messaggi
  WebSocket JSON;
- il ramo POINTING attuale invoca VLM e TTS senza alcun trigger gestuale.

Questi punti non devono essere tutti "congelati" come requisiti: alcuni sono
bug o debito tecnico. La Fase 0 deve prima classificarli in:

- comportamento AUTO da preservare;
- bug da correggere prima del refactoring;
- policy ambigua da decidere e poi testare.

#### Attività

- predisporre un ambiente test riproducibile;
- aggiungere `pytest` e il supporto necessario ai test asincroni;
- creare fake conformi ai tre port attuali;
- caratterizzare il percorso senza cambio scena;
- caratterizzare il blocco del rate limiter;
- caratterizzare il percorso con cambio scena;
- verificare la callback delle detection;
- verificare `commit()` del scene detector;
- caratterizzare lo streaming dei chunk VLM;
- verificare la deduplicazione delle caption;
- verificare le freshness guard pre-VLM, pre-TTS e post-TTS;
- verificare il timeout del VLM;
- verificare la chiusura dell'async generator;
- registrare separatamente i difetti già presenti, senza trasformarli per errore
  in comportamento desiderato.

#### Fatto quando

- i test AUTO sono eseguibili senza GPU, rete, OpenRouter o servizio TTS;
- ogni ramo di uscita principale della pipeline ha almeno un test;
- è documentato quali comportamenti sono requisiti e quali sono bug correnti;
- i test passano prima di iniziare il refactoring;
- gli stessi test passano dopo l'estrazione di `AutoCaptionPipeline`.

### Fase 1 — Modellare il dominio POINTING

#### Obiettivo

Rappresentare mano, geometria ed evento senza dipendere dalle librerie esterne.

#### Concetti da introdurre

- landmark normalizzato 2D/3D;
- osservazione della mano;
- angoli delle dita;
- punto normalizzato;
- vettore di puntamento;
- raggio di puntamento;
- stato della gesture;
- evento di puntamento;
- risposta strutturata del VLM pointing;
- caption accessibile finale.

`PointingCoordinates(x, y)` non è sufficiente a descrivere la direzione. Il
nuovo contratto deve conservare almeno origine e fine del raggio. Il risultato
non deve essere scritto dentro il `Frame` frozen: deve viaggiare in un
`PointingEvent` separato, correlato tramite `frame_id`.

#### Fatto quando

- tutti i modelli possono essere istanziati senza MediaPipe, OpenCV o NumPy;
- origine e fine del raggio hanno una convenzione normalizzata documentata;
- la risposta VLM pointing ha uno schema validabile;
- il core non contiene tipi provenienti dagli adapter.

### Fase 2 — Estrarre geometria e riconoscimento

#### Obiettivo

Trasferire nel core la parte deterministica del prototipo.

#### Attività

- calcolo degli angoli PIP e DIP;
- misura dell'estensione del dito;
- rapporto normalizzato pollice/palmo;
- classificazione della posa;
- isteresi tra attivazione e mantenimento;
- smoothing EMA;
- calcolo del vettore indice;
- proiezione del vettore al bordo;
- conferma temporale;
- latch dell'evento;
- rilascio e riarmo;
- cooldown fra due eventi.

Nel server la frequenza dei frame non è costante e il WebSocket può scartare
frame arretrati. Conferma e rilascio dovrebbero quindi essere espressi in tempo
monotono, oppure almeno affiancati da soglie temporali, invece di dipendere solo
dal numero di frame.

#### Fatto quando

- la geometria è testata senza immagini reali;
- una posa stabile produce un solo evento;
- una posa mantenuta non genera altri eventi;
- rilascio e nuovo gesto producono un nuovo evento;
- FPS differenti non cambiano drasticamente il tempo percepito di attivazione.

### Fase 3 — Implementare l'adapter MediaPipe

#### Obiettivo

Tradurre un `Frame` JPEG in osservazioni di dominio.

#### Responsabilità dell'adapter

- decodifica JPEG;
- resize esclusivamente per l'inferenza;
- conversione BGR/RGB;
- inizializzazione di `HandLandmarker`;
- timestamp video strettamente crescenti;
- invocazione di MediaPipe;
- conversione dei risultati in tipi di dominio;
- chiusura del landmarker.

Il modello `hand_landmarker.task` deve avere un percorso configurabile, per
esempio sotto `models/hand_tracking/`, e non essere cercato accanto al sorgente.

#### Fatto quando

- una fixture con mano produce 21 landmark;
- una fixture senza mano produce un risultato vuoto;
- l'adapter può essere sostituito con un fake;
- l'uso dell'adapter dopo `close()` è gestito esplicitamente;
- nessun import MediaPipe è presente nel core.

### Fase 4 — Preparare le immagini per il VLM pointing

#### Obiettivo

Produrre gli stessi tre input visivi del prototipo:

- contesto completo annotato;
- focus sul corridoio;
- frame pulito per OCR.

#### Attività

- costruzione del poligono di tolleranza;
- clipping ai bordi;
- guide visive leggere;
- oscuramento dell'esterno;
- crop con padding;
- codifica JPEG;
- configurazione della qualità;
- salvataggio diagnostico opzionale.

Le larghezze del corridoio non devono restare pixel fissi calibrati sulla
risoluzione del prototipo. Devono essere normalizzate o scalate rispetto alle
dimensioni del frame ricevuto.

#### Fatto quando

- i tre JPEG sono validi e decodificabili;
- il frame pulito non contiene guide;
- il focus comprende il corridoio senza uscire dai bordi;
- lo stesso raggio produce risultati coerenti a risoluzioni diverse.

### Fase 5 — Creare il generatore VLM POINTING

#### Obiettivo

Separare il caso d'uso pointing dal generatore testuale in streaming di AUTO.

#### Attività

- costruire il prompt deittico;
- includere coordinate normalizzate e handedness;
- inviare context, focus e clean;
- richiedere JSON strutturato;
- validare la risposta;
- comporre `description` e `visible_text`;
- gestire risposta non valida e filtri di sicurezza;
- produrre una singola caption parlabile.

Il JSON non deve essere inviato a pezzi al TTS. La risposta POINTING deve essere
completa e validata prima della sintesi.

#### Fatto quando

- l'adapter AUTO non è stato modificato nel suo comportamento;
- il pointing usa tre immagini e il prompt dedicato;
- una risposta non valida non viene letta dal TTS;
- `visible_text` viene preservato senza parafrasi;
- la caption finale è testo semplice.

### Fase 6 — Creare la pipeline POINTING e il router di modalità

#### Obiettivo

Fare di `CaptionPipeline` un router sottile.

#### Flusso POINTING

1. stimare la mano;
2. aggiornare il gesture recognizer;
3. terminare senza output se manca l'attivazione;
4. applicare il cooldown;
5. produrre il `PointingEvent`;
6. preparare le tre immagini;
7. chiamare il VLM pointing;
8. validare e comporre la caption;
9. chiamare il TTS una sola volta;
10. produrre un solo `CaptionResult`.

#### Regola di routing

```text
AUTO     -> AutoCaptionPipeline
POINTING -> PointingCaptionPipeline
```

Il ramo POINTING attuale deve essere sostituito: oggi chiama il generatore
generico immediatamente per ogni frame e non aspetta una gesture.

#### Fatto quando

- cento frame AUTO producono zero chiamate al port di hand pose;
- un frame POINTING senza gesture produce zero chiamate VLM/TTS;
- una gesture produce una sola caption;
- l'AUTO continua a superare i test della Fase 0.

### Fase 7 — Gestire dependency injection e ciclo di vita

#### Obiettivo

Assicurare che lo stato temporale non venga condiviso tra client.

#### Stato per connessione

- tracker della gesture;
- event gate;
- ultimo timestamp MediaPipe;
- stato candidato/attivo;
- eventuale landmarker video;
- modalità precedente della sessione.

#### Comportamento

- inizializzare MediaPipe in modo lazy al primo frame `POINTING`;
- non caricarlo se la connessione resta in `AUTO`;
- resettare lo stato quando si passa da `POINTING` ad `AUTO`;
- chiudere le risorse nel `finally` del WebSocket;
- non condividere un `HandLandmarker` in modalità VIDEO tra stream diversi;
- condividere soltanto dipendenze realmente stateless o thread-safe.

#### Fatto quando

- due connessioni non condividono latch, cooldown o timestamp;
- la disconnessione chiude le risorse;
- l'avvio in AUTO non crea il landmarker;
- il cambio modalità non lascia una gesture bloccata nello stato attivo.

### Fase 8 — Test end-to-end, taratura e seconda iterazione RF-DETR

#### Test end-to-end

- sequenza preregistrata di frame via WebSocket;
- fake VLM e TTS;
- assenza di risposta prima del gesto;
- una sola risposta per gesto;
- correlazione tramite `frame_id`;
- reset al cambio modalità;
- disconnessione durante inferenza;
- gestione del backlog.

#### Taratura

- latenza frame -> gesture;
- latenza gesture -> caption;
- falsi trigger;
- gesture mancate;
- errore angolare;
- influenza di FPS e risoluzione;
- larghezza del corridoio;
- soglie geometriche e temporali.

#### Seconda iterazione

Solo dopo l'MVP introdurre un `ObjectDetectorPort` specifico per ottenere
detection senza la policy SSIM/keyframe di AUTO:

```text
raggio MediaPipe
    + detection RF-DETR
    -> ranking delle bounding box
    -> referente selezionato
    -> crop o marker più preciso
    -> VLM
```

`SceneDetectorPort` non è il contratto adatto per questo compito perché contiene
responsabilità specifiche del regime AUTO.

#### Fatto quando

- l'MVP è misurato su sequenze ripetibili;
- le soglie hanno una motivazione sperimentale;
- AUTO e POINTING funzionano nello stesso server senza interferenze;
- l'eventuale uso di RF-DETR è confrontabile con il solo corridoio VLM.

## 7. Matrice minima dei test

| Scenario | Scene detector | Hand tracking | VLM | TTS | Output |
|---|---:|---:|---:|---:|---|
| AUTO, scena invariata | 1 | 0 | 0 | 0 | nessuno |
| AUTO, rate limited | 1 | 0 | 0 | 0 | nessuno |
| AUTO, cambio valido | 1 + commit | 0 | 1 | uno per chunk valido | audio |
| POINTING, nessuna mano | 0 | 1 | 0 | 0 | nessuno |
| POINTING, posa non stabile | 0 | 1 | 0 | 0 | nessuno |
| POINTING, attivazione | 0 | 1 | 1 | 1 | una caption |
| POINTING, posa mantenuta | 0 | 1 | 0 nuove | 0 nuove | nessuno |
| POINTING, nuovo gesto dopo rilascio | 0 | 1 | 1 | 1 | una caption |

## 8. Rischi tecnici da monitorare

- MediaPipe è sincrono e può bloccare l'event loop;
- `RunningMode.VIDEO` richiede timestamp ordinati e stato per stream;
- il drain del WebSocket rende variabile il numero di frame elaborati;
- immagine MediaPipe e immagine VLM devono avere lo stesso orientamento;
- handedness e mirroring devono seguire una convenzione unica;
- i valori in pixel del prototipo non sono portabili direttamente;
- lo streaming testuale AUTO non è compatibile con il JSON pointing;
- i fake devono rispettare davvero i contratti asincroni dei port;
- il debug su filesystem non deve diventare una dipendenza del core;
- i grafi Graphify devono essere aggiornati dopo l'aggiunta dei nuovi moduli.

## 9. Ordine pratico di implementazione

```text
Fase 0: test di caratterizzazione AUTO
    -> Fase 1: dominio POINTING
    -> Fase 2: geometria e gesture
    -> Fase 3: adapter MediaPipe
    -> Fase 4: immagini del corridoio
    -> Fase 5: VLM POINTING
    -> Fase 6: pipeline e router
    -> Fase 7: lifecycle WebSocket
    -> Fase 8: E2E, taratura e RF-DETR opzionale
```
