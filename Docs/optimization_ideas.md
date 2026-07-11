# Idee di Ottimizzazione Backend per Azzeramento Lag e Falsi Positivi

Questo documento raccoglie le idee architetturali emerse durante l'analisi del log del 30/06/2026.

## 1. Sovrapposizione a Cascata (Streaming Tokens)
Attualmente la pipeline è strettamente sequenziale:
`Frame -> VLM calcola TUTTO il testo (4s) -> TTS calcola TUTTO l'audio (8s) -> Frontend`
**Soluzione:** Sfruttare lo stream dei token del VLM. Non appena il VLM genera la prima frase, inviarla al TTS.

## 2. Fast Models
- **TTS (8.5s):** Sostituire Chatterbox locale con modelli ultra-rapidi (Piper TTS) o API esterne.
- **VLM (3.9s):** Passare a modelli small-edge (es. Llama-3-Vision-Edge o Moondream2).

## 3. Preemptive Task Cancellation
Quando arriva un nuovo frame che triggera un cambio scena reale, il backend cancella brutalmente il Task asincrono del frame precedente. 

## 4. Problema del Dondolio (Filtro Semantico Ibrido)
Salvare in memoria l'elenco delle etichette (labels) estratte da RF-DETR. Se l'elenco delle etichette è *identico* al precedente, il backend sopprime la chiamata al VLM. Fatto!

---

## 5. Deduplicazione Semantica delle Caption (Anti-Sovrapposizione Audio)
**Il Problema:** Se l'utente introduce un telefono, parte il VLM (1° volta). Se RF-DETR "sfarfalla" e rileva un oggetto in più o in meno un secondo dopo, riparte il VLM (2° volta). Se le due descrizioni generate dal VLM sono praticamente identiche (es. "Un uomo con un telefono" vs "Un uomo tiene un telefono"), la seconda descrizione viene inviata al TTS, sprecando 8 secondi e interrompendo l'audio in esecuzione sul frontend.

**Soluzioni Proposte:**
- **Controllo di similarità testuale:** Subito dopo che il VLM ha generato la caption (e PRIMA di chiamare il TTS), il backend usa un algoritmo leggerissimo (come `difflib.SequenceMatcher` di Python) per confrontare la nuova frase con quella precedente.
- Se la similarità è > 80% (es. 0.8), la nuova caption viene classificata come "Falso Positivo Semantico". Il flusso si interrompe, il TTS non viene chiamato, e l'audio precedente sul frontend continua a suonare indisturbato.
