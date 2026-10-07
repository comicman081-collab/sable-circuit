"""Validate temporal evidence, not a PASS label or actor displacement alone."""
import hashlib,json,math,re
from pathlib import Path
from gait_contract import frame_at, starts as phase_starts

DIRECTIONS=['E','SE','S','SW','W','NW','N','NE']
def validate_report(report,character,input_sha,script_sha,profile=None):
    if report.get('kind')!='motion-studio-locomotion-browser' or report.get('character')!=character:raise ValueError('Wrong locomotion report')
    if report.get('build',{}).get('inputSHA256')!=input_sha or report.get('testScriptSHA256')!=script_sha:raise ValueError('Stale locomotion report')
    expected={f'{action}_{d}' for action in ['walk','run','walk_fire','run_fire','stationary_fire'] for d in DIRECTIONS}
    rows=report.get('results',[])
    if len(rows)!=40 or {r['name'] for r in rows}!=expected or report.get('pass') is not True:raise ValueError('Missing/failed locomotion matrix')
    if len(report.get('viewport',[]))!=2 or report['viewport'][0]<1920 or report['viewport'][1]<1080:raise ValueError('Locomotion evidence must be native 1080p')
    for row in rows:
        expected_action,expected_direction=row['name'].rsplit('_',1)
        if row['direction']!=expected_direction or row.get('stationary')!=(expected_action=='stationary_fire') or row.get('firing')!=('fire' in expected_action):raise ValueError('Case flags disagree with matrix name')
        samples=row.get('samples',[])
        if len(samples)<6 or row.get('pass') is not True:raise ValueError('Missing temporal samples: '+row['name'])
        frames={s['frame'] for s in samples};hashes={s['hash'] for s in samples};count=row['frameCount']
        if any(s['direction']!=row['direction'] or s['frameCount']!=count for s in samples):raise ValueError('Renderer disagrees with selected direction/clip')
        if any(not isinstance(h,str) or not re.fullmatch('[0-9a-f]{64}',h) for h in hashes):raise ValueError('Missing decoded lower-body pixel hashes')
        if set(row['frames'])!=frames or set(row['lowerPixelHashes'])!=hashes:raise ValueError('Summary does not match temporal samples')
        if row.get('stationary'):
            if len(hashes)!=1 or row['travel']>=.001:raise ValueError('Stationary firing changes support feet')
        elif count<6 or frames!=set(range(count)) or len(hashes)<6 or row['travel']<=.1:
            raise ValueError('Frozen, missing or duplicate visible locomotion: '+row['name'])
        if (row['shots']>0)!=row['firing']:raise ValueError('Firing coverage mismatch')
        # Preserve chronological evidence instead of reducing motion to sets.
        finite=lambda v:type(v) in (int,float) and math.isfinite(v)
        for sample in samples:
            if not finite(sample.get('time')) or not finite(sample.get('phase')) or not 0<=sample['phase']<1:raise ValueError('Missing/non-finite time or phase')
            position=sample.get('position')
            if not isinstance(position,list) or len(position)!=2 or not all(finite(v) for v in position):raise ValueError('Missing/non-finite actor position')
            if type(sample.get('shots')) is not int or sample['shots']<0:raise ValueError('Missing observed shot counter')
        if not finite(row.get('travel')) or type(row.get('shots')) is not int:raise ValueError('Invalid temporal summary')
        measured=0;phase_travel=0;by_frame={}
        clip=None
        if profile:
            view=profile['views'][row['direction']]
            clip=view['idle'] if row['stationary'] else view.get('run',view['walk']) if expected_action.startswith('run') else view['walk']
            if clip['frames']!=count:raise ValueError('Report frame count differs from selected profile')
        timing=phase_starts(clip or {}) if not row['stationary'] else None
        for sample in samples:
            if not row['stationary'] and sample['frame']!=frame_at(sample['phase'],timing):raise ValueError('Chronological frame differs from authored phase')
            if sample['frame'] in by_frame and by_frame[sample['frame']]!=sample['hash']:raise ValueError('Same frame index changed lower-body pixels')
            by_frame[sample['frame']]=sample['hash']
        for a,b in zip(samples,samples[1:]):
            if b['time']<=a['time']:raise ValueError('Sample time must increase')
            travel=math.dist(a['position'],b['position']);measured+=travel
            if b['shots']<a['shots']:raise ValueError('Shot counter went backwards')
            delta=(b['phase']-a['phase'])%1
            phase_travel+=delta
            if profile and not row['stationary']:
                mode='run' if expected_action.startswith('run') else 'walk'
                stride=profile['locomotion'][mode+'Stride'];speed=profile['locomotion'][mode+'Speed']
                if not finite(stride) or stride<=0 or not finite(speed) or speed<=0:raise ValueError('Invalid profile stride/speed')
                if abs(delta-travel/stride)>1e-5:raise ValueError('Gait phase is not tied to measured travel')
                if travel/(b['time']-a['time'])>speed*1.02:raise ValueError('Observed movement exceeds configured speed')
        if abs(measured-row['travel'])>1e-5:raise ValueError('Travel summary differs from observed positions')
        if samples[-1]['shots']-samples[0]['shots']!=row['shots']:raise ValueError('Shot summary differs from observed counter')
        if not row['stationary'] and phase_travel<1:raise ValueError('Capture lacks a complete chronological cycle')
    return True

def check(root,character,path,package):
    target=(root/path).resolve()
    if not target.is_relative_to(root):raise ValueError('Evidence path escaped project')
    report=json.loads(target.read_text(encoding='utf-8-sig'))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    profile=json.loads((root/'public/assets/atlas'/character/'profile.json').read_text(encoding='utf-8-sig'))
    validate_report(report,character,package['inputSHA256'],sha(root/'public/qa/locomotion-checks.js'),profile)
    return {'path':target.relative_to(root).as_posix(),'sha256':sha(target)}
