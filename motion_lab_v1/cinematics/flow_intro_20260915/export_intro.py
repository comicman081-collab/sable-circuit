"""Export user-authorized 720p Flow clips as silent upscaled 1080p deliveries.

No AI generation, interpolation, audio, or runtime asset promotion occurs here.
"""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import av
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OUT = HERE / 'delivery_1080p'
QA = HERE / 'review'
OUT.mkdir(exist_ok=True)
QA.mkdir(exist_ok=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoder(path):
    container = av.open(str(path), 'w', options={'movflags': '+faststart'})
    stream = container.add_stream('libx264', rate=24)
    stream.width, stream.height = 1920, 1080
    stream.pix_fmt = 'yuv420p'
    stream.options = {'crf': '18', 'preset': 'fast'}
    return container, stream


def finish(container, stream):
    for packet in stream.encode():
        container.mux(packet)
    container.close()


def inspect(path):
    with av.open(str(path)) as video:
        assert len(video.streams.audio) == 0, path
        stream = video.streams.video[0]
        times = []
        for frame in video.decode(video=0):
            assert (frame.width, frame.height) == (1920, 1080)
            times.append(float(frame.pts * frame.time_base))
        assert all(b > a for a, b in zip(times, times[1:]))
        return {'file': str(path.relative_to(HERE)), 'sha256': sha(path),
                'frames': len(times), 'fps': 24, 'duration_seconds': len(times) / 24,
                'resolution': [1920, 1080], 'audio_streams': 0, 'all_frames_decoded': True}


def main():
    sources = sorted((HERE / 'source_720p').glob('*.mp4'))
    assert len(sources) == 6
    master_path = OUT / 'SABLE_CIRCUIT_INTRO_60s_1080p_SILENT.mp4'
    master, master_stream = encoder(master_path)
    total = 0
    records = []
    for source in sources:
        destination = OUT / (source.stem + '_1080p_SILENT.mp4')
        clip, clip_stream = encoder(destination)
        panels = []
        count = 0
        with av.open(str(source)) as input_video:
            original_audio = len(input_video.streams.audio)
            assert input_video.streams.video[0].average_rate == 24
            for index, frame in enumerate(input_video.decode(video=0)):
                assert (frame.width, frame.height) == (1280, 720)
                if index in (24, 120, 216):
                    panels.append(frame.to_image())
                for container, stream, pts in ((clip, clip_stream, index), (master, master_stream, total)):
                    scaled = frame.reformat(width=1920, height=1080, format='yuv420p', interpolation='LANCZOS')
                    scaled.pts = pts
                    scaled.time_base = Fraction(1, 24)
                    for packet in stream.encode(scaled):
                        container.mux(packet)
                count += 1
                total += 1
        assert count == 240, (source, count)
        finish(clip, clip_stream)
        # Documentary contact sheet, not native 1080p generation-quality proof.
        sheet = Image.new('RGB', (1920, 1080), '#10191e')
        draw = ImageDraw.Draw(sheet)
        for i, panel in enumerate(panels):
            panel.thumbnail((960, 540))
            xy = ((i % 2) * 960, (i // 2) * 540)
            sheet.paste(panel, xy)
            draw.text((xy[0] + 12, xy[1] + 12), f'{source.stem} / {1 if i == 0 else 5 if i == 1 else 9}s', fill='white')
        draw.text((990, 610), 'SOURCE: 1280x720 / 24fps\nDELIVERY: 1920x1080 Lanczos upscale\nSilent export / no added generations\nContact sheet is not native-1080p quality proof.', fill='white')
        sheet.save(QA / (source.stem + '_samples.jpg'), quality=95)
        record = inspect(destination)
        record.update({'source_file': str(source.relative_to(HERE)), 'source_sha256': sha(source),
                       'source_resolution': [1280, 720], 'source_audio_streams_removed': original_audio})
        records.append(record)
        print(json.dumps(record), flush=True)
    finish(master, master_stream)
    assert total == 1440
    master_record = inspect(master_path)
    assert master_record['frames'] == 1440
    manifest = {'status': 'EXPORTED_DECODE_VERIFIED_NOT_ART_APPROVAL',
                'method': 'User-authorized 720p generation, Lanczos 1080p upscale, no audio; ordered hard cuts, no timing change',
                'native_1080p_generation': False, 'generated_clips': 6,
                'submission_attempts': 7, 'failed_attempts_reported_uncharged_by_flow': 1,
                'retry': 'Part 3 retried once with explicit user authorization',
                'displayed_credits_per_success': 15, 'expected_total_credits': 90,
                'billing_ledger_audited': False, 'clips': records, 'master': master_record}
    (HERE / 'delivery_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(master_record), flush=True)


if __name__ == '__main__':
    main()
