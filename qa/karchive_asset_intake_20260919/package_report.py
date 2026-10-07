from pathlib import Path
from collections import Counter
from PIL import Image, ImageDraw, ImageFont
import hashlib
import json

ROOT = Path(__file__).resolve().parent
LIBRARY = Path("C:/ai_asset/karchive/2026-09-19")
items = json.loads((ROOT / "shortlist.json").read_text(encoding="utf-8"))
renders = json.loads((ROOT / "render_receipts.json").read_text(encoding="utf-8"))
inventory = json.loads((ROOT / "inventory.json").read_text(encoding="utf-8"))
verification = json.loads((ROOT / "download_verification.json").read_text(encoding="utf-8"))
assert len(items) == len(renders) == 12

labels = [
    ("보급 상자 / 닫힘", "높음", "O01_SUPPLY 보급품·회수 상자", "단순한 실루엣과 군용 녹색이 어울림. 충돌·상호작용 영역 별도 제작."),
    ("보급 상자 / 공구", "조건부", "보급품을 열어 둔 정적 소품", "닫힌 상자와 크기·형상이 다름. 동일 상자의 개폐 프레임으로 바로 교체하지 말 것."),
    ("비상 발전기", "높음", "R06_LIFT 전력 복구 장치", "발전기 외형이 명확함. 전원 표시·소리·상호작용은 별도 구현."),
    ("배터리 뱅크", "높음", "격리시설 전력·에너지 회수 소품", "배터리 뭉치의 반복 구조가 읽힘. 실제 단위·발광 표현 조정 필요."),
    ("의료 캐비닛", "높음", "O01_SUPPLY 의약품 보관", "보관함과 내용물 포함. 문·내용물이 하나의 메시라 분리 동작에는 가공 필요."),
    ("무전 장비 책상", "높음", "R03_ARCHIVE / O02_RESEARCH 통신 단말", "단말의 기능이 읽히는 실루엣. 기존 SF UI 및 팔레트와 조율 필요."),
    ("콘크리트 차단물", "높음", "R01_GATE 진입 통제·엄폐물", "넓은 덩어리와 경고 줄무늬가 유용. 캐릭터 가림 및 충돌 크기 검토 필요."),
    ("모래주머니 엄폐물", "높음", "외곽 경계·엄폐 라인", "낮은 엄폐 형태가 명확함. 연구소 내부보다 외곽 구역에 적합."),
    ("연료 드럼 랙", "높음", "비상 전원실·위험물 적재", "적재물·탱크 형태로 쓰기 좋음. 폭발 기믹과 경고는 별도 게임 디자인."),
    ("보급품 사물함", "높음", "보급실·대기실 수납", "내용물 있는 정적 소품. 이동 경로와 시야를 가리지 않도록 배치 조정."),
    ("방호 출입문", "조건부", "R04_JUNCTION 격리 출입문", "문은 단일 메시이며 애니메이션 없음. 개폐 구조·피벗·통로 크기부터 검토."),
    ("산업용 전기 접속함", "높음", "R02_DECON / R06_LIFT 시설 전기 소품", "시설물의 용도가 읽힘. 터미널 기능·조작 표시·파손 상태를 별도 정의."),
]

font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 34)
small = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 24)
title_font = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 56)
sheet = Image.new("RGB", (3840, 2160), "#101820")
draw = ImageDraw.Draw(sheet)
draw.text((56, 25), "kArchive · SABLE CIRCUIT 환경·소품 후보 12종", font=title_font, fill="#f2f5f8")
draw.text((58, 100), "실제 GLB 렌더 / 원본은 각각 1920×1080 / 이 목록은 활용성 검토이며 게임 적용 승인이 아닙니다.", font=small, fill="#aec0cb")
for i, (entry, render, detail) in enumerate(zip(items, renders, labels)):
    x, y = 48 + (i % 4) * 940, 165 + (i // 4) * 640
    with Image.open(render["output"]) as source:
        assert source.size == (1920, 1080)
        preview = source.convert("RGB").resize((912, 513), Image.Resampling.LANCZOS)
    sheet.paste(preview, (x, y))
    draw.text((x + 8, y + 524), f"{i+1:02d}  {detail[0]}", font=font, fill="#f0f4f8")
    draw.text((x + 8, y + 570), f"{entry['triangles_mesh_sum']:,} triangles · Godot import OK · 정적 메시", font=small, fill="#a6c3d0")
draw.text((58, 2095), "자료: kArchive   |   출처: 쓰레드 dogfooter   |   Original assets preserved in C:\\ai_asset\\karchive\\2026-09-19", font=small, fill="#96aab8")
sheet.save(ROOT / "shortlist_overview_3840x2160.png")

lines = ["# kArchive 3D 자산 — SABLE CIRCUIT 활용 검토", "", "2026-09-19 · 다운로드·검사 완료. 런타임 자산 승격이나 게임 파일 변경은 하지 않음.", "",
         "## 저장 및 검증", "", f"- 저장 폴더: `{LIBRARY}`", f"- 전체 원본 ZIP: `all-6400.zip` — {verification['archive_bytes']:,} bytes (4.03 GiB)",
         f"- 압축 해제: `models/rounded` 3,000개 / `models/angular` 3,000개 / `models/crops-fish` 400개", 
         f"- 압축 해제 용량: {verification['unpacked_bytes']:,} bytes (4.62 GiB), 원본 ZIP 포함 약 8.65 GiB", 
         "- 전체 6,401 ZIP 항목 CRC 및 6,400 GLB의 헤더·길이·JSON 구조 검사 통과. 외부 파일 의존성 없음.",
         "- 각 파일 SHA-256 및 구조 정보: `inventory.json`. ZIP SHA-256: `" + verification['archive_sha256'] + "`.",
         "- 이것은 전체 glTF 표준 적합성·모든 면의 미술 품질·게임 성능을 보증하는 검사가 아님.", "",
         "## 프로젝트 적합성", "", "활용할 만한 자산이 있다. 우선순위는 **angular의 생존·시설·수납 소품**이다. 보급실, 격리시설 외곽, 비상 전원실, 통신실에 잘 맞는다. 농작물·생선과 귀여운 생활/온천/식당 계열은 현재 SITE-7의 우선순위가 낮다.", "",
         "전체 6,400개는 모두 메시 1개·재질 1개·이미지 1개이며, 스킨·애니메이션이 없다. 삼각형 수는 603–10,452, 중앙값 5,681이다. 따라서 환경과 정적 소품 후보로 보는 것이 적절하다. 플레이어 동작, 적 로봇의 방향별 애니메이션, 움직이는 문을 바로 공급하는 패키지는 아니다.", "",
         "현재 프로젝트는 2D/2.5D 탑다운과 ImageGen 원화 권한을 유지한다. 이번 3D 검토 렌더는 참고용이며 원화나 런타임 스프라이트로 승격되지 않는다. 실제 적용 단계에는 현재 아트 규칙에 맞는 제작 경로, 게임 시점·팔레트·실제 크기·충돌·가림 처리가 필요하다. 현재 승인된 플레이어·드론·앵커 및 적 체형 제한은 유지한다.", "",
         "## 실제 파일을 확인한 우선 후보", "", "| 후보 | 적합성 | 예상 용도 | 삼각형 | 조건 |", "|---|---|---|---:|---|"]
for i, (entry, detail) in enumerate(zip(items, labels)):
    lines.append(f"| [{i+1:02d} {detail[0]}]({Path(entry['local_path']).as_posix()}) | {detail[1]} | {detail[2]} | {entry['triangles_mesh_sum']:,} | {detail[3]} |")
lines += ["", "12개 파일은 별도 Godot 4.7.2 프로젝트에서 GLTFDocument 로드 및 장면 생성에 성공했다(`godot_import_receipt.json`). 이 결과는 실제 SABLE 플레이, 충돌, 웹 성능 또는 아트 승인까지 포함하지 않는다.", "",
          "각 1920×1080 원본 렌더는 `renders/`, 전체 요약 이미지는 `shortlist_overview_3840x2160.png`에 있다. Blender Cycles CPU로 직접 렌더했으며 저해상도 렌더를 확대하지 않았다. 검토는 고정된 한 방향에서 이뤄졌으므로 후면·내부·가려진 면은 적용 전 별도 확인이 필요하다.", "",
          "특히 01 닫힌 상자와 02 열린 상자는 원본 바운딩 크기부터 다르다(약 0.767×0.550×0.463 대 0.536×0.361×0.500). 이름이 유사해도 같은 상자의 호환 애니메이션 상태로 가정하면 안 된다. 문·서랍·뚜껑은 독립 리그 없이 한 메시 안에 묶여 있다.", "",
          "## 이용 조건과 출처", "", "공식 페이지: https://karchive.vibeline.co.kr/models", "",
          "페이지에 개인·상업 프로젝트 사용 및 수정 가능, AI 학습 사용 가능, 원본 재판매 금지, 출처 표기 필수가 명시되어 있다. 사용자가 이 조건을 확인하고 다운로드 진행을 승인했다.", "",
          "프로젝트에서 사용할 때 다음 출처를 라이선스 화면·크레딧·설명란 등에 표기한다:", "", "```text", "자료: kArchive", "출처: 쓰레드 dogfooter", "```", "",
          "원본 ZIP의 LICENSE.txt 역시 개인·상업 프로젝트 사용 및 수정을 허용한다. 단 AI 학습 항목은 ZIP에서 금지하고 웹페이지에서 허용하므로 원문을 모두 보존했다. 이번 다운로드·3D 검사·활용성 검토는 상업 프로젝트 사용 허용과 충돌하지 않는다. 이번 작업에서 AI 학습은 수행하지 않았다.", "",
          "웹페이지 스냅샷: `models.html`, 추출 텍스트: `models_page_text.txt`, ZIP 원문: `bundled_LICENSE.txt`, 라이선스 기록: `model-license-manifest.json`.", "",
          "## 파일 찾기", "", "- `models/angular/angular-apocalypse-*`: 비상 전원, 의료, 보급, 엄폐, 방호문 등 우선 탐색", "- `models/angular/angular-common-infrastructure-*`: 접속함·설비·바닥 등", "- `models/rounded/`: 같은 주제의 둥근 스타일 및 변형", "- `models/crops-fish/`: 현재 전투 연구시설보다 다른 프로젝트의 농업·음식·생활 용도", "",
          "원본 파일은 그대로 보관한다. 가공·변환·재질 수정·렌더·Godot 작업은 SABLE 프로젝트 내부 복사본 또는 프로젝트 출력 경로에서 수행한다."]
report = "\n".join(lines) + "\n"
(ROOT / "RECOMMENDATIONS_KO.md").write_text(report, encoding="utf-8")
(LIBRARY / "SABLE_RECOMMENDATIONS_KO.md").write_text(report, encoding="utf-8")
(LIBRARY / "ATTRIBUTION.txt").write_text("자료: kArchive\n출처: 쓰레드 dogfooter\nhttps://karchive.vibeline.co.kr/models\n", encoding="utf-8")
(LIBRARY / "SABLE_SHORTLIST.json").write_text(json.dumps([{**entry, "label_ko": detail[0], "suitability": detail[1], "use_case": detail[2], "caveat": detail[3]} for entry, detail in zip(items, labels)], ensure_ascii=False, indent=2), encoding="utf-8")
duplicate_count = len(inventory) - len({x["sha256"] for x in inventory})
print(json.dumps({"report": str(ROOT / 'RECOMMENDATIONS_KO.md'), "contact_sheet": str(ROOT / 'shortlist_overview_3840x2160.png'), "byte_identical_duplicate_glbs": duplicate_count}, ensure_ascii=False))
