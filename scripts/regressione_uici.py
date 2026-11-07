"""Confronta prompt e composizione prima/dopo sui sample UICI e sulle slide PDF.

Offline: uv run python scripts/regressione_uici.py --offline
Con VLM: uv run python scripts/regressione_uici.py --pdf 'artifacts/...pdf'
Il PDF richiede PyMuPDF opzionale: uv run --with pymupdf python scripts/regressione_uici.py ...
La chiave viene letta da OPENROUTER_API_KEY o da .env, mai scritta nei risultati.
"""

import argparse
import asyncio
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from statistics import median

import httpx

from benchmark_vlm import _load_key_from_dotenv
from summarize_research_log import load
from vision_caption.adapters.vlm.OpenRouterCaptionGenerator import OpenRouterCaptionGenerator
from vision_caption.adapters.vlm.OpenRouterPointingCaptionGenerator import build_pointing_payload, parse_pointing_caption
from vision_caption.adapters.vlm.prompts import auto_prompt
from vision_caption.core.domain.frame import CaptionMode, Frame
from vision_caption.core.domain.pointing import PointingEvent
from vision_caption.core.domain.pointing_caption import PointingCaption
from vision_caption.core.ports.pointing_image_preparer_port import PointingImages
from vision_caption.core.services.lesson_memory import LessonMemory, split_page_tag
from vision_caption.core.services.pointing.pointing_pipeline import compose_lesson_caption
from vision_caption.core.services.speech_text import lesson_speech

ROOT = Path(__file__).resolve().parents[1]


def revision_module(revision, relative):
    source = subprocess.check_output(['git', 'show', f'{revision}:src/vision_caption/{relative}'], cwd=ROOT, text=True)
    namespace = {'__name__': '_regression_baseline'}
    exec(compile(source, f'{revision}:{relative}', 'exec'), namespace)
    return namespace


def markdown(rows, path):
    def esc(value):
        return str(value if value is not None else '—').replace('|', '\\|').replace('\n', '<br>')
    lines = ['# Regressione UICI: risposte reali prima e dopo', '',
        'Il precedente storico è il testo salvato nella sessione locale Qwen; prima/dopo controllati usano lo stesso modello e la stessa immagine. ',
        'I tempi VLM includono rete e generazione; parole/s è il rapporto parole generate / tempo totale, non la velocità di decodifica del provider. ',
        'AUTO usa lo stesso adapter streaming del server, che emette un unico chunk completo: il primo chunk coincide con la fine della risposta. ',
        'Non viene chiamato il TTS: questi tempi NON sono latenza del primo audio. NIENTE con memoria può essere una soppressione corretta. ',
        'Il replay offline del POINTING ricompone i soli risultati salvati: non ricostruisce landmark o gesti mancanti.', '',
        '| Caso / replica / memoria | Storico della prof | Prima controllato | Dopo | Tempi VLM prima/dopo ms | Parole/s prima/dopo |',
        '| --- | --- | --- | --- | --- | --- |']
    grouped = {}
    for row in rows:
        grouped.setdefault((row['case'], row['repeat'], row['memory']), {})[row['stage']] = row
    for key, stages in grouped.items():
        before, after = stages.get('before', {}), stages.get('after', {})
        any_row = after or before
        lines.append('| ' + ' | '.join(map(esc, [f'{key[0]} / {key[1]} / {key[2]}', any_row.get('historical'),
            before.get('spoken', before.get('error')), after.get('spoken', after.get('error')),
            f"{before.get('vlm_ms', '—')} / {after.get('vlm_ms', '—')}",
            f"{before.get('words_per_s', '—')} / {after.get('words_per_s', '—')}"])) + ' |')
    for stage in ('before', 'after'):
        good = [r for r in rows if r['stage'] == stage and r.get('vlm_ms') is not None]
        times = sorted(r['vlm_ms'] for r in good)
        if times:
            rank = (len(times) - 1) * .95
            lo = int(rank)
            p95 = times[lo] + (times[min(lo+1, len(times)-1)] - times[lo])*(rank-lo)
            lines += ['', f"{stage}: n={len(times)}, mediana={median(times):.1f} ms, p95={p95:.1f} ms; errori={sum(r['stage']==stage and 'error' in r for r in rows)}."]
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def cases(args, events):
    result = []
    activations = {e['frame_id']: e for e in events if e['event'] == 'pointing_activation'}
    for metadata in sorted(args.samples.glob('*/caption.json')):
        name = metadata.parent.name
        if args.select and name not in args.select:
            continue
        saved = json.loads(metadata.read_text())
        mode = saved['mode']
        historical = saved.get('text') or '\n'.join(c['text'] + ('' if c['spoken'] else ' [non detto]') for c in saved.get('captions', []))
        case = {'name': name, 'mode': mode, 'saved': saved, 'historical': historical}
        if mode == 'AUTO':
            case['image'] = (metadata.parent/'frame.jpg').read_bytes()
        else:
            activation = activations[saved['frame_id']]
            if not saved.get('memory_context'):
                # I vecchi sample POINTING omettono il contesto. La memoria
                # condivisa si ricostruisce dalle utterance AUTO precedenti.
                memory = LessonMemory(clock=lambda: 0.0)
                described = {e['frame_id']:e for e in events if e['event']=='slide_described'}
                for utterance in events:
                    if utterance['t'] >= activation['t']:
                        break
                    note = described.get(utterance.get('frame_id'))
                    if utterance['event']=='utterance' and utterance.get('mode')=='AUTO' and note:
                        memory.remember(note.get('page'),note.get('total'),utterance['text'])
                saved['memory_context'] = memory.context()
                case['memory_origin'] = 'reconstructed_from_auto_utterances'
            case['event'] = PointingEvent(frame_id=saved['frame_id'], handedness=activation['handedness'], ray=activation['ray'])
            case['images'] = PointingImages(*[(metadata.parent/p).read_bytes() for p in ('01_context.jpg','02_focus.jpg','03_clean.jpg')])
        result.append(case)
    if args.pdf:
        try:
            import pymupdf
        except ImportError:
            raise SystemExit('PDF: installare PyMuPDF opzionale con uv run --with pymupdf python scripts/regressione_uici.py ...')
        with pymupdf.open(args.pdf) as doc:
            for i, page in enumerate(doc):
                pix = page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5))
                result.append({'name': f'pdf_pagina_{i+1}', 'mode': 'AUTO', 'image': pix.tobytes('jpeg'), 'saved': {}, 'historical': 'Vedi ground truth PDF; nessuna generazione storica su questo rendering.'})
    return result


async def main(args):
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.recompose_source:
        # Stesse risposte e stessi tempi del provider; verifica deterministica
        # del filtro vocale corrente senza spendere altre chiamate API.
        rows = load(args.recompose_source)
        prepare = lesson_speech(50)
        for row in rows:
            if row['stage'] != 'after' or 'error' in row:
                continue
            if row['mode'] == 'AUTO':
                _, _, body = split_page_tag(row['raw'])
            else:
                caption = parse_pointing_caption(row['raw'])
                body = compose_lesson_caption(caption) if caption else None
                body = body or 'Non capisco cosa stai indicando. Prova a puntare di nuovo.'
            row['spoken'] = prepare(body)
            row['recomposed_without_vlm'] = True
        args.output.with_suffix('.jsonl').write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in rows))
        markdown(rows,args.output)
        print(f'Ricomposte {len(rows)} risposte senza nuove chiamate VLM: {args.output}')
        return
    events = load(args.log)
    old_prompts = revision_module(args.before_revision, 'adapters/vlm/prompts.py')
    old_auto = revision_module(args.before_revision, 'adapters/vlm/OpenRouterCaptionGenerator.py')['OpenRouterCaptionGenerator']
    old_speech = revision_module(args.before_revision, 'core/services/speech_text.py')['lesson_speech'](50)
    old_pointing = revision_module(args.before_revision, 'core/services/pointing/pointing_pipeline.py')['compose_lesson_caption']
    old_adapter = revision_module(args.before_revision, 'adapters/vlm/OpenRouterPointingCaptionGenerator.py')
    old_adapter['pointing_context'] = old_prompts['pointing_context']
    items = cases(args, events)
    key = os.environ.get('OPENROUTER_API_KEY') or _load_key_from_dotenv()
    if not args.offline and not key:
        raise SystemExit('Chiave OpenRouter assente: impostare OPENROUTER_API_KEY in .env o usare --offline.')
    rows = []
    semaphore = asyncio.Semaphore(args.concurrency)
    request_lock = asyncio.Lock()
    next_request = 0.0
    raw_path = args.output.with_suffix('.jsonl')

    async def run(case, stage, repeat):
        nonlocal next_request
        async with semaphore:
            prepare = old_speech if stage == 'before' else lesson_speech(50)
            memory = case['saved'].get('memory_context') if args.memory == 'recorded' else None
            row = {'case': case['name'], 'repeat': repeat, 'stage': stage, 'memory': args.memory,
                'historical': case['historical'], 'model': args.model, 'baseline_revision': args.before_revision,
                'mode': case['mode'], 'offline': args.offline}
            if case['mode'] == 'AUTO':
                row['max_output_tokens'] = args.auto_max_tokens
            row['memory_origin'] = case.get('memory_origin','saved_sample')
            row['had_memory'] = bool(memory)
            if not args.offline:
                async with request_lock:
                    await asyncio.sleep(max(0, next_request-time.perf_counter()))
                    next_request = time.perf_counter()+args.request_interval
            started = time.perf_counter()
            try:
                if args.offline:
                    if case['mode'] == 'POINTING':
                        caption = PointingCaption.model_validate(case['saved'])
                        row['spoken'] = prepare((old_pointing if stage=='before' else compose_lesson_caption)(caption) or '')
                    else:
                        row['spoken'] = '\n'.join(prepare(c['text']) for c in case['saved'].get('captions', []))
                    row['raw'] = 'Solo ricomposizione; VLM non invocato.'
                elif case['mode'] == 'AUTO':
                    prompt = old_prompts['auto_prompt']('lesson') if stage == 'before' else auto_prompt('lesson')
                    row['prompt_sha256'] = hashlib.sha256(prompt.encode()).hexdigest()
                    generator_class = old_auto if stage == 'before' else OpenRouterCaptionGenerator
                    generator = generator_class(api_key=key, model_name=args.model, base_url=args.base_url,
                        max_tokens=args.auto_max_tokens, temperature=.1, timeout_seconds=120, prompt=prompt)
                    frame = Frame(frame_id=case['saved'].get('frame_id',0), image_bytes=case['image'], caption_mode=CaptionMode.AUTO)
                    chunks = [text async for text in generator.generate(frame, memory)]
                    row['raw'] = '\n'.join(chunks)
                    if not row['raw'].strip():
                        raise ValueError('Risposta AUTO vuota')
                    page, total, body = split_page_tag(row['raw'])
                    row.update(page=page, total=total, spoken=prepare(body))
                else:
                    builder = old_adapter['build_pointing_payload'] if stage == 'before' else build_pointing_payload
                    payload = builder(event=case['event'], images=case['images'], model_name=args.model,
                        max_tokens=1200, temperature=.1, context='lesson', memory=memory)
                    row['prompt_sha256'] = hashlib.sha256(payload['messages'][0]['content'][0]['text'].encode()).hexdigest()
                    async with httpx.AsyncClient() as client:
                        response = await client.post(args.base_url.rstrip('/')+'/chat/completions',
                            headers={'Authorization': f'Bearer {key}'}, json=payload, timeout=120)
                        response.raise_for_status()
                        row['raw'] = response.json()['choices'][0]['message']['content']
                    caption = parse_pointing_caption(row['raw'])
                    if caption is None:
                        raise ValueError('JSON del puntamento non valido')
                    row['caption'] = caption.model_dump(mode='json')
                    row['spoken'] = prepare((old_pointing if stage=='before' else compose_lesson_caption)(caption) or 'Non capisco cosa stai indicando. Prova a puntare di nuovo.')
                    row['needs_repointing'] = caption.needs_repointing
                if not args.offline:
                    row['vlm_ms'] = round((time.perf_counter()-started)*1000,1)
                    row['words_per_s'] = round(len(row['raw'].split())/(row['vlm_ms']/1000),2)
            except Exception as error:
                # Nessun header, chiave o payload immagine nei messaggi d'errore.
                row['error'] = type(error).__name__ + (f' HTTP {error.response.status_code}' if isinstance(error,httpx.HTTPStatusError) else '')
                row['elapsed_ms'] = round((time.perf_counter()-started)*1000,1)
                if isinstance(error, httpx.HTTPStatusError):
                    row['retry_after'] = error.response.headers.get('retry-after')
                    try:
                        details = error.response.json().get('error', {})
                        if isinstance(details, dict):
                            row['error_message'] = str(details.get('message', '')).replace(key or '\x00', '[redacted]')[:400]
                    except (ValueError, AttributeError):
                        pass
            rows.append(row)
            with raw_path.open('a',encoding='utf-8') as target:
                target.write(json.dumps(row,ensure_ascii=False)+'\n')
            markdown(rows, args.output)
            print(f"{case['name']} {stage} #{repeat}: {row.get('vlm_ms',row.get('elapsed_ms','offline'))} ms {row.get('error','OK')}",flush=True)

    # Una nuova esecuzione sostituisce il confronto, mai il dataset originale.
    raw_path.write_text('')
    await asyncio.gather(*(run(case,stage,repeat) for case in items for repeat in range(1,args.repeat+1) for stage in ('before','after')))
    markdown(rows,args.output)
    print(f'Risultati: {args.output} e {raw_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--samples',type=Path,default=ROOT/'artifacts/samples/4946323addfd')
    parser.add_argument('--log',type=Path,default=ROOT/'logs/research/20261106-093842_4946323addfd.jsonl')
    parser.add_argument('--pdf',type=Path)
    parser.add_argument('--select',nargs='+',help='nomi cartelle sample; il PDF, se presente, resta completo')
    parser.add_argument('--model',default='google/gemini-2.5-flash')
    parser.add_argument('--base-url',default='https://openrouter.ai/api/v1')
    parser.add_argument('--before-revision',default='63d9337')
    parser.add_argument('--repeat',type=int,default=1)
    parser.add_argument('--concurrency',type=int,default=2)
    parser.add_argument('--auto-max-tokens',type=int,default=250,
                        help='stesso budget di token AUTO per prima/dopo; deve coprire anche le etichette interne')
    parser.add_argument('--request-interval',type=float,default=0,
                        help='intervallo minimo fra richieste API in secondi; riduce i 429 senza alterare i tempi VLM misurati')
    parser.add_argument('--memory',choices=('none','recorded'),default='none')
    parser.add_argument('--output',type=Path,default=ROOT/'Docs/regressione_uici.md')
    parser.add_argument('--offline',action='store_true')
    parser.add_argument('--recompose-source',type=Path,help='riapplica solo il filtro vocale alle risposte JSONL già misurate')
    arguments=parser.parse_args()
    if arguments.repeat < 1 or arguments.concurrency < 1 or arguments.auto_max_tokens < 1:
        parser.error('repeat, concurrency e auto-max-tokens devono essere positivi')
    if arguments.request_interval < 0:
        parser.error('request-interval non può essere negativo')
    asyncio.run(main(arguments))
