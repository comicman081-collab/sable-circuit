# 항목 3 검수 후속 기록 (Claude, 2026-10-06 저녁)

Codex의 항목 3(`98292b3d`)과 그 위에 내가 사용자 지시("돌리기 전에 코드 수정할꺼 해라")로 한 손질(`4fd9d502`, `0a14d5b6`)을
Godot로 직접 돌려 확인한 기록이다. 서술과 판정은 `../REVIEW_KO.md`의 후속 절에 있다. 이 폴더는 증거만 담는다.
검사한 코드는 깨끗한 `0a14d5b6`이고, 이 폴더를 더한 커밋은 코드가 같다(`qa/`만 늘었다).

| 폴더 | 내용 |
|---|---|
| `runs/` | 내 quick 전체(56/56 PASS, 621 s, `git_dirty` 0, `qa/` 보호 변경 0)와 `--only m10_intel,m13_loadout,campaign,lab_capture_geometry`(4/4 PASS)의 러너 요약. `quick_vs_codex_quick.txt`는 Codex의 quick(`d6094211`, 56/56)과 검사 수를 맞춘 것: 다른 곳은 `weapon_expansion` 122 → 131, `lab_geometry` 3,694 → 4,005뿐이고 둘 다 내 손질이 더한 검사다. **풀 스위트**: `full_ccfaa96e_summary.json` · `…_SUMMARY_KO.md`(88개 가운데 **87 PASS, `full_op_08`만 FAIL**, 5,268 s, `git_dirty` 0, 가드 0·0·0), 그 FAIL을 `--only full_op_08`로 다시 돌린 `rerun_full_op_08_ccfaa96e_*`(**또 FAIL**, 144 s, 가드 0·0·0), 두 실행의 봇 보고서 `full_op_08_wipe_run1_report.json` · `…run2_report.json`(둘 다 보스방 `R05_TERMINAL` 전멸, 추적 줄 포함), `full_vs_quick.txt`(풀 실행 안의 quick 56개는 내 quick과 검사 수가 모두 같다: 차이 0, 빠진 것 0). |
| `matrix/` | 규칙 깨기 표. 변형 27개를 복사본(`proj_i3`, `0a14d5b6`)에 한 번에 하나씩 적용하고 시험을 돌렸다(`i3_table.md`가 표, `i3_matrix.jsonl`이 원자료, `all.log`가 진행 줄, `base*.log`가 변형 없는 기준). `native_control.log` / `native_wait1.log`는 T-8 변형만 1080p 네이티브 캡처로 확인한 실행(통제 PASS 19검사, 변형 FAIL). |
| `probes/` | 저장 왕복: 같은 저장 파일(v3·v4·v5 고정물과 새 코드로 만든 가득 찬 v6)을 옛 코드(`381ef0fb`, 형식 5)와 새 코드(형식 6)가 어떻게 읽는지(`compare_saves_out.txt`). 손질의 측정: `profile_bench_out.txt`(T-4), `results_layout_probe_out.txt`(T-1, 열 작전 × 두 결과). |
| `polish_native/` | 손질 뒤 1080p 네이티브 캡처 중 바뀐 세 장(결과 화면 T-1, 두 무기 발사 T-2)과 `capture_report.json`, 1080p 검증기 보고(`validator_report.json`: 컨테이너와 동적 캡처 PASS, 화질 주장 아님, 세 PNG의 SHA-256 포함). PNG는 `.gitignore`의 `qa/**/*.png` 때문에 git에 들어가지 않고 이 작업 사본에만 있다. |
| `tools/` | 위를 만든 도구 전부(복사본 만들기·변형 적용·표 만들기·네이티브 실행·저장 탐침, 풀 실행과 quick 줄 맞추기 `compare_full_vs_quick.py`). 복사본 둘(`proj_i3`, `proj_i3old`)은 풀 스위트가 끝난 뒤 지웠고, 만들던 초안과 로그는 git에 안 들어가는 `.cache/claude_scratch/item3_review/`에 있다. |

기술 확인일 뿐 그림·균형·플레이 승인이 아니다. 모듈·무기·연구 수치는 아직 아무도 플레이하지 않은 제안이다.
