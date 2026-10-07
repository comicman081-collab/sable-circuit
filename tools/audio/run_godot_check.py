"""Bounded owned Godot check with project-local output and hidden native window."""
from pathlib import Path
import os
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
qa = root/'qa/sfx_integration_20260919'
qa.mkdir(parents=True, exist_ok=True)
env = os.environ.copy()
env.update(TEMP=str(qa), TMP=str(qa))
startup = subprocess.STARTUPINFO()
startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startup.wShowWindow = 0
godot = 'D:/AI 종합 폴더/Godot/4.7.1-standard/Godot_v4.7.1-stable_win64.exe'
result = subprocess.run([godot, '--path', str(root), *sys.argv[1:]], cwd=root, env=env,
                        startupinfo=startup, timeout=240)
sys.exit(result.returncode)
