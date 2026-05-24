import base64
import httpx
from vision_caption.core.domain.frame import Frame
from vision_caption.core.ports.CaptionGeneratorPort import CaptionGeneratorPort

class OpenRouterCaptionGenerator(CaptionGeneratorPort):
    def __init__(
        self, 
        api_key: str, 
        model_name: str = "google/gemma-4-26b-a4b-it", 
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        self._api_key = api_key
        self._model_name = model_name
        self._base_url = base_url

    async def generate(self, frame: Frame) -> str:
        # Convertiamo i byte JPEG in formato Base64 per la trasmissione HTTP
        base64_image = base64.b64encode(frame.image_bytes).decode("utf-8")
        
        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/vision-caption",  # Tracciamento opzionale richiesto da OpenRouter
            "X-Title": "Vision Caption Server"
        }
        
        # Struttura del payload multimodale standard (compatibile OpenAI)
        payload = {
            "model": self._model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Descrivi brevemente e in italiano l'ambiente, indicando gli ostacoli o gli oggetti principali per una persona non vedente."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            # Invio della chiamata POST a OpenRouter
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            
        # Estrazione del testo generato dalla risposta
        choices = result.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "").strip()
            return content
            
        return "Non è stato possibile ottenere una descrizione dell'ambiente."
