from pathlib import Path
import sys
import av

source = Path(sys.argv[1])
destination = source.with_suffix('.mp3')
with av.open(str(source)) as input_audio, av.open(str(destination), 'w') as output:
    stream = output.add_stream('libmp3lame', rate=24000)
    stream.layout = 'mono'
    stream.bit_rate = 48000
    resampler = av.AudioResampler(format='fltp', layout='mono', rate=24000)
    for frame in input_audio.decode(audio=0):
        for converted in resampler.resample(frame):
            for packet in stream.encode(converted):
                output.mux(packet)
    for converted in resampler.resample(None):
        for packet in stream.encode(converted):
            output.mux(packet)
    for packet in stream.encode():
        output.mux(packet)
