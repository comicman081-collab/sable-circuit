"""Read-only source intake + independent PCM diagnostics; no source regeneration."""
from pathlib import Path
import hashlib
import json
import shutil
import stat
import zipfile
import numpy as np
import av
import wave
from scipy.signal import resample_poly

ROOT = Path(__file__).resolve().parents[2]
INTAKE = ROOT / 'art_src/audio/chatgpt_sfx_r04_20260919'
QA = ROOT / 'qa/sfx_integration_20260919'
ZIP_NAME = 'SABLE_CIRCUIT_SFX_R04_COLOSSAL_120.zip'
EXPECTED = 'c8758f1f030923a63dd01c10e50889307c72fbdf12606bc73acad2b5e7ed54eb'


def read_audio(path):
    with av.open(str(path)) as container:
        stream = container.streams.audio[0]
        rate = stream.rate
        resampler = av.AudioResampler(format='dblp', layout=stream.layout, rate=rate)
        chunks = []
        for frame in container.decode(audio=0):
            chunks.extend(f.to_ndarray().T for f in resampler.resample(frame))
        chunks.extend(f.to_ndarray().T for f in resampler.resample(None))
        return np.concatenate(chunks), rate


def write_audio(path, pcm, rate=48000):
    assert np.isfinite(pcm).all() and np.abs(pcm).max() < 1
    with wave.open(str(path), 'wb') as output:
        output.setnchannels(pcm.shape[1])
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(np.rint(pcm*32767).astype('<i2').tobytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    INTAKE.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    source = Path('C:/Users/AAA/Downloads') / ZIP_NAME
    assert sha(source) == EXPECTED
    archive = INTAKE / ZIP_NAME
    if not archive.exists():
        shutil.copy2(source, archive)
    assert sha(archive) == EXPECTED
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for item in z.infolist():
            target = (INTAKE / item.filename).resolve()
            assert target.is_relative_to(INTAKE.resolve())
            assert not stat.S_ISLNK(item.external_attr >> 16)
            assert item.file_size < 100_000_000
            if target.exists():
                assert target.read_bytes() == z.read(item)
            else:
                z.extract(item, INTAKE)
    bank = INTAKE / 'SABLE_CIRCUIT_SFX_R04_COLOSSAL'
    manifest = json.loads((bank / 'BANK_MANIFEST.json').read_text('utf-8-sig'))
    source_manifest = json.loads((bank / 'sources/SOURCE_MANIFEST.json').read_text('utf-8-sig'))
    for entry in manifest['assets'] + source_manifest['used']:
        assert sha(bank / entry['file']) == entry['sha256'], entry['file']
    paths = sorted((bank / 'audio/wav').rglob('*.wav')) + sorted((bank / 'extras/stereo_boss').glob('*.wav'))
    assert len(paths) == 132
    metrics = []
    for path in paths:
        pcm, rate = read_audio(path)
        assert rate == 48000 and np.isfinite(pcm).all()
        peak = float(np.abs(pcm).max())
        power = np.mean(pcm * pcm, axis=1)
        active = np.where(np.max(np.abs(pcm), axis=1) > .001)[0]
        spectrum = np.abs(np.fft.rfft(pcm.mean(axis=1))) ** 2
        frequencies = np.fft.rfftfreq(len(pcm), 1/rate)
        row = {'file': str(path.relative_to(bank)), 'sha256': sha(path), 'frames': len(pcm),
               'sample_rate': rate, 'channels': pcm.shape[1], 'seconds': len(pcm)/rate,
               'peak_dbfs': 20*np.log10(max(peak, 1e-12)),
               'true_peak_dbfs_4x': float(20*np.log10(max(float(np.abs(resample_poly(pcm, 4, 1, axis=0)).max()), 1e-12))),
               'rms_dbfs': float(10*np.log10(max(float(power.mean()), 1e-12))),
               'dc': float(np.max(np.abs(pcm.mean(axis=0)))),
               'fullscale_samples': int(np.count_nonzero(np.abs(pcm) >= .999)),
               'onset_ms': float(active[0]/rate*1000) if len(active) else None,
               'low_energy_fraction': float(spectrum[frequencies < 250].sum()/max(spectrum.sum(), 1e-12)),
               'tail_rms_dbfs': float(10*np.log10(max(float(power[-480:].mean()),1e-12))),
               'edge_peak': float(np.max(np.abs(pcm[[0,-1]])))}
        row['technical_ok'] = bool(peak > .01 and row['true_peak_dbfs_4x'] < -.5 and row['dc'] < .001 and row['fullscale_samples'] == 0 and row['edge_peak'] < .001)
        metrics.append(row)
    (QA / 'source_audio_analysis.json').write_text(json.dumps({'archive_sha256': EXPECTED, 'manifest_hashes_match': True, 'records': metrics}, indent=2), encoding='utf-8')
    cues = json.loads((bank/'CUE_MAP.json').read_text('utf-8-sig'))['cues']
    considered = ['aster_fire','rook_fire','mica_fire','enemy_fire','turret_fire','impact_steel_light','impact_steel_heavy','robot_hit','armor_break','boss_core_hit','boss_charge','boss_cross_beam','boss_stomp','boss_destroy']
    # Audition reels preserve full cues; consistent -3 dB preview headroom.
    for cue in cues:
        if cue['id'] not in considered:
            continue
        chunks, events, cursor = [], [], 0
        for rel in cue['variants']:
            path = bank / rel
            if cue['id'] in ['boss_cross_beam','boss_stomp','boss_destroy']:
                path = bank / 'extras/stereo_boss' / path.name
            pcm, rate = read_audio(path)
            pcm = np.repeat(pcm, 2, axis=1) if pcm.shape[1] == 1 else pcm
            gap = np.zeros((24000,2))
            chunks.extend([gap, pcm*.707])
            cursor += .5
            events.append({'start_s':cursor, 'file':str(path.relative_to(bank))})
            cursor += len(pcm)/rate
        write_audio(QA/(cue['id']+'_audition.wav'), np.concatenate(chunks))
        (QA/(cue['id']+'_audition.json')).write_text(json.dumps(events,indent=2),encoding='utf-8')
    print(json.dumps({'files':len(metrics),'technical_failures':[r['file'] for r in metrics if not r['technical_ok']], 'hashes_verified':True}))
    for cue in considered:
        rows=[r for r in metrics if f'_{cue}_v' in r['file'] and not r['file'].startswith('extras')]
        print(cue, [(Path(r['file']).stem[-3:],round(r['rms_dbfs'],1),round(r['low_energy_fraction'],2)) for r in rows])


if __name__ == '__main__':
    main()
