"""La voce già pronunciata, tenuta da parte per quando serve di nuovo.

Oggi tornare su una slide già descritta produce silenzio. Il rilevatore vede
un cambio di scena, il modello viene chiamato e pagato per intero, la
descrizione arriva, e il filtro della ripetizione la butta perché quella
slide era già stata raccontata. Nei log delle sessioni di prova è successo
183 volte, contro 126 descrizioni dette: più della metà del lavoro del
modello è finito in niente, e chi ascoltava non ha sentito nulla.

Il silenzio è la parte peggiore. Chi vede capisce dal proiettore di essere
tornato indietro; chi non vede non sa se l'applicazione ha riconosciuto la
slide o si è rotta.

Qui si tiene l'audio già sintetizzato delle slide in memoria, con la stessa
chiave con cui la memoria della lezione le riconosce - il testo che era
stato detto. Quando la ripetizione scatta, invece di tacere si risente
quella voce, preceduta da un avviso breve che dice che è una ripetizione.

La chiave non è l'immagine. Riconoscere la stessa slide dai pixel sarebbe il
modo per risparmiare anche la chiamata al modello, ma la soglia oltre la
quale due riprese sono la stessa slide non si può indovinare: misurata sui
campioni delle sessioni, nessun valore separa le riprese della stessa scena
da quelle di scene diverse, perché a mano libera la stessa scena cambia più
di quanto cambino due scene vicine. Finché quella soglia non è misurata su
una lezione vera, la chiave resta il giudizio che il modello ha già dato.
"""

from collections import OrderedDict
from collections.abc import Iterable

from vision_caption.core.domain.audio import Audio


def normalize_key(text: str) -> str:
    """La forma con cui due testi identici coincidono davvero."""
    return " ".join(text.casefold().split()).strip(".,!?;:")


class DescribedSceneCache:
    """L'audio delle descrizioni già dette, nella finestra della memoria."""

    def __init__(self, max_entries: int = 8) -> None:
        self._entries: OrderedDict[str, Audio] = OrderedDict()
        self._max_entries = max(1, max_entries)
        self._cue: Audio | None = None

    def __len__(self) -> int:
        return len(self._entries)

    def remember(self, text: str, audio: Audio) -> None:
        key = normalize_key(text)
        if not key:
            return
        # Risentita di recente, va tenuta: l'ordine è quello dell'uso, non
        # quello dell'arrivo.
        self._entries.pop(key, None)
        self._entries[key] = audio
        while len(self._entries) > self._max_entries:
            self._entries.popitem(last=False)

    def find(self, text: str) -> Audio | None:
        key = normalize_key(text)
        audio = self._entries.get(key)
        if audio is None:
            return None
        self._entries.move_to_end(key)
        return audio

    def keep_only(self, texts: Iterable[str]) -> None:
        """Butta ciò che la memoria della lezione non ricorda più.

        La memoria tiene le ultime cinque slide e si azzera quando la
        presentazione cambia: l'audio di una slide che non è più lì non
        verrebbe mai richiesto, e tenerlo occuperebbe memoria per niente.
        """
        vivi = {normalize_key(text) for text in texts}
        for key in [key for key in self._entries if key not in vivi]:
            del self._entries[key]

    def clear(self) -> None:
        self._entries.clear()

    # ------------------------------------------------------------ avviso
    # L'avviso che precede una ripetizione si sintetizza una volta per
    # sessione e si riusa: è sempre la stessa frase, e chiederla di nuovo
    # al servizio vocale costerebbe il tempo che stiamo risparmiando.

    @property
    def cue(self) -> Audio | None:
        return self._cue

    def remember_cue(self, audio: Audio) -> None:
        self._cue = audio
