# SITE-7 작전 6–10 확장 설계

작성: 2026-09-29. 사용자 지시: "작전 즉, 스테이지를 10까지 확장해봐라."

이 문서는 작전 6–10의 설계, 통합 절차, 게이트를 담는다. 그림 작업 지시서는 둘로 나뉜다.

- 맵 판 75장: `docs/production/SITE7_OPERATIONS_6_10_PLATES_CODEX_PROMPT_KO.md`
- 보스 5기와 공격 패턴: `docs/production/SITE7_OPERATIONS_6_10_BOSSES_CODEX_PROMPT_KO.md`

작전 9–10의 판 30장, 연결, 켜기는 `docs/production/SITE7_OPERATIONS_9_10_PRODUCTION_ORDER_KO.md`(2026-09-30)가 본문이다. 작전 9(2026-10-01)와 작전 10(2026-10-02)을 켰다.

작전별 표(2절)와 곡선(3절)은 `data/missions/MIS_CH01_06.json`–`10.json`과 `data/story/site7_campaign.json`에서 뽑았다. 수치가 다르면 데이터가 맞다.

---

## 0. 상태

| 작전 | 제목 | 상태 | 남은 것 |
|---|---|---|---|
| 1–5 | BLACKOUT AT SITE-7 … OFFSHORE NULL | **출격 가능** (변경 없음) | — |
| 6 | VERDANT LOCK | **출격 가능** (2026-09-29 사용자 지시 "작전 6 켜라") | 사람 플레이로 균형과 그림 확인, 같은 세션 회전 A/B FPS. 판 15장과 무드·심연 행(Codex), 보스 AERATOR TOWER(원화·등록·패턴), 켜기(6절 C), 풀플레이 `full_op_06`, 방 바닥 공정성 시험 `boss_room_fairness`, 자기 방 캡처와 게임 소리 영상은 끝 |
| 7 | COLD STORAGE | **출격 가능** (2026-09-30 사용자 지시 "작전 7 켜라") | 사람 플레이로 균형과 그림 확인, 같은 세션 회전 A/B FPS. 판 15장과 무드·심연·엄폐 행(Codex), 보스 CRYO COMPRESSOR(원화·등록·패턴), 켜기(6절 C), 풀플레이 `full_op_07`, 방 바닥 공정성 시험 `boss_room_fairness`(축 레인을 900에서 300 px로 줄여 맞췄다), 자기 방 캡처와 게임 소리 영상은 끝. 보스방 R05_VAULT에는 엄폐물이 없다(6절 C) |
| 8 | SWITCHYARD | **출격 가능** (2026-09-30 사용자 지시 "8 켜라") | 사람 플레이로 균형과 그림 확인, 같은 세션 회전 A/B FPS. 판 15장과 무드·심연(새벽)·접촉 그림자·이음매 면제 3건(Codex), 보스 SIGNAL GANTRY(원화·등록·패턴), 켜기(6절 C), 방 바닥 공정성 시험 `boss_room_fairness`(뒤 페이즈 준비 시간을 1.6초로 늘려 열기 전에 맞췄다)는 끝. 풀플레이 `full_op_08`은 봇이 자주 진다(6절 C의 작전 8 대목: 9기 PRISM, 보급 가지가 정예방 뒤). 보스방 R05_TERMINAL에는 엄폐물이 없다 |
| 9 | MEMORY VAULT | **출격 가능** (2026-10-01 사용자 지시 "작전 9 켜고") | 사람 플레이로 균형과 그림 확인, 같은 세션 회전 A/B FPS. 판 15장과 무드·심연(`vault`)·엄폐 행(Codex), 보스 INDEX SPIRE(원화·등록·패턴), 켜기(6절 C), 방 바닥 공정성 시험 `boss_room_fairness`(메아리 예고를 1.0초에서 1.3초로 늘려 열기 전에 맞췄다), 풀플레이 `full_op_09`, 자기 방 캡처와 게임 소리 영상은 끝. 보스방 R05_STACKS에는 엄폐물이 없고, 보급 갈래 O01_BLADES는 정예방 R04 뒤에 있다. 방 R02의 NE 문 에이프런에 사람이 W+D를 계속 누르면 끼는 주머니가 남아 있다(정렬 시험은 통과) |
| 10 | ZERO POINT | **출격 가능** (2026-10-02 사용자 지시 "작전 10 켜라") | 사람 플레이로 균형 확인, 같은 세션 회전 A/B FPS(그림은 2026-10-02 사용자가 승인했다: 판 15장, ORIGIN CORE, `null` 허공 모습). 판 15장과 무드·심연(`null`) 행(Codex), 보스 ORIGIN CORE(원화·등록·패턴), 켜기(6절 C), 방 바닥 공정성 시험 `boss_room_fairness`(마지막 단계 예고를 1.6초로 늘려 열기 전에 맞췄다), 풀플레이 `full_op_10`, 자기 방 캡처와 게임 소리 영상은 끝. 보스방 R05_CORE에는 엄폐물이 없고 이름 지정 면제를 받은 좁은 방(전체 바닥 짧은 변 547 px)이며, 보급 갈래 O01_VAULT가 보스방에서 갈라져 보스 앞에서는 회복할 곳이 없다. `null` 허공은 처음에 거의 검게 보였고 같은 날 밝혔으며 사용자가 그 모습을 승인했다(아래 "`null` 심연" 항목). 판 15장과 ORIGIN CORE 그림도 같은 날 사용자가 승인했다(`AGENTS.md`의 "Operation 10 art approved", 해시 묶음 `qa/site7_op10_art_approval_20261002/`) |

보스 5기는 2026-09-29에 등록을 마쳤다(원화는 Codex, 구조·등록·패턴·시험은 Claude). 같은 날 사용자가 작전 6을 켜라고 지시해 6절 C대로 켰고(기록: `qa/site7_op6_enable_20260929/README_KO.md`), 2026-09-30에 Codex가 작전 7의 판을 넘기자 사용자가 작전 7을 켜라고 지시해 같은 절차로 켰다(기록: `qa/site7_op7_enable_20260930/README_KO.md`). 2026-09-30에 Codex가 작전 8의 판을 마무리하자 사용자가 작전 8을 켜라고 지시해 같은 절차로 켰다(기록: `qa/site7_op8_enable_20260930/README_KO.md`). 2026-10-01에 Codex가 작전 9의 판을 넘기자 사용자가 작전 9를 켜라고 지시해 같은 절차로 켰다(기록: `qa/site7_op9_enable_20261001/README_KO.md`). 2026-10-02에 Codex가 작전 10의 판을 넘기고 Claude가 켜기 전 검증을 마치자(`qa/site7_op10_preenable_20261002/`) 사용자가 작전 10을 켜라고 지시해 같은 절차로 켰다(기록: `qa/site7_op10_enable_20261002/README_KO.md`). 보스 등록 기록: `qa/site7_ops_6_10_boss_integration_20260929/README_KO.md`.

**왜 작전 6–10은 처음에 켜지 않았는가.** 작전 10까지 모두 켰으므로 이 대목은 기록이다.

- `AGENTS.md`: 판은 작전마다 따로 쓴다. 작전 1–9의 135장과 작전 10에 올 15장을 합쳐 150장이 되고, 두 작전이 판을 함께 쓰면 `site7_battle_geometry_smoke.gd`가 실패한다.
- `AGENTS.md`: 판과 보스의 원화는 Codex 내장 ImageGen으로만 만든다(로컬 이미지 모델, 손칠, 합성은 금지). 이 작업 세션에는 그 도구가 없다.
- 그래서 그림이 필요 없는 모든 것(캠페인 배선, 작전 데이터, 안내와 대사, 시험 게이트, 작업 지시서)을 먼저 끝냈다. 작전 6–10은 `data/story/site7_campaign.json`에 `"deployable": false`로 올랐고, 판과 보스가 들어온 작전을 **하나씩** 켠다(6절). 작전 6–10은 모두 켰다.

**이번에 들어간 것.**

- 캠페인 카탈로그 `scripts/core/site7_campaign.gd`: `deployable`, `available`(출격 가능하고 앞 작전을 깼을 때만), `next_after`(출격 불가 후속은 "없음"), `recommended`(출격 불가 작전은 건너뜀), `ui_rows`(`deployable`, `unlocked`, `cleared`), `playable_ids`.
- `scripts/core/campaign_progression.gd`: `snapshot()`에 `playable_complete`(열려 있는 작전을 모두 깼는가)를 더했다. `chapter_complete`는 열 작전을 모두 깼을 때만 참이다.
- `scripts/core/game_flow.gd`: `--battle-stage=`의 상한 5를 없애고, 전투 미리보기는 출격 가능한 작전 수까지만 받는다.
- `scripts/ui/base_lobby.gd`: 출격 불가 작전은 목록에 "IN PREPARATION"으로 나오고 선택되지 않는다. 상태 문구는 "CH01 COMPLETE // REPLAY AVAILABLE", "CLEARED // NEXT OPERATION IN PREPARATION", "NEXT OPERATION IN PREPARATION"이다.
- `scripts/audio/demo_music.gd`: `stage_key(mission_id)`. 작전 6–10은 자기 곡이 없으므로 스테이지 곡 1–5를 순서대로 다시 쓴다(`sound/README.md`).
- `data/story/site7_campaign.json` 6–10행(브리핑 4줄, 디브리프 2줄, 증거), `data/missions/MIS_CH01_06.json`–`10.json`.
- 시험: `tests/smoke/site7_campaign_data_smoke.gd`(러너 `campaign_data`, 7절), 캠페인 진행 스모크(출격 불가 작전 확인), 음악 스모크(곡 재사용).
- 업그레이드 경제(3절): `data/progression/upgrades.json`(무기고와 연구소 6단계), `CampaignProgression.max_level` / `upgrade_table`, 기지 시설 버튼의 값 표시(`base_lobby.gd`), 시험 `tests/smoke/upgrade_economy_smoke.gd`(러너 `upgrade_economy`), 모의 `tools/maintenance/upgrade_economy_sim.py`.

**작전 파일의 `staging` 블록.** 출격 불가 작전의 파일에는 `staging`이 있다(지금은 없다: 작전 6–10을 켜며 모두 지웠다): 상태 `ART_PENDING`, 판 접두어와 경로, 구조(오르막/내리막, 갈래), 보스(id, 이름, 방, 체력, 패턴). 보스 행의 `enemy_id`는 2026-09-29부터 등록된 그 작전의 보스이고 `staging.boss`와 같다(그 전에는 자리표시 `BOSS_SITE7_CARRIER_01`이었다). `motion_lab_v1/tests/test_enemy_body_plan.py`는 미션 파일의 모든 `enemy_id`가 활성 로봇 목록에 있어야 한다고 검사한다. 작전을 켤 때 `staging`을 지운다(작전 6–10은 지웠다).

---

## 1. 이야기 흐름

작전 1–5는 블랙아웃의 원인을 SITE-7 안에서 해저 중계까지 좇아 CARRIER NULL을 부순다. 작전 5의 끝에서 MICA가 말한다: "something answered from beyond the relay." 작전 6–10은 그 응답이 어디로 돌아오는지 따라가는 다섯 구역이다.

- 6 수경재배동: 응답 신호가 온실 안테나를 타고 되돌아온다. 공조 탑이 그것을 살려 둔다.
- 7 냉동 보관고: 응답은 그저 중계되는 게 아니라 저장된다. 압축기가 그것이 식지 않게 한다.
- 8 지상 자기부상 야적장: 저장된 응답을 발송하는 명령이 여기서 나간다. 유일한 지상 작전이다.
- 9 봉인된 기억 저장고: 발송 명령이 향하는 곳. 서 있던 자리를 기억하는 첨탑이 근원의 주소를 쥐고 있다.
- 10 근원 갱도: 응답의 출처인 핵심. 챕터의 끝.

브리핑에서 COMMAND는 목적을, MICA는 그 작전의 보스 패턴과 적의 습성을, ROOK은 전술을, ASTER는 임무 순서를 말한다. 대사는 영어, 이 문서는 한국어다. 디브리프의 MICA 대사가 다음 작전의 단서다.

| 작전 | 제목 | 찾는 것 | 디브리프의 MICA 대사(다음으로 이어지는 단서) |
|---|---|---|---|
| 2 | RECOVERY SWEEP | RELAY ROUTING LOG | The routing log isolates the final carrier path. It runs beneath the bulkhead into the resonance core. |
| 3 | CORE PRESSURE | CARRIER TRACE | Site-7 is silent. The resonance sample still carries a trace toward the offshore network. |
| 4 | FORGE DESCENT | HEAT-MAP TRACE | The Warden's trace points beyond Site-7. The offshore relay is carrying the carrier's null-space signature. |
| 5 | OFFSHORE NULL | NULL CARRIER TRACE | Carrier Null is gone. The offshore trace ends, but something answered from beyond the relay. |
| 6 | VERDANT LOCK | GERMINATION LOG | The aerator tower is offline. The germination log points down to the cryo archive; the answer is being stored, not just relayed. |
| 7 | COLD STORAGE | THERMAL LEDGER | The archive kept the answer on cold media. The dispatch orders in the ledger send it out along the maglev yard. |
| 8 | SWITCHYARD | DISPATCH ORDERS | The gantry is down. The last dispatch order ends at a vault that is on no Site-7 map. |
| 9 | MEMORY VAULT | VAULT INDEX | The index is complete. The origin's address is a shaft beneath the vault, straight down. |
| 10 | ZERO POINT | ANSWER LOG | The core is silent. The answer has stopped, and Site-7 is quiet for the first time since the blackout. |

작전 5–9의 COMMAND 디브리프는 다음 작전을 켤 때 그 작전을 알리는 문장으로 바꿨다(작전 9의 것은 2026-10-02에 "Memory Vault complete. Zero Point is now available."로, 6절 C). 데이터 게이트가 이를 강제한다. 작전 10의 디브리프는 챕터의 끝이다("Chapter 01 complete. All ten operations are available for recovery runs and upgrades.").

---

## 2. 작전별 설계

적 코드: **DR** SITE-7 RECON DRONE, **PZ** PRISM / SKIMMER, **RM** CINDER / IMPACT ROBOT(호버 램), **MT** VESPER / SIEGE MORTAR, **BW** BULWARK / SHIELD CRAWLER, **NP** NULL / PYLON. 괄호 안 **S/O/V**는 엘리트 접두어 SHIELDED / OVERCHARGED / VOLATILE다. 정보 보상은 일반/고가 연구, 부품, 신호 조각, 기계 정보다.

공통 구조(작전 4·5와 같다): 주 경로 6개 방(이벤트 → 전투 → 연구 → 엘리트 → 보스 → 탈출), 갈래 2개(보급, 연구). 전투방마다 증원이 있고 동시에 5기 이상이 나온다. 위험지대 ARC_VENT는 전투·엘리트 방에만 둔다. 엘리트 접두어는 보스에 붙이지 않는다. 탈출 창은 방 3–5다.

### 작전 6 VERDANT LOCK — Site-7 Hydroponic Wing

- 구조: 주 경로 오르막, 갈래 O01←R01, O02←R03. 판 15장(방 8 + 통로 7), 판 ID `S6_*`.
- 적 체력 배율 ×1.04. 보스 제외 적 22기(엘리트 4기): PZ 6, DR 6, NP 3, RM 3, MT 2, BW 2.
- 보스 AERATOR TOWER (`BOSS_SITE7_AERATOR_01`), 체력 1560, 패턴 `bloom_field`. 보스 지시서 2절과 4절이 본문이다.
- 분위기: 온실 · 수경재배동. 밝은 에메랄드와 흰 재배등, 습한 안개, 포화도 높음.

| 방 | 종류 | 이름 | 목표 | 첫 웨이브 | 증원 | 위험지대 | 정보 보상 |
|---|---|---|---|---|---|---|---|
| R01 `R01_AIRLOCK` | 이벤트 | Hydro Airlock | Cycle the hydro airlock | — | — | — | 일반 32 |
| R02 `R02_GALLERY` | 전투 | Planter Gallery | Clear the planter gallery | NP MT PZ DR | RM PZ BW DR (남은 적 2 이하일 때) | ARC_VENT ×2 | 일반 44 |
| R03 `R03_LAB` | 연구 | Germination Lab | Recover the germination log | — | — | — | 일반 54 · 고가 30 |
| R04 `R04_PUMPS` | 엘리트 | Irrigation Pumps | Break the irrigation pump line | NP(S) NP MT(V) RM(O) | PZ DR(V) BW PZ (남은 적 2 이하일 때) | ARC_VENT ×2 | 일반 52 |
| R05 `R05_ATRIUM` | 보스 | Grow Atrium | Silence the aerator tower | 보스 1560 + PZ DR | RM PZ → DR DR (남은 적 1 이하일 때) | — | 고가 130 |
| R06 `R06_LIFT` | 탈출 | Seed Lift | Extract by the seed lift | — | — | — | — |
| O01 `O01_STORES` | 보급 (갈래, R01_AIRLOCK에서) | Seed Stores | 물자 회수 | — | — | — | 일반 34 · 부품 6 |
| O02 `O02_NURSERY` | 연구 (갈래, R03_LAB에서) | Antenna Nursery | Read the antenna beds | — | — | — | 고가 68 · 신호 3 · 정보 1 |

### 작전 7 COLD STORAGE — Site-7 Cryo Archive

- 구조: 주 경로 내리막(`reverse`), 갈래 O01←R02, O02←R05. 판 15장(방 8 + 통로 7), 판 ID `S7_*`.
- 적 체력 배율 ×1.08. 보스 제외 적 22기(엘리트 4기): RM 6, BW 5, DR 5, PZ 4, MT 2.
- 보스 CRYO COMPRESSOR (`BOSS_SITE7_CRYO_01`), 체력 1740, 패턴 `frost_sweep`. 보스 지시서 2절과 4절이 본문이다.
- 분위기: 냉동 보관고. 밝은 서리 흰색과 분홍 비상등, 낮은 채도의 차가운 강철.

| 방 | 종류 | 이름 | 목표 | 첫 웨이브 | 증원 | 위험지대 | 정보 보상 |
|---|---|---|---|---|---|---|---|
| R01 `R01_INTAKE` | 이벤트 | Cryo Intake | Cross the cryo intake dock | — | — | — | 일반 34 |
| R02 `R02_FREEZE` | 전투 | Deep Freeze Hall | Clear the deep freeze hall | RM RM BW PZ | DR DR MT BW (남은 적 2 이하일 때) | ARC_VENT ×2 | 일반 46 |
| R03 `R03_LEDGER` | 연구 | Thermal Ledger | Recover the thermal ledger | — | — | — | 일반 56 · 고가 32 |
| R04 `R04_COMPRESSORS` | 엘리트 | Compressor Deck | Break the compressor line | BW(S) RM(O) RM PZ(O) | MT DR(V) PZ BW (남은 적 2 이하일 때) | ARC_VENT ×2 | 일반 54 |
| R05 `R05_VAULT` | 보스 | Cryo Vault | Shut down the cryo compressor | 보스 1740 + BW PZ | RM RM → DR DR (남은 적 1 이하일 때) | — | 고가 148 |
| R06 `R06_LOCK` | 탈출 | Cargo Lock | Extract through the cargo lock | — | — | — | — |
| O01 `O01_REAGENTS` | 보급 (갈래, R02_FREEZE에서) | Reagent Stores | 물자 회수 | — | — | — | 일반 36 · 부품 7 |
| O02 `O02_RECORDER` | 연구 (갈래, R05_VAULT에서) | Cold Recorder | Read the cold recorder | — | — | — | 고가 72 · 신호 3 · 정보 1 |

### 작전 8 SWITCHYARD — Site-7 Surface Maglev Yard

- 구조: 주 경로 오르막, 갈래 O01←R04, O02←R05. 판 15장(방 8 + 통로 7), 판 ID `S8_*`.
- 적 체력 배율 ×1.12. 보스 제외 적 23기(엘리트 4기): PZ 9, DR 6, MT 3, RM 2, NP 2, BW 1.
- 보스 SIGNAL GANTRY (`BOSS_SITE7_GANTRY_01`), 체력 1920, 패턴 `rail_charge`. 보스 지시서 2절과 4절이 본문이다.
- 분위기: 지상 자기부상 선로 야적장, 새벽. 유일한 밝은 지상 작전: 옅은 금색 빛, 낮은 채도, 긴 그림자, 신호등.

| 방 | 종류 | 이름 | 목표 | 첫 웨이브 | 증원 | 위험지대 | 정보 보상 |
|---|---|---|---|---|---|---|---|
| R01 `R01_GATE` | 이벤트 | Yard Gate | Open the yard gate | — | — | — | 일반 36 |
| R02 `R02_MARSHALLING` | 전투 | Marshalling Track | Clear the marshalling track | PZ PZ MT DR | PZ RM NP DR (남은 적 2 이하일 때) | ARC_VENT ×2 | 일반 48 |
| R03 `R03_TOWER` | 연구 | Signal Tower | Recover the dispatch orders | — | — | — | 일반 58 · 고가 34 |
| R04 `R04_JUNCTION` | 엘리트 | Switch Junction | Break the switch junction | PZ(O) PZ MT(V) NP(S) | RM BW DR(V) PZ (남은 적 2 이하일 때) | ARC_VENT ×2 | 일반 56 |
| R05 `R05_TERMINAL` | 보스 | Depot Terminal | Bring down the signal gantry | 보스 1920 + PZ DR | PZ MT → DR DR PZ (남은 적 1 이하일 때) | — | 고가 166 |
| R06 `R06_PLATFORM` | 탈출 | Departure Platform | Board the departure capsule | — | — | — | — |
| O01 `O01_DEPOT` | 보급 (갈래, R04_JUNCTION에서) | Parts Depot | 물자 회수 | — | — | — | 일반 38 · 부품 7 |
| O02 `O02_DISPATCH` | 연구 (갈래, R05_TERMINAL에서) | Dispatch Office | Read the dispatch map | — | — | — | 고가 76 · 신호 4 · 정보 1 |

### 작전 9 MEMORY VAULT — Sealed Memory Vault

- 구조: 주 경로 내리막(`reverse`), 갈래 O01←R04, O02←R03. 판 15장(방 8 + 통로 7), 판 ID `S9_*`.
- 적 체력 배율 ×1.16. 보스 제외 적 24기(엘리트 4기): DR 11, PZ 5, NP 3, RM 3, MT 1, BW 1.
- 보스 INDEX SPIRE (`BOSS_SITE7_ARCHIVE_01`), 체력 2100, 패턴 `echo_copy`. 보스 지시서 2절과 4절이 본문이다.
- 분위기: 봉인된 기억 저장고, 성당 같은 서가. 짙은 남보라와 금빛 필라멘트, 대비 높음.

| 방 | 종류 | 이름 | 목표 | 첫 웨이브 | 증원 | 위험지대 | 정보 보상 |
|---|---|---|---|---|---|---|---|
| R01 `R01_ANTECHAMBER` | 이벤트 | Vault Antechamber | Enter the memory vault | — | — | — | 일반 38 |
| R02 `R02_NAVE` | 전투 | Index Nave | Clear the index nave | DR DR DR NP PZ | DR DR RM PZ (남은 적 2 이하일 때) | ARC_VENT ×2 | 일반 50 |
| R03 `R03_CHAPEL` | 연구 | Read-Out Chapel | Recover the vault index | — | — | — | 일반 60 · 고가 36 |
| R04 `R04_GALLERY` | 엘리트 | Echo Gallery | Break the echo gallery | NP(S) NP PZ(O) MT | DR(V) DR(V) RM BW (남은 적 2 이하일 때) | ARC_VENT ×2 | 일반 58 |
| R05 `R05_STACKS` | 보스 | Core Stacks | Erase the index spire | 보스 2100 + PZ DR | DR DR PZ → RM DR (남은 적 1 이하일 때) | — | 고가 184 |
| R06 `R06_LIFT` | 탈출 | Archive Lift | Extract by the archive lift | — | — | — | — |
| O01 `O01_BLADES` | 보급 (갈래, R04_GALLERY에서) | Spare Blades | 물자 회수 | — | — | — | 일반 40 · 부품 8 |
| O02 `O02_RESTORE` | 연구 (갈래, R03_CHAPEL에서) | Restore Lab | Read the restore log | — | — | — | 고가 80 · 신호 4 · 정보 1 |

### 작전 10 ZERO POINT — Site-7 Origin Shaft

- 구조: 주 경로 오르막, 갈래 O01←R05, O02←R02. 판 15장(방 8 + 통로 7), 판 ID `S10_*`.
- 적 체력 배율 ×1.22. 보스 제외 적 27기(엘리트 5기): PZ 7, DR 6, RM 5, MT 4, BW 3, NP 2.
- 보스 ORIGIN CORE (`BOSS_SITE7_ORIGIN_01`), 체력 2460, 패턴 `null_convergence`. 보스 지시서 2절과 4절이 본문이다.
- 분위기: 근원 갱도. 검은 합금과 흰 빛, 붉은 이음선. 흑백에 가까운 최소 채도와 강한 대비.

| 방 | 종류 | 이름 | 목표 | 첫 웨이브 | 증원 | 위험지대 | 정보 보상 |
|---|---|---|---|---|---|---|---|
| R01 `R01_DESCENT` | 이벤트 | Sealed Descent | Reach the shaft floor | — | — | — | 일반 40 |
| R02 `R02_RELAY` | 전투 | First Relay | Clear the first relay | PZ MT RM BW(S) NP | DR PZ RM DR (남은 적 2 이하일 때) | ARC_VENT ×2 | 일반 52 |
| R03 `R03_LOG` | 연구 | Answer Log | Recover the answer log | — | — | — | 일반 62 · 고가 38 |
| R04 `R04_GALLERY` | 엘리트 | Null Gallery | Break the null gallery | NP(S) PZ(O) MT(V) RM BW | PZ DR(V) MT RM (남은 적 2 이하일 때) | ARC_VENT ×2 | 일반 60 |
| R05 `R05_CORE` | 보스 | Origin Core | Destroy the origin core | 보스 2460 + PZ DR | RM PZ → DR DR MT → BW PZ (남은 적 1 이하일 때) | — | 고가 220 |
| R06 `R06_EXIT` | 탈출 | Way Out | Leave the origin shaft | — | — | — | — |
| O01 `O01_VAULT` | 보급 (갈래, R05_CORE에서) | Reserve Vault | 물자 회수 | — | — | — | 일반 44 · 부품 8 |
| O02 `O02_RECORDER` | 연구 (갈래, R02_RELAY에서) | First Recorder | Play the first recording | — | — | — | 고가 90 · 신호 5 · 정보 1 |

---

## 3. 난이도와 보상 곡선

작전 6–10은 1–5의 곡선을 이어 간다. 보스 체력은 620 → … → 1380에서 1560 → 1740 → 1920 → 2100 → 2460으로 늘고(게이트가 순증을 요구한다), 적 체력 배율은 작전 6의 ×1.04에서 작전 10의 ×1.22까지 올라간다. 작전 1은 정보 보상 행이 없고 기본값을 쓴다. 열 작전이 모두 출격 가능하다.

| 작전 | 제목 | 적(보스 제외) | 엘리트 | 적 체력 합 | 보스 체력 | 일반 연구 | 고가 연구 | 부품 | 신호 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | SITE-7: FIRST DESCENT | 20 | 1 | 1975 | 620 | 기본값 | 기본값 | 기본값 | 기본값 |
| 2 | SITE-7: RECOVERY SWEEP | 20 | 1 | 2112 | 710 | 132 | 106 | 3 | 1 |
| 3 | SITE-7: CORE PRESSURE | 20 | 2 | 2504 | 820 | 150 | 138 | 4 | 2 |
| 4 | FORGE DESCENT | 20 | 3 | 2916 | 1120 | 182 | 164 | 5 | 2 |
| 5 | OFFSHORE NULL | 20 | 3 | 3154 | 1380 | 206 | 204 | 6 | 3 |
| 6 | VERDANT LOCK | 22 | 4 | 3746 | 1560 | 216 | 228 | 6 | 3 |
| 7 | COLD STORAGE | 22 | 4 | 4026 | 1740 | 226 | 252 | 7 | 3 |
| 8 | SWITCHYARD | 23 | 4 | 4128 | 1920 | 236 | 276 | 7 | 4 |
| 9 | MEMORY VAULT | 24 | 4 | 4156 | 2100 | 246 | 300 | 8 | 4 |
| 10 | ZERO POINT | 27 | 5 | 5372 | 2460 | 258 | 348 | 8 | 5 |

- 작전 6–10 적 체력 합의 증가는 적 수(22 → 27)와 체력 배율이 함께 만든다. 작전 10은 엘리트 5기와 보스방 증원 3웨이브로 가장 무겁다.
- **후반 보상의 소비처 (해결됨: 업그레이드 6단계).** 이전에는 연구를 쓰는 곳이 업그레이드 두 가지(각 3단계, 무기고 720 + 연구소 660)와 정보 분석 3건(합 440)뿐이라 합계 1,820이었다. 작전 1–10을 한 번씩 전부 모으면 연구 4,088(작전 2–5 약 1,280, 작전 6–10 약 2,590)이라 2,268이 남았고, 부품(56 대 6)과 신호 조각(28 대 3)은 거의 다 남았다. 사용자 지시(2026-09-29 "상한이나 소모처도 늘려")로 두 업그레이드를 6단계까지 늘렸다. 값은 `data/progression/upgrades.json`이고 `CampaignProgression`의 `max_level`, `upgrade_table`, `get_upgrade_cost`가 읽는다.

| 값(연구 · 부품 · 신호) | 4단계 | 5단계 | 6단계 | 6단계까지 합계 |
|---|---|---|---|---|
| 무기고 (피해 +8 %/단계) | 440 · 5 · 1 | 540 · 7 · 2 | 640 · 9 · 3 | 2,340 · 27 · 6 |
| 연구소 (연구 +12 %/단계) | 460 · 2 · 2 | 580 · 3 · 3 | 700 · 4 · 4 | 2,400 · 9 · 12 |

  - 1–3단계 값은 그대로다(저장한 사람이 그 값을 냈다). 4–6단계는 부품과 신호 조각도 쓰게 해서 세 재화가 모두 소비처를 갖는다.
  - 6단계 효과는 피해 ×1.48, 연구 ×1.72다. 전투와 스테이지가 거는 ×2 제한 안이다.
  - 기지 전체의 소비량은 연구 5,180(업그레이드 4,740 + 분석 440) · 부품 36 · 신호 18이다. 작전 1–10이 주는 4,088 · 56 · 28의 1.27 · 0.64 · 0.64배다. 시험 `upgrade_economy`(러너 quick)가 연구 0.9–1.5배, 부품과 신호 0.5–1.5배를 요구하고, 작전 1–5만으로 1–3단계 값을 낼 수 있는지도 본다.
  - 모의(`python tools/maintenance/upgrade_economy_sim.py --path 1.0`, 싼 것부터 사는 플레이어): 전부 모으면 작전 10에서 두 업그레이드가 6단계에 닿는다(작전 7에서 4/4, 8에서 무기고 5, 9에서 연구소 5). 85 %만 모으면 무기고 6, 연구소 5이고 70 %면 5, 4다. 작전 1–5 구간은 이전과 같다(전부 모아도 무기고 3, 연구소 2). 사람이 해 본 값이 아니다.
- 균형은 사람의 플레이로 확인한 적이 없다. 봇 풀플레이(`full_op_0N`)는 통과 여부만 본다. 작전 10은 봇이 이기기 어려울 수 있다(`full_op_03`은 지금도 약 3번에 1번 전멸한다).

---

## 4. 분위기와 심연

모든 v2 판은 중성 조명으로 그려지고, 방과 작전의 분위기는 런타임 무드(`data/visual/site7_mood.json`, `site7_room_art_layer.gd`의 판 셰이더)가 입힌다. 그러므로 작전 6–10의 분위기는 그림이 아니라 무드 행이다. 작전 1–5와 달라야 한다: 노출, 색 치우침(`tint`), 채도, 대비, 그림자색, 심연 스타일.

아래 등급은 **시작값**이다. 판이 들어온 뒤 실제 화면을 보며 조정한다. 판별 행(램프 웅덩이, 위에서 내리는 빛, 별도 조명)은 판이 있어야 쓸 수 있다.

| 작전 | 분위기 | 등급 시작값(`site7_mood.json`) | 심연 |
|---|---|---|---|
| 6 VERDANT LOCK | 온실 · 수경재배동. 밝은 에메랄드와 흰 재배등, 습한 안개, 포화도 높음 | exposure +0.05, tint [0.94, 1.06, 0.96], saturation 1.2, contrast 1.05, shadows 짙은 청록 | spore (새 스타일): 아래 구덩이에 초록 포자 티끌이 느리게 떠오르고 낮은 안개가 흐른다 |
| 7 COLD STORAGE | 냉동 보관고. 밝은 서리 흰색과 분홍 비상등, 낮은 채도의 차가운 강철 | exposure +0.15, tint [0.96, 1.0, 1.08], saturation 0.7, contrast 1.0, shadows 옅은 자홍 | cryo (새 스타일): 아래 구덩이에 서리 안개와 얼음 결정이 천천히 가라앉고 분홍 비상등이 멀리서 깜박인다 |
| 8 SWITCHYARD | 지상 자기부상 선로 야적장, 새벽. 유일한 밝은 지상 작전: 옅은 금색 빛, 낮은 채도, 긴 그림자, 신호등 | exposure +0.35, tint [1.04, 1.0, 0.94], saturation 0.8, contrast 0.95, shadows 옅은 청자색 | dawn (새 스타일): 어두운 구덩이 대신 옅은 금빛 구름 바다와 아침 안개가 아래로 흐른다. 검은 배경이 아니다 |
| 9 MEMORY VAULT | 봉인된 기억 저장고, 성당 같은 서가. 짙은 남보라와 금빛 필라멘트, 대비 높음 | exposure -0.2, tint [1.0, 0.94, 1.1], saturation 1.05, contrast 1.2, shadows 짙은 남색 | vault (새 스타일): 아래 구덩이에서 금빛 광선 가닥이 위로 천천히 올라오고 짙은 남보라 안개가 깔린다 |
| 10 ZERO POINT | 근원 갱도. 검은 합금과 흰 빛, 붉은 이음선. 흑백에 가까운 최소 채도와 강한 대비 | exposure -0.35, tint [1.0, 1.0, 1.0], saturation 0.45, contrast 1.3, shadows 짙은 적색 | null (새 스타일): 별 없는 어두운 슬레이트빛 허공에 흰 격자선과 붉은 점이 느리게 어긋난다. 검은 배경이 아니다(처음 설계는 "안개 거의 없는 검은 허공"이었으나 화면에서 검게 보여 2026-10-02에 밝혔다) |

**새 심연 스타일 5종.** `scripts/missions/site7_abyss_backdrop.gd`의 `STYLES`는 지금 `shaft`, `flood`, `pressure`, `forge`, `offshore`다. 작전 6–10에 `spore`, `cryo`, `dawn`, `vault`, `null`을 더한다. 기존 스타일과 같은 규칙을 따른다: 그림 없이 코드로 그린 쿼드 하나, 웹 빌드는 안개 옥타브 절반, 검은 배경이 아니다. `site7_battle_geometry_smoke.gd`는 작전마다 스타일이 서로 다르고 `STYLES`에 있는지 검사한다. 이 코드는 그림이 필요 없어서 판보다 먼저 만들 수 있다(9절).

**작전 8은 유일한 지상 작전이다.** 판의 건축 밖은 다른 작전과 같이 평평한 거의 검정 `#07090D`이고 런타임이 투명 마스크로 바꾼다. 그 자리에 옅은 금빛 구름 바다(`dawn`)를 코드로 그린다. 하늘, 구름, 지평선을 판에 그리지 않는다.

```json
// data/visual/site7_mood.json 의 missions 행 형식 (작전 4 예)
{"exposure": 0.0, "tint": [1.12, 1.0, 0.84], "saturation": 1.15, "contrast": 1.15,
 "shadows": {"color": [0.024, 0.01, 0.0], "strength": 1.0},
 "abyss": {"style": "forge", "style_color": [1.0, 0.38, 0.08], "style_strength": 0.5,
           "base": [0.015, 0.009, 0.005], "fog": [0.08, 0.045, 0.022], "fog_strength": 1.0,
           "haze_strength": 0.2, "far_light_density": 0.3, "dust_strength": 1.0,
           "dust": [1.0, 0.55, 0.2], "work_lights": [1.0, 0.62, 0.3]}}
```

---

## 5. 보스

| 작전 | 보스 | id | 체력 | 패턴 | 강조색 | 실루엣 |
|---|---|---|---|---|---|---|
| 6 | AERATOR TOWER | `BOSS_SITE7_AERATOR_01` | 1560 | `bloom_field` | `#8fdc4a` | 버섯: 넓은 갓과 가는 기둥 |
| 7 | CRYO COMPRESSOR | `BOSS_SITE7_CRYO_01` | 1740 | `frost_sweep` | `#ff7fc8` | 낮은 압축기 블록과 한쪽의 높은 라디에이터 벽 |
| 8 | SIGNAL GANTRY | `BOSS_SITE7_GANTRY_01` | 1920 | `rail_charge` | `#ffd84a` | T자: 기둥과 가로보 |
| 9 | INDEX SPIRE | `BOSS_SITE7_ARCHIVE_01` | 2100 | `echo_copy` | `#2fe0b4` | 계단식 지구라트와 가는 바늘 |
| 10 | ORIGIN CORE | `BOSS_SITE7_ORIGIN_01` | 2460 | `null_convergence` | `#f4efe8` | 뾰족한 결정 다발 |

기존 다섯(ANCHOR 보라, RELAY 진홍, REMNANT 얼음 청백, FORGE 호박, CARRIER 청록)과 강조색, 실루엣, 공격 모양이 모두 달라야 한다. 새 다섯 패턴은 같은 경고 부품(투사체, 원, 직선 레인)으로 짜고 공정성 규칙을 지킨다. 원화, 등록, 패턴 수치, 효과 계열은 보스 지시서가 본문이다.

---

## 6. 통합 절차

작전 하나를 켜기까지의 순서다. **작전 N의 A–C가 끝나기 전에는 N+1을 켜지 않는다.** A와 B는 어느 쪽을 먼저 해도 되지만 C는 둘이 모두 끝난 뒤다.

### A. 판 연결 (판 15장이 들어온 뒤, Codex)

판 15장의 반입 규칙은 판 지시서 5절이다. 연결은 다음 순서다. 한 단계마다 `python tools/maintenance/run_regression_suite.py --only <테스트>`로 해당 테스트만 돌려도 된다.

1. `data/visual/site7_plate_floors.json`: 판마다 바닥 다각형과 방의 문(`doors`)을 추적한다. `tests/render/site7_walk_graph_capture.gd`의 1080p 오버레이로 확인한다.
2. `data/visual/site7_battle_art.json`: 작전 행(방 8: `room_id`, `asset_id` `ENV_S0N_*`, `asset`, `position`, `scale` 1.0 / 통로 7: `connector_id`(`S06_C01` 형식), `asset_id`, `asset`, `position`, `scale`, `deck`, `seam_fade`). 내리막 작전(7, 9)은 주 경로 통로 5개에 `"reverse": true`. 본보기: 작전 5 행.
3. `python tools/environment/build_site7_world_layout.py`: `site7_world_layout.json`과 `site7_seam_light.json`을 다시 쓴다. 이어서 `--check`가 PASS해야 한다(러너 `world_layout`).
4. `data/visual/site7_battle_layouts.json`: 전투방 3개(COMBAT, ELITE, BOSS)의 바닥, 엄폐, `spawn`, `enemy_spawns`, `boss_anchor`. 오른쪽 위에서 들어오는 방(내리막 작전의 방)은 `spawn`, `enemy_spawns`, `boss_anchor`를 먼 쪽에 둔다. 보스 복도(작전 8)는 보스를 출구 끝에 세운다. `data/visual/site7_environment_props.json`: 방마다 엄폐 소품. 그 뒤 `godot --headless -s tools/environment/settle_cover_on_floor.gd -- --write`를 마른 실행이 아무것도 옮기지 않을 때까지 되풀이한다.
5. `data/visual/site7_mood.json`: 작전 행과 판 15장 행(4절). 이어서 `python tools/environment/build_site7_mood_light.py`가 램프와 바깥 허공 마스크를 만든다. 러너 `mood_light`(`--check`)가 PASS해야 한다.
6. `python tools/environment/audit_site7_plate_lighting.py --mission MIS_CH01_0N --strict`: 15 plates, 14 seams가 PASS해야 한다.
7. 새 심연 스타일(4절): `site7_abyss_backdrop.gd`의 `STYLES`와 셰이더 분기를 더한다. 이미 있으면 건너뛴다.
8. 시험의 작전 반복문(아래 표)을 새 작전까지 넓힌다. 데이터 게이트가 5개를 넘는 출격 가능 작전에서 이 반복문이 남아 있으면 실패한다.
9. 1080p 게임 캡처(방 8 + 통로 7), 전체 조감(`build_site7_world_layout.py --preview .cache/…`), S3 판과 나란히 놓은 비교. 기록은 `qa/site7_ops_6_10_plates_<날짜>/`.

**5에서 멈춘 시험과 도구 (8단계).** `range(1, 6)` 반복문, 5에서 끝나는 작전 목록, `(1,2,3,4,5)` 허용 번호가 그 작전 수를 정한다.

| 파일 | 넓힐 것 |
|---|---|
| `tests/smoke/combat_density_smoke.gd` | 작전 반복문 |
| `tests/smoke/site7_battle_geometry_smoke.gd` | 작전 반복문, 끝의 `plate_uses.size() == 75`(15 × 작전 수) |
| `tests/smoke/site7_branch_navigation_regression.gd` | 작전 반복문 |
| `tests/smoke/site7_connector_alignment_smoke.gd` | 작전 반복문(`--mission=N` 인자는 이미 있다) |
| `tests/smoke/site7_traversal_audit_smoke.gd` | 작전 반복문 |
| `tests/smoke/site7_world_route_navigation_smoke.gd` | 작전 반복문 |
| `tests/smoke/firing_lane_search_smoke.gd`, `floor_segment_smoke.gd`, `zone_hazard_smoke.gd` | `MISSIONS` 목록에 새 작전 id |
| `tests/smoke/elite_affix_smoke.gd` | `EXPECTED_ROWS`에 작전별 접두어 수(작전 6–9는 4, 작전 10은 5) |
| `tests/render/site7_battle_capture.gd` | 작전 반복문 |
| `tests/render/stage_battle_video_10s_capture.gd` | `ALLOWED_MISSIONS`에 새 작전 id |
| `tools/environment/record_stage_battle_with_audio.py` | 허용 번호 `(1,2,3,4,5)`(86줄 근처), 미션 id 형식 `f'MIS_CH01_0{number}'`은 작전 10에서 틀리니 `{number:02d}`로, 보스 표(131줄 근처) |
| `tools/maintenance/run_regression_suite.py` | `full_op_0N` 등록: `range(1, 6)` → 출격 가능 작전 수, 이름 형식 `full_op_%02d`와 `--mission=MIS_CH01_%02d`(작전 10은 두 자리). `--list`로 확인한다. |

### B. 보스 등록 (보스 원화가 들어온 뒤)

**작전 6–10의 보스는 2026-09-29에 이 절을 모두 끝냈다**(원화 Codex, 등록·패턴·시험 Claude). 작전을 켤 때 남은 것은 A와 C다. 아래는 등록이 무엇을 포함하는지의 기록이고, 새 보스가 더 생기면 그대로 따른다. 보스 지시서 2.3절이 본문이다. 요약: `enemy_profiles.json`과 `site7_enemy_body_plan.json`에 프로필, id로 묶인 코드(`site7_enemy_tactics.gd`, `site7_machine_sprite.gd`, `enemy_actor.gd`, `enemy_detail_overlay_presentation.gd`), 효과 계열(`combat_hit_vfx.gd`, `combat_muzzle_vfx.gd`, `prototype_projectile.gd`), 그리고 작전 파일의 보스 행 `enemy_id`를 자리표시 `BOSS_SITE7_CARRIER_01`에서 새 id로 바꾸고 `new_enemy_ids`에 넣는다. 보스 시험(`boss_registry`, `boss_pattern`, `robot_roster`, `emission_owner`, `combat_vfx`)의 보스 표에 새 보스를 넣는다. 실시간 교전 시험 `boss_duel`은 `boss_pattern`의 `OTHER_BOSSES`와 `SIGNATURES`를 그대로 읽으므로 따로 고칠 표가 없다.

### C. 작전 켜기 (A와 B가 끝난 뒤, 이 순서로)

1. `data/missions/MIS_CH01_0N.json`에서 `staging` 블록을 지운다.
2. `data/story/site7_campaign.json`의 그 작전 행에서 `"deployable": false`와 `"pending"`을 지운다.
3. **앞 작전의 COMMAND 디브리프**를 이 작전을 알리는 문장으로 바꾼다(데이터 게이트가 강제한다):

   | 켜는 작전 | 앞 작전 COMMAND 디브리프 |
   |---|---|
   | 6 | `Offshore Null complete. The answer signal is tracing back into Site-7's sealed lower wings. Verdant Lock is now available.` |
   | 7 | `Verdant Lock complete. Cold Storage is now available.` |
   | 8 | `Cold Storage complete. Switchyard is now available.` |
   | 9 | `Switchyard complete. Memory Vault is now available.` |
   | 10 | `Memory Vault complete. Zero Point is now available.` |

4. 게이트를 돌린다: `python tools/maintenance/run_regression_suite.py --only campaign_data,campaign,demo_integration`. 실패 문구가 빠진 것을 하나씩 말해 준다(판, 배치, 무드, 소품, 보스 프로필 등).
5. 작전 10을 켰으므로 열 작전을 모두 깨면 `chapter_complete`가 참이고(기지 문구 "CH01 COMPLETE // REPLAY AVAILABLE", 제목 화면 "CHAPTER COMPLETE ▸ REPLAY ANY OPERATION") 디브리프는 "Chapter 01 complete"다. `playable_complete`는 이제 같은 값이다.

**작전 6을 켜며 나온 것 (2026-09-29, 다음 작전에도 해당).** 위 1–3과 게이트만으로는 잡히지 않은 것이 둘 있었다. 둘 다 시험으로 굳혔다.

- 갈래방의 종류를 id가 아니라 `type`으로 읽는다(`StoryStage01.optional_kind_of`). 작전 1–5는 갈래방을 `O01_SUPPLY`, `O02_RESEARCH`로 부르지만 작전 6–10은 자리 이름(`O01_STORES`, `O02_NURSERY` …)으로 부른다. 스테이지는 앞의 id만 알아서 두 보급·신호 회수가 지급되지 않았고 런 부스트가 켜지지 않았고 풀플레이 봇이 첫 갈래방으로 영영 걸어갔다. `full_op_06`이 잡았고, `site7_campaign_progression_smoke.gd`가 이제 출격 가능한 모든 작전의 두 갈래방을 실제 상호작용으로 회수해 본다. 새 작전의 갈래방 `type`은 순서대로 `SUPPLY`, `RESEARCH`여야 한다(데이터 게이트가 이미 요구한다).
- 진행 스모크의 엄폐 소품 하한은 방마다 하나다(작전 1–5는 12–15개, 작전 6은 11개를 쓴다). 그려 둔 소품은 모두 붙어야 한다는 검사는 그대로다.

**작전 6의 검증 (6절 E).** 결과와 캡처는 `qa/site7_op6_enable_20260929/README_KO.md`에 있다.

**작전 7을 켜며 나온 것 (2026-09-30, 다음 작전에도 해당).**

- 오래된 반복문 게이트를 일반화했다. `campaign_data`의 "작전 반복문이 출격 가능한 작전까지 닿는가" 검사는 처음엔 "다섯에서 멈춘 반복문"만 알았다. 이제 출격 가능한 수가 몇이든 `range(1, N)`, 튜플, 목록, 표가 앞 작전에서 끝나면 어느 파일인지 말해 준다. 작전 8을 켤 때 넓힐 곳은 이 게이트가 알려 준다.
- **방 바닥 공정성이 새 방에서 실패할 수 있다.** 보스 패턴 스모크(`boss_pattern`)는 빈 바닥에서 재고, `boss_room_fairness`는 그 작전의 진짜 보스방 바닥과 엄폐에서 잰다. 작전 7에서 CRYO의 3페이즈 축 레인(길이 900)이 R05_VAULT의 좁은 서쪽 턱과 문 어귀에서 1.5명 폭의 빈 바닥을 남기지 않았다(25 px 격자에서 10곳, 20 px에서 20곳). 규칙을 낮추지 않고 레인을 300 px(`FROST_AXIS_REACH`, 두 번째 막대까지)로 줄였다. 길이별 실패(20 px 격자, 7,260 공격): 900 → 20, 400 → 14, 340 → 0, 300 → 0, 레인 없음 → 0. `boss_pattern`이 300을 고정하고 340 이하만 허용한다. 다음 보스(GANTRY, ARCHIVE, ORIGIN)도 그 작전이 열리면 자기 방에서 같은 시험을 받는다. 통과하지 못하면 규칙을 낮추지 말고 패턴이나 방을 맞춘다.
- **엄폐물.** R05_VAULT의 소품 목록은 비어 있다(Codex의 Stage B 기록: 방 중앙에 엄폐물을 두지 않음). 작전 1–7에서 엄폐물이 없는 방은 이 방뿐이다. `campaign_data`는 방마다 행이 있는지, 진행 스모크는 작전 전체에 방 수 이상의 소품이 붙는지를 보므로 통과한다(작전 7은 9개, 작전 6은 11개, 1–5는 12–15개). 보스방에 엄폐물을 더할지는 Codex의 그림 작업이며 사용자가 원할 때만 한다. 더하면 방의 공정성 기하가 바뀌므로 `boss_room_fairness`를 다시 돌린다.

**작전 7의 검증 (6절 E).** 결과와 캡처는 `qa/site7_op7_enable_20260930/README_KO.md`에 있다.

**작전 8을 켜며 나온 것 (2026-09-30, 다음 작전에도 해당).**

- **봇 풀플레이가 자주 진다.** `full_op_08`은 러너에서 5번 중 2번만 EXTRACTED(196초, 그리고 커밋된 끝에서 돌린 full 스위트의 199초)이고 3번은 WIPED(엘리트방 R04에서 74–76초 두 번, 보스방에서 139초 한 번)였다. 켜기 전에 직접 돌린 한 번은 EXTRACTED(193.5초)였다. 원인은 데이터와 구조다. 작전 8은 PRISM이 9기(모든 작전 중 가장 많다. 작전 4–7은 7, 6, 6, 4)이고 PRISM이 모든 실행에서 가장 큰 피해원이며(180–282), 보급 갈래 O01_DEPOT이 엘리트방 R04에서 갈라져(작전 5–7은 R02, R01, R02) 엘리트방 앞에서는 회복할 곳이 없다. R02가 매번 190–220 HP를 깎아 조작 대원이 5–48 HP로 R04에 들어선다. 수치는 그대로 두었다. 엘리트방, PRISM 수, 보급 갈래를 손보거나 러너가 WIPED를 다시 시도하게 하는 것은 균형과 도구 정책이라 사용자가 정한다. 다음 작전을 켤 때도 종류별 적 수와 갈래의 부모 방(`from`)을 미리 세어, 회복이 엘리트방 뒤에 있는지 본다.
- **켜기 전에 보스방 공정성을 미리 잴 수 있다.** `boss_room_fairness`는 출격 가능한 작전만 돌지만, 켜기 전에 작전을 출격 가능 목록에 억지로 넣은 사본으로 돌리면 새 보스방을 미리 잴 수 있다. GANTRY는 그렇게 R05_TERMINAL에서 예고 시간을 1.6초로 맞춰 두어(커밋 `628aeae8`) 켤 때 바로 통과했다(13검사, 1,410 공격 중 실패 0, 가장 나쁜 자리의 안전 바닥 180 px는 한도 그대로, 탈출 여유 0.30초). ARCHIVE와 ORIGIN도 판이 들어오면 켜기 전에 같은 방식으로 잰다.
- **오래된 반복문 게이트.** 러너 밖에 있던 라이브 진입 스모크를 `PER_OPERATION_FILES`에 넣어 작전 9를 켤 때 `range(1, 9)`가 잡히게 했고, 8개와 9개 작전 대조를 더했다.

**작전 8의 검증 (6절 E).** 결과와 캡처는 `qa/site7_op8_enable_20260930/README_KO.md`에 있다.

**작전 9를 켜며 나온 것 (2026-10-01, 다음 작전에도 해당).**

- **full 스위트가 한 번에 72/72로 끝나지 않을 수 있다.** 작전 9를 연 커밋의 첫 full 실행은 69/72였다. `traversal_audit`는 종료코드 −1(4,294,967,295)로 끝났다. 시험 스크립트가 낸 실패가 아니라 프로세스가 끊긴 값이고, 같은 코드에서 직접 재실행(815초)과 러너 재실행(809초)이 모두 통과해 원인은 증명하지 못한 채 외부 종료로 적었다(여러 AI 세션이 함께 쓰는 PC). `full_op_07`은 이 기록에서 처음으로 졌다가(R04_COMPRESSORS, 140초) 재실행에서 이겼다(220초). `full_op_08`은 그날 4번 모두 보스방에서 졌다(위 작전 8 블록의 알려진 한계, 코드 변경과 무관). 기록에는 그대로 적는다: 72/72로 끝난 실행은 없고 실패한 시험마다 재실행 결과를 따로 적는다. 시험의 한도를 낮추지 않는다.
- **방 바닥 공정성은 미리 맞추면 켜는 날 한 번에 통과한다.** INDEX SPIRE는 열기 전에 진짜 R05_STACKS 바닥에서 재서 `ECHO_WINDUP`을 1.0 → 1.3초로 맞췄고(커밋 `e4a305d6`) 켠 뒤 세 격자(100, 50, 25 px)에서 모두 통과했다. 가만히 선 대원 한 자리에 메아리가 쌓이는 패턴은 벽 곁에서 여유가 가장 먼저 줄어든다. 다음 보스(ORIGIN)도 그 방이 생기면 열기 전에 같은 방식으로 맞춘다.
- **오래된 반복문 게이트가 통했다.** 라이브 진입 스모크가 감시 목록에 있어 `range(1, 9)`가 작전 9를 켤 때 잡혔다(작전 8 기록의 개선). 아홉·열 작전 대조군을 더했으니 작전 10을 켤 때 넓힐 곳도 이 게이트가 알려 준다.
- **엄폐물이 없는 보스방이 셋이다**(작전 7 R05_VAULT, 작전 8 R05_TERMINAL, 작전 9 R05_STACKS). 방의 설계 선택으로 보고 고치지 않았다. 더하려면 Codex의 그림 작업이고 `boss_room_fairness`를 다시 돌린다.
- **방의 문 주머니.** R02_NAVE의 NE 문 에이프런은 먼 쪽 가장자리가 수직선이라 데크 위로 약 69 px 솟은 주머니가 남는다. 정렬 시험은 통과하지만 사람이 W+D를 계속 누르면 낄 수 있다(A나 S로 빠진다). 작전 8의 R01_GATE처럼 에이프런 윤곽을 대각선으로 다시 추적하면 없어진다(Codex, 그림 생성 없음, 사용자가 원할 때만).

**작전 9의 검증 (6절 E).** 결과와 캡처는 `qa/site7_op9_enable_20261001/README_KO.md`에 있다.

**작전 10을 켜며 나온 것 (2026-10-02, 작전이 더 생기면 해당).**

- **열기 전에 맞춘 보스는 켜는 날 한 번에 통과한다(GANTRY, INDEX SPIRE에 이어 세 번째).** ORIGIN CORE는 판이 들어온 뒤 사본으로 진짜 R05_CORE 바닥을 열 격자(100–10 px)에서 재서 40·20·15·10 px 격자의 실패를 잡고 마지막 단계 예고를 1.6초로 맞춰 두었다(`ORIGIN_LATE_WINDUP`, 커밋 `749ff72b`). 켠 뒤 러너의 시험이 여섯 격자(100·75·50·40·25·20 px)에서 공격 330 / 654 / 1,386 / 2,118 / 5,472 / 8,562개 중 실패 0, 가장 가까운 안전 바닥 최악 120–150 px(한도 180), 가장 빠듯한 탈출 여유 0.33초(한도 0.25)로 통과했다. **러너의 시험은 격자를 20 px 아래로 줄이지 않는다**(`--grid`를 20으로 묶는다). 더 촘촘한 15·10 px 격자는 사본에서만 잴 수 있다. 여유와 한도의 차이가 0.08초뿐이고 가장 빠듯한 곳은 2페이즈의 두 번째 공격(빈 바닥 120 px을 걸어 나가는 데 0.87초, 예고 1.2초)이므로 R05_CORE의 바닥이나 엄폐, ORIGIN의 예고를 바꾸면 이 시험이 먼저 실패한다.
- **보류된 작전이 없으면 보류 대조군은 돌지 않는다.** `campaign_data`의 보류 관련 검사(`pending_id`와 오래된 반복문 게이트의 대조군)는 작전이 하나라도 보류일 때만 돈다. 열 작전이 모두 열린 지금은 292검사이고(보류 하나일 때 297) 다섯 개가 빠진다. 작전을 더하면 그 행을 `"deployable": false`로 올릴 때 다시 돈다.
- **보스 캡처의 `TEST_BED`는 비었다.** 열 보스가 모두 자기 방에서 찍힌다. 시험대 기계(`_test_bed`, `_boss_row`, `_stage(swap)`)는 남겨 두어 다음 보스가 방보다 먼저 올 때 쓴다.
- **`chapter_complete`와 `playable_complete`가 같은 값이 되었다.** 두 자리 번호는 기지 UI(`mission_id.right(2)`)와 제목 화면에서 문제가 없었다(`campaign` 235검사, `demo_integration` 26검사, 라이브 진입 스모크 열 작전 PASS). 음악 스모크 `demo_music_smoke`(러너에는 없다, 52검사)도 통과해 작전 10이 스테이지 곡 5를 다시 쓰는 것을 확인했다. 이 스모크는 추적 중인 `qa/music_integration_20260920/`의 파일 둘(`runtime_check.json`, `native_music_mix.wav`)을 다시 쓰므로 돌린 뒤 `git checkout`으로 되돌렸다.
- **러너의 시험 예산.** `connector_alignment`는 1,446초(예산 1,800초의 80%, 1,060검사), `traversal_audit`는 897초(1,200초의 75%, 2,394검사)가 걸렸다. full 스위트는 73개에 5,421초(약 90분)다.
- **full 스위트가 이번에도 73/73으로 끝나지 않았다.** 70/73이었다. `rook_app`이 1,895검사 중 한 검사를 놓쳤고(재실행 통과), `full_op_01`이 처음으로 졌고(보스방, 재실행 통과), `full_op_07`이 R04_COMPRESSORS에서 졌다(재실행 첫 판도 졌고 다음 두 판은 이겼다). 켜기와 관계없다고 판단했다(근거는 기록 6절). 한도를 낮추거나 시험을 빼지 않았다. 앞으로도 풀플레이 패배는 재실행으로 가르고, 경로·보상·탈출에서 멈추면 결함으로 읽는다.
- **봇.** `full_op_10`은 full 스위트에서 EXTRACTED(231.2초, 696.5 HP)다. R02_RELAY가 매판 385–408 HP(이번 392.5)를 깎고, 보급 갈래 O01_VAULT가 보스방에서 갈라져 보스 앞에서는 회복할 곳이 없다. 수치는 그대로 두었다(사용자가 정한다).
- **`null` 심연은 처음에 거의 검었고, 같은 날(2026-10-02) 밝혔다.** 흰 격자와 붉은 점이 매우 흐려서(약 4배로 밝혀야 보인다) 화면에서는 검은 배경에 가깝게 보였고, 사용자가 이를 보고 검은 배경을 없애 달라고 다시 요청했다(2026-09-27 요청은 `AGENTS.md`의 "Mood light"). 행의 바탕·안개·연무와 격자·붉은 점을 올려 보이는 허공의 평균 밝기를 0.025에서 0.124로 만들었고(작전 1–7·9는 0.062–0.107, 작전 8의 새벽 바다는 0.175; 작전 1–7·9의 첫 방 R01은 0.028–0.046으로 이번에 손대지 않았다), 밝은 허공이 드러낸 벽 틈새 투명 문제는 `void_fill_px`로 막았다. 근거와 수치는 `qa/site7_null_abyss_20261002/README_KO.md`와 `AGENTS.md`의 "Operation 10 void lit"이다. 사용자가 같은 날 보고와 전/후 비교판을 보고 "승인한다"고 답했다(2026-10-02). 이 승인은 밝힌 허공 모습만 뜻한다(판 15장과 ORIGIN CORE 그림은 같은 날 "판·보스 그림까지 승인"으로 따로 승인했다). 다른 작전의 첫 방은 포함하지 않는다.

**작전 10의 검증 (6절 E).** 결과와 캡처는 `qa/site7_op10_enable_20261002/README_KO.md`에 있다.

### D. 음악 (선택)

작전 6–10은 스테이지 곡 1–5를 순환해 쓴다(`demo_music.gd`의 `stage_key`: 카탈로그에 자기 `stage<N>` 곡이 있으면 그것, 없으면 `((N-1) % 자기 곡 수) + 1`). 곡이 생기면 `sound/music/runtime/`에 넣고 `sound/music/catalog.json`에 `stage6`–`stage10`을 더한다(`allocation.json`과 `sound/README.md`도 맞춘다). `tests/smoke/demo_music_smoke.gd`의 "작전 6–10 곡 재사용" 검사와 `catalog.size() == 9`를 그때 고친다. 음악은 켜는 조건이 아니다.

### E. 검증과 기록

1. quick 스위트와 `--suite full`이 PASS한다. 켠 작전의 `full_op_0N`이 PASS한다(`full_op_03`처럼 봇이 마지막 보스에서 자주 지면 다시 돌려 본다. 계속 지면 수치를 조정하되 공정성 규칙(보스 지시서 3.1절)을 낮추지 않는다).
2. 사람 플레이로 균형을 확인한다. 봇 통과는 균형 승인이 아니다.
3. 기록: `qa/site7_ops_6_10_<날짜>/README_KO.md`. 로컬 커밋만 한다. GitHub 작업과 웹 배포는 하지 않는다.

---

## 7. 데이터 게이트

`tests/smoke/site7_campaign_data_smoke.gd`(러너 이름 `campaign_data`, quick 스위트)가 작전 1–10 전부를 검사한다. 그림, 균형, 플레이 승인은 아니다.

- 카탈로그: 10행, 행 i의 id는 `MIS_CH01_%02d`, `requires`는 앞 행, 출격 가능한 작전은 앞쪽에서 연속, `available`/`next_after`/`recommended`/`ui_rows`의 의미.
- 모든 작전 파일: 방 순서와 종류, 갈래의 `from`, 전투방마다 동시 5기 이상과 증원(`reinforce_at` ≥ 1), 작전 합계 18기 이상, 엘리트 접두어는 보스에 없음, 위험지대는 보스방에 없음, 프로필이 있는 적만, 정보 보상 행, 탈출 창, 목표 사슬.
- 출격 불가 작전: `staging`(상태, 보스 id 형식과 금지 조각, 보스 방과 체력, 판 접두어와 경로, 구조)이 유효하고, 보스 행이 `staging.boss.id`의 등록된 보스이며 그 프로필의 `boss_pattern`이 `staging`의 패턴과 같고 기계 명세 파일이 있다. 출격 가능 작전: `staging`이 없고, 판 8+7장이 파일로 있고, 세계 배치, 무드 행, 방마다 소품, 전투방마다 배치, 등록된 보스 프로필과 기계 명세가 있다.
- 작전 사이: 보스 체력이 순증하고, 보스 id와 패턴이 겹치지 않고, 경로 구조(방향과 갈래 부모)가 겹치지 않는다.
- 안내 문구: 작전 5–9의 디브리프와 ASTER 마지막 브리핑 줄은 출격 불가 후속을 알리지 않고, 출격 가능한 후속은 디브리프가 이름으로 알린다.
- 5에서 멈춘 시험: 출격 가능 작전이 5개를 넘으면 6절 표의 파일에 `range(1, 6)`, 5에서 끝나는 목록, `(1,2,3,4,5)`가 남아 있으면 실패한다.
- 부정 대조(고장 난 사본이 실패하는지): 출격 가능인데 `staging` 있음, 등록 안 된 보스, 증원 없는 전투방, 중복 방 id, 접두어가 붙은 보스, 출격 불가를 일찍 켬, 상태 없는 `staging`, 금지 조각이 든 보스 id, 거짓 안내 문구, 남은 반복문, 보스 행이 자리표시로 돌아감(`placeholder`), 보스 패턴이 `staging`과 다름(`wrong_pattern`).

---

## 8. 위험과 결정

1. **원화 분량.** 판 75장 + 보스 5장. 맵 키트 v2 실적은 파일럿 3장에 20회, 규격이 잡힌 뒤 12장에 14회였다. 110–150회로 잡지만 늘 수 있다. 한 작전씩 승인하며 가는 것이 이 때문이다.
2. **판 임시 대용.** 판 없이 작전을 시험하려고 다른 작전의 판을 빌리면 `AGENTS.md`의 "어떤 판도 두 작전이 함께 쓰지 않는다"를 어긴다. 하려면 사용자의 명시적 예외가 필요하고, `site7_battle_geometry_smoke.gd`의 75장 검사를 그 동안 끄거나 고쳐야 한다. 지금은 하지 않는다.
3. **후반 보상의 소비처**(3절). 해결: 업그레이드를 6단계로 늘리고 4–6단계가 부품과 신호 조각도 쓰게 했다. 남은 위험 둘. 새 종류의 소비처(장갑, 무기 제작 같은 것)는 넣지 않았다. 효과와 기지 화면의 자리가 필요해 사용자 결정이다(9절). 곡선은 총량 검사와 모의일 뿐이라, 후반 작전이 열린 뒤 실제 획득량으로 다시 본다.
4. **음악.** 작전 6–10은 곡을 돌려 쓴다. 곡을 새로 얻으면 6절 D.
5. **균형.** 적 수와 체력 배율, 보스 체력은 곡선을 잇는 값이지 검증된 값이 아니다. 작전 10 봇 풀플레이는 실패할 수 있다. 사람 플레이가 기준이다.
6. **작전 3·4의 낡은 디브리프.** 작전 3의 COMMAND 디브리프는 "The offshore operation is not deployed yet"로 끝나고 작전 4의 것은 "offshore operation is unlocked"다. 지금 게임 상태와 다르지만 이번 범위가 아니라 그대로 두었다.
7. **`chapter_complete`.** 작전 10을 켰으므로 열 작전을 모두 깨면 참이 된다(`playable_complete`와 같은 값). 켜기 전에는 참이 될 수 없어 챕터 완료를 보는 곳은 `playable_complete`를 썼고, 표시 문구는 두 값 모두에 맞다.

---

## 9. 그림 없이 지금 할 수 있는 일 (다음 후보)

- 새 심연 스타일 5종(`spore`, `cryo`, `dawn`, `vault`, `null`)의 셰이더와 `STYLES` 항목. 판 없이도 배경 쿼드를 단독으로 그려 볼 수 있다.
- ~~보스 패턴 5종의 `_boss_attack` 분기와 공정성 스모크(보스 지시서 4절).~~ 완료(2026-09-29, 보스 원화가 들어온 뒤 함께 등록).
- ~~새 보스 5종의 피격, 총구, 투사체 효과 계열(코드로만 그린다, `vfx_painter.gd`).~~ 완료(2026-09-29).

- 새 소비처 종류. 지금 소비처는 두 업그레이드와 분석 3건이다. 종류를 늘리려면 효과와 화면이 필요하다. 예: 장갑(받는 피해 감소. `OperatorActor.apply_damage`와 `apply_campaign_modifiers`에 키 하나, 부품 소비), 무기 제작(구매하면 `unlocked_weapons`에 추가, 부품과 신호 소비). 기지 시설 패널은 COMMAND, ARMORY, LAB 세 버튼으로 차 있어서 자리를 넓혀야 한다.
