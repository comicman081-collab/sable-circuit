# 항목 1 기준선 작전 9 봇 정지 조사

기록: 2026-10-03. 읽기 조사만 수행했다. 이 기록 하나 외 코드·시험·QA·기준선 프로젝트를 쓰지 않았고 Godot, 시험, 러너를 실행하지 않았다. 최종 러너 판정은 아직 관측하지 않은 상태다. root가 종료 결과를 뒤에 덧붙인다.

## 기준선과 출처

- 기준선 폴더: `.cache/diag/expansion_item1_20261003/baseline_project/`.
- 스냅샷 HEAD: `7dfe367eeb7e2b47738c9cb49eb41ad4b263fde3` (`baseline_head.txt`, `baseline_sources.json`). 항목 1 기능 구현 전 스냅샷이다.
- `baseline_sources.json`은 565개의 경로별 SHA-256을 담는다. 기록 파일 SHA-256: `e082174d73eb7db7ccea3a0765cdc6ad28e96b62d591f8d8c2302fedd9186e96`.
- root가 현재 런타임 스냅샷의 565개 SHA 불변을 검증했다고 통보했다. 이 읽기 조사에서 565개 전체를 다시 검증하거나 시험을 다시 실행하지 않았다.
- 조사 로그: `baseline_project/qa/regression_runs/20261003_103852_custom/logs/full_op_09.godot.log`.
- 조사 시험: `baseline_project/tests/smoke/site7_full_operation_smoke.gd`.
- 읽은 규칙: `AGENTS.md`의 작전 9 봇 기록·Expansion after operation 10, `docs/production/SITE7_EXPANSION_1_3_CODEX_ORDER_KO.md` 전체. 지시서 2절은 변경 전 기존 시험 실패를 멈춤 조건으로 정한다. 작전 9 WIPED/TIMEOUT은 알려진 허용 잡음이 아니다.

### 주요 기준선 소스 SHA-256

| 경로(기준선 폴더 아래) | 스냅샷 SHA-256 |
|---|---|
| `tests/smoke/site7_full_operation_smoke.gd` | `a58b199bf50307b4096a052e2f011e2cf5c4642d14fa8f57eccacbba81720aae` |
| `scripts/combat/cover_navigation.gd` | `cf73f545f4b7511e382c24c0ac73d83a335691d8869236a64a5b6c076e794960` |
| `scripts/missions/site7_battlefield.gd` | `d91d010dc559f5e7003eae95c118166322444d1c1bdde98a0f5e7dc9790d700b` |
| `scripts/missions/story_stage_01.gd` | `0ce95f81b47bfe754f4f09f75075852a24eaeb25914002788affe9cd51dc3eab` |
| `data/missions/MIS_CH01_09.json` | `b091917fced12c8bb8736769fc3d3849885048876a54203bf2992b2038d22f3f` |
| `data/visual/site7_environment_props.json` | `8bfdce268fba5f8d0f3713dd1cb72a47209a6bc7e4e3f406d1c536274c82f865` |
| `data/visual/site7_plate_floors.json` | `ba89d725546b202c8b4b4f897d8adf12d27c177ce8b7117d3a1ddfa207ad04ca` |

## 관측 사실

| 기준선 실행 | 관측 결과 |
|---|---|
| `20261003_100926_custom` | 작전 9 `PASS_TECHNICAL_PLAYTHROUGH`, EXTRACTED, 전체 경로, 양쪽 선택 방 회수, 25킬, 미션 경과 168.759060초, failures 빈 배열 |
| `20261003_102455_custom` | 작전 9 `PASS_TECHNICAL_PLAYTHROUGH`, EXTRACTED, 전체 경로, 양쪽 선택 방 회수, 25킬, 미션 경과 162.291398초, failures 빈 배열 |
| `20261003_103852_custom` | 3회차 실행 중 정지. 이 기록의 마지막 읽기는 tick26400. 최종 FAIL/PASS 로그는 아직 없음 |

3회차 흐름:

- tick5101에 step3(R04_GALLERY 전투)에서 step4로 진행했다. 당시 위치 `(-6102.2114,3791.4341)`, 체력 `44 / 120 / 73`, 적 없음, remaining=0, wave=1.
- tick5400부터 마지막 읽기 tick26400까지 위치는 정확히 `(-6100.857421875,3838.12670898438)`였다. 체력 `44 / 120 / 73`, ammo16, hostiles 빈 배열, remaining0, step4, wave1이 유지됐다.
- 전멸 결과가 아니며 적이나 증원 잔존으로 방 정리가 막힌 로그가 아니다. 체력이 모두 양수이므로 이 로그의 장시간 정지를 부활 대기로 해석할 근거도 없다.
- 기준선 `StoryStage01._on_story_enemy_defeated`는 마지막 웨이브 정리에서 `_clear_hazards()`, battlefield.release(), `_complete_step()`을 호출한다. 따라서 step4의 이 상태는 기준선 ARC_VENT를 정리한 뒤의 이동 구간이다.

## 시험 코드로 확인되는 이동 목표와 기술 상한

`site7_full_operation_smoke.gd:230–251`의 비전투 분기는 현재 본 경로 방보다 선택 방을 먼저 회수한다. 첫 선택 방 O01_BLADES의 부모는 R04_GALLERY(step3)다. step4에서 아직 첫 선택 방을 회수하지 않았다면 목적지는 O01_BLADES `(-3964.3,4646.3)`이며, 회수했더라도 부모 R04로 돌아오는 분기를 먼저 수행한다.

로그에는 선택 방 회수 여부와 실제 goal이 없다. 그러나 step4 전환부터 정지까지 약5초 미만이고, 정지점에서 O01 중심까지 약2,285px 떨어져 있어 첫 선택 방을 회수하러 향하는 상황으로 읽힌다. 이것은 코드와 로그에 따른 추정이며 런타임 goal 관측은 아니다.

- R04 중심: `(-6003.3,3512.8)`.
- 정지점은 그 중심에서 약 `(-97.6,+325.3)`이며 방 남쪽 바닥이다.
- R04 SE 문/분기 시작점: `(-5524.3,3697.3)`; 정지점에서 약594px.
- 다음 본 경로 R05_STACKS 중심: `(-8598.3,4511.3)`.
- 루프는 `range(36000)`이며 매 반복 physics_frame/process_frame을 기다린다. 기본60Hz에서 600초의 물리 프레임 상한이다. 36,000프레임 동안 stage_completed 결과가 없으면 `Route finishes within technical playthrough bound`가 실패하고 EXTRACTED·full_route·회수·킬 검사도 결과에 따라 실패한다.
- 현재 프로젝트 러너 등록의 `full_op_%02d` 외부 wall-clock timeout은900초다. 이 기록은 별도 러너를 실행하지 않았고 진행 중 실행의 종료 상태를 확정하지 않는다.

## 원인 후보 — 확정하지 않음

정지 좌표는 R04의 남쪽 barrier와 바닥 경계가 가까운 위치다. 기준선 데이터와 소스 수식에 대한 읽기 계산(런타임 재현 아님):

- barrier: normalized point `(0.48,0.76)`, width200. 1672×941 판과 기록된 중심에서 월드 중심 약 `(-6036.74,3757.46)`.
- prop 원화 spec의 ground_px에서 구한 ground box: x `[-6136.74,-5936.74]`, y `[3716.532,3798.388]`.
- NAV는 operator capsule14×36/offset(0,-18)에 여유3px를 더해 박스를 팽창한다. 해당 NAV 박스 하단은 y `3837.388`이고 정지점 y는 `3838.127`로 약0.739px 아래다.
- 같은 x에서 방 남쪽 직선 변의20px 바닥 inset 하단은 약 y `3840.287`이다. NAV 박스와 이 바닥 변 사이의 수직 여유는 약2.90px다.
- NAV의 CORNER_CLEARANCE=12를 더한 남쪽 박스 코너 두 개는 해당 방 바닥 변보다 약35.58/8.41px 밖이다. `_fixed_nodes`는 바닥 밖 노드를 버린다.

따라서 남쪽 좁은 바닥 주머니에서 NAV 박스가 길을 끊거나 실제 물리 접촉이 이동을 막았다는 가능성이 있다. 다만 기존 trace는 move 벡터, nav.direction 반환값, NAV._path, 실제 목표, 동료 좌표와 collision 결과를 기록하지 않는다. NAV가 ZERO를 돌려준 것인지, 미끄러짐/동료 접촉인지, 다른 경계 문제인지 **이 읽기 조사만으로 확정할 수 없다**. 기존 baseline의 두 회차는 통과했으므로 항상 재현되는 연결 단절이라고도 주장하지 않는다.

## 사용한 읽기 명령

- `Get-Content -LiteralPath <위 baseline 로그> -Tail 95` 및 이후 -Tail 2–10.
- `Get-Content -LiteralPath <baseline 시험/소스> | Select-Object -Skip ... -First ...`로 코드 흐름 확인.
- `rg -n`으로 stage step·goal·optional·NAV·ground·timeout 정의 검색.
- `Get-Content ... -Raw | ConvertFrom-Json`으로 월드 위치, 바닥, cover, 앞선 두 회차 `full_operation.json` 읽기.
- `Get-ChildItem -LiteralPath <cache/기준선 regression_runs>`로 기록 경로 확인.
- `Get-FileHash -LiteralPath <baseline_sources.json> -Algorithm SHA256` 및 JSON rows 개수 읽기(565).
- functions의 JavaScript에서 읽은 좌표·스펙 상수만 대입해 barrier 박스와 바닥 직선/inset 위치 계산. 파일 쓰기·게임 실행 없음.

## 판정 범위

현 시점 확인: 기준선 작전9 2회 PASS, 3회차 step4 이동 정지, tick26400까지 지속. **최종 FAIL는 아직 관측하지 않았다.** 상한에 도달해 FAIL/TIMEOUT으로 끝나면 지시서2절의 기존 시험 실패 멈춤 조건이며, 새 구현이 성공했다고 덮어쓰지 않는다. 추가 조사 실행이나 수정은 하지 않는다.

이 기록은 그림·플레이·균형 승인이 아니다.

## 종료 결과 — root가 추가

2026-10-03 러너는 `full_op_09`를 607초 후 FAIL로 기록했다. 기술 상한 36,000프레임에 도달했고 최종 trace는 tick35400에서도 동일 좌표다. WIPED 결과가 아니라 result 빈 객체이며 경로·추출·전체 방·선택 방·처치 수 검사가 실패했다. `baseline_stall_final.json`에 실제 failures·피해·tested SHA·마지막 trace와 원본 보고서 SHA를 보존했다. 지시서 2절에 따라 후속 러너·기능 작업은 시작하지 않는다.
