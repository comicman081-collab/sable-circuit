# REDLINE 수치 결정의 근거 (2026-10-04)

`docs/production/SITE7_EXPANSION_1_3_CODEX_ORDER_KO.md` 9.11절의 표와 봇 실험이 나온 파일이다. 결정과 이유는 거기에 있고, 이 폴더는 숫자의 출처만 적는다.
이 기록은 그림·플레이·균형 승인이 아니다. 사람 플레이는 없다(`playtest_logs/`가 비어 있다).

## 무엇이 어느 파일에서 나왔나

| 9.11의 내용 | 도구(`tools/`) | 결과 |
|---|---|---|
| 표준 카드 4장과 REDLINE 이전·이후의 P(= 체력 × 피해 ÷ 간격), 보스 경고 한 방, 쓰러지는 횟수, 환율 k | `pressure_table.py` (`data/progression/run_modifiers.json`을 읽는다) | `pressure_table.md` |
| 작전 1 봇 조합 5개 (이전 값 · 이후 값 · 더 약한 값 × 업그레이드 없음 / 병기고 6단계) | `bot_arms2.gd`, `bot_arms2.sh`, `bots_arms2_report.py` | `bots_arms2.md`, `raw/bots_arms2.jsonl`, `raw/bot_runs/rl_1_<조합>_<라운드>.json` (판마다 `full_operation.json`) |
| 지정 시험 11개 PASS | 저장소의 `tools/maintenance/run_regression_suite.py --only …` | `raw/targeted_11_tests.log`, `raw/targeted_11_tests_SUMMARY_KO.md`, `raw/targeted_11_tests_summary.json` |
| quick 전체 (사용자 지시로 38/52에서 끊김, 실패 0) | 같은 러너 `--suite quick` | `raw/quick_interrupted_38_of_52.log` (끝의 `exit=127`은 내가 러너를 끊은 것) |
| Godot 없이 따로 돌린 파이썬 시험 6개와 `world_layout`의 같은 결과 확인, 승인된 그림 17/17 | `tools/py_tests.sh` (러너와 같은 명령, 낮은 우선순위) | `raw/python_tests/` |
| 파일마다 SHA-256 | | `MANIFEST.json` |

## 봇 실험 (작전 1)

- 사본은 `f2cbe1d6`(코드는 `b4aa2ae0`과 같다)의 `git archive`이고 저장소 작업 트리는 건드리지 않았다. 조합마다 라운드를 돌려 가며 한 번에 하나씩 돌렸고 낮은 우선순위, 화면 없음(`--headless`)이다.
- `--contract=redline:<체력>,<피해>,<속도>,<간격>`은 `RunContract.redline()`이 만든 계약의 적 배율 네 개만 덮어쓴다(식별자, 보스 예외, 보상은 그대로). `--damage=<x>`는 `configure_campaign`의 스냅샷 `damage_multiplier`(병기고 6단계 = 1 + 0.08 × 6 = 1.48)다. 저장·장비·모듈은 쓰지 않는다.
- 계획은 5조합 × 3라운드 15판이었고 **11판에서 멈췄다**: 사용자가 다른 작업이 Godot를 써야 한다고 해서다. 라운드 2의 `P1`은 71 s에서 내가 끊었고 그 행은 기록에서 뺐다(`raw/bots_arms2.jsonl`에는 없다). `P0`·`M0`·`M1`의 라운드 2는 시작하지 않았다.
- 결과는 `bots_arms2.md`: 11판이 모두 추출이다. 앞선 세션(항목 2 검수 5.3절, `evidence/raw/bots_arms.jsonl`)에서 **같은 이전 값**은 3판 중 0이었다.

### 정정

항목 2 검수(9.10, `REVIEW_KO.md` 5.3절)와 사용자 보고에 "REDLINE 3판 중 0 추출"을 적었다. 이번 세션에서는 같은 값을 업그레이드 없는 봇이 2판 모두 추출했다(합쳐서 5판 중 2판). 그 0/3은 REDLINE이 너무 세다는 증거로 읽으면 안 된다. 이 봇의 추출 개수는 설정의 세기를 가르는 눈금이 아니다. 두 세션의 부하가 달랐고, 판 수가 적고, 받은 피해가 조합과 상관이 약했다(`bots_arms2.md`의 이후 값이 이전 값보다 큰 판이 있다). 9.11은 낮춘 근거를 봇이 아니라 표준 카드와의 환율에서 댄다.

## 시험 (이 트리 = `125be138` + 상수 커밋 `4158aaaa`의 변경)

- 지정 시험 11개 PASS: `boss_duel` 2,184 · `run_contract` 34 · `contract_offers` 26,950 · `redline` 78 · `contract_save` 69 · `play_log` 25 · `demo_integration` 26 · `m10_intel` 39 · `m13_loadout` 46 · `campaign` 235 · `contract_ui` 484.
- quick 전체는 38/52에서 끊겼다(실패 0). 파이썬 시험은 `world_layout`(10작전), `mood_light`(150판 788풀), `walk_registration`, `plate_axis`(2), `variety_placement`(10), `seam_waiver`(10), `mood_contact`(13)가 모두 통과, 승인된 그림 17/17 변경 없음.
- **못 돌린 것:** Godot 시험 7개(`battle_flow` `combat_entry` `deploy_warmer` `hazard_expansion` `m13_campaign` `m13_migration` `m13_runtime`)와 풀 스위트(K-13).

## 한계

봇은 사람이 아니다. 11판은 적고 두 세션의 부하가 다르다. `pressure_table.py`의 P는 어림값이다(속도와 적 종류별 사격 비율을 넣지 않았다). 이 숫자들은 잠정 결정의 근거일 뿐 균형 승인이 아니다.

줄 끝은 LF로 맞췄다(러너와 도구가 CRLF로 쓴 로그 몇 개를 바꿨고, 내용은 같다). `MANIFEST.json`의 SHA-256은 저장된 그 바이트의 것이다.
