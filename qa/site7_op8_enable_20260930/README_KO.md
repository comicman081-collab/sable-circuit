# SITE-7 작전 8 SWITCHYARD 켜기 (2026-09-30)

**판정: PASS_TECHNICAL_ONLY, 단 봇 풀플레이는 자주 진다.** 코드와 자동 시험이 통과했다는 뜻이다. 그림, 균형, 플레이 승인이 아니다. 작전 8은 이제 **출격 가능**하다. 작전 9–10은 판이 없어 그대로 출격 불가다(`deployable: false`, `staging` 유지). `full_op_08`(봇이 작전 8을 처음부터 끝까지 도는 시험)은 마지막 full 스위트에서는 통과했지만 러너에서 5번 중 2번, 열기 전 직접 실행까지 합쳐도 6번 중 3번밖에 이기지 못했다(5절). 원인은 보스나 코드가 아니라 작전 구성이라서 숫자를 바꾸지 않았고, 어떻게 할지는 사용자가 정한다(10절 1번).

사용자 지시(2026-09-30): "8 켜라". 근거는 `docs/production/SITE7_OPERATIONS_6_10_DESIGN_KO.md` 6절 C이고, 작전 6과 7을 켠 기록(`qa/site7_op6_enable_20260929/README_KO.md`, `qa/site7_op7_enable_20260930/README_KO.md`)의 교훈(갈래방 종류, 오래된 반복문 게이트, 방 바닥 공정성)을 따랐다. 켜기 전 확인은 `qa/site7_op8_preenable_20260930/README_KO.md`와 `qa/site7_op8_a1_a2_verified_20260930/README_KO.md`에 있다.

## 1. 한눈에

| 항목 | 결과 |
|---|---|
| 작전 8 켜기(6절 C 1–3) | **됨.** `staging`, `deployable: false`, `pending`을 지웠고 작전 7의 COMMAND 디브리프가 Switchyard를 알린다 |
| Codex 납품 확인 | 판 15장(방 8, 통로 7), 이음부 14개, 무드·새벽 심연·접촉 그림자, 이음부 면제 3건과 C06/C07 축 예외(사용자 승인). 3절 |
| 데이터 게이트(`campaign_data`, `campaign`, `demo_integration`) | PASS (279 / 200 / 26 검사). 오래된 반복문 게이트를 넓힌 뒤 `campaign_data`는 286검사 |
| 라이브 진입 스모크(작전 1–8) | PASS (`-s`로 직접 실행. 러너에는 없다) |
| 켜며 찾은 것 | ① **봇 풀플레이가 자주 진다**(5절). ② 라이브 진입 스모크의 `range(1, 8)`이 오래된 반복문 게이트의 감시 대상이 아니었다: 이제 대상이다(2절). ③ GANTRY의 공정성은 열기 전에 맞춰 둔 값 그대로 실제 방에서 통과했다(4절) |
| 작전 8 풀플레이(`full_op_08`) | PASS: full 스위트(`20260930_203611_full`)에서 EXTRACTED, 게임 시간 193.4 s, 적 24기. 단 **자주 진다**: 러너에서 5번 중 2번, 열기 전 직접 실행까지 6번 중 3번 이겼다(5절) |
| 실제 보스방 바닥에서의 공정성(`boss_room_fairness`) | PASS. R05_TERMINAL 격자 25 px에서 공격 5,652개 중 0개 실패, 가장 가까운 안전 바닥 최악 180 px(한도 그 자체), 가장 빠듯한 탈출 여유 0.30 s(한도 0.25 s) |
| GANTRY 자기 방 캡처(1080p) | **됨.** 7장과 1:1 크롭 시트 2장(7절) |
| 게임 소리 영상 | **됨.** 10초 600프레임, 실제 게임 믹스(8절) |
| quick·full 스위트 | 최종 커밋 `c249af7d` 위에서 quick 44/44(415초), full 71/71(4,210초) PASS, `qa/` 가드 변경 0(6절) |
| 같은 세션 회전 A/B FPS | **못 했다**(10절) |
| 사람 플레이, 균형, 그림 승인 | **못 했다.** 사용자 몫이다(10절) |

## 2. 커밋과 바뀐 것

| 커밋 | 내용 |
|---|---|
| `a186e53d` | (Codex) 작전 8 판 15장 통합: 바닥·문·월드 배치·전투 지형·엄폐·무드·램프·허공 마스크·심연 행. 작전 8은 여전히 출격 불가였다(`deployable: false`) |
| `628aeae8` | GANTRY의 2페이즈 대각 레일과 3페이즈 별·원 준비 시간을 1.6초로(열기 전에, 복사본 R05_TERMINAL 바닥에서 맞췄다) |
| `2fcb622a`, `268730f7`, `2d7a51a9` | 판 조명 축 시험의 러너 등록, C06/C07 축 예외의 문서, 이음부 3건의 이름 지정 면제(사용자 승인) |
| `5b1670f6` | 열기 전 검증 기록 `qa/site7_op8_preenable_20260930/` |
| `ed2ce9b0` | (Codex) S8_O02 노출과 새벽 접촉 그림자 마무리(A1/A2) |
| `7ed8fe3b` | A1/A2 검증 기록 `qa/site7_op8_a1_a2_verified_20260930/`, `AGENTS.md`의 새벽 접촉 그림자 대목 |
| `02f261c7` | 작전 8 켜기. 러너의 `full_op_08`, 라이브 진입 스모크의 반복 범위, 오래된 반복문 게이트의 새 대조군, 보스 캡처가 GANTRY를 자기 방에서 찍는 것 |
| `c249af7d` | 문서: `AGENTS.md`("Operation 8 enabled"), 설계 문서(상태표, 6절 C), 보스 지시서(`rail_charge`의 구현된 값), `README.md`, `sound/README.md` |
| `5ec8b9c6` | 문서 보정: `AGENTS.md`, `README.md`, 설계 문서의 러너 실행 시간과 봇 수치(마지막 full 스위트가 `full_op_08`을 이긴 뒤 다시 센 것) |
| (이 폴더를 추가한 커밋) | 이 기록. 코드는 건드리지 않았다. 커밋은 `git log -- qa/site7_op8_enable_20260930`로 찾는다 |

**켜는 순서(설계 문서 6절 C).**

| 순서 | 한 일 |
|---|---|
| 1 | `data/missions/MIS_CH01_08.json`에서 `staging` 블록을 지웠다 |
| 2 | `data/story/site7_campaign.json`의 작전 8 행에서 `"deployable": false`와 `"pending"`을 지웠다 |
| 3 | 작전 7의 COMMAND 디브리프를 `Cold Storage complete. Switchyard is now available.`로 바꿨다(데이터 게이트가 강제한다). 작전 8 자신의 디브리프는 "Switchyard complete. Refit at base."로 두었다(출격 불가인 작전 9를 이야기에 올리지 않는다. MICA의 "on no Site-7 map"은 이름을 말하지 않는다) |
| 4 | 게이트 `campaign_data`, `campaign`, `demo_integration` |
| 5 | 7에서 멈춘 곳: `tests/smoke/site7_live_entry_autostart_smoke.gd`의 `range(1, 8)`을 `range(1, 9)`로, 러너의 `full_op_%02d`를 8까지, `tests/render/site7_boss_pattern_capture.gd`의 `BOSS_IDS`에 GANTRY를 넣고 `TEST_BED`에서 뺐다(자기 방 캡처가 된다) |

**오래된 반복문 게이트의 감시 목록에 라이브 진입 스모크가 없었다.** 작전 7 기록의 게이트(`stale_loop_gaps`)는 `PER_OPERATION_FILES`에 적힌 파일만 훑는데 `tests/smoke/site7_live_entry_autostart_smoke.gd`가 그 목록에 없었다. 그 스모크의 `range(1, 8)`은 게이트가 아니라 설계 문서 6절 C의 점검 순서와 작전 7 기록이 지목해서 찾았다. 다음 작전이 같은 곳에서 빠지지 않도록 그 스모크를 목록에 넣었고(`tests/smoke/site7_campaign_data_smoke.gd`), 음성·양성 대조를 여섯 개 더했다: 붙여 쓴 일곱 작전 반복문(여덟이 출격 가능할 때 거절), 튜플 `(1,2,3,4,5,6,7)`, `"MIS_CH01_07"]`으로 끝나는 목록, 07로 끝나는 표(모두 거절), 여덟으로 넓힌 반복문·목록·표(통과), 아홉이 출격 가능해지면 여덟에서 멈춘 반복문을 이름 붙여 거절. 작전 9를 켤 때 넓힐 곳은 이 게이트가 알려 준다.

## 3. Codex 납품 확인

`qa/site7_ops_6_10_plates_20260929/stage_c/README_KO.md`(Codex의 단계 C 기록, A1/A2 마무리 포함)와 커밋 `a186e53d`, `ed2ce9b0`을 읽고, 아래를 직접 확인했다.

| 확인한 것 | 결과 |
|---|---|
| 판 15장 | 방 `S8_R01`–`R06`, 갈래 `S8_O01`, `S8_O02`, 통로 `S8_C01`–`C07`. RAW_NATIVE와 MASTER는 `art_src/environments/site7_v2/stage08/`, 게임용은 `assets/environments/site7_v2/stage08/`. Codex 기록: ImageGen 26회 호출, 15장 채택, 거절 후보 11장은 보존(반복한 벽 실루엣, 축 각도 초과 등) |
| 판이 다른 작전과 겹치지 않는가 | 겹치지 않는다. `battle_geometry`(full)가 판마다 한 작전만 쓰는지 확인한다 |
| 이음부 | 월드 레이아웃의 14개 연결 틈이 모두 0 px. 엄격 감사가 15판·14이음부 PASS(3건은 이름 지정 면제). 면제는 `S8_C01`–`R01_GATE`, `S8_C03`–`R04_JUNCTION`, `S8_C05`–`R05_TERMINAL`이고 사용자 승인(2026-09-30)이며 `seam_waiver`가 묶는다. 오른쪽 아래 갈래 통로 `S8_C06`, `S8_C07`은 바닥 축 31.5°까지(사용자 승인 2026-09-30), `plate_axis`가 묶는다 |
| 무드·램프·허공 마스크·새벽 접촉 그림자 | `mood_light --check` PASS(판 120장, 램프 풀 620개, 허공 마스크 120장, 접촉 그림자 15개). `world_layout --check` PASS(8개 작전) |
| 작전 데이터 | 방 여덟 개: R01_GATE 이벤트, R02_MARSHALLING 전투, R03_TOWER 연구(증거 "DISPATCH ORDERS"), R04_JUNCTION 엘리트, R05_TERMINAL 보스, R06_PLATFORM 탈출, 갈래 O01_DEPOT(보급) ← **R04_JUNCTION**, O02_DISPATCH(연구) ← R05_TERMINAL. 보스 SIGNAL GANTRY 체력 1,920, 패턴 `rail_charge`. 적 23기(PRISM 9, DRONE 6, MORTAR 3, RAM 2, NULL_PYLON 2, BULWARK 1). `campaign_data` 통과 |
| 엄폐 소품 | 11개(작전 1–7은 9–15개). **R05_TERMINAL의 목록이 비어 있다**(Codex 기록: 방 중앙에 엄폐물을 두지 않음). 작전 1–8에서 엄폐물이 없는 방은 이 방과 작전 7의 R05_VAULT뿐이다. 방 설계의 선택으로 보고 고치지 않았다(10절) |
| 보스 | `BOSS_SITE7_GANTRY_01`은 2026-09-29에 등록됐다(프로필, 패턴, 효과, 안내문). 열기 전에 복사본 바닥에서 준비 시간을 맞췄고(`628aeae8`), 이번에 처음 진짜 방에서 쟀다(4절) |
| 새벽 배경의 모습 | 사람이 봐야 한다(10절). 이 기록의 캡처와 영상 프레임에서 방은 어두운 철 바닥에 따뜻한 벽 램프가 켜진 모습이고, 바닥 가장자리 난간 바깥은 어두운 회갈색 안개다. 새벽으로 읽히는지는 내가 판단하지 않는다 |

## 4. 실제 보스방 바닥에서의 공정성

`tests/smoke/site7_boss_room_fairness_smoke.gd`(quick `boss_room_fairness`)는 출격 가능한 각 작전의 새 보스를 자기 방에 세우고 여섯 공격(세 페이즈 × A/B)을 모두 깐다. 대원이 설 수 있는 모든 자리(칠해진 바닥 위, 엄폐 밖, 보스에서 150–800 px)에서 경고가 덮지 않는 1.5 대원 폭의 바닥이 180 px 안에 있고, 곧게 걸어 닿을 수 있고, 가장 느린 걸음(138 px/s)이 그 자리의 경고가 터지기 0.25 s 전에 닿아야 한다.

**작전 8에서는 실패하지 않았다.** 이번에는 열기 전에 보스를 맞춰 두었다. 작전 7에서는 열자마자 이 시험이 CRYO를 잡았고, 그래서 작전 8의 방을 열기 전에 복사본(작전 8을 출격 가능 목록에 억지로 넣은 것)으로 먼저 재 보았다. 그 때 GANTRY는 50 px 격자에서 1,410개 중 101개 공격이 실패했다(2페이즈 대각 레일, 3페이즈 별과 그 원: 벽 옆에서 가장 가까운 빈 쐐기가 180 px 떨어진 자리에 예고가 1.4–1.5초라 여유가 0.10–0.20초). 준비 시간을 `GANTRY_LATE_WINDUP` = 1.6초로 늘려 실패 0이 되었고 `boss_pattern`이 1.6초와 바닥 1.56초를 고정한다(`qa/site7_op8_preenable_20260930/`). 한도(180 px, 0.25 s)는 낮추지 않았다.

이번에 진짜 방 R05_TERMINAL을 세 격자에서 쟀다(`boss_room_fairness_grid100.json`, `boss_room_fairness_grid50.json`, `boss_room_fairness_grid25.json`, 세 작전의 방이 함께 들어 있다):

| 격자 | 서 볼 자리 | 시험한 공격 | 실패 | 가장 가까운 안전 바닥(최악) | 가장 빠듯한 탈출 여유 | 엄폐 |
|---|---:|---:|---:|---:|---:|---:|
| 100 px | 58 | 348 | 0 | 180 px | 0.30 s | 0 |
| 50 px(러너 기본) | 235 | 1,410 | 0 | 180 px | 0.30 s | 0 |
| 25 px | 942 | 5,652 | 0 | 180 px | 0.30 s | 0 |

- 최악은 세 격자 모두 페이즈 3 공격 A다. 보스에서 707–776 px 떨어진 자리에서 가장 가까운 빈 바닥이 180 px이고(**한도 그 자체**) 가장 느린 걸음으로 1.30초가 걸리는데 예고는 1.60초라서 여유가 0.30초다(한도 0.25초). 통과하지만 **여유가 얇다**: R05_TERMINAL의 바닥이나 엄폐를 바꾸거나, GANTRY의 뒤 페이즈 준비 시간을 줄이면 이 시험이 먼저 실패한다. 바꿀 때는 `boss_room_fairness`를 다시 돌린다.
- 같은 실행이 작전 6의 R05_ATRIUM(최악 90 px, 여유 1.05초)과 작전 7의 R05_VAULT(최악 120 px, 여유 0.43–0.45초)도 재고, 둘 다 그대로 통과한다.
- 방에 엄폐가 0개라 엄폐가 경로를 막는 일은 없다.

## 5. 작전 8 풀플레이 — 봇이 자주 진다

`tests/smoke/site7_full_operation_smoke.gd --mission=MIS_CH01_08`(러너 `full_op_08`). 봇이 실제 액터 물리, 무기 쿨다운, 투사체 충돌, 임무 상호작용으로 진행한다(`debug_fire_once` 없음). 봇은 이동하며 쏘고, 스킬은 Q·E·X 실제 키 입력으로 쓰고, 쓰러진 대원은 F를 길게 눌러 살리고, 갈래방은 부모 방을 마친 뒤에만 들른다. 파일: `full_operation_op08_*.json`(9절).

이 작전을 켜는 동안 러너로 돌린 것과 열기 전 직접 돌린 것을 모두 적는다. 봇의 싸움은 물리 시간에 따라 조금씩 달라서 같은 코드도 결과가 다르다.

| 실행 | 결과 | 게임 시간 | 처치 | 끝난 곳 | 받은 피해 합 | 그 중 PRISM |
|---|---|---:|---:|---|---:|---:|
| 열기 전 직접 실행(`qa/site7_op8_preenable_20260930/full_op_08_summary.json`) | **EXTRACTED** | 193.5 s | 24 | — | 570.3 | 199.2 |
| 러너 `20260930_200604_custom`(`full_operation_op08_runner_batch_wiped_r04.json`) | WIPED | 76.4 s | 12 | R04_JUNCTION | 346.0 | 197.7 |
| 러너 `20260930_200951_custom`(`full_operation_op08_rerun_1_extracted.json`) | **EXTRACTED** | 196.4 s | 24 | — | 613.2 | 281.7 |
| 러너 `20260930_201410_custom`(`full_operation_op08_rerun_2_wiped_boss_room.json`) | WIPED | 139.2 s | 19 | R05_TERMINAL(GANTRY 체력 628.7 남음) | 616.2 | 227.6 |
| 러너 `20260930_201707_custom`(`full_operation_op08_rerun_3_wiped_r04.json`) | WIPED | 74.4 s | 10 | R04_JUNCTION | 346.0 | 212.0 |
| full 스위트 `20260930_203611_full`, 커밋 `c249af7d` 위(`full_operation_op08_full_tip_extracted.json`) | **EXTRACTED** | 193.4 s | 24 | — | 582.9 | 180.0 |

받은 피해 합 346.0은 세 대원의 체력 합(96 + 138 + 112)이다: 보급 없이 전멸한 두 번이다. 러너에서 이긴 것은 5번 중 2번, 열기 전 직접 실행까지 합치면 6번 중 3번이다. 앞의 다섯 실행은 코드가 같은 작업 트리에서 돌았고(커밋 `7ed8fe3b` 위, 커밋 전 경로가 6–10개: 이 기록의 `regression_runs.json`) 마지막 것만 커밋된 끝에서 돌았다.

- **원인은 구성이다.** 진 세 번 중 둘은 R04_JUNCTION(엘리트 방)에서 74–76초에, 하나는 보스방에서(GANTRY 체력 628.7 남김) 졌다.
  - 작전 8에는 PRISM이 **9기** 있다(작전 4–7: 7, 6, 6, 4. 작전 9: 5. 작전 10: 7). PRISM은 모든 실행에서 가장 큰 피해원이다(받은 피해 346–616 중 180–282).
  - 보급 갈래 O01_DEPOT이 **엘리트 방 R04_JUNCTION**에 매달려 있다(작전 5–7은 R02, R01, R02). 봇은 갈래방을 부모 방을 마친 뒤에만 가므로 R04까지는 치유할 곳이 없다. 앞 방 R02_MARSHALLING이 매번 190–220 HP를 깎고(세 대원의 체력 합은 346), 선두 대원이 R04에 들어갈 때 체력이 5–48뿐이다.
  - 보스는 주된 원인이 아니다. GANTRY가 준 피해는 보스방에 들어간 네 실행에서 112–164로 받은 피해의 20–27%다(이긴 세 번은 112–139, 보스방에서 진 한 번은 164). 그 한 번도 보스방에 체력 합 36으로 들어섰고 보급을 받아 158로 싸웠다.
- **고치지 않았다.** 방의 구성과 적 수는 균형이다. 갈래의 부모 방(`from`)을 바꾸는 일은 통로 판의 문과 월드 배치에 얽혀 있어 Codex의 판 작업이 필요할 수 있다(v2 판은 칠해진 문에 묶여 있다). 봇은 사람이 아니라서 사람이 하면 다를 수 있다. `full_op_03`과 같은 방식으로, 이 시험이 WIPED로만 실패하면 회귀가 아니다: `--only full_op_08`로 다시 돌린다. 경로, 보상, 탈출 같은 다른 이유로 서는 실패는 회귀다.
- **선택지(사용자 몫, 10절 1번).** ⒜ 그대로 두고 `full_op_03`처럼 "가끔 진다"로 기록한다(지금 상태). ⒝ 숫자를 바꾼다(엘리트 방의 PRISM 수, 보급 갈래의 위치, 앞 방의 세기). 균형이라 사람이 정한다. ⒞ 러너가 WIPED에 한해 한 번 더 돌게 한다(시도 횟수를 요약에 남기고, 진짜 회귀는 모든 시도에서 실패하므로 걸러진다). 도구 정책이라 사용자가 정한다.
- 작전 9–10은 적이 더 많으니(24기, 27기) 그 봇 시험도 자주 질 수 있다. 예상일 뿐 재지 않았다.

## 6. 시험 결과

`regression_runs.json`이 아래 실행의 요약을 담고 있다(러너 폴더 `qa/regression_runs/`는 git이 무시한다). 시간 열은 한 시험만 돌린 실행이면 그 시험의 시간이고, 스위트면 실행 전체 시간이다.

| 실행 | 내용 | 결과 | 시간 |
|---|---|---|---:|
| `20260930_200318_custom` | `campaign_data`(279), `demo_integration`(26), `campaign`(200). 작전 8을 켠 직후(`7ed8fe3b` 위, 커밋 전 경로 6개) | PASS 3개 중 3개 | 43초 |
| `20260930_200604_custom` | `combat_entry`, `boss_registry`(161), `boss_pattern`(959), `boss_duel`(1,124), `boss_room_fairness`(13), `robot_roster`(302), `emission_owner`(1,293), `combat_vfx`(189), `full_op_08`(커밋 전 경로 6개) | **FAIL** — `full_op_08`이 R04에서 WIPED(76.4초). 나머지 8개는 PASS | 184초 |
| `20260930_200951_custom` | `full_op_08` 다시(커밋 전 경로 10개) | PASS(EXTRACTED 196.4초) | 216초 |
| `20260930_201410_custom` | `full_op_08` 다시 | **FAIL** — 보스방에서 WIPED(139.2초) | 163초 |
| `20260930_201707_custom` | `full_op_08` 다시 | **FAIL** — R04에서 WIPED(74.4초) | 95초 |
| `20260930_201948_custom` | `campaign_data`(286), `boss_capture_geometry`, `boss_lineup` | PASS 3개 중 3개 | 38초 |
| `20260930_202408_quick` | quick 스위트, **커밋 `c249af7d` 위**(`git_head` `c249af7d`, 더러운 경로 없음) | PASS 44개 중 44개 PASS, `qa/` 가드 바뀜 0·사라짐 0·추가 0 | 415초 |
| `20260930_203611_full` | full 스위트, 같은 커밋 위(더러운 경로 없음) | PASS 71개 중 71개 PASS, `qa/` 가드 바뀜 0·사라짐 0·추가 0 | 4,210초 |

- 마지막 두 실행은 코드와 문서가 모두 커밋된 깨끗한 작업 폴더에서 돌았다(Codex의 커밋 전 파일도 없었다). 그 뒤의 커밋 둘(`5ec8b9c6`: `AGENTS.md`, `README.md`, 설계 문서의 실행 시간과 봇 수치를 고친 문서 커밋, 그리고 이 기록의 커밋)은 코드를 건드리지 않았으므로 두 실행은 그 커밋에도 그대로 해당한다.
- full 실행은 작전 8에 해당하는 시험을 모두 새로 돌렸다: `full_op_08`(199초), `connector_alignment`(848검사, 1,141초. 작전 1–8의 통로와 문턱 왕복을 훑는다), `traversal_audit`(1,928검사, 704초), `battle_geometry`(4,038검사), `world_route`(76검사), `boss_capture_geometry`, `boss_lineup`, `campaign`(200검사), `demo_integration`(26검사). 작전 1–7의 풀플레이 일곱 개도 모두 PASS했다(140 / 123 / 155 / 152 / 160 / 186 / 224초).
- quick의 `world_layout`은 PASS(8개 작전)이고 `mood_light`는 PASS(판 120장, 램프 풀 620개, 허공 마스크 120장, 접촉 그림자 15개)다. Codex가 판을 넘길 때 만든 데이터가 오래되지 않았다는 뜻이다. `plate_axis`(2), `seam_waiver`(10), `mood_contact`(5)도 PASS다.
- 한 번 실패한 러너 시험은 `full_op_08`뿐이고 세 번 모두 WIPED다(5절). 시험을 낮추지 않았고 숫자도 바꾸지 않았다. 마지막 full 스위트는 71/71이다.
- 이 기록을 쓰는 동안 quick과 full을 각각 한 번씩 돌렸다. full을 처음 시작한 한 번(`20260930_203524_full`)은 백그라운드 도구의 시간 제한이 걸릴까 봐 1분 만에 내가 멈추고 떼어 내 다시 시작했다. 요약이 없고 결과에 넣지 않았다.

## 7. 자기 방 캡처 (SIGNAL GANTRY, R05_TERMINAL)

창을 띄운 실제 렌더, 네이티브 1920 × 1080. `tests/render/site7_boss_pattern_capture.gd`가 이제 GANTRY를 미션 3의 시험대가 아니라 **작전 8의 자기 보스방**에 세운다(작전 9–10은 계속 시험대). 캡처는 통제된 페이즈 고정 장면(`controlled_phase_fixture`)이다: 페이즈와 공격 번호를 시험이 정해 넣었다.

| 파일 | 내용 |
|---|---|
| `captures/mission8_boss_room.png` | 보스방 전경: 신호 갠트리(검은 십자 마스트, 호박색 신호등, 황흑 줄무늬 밑판), 체력바, 기둥 네 개, 대원 패널과 HUD(목표 "Bring down the signal gantry", 선택 목표 Parts Depot과 Dispatch Office) |
| `captures/mission8_phase{1,2,3}{a,b}_warning.png` × 6 | 페이즈·공격별로 바닥에 깔린 경고 |
| `crop_sheets_1to1/mission8_gantry_1to1_sheet_{a,b}.png` | 보스와 경고 부분을 보간 없이 오려 붙인 1:1 시트(원본 해상도) |

- 모든 장면에서 경고가 덮지 않는 안전 바닥이 이 방의 실제 바닥에 있다(`safe_floor_gap` 6/6). 경고 수는 1A 2, 1B 1, 2A 3, 2B 2, 3A 4, 3B 5로 일곱 개 한도 안이다. 갠트리는 게임 안에서 높이 255 px(보스 한도 220–270 px 안)로 그려진다.
- 눈으로 본 것: 갠트리가 방의 북동쪽 끝에 서고 체력바가 위에 뜬다. 1A는 레일 두 줄이 십자로 대상 자리를 지나고, 1B는 충돌 원 하나가 대상 자리에 놓인다. 2A는 십자에 대각 레일이 더해지고 2B는 대상 양옆에 원 두 개가 놓인다. 3A는 별 모양 레일 네 줄이, 3B는 22.5° 돌린 별과 대상 자리의 원이 놓이며 페이즈 3 프레임에는 "CORE SHIELDED" 막대가 뜬다. 방은 어두운 철 바닥에 따뜻한 벽 램프가 켜진 모습이라 작전 7의 차가운 청회색 냉동고와 뚜렷이 다르다. **이것은 그림 승인이 아니다.**
- **관찰(고치지 않음):** 보스 발밑 타원 그림자는 모든 보스가 같은 크기다(이전 기록). 방 전체가 확 트여 엄폐가 없다(3절).
- `tools/art_pipeline/validate_visual_evidence_1080p.py --require-dynamic-capture`를 이 폴더의 이미지와 영상에 돌린 기록이 `visual_evidence_1080p.json`이다(PASS: 13개 파일). 이 검사는 컨테이너와 해상도만 확인하고 그림의 질을 판정하지 않는다. PNG와 영상은 git이 무시하고 작업 폴더에만 있다.

## 8. 게임 소리 영상

`tools/environment/record_stage_battle_with_audio.py`(`SABLE_CAPTURE_MISSIONS=8`, `SABLE_CAPTURE_BOSS=1`, `SABLE_CAPTURE_ROOT`는 스크래치 폴더). 보스방에서 실제 입력 경로(WASD, 마우스 조준, 발사)로 10초를 진행한다.

- `video/stage8_combat_10s_sound_1080p.mp4`: 1920 × 1080, 60 fps, 600프레임, 10.0초. 소리는 Godot의 실제 믹스이고 스테레오 48 kHz 480,000 샘플이다(RMS 0.0609, 최대 0.491, 무음 아님). 본 적: GANTRY, ENM_SITE7_DRONE_01, ENM_SITE7_PRISM_01. 영상 sha256 `e357f73d…78598`. 기록: `video/encode.json`, `video/capture.json`.
- 시계는 `--fixed-fps 60`이다. **성능 측정이 아니다.**
- 세 대원이 R05_TERMINAL에서 GANTRY와 교전한다. 300프레임에서는 ASTER가 사격하고 ROOK 주변에 원형 효과가 있고 MICA가 뛰며 남은 적이 하나("HOSTILES 01")이고, 540프레임에서는 갠트리의 십자 레일 경고가 방을 가로지르고 사격 궤적이 보인다(프레임 3장은 `video/frames/frame_*.png`). 사람이 듣고 보고 판단할 몫이다.

## 9. 파일

| 파일 | 내용 |
|---|---|
| `README_KO.md` | 이 문서 |
| `regression_runs.json` | 인용한 실행의 요약(추적) |
| `boss_room_fairness_grid{100,50,25}.json` | R05_TERMINAL과 R05_VAULT, R05_ATRIUM 공정성 결과(추적) |
| `full_operation_op08_*.json` | 작전 8 봇 풀플레이 보고서, 실행마다 하나(추적) |
| `capture_report.json` | 캡처 보고서(추적). 작전 8 행만 남겼다(같은 실행이 찍은 작전 1–7 자기 방과 작전 9–10 시험대는 뺐다) |
| `visual_evidence_1080p.json` | 1080p 검증기 결과(추적) |
| `captures/`, `crop_sheets_1to1/`, `video/` | 이미지와 영상. `qa/**/*.png`와 영상은 git이 무시한다 |

## 10. 하지 못한 것, 사용자와 Codex 몫

1. **`full_op_08`을 어떻게 할지(5절).** 러너에서 5번 중 2번, 직접 실행까지 6번 중 3번 이겼다. 그대로 두거나, 숫자를 바꾸거나(균형), 러너가 WIPED에 한해 다시 돌게 하거나(도구 정책) 사용자가 정한다. 나는 그대로 두었고 숫자와 러너를 바꾸지 않았다.
2. **사람 플레이와 균형.** 봇 통과는 균형 승인이 아니다. GANTRY의 체력 1,920, 공격 세기, 방의 난이도, 보상은 사람이 해 보고 정한다. 특히 위 봇의 결과는 엘리트 방 R04_JUNCTION이 어렵다는 신호일 수 있다.
3. **그림 승인.** 작전 8의 판 15장(Codex), 새벽 배경, GANTRY의 겉모습은 이 기록이 승인하지 않는다.
4. **같은 세션 회전 A/B FPS.** `AGENTS.md`는 FPS를 같은 세션의 회전 A/B로만 비교하라고 한다. 작전을 골라 그렇게 재는 정식 도구가 없다. 그래서 작전 8은 재지 못했다(영상은 고정 시계라 성능 자료가 아니다). 새벽 심연 배경은 안개 옥타브와 접촉 그림자 원자판(atlas)을 더해서 다른 작전보다 비용이 다를 수 있다. 사람이 F9(FPS 표시)로 작전 8을 플레이하며 보는 것이 가장 빠르다.
5. **엄폐 소품**(3절). R05_TERMINAL에는 엄폐가 없다. 더 원하면 Codex가 소품을 더한다. 더하면 `boss_room_fairness`를 다시 돌린다(방의 공정성 기하가 바뀌고, 이 방은 한도에 붙어 있다).
6. **작전 9–10.** 판이 없어 그대로다. Codex가 작전 9의 판을 끝내면 같은 순서(6절 C)로 사용자의 지시에 따라 켠다. 그때 `tests/render/site7_boss_pattern_capture.gd`의 `TEST_BED`에서 ARCHIVE의 행을 빼고 `BOSS_IDS`에 넣으면 자기 방 캡처가 되고, `boss_room_fairness`가 자동으로 그 방을 잰다. 오래된 반복문 게이트가 `range(1, 9)`처럼 넓힐 곳을 알려 준다.
