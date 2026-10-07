#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VIDEO="${1:?Usage: render_video_r04.sh /path/to/original_10s.mp4}"
OUT="${2:-$ROOT/previews}"
mkdir -p "$OUT"
CREDIT='Explosion source: 2 High Quality Explosions (explode), Michel Baradari, CC BY 3.0; modified. https://opengameart.org/content/2-high-quality-explosions ; https://creativecommons.org/licenses/by/3.0/'
ffmpeg -y -v error -i "$VIDEO" -i "$ROOT/previews/COMBAT_R04_COLOSSAL_10s.wav" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 256k -t 10 -metadata "comment=$CREDIT" -movflags +faststart "$OUT/SABLE_CIRCUIT_COMBAT_SFX_R04_COLOSSAL_10s.mp4"
ffmpeg -y -v error -threads 4 -i "$VIDEO" -i "$ROOT/previews/COMBAT_R04_COLOSSAL_17s.wav" -map 0:v:0 -map 1:a:0 -vf 'tpad=stop_mode=clone:stop_duration=7' -c:v libx264 -preset veryfast -crf 20 -threads 4 -pix_fmt yuv420p -c:a aac -b:a 256k -t 17 -metadata "comment=$CREDIT" -movflags +faststart "$OUT/SABLE_CIRCUIT_COMBAT_SFX_R04_COLOSSAL_17s.mp4"
