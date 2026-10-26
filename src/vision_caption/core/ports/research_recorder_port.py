from typing import Any, Protocol


class ResearchRecorderPort(Protocol):
    """Registra gli eventi di una sessione per l'analisi dello studio.

    Ogni evento ha un nome e dei campi semplici (numeri, stringhe, liste).
    La registrazione non deve mai interrompere la pipeline: chi la implementa
    assorbe da sé gli errori di scrittura.
    """

    def record(self, event: str, **fields: Any) -> None:
        ...


class NullResearchRecorder:
    """Registratore che scarta tutto: è quello usato quando il log è spento."""

    def record(self, event: str, **fields: Any) -> None:
        pass

    def close(self) -> None:
        pass
