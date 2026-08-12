"""Misure per fotogramma della pipeline AUTO.

Ogni fotogramma elaborato produce una riga di log strutturata con il prefisso
``PIPELINE_METRIC`` seguito da un oggetto JSON. Le righe sono pensate per
essere aggregate a posteriori da ``scripts/aggregate_metrics.py``, che ne
ricava le tabelle della valutazione sperimentale.

Il tracciamento non altera il comportamento della pipeline: registra soltanto
tempi ed esiti delle decisioni già prese altrove.
"""

import json
import time
from dataclasses import asdict, dataclass, field

from loguru import logger

METRIC_PREFIX = "PIPELINE_METRIC"


@dataclass
class FrameMetrics:
    """Raccoglie le misure di un singolo fotogramma in modalità AUTO.

    ``outcome`` indica il livello al quale l'elaborazione si è fermata, ed è
    la chiave con cui si ricostruisce quanti fotogrammi superano ciascun
    filtro della cascata.
    """

    frame_id: int
    outcome: str = "unknown"
    ssim_score: float | None = None
    detect_ms: float | None = None
    vlm_first_chunk_ms: float | None = None
    vlm_total_ms: float | None = None
    tts_ms: list[float] = field(default_factory=list)
    first_audio_ms: float | None = None
    frame_age_at_first_audio_s: float | None = None
    detections: int = 0
    chunks_emitted: int = 0
    chunks_deduplicated: int = 0

    _started_at: float = field(default=0.0, repr=False)

    def __post_init__(self) -> None:
        self._started_at = time.perf_counter()

    def elapsed_ms(self) -> float:
        """Millisecondi trascorsi dall'inizio dell'elaborazione del frame."""
        return (time.perf_counter() - self._started_at) * 1000.0

    def emit(self, outcome: str) -> None:
        """Registra l'esito e scrive la riga di misura."""
        self.outcome = outcome
        payload = {
            key: value
            for key, value in asdict(self).items()
            if not key.startswith("_")
        }
        payload["total_ms"] = round(self.elapsed_ms(), 1)
        logger.debug(f"{METRIC_PREFIX} {json.dumps(payload)}")
