import pytest

from vision_caption.adapters.vlm.prompts import auto_prompt, pointing_context


def test_lesson_prompt_requires_concrete_pictures_after_text() -> None:
    prompt = auto_prompt("lesson")
    assert "Immagine:" in prompt
    assert "oggetti" in prompt and "colori" in prompt
    assert "prima il testo" in prompt
    assert "dentro" in prompt
    # Le superfici dell'aula restano escluse come nel contesto generale.
    assert "Non descrivere mai pavimento" in prompt
    assert "pavimento, pareti, soffitto" in auto_prompt("general")


def test_lesson_pointing_picture_has_its_own_description_budget() -> None:
    prompt = pointing_context("lesson")
    assert "fotografie" in prompt and "colori" in prompt
    assert "venti parole" in prompt


async def _generate_with_memory(monkeypatch):
    import importlib
    import json
    import httpx
    from vision_caption.core.domain.frame import Frame, CaptionMode

    module = importlib.import_module('vision_caption.adapters.vlm.OpenRouterCaptionGenerator')
    seen = []
    def handler(request):
        seen.append(json.loads(request.content))
        return httpx.Response(200,content=b'data: {"choices":[{"delta":{"content":"PAGINA: nessuna\\nTitolo: Prova."}}]}\n\ndata: [DONE]\n')
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(module.httpx,'AsyncClient',lambda:client)
    generator=module.OpenRouterCaptionGenerator('key',prompt=auto_prompt('lesson'))
    frame=Frame(frame_id=1,image_bytes=b'jpeg',caption_mode=CaptionMode.AUTO)
    result=[text async for text in generator.generate(frame,'Slide precedente con sedie rosa.')]
    return seen[0]['messages'][0]['content'][0]['text'],result


@pytest.mark.asyncio
async def test_current_image_instructions_follow_the_historical_memory(monkeypatch):
    prompt,result=await _generate_with_memory(monkeypatch)
    assert prompt.index('Slide precedente') < prompt.index("ISTRUZIONI PER L'IMMAGINE CORRENTE")
    assert 'entro i suoi confini' in prompt
    assert result == ['PAGINA: nessuna\nTitolo: Prova.']
