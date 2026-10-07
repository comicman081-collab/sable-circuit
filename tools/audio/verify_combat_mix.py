"""Inspect actual engine-mixed audio, export a ten-second listening preview."""
import json
import av
import numpy as np
from scipy.signal import resample_poly
from intake_sfx_r04 import QA, read_audio, write_audio, sha

report = json.loads((QA/'battle_capture.json').read_text('utf-8'))
pcm, rate = read_audio(QA/'battle_native.avi')
start = round(report['capture_start_render_frame']/60*rate)
preview = pcm[start:start+rate*10]
assert len(preview) == rate*10 and preview.shape[1] == 2 and rate == 48000
peak = float(np.abs(preview).max())
true_peak = float(np.abs(resample_poly(preview,4,1,axis=0)).max())
rms = float(np.sqrt(np.mean(preview**2)))
assert peak > 0.01 and peak < .99 and true_peak < .99 and rms > .0001
wave = QA/'sable_combat_r04_actual_mix_10s.wav'
write_audio(wave, preview)
mp3 = wave.with_suffix('.mp3')
with av.open(str(wave)) as source, av.open(str(mp3), 'w') as output:
    stream = output.add_stream('libmp3lame',rate=rate)
    stream.layout='stereo'
    stream.bit_rate=256000
    converter=av.AudioResampler(format='fltp',layout='stereo',rate=rate)
    for frame in source.decode(audio=0):
        for audio_frame in converter.resample(frame):
            for packet in stream.encode(audio_frame): output.mux(packet)
    for frame in converter.resample(None):
        for packet in stream.encode(frame): output.mux(packet)
    for packet in stream.encode(): output.mux(packet)
counts={}
for event in report['audio_events']['events']:
    counts[event['cue']]=counts.get(event['cue'],0)+1
result={'status':'PASS_TECHNICAL_ONLY','duration_s':10,'rate':rate,'channels':2,
        'peak_dbfs':float(20*np.log10(peak)), 'estimated_true_peak_4x_dbfs':float(20*np.log10(true_peak)),
        'rms_dbfs':float(20*np.log10(rms)), 'fullscale_samples':int(np.count_nonzero(np.abs(preview)>=.999)),
        'actual_engine_events':counts,'peak_voices':report['audio_events']['peak_voices'],
        'wav_sha256':sha(wave),'mp3_sha256':sha(mp3),'capture_source':'Godot MovieWriter actual AudioServer stereo mix',
        'post_added_sfx':False,'subjective_listening_approval':False,
        'video_intermediate':'battle_native.avi uses default MovieWriter 1280x720; audio-only source, not eligible visual evidence. Native viewport stills are 1920x1080.'}
(QA/'mix_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
