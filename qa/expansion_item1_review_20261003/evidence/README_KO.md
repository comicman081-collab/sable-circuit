# 증거 목록 (항목 1 검수, 2026-10-03)

`../REVIEW_KO.md`의 숫자가 나온 파일이다. 검수 대상은 `dca7ef20..a6eb1d35`이고 비교 기준선은 `7dfe367e`(항목 1 이전 코드)다. 사본은 `.cache/claude_scratch/proj_base`, `proj_after`에서 만들었고 저장소 작업 트리는 건드리지 않았다.

| 파일 | 내용 |
|---|---|
| `mutations.md` | 규칙을 일부러 깬 변형 18개와 결과(15 잡힘, 3 놓침) |
| `bots_ab.md` | 작전 6–10 봇 20판(기준선 대 변경)의 판별 표 |
| `raw/mutations_main_results.json`, `raw/mutations_b1_extra_results.json` | 변형 결과 원자료 |
| `raw/b2_time_bomb_demo.txt` | B-2: 정당한 미션 수정에서 `variety_placement`가 실패하는 재현 |
| `raw/escape_25px_{base,after}.json`, `raw/escape_10px_after_ops6-9.json`, `raw/escape_grids.log` | 장판 탈출 격자 |
| `raw/json_compare.txt` | 미션 JSON 비교(V-31) |
| `raw/fps_ab_summary.log`, `raw/fps_ab_all_reports.json` | 같은 세션 회전 FPS A/B |
| `raw/nav_audit_{base,after}_12px.json`, `raw/nav_audit_12px.log`, `raw/nav_audit_main_project_12px.{json,log}` | 길찾기 막다른 구역 감사(70칸/4방). 기준선과 변경 사본의 JSON이 같다 |
| `raw/nav_pocket_probe_{base,after}_op9_r04.json` | 작전 9 R04 정지 지점 주변의 영벡터 칸 |
| `raw/bots_ab.jsonl` | 봇 판별 원자료 |
| `raw/bot_runs/<사본>_<작전>_<짝>.json` | 봇 20판 각각의 `full_operation.json`(결과, 방별·원천별 피해, 틱별 체력 추적). `bots_report.py`는 원래 작업 사본의 `.cache/bot_out/…/full_operation.json`을 읽었고, 사본은 검수 뒤 지웠으므로 이 폴더가 원본이다 |
| `raw/visual_validation_rerun.json` | 캡처 14장 검증기 재실행 |
| `raw/quick_46_of_46_SUMMARY_KO.md`, `raw/full_only_21_of_21_SUMMARY_KO.md` | 러너 요약(실행 폴더 `qa/regression_runs/20261003_111607_quick/`, `…_120432_custom/`은 git에서 제외되어 있어 이 사본이 기록이다) |
| `tools/` | 위 측정에 쓴 도구의 사본(기록용). 원본은 `.cache/claude_scratch/item1_review/`에서 돌렸고 경로는 거기에 맞춰져 있다. 저장소 도구는 `tools/environment/audit_nav_pockets.gd` 하나다 |

## 재확인 증거 (`recheck_753cf029/`, 10절)

Codex의 보완 커밋 `753cf029`를 별도 사본(`git archive`)에서 다시 깬 기록이다. 사본은 만들고 지웠다(`tools/make_snapshot.sh`, `tools/drop_snapshot.sh`).

| 파일 | 내용 |
|---|---|
| `recheck_753cf029/raw/mutations_fix.log`, `raw/mutations_fix_results.json` | 변형 없는 시험 4개(정예 438, 장판 438, 정예 기존 71, 장판 기존 366)와 정예 시험 대상 변형 19개의 결과(놓침 0) |
| `recheck_753cf029/raw/py_place_results.json` | 배치 시험 14경우(정당한 후속 수정, 디스크의 실제 위반, 다른 커밋 쌍, 이력 없음)의 결과 |
| `recheck_753cf029/tools/mutate_fix.py`, `py_place_check.py` | 위 두 측정 도구 |
| `recheck_753cf029/tools/make_snapshot.sh`, `drop_snapshot.sh`, `run_godot_low.sh`, `lowrun.py` | 사본 만들기, 안전하게 지우기(링크 6개를 먼저 끊고 남은 링크가 0일 때만 삭제), 낮은 우선순위로 Godot 돌리기 |
| `recheck_753cf029/tools/nav_direction_dump.gd`, `nav_dump_diff.py` | N-1 재검수용: 모든 전투 방 격자 칸의 길찾기 방향을 떠서 수정 전후를 칸 단위로 비교(수정 전 12 px 105,535칸 기준은 떠 놨다) |

이 기록은 그림·플레이·균형 승인이 아니다.
