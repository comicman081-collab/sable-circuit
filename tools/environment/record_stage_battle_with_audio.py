"""Native Godot MovieWriter AV capture, preserving the actual mixed game sound."""
from datetime import datetime
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess
import socket
import struct
import av
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/os.environ.get('SABLE_CAPTURE_ROOT','qa/enemy_cover_repair_20260919')/('video_'+datetime.now().strftime('%H%M%S'))
GODOT='D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64.exe'
FPS=60
RATE=48000

def encode(raw, native, output, start):
    video_count=audio_count=source_video=source_audio=0
    sum_square=0.0
    peak=0.0
    with av.open(str(raw)) as source, av.open(str(output),'w',options={'movflags':'+faststart'}) as dest:
        assert len(source.streams.audio)==1, 'Missing Godot AudioServer mix'
        vs=dest.add_stream('libx264',rate=FPS)
        vs.width,vs.height=1920,1080; vs.pix_fmt='yuv420p'
        vs.options={'crf':'18','preset':'fast'}
        aus=dest.add_stream('aac',rate=RATE)
        aus.layout='stereo'; aus.bit_rate=192000
        resampler=av.AudioResampler(format='fltp',layout='stereo',rate=RATE)
        # Godot's built-in AVI size is fixed at launch from project settings.
        # Only its synchronized AudioServer mix is used. Video comes directly
        # from the native 1920x1080 viewport readback, never from the 720p AVI.
        with av.open(str(native)) as pictures:
            for frame in pictures.decode(video=0):
                assert (frame.width,frame.height)==(1920,1080)
                frame.pts=video_count; frame.time_base=Fraction(1,FPS)
                for packet in vs.encode(frame): dest.mux(packet)
                video_count+=1
        for frame in source.decode(audio=0):
            if isinstance(frame,av.AudioFrame):
                for audio in resampler.resample(frame):
                    array=audio.to_ndarray()
                    lo=max(0,start*800-source_audio)
                    hi=min(array.shape[1],(start+600)*800-source_audio)
                    if hi>lo:
                        data=np.ascontiguousarray(array[:,lo:hi])
                        peak=max(peak,float(np.abs(data).max()))
                        sum_square+=float(np.square(data.astype(np.float64)).sum())
                        mixed=av.AudioFrame.from_ndarray(data,format='fltp',layout='stereo')
                        mixed.sample_rate=RATE; mixed.pts=audio_count; mixed.time_base=Fraction(1,RATE)
                        for packet in aus.encode(mixed): dest.mux(packet)
                        audio_count+=hi-lo
                    source_audio+=array.shape[1]
        for packet in vs.encode(): dest.mux(packet)
        for packet in aus.encode(): dest.mux(packet)
    assert video_count==600 and audio_count==480000,(video_count,audio_count,start,source_video,source_audio)
    rms=(sum_square/(audio_count*2))**0.5
    assert rms>0.0001 and peak>0.001,'Game audio is silent'
    with av.open(str(output)) as check:
        assert len(check.streams.audio)==1
        duration=float(check.streams.video[0].duration*check.streams.video[0].time_base)
        assert abs(duration-10)<.001
        assert sum(1 for _ in check.decode(video=0))==600
    return {'frames':video_count,'audio_samples_per_channel':audio_count,'audio_rms':rms,'audio_peak':peak,
            'native_resolution':[1920,1080],'fps':60,'duration_seconds':duration,'source_start_frame':start,
            'audio':'Actual Godot MovieWriter stereo mix; synchronized trim, no added soundtrack',
            'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),
            'native_readback_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
            'video_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}

def receive(peer, count):
    result=bytearray()
    while len(result)<count:
        chunk=peer.recv(count-len(result))
        if not chunk: raise RuntimeError('Incomplete native viewport stream')
        result.extend(chunk)
    return result

def main():
    OUT.mkdir(parents=True,exist_ok=False)
    reports=[]
    requested=os.environ.get('SABLE_CAPTURE_MISSIONS','1,2,3')
    numbers=tuple(int(value.strip()) for value in requested.split(',') if value.strip())
    if not numbers or any(number not in (1,2,3,4,5,6,7,8,9,10) for number in numbers):
        raise ValueError(f'Invalid SABLE_CAPTURE_MISSIONS: {requested!r}')
    for number in numbers:
        folder=OUT/f'stage{number}'; folder.mkdir(); cache=folder/'cache'; cache.mkdir()
        env=os.environ.copy()
        env.update({'SABLE_CAPTURE_OUTPUT':str(folder),'SABLE_CAPTURE_MISSION':f'MIS_CH01_{number:02d}',
                    'SABLE_CAPTURE_MOVIE':'1','TEMP':str(cache),'TMP':str(cache),'XDG_CACHE_HOME':str(cache),
                    'PYTHONPYCACHEPREFIX':str(cache),'PYTHONDONTWRITEBYTECODE':'1'})
        if os.environ.get('SABLE_CAPTURE_BOSS') == '1':
            env['SABLE_CAPTURE_BOSS'] = '1'
        raw=folder/'native_mix.avi'
        command=[GODOT,'--path',str(ROOT),'--script','res://tests/render/stage_battle_video_10s_capture.gd',
                 '--resolution','1920x1080','--fixed-fps','60','--write-movie',str(raw),
                 '--log-file',str(folder/'godot.log')]
        startup=subprocess.STARTUPINFO(); startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW; startup.wShowWindow=0
        native=folder/'native_readback.mkv'
        with socket.socket() as server, (folder/'process.log').open('w',encoding='utf-8') as log:
            server.bind(('127.0.0.1',0)); server.listen(1); server.settimeout(90)
            env['SABLE_CAPTURE_PORT']=str(server.getsockname()[1])
            child=subprocess.Popen(command,cwd=ROOT,env=env,startupinfo=startup,stdout=log,stderr=subprocess.STDOUT)
            try:
                peer,_=server.accept(); peer.settimeout(90)
                with peer, av.open(str(native),'w') as mux:
                    stream=mux.add_stream('libx264',rate=60)
                    stream.width,stream.height=1920,1080; stream.pix_fmt='yuv420p'
                    stream.options={'crf':'0','preset':'ultrafast'}
                    count=0
                    while True:
                        size=struct.unpack('>I',receive(peer,4))[0]
                        if size==0: break
                        assert size==1920*1080*4 and count<600
                        pixels=np.frombuffer(receive(peer,size),dtype=np.uint8).reshape(1080,1920,4)
                        frame=av.VideoFrame.from_ndarray(pixels,format='rgba')
                        frame.pts=count; frame.time_base=Fraction(1,60)
                        for packet in stream.encode(frame): mux.mux(packet)
                        count+=1
                    for packet in stream.encode(): mux.mux(packet)
                assert count==600 and child.wait(timeout=30)==0
            finally:
                if child.poll() is None: child.terminate(); child.wait(timeout=15)
        assert 'SCRIPT ERROR' not in (folder/'process.log').read_text(encoding='utf-8')
        capture=json.loads((folder/'capture.json').read_text(encoding='utf-8'))
        assert capture['audio'] and capture['capture_end_render_frame']-capture['capture_start_render_frame']==600
        if os.environ.get('SABLE_CAPTURE_BOSS') == '1':
            assert capture['initial_encounter_step'] == 4
            expected = {1:'BOSS_SITE7_ANCHOR_01',2:'BOSS_SITE7_RELAY_01',3:'BOSS_SITE7_REMNANT_01',4:'BOSS_SITE7_FORGE_01',5:'BOSS_SITE7_CARRIER_01',
                        6:'BOSS_SITE7_AERATOR_01',7:'BOSS_SITE7_CRYO_01',8:'BOSS_SITE7_GANTRY_01',9:'BOSS_SITE7_ARCHIVE_01',10:'BOSS_SITE7_ORIGIN_01'}[number]
            assert expected in capture['seen_enemy_ids'], f'Boss missing from game capture: {expected}'
        video=folder/f'stage{number}_combat_10s_sound_1080p.mp4'
        report=encode(raw,native,video,capture['capture_start_render_frame'])
        report.update({'mission':capture['mission'],'path':str(video),'capture_sha256':hashlib.sha256((folder/'capture.json').read_bytes()).hexdigest()})
        reports.append(report)
        (folder/'encode.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'STAGE {number} VIDEO+AUDIO COMPLETE {video}',flush=True)
    dependencies=['scripts/combat/cover_navigation.gd','scripts/combat/site7_enemy_tactics.gd',
        'scripts/animation/site7_machine_sprite.gd','scripts/actors/enemy_actor.gd',
        'tests/render/stage_battle_video_10s_capture.gd','scripts/audio/combat_sfx_bank.gd',
        'data/art_profiles/enemy_profiles.json','data/visual/site7_environment_props.json',
        'tools/environment/record_stage_battle_with_audio.py']
    (OUT/'manifest.json').write_text(json.dumps({'clips':reports,'sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in dependencies}},ensure_ascii=False,indent=2),encoding='utf-8')
    print(OUT,flush=True)
if __name__=='__main__': main()
