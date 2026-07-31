"""
Benchmark di modelli VLM su OpenRouter per il captioning.

Uso:
    OPENROUTER_API_KEY=... python scripts/benchmark_vlm.py path/immagine.jpg

Prova una lista di modelli veloci con visione sullo stesso prompt/immagine
e stampa latenza + caption, così puoi scegliere il piu preciso.
"""
import asyncio
import base64
import os
import sys
import time

import httpx

# Modelli candidati: veloci, economici, con supporto immagini.
MODELS = [
    "google/gemini-2.5-flash",
    "google/gemini-2.0-flash-001",
    "openai/gpt-4o-mini",
    "qwen/qwen-2.5-vl-7b-instruct",
    "meta-llama/llama-3.2-11b-vision-instruct",  # quello attuale, come riferimento
]

PROMPT = (
    "Sei una guida per una persona non vedente. Descrivi la scena in UNA sola frase "
    "breve (massimo 20 parole), diretta e concreta.\n"
    "REGOLE FONDAMENTALI:\n"
    "- Descrivi SOLO cio che vedi con certezza. Se un dettaglio non e chiaro, "
    "NON indovinare e NON menzionarlo.\n"
    "- Se non sei sicuro del tipo di un oggetto, usa un termine generico "
    "(es. 'occhiali' invece di 'occhiali da sole', 'accessorio al collo' invece di 'collare').\n"
    "- Se non riconosci con certezza l'ambiente, non nominarlo: descrivi solo gli elementi visibili.\n"
    "- Niente elenchi, markdown o intestazioni. Solo testo semplice in ITALIANO."
)


def _load_key_from_dotenv():
    """Legge OPENROUTER_API_KEY dal file .env nella root del progetto."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(root, ".env")
    if not os.path.exists(env_path):
        return None
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY"):
                _, _, value = line.partition("=")
                return value.strip().strip('"').strip("'")
    return None


async def run_model(client, api_key, model, b64, mime):
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                ],
            }
        ],
        "max_tokens": 80,
        "temperature": 0.1,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    t0 = time.perf_counter()
    try:
        r = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60.0,
        )
        dt = time.perf_counter() - t0
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        return model, dt, text
    except Exception as e:  # noqa: BLE001
        return model, time.perf_counter() - t0, f"ERRORE: {e}"


async def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/benchmark_vlm.py path/immagine.jpg")
        sys.exit(1)

    api_key = os.environ.get("OPENROUTER_API_KEY") or _load_key_from_dotenv()
    if not api_key:
        print("Imposta OPENROUTER_API_KEY nell'ambiente o nel file .env.")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    mime = "image/png" if sys.argv[1].lower().endswith(".png") else "image/jpeg"

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *(run_model(client, api_key, m, b64, mime) for m in MODELS)
        )

    print(f"\nImmagine: {sys.argv[1]}\n" + "=" * 70)
    for model, dt, text in sorted(results, key=lambda x: x[1]):
        print(f"\n[{dt:5.2f}s] {model}\n  -> {text}")


if __name__ == "__main__":
    asyncio.run(main())
