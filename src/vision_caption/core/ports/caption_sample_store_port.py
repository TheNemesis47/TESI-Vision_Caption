from typing import Any, Protocol


class CaptionSampleStorePort(Protocol):
    """Conserva ciò che il modello visivo ha ricevuto e ciò che ha risposto.

    Serve a rivedere dopo i test, immagine per immagine, ogni descrizione
    generata. Come il log di ricerca, non deve mai fermare la pipeline.
    """

    def save(
        self,
        name: str,
        images: dict[str, bytes],
        record: dict[str, Any],
    ) -> None:
        ...


class NullCaptionSampleStore:
    """Non salva nulla: è il comportamento quando i campioni sono spenti."""

    def save(
        self,
        name: str,
        images: dict[str, bytes],
        record: dict[str, Any],
    ) -> None:
        pass
