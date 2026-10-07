# 2026-10-02 정리: 프로젝트 폴더의 쓸데없는 파일과 C: temp

**판정: 영구 삭제는 하지 않았다.** 사용자 지시(2026-10-02, "C드라이브 temp 와 D 드라이브 프로젝트 폴더 내 쓸데 없는 것들 좀 지워라")에 따라 프로젝트의 쓸데없는 파일 8.2 GiB(2,896개)를 `_retired_20261002/`로 옮겼다(같은 드라이브에서 이름만 바꾸기, 실패 0). 최종 삭제는 2026-09-24, 2026-09-28 정리와 같은 방식으로 사용자가 한다. C: temp는 옮기지 않고 측정만 했다. 추적 파일은 건드리지 않았다. 이 정리는 기술 정리일 뿐 그림, 균형, 플레이 승인이 아니다.

## 1. 옮긴 것 (`tools/maintenance/retire_20261002.py`)

| 자리 | 파일 | 용량 | 무엇 |
|---|---:|---:|---|
| `.cache/diag` | 2,155 | 3,890 MB | Codex 진단 캡처(PNG, WebP). 작전 6–10 판 작업의 단계 A–E 비교 이미지 등 |
| `.cache/claude_scratch` | 646 | 2,616 MB | Claude 작업용 캡처, 영상, 증거 사본. 최종본은 커밋된 `qa/site7_op*_enable_*` 기록에 있다 |
| `qa/site7_boss_robots_20260928_final/video_210940/stage1`–`stage5` | 10 | 1,770 MB | 녹화기 중간 파일 `native_readback.mkv` 5개와 `native_mix.avi` 5개. 1080p mp4와 `capture.json`의 SHA-256은 그대로다 |
| `.cache/tmp` | 37 | 79 MB | 2026-09-28 작업 캡처 |
| `.cache/site7_ops_a` | 48 | 55 MB | 단계 A 작업 캡처 |
| 합계 | 2,896 | 8,410 MB | |

모든 파일의 SHA-256, 크기, 옮긴 자리는 `retirement_manifest.jsonl`(2,896줄)에 있다. 복구는 `_retired_20261002/<같은 상대 경로>`를 원래 자리로 옮기면 된다. `_retired_20261002/`는 `.gitignore`에 올렸다.

고르는 기준은 `.cache/` 안의 이미지와 영상(Godot 사용자 자료와 바이트코드 접두사 폴더 제외)과 `qa/`의 녹화기 중간 파일뿐이다. 이 프로젝트에서 최근 한 시간 안에 쓴 파일, 추적 파일, 링크는 건너뛰게 되어 있다(이번에는 건너뛴 것이 없었다). 옮기기 전에 Codex와 러너가 이 프로젝트에서 일하지 않는 것을 확인했다. Codex의 파이썬 작업 하나(`qa/evidence/P1/...`, 이 프로젝트에 없는 경로)와 주식 프로그램의 파이썬 프로세스가 돌고 있었으나, 최근 10분 안에 이 폴더에 쓰인 파일은 새 도구 하나뿐이었다.

## 2. 남긴 것과 이유

| 자리 | 용량 | 이유 |
|---|---:|---|
| `.cache/` 안의 로그, JSON, 스크립트, 메모 | 약 40 MB | 앞으로 쓰는 도구가 있다(`claude_scratch/codex_activity.ps1`, `s9_seam_preview2.py`, `op10_enable/bot_stats_gen.py` 등) |
| `.cache/Godot`, `godot_appdata`, `godot_localappdata`, `python` | 약 40 MB | Godot 사용자 자료, 러너가 Godot를 C:에 쓰지 않게 돌리는 폴더, 바이트코드 접두사 |
| `.godot/` | 1.8 GB | Godot 가져오기 캐시. 지우면 다음 실행이 모두 다시 가져온다 |
| `web_demo/` | 2.0 GB | 웹 데모 배포용 별도 Git(Site ID 포함, `.git`이 1.8 GB)과 `dist`(239 MB). 갱신에 필요하고 `.claude/launch.json`이 `web_demo/dist`를 제공한다 |
| `tools/blender/` | 1.3 GB | 설치 문서(`docs/ART_PRODUCTION/BLENDER_5_2_1_INSTALL.md`)가 zip과 SHA-256을 가리킨다 |
| `qa/`의 기록 캡처와 영상 | 약 0.8 GB | 각 기록의 README가 인용한다 |
| `qa/regression_runs/` | 81 MB | 오늘 기록이 인용한 실행이 들어 있다 |
| `.git` | 3.9 GB | 건드리지 않았다 |

## 3. C: temp 측정 (옮기지 않았다)

`%LOCALAPPDATA%\Temp`는 모두 약 2.0 GB다(C: 여유 926 GB).

- `claude\`는 1.1 GB로 가장 크지만 다른 프로젝트의 Claude 세션 작업 폴더이고 지금도 쓰이는 것(AFTER SIGNAL 642 MB 등)이 있어 건드리지 않는다. 이 프로젝트의 몫은 거의 0이다(작업 파일을 `.cache/claude_scratch`에 두기 때문이다).
- 그 밖에서 2일 이상 손대지 않은 것: **821개, 378 MB.** Paseo 첨부 99.6 MB, `cat.json` 93.4 MB, Codex 클립보드 PNG 81 MB(82개), `*.tmp` 77 MB(344개), AFTER SIGNAL 검토 폴더 13 MB, 나머지 Codex와 Chromium 임시 파일이다. 일부는 다른 프로젝트나 도구의 것이므로 사용자가 직접 지운다.

## 4. 최종 삭제 (사용자가 실행)

`tools/maintenance/purge_20261002.py`는 `_retired_20261002/`와 위의 오래된 temp 항목을 지운다(`claude\`는 건드리지 않고, 링크는 따라가지 않고, 쓰고 있는 파일은 건너뛴다).

```
python tools/maintenance/purge_20261002.py            # 미리보기, 지우지 않는다
python tools/maintenance/purge_20261002.py --apply    # 삭제
```

미리보기 결과(이 기록을 쓸 때): `_retired_20261002/` 8.21 GB와 temp 821개 378 MB. 영구 삭제는 사용자 몫이라는 규칙에 따라 Claude는 `--apply`를 돌리지 않았다.

## 5. 확인

- 옮긴 뒤 `.cache/`(제외 폴더 빼고)에 이미지와 영상이 0개, `qa/`에 `native_readback.mkv`와 `native_mix.avi`가 0개, 보존한 스크립트가 그대로 있다.
- `_retired_20261002/`에 2,896개 8.3 GB가 있고 매니페스트가 2,896줄이다.
- 추적 파일의 변경은 `.gitignore` 한 줄과 도구 둘(`retire_20261002.py`, `purge_20261002.py`), 이 기록뿐이다.
