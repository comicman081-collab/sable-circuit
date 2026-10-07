"""Bounded native 1080p capture, streamed directly to project-local H.264.

No image generation, frame resize, injected soundtrack or persistent server.
The existing Godot capture drives normal input/AI/damage at fixed 60 Hz.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import socket
import struct
import subprocess
import av
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'qa/cover_ai_20260919' / ('battle_' + datetime.now().strftime('%H%M%S'))
OUT.mkdir(parents=True, exist_ok=False)
env = os.environ.copy()
for name in ('TEMP', 'TMP', 'XDG_CACHE_HOME', 'PYTHONPYCACHEPREFIX'):
    folder = OUT / 'cache' / name.lower()
    folder.mkdir(parents=True, exist_ok=True)
    env[name] = str(folder)
env['PYTHONDONTWRITEBYTECODE'] = '1'
env['SABLE_CAPTURE_OUTPUT'] = str(OUT)
startup = subprocess.STARTUPINFO()
startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startup.wShowWindow = 0
command = ['D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64.exe',
           '--path', str(ROOT), '--fixed-fps', '60', '--audio-driver', 'Dummy',
           '--log-file', str(OUT / 'godot.log'), '--script', 'res://tests/render/battle_video_10s_capture.gd']

def receive(peer, count):
    chunks = bytearray()
    while len(chunks) < count:
        chunk = peer.recv(count - len(chunks))
        if not chunk:
            raise RuntimeError('Godot closed capture before completing the frame')
        chunks.extend(chunk)
    return chunks

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server, (OUT / 'stdout.log').open('w', encoding='utf-8') as log:
    server.bind(('127.0.0.1', 0))
    server.listen(1)
    server.settimeout(90)
    env['SABLE_CAPTURE_PORT'] = str(server.getsockname()[1])
    child = subprocess.Popen(command, cwd=ROOT, env=env, startupinfo=startup, stdout=log, stderr=subprocess.STDOUT)
    frames = 0
    try:
        peer, _address = server.accept()
        with peer, av.open(str(OUT / 'site7_cover_combat_10s.mp4'), 'w', options={'movflags': '+faststart'}) as movie:
            peer.settimeout(60)
            stream = movie.add_stream('libx264', rate=60)
            stream.width = 1920
            stream.height = 1080
            stream.pix_fmt = 'yuv420p'
            stream.codec_context.thread_count = 4
            stream.options = {'crf': '20', 'preset': 'fast'}
            while True:
                size = struct.unpack('>I', receive(peer, 4))[0]
                if size == 0:
                    break
                if size != 1920 * 1080 * 4 or frames >= 600:
                    raise RuntimeError(f'Unexpected native frame: {frames}, {size}')
                pixels = np.frombuffer(receive(peer, size), dtype=np.uint8).reshape(1080, 1920, 4)
                frame = av.VideoFrame.from_ndarray(pixels, format='rgba')
                for packet in stream.encode(frame):
                    movie.mux(packet)
                frames += 1
                if frames % 120 == 0:
                    print(f'NATIVE_CAPTURE {frames}/600', flush=True)
            for packet in stream.encode():
                movie.mux(packet)
        if child.wait(timeout=30) != 0 or frames != 600:
            raise RuntimeError(f'Incomplete owned capture: {frames} frames')
    finally:
        if child.poll() is None:
            child.terminate()
            child.wait(timeout=15)

paths = ['scripts/combat/cover_navigation.gd', 'scripts/combat/site7_enemy_tactics.gd',
         'scripts/actors/operator_actor.gd', 'scripts/actors/enemy_actor.gd',
         'scripts/combat/prototype_projectile.gd', 'scripts/missions/site7_environment_prop.gd',
         'scripts/ui/battle_reticle.gd', 'scripts/ui/story_stage_hud.gd',
         'scripts/animation/boss_phase_transition_guard.gd', 'scripts/ui/enemy_overhead_ui.gd',
         'data/visual/site7_environment_props.json', 'data/art_profiles/enemy_profiles.json',
         'tests/render/battle_video_10s_capture.gd', 'tools/environment/capture_battle_review.py']
report = {'recorded_utc': datetime.now(timezone.utc).isoformat(), 'frames': frames,
          'native_resolution': [1920, 1080], 'fps': 60, 'duration_seconds': 10,
          'clock': 'fixed simulation; not a wall-clock performance measurement',
          'audio': 'silent technical review; runtime SFX not disabled in production',
          'dependency_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
          'video_sha256': hashlib.sha256((OUT / 'site7_cover_combat_10s.mp4').read_bytes()).hexdigest(),
          'quality_approval': False}
(OUT / 'encode_manifest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(OUT, flush=True)
