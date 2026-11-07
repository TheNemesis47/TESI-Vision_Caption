"""Ristima le pose nei JPEG conservati, senza inventare frame o tentativi persi.

uv run python scripts/rigioca_pose_sample.py --model /path/hand_landmarker.task
Usa il modello e le soglie MediaPipe della sessione UICI, un estimatore nuovo
per immagine: questa è una stima statica ex post, non il tracking originale.
"""
import argparse
import asyncio
import json
from pathlib import Path

from vision_caption.adapters.hand_tracking.mediapipe_hand_pose_estimator import MediaPipeHandPoseEstimator, MediaPipeHandPoseSettings
from vision_caption.core.domain.frame import Frame, CaptionMode
from vision_caption.core.services.pointing.gesture_recognizer import GestureRecognizerSettings, pose_rejection_reason
from vision_caption.core.services.pointing.pointing_geometry import calculate_finger_angles, calculate_pointing_vector, calculate_thumb_palm_ratio, project_vector_to_frame


async def main(args):
    rows = []
    for session in args.sessions:
        for metadata in sorted((args.samples/session).glob('*/caption.json')):
            if args.select and metadata.parent.name not in args.select:
                continue
            saved = json.loads(metadata.read_text())
            mode = saved['mode']
            if mode != 'POINTING' and not args.include_auto:
                continue
            path = metadata.parent/('03_clean.jpg' if mode == 'POINTING' else 'frame.jpg')
            estimator = MediaPipeHandPoseEstimator(MediaPipeHandPoseSettings(
                model_path=args.model, min_hand_detection_confidence=args.hand_confidence,
                min_hand_presence_confidence=args.hand_confidence, min_tracking_confidence=args.hand_confidence,
            ))
            try:
                result = await estimator.estimate(Frame(frame_id=saved['frame_id'], image_bytes=path.read_bytes(), caption_mode=CaptionMode(mode)))
                row = {'sample': f'{session}/{metadata.parent.name}', 'original_mode': mode,
                    'original_outcome': saved['outcome'], 'hands': []}
                for hand in result.hands:
                    angles = calculate_finger_angles(hand.world_landmarks)
                    ratio = calculate_thumb_palm_ratio(hand.world_landmarks)
                    vector = calculate_pointing_vector(hand.image_landmarks)
                    ray = project_vector_to_frame(vector) if vector else None
                    reason = 'invalid_ray' if ray is None else pose_rejection_reason(angles, ratio, active=False, settings=GestureRecognizerSettings())
                    row['hands'].append({'handedness': hand.handedness.value,
                        'angles': {name: {'pip': value.pip,'dip': value.dip,'extension': value.extension} for name,value in angles.items()},
                        'thumb_palm_ratio': ratio, 'rejection': reason, 'ray': ray.model_dump(mode='json') if ray else None,
                        'landmarks': hand.model_dump(mode='json')})
                rows.append(row)
                print(row['sample'], 'no_hand' if not row['hands'] else [(h['handedness'], h['rejection'], {k:round(v['extension'],1) for k,v in h['angles'].items()}) for h in row['hands']],flush=True)
            finally:
                await estimator.close()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.with_suffix('.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    lines=['# Pose ristimate sui sample reali', '',
        f'Stime statiche ex post, modello MediaPipe del Dockerfile e confidence {args.hand_confidence}. Gli angoli sono in gradi, estensione=min(PIP,DIP). ',
        'Non sono gli angoli originali filtrati e non ricostruiscono i frame non conservati. Una posa valida in AUTO non può attivare POINTING. ',
        'no_hand su una foto non dimostra che il tracking video originale non vedesse la mano.', '',
        '| Sample | Modalità originale | Mano | Indice | Medio | Anulare | Mignolo | Pollice/palmo | Rifiuto statico |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in rows:
        for h in r['hands'] or [None]:
            values=[r['sample'],r['original_mode']]
            values+=([h['handedness'],*[round(h['angles'][f]['extension'],1) for f in ('INDICE','MEDIO','ANULARE','MIGNOLO')],round(h['thumb_palm_ratio'],3),h['rejection'] or 'posa valida'] if h else ['—']*6+['no_hand'])
            lines.append('| '+' | '.join(map(str,values))+' |')
    args.output.write_text('\n'.join(lines)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--samples',type=Path,default=Path('artifacts/samples'))
    parser.add_argument('--sessions',nargs='+',default=['4946323addfd','117841ba5147','58d49bcef649'])
    parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--include-auto',action='store_true')
    parser.add_argument('--select',nargs='+')
    parser.add_argument('--hand-confidence',type=float,default=.5)
    parser.add_argument('--output',type=Path,default=Path('Docs/pose_sample_uici.md'))
    asyncio.run(main(parser.parse_args()))
