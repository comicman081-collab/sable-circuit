# 항목 1D — 방 규칙 OVERRUN (가장 작은 형태)

작성 2026-10-06 밤 · 작성자 Claude · 구현 `25fc3c31` · 근거 `docs/production/SITE7_EXPANSION_1_3_CODEX_ORDER_KO.md` 3.5절(요구)과 9.17절(검수 표)

## 판정: 기술 PASS — 규칙 장치와 시험은 끝났고, 어느 방에도 규칙을 두지 않았다

사용자가 "남은것들 해"라고 해서 지시서 3.5절의 선택 항목 1D를 시작했다. Codex가 닫혀 있어 구현과 검수를 모두 Claude가 했다. 3.5절의 예("연구실에서 F를 누르면 30초 버티기")는 새 전투 바닥·덮개·스폰 슬롯 행과 여러 시험의 확장이 필요한 큰 일이라 **하지 않았다.** 대신 3.5절이 시작하게 되면 지키라고 한 네 줄(데이터에 선언, 키가 없으면 HEAD와 똑같이, `ROOM_TYPES` 불변, HUD에 보임, 같은 검수 표)을 그대로 지키는 규칙 하나를 만들었다.

**지금 게임에는 달라진 것이 없다.** 어느 임무 파일의 어느 방도 `"rule"` 키를 갖지 않는다(`room_rule` 시험이 열 파일 80개 방을 읽어 0개를 확인한다). 어디에 몇 초로 둘지는 사람이 쏴 본 기록이 없는 난이도 결정이라 **사용자의 몫**이고, 두게 되면 미션 행만 고친 한 커밋으로 해서 그 커밋 하나를 되돌리면 지금 난이도가 된다.

## 1. 규칙이 하는 일

전투 방 행에 `"rule": {"type": "OVERRUN", "seconds": n}`을 쓴다(`encounter` · `reinforcements` · `hazards` 옆). `seconds`는 20–120이고 생략하면 45다.

- 스테이지는 **직전 파도를 부른 때부터** n초가 지나면 다음 증원 파도를 부른다. 앞 파도가 `reinforce_at`까지 줄었든 아니든 부른다.
- 부르는 방식은 기존 증원과 같다. `_call_reinforcements()`가 `_on_story_enemy_defeated`가 늘 돌리던 네 줄(파도 번호, 시계 0, 적이 남았으면 1.4 s 없으면 2.2 s 기다림, 목표 문구)을 한 곳으로 옮긴 것이다. 바닥의 진입 표시가 먼저 그려지고 로봇은 그 뒤에 나타난다.
- 앞 파도를 먼저 줄여 증원이 불리면 그 호출이 시계를 다시 센다.
- 피해를 더하지 않고, 로봇 그림 · 보상 · 소리를 건드리지 않는다.
- HUD는 정보 줄 밑(x 924–1256, y 100–118)에 `OVERRUN // NEXT WAVE IN n`을 붉게 보이고, 파도가 들어오는 동안과 남은 파도가 없을 때는 숨긴다. 브리핑 줄이 규칙을 설명한다.
- 보스 방, 훈련 시뮬레이터(`battle_preview`), 키가 없는 방은 예전과 같다. 쓸 수 없는 규칙(객체 아님 · 모르는 종류 · 보스 방 · 증원 없는 방 · 초 범위 밖)은 `push_error`로 적고 그 방은 규칙 없이 돈다.

코드: `scripts/combat/room_rule.gd`(표와 검증, 순수 함수), `data/progression/room_rules.json`, `scripts/missions/story_stage_01.gd`(시작 · 틱 · 호출 · 정리), `scripts/ui/story_stage_hud.gd`(줄 하나). 시험 `tests/smoke/room_rule_smoke.gd`(87검사)는 러너에 `room_rule`(quick)로 올라 있다.

## 2. 시험이 보는 것 (87검사)

표와 한계 · 검증기의 거절 아홉 가지 · 순수 타이머와 HUD 줄 · 임무 파일 열 개의 80개 방 · 살아 있는 스테이지(30초 규칙이 정확히 30.0초에 부르고 29초에는 부르지 않음 · 앞 파도를 먼저 줄인 경로 · 규칙 없는 방이 120초 동안 부르지 않음 · 두 파도 방이 직전 호출부터 세고 화면이 다시 켜짐 · 거절 다섯 가지 · 시뮬레이터 · 방 바꿈 · HUD 사각형이 정보·화물·상태·교신 상자와 겹치지 않고 1280×720 안).

시험을 쓰다가 **실제 결함 하나**를 찾았다. 앞 파도를 먼저 줄여 증원이 불린 직후, 카운트다운이 한 프레임 묵은 값을 보였다. `_call_reinforcements()`가 화면 줄을 바로 갱신하게 고쳤다(시험을 느슨하게 하지 않았다).

## 3. 규칙 깨기 (R-07) — 변형 26개 모두 잡힘, 정상 배치 통제 1개는 통과

실제 트리의 파일 하나를 바이트 백업해 두고 변형 하나씩 적용한 뒤 `room_rule_smoke.gd`를 직접 돌렸다(낮은 우선순위, 한 번에 하나, 14 s씩). 끝나면 백업에서 복원하고 바이트가 같은지 비교했다. **`RESTORED_BYTES_EQUAL True`**, `git status`에서 게임 파일 변화 0.

통제(변형 없음)는 87검사 PASS. 아래 표의 숫자는 87검사 가운데 **빨개진 검사 수**다. 스크립트 오류는 28회(통제 1 + 변형 27) 모두 0이었다(실패가 시험이 아니라 깨진 스크립트 때문이 아니라는 뜻).

| # | 변형 | 무엇을 깼나 | 빨간 검사 |
|---|---|---|---|
| 1 | `timer_boundary_gt` | 정확히 n초에 부르지 않고 넘어야 부른다(`>=` → `>`) | 13 |
| 2 | `timer_ignores_wave_wait` | 증원이 들어오는 중에도 타이머가 부른다 | 1 |
| 3 | `timer_ignores_pending` | 남은 파도가 없어도 부른다 | 2 |
| 4 | `clock_not_reset_on_call` | 부른 뒤 시계를 0으로 돌리지 않는다 | 6 |
| 5 | `line_not_refreshed_on_call` | 부른 직후 HUD 줄을 갱신하지 않는다(2절의 결함) | 1 |
| 6 | `entry_wait_changed` | 대기를 항상 1.4 s로(비어 있을 때의 2.2 s를 지운다) | 2 |
| 7 | `thinned_path_no_call` | 앞 파도를 줄여도 증원을 부르지 않는다(기존 경로 끊김) | 4 |
| 8 | `tick_not_called` | `_process`가 타이머를 돌리지 않는다 | 15 |
| 9 | `rule_never_begun` | 방에 들어가도 규칙을 시작하지 않는다 | 16 |
| 10 | `rule_in_simulator` | 훈련 시뮬레이터에도 규칙이 선다 | 1 |
| 11 | `rule_survives_clear` | 방을 비워도 규칙이 남는다 | 1 |
| 12 | `rule_inherited_by_next_room` | 다음 방이 앞 방의 규칙을 이어받는다 | 1 |
| 13 | `tip_missing` | 브리핑 줄에 규칙 설명이 없다 | 1 |
| 14 | `boss_room_allowed` | 보스 방도 규칙을 받는다 | 3 |
| 15 | `no_wave_check_dropped` | 증원이 없는 방도 규칙을 받는다 | 3 |
| 16 | `seconds_floor_dropped` | 초 하한(20) 검사를 뺀다 | 5 |
| 17 | `seconds_ceiling_dropped` | 초 상한(120) 검사를 뺀다 | 2 |
| 18 | `hud_countdown_floor` | 카운트다운을 올림이 아니라 내림으로 | 3 |
| 19 | `hud_shown_while_wave_inbound` | 파도가 들어오는 동안에도 HUD가 보인다 | 1 |
| 20 | `hud_label_overlaps_intel` | HUD 상자를 정보 줄과 겹치게 옮긴다 | 2 |
| 21 | `hud_label_off_screen` | HUD 상자를 화면 밖으로 옮긴다 | 1 |
| 22 | `data_default_seconds_30` | 데이터의 기본 초를 45에서 30으로 | 2 |
| 23 | `data_min_seconds_5` | 데이터의 하한을 20에서 5로 | 4 |
| 24 | `data_tip_too_long` | 설명이 교신 상자에 안 들어갈 만큼 길다 | 1 |
| 25 | `mission_row_bad_seconds` | 작전 3의 증원 방에 `seconds: 5` | 1 |
| 26 | `mission_row_on_boss` | 작전 3의 보스 방에 규칙 | 1 |
| 통제 | `mission_row_valid_placement` | 작전 3의 증원 방에 `seconds: 40`(정상 배치) | **0 (통과해야 한다)** |

**읽을 때 주의.** 빨간 검사가 1개뿐인 변형이 11개다(# 2, 5, 10–13, 19, 21, 24–26). 잡히긴 했지만 한 검사에만 기대는 규칙이다. 그 검사가 약해지면 그 규칙은 지켜지지 않는다. 변형 25와 26은 실제 임무 파일에 규칙을 심은 것이라 이 시험이 **나중에 누가 임무 파일에 규칙을 잘못 두는 것**을 막는다는 증거이고, 통제는 올바른 배치가 시험을 깨지 않는다는 증거다.

재현(Godot가 필요하다, 다른 Godot와 러너가 모두 꺼져 있을 때만): `tools/mutate_room_rule.py`는 내 스크래치 도우미(`.cache/claude_scratch/item1_review/run_godot_low.sh`, Godot를 낮은 우선순위로 한 번 돌리는 스크립트)를 부른다. 그 경로가 없으면 `RUNNER`를 바꿔야 한다. 약 7분.

## 3b. 러너 전체(quick)

`python tools/maintenance/run_regression_suite.py` — **58/58 PASS**, 562 s, `qa/` 가드 변경 0 · 삭제 0 · 추가 0(`qa/regression_runs/20261006_231916_quick`, 커밋 `25fc3c31`). `room_rule`은 러너 안에서도 87검사 PASS(12 s). `battle_flow` · `combat_entry` · `m2_story` · `elite_expansion`(증원 호출 2.2 s 검사 포함) · `hazard_expansion` · `contract_ui` · `redline` · `boss_duel` · `boss_room_fairness` · `title_geometry` 모두 PASS.

증원 호출을 한 함수로 모은 변경(`_call_reinforcements()`)은 실제 플레이로도 지나갔다. 전체 전용 `campaign`(235검사)과 한 작전에서 증원이 실제로 불리는 봇 `full_op_01` · `full_op_02` · `full_op_04` · `full_op_05` · `full_op_09`를 러너로 돌렸다: **6/6 PASS**, 796 s, `qa/` 가드 0 · 0 · 0(`qa/regression_runs/20261006_233054_custom`, 커밋 `5362a7c6`, 봇은 134 · 124 · 172 · 162 · 164 s에 탈출, 봇 기록의 `wave`가 0에서 1로 올라간다). 불안정한 봇(작전 3 · 6 · 7 · 8 · 10)은 이 확인에서 뺐다: 지는 것이 소음인 시험이라 이 변경의 판정이 되지 못한다.

## 4. 그림 · 소리 · 한계

- 보스 공정성(`boss_pattern` · `boss_room_fairness`의 대기 시간 바닥과 180 px · 0.25 s), `upgrade_economy`의 띠, x2 클램프, "피해 전에 텔레그래프" 규칙을 건드린 줄이 없다. 로봇 그림에 색을 입히지 않는다. 새 그림 · 소리가 없다.
- 승인한 작전 10 그림 17개의 해시는 `verify_hashes.py`로 확인한다(결과는 9.17절).

## 5. 열려 있는 것

- 어느 방에 몇 초로 둘지(난이도 결정). 사람이 쏴 본 기록이 없다(`playtest_logs/` 비어 있음).
- 3.5절의 큰 형태(연구실 전투)는 새 바닥 · 덮개 · 스폰 슬롯이 필요한 일이고 시작하지 않았다.
- 이 기록은 그림 · 플레이 · 균형 승인이 아니다.

## 6. 파일

- `records/mutants.jsonl` — 변형 27행과 통제 1행(결과 · 검사 수 · 실패한 검사의 앞 세 줄)
- `records/room_rule_smoke_control.json` — 통제 실행의 시험 출력(87검사, 실패 0)
- `tools/mutate_room_rule.py` — 변형 표와 적용 · 복원 스크립트(위 재현 주의 참고)
