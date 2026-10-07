"""Stream native Godot viewport frames to a ten-second H.264 MP4."""
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
from fractions import Fraction

import av
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "qa/combat_preview_20260914/combat_sequence"
GODOT = Path("D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64.exe")
OUT.mkdir(parents=True, exist_ok=True)
TEMP = OUT / "temp"
TEMP.mkdir(exist_ok=True)
OUTPUT = OUT / "sable_in_app_combat_10s.mp4"


def receive(connection, size):
    data = bytearray()
    while len(data) < size:
        chunk = connection.recv(size - len(data))
        if not chunk:
            raise EOFError("Godot stopped during a frame")
        data.extend(chunk)
    return bytes(data)


with socket.socket() as server:
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    server.settimeout(90)
    env = os.environ.copy()
    env.update(SABLE_CAPTURE_PORT=str(server.getsockname()[1]),
               SABLE_CAPTURE_OUTPUT=str(OUT), TEMP=str(TEMP), TMP=str(TEMP),
               PYTHONDONTWRITEBYTECODE="1")
    command = [str(GODOT), "--path", str(ROOT), "--script",
               "res://tests/render/battle_video_10s_capture.gd", "--resolution",
               "1920x1080", "--fixed-fps", "60", "--disable-vsync",
               "--log-file", str(OUT / "godot.log")]
    with (OUT / "process.log").open("w", encoding="utf-8") as log:
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log,
                                   stderr=subprocess.STDOUT, startupinfo=startup)
        (OUT / "process.json").write_text(json.dumps({"pid": process.pid, "command": command}, indent=2), encoding="utf-8")
        count = 0
        try:
            connection, _ = server.accept()
            connection.settimeout(90)
            with connection, av.open(str(OUTPUT), "w", options={"movflags": "+faststart"}) as mux:
                stream = mux.add_stream("libx264", rate=60)
                stream.width, stream.height = 1920, 1080
                stream.pix_fmt = "yuv420p"
                stream.options = {"crf": "18", "preset": "fast"}
                while True:
                    length = struct.unpack(">I", receive(connection, 4))[0]
                    if not length:
                        break
                    assert length == 1920 * 1080 * 4, length
                    picture = Image.frombytes("RGBA", (1920, 1080), receive(connection, length)).convert("RGB")
                    assert picture.size == (1920, 1080), picture.size
                    frame = av.VideoFrame.from_image(picture)
                    frame.pts, frame.time_base = count, Fraction(1, 60)
                    for packet in stream.encode(frame):
                        mux.mux(packet)
                    count += 1
                    if count % 120 == 0:
                        print(f"Encoded {count}/600 native frames", flush=True)
                for packet in stream.encode():
                    mux.mux(packet)
            exit_code = process.wait(timeout=30)
            assert exit_code == 0, exit_code
            assert count == 600, count
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=15)

with av.open(str(OUTPUT)) as movie:
    decoded = sum(1 for _ in movie.decode(video=0))
    duration = float(movie.streams.video[0].duration * movie.streams.video[0].time_base)
assert decoded == 600 and abs(duration - 10) < 0.01, (decoded, duration)
report = {"frames": count, "decoded_frames": decoded, "fps": 60, "duration_seconds": duration,
          "native_resolution": [1920, 1080], "audio": False, "bytes": OUTPUT.stat().st_size,
          "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
          "output": str(OUTPUT), "scope": "current app combat preview capture only; no art approval"}
(OUT / "encode.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report), flush=True)
