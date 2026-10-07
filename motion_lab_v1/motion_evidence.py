"""A native video must belong to this build, not merely have large dimensions."""
import hashlib,json,math
from pathlib import Path

def validate_capture(report,input_sha,video_sha,script_sha):
    if report.get('kind')!='motion-studio-native-capture':raise ValueError('Missing actual capture metadata')
    if report.get('build',{}).get('inputSHA256')!=input_sha:raise ValueError('Capture is from another build')
    if report.get('videoSHA256')!=video_sha or report.get('captureScriptSHA256')!=script_sha:raise ValueError('Capture bytes or capture script changed')
    if report.get('native')!=[1920,1080] or report.get('pixelUpscaling') is not False:raise ValueError('Capture is not native 1080p')
    samples=report.get('observations',[])
    if len(samples)<60 or samples[-1].get('elapsedMs',0)-samples[0].get('elapsedMs',0)<2000:raise ValueError('Missing timed motion capture')
    if any(type(s.get('elapsedMs')) not in (int,float) or not math.isfinite(s['elapsedMs']) for s in samples):raise ValueError('Invalid capture timestamps')
    if any(b['elapsedMs']<=a['elapsedMs'] for a,b in zip(samples,samples[1:])):raise ValueError('Capture timestamps are not chronological')
    labels={s.get('segment','') for s in samples}
    for direction in ['E','SE','S','SW','W','NW','N','NE']:
        for action in ['walk','run']:
            rows=[s for s in samples if s.get('segment','').startswith(direction+' '+action) and ' / ' not in s.get('segment','')]
            if len({s.get('frame') for s in rows if s.get('amount',0)>.9})<6:raise ValueError('Capture lacks a complete cycle: '+direction+' '+action)
            indices=[s['frame'] for s in rows if s.get('amount',0)>.9]
            changes=[b for a,b in zip(indices,indices[1:]) if b!=a]
            previous=indices[0]
            for index in changes:
                if index!=(previous+1)%6:raise ValueError('Capture has skipped/reordered phases: '+direction+' '+action)
                previous=index
            if len(changes)<6:raise ValueError('Capture does not traverse the cycle seam: '+direction+' '+action)
    for transition in ['adjacent turn + fire','opposite turn','speed up','speed down + stop fire','stop + planted fire','resume']:
        if not any(label.endswith(' / '+transition) for label in labels):raise ValueError('Missing captured transition: '+transition)
    return True

def check(root,video,package):
    metadata=video.with_suffix('.json')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    report=json.loads(metadata.read_text(encoding='utf-8-sig'))
    if report.get('video')!=video.name or report.get('bytes')!=video.stat().st_size:raise ValueError('Capture metadata points to different bytes')
    validate_capture(report,package['inputSHA256'],sha(video),sha(root/'public/qa/capture-motion.js'))
    return {'path':metadata.relative_to(root).as_posix(),'sha256':sha(metadata)}
