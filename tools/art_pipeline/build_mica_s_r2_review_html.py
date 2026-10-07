#!/usr/bin/env python3
"""Build a self-contained visual review page for the MICA S R2 pilot.

The page is intentionally evidence-only: it embeds the already-rendered PNG
frames and the two independently captured 5-second videos.  It does not alter
the candidate or promote any asset.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
from pathlib import Path


def data_url(path: Path, mime: str) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidate",
        type=Path,
        default=Path(
            "art_src/characters/mica/fast_pipeline/motion/"
            "candidate_mica_c03_v8_r13_s_segmented_ual"
        ),
    )
    parser.add_argument(
        "--review-dir",
        type=Path,
        default=Path("artifacts/mica_c03_v8_r13_s_segmented_review_r2"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "artifacts/mica_c03_v8_r13_s_segmented_review_r2/"
            "MICA_C03_V8_R13_S_R2_REVIEW.html"
        ),
    )
    args = parser.parse_args()

    frame_dir = args.candidate / "blender_frames" / "S" / "move"
    frames = []
    for index in range(24):
        path = frame_dir / f"{index:02d}.png"
        if not path.is_file():
            raise FileNotFoundError(path)
        frames.append(data_url(path, "image/png"))

    fixed = args.review_dir / "MICA_C03_V8_R13_S_R2_FIXED_GRID_5S_1920X1080.mp4"
    world = args.review_dir / "MICA_C03_V8_R13_S_R2_WORLD_GRID_5S_1920X1080.mp4"
    sheet = args.review_dir / "MICA_C03_V8_R13_S_R2_S_GAIT_REVIEW_2304X1080.png"
    validator = args.review_dir / "MICA_C03_V8_R13_S_R2_VISUAL_EVIDENCE_VALIDATION.json"
    for path in (fixed, world, sheet, validator):
        if not path.is_file():
            raise FileNotFoundError(path)

    validator_obj = json.loads(validator.read_text(encoding="utf-8"))
    validator_text = json.dumps(validator_obj, ensure_ascii=False, indent=2)
    sheet_url = data_url(sheet, "image/png")
    fixed_url = data_url(fixed, "video/mp4")
    world_url = data_url(world, "video/mp4")
    frames_json = json.dumps(frames)

    document = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MICA C03 V8 R13 S R2 — 검수 증거</title>
  <style>
    :root {{ color-scheme: dark; font-family: "Segoe UI", system-ui, sans-serif; background:#071019; color:#eaf4ff; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; background:linear-gradient(#152536,#071019 55%); }}
    main {{ width:min(100%, 2048px); margin:0 auto; padding:18px; }}
    h1 {{ margin:0 0 5px; font-size:clamp(20px,2.4vw,34px); letter-spacing:.04em; }}
    p {{ color:#a8bed0; }} .badge {{ color:#9ff5ce; font-weight:700; }}
    .stage {{ border:1px solid #3e6b86; background:#050b10; }}
    canvas {{ display:block; width:100%; height:auto; aspect-ratio:16/9; }}
    .controls {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin:12px 0; }}
    button, select, input {{ border:1px solid #5685a2; background:#102537; color:#ecf9ff; padding:8px 11px; font-weight:700; }}
    input[type=range] {{ flex:1 1 260px; accent-color:#7de2ff; }}
    .readout {{ border-left:3px solid #7de2ff; padding:8px 12px; background:#0c1823; color:#d6e7f4; line-height:1.5; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:12px; margin-top:14px; }}
    figure {{ margin:0; padding:10px; background:#0c1823; border:1px solid #25475c; }}
    figure img, figure video {{ width:100%; height:auto; display:block; background:#050b10; }}
    figcaption {{ color:#bdd0dd; font-size:13px; margin-top:7px; }}
    details {{ margin-top:14px; background:#0c1823; padding:10px; }}
    pre {{ white-space:pre-wrap; overflow:auto; color:#b9d4e5; font-size:12px; }}
  </style>
</head>
<body>
<main>
  <h1>MICA C03 V8 R13 S R2 · 독립 검수 증거</h1>
  <p><span class="badge">후보 상태: UNREVIEWED_DO_NOT_PROMOTE</span> · S 방향 · 24 프레임 UAL 분절 하체 · 삭제/승격 금지</p>
  <div class="stage"><canvas id="stage" width="1920" height="1080" aria-label="S 방향 고정/월드 보행 증거"></canvas></div>
  <div class="controls">
    <label>표시 <select id="mode"><option value="fixed">fixed-grid</option><option value="world">world-grid(합성 미리보기)</option></select></label>
    <button id="play" type="button">재생</button><button id="prev" type="button">이전</button><button id="next" type="button">다음</button>
    <input id="frame" type="range" min="0" max="23" step="1" value="0" aria-label="프레임">
    <span id="frameLabel">F00</span>
  </div>
  <div class="readout" id="readout">S R2 증거를 불러오는 중입니다…</div>
  <section class="grid">
    <figure><img src="{sheet_url}" alt="S R2 24단계 정적 검수 시트"><figcaption>2304×1080 정적 24단계 시트</figcaption></figure>
    <figure><video controls preload="metadata" src="{fixed_url}"></video><figcaption>fixed-grid · 1920×1080 · 24fps · 5초</figcaption></figure>
    <figure><video controls preload="metadata" src="{world_url}"></video><figcaption>world-grid · 1920×1080 · 24fps · 5초 · 지지발 마커</figcaption></figure>
  </section>
  <details><summary>컨테이너 검증 결과</summary><pre>{html.escape(validator_text)}</pre></details>
</main>
<script>
(() => {{
  const frames = {frames_json};
  const canvas = document.querySelector('#stage'), ctx = canvas.getContext('2d');
  const mode = document.querySelector('#mode'), slider = document.querySelector('#frame');
  const label = document.querySelector('#frameLabel'), readout = document.querySelector('#readout');
  const images = frames.map((src) => {{ const image = new Image(); image.src = src; return image; }});
  let index = 0, playing = false, last = performance.now();
  function drawGrid() {{
    const grad = ctx.createLinearGradient(0,0,0,1080); grad.addColorStop(0,'#0a1722'); grad.addColorStop(1,'#03080d');
    ctx.fillStyle = grad; ctx.fillRect(0,0,1920,1080);
    ctx.save(); ctx.translate(960,560); ctx.strokeStyle='rgba(95,180,215,.16)'; ctx.lineWidth=2;
    for (let y=-650;y<=650;y+=82) {{ ctx.beginPath();ctx.moveTo(-1100,y);ctx.lineTo(1100,y);ctx.stroke(); }}
    for (let x=-1100;x<=1100;x+=82) {{ ctx.beginPath();ctx.moveTo(x,-650);ctx.lineTo(x,650);ctx.stroke(); }} ctx.restore();
    ctx.strokeStyle='rgba(125,226,255,.35)'; ctx.strokeRect(44,44,1832,992);
  }}
  function render() {{
    drawGrid(); const image=images[index]; if (!image.complete) return;
    const cell=384, size=560, rootY=mode.value==='world' ? 180 + (190*index/23) : 390;
    ctx.save(); ctx.shadowColor='rgba(0,0,0,.65)';ctx.shadowBlur=22;ctx.shadowOffsetY=16;
    ctx.drawImage(image,0,0,cell,cell,960-size/2,rootY-size/2,size,size); ctx.restore();
    if (mode.value==='world') {{
      ctx.fillStyle='#ffe17a'; ctx.beginPath(); ctx.arc(960,rootY+size*.5-24,10,0,Math.PI*2);ctx.fill();
      ctx.fillStyle='#ffe17a';ctx.font='700 22px Segoe UI';ctx.fillText('support sole marker',980,rootY+size*.5-16);
    }}
    ctx.fillStyle='#d7ecfb';ctx.font='700 28px Segoe UI';ctx.fillText(`MICA C03 S R2 · ${{mode.value.toUpperCase()}} · F${{String(index).padStart(2,'0')}}`,72,96);
    label.textContent=`F${{String(index).padStart(2,'0')}}`; slider.value=index;
    readout.innerHTML=`고정/월드 증거 프레임 <strong>F${{String(index).padStart(2,'0')}}</strong> · ${{mode.value}} · 384×384 셀 · 후보는 승격하지 않음`;
  }}
  function step(delta) {{ index=(index+delta+24)%24; render(); }}
  function tick(now) {{ if (playing && now-last>=1000/24) {{ const n=Math.floor((now-last)/(1000/24)); index=(index+n)%24; last+=n*(1000/24); render(); }} requestAnimationFrame(tick); }}
  document.querySelector('#play').onclick=()=>{{ playing=!playing; document.querySelector('#play').textContent=playing?'일시정지':'재생'; last=performance.now(); }};
  document.querySelector('#prev').onclick=()=>step(-1); document.querySelector('#next').onclick=()=>step(1);
  slider.oninput=()=>{{ index=Number(slider.value); render(); }}; mode.onchange=render;
  images[0].onload=render; requestAnimationFrame(tick);
}})();
</script>
</body>
</html>
"""
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding="utf-8")
    print(args.output)
    print(f"embedded_frames={len(frames)} embedded_videos=2 embedded_sheet=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
