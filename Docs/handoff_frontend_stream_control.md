# Handoff frontend: controllo del flusso e interfaccia utente mobile

Il backend espone il protocollo WebSocket versione 1. Il frontend deve usarlo
per evitare code di frame e mantenere separata l'anteprima locale dalla cadenza
dei JPEG inviati al server.

## Branch

Eseguire queste operazioni nel repository frontend, con working tree pulito:

```bash
git switch main
git pull --ff-only
git branch debug
git push -u origin debug
git switch -c feat/mobile-user-interface
```

Il branch `debug` conserva log, bounding box, landmark e strumenti diagnostici.
La feature viene integrata in `main`, che contiene soltanto l'interfaccia per
l'utente finale.

## Messaggio iniziale del backend

Subito dopo la connessione il backend invia:

```json
{
  "type": "stream_config",
  "protocol_version": 1,
  "fps": {"AUTO": 2.0, "POINTING": 10.0},
  "max_in_flight": 1,
  "max_buffered_amount_bytes": 262144
}
```

Salvare questi valori nello stato del client. Non applicare gli FPS alla
preview `<video>`: limitare soltanto la cattura JPEG e `WebSocket.send()`.

## Invio di un solo frame alla volta

Il client mantiene `frameInFlight` e il timestamp dell'ultimo invio:

```ts
let frameInFlight = false;
let lastFrameSentAt = 0;

function canSendFrame(socket: WebSocket, intervalMs: number): boolean {
  return !frameInFlight
    && socket.readyState === WebSocket.OPEN
    && socket.bufferedAmount <= 262_144
    && performance.now() - lastFrameSentAt >= intervalMs;
}
```

Immediatamente prima di `socket.send(payload)`:

```ts
frameInFlight = true;
lastFrameSentAt = performance.now();
```

Non creare una coda di JPEG. Quando il backend è occupato, la preview continua
a scorrere e il prossimo invio viene catturato dal frame video più recente.

## ACK del backend

Al termine di ogni frame, con o senza audio, il backend invia:

```json
{
  "type": "frame_done",
  "frame_id": 123,
  "min_frame_interval_ms": 500,
  "processing_ms": 52.4
}
```

Gestione richiesta:

```ts
if (message.type === "frame_done") {
  frameInFlight = false;
  scheduleLatestCameraFrame(message.min_frame_interval_ms);
}
```

`min_frame_interval_ms` è l'intervallo minimo misurato dall'ultimo invio, non
un'attesa da aggiungere alla durata di elaborazione. Se sono già passati 500 ms,
il nuovo frame può essere inviato immediatamente.

## Detection e overlay

Il frontend continua a riconoscere i messaggi `detections` e
`pointing_overlay`, ma in `main` non monta i componenti che li disegnano.
Non è sufficiente nasconderli con CSS: canvas, bounding box e landmark non
devono essere renderizzati nell'albero della UI finale.

Nel branch `debug` possono rimanere disponibili dietro un flag di build:

```ts
const DEBUG_UI = import.meta.env.VITE_DEBUG_UI === "true";
```

```tsx
{DEBUG_UI && <DebugPanel />}
{DEBUG_UI && <DetectionOverlay />}
{DEBUG_UI && <LandmarkOverlay />}
```

Produzione:

```dotenv
VITE_DEBUG_UI=false
```

## Layout mobile finale

- pagina verticale a `100dvh`;
- rispetto delle safe area iOS;
- preview fotocamera a tutto schermo con `object-fit: contain`;
- controlli essenziali sovrapposti in basso;
- nessun pannello log, metrica, frame ID, box o landmark;
- stato sintetico accessibile: connessione, analisi e riproduzione audio.

## Casi da verificare

1. In AUTO non vengono inviati più di 2 FPS.
2. In POINTING non vengono inviati più di 10 FPS.
3. Non esistono mai due frame in flight.
4. Durante una caption di due secondi la preview resta fluida e non cresce una
   coda di JPEG.
5. `audio` viene gestito prima del successivo `frame_done`.
6. Detection e overlay ricevuti non sono visibili nella build di produzione.
