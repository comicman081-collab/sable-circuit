# 벽 충돌 · 적 등장 · 진행 막힘 점검과 수리 — 2026-09-24

사용자 요청: 커밋 전에 벽 충돌, 몹이 안 나오는 문제, 맵이 막혀 진행이 안 되는 문제,
가야 할 길에 벽이 있거나 벽을 통과하던 문제가 해결됐는지 확인하고, 안 됐으면 해결.

## 수정 전 상태 (Codex 2026-09-23 코드·데이터)
- 5개 작전 전체 플레이 봇: 모두 EXTRACTED. 적 전원 등장·처치, 진행·탈출 정상.
- 새 통과 감사 테스트 기준 12건 실패: 5작전 보스방 발전기 엄폐물이 바닥 밖,
  2·4·5작전 R04 복도 분대 스폰이 방벽과 겹침, 1작전 R04→R05 경로 계산 실패.
- 적 엄폐 경로 회귀(Codex 테스트, 5개 작전으로 확장): 2작전 R04 CINDER가
  공격 위치를 못 찾고 10초 이상 정지 (9/23 엄폐물 이동 이후 발생).
- 벽 통과: 비전투 방 8종·통로 21종이 도색과 무관한 공용 사각형 바닥을 썼고,
  방 중심에서 뻗은 폭 200px 경로 띠가 판 사이 기계·벽 위를 가로질렀음.
  30개 엄폐물 중 18개가 난간 위(바닥 밖)에 걸쳐 배치돼 있었음.

## 수정
- `data/visual/site7_plate_floors.json`: 비전투 방·통로 배경 36장의 실제 도색
  바닥 윤곽(정규화 좌표). 전투방 9종은 Codex가 검증한 레이아웃 바닥 유지.
- `scripts/missions/site7_battlefield.gd`
  - 배경별 추적 바닥 사용, 전투방은 기존 방 중심 경로(반폭 100px) 유지,
    비전투 방·통로 사이는 반폭 48px 연결만 사용.
  - 통로 이미지 경계의 수직 절단면에 막히지 않도록 통로 끝과 방 바닥을 잇는
    깔때기형 연결 바닥 추가(사용자 보고 "오른쪽 누르면 문턱에 걸림" 유형).
  - 오목한 바닥의 안쪽 모서리를 경로 탐색 경유점으로 추가.
  - 경계 보정을 가장자리 법선 방향으로 수정(오목 바닥에서 밖으로 튀던 문제).
- `scripts/combat/cover_navigation.gd`: 고정 경유점 사이 가시성 캐시.
  경로 계산 첫 회 평균 7→약 12ms, 반복 계산 최대 약 3~4ms(기존 매번 7ms).
- `data/visual/site7_environment_props.json`: 엄폐물 35개 위치 조정(크기 동일).
  `tools/environment/settle_cover_on_floor.gd`가 실제 경로 계산기로
  (1) 발판 전체가 바닥 위, (2) 목표 지점·분대/적 스폰(적 몸체로 부풀린 사각형
  기준)과 비겹침, (3) 방을 지나는 모든 경로가 여전히 계산됨을 만족하는 가장
  가까운 위치를 선택. 실행 기록: `cover_settle.log`.
- 테스트
  - 신규 `tests/smoke/site7_traversal_audit_smoke.gd`(5개 작전, 955 검사).
  - 신규 `tests/render/site7_walk_graph_capture.gd`(1080p 바닥 오버레이).
  - `tests/render/enemy_cover_navigation_regression.gd`: 1~3 → 1~5작전.
  - `tests/smoke/site7_entry_direct_input_probe.gd`: 얼린 적의 충돌을 끔
    (연결부 테스트와 같은 처리. 막힌 대상이 벽이 아니라 얼린 BULWARK였음).

## 검증 결과 (최종 데이터, 재부팅 후 재실행 포함)
| 테스트 | 결과 |
|---|---|
| site7_traversal_audit_smoke (신규, 5개 작전) | PASS 955 / 0 |
| enemy_cover_navigation_regression (1~5작전으로 확장) | PASS (수정 전 2작전 R04 CINDER 정지) |
| site7_connector_alignment_smoke (D키·WASD 문턱 통과) | PASS |
| site7_entry_direct_input_probe (사용자 보고 D키 막힘) | PASS, x=5393 |
| site7_world_route_navigation_smoke | PASS 49 |
| site7_branch_navigation_regression | PASS |
| site7_battle_geometry_smoke | PASS 4133 |
| site7_live_entry_autostart_smoke | PASS |
| cover_navigation_smoke / site7_player_cover_collision_smoke | PASS 15 / PASS 5 |
| site7_cover_ai_check | PASS_TECHNICAL_ONLY 46 |
| site7_campaign_progression_smoke / site7_battle_flow_smoke | PASS 94 / PASS |
| site7_full_operation_smoke 1~5작전 (실제 물리·쿨다운·치트 없음) | 5개 모두 PASS, EXTRACTED |

- 3작전 입구 방벽은 캠페인 분대 대형(입구 중심±오프셋)과 겹쳐 추가 이동
  (`cover_settle.log` 마지막 줄). 이후 감사·연결부·3작전 전체 플레이 재확인 PASS.
- 1080p 바닥 오버레이 80장: `walk_graph/`. 개요 5장은
  `walk_graph_visual_evidence_check.json` 컨테이너 PASS(아트 승인 아님).

## 남은 한계
- 바닥 윤곽은 눈으로 추적한 근사치. 판 이음새의 검은 공간·일부 가장자리는
  오버레이로 확인 가능하며 사람 플레이테스트는 아님.
- 전투방 9종(Codex 레이아웃)은 기존 방 중심 경로 폭을 그대로 써서, 이 방들의
  벽 근처 통과 여부는 이번에 바꾸지 않음.
- 적 경로 계산 첫 회 비용은 평균 약 12ms로 늘었음(반복은 캐시로 3~4ms).
