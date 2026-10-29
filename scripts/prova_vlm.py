r"""Manda al modello visivo una slide di prova, come farebbe il server.

Si esegue dentro il contenitore del server, che ha già codice e indirizzi:

    Get-Content scripts\prova_vlm.py | docker compose exec -T server python -

Con un percorso usa quell'immagine invece della slide, per esempio un frame
salvato fra i campioni (artifacts è montata in /app/artifacts):

    Get-Content scripts\prova_vlm.py | docker compose exec -T server python - /app/artifacts/samples/<sessione>/auto_000001/frame.jpg

Stampa il testo generato e quanto ci è voluto, due volte: la prima misura
anche la lettura dell'immagine, la seconda la ritrova già in cache.
"""

import asyncio
import sys
import time
from pathlib import Path

import cv2
import numpy as np

from vision_caption.adapters.vlm.OpenRouterCaptionGenerator import (
    OpenRouterCaptionGenerator,
)
from vision_caption.adapters.vlm.prompts import auto_prompt
from vision_caption.core.domain.frame import CaptionMode, Frame
from vision_caption.infrastructure.settings import AppSettings


def slide() -> bytes:
    image = np.full((480, 640, 3), 255, np.uint8)
    cv2.putText(image, "Le derivate", (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 0, 0), 3)
    for row, text in enumerate(
        ["- definizione di limite", "- regola della catena", "- f'(x) = 2x + 3"]
    ):
        cv2.putText(image, text, (60, 180 + row * 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    return cv2.imencode(".jpg", image)[1].tobytes()


async def main() -> None:
    settings = AppSettings.from_env()
    generator = OpenRouterCaptionGenerator(
        api_key=settings.vlm.api_key,
        model_name=settings.vlm.resolved_model_name,
        base_url=settings.vlm.resolved_base_url,
        max_tokens=settings.auto.vlm.max_output_tokens,
        temperature=settings.auto.vlm.temperature,
        prompt=auto_prompt(settings.vlm.context),
    )
    print(f"modello={settings.vlm.resolved_model_name} endpoint={settings.vlm.resolved_base_url}")
    image = Path(sys.argv[1]).read_bytes() if len(sys.argv) > 1 else slide()
    decoded = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
    print(f"immagine: {decoded.shape[1]}x{decoded.shape[0]}, {len(image)} byte")
    frame = Frame(frame_id=1, image_bytes=image, caption_mode=CaptionMode.AUTO)
    for attempt in (1, 2):
        started = time.perf_counter()
        texts = [text async for text in generator.generate(frame)]
        print(f"prova {attempt}: {time.perf_counter() - started:.1f}s -> {texts}")


asyncio.run(main())
