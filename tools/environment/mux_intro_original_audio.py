"""Bind the six original Flow clip soundtracks to the existing 1080p intro.

The current Web/runtime video is intentionally left untouched.  Its Theora
packets are remuxed byte-for-byte into a new OGV while the AAC audio tracks
from the six user-authorized source clips are decoded and encoded as Vorbis.
No image frame is generated, redrawn, resized or re-timed here.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess

import av
import imageio_ffmpeg
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
VIDEO = ROOT / "assets/cinematics/sable_intro.ogv"
SOURCES = sorted((ROOT / "motion_lab_v1/cinematics/flow_intro_20260915/source_720p").glob("*.mp4"))
OUTPUT = ROOT / "assets/cinematics/sable_intro_original_bgm.ogv"
QA = ROOT / "qa/music_integration_20260920"
TEMP = QA / "sable_intro_original_bgm.tmp.ogv"
MANIFEST = QA / "intro_original_audio_mux.json"
RATE = 48_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def packet_payload_digest(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    count = 0
    with av.open(str(path)) as container:
        stream = container.streams.video[0]
        for packet in container.demux(stream):
            if packet.dts is None:
                continue
            digest.update(bytes(packet))
            count += 1
    return count, digest.hexdigest()


def inspect(path: Path) -> dict[str, object]:
    with av.open(str(path)) as container:
        assert len(container.streams.video) == 1
        assert len(container.streams.audio) == 1
        video = container.streams.video[0]
        audio = container.streams.audio[0]
        assert video.codec_context.name == "theora"
        assert audio.codec_context.name == "vorbis"
        assert (video.codec_context.width, video.codec_context.height) == (1920, 1080)
        frames = sum(1 for _ in container.decode(video=0))
    sample_count = 0
    squared = 0.0
    with av.open(str(path)) as container:
        for frame in container.decode(audio=0):
            samples = frame.to_ndarray().astype(np.float64, copy=False)
            sample_count += samples.size
            squared += float(np.square(samples).sum())
    return {
        "video_codec": "theora",
        "audio_codec": "vorbis",
        "video_resolution": [1920, 1080],
        "video_frames": frames,
        "audio_samples": sample_count,
        "audio_rms": (squared / sample_count) ** 0.5 if sample_count else 0.0,
    }


def main() -> None:
    assert VIDEO.is_file()
    assert len(SOURCES) == 6
    QA.mkdir(parents=True, exist_ok=True)
    if TEMP.exists():
        TEMP.unlink()

    input_packets, input_digest = packet_payload_digest(VIDEO)
    source_audio = []
    for path in SOURCES:
        with av.open(str(path)) as source:
            assert len(source.streams.audio) == 1
            stream = source.streams.audio[0]
            assert stream.codec_context.name == "aac"
            source_audio.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path),
                                 "codec": "aac", "duration_seconds": float(stream.duration * stream.time_base)})
    # PyAV's supplied codec library decodes Theora but cannot open its encoder.
    # Its installed local FFmpeg companion can stream-copy the Theora packets
    # and encode Vorbis, so the operation remains entirely local and lossless
    # for every visible frame.
    audio_inputs = [flag for path in SOURCES for flag in ("-i", str(path))]
    concat_inputs = "".join("[%d:a:0]" % index for index in range(1, len(SOURCES) + 1))
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
               "-i", str(VIDEO), *audio_inputs,
               "-filter_complex", concat_inputs + "concat=n=6:v=0:a=1[original_bgm]",
               "-map", "0:v:0", "-map", "[original_bgm]", "-c:v", "copy", "-c:a", "libvorbis",
               "-ar", str(RATE), "-ac", "2", "-b:a", "128k", "-shortest", str(TEMP)]
    subprocess.run(command, cwd=ROOT, check=True, timeout=600)

    output_packets, output_digest = packet_payload_digest(TEMP)
    assert (output_packets, output_digest) == (input_packets, input_digest)
    evidence = inspect(TEMP)
    assert evidence["video_frames"] == 1440
    # The audio encoder's final packet is 4 ms shorter than the 60.0 s video.
    # This is inside one Vorbis block and avoids a trailing black/silent tail.
    assert evidence["audio_samples"] >= int(RATE * 59.9 * 2)
    assert evidence["audio_rms"] > 0.0001
    TEMP.replace(OUTPUT)
    receipt = {
        "status": "PASS_ORIGINAL_VIDEO_AUDIO_BOUND",
        "method": "Existing 1080p Theora video packets remuxed unchanged; six original AAC tracks encoded to Vorbis in timeline order.",
        "source_video": {"path": VIDEO.relative_to(ROOT).as_posix(), "sha256": sha256(VIDEO),
                         "packet_count": input_packets, "packet_payload_sha256": input_digest},
        "source_audio": source_audio,
        "output": {"path": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT),
                   "packet_count": output_packets, "packet_payload_sha256": output_digest, **evidence},
        "no_new_generation": True,
        "no_visual_reencode": True,
    }
    MANIFEST.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
