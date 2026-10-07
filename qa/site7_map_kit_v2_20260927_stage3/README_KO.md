# SITE-7 맵 키트 v2 · 단계 3 완료 기록

작전 MIS_CH01_03·04·05에 공유되는 방 8장과 통로 7장, 총 15장의 v2 원화를 제작하고 게임에 연결했다. 세 작전은 같은 판을 서로 다른 순서로 지나간다. 작전 4는 주 통로를 역방향으로 내려가며, 갈래 통로 2장은 세 작전 모두 비반전 descending 원화다. 사용하지 않는 방 문은 충돌이 있는 금속 폐쇄 벽체로 막았다.

## 원화와 게임 데이터

- ImageGen 호출 16회: 15장 채택, S3_C04 첫 시도 1장 거절. 거절 원화는 `art_src/environments/site7_v2/stage03/_quarantine/`에 보존했다.
- 각 판의 RAW와 MASTER는 바이트가 같고, GAME은 전체 판에 sRGB 노출 계수 한 번만 적용했다. 자르기·리사이즈·반전·부분 칠을 하지 않았다. 런타임 배율은 1.0이다. 세부 해시와 117개 검사는 [원본·범위 검증](scope_and_derivative_verification.json)에 있다.
- `site7_plate_floors.json`에 실제 바닥 윤곽과 문 앵커를 기록하고, 월드 배치·이음매 조명·무드 조명·보행 바닥·전투방 엄폐물을 재계산했다. 엄폐물 7개를 재정착한 뒤 재검사는 `SETTLE_DONE moved=0 DRY`였다. 변경 전후 좌표와 로그 해시는 [엄폐물 기록](cover_settle_summary.json)에 있다.
- 작전 1·2의 원화와 바닥·배치 데이터는 원본·범위 검증에서 변경 없음으로 확인했다. 기존 v1 원화 파일은 삭제하지 않았지만, 작전 1–5의 현재 런타임 판은 모두 v2다.

| 작전 | strict 판 | strict 이음매 | 감사 파일 |
|---|---:|---:|---|
| MIS_CH01_01 | 15/15 PASS | 14/14 PASS | [작전 1](plate_lighting_mission1.json) |
| MIS_CH01_02 | 15/15 PASS | 14/14 PASS | [작전 2](plate_lighting_mission2.json) |
| MIS_CH01_03 | 15/15 PASS | 14/14 PASS | [작전 3](plate_lighting_mission3.json) |
| MIS_CH01_04 | 15/15 PASS | 14/14 PASS | [작전 4](plate_lighting_mission4.json) |
| MIS_CH01_05 | 15/15 PASS | 14/14 PASS | [작전 5](plate_lighting_mission5.json) |

월드 배치·무드 조명 `--check`도 통과했고, 사용하지 않는 문은 작전마다 4개씩 충돌 벽체가 생성됨을 [게임 씬 검사](sealed_doors_check.json)로 확인했다.

## 회귀 및 게임 화면

- [quick 회귀](regression/quick_SUMMARY_KO.md): 34/34 PASS.
- [full 회귀](regression/full_SUMMARY_KO.md): 55/55 PASS. 보행 바닥 감사 1,235개, 통로 양방향 WASD 정렬 530개, 전투 공간 2,496개 항목과 작전 1–5 전체 플레이 경로를 포함한다. 작전 4·5에 원래 엄폐물이 각 12개인데 모든 작전에 13개 이상을 요구하던 캠페인 테스트를, 실제 원화 배치 데이터의 개수와 게임에 붙은 개수를 비교하도록 바로잡았다.
- 실제 Godot 게임 1920×1080 캡처 69장: 작전마다 통로 7장과 방 양쪽 시점 16장. 예: [작전 3 통로](game/MIS_CH01_03_C4.webp), [작전 4 방](game/MIS_CH01_04_R01_ENTRY_a.webp), [작전 5 방](game/MIS_CH01_05_R01_ENTRY_b.webp).
- 게임 보행 바닥 오버레이 48장, 동일 카메라 v1/v2 게임 캡처 9장, 월드 배치 미리보기 24장, 캡처를 크기 변경 없이 나란히 놓은 비교 3장. 예: [바닥 오버레이](walk_graph/03_00_ENV_S03_BREACH.webp), [작전 3 비교](compare/MIS_CH01_03_v1_v2_pair.webp).
- 총 153장 무손실 WebP는 PNG 원본과 디코딩 픽셀이 같다. [증거 매니페스트](evidence_manifest.json)와 [1080p 검사](resolution_validation.json)는 각각 153장과 153/153 PASS를 기록한다. 1080p 검사는 캡처 용기 크기와 디코딩 검증이며, 원화 자체를 1080p 원본이라고 주장하지 않는다.

게임 캡처는 실제 엔진에서 실행한 자동 검토 장면이며 사람의 직접 플레이 승인이나 성능 승인을 뜻하지 않는다. 캡처 스크립트는 [capture_scripts](capture_scripts/)에 있다.

작업 중 ImageGen 관리 폴더의 임시 사본 16개를 유지했다. 완료 검증 후 프로젝트에 보존된 원본·격리본과 해시가 같음을 확인하고 그 임시 중복 파일만 정리했다. 대상·해시는 [정리 명세](managed_staging_retirement.jsonl), 정리 후 원본 보존 결과는 [사후 검사](post_retirement_verification.json)에 있다. 프로젝트의 RAW, MASTER, GAME, 거절 원화와 작업 캡처 원본은 보존했다.
