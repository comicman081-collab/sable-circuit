# SITE-7 맵 키트 v2 — 단계 1, 작전 1 전체 교체

2026-09-27. 사용자의 후속 지시에 따라 파일럿 3장을 기준으로 작전 `MIS_CH01_01`의 남은 v1 판 12장을 새 원화로 교체했다. 작전 1은 방 8장·통로 7장 모두 v2이며, 이 단계에서 멈춘다. 작전 2–5의 원화와 데이터는 바꾸지 않았다.

## 게임 안 1080p 화면

- [R01 실제 게임 장면, 카메라 1:1](hero/R01_game_1to1.webp)
- [R01 v1/v2 동일 카메라·동일 대원 위치 비교](R01_v1_v2_compare.webp): 각각 네이티브 1920×1080 게임 프레임을 확대 없이 나란히 배치했다. v1 게임 배율 0.88, v2 1.0이다.
- [R03↔R04 연결](game/MIS_CH01_01_C2.webp), [R04↔R05 연결](game/MIS_CH01_01_C3.webp), [R04↘O02 갈래](game/MIS_CH01_01_C6.webp)
- [실제 게임 보행 바닥 오버레이](walk_graph/01_03_ENV_S01_CONTAINMENT.webp), [월드 배치 조감](overview/MIS_CH01_01_overview.webp)

`game/`은 통로 7장과 방 양쪽 시점 16장, `walk_graph/`는 16장, `hero/`는 같은 카메라 증빙 4장이다. `overview/` 8장은 배치 풀이 도구의 합성 조감이므로 게임 캡처와 구별한다. 비교 1장을 포함한 52장 모두 무손실 WebP이며 원본 PNG와 디코딩 픽셀 일치를 확인했다. [증빙 해시와 출처](evidence_manifest.json), [캡처 스크립트](capture_scripts/), [1080p 검사](resolution_validation.json)를 보존한다. 네이티브 Godot OpenGL Compatibility에서 `StoryStage01` 전투 프리뷰를 실행해 캡처했으며 사람의 플레이나 미술 승인을 의미하지 않는다. 원화 자체를 1920×1080로 생성했다고 주장하지 않는다.

## 전체 조명 audit

`audit_site7_plate_lighting.py --mission MIS_CH01_01 --strict` 결과: **판 15/15 PASS, 이음매 14/14 PASS, FAIL 0건**. 파일럿 때 남아 있던 v1 판·이음매 FAIL 21건을 작전 1에서 해소했다. 최대 이음매 밝기 차는 절댓값 **0.181 stop**으로 기준 0.35 이내다. 판 평균 휘도는 0.209–0.212, 바닥 축은 23.1–28.8°다. 이 수치는 GAME 원화 픽셀의 런타임 이음매 조명 보정 전 측정이다. 전체 [strict audit JSON](audit_strict.json)을 보존한다. 작전 2–5의 v1 문제까지 해결했다는 뜻은 아니다.

## 원화·연결

새 방 7장과 통로 5장은 내장 ImageGen으로 순차 생성했다. R01 2회 중 1회차, O01 2회 중 2회차를 선택했고 나머지 10장은 1회차를 선택했다. 거절 2장은 원본 작업 파일을 남기고 `_quarantine/`에 해시와 사유를 기록해 복사했다. 전체 프롬프트 전문·참조 이미지·SHA-256·시도 기록은 [원본 매니페스트](../../art_src/environments/site7_v2/SITE7_MAP_KIT_V2_MANIFEST.md)와 [14회 생성 로그](../../art_src/environments/site7_v2/stage01/stage1_generation_log.json)에 있다.

선택 RAW와 MASTER는 바이트 동일하고 크롭·리사이즈·회전·미러·부분 칠을 하지 않았다. GAME에는 판 전체에 동일한 sRGB 노출 계수만 한 번 적용했다. 런타임 배율은 모든 판 1.0, Godot import는 무손실·mipmap 비활성이다. 실제 칠해진 바닥 윤곽과 문 앵커를 `site7_plate_floors.json`에 기록하고 새 R04·R05 전투방 바닥을 원화에 맞췄다. 공식 엄폐 재정착은 추가 이동 **0개**였다. ↗ 통로는 `ascending`, ↘ 갈래는 비반전 `descending` 원화를 쓴다. 14개 연결부의 보행 바닥 간격 측정은 모두 **0.0px**이다([오버레이 실행 로그](walk_graph.log)).

[원본·파생·범위 독립 검증](scope_and_derivative_verification.json): **70/70 PASS**. 12개 판의 RAW/MASTER/GAME 해시, 전역 노출 픽셀 계산, 네이티브 크기와 RGB, import 설정, 작전 1의 15개 v2 포인터·문·데크, 작전 2–5의 데이터 불변을 확인했다. 기존 v1 원화 파일은 삭제하지 않았다.

## 게임 회귀

지정된 `run_regression_suite.py`로 최종 원화·데이터 상태를 검증했다.

- [quick](regression/quick_SUMMARY_KO.md): **33/33 PASS**.
- [full](regression/full_SUMMARY_KO.md): **54/54 PASS**. 작전 5개 풀플레이 모두 첫 실행에서 PASS. 통로 정합성 355개, 전투방 기하 2,134개, 보행/연결 감사 1,253개, 적 엄폐 이동, Motion Studio Python/JS 검사를 포함한다.

테스트 러너는 기존 `qa/` 및 `motion_lab_v1/qa/` 기록의 변경·삭제·추가를 감시했고 두 실행 모두 PASS했다. 게임 캡처 PNG와 작업 중간 파일은 프로젝트의 git-ignored `.cache/`에 남겨 두었다. 사용자 지시에 따라 생성 직후 작업 이미지를 지우지 않았고, 거절 원화는 격리 보존했다. GitHub push·PR·배포 없이 로컬 커밋만 한다. **단계 1에서 멈춘다.**
