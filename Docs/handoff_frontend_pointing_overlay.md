# Messaggio per il team frontend — overlay POINTING via WebSocket

Il backend espone ora un terzo tipo di messaggio JSON sullo stesso WebSocket
`/ws/vision` già usato per `audio` e `detections`:

```text
type = "pointing_overlay"
```

Non dovete eseguire MediaPipe, RF-DETR o altri modelli nel client. Il backend
calcola mano, stato della gesture e raggio; il frontend deve soltanto disegnare
il cono sopra la preview della camera.

## Contratto

Esempio con una mano in puntamento:

```json
{
  "type": "pointing_overlay",
  "frame_id": 123,
  "overlays": [
    {
      "handedness": "RIGHT",
      "state": "CANDIDATE",
      "confirmation_progress": 0.62,
      "ray": {
        "start": {"x": 0.42, "y": 0.61},
        "end": {"x": 1.0, "y": 0.34}
      }
    }
  ],
  "corridor": {
    "coordinate_space": "normalized",
    "width_reference": "short_side",
    "start_half_width_ratio": 0.008,
    "min_end_half_width_ratio": 0.03,
    "expansion_ratio": 0.04,
    "fill_alpha": 0.14,
    "color": "#FFFF00",
    "line_width_px": 2.0
  }
}
```

Quando non esiste più un puntamento da mostrare:

```json
{
  "type": "pointing_overlay",
  "frame_id": 124,
  "overlays": [],
  "corridor": {
    "coordinate_space": "normalized",
    "width_reference": "short_side",
    "start_half_width_ratio": 0.008,
    "min_end_half_width_ratio": 0.03,
    "expansion_ratio": 0.04,
    "fill_alpha": 0.14,
    "color": "#FFFF00",
    "line_width_px": 2.0
  }
}
```

`overlays` è un array perché il protocollo resta valido anche se in futuro il
backend viene configurato per più mani.

Gli stati possibili sono:

- `CANDIDATE`: la posa sembra corretta ma non ha ancora superato il tempo di
  conferma. Usare `confirmation_progress`, compreso fra `0` e `1`, per mostrare
  il progresso;
- `ACTIVE`: gesture confermata. Il VLM viene attivato una sola volta, ma il
  raggio continua a descrivere dove sta puntando la mano.

## Tipi TypeScript suggeriti

```ts
type NormalizedPoint = {
  x: number;
  y: number;
};

type PointingOverlay = {
  handedness: "LEFT" | "RIGHT" | "UNKNOWN";
  state: "CANDIDATE" | "ACTIVE";
  confirmation_progress: number;
  ray: {
    start: NormalizedPoint;
    end: NormalizedPoint;
  };
};

type PointingCorridorStyle = {
  coordinate_space: "normalized";
  width_reference: "short_side";
  start_half_width_ratio: number;
  min_end_half_width_ratio: number;
  expansion_ratio: number;
  fill_alpha: number;
  color: string;
  line_width_px: number;
};

type PointingOverlayMessage = {
  type: "pointing_overlay";
  frame_id: number;
  overlays: PointingOverlay[];
  corridor: PointingCorridorStyle;
};
```

Aggiungete `PointingOverlayMessage` alla union discriminata che contiene già i
messaggi `audio` e `detections`. Non aprite un secondo WebSocket.

## Costruzione del cono

Usate un canvas o SVG sovrapposto alla preview. Per ogni overlay:

1. trasformate le coordinate normalizzate in coordinate dell'immagine:
   `startX = ray.start.x * imageWidth`, `startY = ray.start.y * imageHeight` e
   analogamente per `end`;
2. calcolate `dx = endX - startX`, `dy = endY - startY` e
   `length = hypot(dx, dy)`;
3. calcolate il versore perpendicolare:
   `px = -dy / length`, `py = dx / length`;
4. calcolate `shortSide = min(imageWidth, imageHeight)`;
5. calcolate:

```ts
const startHalfWidth =
  corridor.start_half_width_ratio * shortSide;

const endHalfWidth = Math.max(
  corridor.min_end_half_width_ratio * shortSide,
  length * corridor.expansion_ratio,
);
```

6. costruite il quadrilatero:

```ts
const polygon = [
  [startX + px * startHalfWidth, startY + py * startHalfWidth],
  [startX - px * startHalfWidth, startY - py * startHalfWidth],
  [endX - px * endHalfWidth, endY - py * endHalfWidth],
  [endX + px * endHalfWidth, endY + py * endHalfWidth],
];
```

7. riempite il poligono con `corridor.color` e alpha
   `corridor.fill_alpha`;
8. disegnate contorno, linea centrale e un piccolo cerchio sull'origine.

In `CANDIDATE` potete usare un contorno tratteggiato o un'alpha più basso. In
`ACTIVE` usate lo stile pieno.

## Allineamento con la preview

Le coordinate si riferiscono ai pixel del JPEG inviato al backend. Il canvas
deve quindi usare la stessa trasformazione della preview:

- stesso aspect ratio;
- stesso crop prodotto da `object-fit: cover` oppure stessi margini di
  `object-fit: contain`;
- stessa rotazione;
- stesso mirroring.

Se la preview è specchiata solo tramite CSS, specchiate anche il canvas oppure
convertite ogni ascissa con `x = 1 - x`. Non applicate entrambe le correzioni.

Usate le dimensioni intrinseche del frame/video per calcolare il poligono e
applicate successivamente la trasformazione verso le dimensioni visualizzate.

## Lifecycle

- Disegnate il messaggio soltanto se `frame_id` non è più vecchio dell'ultimo
  overlay applicato.
- `overlays: []` deve cancellare immediatamente il canvas.
- Cancellate il canvas anche passando da `POINTING` ad `AUTO`, chiudendo la
  camera o chiudendo il WebSocket.
- Per evitare un cono congelato mentre il backend esegue VLM/TTS, applicate una
  scadenza visiva di circa 750 ms: se non arriva un aggiornamento, nascondete
  l'overlay fino al messaggio successivo.
- Non interpretate l'assenza di audio come errore: durante `CANDIDATE` è il
  comportamento normale.

## Test minimi richiesti

1. parsing del nuovo tipo senza influenzare `audio` e `detections`;
2. rendering di un raggio orizzontale, verticale e diagonale;
3. cancellazione con `overlays: []`;
4. scarto di un `frame_id` vecchio;
5. allineamento con `object-fit: contain` e `cover`;
6. mirroring della camera frontale;
7. differenza visiva fra `CANDIDATE` e `ACTIVE`;
8. nessun secondo WebSocket e nessun modello ML nel frontend.
