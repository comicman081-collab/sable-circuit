# SITE-7 맵 키트 v2 · 단계 4 검증 기록

작전 4와 5가 각각 전용 방 원화 8장씩 사용한다. 작전 3의 방 8장과 통로 7장은 그대로 두었고, 작전 4·5는 S3 통로 7장을 공유한다. 새 방은 각 작전의 실제 문만 그렸으며 런타임 배율은 1.0이다.

## 원화와 연결

- ImageGen 18회로 16장 채택. S4_R05와 S4_R06의 첫 후보는 거절하고 `art_src/environments/site7_v2/stage04/_quarantine/`에 보존했다. 최종 프롬프트, 참조 이미지, 시도 수, 원본 및 GAME 해시는 [원화 매니페스트](../../art_src/environments/site7_v2/SITE7_MAP_KIT_V2_MANIFEST.md)의 Stage 4 절에 있다.
- [파생본 검증](derivative_verification.json): 16/16 RAW·MASTER 바이트 동일, GAME은 원본 크기에서 판 전체 sRGB 노출·기록된 화이트밸런스만 적용. 자르기·리사이즈·반전·부분 칠 없음. [판별 계수와 해시](stage4_derivatives.json).
- `site7_plate_floors.json`에 새 바닥과 문 앵커를 넣고 월드 배치·이음매 조명·무드 조명을 재계산했다. 전투방 6개의 바닥·스폰을 새 판에 맞췄고 엄폐물 5개를 재정착했다. 최종 [건조 실행](cover_settle_dry.log)은 `SETTLE_DONE moved=0 DRY`이며 경고가 없다.
- 작전 5의 긴 보스방에서 자동 지원 로봇 스폰이 출구를 막던 문제를 해결했다. 지원 로봇 3기의 스폰을 접근 측에 지정하고, 긴 통로의 길찾기 경유점을 900px 그래프 연결 한도 안으로 나눴다. [변경 범위 검사](scope_check.json)상 작전 1–3의 기존 데이터 값은 그대로다.

| 작전 | strict 판 | strict 이음매 | 감사 |
|---|---:|---:|---|
| MIS_CH01_01 | 15/15 PASS | 14/14 PASS | [작전 1](plate_lighting_mission1.json) |
| MIS_CH01_02 | 15/15 PASS | 14/14 PASS | [작전 2](plate_lighting_mission2.json) |
| MIS_CH01_03 | 15/15 PASS | 14/14 PASS | [작전 3](plate_lighting_mission3.json) |
| MIS_CH01_04 | 15/15 PASS | 14/14 PASS | [작전 4](plate_lighting_mission4.json) |
| MIS_CH01_05 | 15/15 PASS | 14/14 PASS | [작전 5](plate_lighting_mission5.json) |

## 회귀 및 게임 화면

- [quick 회귀](regression/quick_SUMMARY_KO.md) 34/34 PASS, [full 회귀](regression/full_SUMMARY_KO.md) 55/55 PASS. full에는 [실제 이동 1,235개](regression/traversal_audit.json), 양방향 통로 정렬 530개, 전투 공간 2,496개, 작전 1–5 전체 플레이가 포함된다. 이후 로컬 커밋 `59c9959b8`이 공유 통로 조명 검사를 추가했고, 강화된 [전투 공간 재검사](regression/battle_geometry_after_59c9959b8.log)도 2,518개 PASS했다. 대상 작전의 [4 전체 플레이](regression/full_operation_m4.json)와 [5 전체 플레이](regression/full_operation_m5.json) 기록을 별도로 보존했다.
- 실제 Godot 게임의 1920×1080 캡처 110장: 작전마다 통로 7장과 방 양쪽 시점 16장(예: [작전 4 통로](game/MIS_CH01_04_C0.webp), [작전 4 보스방](game/MIS_CH01_04_R05_WARDEN_a.webp), [작전 5 보스방](game/MIS_CH01_05_R05_CARRIER_b.webp)), 보행 바닥 오버레이 16장([작전 5 보스방](walk_graph/05_04_ENV_S05_CARRIER.webp)), 전용 방과 S3 기준 방의 동일 카메라 비교 16쌍([새 S5 보스방](compare/MIS_CH01_05_R05_CARRIER_dedicated.webp), [S3 기준](compare/MIS_CH01_05_R05_CARRIER_S3_reference.webp)). 게임 화면 바닥의 방 이름과 화살표는 길 안내 코드 표시이며 원화 글자가 아니다.
- [증거 매니페스트](evidence_manifest.json)는 110장 각각의 원본 PNG 및 무손실 WebP 해시와 디코딩 픽셀 일치를 기록한다. [1080p 검사](resolution_validation.json)는 110/110 PASS다. 이 검사는 캡처 해상도와 디코딩을 보증하며 원화 자체의 1080p 원본성이나 사람의 플레이 승인을 뜻하지 않는다. 재현 스크립트는 [capture_scripts](capture_scripts/)에 있다.

검증이 끝난 뒤 ImageGen 관리 스테이징 중복본 18개만 [해시 기록](managed_staging_retirement.jsonl)에 따라 정리했다. [사후 검사](post_retirement_verification.json)는 프로젝트의 채택 원본·격리본이 보존됐음을 확인한다. S4_R05의 거절 시도는 격리본 외에 작업 폴더의 중복 사본도 남아 있다. 중복 사본 삭제 명령은 자동 승인 검토에서 정책상 차단됐으며, 런타임은 그 파일을 참조하지 않는다.
