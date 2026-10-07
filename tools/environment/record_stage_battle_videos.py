"""Record one real ten-second Chapter 01 combat clip for each current stage."""
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import subprocess

import av
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
GODOT = Path('D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64.exe')
OUT = ROOT / 'qa/stage_battle_videos_20260919' / ('capture_' + datetime.now().strftime('%H%M%S'))
ROWS = [
    ('stage1_bulwark', 'MIS_CH01_01', 'ENM_SITE7_BULWARK_01'),
    ('stage2_cinder', 'MIS_CH01_02', 'ENM_SITE7_RAM_01'),
    ('stage3_vesper', 'MIS_CH01_03', 'ENM_SITE7_MORTAR_01'),
]
SIZE, FPS, FRAMES = (1920, 1080), 60, 600

def receive(peer, length):
    data = bytearray()
    while len(data) < length:
        piece = peer.recv(length - len(data))
        if not piece:
            raise RuntimeError('Godot stopped before every video frame was received')
        data.extend(piece)
    return bytes(data)

def capture(name, mission_id, expected_enemy):
    folder = OUT / name
    folder.mkdir(parents=True, exist_ok=False)
    cache = folder / 'cache'
    cache.mkdir()
    env = os.environ.copy()
    env.update({'SABLE_CAPTURE_OUTPUT': str(folder), 'SABLE_CAPTURE_MISSION': mission_id,
                'TEMP': str(cache), 'TMP': str(cache), 'XDG_CACHE_HOME': str(cache),
                'PYTHONPYCACHEPREFIX': str(cache / 'pycache'), 'PYTHONDONTWRITEBYTECODE': '1'})
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(('127.0.0.1', 0)); server.listen(1); server.settimeout(90)
        env['SABLE_CAPTURE_PORT'] = str(server.getsockname()[1])
        command = [str(GODOT), '--path', str(ROOT), '--script', 'res://tests/render/stage_battle_video_10s_capture.gd',
                   '--resolution', '1920x1080', '--fixed-fps', str(FPS), '--disable-vsync', '--audio-driver', 'Dummy',
                   '--log-file', str(folder / 'godot.log')]
        with (folder / 'process.log').open('w', encoding='utf-8') as log:
            child = subprocess.Popen(command, cwd=ROOT, env=env, startupinfo=startup, stdout=log, stderr=subprocess.STDOUT)
            (folder / 'process.json').write_text(json.dumps({'pid': child.pid, 'command': command}, indent=2), encoding='utf-8')
            count = 0
            video = folder / (name + '_10s_1080p.mp4')
            try:
                peer, _ = server.accept()
                with peer, av.open(str(video), 'w', options={'movflags': '+faststart'}) as movie:
                    stream = movie.add_stream('libx264', rate=FPS)
                    stream.width, stream.height = SIZE
                    stream.pix_fmt = 'yuv420p'
                    stream.options = {'crf': '18', 'preset': 'fast'}
                    peer.settimeout(90)
                    while True:
                        length = struct.unpack('>I', receive(peer, 4))[0]
                        if length == 0:
                            break
                        if length != SIZE[0] * SIZE[1] * 4 or count >= FRAMES:
                            raise RuntimeError(f'Unexpected frame {count}: {length}')
                        picture = Image.frombytes('RGBA', SIZE, receive(peer, length)).convert('RGB')
                        frame = av.VideoFrame.from_image(picture)
                        frame.pts, frame.time_base = count, Fraction(1, FPS)
                        for packet in stream.encode(frame): movie.mux(packet)
                        count += 1
                    for packet in stream.encode(): movie.mux(packet)
                if child.wait(timeout=30) != 0:
                    raise RuntimeError(f'Godot exit code {child.returncode}')
            finally:
                if child.poll() is None:
                    child.terminate(); child.wait(timeout=15)
    with av.open(str(video)) as movie:
        decoded = sum(1 for _ in movie.decode(video=0))
        duration = float(movie.streams.video[0].duration * movie.streams.video[0].time_base)
    report = json.loads((folder / 'capture.json').read_text(encoding='utf-8'))
    if count != FRAMES or decoded != FRAMES or abs(duration - 10) >= .01:
        raise RuntimeError(f'Video validation failed: written={count}, decoded={decoded}, duration={duration}')
    if expected_enemy not in report['seen_enemy_ids']:
        raise RuntimeError(f'{mission_id} did not show its expected enemy: {expected_enemy}')
    return {'stage': name, 'mission_id': mission_id, 'expected_enemy': expected_enemy,
            'seen_enemy_ids': report['seen_enemy_ids'], 'frames': decoded, 'fps': FPS,
            'duration_seconds': duration, 'native_resolution': list(SIZE), 'audio': False,
            'video': video.relative_to(ROOT).as_posix(), 'video_sha256': hashlib.sha256(video.read_bytes()).hexdigest(),
            'capture_sha256': hashlib.sha256((folder / 'capture.json').read_bytes()).hexdigest()}

def main():
    OUT.mkdir(parents=True, exist_ok=False)
    clips = [capture(*row) for row in ROWS]
    report = {'status': 'PASS_TECHNICAL_NATIVE_STAGE_COMBAT_CAPTURE', 'recorded_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Controlled app input and real Stage 01 combat. Silent capture; not a human playtest or performance benchmark.',
              'clips': clips, 'capture_script_sha256': hashlib.sha256((ROOT / 'tests/render/stage_battle_video_10s_capture.gd').read_bytes()).hexdigest(),
              'recorder_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'output': str(OUT), 'clips': [clip['video'] for clip in clips]}, ensure_ascii=False))

if __name__ == '__main__':
    main()
