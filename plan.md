# Piano di Implementazione — vision-caption

Questo documento descrive **cosa fare**, non come scriverlo.
Ogni fase ha un obiettivo, delle domande guida per ragionare sulla soluzione,
e una condizione di completamento verificabile.

Lavora una fase alla volta. È normale tornare indietro a raffinare.
Non copiare: usa questo documento come bussola, non come ricetta.

---

## Fase 0 — Setup del Progetto

**Obiettivo**: Progetto Python funzionante, struttura corretta, dipendenze installate.

**Cosa fare**:
- Inizializza il progetto con `uv init`
- Crea tutta la struttura delle cartelle come da README
- Aggiungi le dipendenze al `pyproject.toml`
- Verifica che `uv sync` vada a buon fine senza errori
- Crea tutti gli `__init__.py`
- Crea un `__main__.py` che stampa "server starting..." ed esce

**Fatto quando**: `uv run python -m vision_caption` esegue e stampa il messaggio.

---

## Fase 1 — Domain Layer

**Obiettivo**: Definire i modelli che rappresentano i concetti del dominio.
Questi file non importano NULLA di esterno — solo tipi Python e Pydantic.

**Concetti da modellare**:
1. Un frame video (con i bytes dell'immagine e metadati)
2. Una caption (la descrizione testuale prodotta dal VLM)
3. Una richiesta di caption (frame + modalità + eventuale prompt custom)
4. Un risultato audio (bytes audio + formato + durata)
5. La modalità di acquisizione (AUTO vs POINTING)

**Domande guida**:
- Che metadati ha un frame? Pensa a: timestamp, modalità, coordinate pointing
- Che informazioni porta una Caption oltre al testo? (pensa al benchmark della tesi)
- Come rappresenti i bytes audio? Che formati supporti (WAV, Opus)?
- `CaptureMode` è un Enum? Quali valori ha?
- I modelli devono essere immutabili? (suggerimento: `frozen=True` in Pydantic)

**Fatto quando**: Puoi creare istanze di ogni modello in un REPL Python senza errori.

---

## Fase 2 — Ports (Contratti)

**Obiettivo**: Definire le interfacce tra il core e il mondo esterno.
Un port è un contratto: dice cosa si aspetta il sistema, non come viene soddisfatto.

**Ports da definire**:
1. `SceneDetectorPort` — analizza un frame e dice se la scena è cambiata
2. `CaptionGeneratorPort` — riceve una CaptionRequest e restituisce una Caption
3. `SpeechSynthesizerPort` — riceve testo + lingua e restituisce AudioResult

**Domande guida**:
- Usa `typing.Protocol` (non ABC) — sai perché è preferibile qui?
- I metodi sono `async` o sync? Pensa: chi ha latenza alta? (rete, modelli AI)
- `SceneDetectorPort.analyze()` cosa restituisce? Solo bool o anche dati aggiuntivi?
  (utile per logging: es. il valore SSIM)
- Usa solo tipi del domain layer nelle firme — mai tipi di librerie esterne

**Fatto quando**: Puoi importare ogni Port e usarlo come type hint. `ruff` non si lamenta.

---

## Fase 3 — Services (Logica Applicativa)

**Obiettivo**: Implementare il cuore della pipeline. Questi moduli orchestrano i ports
iniettati ma non sanno nulla di Ollama, OpenCV, FastAPI.

### `RateLimiter`
Controlla che non vengano generate caption troppo frequentemente.
- Mantiene il timestamp dell'ultima caption generata
- `can_proceed()` → True se è passato abbastanza tempo
- `record()` → segna il momento corrente come "ultima caption"
- `seconds_until_next` → property: quanti secondi mancano

### `CaptionPipeline`
Orchestratore centrale. Riceve un frame e restituisce `AudioResult | None`.

Disegna il flusso su carta prima di scrivere una riga:
1. Se modalità POINTING → vai diretto alla generazione (saltando detection e rate limiter)
2. Se modalità AUTO → chiedi al scene detector se la scena è cambiata
3. Se scena non cambiata → restituisci None
4. Se rate limiter non permette → restituisci None
5. Registra nel rate limiter
6. Genera la caption (VLM)
7. Sintetizza l'audio (TTS)
8. Restituisci AudioResult

**Domande guida**:
- Come testi la pipeline senza GPU? Cosa deve esporre ogni Port per poterlo "mockare"?
- Come loggi gli step intermedi? (suggerimento: structlog, logga le latenze per la tesi)
- `process_pointing()` è un metodo separato o un ramo dentro `process()`?

**Fatto quando**: Hai un test che crea la pipeline con mock, chiama `process()`,
e verifica il flusso corretto.

---

## Fase 4 — Adapter: Scene Detection (SSIM)

**Obiettivo**: Prima implementazione concreta di `SceneDetectorPort`.
Confronta il frame corrente con il precedente usando la Structural Similarity (SSIM).

**Concetto SSIM**:
SSIM misura quanto due immagini si assomigliano strutturalmente (0 = totalmente diverse,
1 = identiche). Se SSIM scende sotto una soglia (es. 0.85), la scena è cambiata.

**Domande guida**:
- Come converti bytes JPEG → array numpy in scala di grigi per il confronto SSIM?
- Cosa fai al primo frame (non c'è un frame "precedente")?
- La soglia SSIM è un parametro del costruttore o hardcodata?
- Che libreria usi per SSIM? (suggerimento: `skimage.metrics.structural_similarity`)
- L'adapter deve mantenere stato (frame precedente) — dove lo salvi?

**Fatto quando**: Crei due immagini di test (una uguale, una diversa) e verifichi
che l'adapter risponda correttamente in entrambi i casi.

---

## Fase 5 — Adapter: VLM Caption (Ollama)

**Obiettivo**: Implementazione di `CaptionGeneratorPort` che chiama Ollama.

**Come funziona Ollama**:
Ollama espone una REST API locale su `http://localhost:11434`.
Per le completion multimodali, il payload include il frame codificato in base64.

**Domande guida**:
- Studia la documentazione di Ollama per capire il formato del payload multimodale
- Come codifichi l'immagine in base64 da includere nella richiesta?
- Che prompt produce descrizioni utili per non vedenti? (italiano, conciso, orientato all'azione)
- Come misuri il tempo di generazione per il benchmark della tesi?
- Come gestisci un timeout o un errore di rete?
- Usa `httpx` async per la chiamata HTTP — perché async e non requests?

**Fatto quando**: Puoi chiamare l'adapter con un frame reale e Ollama che gira
e ricevere una stringa di descrizione.

---

## Fase 6 — Adapter: TTS (Chatterbox)

**Obiettivo**: Implementazione di `SpeechSynthesizerPort` usando Chatterbox TTS.

Prima di scrivere una riga, studia `docs/Chatterbox_TTS.md` per capire:
- Come si importa e usa Chatterbox
- Che formato audio produce
- Come gestire il caricamento del modello (warmup)

**Domande guida**:
- Chatterbox va caricato nel costruttore o al primo utilizzo (lazy loading)?
- Che formato audio restituisce? Come lo impacchetti in `AudioResult`?
- Come testi questo adapter senza GPU? (mock che restituisce silenzio WAV)
- Il modello è condiviso tra chiamate o ne crei uno per ogni sintesi?

**Fatto quando**: Hai un test che sintetizza "ciao" e ottieni bytes audio non vuoti.

---

## Fase 7 — Infrastructure: Settings

**Obiettivo**: Centralizzare la configurazione. Zero valori hardcodati nel codice.

**Struttura di AppSettings**:
Raggruppa la configurazione in sotto-oggetti:
- `server` → host, porta
- `scene_detection` → soglia SSIM, intervallo minimo tra caption
- `vlm` → nome modello, temperatura, max_tokens, lingua, URL Ollama
- `tts` → modello, parametri voce

**Domande guida**:
- Usa `pydantic-settings` con un `yaml_settings_source` — sai come funziona?
- Quale ordine di priorità: YAML < env var, o il contrario?
- Come gestisci una API key opzionale senza esporla nel YAML?
- Che valori di default hanno senso per lo sviluppo locale?

**Fatto quando**: `AppSettings()` carica `config.yaml` e può essere overridata da env var.

---

## Fase 8 — Infrastructure: DI Container

**Obiettivo**: Unico posto dove si assemblano i componenti concreti.
Il container è l'unico modulo che importa gli adapters.

**Pattern da implementare**:
Ogni componente viene creato una volta sola (singleton per sessione).
Il pattern classico: variabile privata `None`, creata al primo accesso.

```
def create_scene_detector(self) -> SceneDetectorPort:
    if self._scene_detector is None:
        self._scene_detector = ...  # crea qui
    return self._scene_detector
```

**Domande guida**:
- In che ordine si costruiscono le dipendenze? Disegna il grafo prima di scrivere
- Come gestisci `use_mocks=True` per lo sviluppo senza GPU?
- Se `create_pipeline()` chiama internamente `create_scene_detector()`, funziona
  anche se chiamato per primo — verificalo

**Fatto quando**: `ApplicationContainer(settings).create_pipeline()` non lancia eccezioni.

---

## Fase 9 — Infrastructure: WebSocket Server

**Obiettivo**: Esporre la pipeline via WebSocket con FastAPI.

**Protocollo WebSocket**:
- IN: il client manda frame JPEG come bytes binari (o JSON con base64 + metadati)
- OUT: il server manda audio WAV come bytes binari

**Componenti**:
1. `app.py` — factory function che crea l'app FastAPI, inizializza il container
2. `ws_handler.py` — gestisce ogni connessione WebSocket
3. Endpoint `/health` — risponde 200 con status del server
4. `__main__.py` — avvia uvicorn

**Domande guida**:
- Come il WebSocket handler riceve la pipeline? (suggerimento: `app.state`)
- Come decodifichi un messaggio WebSocket in un FrameData?
- Se la pipeline restituisce None (scena stabile), cosa mandi al client?
- Come gestisci una disconnessione improvvisa del client?
- Come gestisci un'eccezione durante l'elaborazione?

**Fatto quando**: Il server parte, accetta connessioni WebSocket, `/health` risponde 200.

---

## Fase 10 — Testing

**Obiettivo**: Verificare i componenti in isolamento e poi in integrazione.

**Unit test** (senza GPU, veloci):
- `test_rate_limiter.py` — testa `can_proceed()`, `record()`, `seconds_until_next`
- `test_caption_pipeline.py` — usa mock per tutti i ports, testa i rami del flusso
- `test_ssim_detector.py` — usa immagini numpy di test, non frame reali

**Integration test** (richiede Ollama + GPU, lenti):
- `test_ws_e2e.py` — client WebSocket che manda un frame e verifica di ricevere audio

**Domande guida**:
- Come scrivi un mock di `CaptionGeneratorPort`? (basta una classe con il metodo)
- Come testi che la pipeline restituisce None quando la scena non cambia?
- Come testi che il rate limiter blocca la seconda richiesta ravvicinata?
- Come generi un'immagine di test senza usare file sul disco? (numpy → jpeg bytes)

**Fatto quando**: `pytest tests/unit/ -v` passa completamente senza GPU.

---

## Fase 11 — Benchmark & Deployment

**Obiettivo**: Misurare le latenze e preparare il deploy per il cluster HPC.

**Script `benchmark_latency.py`**:
- Invia N frame al server
- Misura e registra: latenza SSIM, latenza VLM, latenza TTS, latenza totale round-trip
- Salva i risultati in CSV/JSON per matplotlib (grafici tesi)

**Deploy**:
- `deploy/Dockerfile` — immagine standalone
- `deploy/docker-compose.yml` — stack con Ollama containerizzato
- `deploy/slurm_job.sh` — job per cluster PurpleJeans (SBATCH directives, moduli CUDA)

**Domande guida**:
- Dove nella pipeline hai già loggato le latenze? Bastano o serve strumentazione aggiuntiva?
- Che valori di latenza sono accettabili per l'accessibilità in tempo reale?
- Come monti i pesi del modello Ollama nel job Slurm senza riscaricarli ogni run?

**Fatto quando**: Hai un CSV con latenze reali e almeno un grafico per la tesi.

---

## Checklist di Completamento

- [ ] Fase 0: `uv run python -m vision_caption` esegue
- [ ] Fase 1–3: `pytest tests/unit/test_caption_pipeline.py` con mock passa
- [ ] Fase 4: SSIM detector funziona su frame di test
- [ ] Fase 5: OllamaCaption genera testo con Ollama locale
- [ ] Fase 6: ChatterboxSynth produce audio WAV
- [ ] Fase 7–8: Server parte con `USE_MOCKS=true`
- [ ] Fase 9: Server parte in produzione con Ollama + GPU
- [ ] Fase 10: Tutti gli unit test passano
- [ ] Fase 11: Hai numeri di latenza per la tesi
