"""Rigioca i sample POINTING attraverso l'adapter di produzione, incluso il recupero.

Usa i raggi originali del research log e le tre immagini conservate. Non
ricostruisce le mani dei frame persi e non chiama TTS. Qwen via OpenRouter
non equivale al modello quantizzato eseguito da Ollama sulla macchina della prof.
"""

import argparse
import asyncio
import json
from pathlib import Path
from time import perf_counter

from benchmark_vlm import _load_key_from_dotenv
from regressione_uici import cases
from summarize_research_log import load
from vision_caption.adapters.vlm.OpenRouterPointingCaptionGenerator import OpenRouterPointingCaptionGenerator
from vision_caption.core.services.pointing.pointing_pipeline import CLOSER_VIEW_PROMPT, REPOINT_PROMPT, compose_lesson_caption


class MeasuredGenerator(OpenRouterPointingCaptionGenerator):
    """Registra le risposte ricevute senza cambiare prompt, trasporto o retry."""

    async def _request(self, payload, headers):
        started = perf_counter()
        response = await super()._request(payload, headers)
        self.attempts.append({
            'elapsed_ms': round((perf_counter()-started)*1000, 1),
            'choices': response.get('choices'),
            'usage': response.get('usage'),
        })
        return response


async def main(args):
    key = _load_key_from_dotenv()
    if not key:
        raise SystemExit('OPENROUTER_API_KEY assente da .env')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for log in args.logs:
        events = load(log)
        session = events[0]['session_id']
        options = argparse.Namespace(samples=args.samples/session, select=None, pdf=None)
        items = [item for item in cases(options, events) if item['mode']=='POINTING']
        for model in args.models:
            generator = MeasuredGenerator(api_key=key, model_name=model,
                context='lesson', json_mode='qwen' not in model,
                retry_empty_response=not args.no_retry)
            for repeat in range(1, args.repeat+1):
                for item in items:
                    generator.attempts = []
                    row = {'session':session, 'case':item['name'], 'model':model,
                        'repeat':repeat, 'memory':args.memory,
                        'ray_provenance':'original_research_log',
                        'event':item['event'].model_dump(mode='json'),
                        'historical':item['saved'], 'retry_enabled':not args.no_retry}
                    started = perf_counter()
                    try:
                        caption = await generator.generate(item['event'], item['images'],
                            item['saved'].get('memory_context') if args.memory=='recorded' else None)
                        row['caption'] = caption.model_dump(mode='json') if caption else None
                        if caption and caption.needs_closer_view:
                            row['outcome'], row['spoken'] = 'needs_closer_view', CLOSER_VIEW_PROMPT
                        elif caption and caption.needs_repointing:
                            row['outcome'], row['spoken'] = 'needs_repointing', REPOINT_PROMPT
                        else:
                            speech = compose_lesson_caption(caption) if caption else None
                            row['outcome'] = 'spoken' if speech else 'empty_caption'
                            row['spoken'] = speech or REPOINT_PROMPT
                    except Exception as error:
                        row.update(error=type(error).__name__, outcome='vlm_error', spoken=REPOINT_PROMPT)
                    row.update(vlm_ms=round((perf_counter()-started)*1000,1), attempts=generator.attempts)
                    rows.append(row)
                    args.output.write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in rows))
                    print(session,item['name'],model,repeat,row['outcome'],row['vlm_ms'],row['spoken'],flush=True)
    lines = ['# Replay dei puntamenti con adapter di produzione', '',
        'Raggi originali; immagini e memoria registrate. Non misura TTS o primo audio. ',
        'La variante Qwen cloud non riproduce la quantizzazione, il server e la GPU di Ollama. ',
        'Un messaggio di ripuntamento è un riscontro, non un riconoscimento riuscito.', '',
        '| Sessione / frame / replica | Modello | Storico | Dopo | Esito | VLM ms | Chiamate |',
        '| --- | --- | --- | --- | --- | --- | --- |']
    for row in rows:
        values = [f"{row['session']} / {row['case']} / {row['repeat']}",row['model'],
            row['historical']['outcome'],row['spoken'],row['outcome'],row['vlm_ms'],len(row['attempts'])]
        lines.append('| '+' | '.join(str(value).replace('|','\\|').replace('\n','<br>') for value in values)+' |')
    args.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('logs',nargs='+',type=Path)
    parser.add_argument('--samples',type=Path,default=Path('artifacts/samples'))
    parser.add_argument('--models',nargs='+',default=['qwen/qwen3-vl-8b-instruct','google/gemini-2.5-flash'])
    parser.add_argument('--repeat',type=int,default=3)
    parser.add_argument('--memory',choices=['recorded','none'],default='recorded')
    parser.add_argument('--no-retry',action='store_true')
    parser.add_argument('--output',type=Path,default=Path('Docs/replay_puntamenti_adapter.jsonl'))
    asyncio.run(main(parser.parse_args()))
