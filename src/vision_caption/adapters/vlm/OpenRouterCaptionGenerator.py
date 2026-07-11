import base64
import json
import httpx
from vision_caption.core.domain.frame import Frame
from vision_caption.core.ports.CaptionGeneratorPort import CaptionGeneratorPort

class OpenRouterCaptionGenerator(CaptionGeneratorPort):
    def __init__(
        self, 
        api_key: str, 
        model_name: str = "google/gemini-2.5-flash",
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        self._api_key = api_key
        self._model_name = model_name
        self._base_url = base_url

    async def generate(self, frame: Frame):
        # Convertiamo i byte JPEG in formato Base64 per la trasmissione HTTP
        base64_image = base64.b64encode(frame.image_bytes).decode("utf-8")
        
        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/vision-caption",  # Tracciamento opzionale richiesto da OpenRouter
            "X-Title": "Vision Caption Server"
        }
        
        # Struttura del payload
        payload = {
            "model": self._model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Sei una guida per una persona non vedente. Descrivi la scena in UNA sola frase "
                                "breve (massimo 20 parole), diretta e concreta.\n"
                                "REGOLE FONDAMENTALI:\n"
                                "- Descrivi SOLO ciò che vedi con certezza. Se un dettaglio non è chiaro, "
                                "NON indovinare e NON menzionarlo.\n"
                                "- Se non sei sicuro del tipo di un oggetto, usa un termine generico "
                                "(es. 'occhiali' invece di 'occhiali da sole', 'accessorio al collo' invece di 'collare').\n"
                                "- Se non riconosci con certezza l'ambiente, non nominarlo: descrivi solo gli elementi visibili.\n"
                                "- Niente elenchi, markdown o intestazioni. Solo testo semplice in ITALIANO."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 80,
            "temperature": 0.1
        }

        payload["stream"] = True
        
        async with httpx.AsyncClient() as client:
            # Apriamo uno stream continuo con .stream()
            async with client.stream("POST", url, headers=headers, json=payload, timeout=120.0) as response:
                response.raise_for_status()
                
                buffer = ""
                
                # Leggiamo il flusso riga per riga man mano che i token arrivano via rete
                async for line in response.aiter_lines():
                    line = line.strip()
                    
                    if not line:
                        continue
                        
                    if line == "data: [DONE]":
                        break
                        
                    if line.startswith("data: "):
                        json_str = line[6:] 
                        
                        try:
                            data_chunk = json.loads(json_str)
                            choices = data_chunk.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                if "content" in delta:
                                    frammento = delta["content"]

                                    buffer += frammento

                                    # CHUNKING
                                    if "." in buffer or "," in buffer or "?" in buffer or "!" in buffer:
                                        yield buffer.strip()
                                        buffer = ""
                                    
                        except json.JSONDecodeError:
                            continue
                            
                # Alla fine del ciclo, restituiamo l'ultimo pezzo rimasto
                if buffer.strip():
                    yield buffer.strip()
