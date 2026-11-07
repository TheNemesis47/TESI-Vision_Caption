"""Confronta l'attivazione reale MediaPipe con/senza recupero specchiato.

Ogni JPEG viene mantenuto per cinque osservazioni simulate a 0,21 s.
Non è il replay dei frame perduti: misura la stessa posa statica e il costo
locale di stima. VLM e TTS sono simulati, non si misurano le descrizioni.
"""
import argparse
import asyncio
import json
from dataclasses import replace
from pathlib import Path

from vision_caption.adapters.hand_tracking.mediapipe_hand_pose_estimator import MediaPipeHandPoseEstimator,MediaPipeHandPoseSettings
from vision_caption.core.domain.frame import Frame,CaptionMode
from vision_caption.core.domain.audio import Audio,AudioFormat
from vision_caption.core.domain.pointing_caption import PointingCaption
from vision_caption.core.ports.pointing_image_preparer_port import PointingImages
from vision_caption.core.services.pointing.gesture_recognizer import PointingGestureRecognizer
from vision_caption.core.services.pointing.pointing_event_gate import PointingEventGate
from vision_caption.core.services.pointing.pointing_pipeline import PointingPipeline


class Recorder:
    def __init__(self):self.events=[]
    def record(self,event,**fields):self.events.append({'event':event,**fields})


class Preparer:
    async def prepare(self,frame,event):return PointingImages(b'',b'',b'')


class Caption:
    async def generate(self,*args):
        return PointingCaption(target='segnaposto del benchmark',description='Risposta simulata.',visible_text=None,text_confidence=0,text_complete=False,confidence=1,needs_repointing=False,needs_closer_view=False)


class Speech:
    async def synthesize(self,*args):return Audio(audio_format=AudioFormat.WAV,audio_bytes=b'',audio_duration=0)


async def main(args):
    rows=[]
    config=MediaPipeHandPoseSettings(args.model,min_hand_detection_confidence=.5,min_hand_presence_confidence=.5,min_tracking_confidence=.5)
    for session in args.sessions:
        for metadata in sorted((args.samples/session).glob('*/caption.json')):
            name=metadata.parent.name
            if not name.startswith('pointing') and name not in args.extra:
                continue
            path=metadata.parent/('03_clean.jpg' if name.startswith('pointing') else 'frame.jpg')
            for enabled in (False,True):
                recorder=Recorder();clock=[0.0]
                pipeline=PointingPipeline(
                    MediaPipeHandPoseEstimator(config),PointingGestureRecognizer(),PointingEventGate(2),Preparer(),Caption(),Speech(),
                    clock=lambda:clock[0],research_recorder=recorder,diagnostics_enabled=True,
                    recovery_pose_estimator=MediaPipeHandPoseEstimator(replace(config,mirror_input=True,static_image_mode=True)) if enabled else None,
                )
                try:
                    for step in range(5):
                        clock[0]=step*.21
                        frame=Frame(frame_id=step,image_bytes=path.read_bytes(),caption_mode=CaptionMode.POINTING)
                        _=[result async for result in pipeline.process(frame)]
                    acts=[e for e in recorder.events if e['event']=='pointing_activation']
                    row={'sample':f'{session}/{name}','mirror_recovery':enabled,'activation_count':len(acts),'activations':acts,'events':recorder.events}
                    rows.append(row)
                    print(row['sample'],enabled,'attivazioni',len(acts),'raggio',acts[0].get('ray') if acts else None,flush=True)
                    args.output.parent.mkdir(parents=True,exist_ok=True)
                    args.output.write_text(json.dumps(rows,ensure_ascii=False,indent=2))
                finally:await pipeline.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--samples',type=Path,default=Path('artifacts/samples'))
    parser.add_argument('--sessions',nargs='+',default=['4946323addfd','117841ba5147','58d49bcef649','dbb46cf33e38'])
    parser.add_argument('--extra',nargs='*',default=['auto_000001','auto_000843','auto_000857'])
    parser.add_argument('--output',type=Path,default=Path('Docs/benchmark_pointing_recovery.json'))
    asyncio.run(main(parser.parse_args()))
