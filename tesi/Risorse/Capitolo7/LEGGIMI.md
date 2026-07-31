# Immagini richieste dal Capitolo 7

Il capitolo compila anche senza queste immagini: al loro posto vengono
visualizzati riquadri descrittivi. Quando i file vengono aggiunti con i nomi
indicati, LaTeX li inserisce automaticamente.

## 1. Prova SSIM e RF-DETR

Il Capitolo 7 utilizza quattro immagini della stessa scena:

| Contenuto | Nome usato nella tesi |
|---|---|
| Primo frame in scala di grigi | `ssim_frame1_grayscale.jpeg` |
| Secondo frame in scala di grigi | `ssim_frame2_grayscale.jpeg` |
| Detection RF-DETR sul primo frame | `ssim_frame1_rfdetr.jpeg` |
| Detection RF-DETR sul secondo frame | `ssim_frame2_rfdetr.jpeg` |

Oscurare volti, schermi, documenti e altri dati personali.

## 2. `rfdetr_stampante_microonde.jpg`

Acquisire il caso sperimentale in cui la stampante viene classificata come
`microwave`. Nell'immagine devono essere leggibili:

- bounding box;
- etichetta assegnata;
- confidence.

Ritagliare lo sfondo se contiene informazioni personali.

## 3. Tripletta POINTING

Attivare temporaneamente:

```text
POINTING_DEBUG_SAVE_IMAGES=true
POINTING_DEBUG_OUTPUT_DIR=artifacts/pointing_debug
```

Eseguire un singolo gesto di puntamento su una scena preparata e copiare dalla
stessa cartella di evento:

| File generato dal backend | Nome da usare nella tesi |
|---|---|
| `01_context_with_corridor.jpg` | `pointing_context.jpg` |
| `02_focus_darkened_and_cropped.jpg` | `pointing_focus.jpg` |
| `03_clean_original.jpg` | `pointing_clean.jpg` |

Usare i tre file appartenenti allo stesso `frame_id`. Disattivare nuovamente
il salvataggio dopo l'acquisizione.

## Privacy

Le immagini di debug non devono essere aggiunte al controllo di versione se
contengono persone riconoscibili o informazioni private. Per la versione
definitiva della tesi usare scene predisposte, consenso esplicito oppure
anonimizzazione.
