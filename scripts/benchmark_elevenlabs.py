"""Misura ElevenLabs attuale vs v4 Turbo sullo stesso testo italiano.

uv run python scripts/benchmark_elevenlabs.py --repeat 3
Il primo chunk v4 è misurato dal client dopo handshake, non è TTFA sul telefono.
La porta applicativa restituisce ancora l'MP3 completo.
"""
import argparse
import asyncio
import json
import os
import time
from pathlib import Path
from statistics import median

from vision_caption.adapters.tts.ElevenLabsSynthesizer import ElevenLabsSynthesizer


def dotenv():
    values = {}
    source = Path(__file__).resolve().parents[1]/'.env'
    if source.exists():
        for line in source.read_text().splitlines():
            key, sep, value = line.strip().partition('=')
            if sep and not key.startswith('#'):
                values[key] = value.strip().strip('"').strip("'")
    return {**values, **os.environ}


async def main(args):
    env = dotenv()
    key = env.get('ELEVENLABS_API_KEY')
    if not key:
        raise SystemExit('ELEVENLABS_API_KEY assente in .env/ambiente')
    voice = env.get('ELEVENLABS_VOICE_ID','21m00Tcm4TlvDq8ikWAM')
    texts = [
        'Un visore pesa circa cinquecento grammi.',
        'Entrare in una stanza virtuale. Un visore pesa circa cinquecento grammi. Immagine: un tavolo nero, quattro sedie rosse e un armadio blu.',
        'Non solo divertimento. Progetto Girasole. Immagine: un uomo con cuffie nere gioca con un controller nero.',
    ]
    args.output.mkdir(parents=True,exist_ok=True)
    rows=[]
    for repeat in range(1,args.repeat+1):
        for index,text in enumerate(texts,1):
            for model in args.models:
                metrics=[]
                started=time.perf_counter()
                row={'model':model,'text':text,'case':index,'repeat':repeat,'voice_id':voice}
                try:
                    synth=ElevenLabsSynthesizer(key,voice,model,timeout_seconds=30,metrics_callback=metrics.append)
                    audio=await synth.synthesize(text)
                    row.update(metrics[0])
                    row.update(bytes=len(audio.audio_bytes),estimated_audio_seconds=audio.audio_duration)
                    row['audio']=f'{model}_{index}_{repeat}.mp3'
                    (args.output/row['audio']).write_bytes(audio.audio_bytes)
                except Exception as error:
                    row['error']=type(error).__name__
                    if hasattr(error,'response'):
                        response=error.response
                        row['http_status']=getattr(response,'status_code',getattr(response,'status',None))
                    row['elapsed_ms']=round((time.perf_counter()-started)*1000,1)
                rows.append(row)
                print(model,index,repeat,{k:v for k,v in row.items() if k not in ('text','voice_id')},flush=True)
                (args.output/'metrics.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    lines=['# Confronto ElevenLabs su testo italiano', '',
        'v4 Turbo usa il WebSocket Text to Dialogue. first_chunk_ms include handshake e rete dal Mac; total_ms è il tempo prima che la porta restituisca l’MP3 completo. ',
        'HTTP v2.5 attuale è bufferizzato: il suo primo chunk non è misurato. Nessuna misura è l’inizio della voce sul telefono. La durata audio è stimata come nel server, non misurata.', '',
        '| Modello | Caso | Replica | Primo chunk ms | Audio completo ms | Errore |',
        '| --- | --- | --- | --- | --- | --- |']
    for r in rows:
        lines.append('| '+' | '.join(str(r.get(k,'—')) for k in ('model','case','repeat','first_chunk_ms','total_ms','error'))+' |')
    for model in args.models:
        good=[r for r in rows if r['model']==model and 'total_ms' in r]
        if good:
            lines += ['',f"{model}: n={len(good)}, mediana audio completo {median(r['total_ms'] for r in good):.1f} ms."]
    (args.output/'confronto.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repeat',type=int,default=3)
    parser.add_argument('--models',nargs='+',default=['eleven_turbo_v2_5','eleven_v4_turbo'])
    parser.add_argument('--output',type=Path,default=Path('Docs/benchmark_elevenlabs'))
    args=parser.parse_args()
    asyncio.run(main(args))
