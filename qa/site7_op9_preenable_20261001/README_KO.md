# 작전 9 MEMORY VAULT 켜기 전 검증 (Claude, 2026-10-01)

작전 9는 **아직 켜지 않았다.** `data/missions/MIS_CH01_09.json`의 `staging` 블록과 `data/story/site7_campaign.json`의 `"deployable": false`, `pending`은 그대로다. 사용자의 "작전 9 켜라"가 없었다.
이 문서는 Codex의 단계 D 연결(판 15장과 데이터)을 Claude가 독립으로 다시 잰 결과와, Claude 몫(감사 상한, 시험 반복문, 보스 공정성, 완주 시험)의 결과다. 그림, 플레이, 균형 승인이 아니다.

## 1. 기준과 측정 순서

- 기준 커밋 `46d812de`. Claude의 변경은 세 커밋이다: `9cb4d2d7`(감사 C06/C07 상한 32.5°, `plate_axis`, 작전 9를 넣은 시험 반복문 12곳, 문서), `e4a305d6`(INDEX SPIRE 메아리 예고 시간), `46d812de`(제작 지시서 상태).
- Codex의 작전 9 연결(판 15장, 데이터 JSON 9개, 심연 `vault` 코드, 캡처 도구, 매니페스트)은 측정하는 동안 미커밋 작업 트리였고, 15:33에 Codex가 `1d0f7eb1`(연결과 기록)과 `7081d30a`(인용한 검토 이미지)로 커밋했다. 이 문서는 그 파일을 건드리지 않았다. 커밋에 든 코드·데이터 파일 11개는 모두 15:03 이전에 마지막으로 바뀌었고(15:04 이후 바뀐 비-`qa/` 파일은 매니페스트 `.md` 하나), 아래 Godot 실행은 그 내용으로 했다. 데이터 JSON 9개를 `46d812de`와 구조로 비교하면 바뀐 것은 작전 9 행의 추가뿐이고 작전 1–8의 행은 그대로다. 코드 변경은 `site7_abyss_backdrop.gd`의 `vault` 스타일 추가(다른 스타일 가지는 그대로)와 판 테두리 캡처 도구뿐이다.
- 14:50에 Codex가 `S9_R02`의 NE 문 등록 위치를 고치고 월드 배치를 다시 풀었다(4절). 그 전에 잰 값 중 파이썬으로 다시 잴 수 있는 것(판 재현, strict 감사, 데이터 검사)은 고친 트리에서 다시 잰 값만 적었다. 고치기 전 트리에서 잰 Godot 실행은 그렇다고 표시했다.

## 2. 판 15장 독립 재현

| 판 | 크기 | RAW = MASTER | GAME 노출 계수 | 바닥 축 | 바닥 휘도 | 바닥 채도 |
|---|---|---|---|---|---|---|
| S9_C01 | 1774×887 | 같음 | 0.7817(LUT 차이 0) | 25.88° | 0.200 | 0.025 |
| S9_C02 | 1774×887 | 같음 | 0.7361(LUT 차이 0) | 23.79° | 0.200 | 0.044 |
| S9_C03 | 1774×887 | 같음 | 0.7115(LUT 차이 0) | 25.35° | 0.200 | 0.019 |
| S9_C04 | 1774×887 | 같음 | 0.7208(LUT 차이 0) | 23.26° | 0.199 | 0.040 |
| S9_C05 | 1774×887 | 같음 | 0.9274(LUT 차이 0) | 25.53° | 0.226 | 0.053 |
| S9_C06 | 1254×1254 | 같음 | 0.7574(LUT 차이 0) | 32.26° | 0.200 | 0.060 |
| S9_C07 | 1254×1254 | 같음 | 0.6822(LUT 차이 0) | 32.03° | 0.200 | 0.013 |
| S9_O01 | 1672×941 | 같음 | 0.7917(LUT 차이 0) | 26.86° | 0.200 | 0.059 |
| S9_O02 | 1672×941 | 같음 | 0.723(LUT 차이 0) | 25.28° | 0.200 | 0.064 |
| S9_R01 | 1672×941 | 같음 | 0.7329(LUT 차이 0) | 25.09° | 0.200 | 0.042 |
| S9_R02 | 1672×941 | 같음 | 0.75(LUT 차이 0) | 23.90° | 0.200 | 0.043 |
| S9_R03 | 1672×941 | 같음 | 0.691(LUT 차이 0) | 25.11° | 0.200 | 0.085 |
| S9_R04 | 1672×941 | 같음 | 0.8146(LUT 차이 0) | 25.05° | 0.200 | 0.001 |
| S9_R05 | 1672×941 | 같음 | 0.775(LUT 차이 0) | 25.75° | 0.200 | 0.075 |
| S9_R06 | 1672×941 | 같음 | 0.8433(LUT 차이 0) | 24.69° | 0.200 | 0.059 |

`plate_verification.txt`(`verify_op9_final.py`): 15장 모두 RGB, RAW와 MASTER가 바이트 같고, GAME은 MASTER에 노출 계수 하나를 곱한 sRGB LUT와 픽셀 단위로 같다(최대 차이 0), 바닥 윤곽 검사 문제 0. 새로 받은 `S9_C06`, `S9_C07`의 RAW와 GAME 해시는 Codex의 매니페스트와 같다.

- 원본 크기 검토: `native_crops.py`가 판마다 960×540 크롭 4장을 1:1(축소 없음)로 이어 붙인 1920×1080 시트 15장을 만든다(방은 문 입구와 바닥 모서리, 통로는 왼쪽 끝 / 30 % / 65 % / 오른쪽 끝). 15장을 모두 봤고 녹은 형상, 벽 반복, 끊긴 난간, 어긋난 문틀은 없었다. 통로의 벽 불빛 색이 양쪽 방에 맞춰 호박색에서 청색으로, 보라에서 호박색으로 넘어가는 것은 설계한 대로다. 시트 이미지는 용량 때문에 기록에 넣지 않았다(스크립트로 다시 만든다). 그림 승인이 아니다.
- 이 기록의 그림 한 장(`r02_ne_pocket_after_door_correction.png`, 1920×1200)은 `tools/art_pipeline/validate_visual_evidence_1080p.py`를 통과했다(`visual_evidence_1080p.json`, 컨테이너 해상도와 디코딩만 확인한다).

## 3. strict 감사와 데이터 검사

- `python tools/environment/audit_site7_plate_lighting.py --mission MIS_CH01_09 --strict`: **판 15 / 이음매 14 통과, 이음매 예외 없음**. 월드 배치를 다시 푼 뒤에도 같다. 달라진 것은 `S9_C01`과 `R02_NAVE`의 이음매 하나의 수치뿐이다(채도비 1.16 → 1.22배, 색조 차 0.38° → 1.20°, 밝기 차 −0.016 → +0.015스톱, 목표 1.5배 / 30° / 0.35스톱). `strict_audit_op9.json`은 고치기 전, `strict_audit_op9_after_door.json`은 고친 뒤 트리의 결과다.
- C06/C07 통로의 바닥 축 32.26° / 32.03°는 사용자가 승인한 상한 32.5°(2026-10-01) 안이다. 다른 판은 22.5–30.5° 안이다(`plate_axis` 2 체크).
- 고친 트리에서: `world_layout --check` PASS(9개 작전), `mood_light --check` PASS(판 135, 조명 웅덩이 708, 허공 마스크 135, 접촉 그림자 15), `plate_axis` 2, `seam_waiver` 10, `mood_contact` 5 체크 통과(`data_checks.txt`).

## 4. 정렬 시험의 작전 9 실패와 Codex의 수정

- Codex의 커스텀 러너(`qa/regression_runs/20261001_135223_custom`)는 14/15 통과, `connector_alignment`만 실패했다: `MIS_CH01_09/link_0 crossed back with WASD`(954 체크). 차단 지점은 대원 (−423.3, 1313.1), 출발 (−536.1, 1441.9).
- Claude가 한 통로(작전 9의 C01)만 도는 탐침으로 40초 만에 같은 좌표에서 재현했다(`connector_alignment_op9.txt`). 원인: R02의 NE 문 에이프런 바닥 윤곽의 먼 쪽 가장자리가 수직선(정규화 u 0.7416 → 0.75)이라 데크 위쪽 경계 위로 약 69 px 솟은 주머니를 만든다. 데크의 왼쪽 끝은 높이 35 px(8 % 안쪽에서 104 px)로 좁다. 시험의 `W+D` 45° 조향이 데크를 벗어나 주머니의 위쪽 경계를 따라 올라가 수직 가장자리와 만나는 구석(−419, 1295.7)에서 대원의 가장자리 여유 20 px를 두고 갇혔다. 작전 8의 R01_GATE 문 에이프런은 가장자리가 대각선이라 같은 주머니가 대원을 데크로 미끄러뜨린다.
- Codex도 같은 결함을 스스로 찾았다. `S9_R02`의 NE 등록 문을 그려진 문턱 중심 (1155, 359) → (1170, 346) px로 옮겼다(Codex 기록: 이전 점은 문턱 줄무늬 아래 방 안쪽에 있었다). 월드 배치를 다시 풀었고(`world_layout --check` PASS), 전투방 적 자리 몇 곳(R02 [5], [7], R04 [3], [7], [8], R05_STACKS 두 자리 추가)을 고쳤다. 바닥 윤곽, 판 픽셀, 시험은 바뀌지 않았다. Codex의 작전 9 정렬 시험 재실행: **PASS, 106 체크, 실패 0**(Codex의 `.cache/diag/site7_ops_d/integration/connector_op9_corrected.log`). Claude도 최종 트리에서 같은 시험을 다시 돌렸다(`--mission=9`, 러너 없이): **PASS 106 체크, 통로 7개, 실패 0, 155초**(`connector_alignment_op9_final.txt`).
- 시험은 낮추지 않았다. 주머니는 그대로 남아 있어서, 사람이 문에서 `W+D`를 계속 누르면 구석에 낄 수 있다(`A`나 `S`로 빠진다). 시험 기준은 충족한다. 없애려면 에이프런 윤곽을 작전 8처럼 대각선으로 다시 그리면 되는데 그림 생성이 필요 없는 Codex의 추적 일이고, 사용자가 원할 때만 한다. 증거 그림: `r02_ne_pocket_after_door_correction.png`(1920×1200, 고친 뒤의 R02 바닥 파랑, C01 데크 초록, 빨간 점은 문 위치).

## 5. 보스 INDEX SPIRE를 R05_STACKS에 맞춤

`boss_room_fairness`는 출격 가능한 작전만 돌므로 작전 9용 사본(`boss_room_fairness_op9.gd`, 반복문만 `MIS_CH01_09`로 바꿈)으로 진짜 방에서 쟀다(사본은 git이 무시하는 `.cache/claude_scratch/op9_fairness/` 아래에 두고 `godot --headless --path . -s res://.cache/claude_scratch/op9_fairness/boss_room_fairness_op9.gd -- --grid=50 --out=res://.cache/claude_scratch/op9_fairness/g50.json`처럼 돌렸다. 이 기록의 `.gd` 파일은 그 사본이다).

| 격자 | 맞추기 전: 공격 / 실패 / 가장 가까운 빈 바닥 최악 / 가장 빠듯한 여유 | 맞춘 뒤: 같은 값 |
|---|---|---|
| 100 px | 258 / 0 / 90 px / 0.35초 (PASS) | 258 / 0 / 90 px / 0.65초 (PASS) |
| 75 px | 498 / 0 / 120 px / 0.35초 (PASS) | 498 / 0 / 120 px / 0.65초 (PASS) |
| 60 px | 762 / 0 / 90 px / 0.35초 (PASS) | 762 / 0 / 90 px / 0.65초 (PASS) |
| 50 px | 1,134 / 1 / 120 px / 0.13초 (FAIL) | 1,134 / 0 / 120 px / 0.43초 (PASS) |
| 40 px | 1,752 / 0 / 90 px / 0.35초 (PASS) | 1,752 / 0 / 90 px / 0.65초 (PASS) |
| 30 px | 3,156 / 1 / 120 px / 0.13초 (FAIL) | 3,156 / 0 / 120 px / 0.43초 (PASS) |
| 25 px | 4,524 / 2 / 120 px / 0.13초 (FAIL) | 4,524 / 0 / 120 px / 0.43초 (PASS) |
| 20 px | 7,026 / 2 / 120 px / 0.13초 (FAIL) | 7,026 / 0 / 120 px / 0.43초 (PASS) |

- 원인: `echo_copy`는 목표가 서 있던 자리의 메아리 세 개를 쌓고, 가만히 서 있으면 모두 그 자리에 겹친다. 가장 새 메아리의 예고가 1.0초였고, 벽 곁에서 가장 가까운 빈 바닥이 120 px(걸어서 0.87초)이면 여유가 0.13초로 한도(0.25초)에 못 미쳤다.
- 맞춤(`e4a305d6`): `ECHO_WINDUP` 1.0 → 1.3초(메아리 1.3/1.4/1.5초, 목표 자신의 바닥 1.6초, 마지막 페이즈의 레인 1.7초). 한도(180 px, 0.25초, 138 px/s)는 낮추지 않았다. 설계상 메아리 예고가 0.3초 더 길어졌다.
- `site7_boss_pattern_smoke.gd`가 `ECHO_WINDUP_MIN`(1.12초 = 걸어서 180 px + 여유 0.25초)을 바닥으로 고정한다. 부정 대조: 상수를 되돌리고 `boss_pattern`을 돌리면 18개 오류로 실패한다(`boss_pattern_negative_control_echo.txt`). 되돌린 뒤 파일은 커밋 내용과 같다.
- 맞춘 뒤 `boss_pattern` 977 체크, `boss_duel` 1,124 체크, `boss_registry` 161 체크, `robot_roster` 302 체크, `boss_room_fairness`(작전 1–8) 13 체크 통과(`boss_pattern_after_fit.json`, `boss_duel_after_fit.json`).

## 6. 작전 9를 넣은 시험

### 6.1 Codex의 러너 실행 (최종 트리)

둘 다 `git_head` `46d812de` 위에 미커밋 항목 17개(Codex의 작전 9 작업)가 있는 상태로 돌았고, 그 작업이 `1d0f7eb1`에 커밋됐다(1절). `qa/` 보호 검사는 바뀜, 사라짐, 추가 모두 0이다. 러너 기록 폴더는 git이 무시하므로 이 기록에는 요약만 옮긴다.

| 실행 | 범위 | 결과 | 시간 |
|---|---|---|---|
| `qa/regression_runs/20261001_150250_custom` | `traversal_audit` 2,155 체크, `world_route` 85, `battle_geometry` 4,538 (셋 다 full 전용) | PASS 3/3 | 879초 |
| `qa/regression_runs/20261001_152035_quick` | quick 44개 전부 | PASS 44/44 | 563초 |

quick 가운데 작전 9와 보스에 닿는 것: `campaign_data` 286, `boss_registry` 161, `boss_pattern` 977, `boss_duel` 1,124, `boss_room_fairness` 13(작전 1–8), `robot_roster` 302, `combat_density` 61, `floor_segment` 21, `elite_affix` 63, `zone_hazard` 299, `firing_lane` 289, `world_layout`, `mood_light`, `plate_axis` 2, `seam_waiver` 10, `mood_contact` 5.

### 6.2 Claude의 직접 실행 (같은 코드·데이터, 러너 밖)

러너를 건드리지 않으려고 `qa/`에 쓰지 않는 시험만 Godot 헤드리스로 하나씩 돌렸다. 러너가 하나라도 뜨면 내 프로세스를 죽이는 감시 스크립트 아래에서 돌렸고(중단 없음), 출력은 모두 git이 무시하는 `.cache/`에 있다.

| 시험 | 결과 | 시간 |
|---|---|---|
| `boss_room_fairness_op9.gd`(작전 9만 도는 사본), 격자 100/75/60/50/40/30/25/20 px | 8개 모두 PASS(실패한 공격 0, 5 체크씩) | 8–20초 |
| `site7_boss_pattern_smoke.gd` | PASS 977 | 5초 |
| `site7_boss_duel_smoke.gd` | PASS 1,124 | 39초 |
| `site7_boss_registry_smoke.gd` | PASS 161 | 20초 |
| `site7_robot_roster_smoke.gd` | PASS 302 | 14초 |
| `site7_boss_room_fairness_smoke.gd`(작전 1–8) | PASS 13 | 21초 |
| `combat_density_smoke.gd` | PASS 61 | 22초 |
| `floor_segment_smoke.gd` | PASS 21 | 47초 |
| `elite_affix_smoke.gd` | PASS 63 | 7초 |
| `zone_hazard_smoke.gd` | PASS 299 (방 13개) | 55초 |
| `firing_lane_search_smoke.gd` | PASS 289 | 41초 |
| `site7_connector_alignment_smoke.gd -- --mission=9` (WASD로 통로 7개 양방향) | PASS 106(통로 7개, 실패 0) | 155초 |

### 6.3 넣지 못한 것

- `full_op_09`는 러너에 없다(켤 때 `full_op_%02d` 범위를 넓히면서 등록한다). 봇은 7절에서 직접 돌렸다.
- full 스위트(71개, 약 70분)는 돌리지 않았다. 작전 9를 켜야 그 자리가 생기는 시험이 있고, 켜기 전에 한 번 돌려도 켠 뒤에 다시 돌려야 한다.
- `connector_alignment` 전체(작전 1–9)는 돌리지 않았다. 작전 9만 따로 돌렸다.

## 7. 봇 완주 (기술 시험)

봇은 `tests/smoke/site7_full_operation_smoke.gd -- --mission=MIS_CH01_09`(진짜 액터 물리, 무기 쿨다운, 투사체 충돌, 방 상호작용으로 길을 걷는 시험용 조종)다. 작전 9는 러너에 없어서 직접 돌렸고, 같은 트리에서 연달아 5번 했다(회마다 약 3분, 그동안 러너는 없었다). 요약은 `full_operation_op09_summary.json`이다.

| 회 | 결과 | 게임 시간 | 처치 | R02_NAVE | R03_CHAPEL | R04_GALLERY | R05_STACKS | 받은 피해 합 | 마지막 표본의 대원 체력 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | EXTRACTED | 164.7초 | 25 | 109 | 7 | 80 | 144.2 | 340.2 | 26.6 / 82.3 / 85.2 |
| 2 | EXTRACTED | 166.3초 | 25 | 116 | 0 | 63 | 131.6 | 310.6 | 0 / 98 / 58.2 |
| 3 | EXTRACTED | 161.3초 | 25 | 112 | 0 | 95 | 20.6 | 227.6 | 57.8 / 96.2 / 112 |
| 4 | EXTRACTED | 163.7초 | 25 | 155 | 0 | 78 | 145.6 | 378.6 | 33.6 / 30.3 / 58.2 |
| 5 | EXTRACTED | 165.0초 | 25 | 116 | 0 | 91.5 | 162.5 | 370 | 27.2 / 38.3 / 65.2 |

피해는 적이 대원에게 준 양이고 칸은 경로 단계(1 R02_NAVE, 2 R03_CHAPEL, 3 R04_GALLERY, 4 R05_STACKS)다. 마지막 표본은 마지막 추적 기록의 값이라 한 명이 쓰러진 채일 수 있다.

- **5판 모두 EXTRACTED**였다. 적 25기를 모두 잡고(`full_route_cleared`), 게임 시간 161–166초(벽시계 172–180초), 확보 보상은 5판이 같다: 연구 546, 고물 8, 신호 조각 4, 정보 샘플(ABERRANT 2, ANCHOR 1, SECURITY 3), 탈출 깊이 6, 조각 회수와 원장 회수 모두 참.
- 받은 피해 합은 228–379(평균 325)이다. 작전 8의 같은 봇은 346–616이었고 5번 중 2번만 탈출했다(`AGENTS.md`의 "Operation 8 enabled"). 작전 3도 세 번에 한 번꼴로 졌다. 작전 9의 봇은 이번 5판에서 한 번도 지지 않았다. 다만 작전 8의 값은 러너 안에서 다른 시험과 함께 돈 것이고 이번 값은 혼자 연달아 돈 것이라 조건이 같지 않다.
- 피해원(5판 합 1,627): 드론 546(34 %), 보스 INDEX SPIRE 487(30 %), NULL_PYLON 306(19 %), PRISM 159(10 %), BULWARK 97(6 %), RAM 32(2 %). 작전 8은 PRISM이 가장 컸는데 작전 9는 드론이 가장 크다(드론 11기). R02_NAVE에서 판마다 109–155를 잃는다. 보급 갈래 O01_BLADES는 엘리트방 R04_GALLERY에서 갈라져 R04 앞에서는 회복할 곳이 없다. 봇은 R04를 깬 뒤 O01을 거쳐 보스방 전투 전에 체력을 채웠다(1회에서 추적 틱 5011 → 6000 사이 대원 체력 합 150 → 305).
- 5판 가운데 4판(1, 2, 3, 5회)에서 대원 한 명이 0 HP로 쓰러진 표본이 있다. 1, 3, 5회는 엘리트방 R04_GALLERY에서 쓰러졌다가 되살아났고(실제 F 길게 누르기 되살리기), 2회는 보스방 R05_STACKS에서 쓰러져 탈출할 때까지 그대로였다. 4회는 쓰러진 대원이 없었다. 쓰러진 채로도 탈출했다.
- 이 봇은 기술 시험이다. 사람이 하는 플레이의 난이도와 균형을 말해 주지 않는다. 수치를 손보는 것은 사용자가 정한다.

## 8. 작전 10 보스 ORIGIN CORE 사전 측정

작전 10의 보스방 R05_CORE는 아직 없다. ORIGIN CORE의 `null_convergence`가 기존 보스방에서 얼마나 공정한지 보려고, `boss_room_fairness` 사본(`boss_room_fairness_origin.gd`: 각 작전의 진짜 보스방에 `--pattern=null_convergence`를 얹도록 바꿈)을 작전 1–9의 보스방에서 50 px 격자로 돌렸다(52초, `origin_surrogate_grid50.json`). 한도(180 px, 0.25초, 138 px/s)는 그대로다.

| 작전 / 방의 보스 | 공격 | 실패 | 가장 가까운 빈 바닥 최악(px) | 가장 빠듯한 여유(초) | 엄폐 | 결과 |
|---|---|---|---|---|---|---|
| 1 ANCHOR | 1,266 | 1 | 150 | 0.21 | 2 | 실패 |
| 2 RELAY | 1,254 | 5 | 240 | -0.44 | 2 | 실패 |
| 3 REMNANT | 1,284 | 10 | 120 | -0.66 | 2 | 실패 |
| 4 FORGE | 1,008 | 6 | 210 | -0.22 | 2 | 실패 |
| 5 CARRIER | 642 | 26 | 120 | -0.76 | 2 | 실패 |
| 6 AERATOR | 924 | 16 | 120 | -0.76 | 2 | 실패 |
| 7 CRYO | 1,188 | 5 | 300 | -0.87 | 0 | 실패 |
| 8 GANTRY | 1,410 | 0 | 120 | 0.33 | 0 | 통과 |
| 9 INDEX SPIRE | 1,134 | 0 | 120 | 0.33 | 0 | 통과 |

- 가장 새로 만든 두 방(작전 8의 R05_TERMINAL, 작전 9의 R05_STACKS)은 통과하고, 작전 1–7의 방은 실패한다(최대 642개 중 26개). 실패한 곳은 가장 가까운 빈 바닥이 150–300 px이거나(한도 180 px) 300 px 안에 없는 자리, 또는 예고 1.2–1.3초로는 걸어서 닿지 못하는 자리다(180 px 탈출에는 1.55초가 필요하다).
- 해석: 작전 10의 방이 작전 8–9의 방과 비슷한 크기와 모양(제작 지시서 4.3절 표)이면 통과할 가능성이 높다. 작은 방이나 벽이 가까운 방이면 CRYO(축 레인 900 → 300 px), GANTRY(예고 1.6초), INDEX SPIRE(메아리 1.3초)처럼 방이 생긴 뒤 패턴을 맞춰야 한다. 지금 미리 맞출지는 선택이다. 한도는 낮추지 않는다. 이 값은 작전 10의 방이 아니라 기존 방에서의 참고값이다.

## 9. 알려진 위험

- 작전 9의 구성은 25기(보스 포함): 드론 11(작전 4–8은 5–6), NULL_PYLON 3, PRISM 5, 엘리트 4(R04_GALLERY의 SHIELDED, OVERCHARGED, VOLATILE 2). 작전 8(PRISM 9)만큼 PRISM이 많지는 않지만 드론이 가장 많다.
- 보급 갈래 O01_BLADES는 작전 8처럼 엘리트방 R04_GALLERY에서 갈라져, 엘리트방 앞에서는 회복할 곳이 없다. 연구 갈래 O02_RESTORE는 R03_CHAPEL에서 갈라진다. 봇은 5판 모두 탈출했지만(7절) 3판에서 한 명이 R04_GALLERY에서 쓰러졌고, 작전 8과 3은 봇이 자주 졌다.
- R05_STACKS는 엘리트 없는 보스방이고 엄폐가 없다(작전 9의 엄폐 소품은 9개, 작전 7과 같다. 작전 1–8은 9–15개). 방에 엄폐를 더하면 공정성 기하가 바뀌므로 `boss_room_fairness`를 다시 돌려야 한다.
- 4절의 R02 NE 문 주머니(시험은 통과).
- `vault` 심연의 모습은 헤드리스 시험이 그리지 않는다. 설정값으로 보면 기본색 휘도가 0.011로 작전 1–7(0.010–0.021)과 같은 범위이고 작전 8의 `dawn`만 0.084다. 나는 Codex의 1080p 캡처 네 장(`plate_edges/S9_R05_native_1080p.webp`, `plate_edges/S9_C06_native_1080p.webp`, `runtime_capture/MIS_CH01_09_R02_NAVE_a.webp`, `runtime_capture/MIS_CH01_09_R05_STACKS_a.webp`, 모두 `qa/site7_ops_6_10_plates_20260929/stage_d/finish_20261001/` 아래)만 눈으로 봤고, 판 가장자리의 회색 후광이나 검은 테두리는 보이지 않았다. 허공은 깊은 남보라이고 금빛 필라멘트는 아주 옅다. 검은 배경을 없애 달라는 요청(2026-09-27)에 비추어 이 정도 어둡기를 받아들일지는 사용자의 몫이다.
- 같은 세션 회전 A/B FPS는 하지 않았다(작전별 도구가 없다).

## 10. 이 세션에서 하지 않은 것, 켤 때 할 일

- 하지 않은 것: 작전 9 켜기, `staging` / `deployable` / `pending` 변경, 작전 8의 COMMAND 디브리프 변경, 시험 넓히기 4곳(`site7_live_entry_autostart_smoke.gd`, 러너의 `full_op_%02d`, `site7_boss_pattern_capture.gd`, `site7_campaign_data_smoke.gd`), full 스위트, 자기 방 보스 캡처와 10초 소리 영상(작전이 켜져야 한다), Codex의 판, 무드, 마스크, 감사 도구, 연결 데이터 수정.
- 사용자가 "작전 9 켜라"고 하면(설계 문서 6절 C 순서): `staging` / `deployable` / `pending` 삭제, 작전 8 COMMAND 디브리프를 `Switchyard complete. Memory Vault is now available.`로 교체, 위 4곳 넓히기(`range(1, 10)`), 게이트 `campaign_data,campaign,demo_integration`, quick과 full, 자기 방 보스 캡처(`SABLE_CAPTURE_MISSIONS=9 SABLE_CAPTURE_BOSS=1`), 10초 소리 영상(`SABLE_CAPTURE_ROOT`는 작업 폴더), `qa/site7_op9_enable_<날짜>/`, `AGENTS.md`의 "Operation 9 enabled", `README.md`, `sound/README.md`, 설계 문서. 작전 10의 판(단계 E)은 사용자가 작전 9의 단계를 승인한 뒤에만 시작한다.
- 사람의 플레이와 균형, 판과 보스의 그림 승인은 사용자의 몫이다.

## 11. Codex의 단계 D 보고서와의 대조 (커밋 `52dee5c5` 뒤에 덧붙임)

사용자가 Codex의 단계 D 완료 보고서를 전달했다. 그 주장을 이 기록과, 새로 한 세 가지 확인에 맞춰 봤다.

| Codex 보고 | 대조 |
|---|---|
| 판 15장, ImageGen 34회, 채택 15, 거절 19 | 판별 시도 수의 합이 34(1+3+3+3+3+1+2+2+1+1+2+3+2+3+4), 34 − 15 = 19로 맞다. 시도와 채택 차수는 Codex의 값이고, 해시와 노출 LUT는 2절에서 다시 쟀다. |
| strict 15판·14이음매 PASS, 새 예외 0 | 3절에서 다시 돌려 같다. |
| 레이아웃·무드 `--check` PASS | 3절에서 같다(`data_checks.txt`). |
| 엄폐 `moved=0` | **새로 확인**: `tools/environment/settle_cover_on_floor.gd`를 쓰기 없이 돌려 `SETTLE_DONE moved=0 DRY`(26초, `settle_dry_run_final.txt`). 작업 트리는 그대로다. |
| 최초 회귀 14/15 FAIL(C01 복귀 실패), R02 NE 문을 고친 뒤 통로 시험 106 PASS | 4절에서 같은 원인을 독립으로 재현했고, 고친 트리에서 같은 시험 106 PASS도 직접 돌려 같다. |
| 수정 후 회귀 3/3 PASS, quick 44/44 PASS | 6.1절. 러너 요약(`summary.json`)을 직접 읽었다. |
| 세 러너 모두 `qa/` 보호 변경·삭제·추가 0 | **새로 확인**: `20261001_135223_custom`(FAIL 14/15), `20261001_150250_custom`, `20261001_152035_quick` 세 요약 모두 `guard`의 changed, removed, added가 비어 있다. |
| 네이티브 검토 이미지 87장, 1080p 검증 PASS, 커밋 완료 | **새로 확인**: 색인(`native_media_index.md`)의 87장이 모두 디스크에 있고 git에 추적되며, `validate_visual_evidence_1080p.py`를 직접 돌려 87장 모두 1920×1080 이상으로 디코딩된다(`codex_native_media_validation.json`). 컨테이너 해상도만 확인한 것이고 그림 승인이 아니다. |
| 보스방 바닥 510,410.5 px² / 1,481×660, 엄폐 0 | 제작 지시서 4.3절 표에 같은 값(510,411 / 1,481 × 660)을 넣었고, `R05_STACKS`의 엄폐 소품은 0이다. |
| 작전 9를 켜지 않았고 단계 E도 시작하지 않았다 | `data/story/site7_campaign.json`에서 작전 9, 10만 `"deployable": false`다. |
| Claude는 켜기 전에 최종 방 공정성과 사본 풀플레이를 확인 | 이 기록 5절(격자 8개)과 7절(5판)로 끝났다. 켠 뒤의 full 스위트와 자기 방 보스 캡처, 소리 영상은 "작전 9 켜라" 이후다. |
| 기존 오디오 import 오류와 ASTER 경고 | 오디오는 `sound/music/originals/fps_bgm_06_sniper_ridge.wav`다. 2026-09-24 커밋 `34344749`에서 들어온 파일이고 헤더가 MP3(`ff fb`)이며, 단계 D에서 `sound/`는 바뀌지 않았다(`git diff --stat 46d812de HEAD -- sound`가 비어 있다). ASTER `M7_RASTER_QUARANTINED` 줄은 내 정렬 시험 로그에도 있다. 이 경고들이 더 늘지 않았는지는 세지 않았다. |

