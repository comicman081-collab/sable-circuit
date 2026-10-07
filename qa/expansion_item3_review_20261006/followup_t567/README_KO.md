# 항목 3 후속 T-5 · T-6 · T-7 기록 (Claude, 2026-10-06 밤)

사용자의 지시("다 고쳐", "T6도 네가 알아서")로 고친 세 줄(T-5 HUD 상자, T-6 연구소 글, T-7 음악 가져오기 설정)을
Godot로 직접 확인한 기록이다. 서술과 판정은 `../REVIEW_KO.md`의 9절에 있다. 이 폴더는 증거만 담는다.
검사한 트리는 커밋 `e88d6459` 위에 다섯 파일이 고쳐진 상태(`git_dirty` 5)였고, 그 다섯 파일을 세 커밋
`92cc7eb3`(T-5) · `4d0ae528`(T-6) · `cfcb065a`(T-7)으로 나눠 넣었다. 커밋한 파일의 git blob이 검사한 것과
모두 같다(`runs/tested_blobs.txt`와 `git rev-parse HEAD:<경로>` 비교).

| 폴더 | 내용 |
|---|---|
| `runs/` | quick 전체(`quick_20261006_210605_quick_*`, **56/56 PASS**, 531 s, `qa/` 가드 0·0·0)와 보조 4개(`only4_20261006_211542_custom_*`, `m10_intel` 39 · `m13_loadout` 53 · `campaign` 235 · `lab_capture_geometry` 5, **4/4 PASS**, 54 s). `quick_vs_previous_quick.txt`는 이전 quick(`0a14d5b6`)과 시험별로 줄을 맞춘 것: 다른 시험은 `lab_geometry` 4,005 → 5,089 하나이고 55개는 상태와 검사 수가 같다. `tested_blobs.txt`는 검사한 다섯 파일의 git blob이다 |
| `native/` | 1080p 네이티브 캡처의 `capture_report.json`(7장의 SHA-256, 19검사 PASS)과 1080p 검증기 보고 `validator_report.json`(컨테이너와 동적 캡처 PASS, 화질 주장 아님), 캡처 로그, PNG 3장(`lab_page1` · `lab_module_cycle` · `field_intel8`). PNG는 `.gitignore`의 `qa/**/*.png` 때문에 git에 들어가지 않고 이 작업 사본에만 있다(나머지 4장은 보고서의 SHA-256만 남는다) |
| `break/` | 규칙 깨기 표(`mutants_table.md`)와 원자료 `mutants.jsonl`: 변형 9개를 실제 트리에 한 번에 하나씩 적용해 `lab_geometry`를 돌렸다(8개 잡힘, 1개는 같은 효과의 변형) |
| `probes/` | 연구소 줄의 실제 자리와 너비(`module_rows_probe_out.txt`, `ui_probe_out.txt`: 543 px · 169 / 187 / 120 px · HUD 글 324 px), T-5만 있는 트리에서 돌린 `lab_geometry`(`state_a_lab_geometry.json`, 4,007검사 PASS, T-6 커밋을 되돌린 트리와 같다), 러너 가져오기 로그의 오류 줄 수 앞뒤(`import_logs_before_after.txt`: 58개는 3줄, 뒤 2개는 0줄) |
| `tools/` | 위를 만든 도구: 변형 적용기 `mutate_t567.py`, 줄 맞추기 `compare_quick.py`, 폴더 조립 `build_evidence.py`, 커밋을 나누려고 트리를 T-5 상태로 만들고 되돌린 `make_state_a.py` · `restore_full.py`, 탐침 `ui_probe.gd` · `module_rows_probe.gd`(`qa/.gdignore`가 있어 Godot가 이 폴더의 스크립트를 가져오지 않는다) |

기술 확인일 뿐 그림·균형·플레이 승인이 아니다. 모듈·무기·연구 수치는 아직 아무도 플레이하지 않은 제안이고,
T-6의 새 연구소 줄은 사람이 화면에서 보고 정할 내 설계다.
