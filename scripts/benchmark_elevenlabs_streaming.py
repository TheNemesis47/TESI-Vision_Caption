"""Confronto del primo audio: stessi testi, voce, PCM 24 kHz e WebSocket.

Il primo warm-up per modello è separato. Si misurano handshake, primo chunk
prima/dopo handshake, fine audio e durata PCM reale. Nessuna misura esclude
la rete del client o misura la riproduzione sul telefono.
"""
import argparse
import asyncio
import base64
import json
from pathlib import Path
from statistics import median
from time import perf_counter
from urllib.parse import urlencode
from websockets.asyncio.client import connect
from benchmark_elevenlabs import dotenv

TEXTS=[
    'Un visore pesa circa cinquecento grammi.',
    'Entrare in una stanza virtuale. Un visore pesa circa cinquecento grammi. Immagine: un tavolo nero, quattro sedie rosse e un armadio blu.',
    'Non solo divertimento. Progetto Girasole. Immagine: un uomo con cuffie nere gioca con un controller nero.',
]


async def request(model,text,key,voice):
    dialogue=model=='eleven_v4_turbo'
    endpoint='text-to-dialogue/stream-input' if dialogue else f'text-to-speech/{voice}/stream-input'
    query=urlencode({'model_id':model,'output_format':'pcm_24000','language_code':'it'})
    row={'model':model,'text':text,'format':'pcm_24000'}
    started=perf_counter();pcm=[];first=None
    async with asyncio.timeout(30):
        async with connect(f'wss://api.elevenlabs.io/v1/{endpoint}?{query}',additional_headers={'xi-api-key':key}) as socket:
            connected=perf_counter()
            row['handshake_ms']=round((connected-started)*1000,1)
            await socket.send(json.dumps({'voices':[voice]} if dialogue else {'text':' '}))
            submitted=perf_counter()
            if dialogue:
                await socket.send(json.dumps({'inputs':[{'text':text,'voice_id':voice}]}))
                await socket.send(json.dumps({'close_socket':True}))
            else:
                await socket.send(json.dumps({'text':text+' ','flush':True}))
                await socket.send(json.dumps({'text':''}))
            async for raw in socket:
                message=json.loads(raw)
                if message.get('error') or message.get('error_type'):
                    raise RuntimeError('ElevenLabs ha rifiutato la sintesi streaming')
                if message.get('audio'):
                    chunk=base64.b64decode(message['audio'],validate=True)
                    if chunk:
                        if first is None:first=perf_counter()
                        pcm.append(chunk)
                if message.get('is_final') or message.get('isFinal'):break
            ended=perf_counter()
    if first is None:raise RuntimeError('Nessun audio')
    row.update(first_chunk_after_connect_ms=round((first-submitted)*1000,1),
        first_chunk_including_connect_ms=round((first-started)*1000,1),
        audio_complete_after_connect_ms=round((ended-submitted)*1000,1),
        measured_duration_s=round(sum(map(len,pcm))/48000,3))
    return row


async def main(args):
    env=dotenv();key=env.get('ELEVENLABS_API_KEY');voice=env.get('ELEVENLABS_VOICE_ID','21m00Tcm4TlvDq8ikWAM')
    if not key:raise SystemExit('ELEVENLABS_API_KEY assente')
    args.output.parent.mkdir(parents=True,exist_ok=True);rows=[]
    for model in args.models:
        warmup=await request(model,TEXTS[0],key,voice);warmup.update(warmup=True,case=1,repeat=0);rows.append(warmup)
        for repeat in range(1,args.repeat+1):
            for index,text in enumerate(TEXTS,1):
                row=await request(model,text,key,voice);row.update(warmup=False,case=index,repeat=repeat);rows.append(row)
                args.output.write_text(json.dumps(rows,ensure_ascii=False,indent=2))
                print(model,index,repeat,{k:v for k,v in row.items() if k.endswith('_ms')},flush=True)
    lines=['# Confronto ElevenLabs del primo audio in streaming', '',
        'Stessa voce, testi italiani e PCM 24 kHz mono. Warm-up escluso dalle mediane. ',
        'Il timer dopo handshake parte prima di inviare il testo; include ancora rete, servizio e consegna del primo chunk. ',
        'Ogni richiesta apre una connessione; il tempo di apertura è misurato separatamente. Il client VisionCaption attuale attende invece il clip completo. ',
        'I 100 ms ufficiali sono una mediana lato server; i dati qui sono tempi dal Mac, non TTFA sul telefono.', '',
        '| Modello | n | Mediana primo chunk dopo apertura ms | Mediana primo chunk con apertura ms | Mediana audio completo dopo apertura ms |',
        '| --- | --- | --- | --- | --- |']
    for model in args.models:
        rs=[r for r in rows if r['model']==model and not r['warmup']]
        if rs:
            vals=[model,len(rs),*[round(median(r[k] for r in rs),1) for k in ('first_chunk_after_connect_ms','first_chunk_including_connect_ms','audio_complete_after_connect_ms')]]
            lines.append('| '+' | '.join(map(str,vals))+' |')
    args.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models',nargs='+',default=['eleven_turbo_v2_5','eleven_flash_v2_5','eleven_v4_turbo'])
    parser.add_argument('--repeat',type=int,default=3)
    parser.add_argument('--output',type=Path,default=Path('Docs/benchmark_elevenlabs_streaming.json'))
    asyncio.run(main(parser.parse_args()))
