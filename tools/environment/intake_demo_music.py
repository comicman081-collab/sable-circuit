"""Claim only explicitly selected user-library music, preserving original bytes.

No source deletions: retirement is a separate hash-checked PowerShell operation
after runtime validation. Analysis uses local PyAV, no external service/model.
"""
from pathlib import Path
import hashlib
import json
import shutil
import av
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = Path('D:/AI 종합 폴더/Games/voice, image asset/voice & sound/sound')
RUN = 'run_gun_audio_pack/run_gun_audio_pack/'
FPS = 'fps_audio_pack/fps_audio_pack/'
SELECTED = {
    'title': (RUN+'01_title_songs/05_steel_horizon.mp3', 'Steel Horizon', 'Main title'),
    'base': (FPS+'02_bgm/fps_bgm_06_sniper_ridge.wav', 'Sniper Ridge', 'Base and briefing'),
    'stage1': (RUN+'02_bgm/13_night_raid_protocol.mp3', 'Night Raid Protocol', 'Blackout / infiltration'),
    'stage2': (RUN+'02_bgm/46_metro_tunnel_surge.mp3', 'Metro Tunnel Surge', 'Sublevel relay'),
    'stage3': (RUN+'02_bgm/20_command_center_push.mp3', 'Command Center Push', 'Core approach'),
    'stage4': (RUN+'02_bgm/35_underground_reactor_charge.mp3', 'Underground Reactor Charge', 'Thermal forge'),
    'stage5': (RUN+'02_bgm/49_warship_deck_breakout.mp3', 'Warship Deck Breakout', 'Offshore relay'),
    'boss': (RUN+'02_bgm/50_final_sector_overrun.mp3', 'Final Sector Overrun', 'Boss encounters'),
    'results': (RUN+'05_ending_songs/01_after_the_smoke.mp3', 'After the Smoke', 'Operation results'),
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def inspect(path):
    squared = 0.0
    count = samples = 0
    peak = clipped = 0
    with av.open(str(path)) as container:
        stream = container.streams.audio[0]
        codec, rate, channels = stream.codec_context.name, stream.rate, stream.channels
        resampler = av.AudioResampler(format='fltp', layout='stereo', rate=44100)
        for frame in container.decode(stream):
            for converted in resampler.resample(frame):
                a = converted.to_ndarray()
                assert np.isfinite(a).all()
                squared += float(np.square(a.astype(np.float64)).sum())
                count += a.size
                samples += a.shape[1]
                peak = max(peak, float(np.abs(a).max()))
                clipped += int((np.abs(a) >= 1.0).sum())
    assert samples > 44100 * 20 and squared / count > 1e-7, 'Short or silent music'
    return dict(codec=codec, rate=rate, channels=channels, seconds=round(samples/44100,3),
                rms_db=round(10*np.log10(squared/count),3), peak=peak,
                clipped_fraction=clipped/count, decoded_full_track=True)

def main():
    qa = ROOT/'qa/music_integration_20260920'
    qa.mkdir(parents=True, exist_ok=True)
    originals = ROOT/'sound/music/originals'
    runtime = ROOT/'sound/music/runtime'
    originals.mkdir(parents=True, exist_ok=True)
    runtime.mkdir(parents=True, exist_ok=True)
    rows = []
    tracks = {}
    for key, (relative, title, use) in SELECTED.items():
        source = LIBRARY/relative
        original = originals/source.name
        if source.exists():
            if original.exists(): assert sha(original) == sha(source), 'Do not overwrite a different original'
            else: shutil.copy2(source, original)
            assert sha(original) == sha(source)
        assert original.exists(), source
        stats = inspect(original)
        # Some library files carry .wav names but actual MP3 payloads. Inspect
        # codec rather than assuming the extension; retain untouched masters.
        output = runtime/(key+'.mp3')
        if stats['codec'] in ('mp3', 'mp3float'):
            shutil.copy2(original, output)
        else:
            with av.open(str(original)) as inp, av.open(str(output), 'w', format='mp3') as out:
                enc = out.add_stream('libmp3lame', rate=44100)
                enc.layout = 'stereo'
                enc.bit_rate = 160000
                rs = av.AudioResampler(format='fltp', layout='stereo', rate=44100)
                for frame in inp.decode(audio=0):
                    for converted in rs.resample(frame):
                        for packet in enc.encode(converted): out.mux(packet)
                for packet in enc.encode(): out.mux(packet)
        runtime_stats = inspect(output)
        # RMS-matched conservative playback; SFX retain their separate bus.
        target = -25.0 if key not in ('title', 'intro', 'results') else -22.0
        gain = round(max(-24, min(-4, target-runtime_stats['rms_db'])), 2)
        tracks[key] = dict(title=title, path='res://'+output.relative_to(ROOT).as_posix(), gain_db=gain)
        rows.append(dict(id=key, title=title, role=use, source=str(source),
                         original=original.relative_to(ROOT).as_posix(), original_sha256=sha(original),
                         runtime=output.relative_to(ROOT).as_posix(), runtime_sha256=sha(output),
                         analysis=stats, runtime_analysis=runtime_stats, gain_db=gain,
                         source_removed=not source.exists()))
        print(key, stats, 'gain', gain, flush=True)
    for name, folder in [('run_gun',RUN),('fps',FPS)]:
        shutil.copy2(LIBRARY/folder/'README.md', ROOT/'sound/music'/f'{name}_SOURCE_README.md')
    manifest = dict(project='SABLE CIRCUIT', selection_basis='User-supplied pack descriptions, stage themes, full local decoding and measured levels; not a claim of human listening or cross-project history audit.',
                    license_evidence='Original-content statements preserved in pack READMEs; user explicitly authorized these files for this demo. No independent rights warranty.',
                    shared_library=str(LIBRARY), exclusive_allocation=True, tracks=rows)
    (ROOT/'sound/music/allocation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'sound/music/catalog.json').write_text(json.dumps(tracks,ensure_ascii=False,indent=2),encoding='utf8')
    print('INTAKE_COMPLETE', len(rows), flush=True)

if __name__ == '__main__': main()
