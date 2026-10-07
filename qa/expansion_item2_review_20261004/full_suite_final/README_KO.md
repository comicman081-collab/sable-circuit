# 항목 2 풀 스위트 확인 (K-13) — 2026-10-05

`docs/production/SITE7_EXPANSION_1_3_CODEX_ORDER_KO.md` 9.12절의 근거 파일이다. 이 기록은 그림·플레이·균형 승인이 아니다.

## 결과 한 줄

커밋 `04eba6c3`(게임 코드는 `4158aaaa` 이후 그대로)에서 러너의 83개 시험 가운데 **81개 PASS, 2개 FAIL**이다. FAIL은 `full_op_06`과 `full_op_10`이고 둘 다 봇이 보스방에서 전멸한 것이다(두 번씩). 항목 2의 기준 K-13은 충족이다.

## 세 번의 실행

작업 트리는 세 번 모두 깨끗했고(`git status` 빈 출력) 커밋은 `04eba6c3`이다. Godot 4.7.1, 러너 `tools/maintenance/run_regression_suite.py`.

| 실행 | 시각 | 무엇을 | 결과 |
|---|---|---|---|
| 1차 `20261005_200721_full` (git 무시 폴더) | 20:07–20:37 | `--suite full` (83개) | 사용자가 Godot를 멈추라고 해서 도중에 끊었다. 53개가 끝났고 로그의 결과 줄은 전부 PASS, 실패 줄 0. 러너가 `summary.json`과 `qa/` 보호 검사를 쓰기 전에 죽어서 종료 코드는 기록이 없다 |
| 2차 `20261005_210052_custom` | 21:00–22:08 | 1차에서 못 끝낸 30개 (`--only`, 이름은 `part2_only.txt`) | 28 PASS, 2 FAIL (`full_op_06`, `full_op_10`). `qa/` 기존 파일 변경·삭제·추가 0건 |
| 3차 `20261005_220907_custom` | 22:09–22:14 | 위 둘만 다시 | 둘 다 FAIL. `qa/` 0건 |

1차의 53개가 PASS라는 근거는 로그의 결과 줄이다(`part1_finished.md`, 로그마다 SHA-256은 `part1_log_sha256.json`). 1차의 `qa/` 보호 검사는 없었지만, 그 뒤 `git status`가 깨끗했고(`qa/`에 추가·변경 없음) 2차·3차 검사도 0건이다. 시험별 최종 결과 83줄은 `results_83.md`.

## 밀려 있던 Godot 시험 7개

`battle_flow` PASS · `combat_entry` PASS · `deploy_warmer` PASS (83검사) · `hazard_expansion` PASS (438검사, 15개 방) · `m13_campaign` · `m13_migration` · `m13_runtime` PASS. `contract_ui` 484검사와 `campaign` 235검사(B-1에 걸렸던 시험)도 이 팁에서 PASS다.

## K-13의 판정: PASS

기준 문구: "러너에 `run_contract`가 있고 quick이다. `full_op_01`–`10`은 기본 계약으로 HEAD와 같이 돈다."

- `run_contract`는 러너의 quick 묶음에 있고 34검사 PASS다.
- 열 개 플레이스루는 모두 기본(중립) 계약으로 돌았다. 실행 ID가 기술 시험용(`MIS_CH01_0N-TECHNICAL-PL…`)이라 `result.run_contract`가 `{}`다(`wiped_runs.md`, 열 개 전부 확인).
- 항목 2가 바꾼 전투 쪽 코드는 두 줄뿐이고 이 경로에서는 아무것도 바꾸지 않는다: `story_stage_01.gd`의 `RunContract.enemy_modifiers(_enemy_run_modifiers_with_mode(), identity)`는 REDLINE이 아니면 입력 그대로를 돌려주고(`run_contract.gd:64`), `EnemyActor.apply_run_modifiers`는 체력·피해·속도·간격 배율 네 키만 읽는다(`enemy_actor.gd:122`). 추가된 `hazard_id`와 `opportunity_id`는 읽히지 않는다. 나머지 변경(`briefing_screen.gd`, `mission_results.gd`, `base_lobby.gd`, `campaign_progression.gd`, `play_session_log.gd`, `game_flow.gd`)은 화면·저장·기록이다(`git diff --stat 7b26a152 HEAD -- scripts data scenes assets`: 8개 파일, +186 −6).

## 실패 두 건은 항목 2의 것이 아니다

`wiped_runs.md`: 작전 6은 AERATOR TOWER를 504·512 / 1,560까지 깎고 전멸(159 s, 161 s), 작전 10은 로봇 27개를 다 잡고 ORIGIN CORE 811 / 2,460에서 전멸(171 s)했고 재시험에서는 로봇 25개를 잡고 981에서 전멸(143 s)했다. 둘 다 **전멸**이지 경로·보상·탈출 결함이 아니다.

- 이 봇은 예전부터 이 두 작전에서 흔들렸다: 작전 6은 N-1 풀 스위트(`20261003_170533_full`)에서 한 번 보스방에서 전멸하고 재시험에 통과했다. 작전 10은 개설 때 6판 중 5판 통과였다.
- N-1 검수(길찾기 수정 `48a0bd28` 전후)에서 같은 봇은 작전 6이 수정 전 4/5, 후 3/5, 작전 10이 수정 전 1/3, 후 0/3이었다. 이번에 같은 팁에서 작전 6 0/2, 작전 10 0/2가 더해진다. 수정 이후만 합치면 작전 6은 3/7, 작전 10은 0/5다.
- 이 PC에서 봇 결과는 부하에 크게 흔들린다(같은 길찾기가 항목 1 검수에서 4/4, N-1 검수에서 1/6이었다). 그래서 이 숫자로 원인을 가리지 못한다. 길찾기 수정이나 항목 1의 배치(작전 6의 SPORE_CLOUD·BROODING)가 봇을 약하게 했을 수는 있으나 **측정하지 않았다**. 항목 2는 위에서 보인 대로 이 봇의 전투 경로에 닿지 않는다.
- 수정, 임계값 변경, 러너가 전멸을 재시도하게 하는 것은 균형·도구 정책이라 사용자의 몫이다. 이번에는 아무것도 바꾸지 않았다.

## 하지 않은 것

- 항목 2 이전 커밋(`7b26a152`)과 같은 세션에서 번갈아 돌려 보는 A/B는 하지 않았다. Godot를 더 쓰지 않으려는 선택이고, 위의 코드 경로 논증이 항목 2에 대한 답이다.
- 1차 실행의 종료 코드는 확인하지 못했다(위).
- 사람 플레이, 그림, 균형 승인은 없다. `playtest_logs/`는 비어 있다.

## 파일

`results_83.md` · `wiped_runs.md` · `part1_finished.md` · `part1_summary.json` · `part1_log_sha256.json` · `part2_only.txt` · `part2_summary.json` · `part2_SUMMARY_KO.md` · `part3_summary.json` · `part3_SUMMARY_KO.md` · `raw/`(전멸한 네 판의 `full_operation.json`과 로그, 2차·3차의 러너 출력) · `MANIFEST.json`(저장된 LF 바이트의 SHA-256). 러너가 CRLF로 쓴 파일은 LF로 바꿔 두었다(내용은 같다).
