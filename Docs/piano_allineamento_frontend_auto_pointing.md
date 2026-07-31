---
title: "Piano frontend per modalità AUTO e POINTING"
tipo: working-plan
stato: da-implementare-nel-repository-frontend
data: 2026-07-28
tags: [frontend, websocket, auto, pointing, accessibility, testing]
backend_contract:
  endpoint: "/ws/vision"
  source: "src/vision_caption/infrastructure/server/ws_handler.py"
---

# Piano frontend per modalità AUTO e POINTING

## 1. Obiettivo per l'agente frontend

Allineare il client al protocollo WebSocket attuale e introdurre uno switch
accessibile che selezioni la modalità di caption.

La modalità selezionata deve essere inserita in **ogni pacchetto contenente un
frame**, usando esattamente uno dei valori:

- `AUTO`
- `POINTING`

Lo switch non deve inviare un comando WebSocket separato. Aggiorna lo stato
locale e, dal frame successivo, il campo `caption_mode` di tutti i pacchetti.

## 2. Prima attività obbligatoria: audit del frontend

Prima di modificare il codice, individuare:

1. il componente che apre il WebSocket;
2. la funzione che acquisisce o riceve i frame della camera;
3. la funzione che converte il JPEG in Base64;
4. il punto esatto in cui viene costruito il payload JSON;
5. il listener dei messaggi WebSocket;
6. il servizio o componente che riproduce l'audio;
7. l'eventuale coda audio;
8. lo stato globale o hook che rappresenta la sessione di cattura;
9. i test esistenti per camera, WebSocket e audio;
10. il modo in cui il progetto gestisce accessibilità e traduzioni.

L'agente deve documentare nel proprio handoff i file individuati e adattare i
nomi proposti in questo piano allo stack reale. Non deve creare un secondo
WebSocket o un secondo ciclo di cattura se ne esiste già uno.

## 3. Contratto WebSocket attuale

### 3.1 Endpoint

```text
ws://HOST:8765/ws/vision
wss://HOST:8765/ws/vision
```

Usare `wss` quando la pagina frontend è servita tramite HTTPS.

### 3.2 Pacchetto inviato dal frontend

Ogni frame deve essere un messaggio JSON con questa forma:

```json
{
  "image": "<JPEG codificato in Base64, senza data URL prefix>",
  "frame_id": 123,
  "caption_mode": "AUTO",
  "pointing_coordinates": null
}
```

Regole:

- `image` contiene solamente la stringa Base64. Non usare
  `data:image/jpeg;base64,` come prefisso;
- `frame_id` è un intero monotono crescente nella sessione;
- `caption_mode` è obbligatorio e case-sensitive;
- `pointing_coordinates` non viene usato dal nuovo POINTING: può essere
  mantenuto a `null` per compatibilità oppure omesso;
- il frame deve essere JPEG;
- il valore dello switch deve essere letto al momento della costruzione di
  ciascun pacchetto, non catturato una sola volta all'avvio dello stream.

Il frontend non deve calcolare landmark, direzione, raggio o coordinate del
dito. Tutta questa elaborazione appartiene al backend.

### 3.3 Messaggio audio ricevuto

Il backend non invia audio binario puro. Invia JSON:

```json
{
  "type": "audio",
  "frame_id": 123,
  "caption": "Descrizione da pronunciare.",
  "audio": "<audio in Base64>",
  "duration": 1.42,
  "format": "mp3"
}
```

`format` può essere:

- `wav`
- `mp3`
- `opus`

Il frontend deve:

1. fare il parse del JSON;
2. validare `type`;
3. decodificare `audio`;
4. costruire il MIME type dal campo `format`;
5. mettere l'audio nella coda di riproduzione;
6. mostrare o rendere disponibile `caption` come testo accessibile;
7. revocare gli eventuali object URL dopo l'uso.

Non assumere che tutti i messaggi audio appartengano a frame diversi: AUTO può
produrre più chunk audio con lo stesso `frame_id`. Il filtro di ordinamento deve
scartare frame con ID **minore**, non quelli con ID uguale all'ultimo ascoltato.

### 3.4 Messaggio detection ricevuto

In modalità AUTO il backend può inviare:

```json
{
  "type": "detections",
  "frame_id": 123,
  "detections": [
    {
      "class_name": "person",
      "confidence": 0.91,
      "bbox": {
        "x_min": 10,
        "y_min": 20,
        "x_max": 200,
        "y_max": 300
      }
    }
  ]
}
```

Le detection sono un messaggio distinto dall'audio. Il listener deve effettuare
dispatch in base a `type`. In POINTING non sono necessarie: quando si passa a
POINTING, eventuali overlay AUTO devono essere rimossi.

### 3.5 Silenzio previsto

In POINTING l'assenza di messaggi audio non è un errore. Significa normalmente:

- nessuna mano rilevata;
- posa non ancora riconosciuta;
- gesto non ancora stabile;
- gesto già attivo e mantenuto;
- cooldown ancora attivo.

Il frontend non deve mostrare timeout o errore soltanto perché non riceve audio.

### 3.6 Messaggio overlay POINTING

Il backend invia anche `type: "pointing_overlay"` con raggio normalizzato, stato
`CANDIDATE`/`ACTIVE`, progresso di conferma e parametri geometrici del
corridoio. Il contratto completo e la formula di disegno sono documentati in
`Docs/handoff_frontend_pointing_overlay.md`.

Il frontend deve disegnare il cono sopra la preview senza eseguire MediaPipe o
altri modelli. Un array `overlays` vuoto cancella il disegno.

## 4. Stato frontend da introdurre

Introdurre un unico tipo di dominio frontend equivalente a:

```text
CaptionMode = "AUTO" | "POINTING"
```

Stato minimo della sessione:

| Stato | Scopo |
|---|---|
| `captionMode` | valore visibile dello switch |
| `captionModeRef` o equivalente | ultimo valore letto dal ciclo camera |
| `frameId` | contatore monotono |
| `captureState` | idle, connecting, streaming, stopped, error |
| `socketState` | connecting, open, closing, closed |
| `lastAudioFrameId` | protezione da audio vecchio |
| `modeChangeCutoffFrameId` | scarto output appartenente alla modalità precedente |
| `sentFrameMetadata` | associa frame ID, modalità e istante di invio |
| `audioQueue` | riproduzione seriale senza sovrapposizioni |

Se lo stack usa uno store globale, mantenere qui soltanto lo stato realmente
condiviso. Camera frame e buffer Base64 non devono causare re-render globali.

## 5. Switch AUTO/POINTING

### 5.1 Comportamento

Lo switch deve:

1. partire da `AUTO` a ogni nuova sessione, salvo requisito esplicito di
   persistenza;
2. mostrare chiaramente entrambe le modalità;
3. aggiornare stato reattivo e riferimento letto dal capture loop;
4. non riaprire camera o WebSocket;
5. non spedire un pacchetto di controllo separato;
6. far sì che il frame successivo contenga il nuovo `caption_mode`;
7. annullare l'audio in riproduzione della modalità precedente;
8. svuotare la coda audio precedente;
9. registrare il primo `frame_id` appartenente alla nuova modalità;
10. aggiornare il testo di stato per screen reader.

La modalità deve continuare a essere inclusa in tutti i frame successivi. Questo
rende il protocollo robusto al queue draining del backend, che può scartare
frame intermedi e conservare solamente l'ultimo.

### 5.2 Accessibilità

Lo switch deve avere:

- nome accessibile, per esempio `Modalità descrizione`;
- stato annunciato come `Automatica` o `Puntamento`;
- focus da tastiera;
- indicatore visivo non basato soltanto sul colore;
- area di tocco adeguata;
- testo di supporto:
  - AUTO: `Descrive automaticamente i cambiamenti della scena`;
  - POINTING: `Descrive quando mantieni il gesto di puntamento`.

In POINTING mostrare uno stato neutro come `In attesa del gesto`. Non mostrare
`Gesto riconosciuto` perché il backend attuale non invia un evento di conferma
della gesture.

## 6. Modifica del ciclo di cattura

Il ciclo esistente deve essere aggiornato, non duplicato.

Per ciascun tick:

1. verificare che cattura e WebSocket siano attivi;
2. verificare eventuale backpressure tramite `socket.bufferedAmount`;
3. se il buffer supera la soglia configurata, saltare il frame corrente;
4. acquisire il frame con orientamento corretto;
5. applicare resize mantenendo l'aspect ratio;
6. codificare realmente in JPEG;
7. convertire in Base64 senza prefisso data URL;
8. incrementare `frame_id`;
9. leggere il valore più recente dello switch;
10. salvare localmente `{frameId, mode, sentAt}`;
11. costruire il payload;
12. inviarlo soltanto se il socket è ancora `OPEN`.

Frequenza iniziale consigliata per la taratura: 10–15 FPS. Deve essere
configurabile e misurata sul dispositivo reale.

Non creare una coda illimitata di frame. Nel caso di congestione è corretto
perdere frame video: il sistema deve privilegiare il frame recente.

## 7. Orientamento e mirroring

MediaPipe e il VLM devono vedere la stessa immagine.

Il frontend deve:

- inviare pixel già ruotati correttamente;
- non affidarsi soltanto ai metadati EXIF;
- evitare crop diversi fra preview e JPEG inviato;
- applicare l'eventuale mirroring soltanto alla preview CSS;
- non specchiare i pixel inviati senza una decisione esplicita e testata;
- conservare l'intera scena, perché il raggio viene proiettato fino al bordo.

Questa fase deve essere provata sia con camera frontale sia con camera
posteriore, se entrambe sono supportate.

## 8. Cambio modalità durante una sessione

Sequenza richiesta:

```text
utente cambia switch
  -> aggiorna captionMode
  -> aggiorna il riferimento usato dal capture loop
  -> ferma audio corrente
  -> svuota audioQueue
  -> registra cutoff del cambio modalità
  -> continua con lo stesso WebSocket
  -> frame successivo contiene il nuovo caption_mode
```

Quando arriva un audio:

- recuperare la modalità associata al suo `frame_id`;
- scartarlo se il frame è precedente al cutoff del cambio modalità;
- scartarlo se la cattura è stata fermata;
- non applicare automaticamente a POINTING la stessa soglia di freschezza
  molto breve usata per AUTO;
- mantenere separate e configurabili le policy di freschezza AUTO e POINTING.

AUTO può produrre più audio per lo stesso frame. POINTING produce un solo audio
per evento confermato.

## 9. Gestione connessione

La connessione deve:

1. aprirsi quando comincia la sessione di cattura;
2. chiudersi esplicitamente quando la cattura termina;
3. chiudersi durante lo smontaggio del componente;
4. cancellare timer, animation frame e media track;
5. interrompere e svuotare l'audio;
6. gestire `open`, `message`, `error` e `close`;
7. effettuare reconnect con backoff soltanto se la sessione è ancora attiva;
8. usare al reconnect il valore corrente dello switch;
9. non riutilizzare promesse, listener o code appartenenti al vecchio socket.

Una nuova connessione crea una nuova sessione POINTING sul backend; gesture,
cooldown e stato MediaPipe ripartono da zero.

## 10. Parser dei messaggi server

Creare un solo punto di parsing con discriminazione sul campo `type`.

Comportamento richiesto:

| `type` | Azione |
|---|---|
| `audio` | valida, decodifica, mostra caption, accoda audio |
| `detections` | aggiorna overlay se la modalità associata è AUTO |
| `pointing_overlay` | aggiorna o cancella il cono se la modalità è POINTING |
| sconosciuto | log diagnostico, nessun crash |
| JSON non valido | log controllato, nessun crash dell'interfaccia |

Il vecchio comportamento che aspetta direttamente `Blob`, `ArrayBuffer` o
messaggi WebSocket binari non è compatibile con il server attuale.

## 11. Suddivisione consigliata

Adattare questi nomi alla struttura reale:

```text
domain/
  captionMode
  visionWebSocketMessages

services/
  visionWebSocketClient
  framePacketSerializer
  audioPlaybackQueue

hooks-or-store/
  visionSession
  cameraCapture

components/
  CaptionModeSwitch
  ConnectionStatus
  CaptionLiveRegion

tests/
  framePacketSerializer
  captionModeSwitch
  visionWebSocketClient
  audioPlaybackQueue
  visionSessionIntegration
```

Responsabilità:

- il componente switch gestisce soltanto interazione e accessibilità;
- il session controller coordina switch, camera, WebSocket e audio;
- il serializer crea il pacchetto richiesto dal backend;
- il WebSocket client gestisce trasporto e parsing;
- la coda audio impedisce sovrapposizioni e gestisce cancellazione;
- i componenti UI non devono conoscere Base64 o dettagli del protocollo.

## 12. Piano di test frontend

### 12.1 Test unitari

1. il serializer produce `caption_mode: "AUTO"` quando lo stato è AUTO;
2. produce `caption_mode: "POINTING"` dopo il toggle;
3. il nuovo valore compare in ogni frame successivo;
4. `frame_id` cresce monotonicamente;
5. l'immagine non contiene il prefisso data URL;
6. `pointing_coordinates` è assente o `null`;
7. il parser riconosce `audio`;
8. il parser riconosce `detections`;
9. un tipo sconosciuto non causa crash;
10. due chunk AUTO con lo stesso `frame_id` vengono entrambi accodati;
11. un frame audio con ID inferiore al cutoff viene scartato;
12. il cambio modalità ferma l'audio e svuota la coda;
13. il capture loop legge il valore aggiornato e non una closure obsoleta;
14. i frame vengono scartati quando `bufferedAmount` supera la soglia;
15. stop e unmount chiudono socket, camera e audio.

### 12.2 Test del componente switch

1. default AUTO;
2. attivazione POINTING;
3. ritorno ad AUTO;
4. uso da tastiera;
5. nome e stato accessibili;
6. annuncio della modalità;
7. nessuna apertura di un secondo socket;
8. nessun riavvio della camera.

### 12.3 Test WebSocket con server finto

1. catturare i messaggi inviati prima e dopo lo switch;
2. verificare che il cambio avvenga nel pacchetto successivo;
3. simulare un messaggio `detections`;
4. simulare un messaggio `audio` JSON Base64;
5. simulare più chunk con lo stesso `frame_id`;
6. simulare JSON invalido;
7. simulare chiusura e reconnect;
8. verificare che al reconnect venga usata la modalità corrente.

### 12.4 Test end-to-end col backend

Scenari minimi:

| Scenario | Risultato atteso |
|---|---|
| avvio | switch su AUTO, frame con `caption_mode=AUTO` |
| AUTO, scena invariata | nessun audio normale |
| AUTO, cambio scena | detection eventuali e audio JSON |
| passaggio a POINTING | stesso socket, overlay AUTO rimosso |
| POINTING senza gesto | nessun audio e nessun errore UI |
| POINTING con gesto stabile | un solo audio |
| gesto mantenuto | nessuna ripetizione |
| rilascio e nuovo gesto | secondo audio |
| POINTING → AUTO | coda precedente cancellata, AUTO riprende |
| stop cattura | nessun audio successivo, risorse chiuse |

La verifica positiva della gesture richiede backend reale, MediaPipe e una
sequenza video con mano. Il backend in mock mode restituisce zero mani e può
verificare soltanto il caso POINTING silenzioso.

## 13. Telemetria diagnostica minima

In sviluppo registrare, senza includere il Base64:

- apertura/chiusura socket;
- `frame_id`;
- modalità del frame;
- dimensioni JPEG;
- `bufferedAmount`;
- frame saltati per backpressure;
- tipo del messaggio ricevuto;
- latenza fra invio frame e ricezione audio;
- audio scartati e relativo motivo;
- cambio modalità e cutoff.

Non loggare immagini Base64, audio Base64, token o credenziali.

## 14. Non-obiettivi del frontend

Il frontend non deve:

- riconoscere la gesture;
- importare MediaPipe;
- calcolare angoli delle dita;
- calcolare il raggio;
- scegliere il bersaglio;
- chiamare direttamente VLM o TTS;
- inviare coordinate manuali di puntamento;
- interpretare il silenzio POINTING come errore.

## 15. Definition of Done

Il lavoro è completo quando:

- esiste uno switch accessibile AUTO/POINTING;
- il valore esatto viene inserito in ogni pacchetto frame;
- il cambio modalità non ricrea camera o WebSocket;
- `frame_id` è sempre presente e monotono;
- il frontend interpreta i messaggi server come JSON;
- audio e detection vengono discriminati tramite `type`;
- l'audio Base64 usa il MIME type derivato da `format`;
- la coda audio non sovrappone chunk;
- il cambio modalità cancella output obsoleto;
- il silenzio POINTING è rappresentato come attesa normale;
- orientamento e mirroring sono verificati sul dispositivo;
- test unitari, WebSocket fake ed end-to-end passano;
- l'agente consegna un breve report con file modificati, decisioni e test.

## 16. Ordine di implementazione

```text
0. Audit del repository frontend
1. Tipi del protocollo
2. Serializer del frame
3. Parser dei messaggi server
4. Switch accessibile
5. Collegamento switch → capture loop
6. Coda audio e cutoff di modalità
7. Backpressure e lifecycle
8. Test unitari
9. Test WebSocket fake
10. Test end-to-end e taratura
```
