"""Summarize all new downloads and their provenance for local use."""
from pathlib import Path
from collections import Counter
import hashlib
import json

ROOT = Path(__file__).resolve().parent
LIBRARY = Path("C:/ai_asset/karchive/2026-09-23")
receipt = json.loads((ROOT / "download_receipt.json").read_text(encoding="utf-8"))
summary = receipt["summary"]
rows = receipt["files"]
catalog = json.loads((ROOT / "downloads_summary.json").read_text(encoding="utf-8"))
groups = json.loads((ROOT / "group_summary.json").read_text(encoding="utf-8"))
prior = json.loads(Path("qa/karchive_asset_intake_20260919/completion_receipt.json").read_text(encoding="utf-8"))
assert prior["downloaded_glbs"] == 6400

label = {"video": "영상", "image": "이미지", "fashion": "패션 이미지", "source": "배경 소스", "recipe": "레시피 예시"}
lines = ["# kArchive 추가 무료 다운로드 조사 및 보관", "",
         "2026-09-23 · 원본 다운로드 버튼이 있는 3D 이외 자료를 수집했다. 기존 3D 6,400개는 `C:/ai_asset/karchive/2026-09-19`에 그대로 보관했다.", "",
         f"새 보관 위치: `{LIBRARY}`", "",
         f"사이트 홈: https://karchive.vibeline.co.kr/ · 조사한 카테고리 그룹: {sum(groups['groups_by_category'].values())} · 개별 게시물: {groups['post_count']}", "",
         "| 카테고리 | 다운로드한 고유 파일 | 사이트 |", "|---|---:|---|"]
for cat in ("video", "image", "fashion", "source", "recipe"):
    lines.append(f"| {label[cat]} | {summary['by_category'].get(cat, 0):,} | https://karchive.vibeline.co.kr/{cat} |")
lines += ["", f"총 {summary['downloaded_count']:,}개 · {summary['downloaded_bytes']:,} bytes ({summary['downloaded_bytes']/2**30:.2f} GiB).",
          "", "오디오·음악 목록은 검사 시점에 비어 있었다. 기존 3D 아카이브는 중복 다운로드하지 않았다.", "",
          "모든 항목은 사이트의 `/api/download` 버튼 주소로 받았다. 파일 서명과 전송 크기를 검사했고, 프로젝트 임시 보관본과 C: 최종 파일의 SHA-256이 일치한다. 상세 출처 페이지, 원본 링크, 이름, 바이트 수, 해시는 `download_receipt.json`에 기록했다.", "",
          "이 자료는 보관 및 검토용이다. 이미지·패션·배경·영상·레시피 페이지에서 3D 전체 ZIP과 동일한 상업 사용 허가를 확인하지 못했다. 일부 레시피는 원 저작자 출처를 따로 밝힌다. 해당 파일을 SABLE 소스 아트, 학습 데이터 또는 제품에 사용하려면 항목별 권리를 먼저 확인해야 한다.", "",
          "3D에 대한 기존 승인과 출처 표시는 원래 묶음에 한정한다. SABLE 캐릭터·배경의 ImageGen 원화 권한, 적 체형, 현재 런타임 자산 포인터는 이 다운로드로 바뀌지 않는다.", "",
          "## 검증 결과", "", f"- 다운로드 상태: `{summary['status']}`", f"- 카탈로그에서 찾은 고유 파일: {catalog['unique_source_files']:,}개", f"- 파일 서명 및 SHA-256 검증: {len(rows):,}개", f"- 오류: {len(summary['failures'])}개", ""]
if summary["failures"]:
    lines += ["## 받지 못한 파일", ""]
    for fail in summary["failures"]:
        lines.append(f"- {fail['page_url']} — {fail['error']}")

report = "\n".join(lines) + "\n"
(ROOT / "REPORT_KO.md").write_text(report, encoding="utf-8")
(LIBRARY / "REPORT_KO.md").write_text(report, encoding="utf-8")
print(json.dumps({"report": str(ROOT / "REPORT_KO.md"), "files": len(rows), "status": summary["status"]}, ensure_ascii=False))
