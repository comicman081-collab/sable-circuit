# SITE-7 맵 키트 v2 — 단계 2, 작전 2 전체 교체

2026-09-27. 작전 `MIS_CH01_02`의 방 8장과 통로 7장을 승인된 파일럿·단계 1 원화를 기준으로 새로 제작해 교체했다. 작전 1, 3, 4, 5의 원화와 미션 데이터는 그대로 두었다. 이 단계에서 멈추며 단계 3은 진행하지 않는다.

## 게임 안 1080p 화면

- [R01 실제 게임 화면](hero/R01_game_1to1.webp), [v1/v2 동일 카메라·대원 위치 비교](R01_v1_v2_compare.webp)
- 통로 7장: [C01](game/MIS_CH01_02_C0.webp), [C02](game/MIS_CH01_02_C1.webp), [C03](game/MIS_CH01_02_C2.webp), [C04](game/MIS_CH01_02_C3.webp), [C05](game/MIS_CH01_02_C4.webp), [C06 ↘](game/MIS_CH01_02_C5.webp), [C07 ↘](game/MIS_CH01_02_C6.webp)
- 방 8장의 양쪽 카메라 시점 16장은 [`game/`](game/)에, 보행 바닥 오버레이 16장은 [`walk_graph/`](walk_graph/)에 보존했다. [작전 2 보행 조감](walk_graph/02_overview.webp), [월드 배치 조감](overview/MIS_CH01_02_overview.webp)을 함께 제공한다.

게임 캡처와 보행 오버레이는 Godot OpenGL Compatibility에서 네이티브 1920×1080으로 실행해 저장했다. `overview/` 8장은 배치 도구가 만든 합성 조감이며 게임 화면과 구별한다. 캡처 23장, 오버레이 16장, 동일 카메라 4장, 합성 8장과 나란히 비교한 1장으로 총 52장을 무손실 WebP로 보존했고 원본 PNG와 디코딩 픽셀이 같은지 확인했다. [캡처 출처·해시](evidence_manifest.json), [캡처 스크립트](capture_scripts/), [1080p 검사 결과](resolution_validation.json)를 남겼다. 원화 자체를 1920×1080으로 생성했다는 뜻은 아니다.

## 조명·이음매 검증

`audit_site7_plate_lighting.py --mission MIS_CH01_02 --strict`: **판 15/15 PASS, 이음매 14/14 PASS, FAIL 0**. 최대 이음매 밝기 차는 절댓값 **0.222 stop**으로 허용치 0.35 이내다. [작전 2 감사 JSON](plate_lighting_mission2.json)을 보존했다. 작전 1의 strict audit도 **판 15/15, 이음매 14/14 PASS**를 유지했다([회귀 JSON](plate_lighting_mission1_regression.json)). 이 수치는 런타임 이음매 보정 전 GAME 원화의 픽셀 검사다.

## 원화·게임 연결

내장 ImageGen으로 15장을 판별로 순차 생성하고 각 1회차를 선택했다. 거절 원화는 없으며, 작업 원본과 관리 스테이징 이미지는 삭제하지 않았다. [원화 매니페스트](../../art_src/environments/site7_v2/stage02/STAGE2_MANIFEST.md)에 프롬프트·참조·SHA-256·노출 계수와 기하 기록을 연결했다.

각 RAW와 MASTER는 바이트 동일하다. GAME에는 판 전체에 같은 sRGB 노출 계수만 한 번 적용하고, 자르기·리사이즈·반전·회전·부분 칠을 하지 않았다. 런타임 배율은 1.0, Godot import는 무손실·mipmap 비활성이다. `site7_plate_floors.json`에 실제 칠해진 바닥 윤곽과 문 앵커를 기록하고, 작전 2 전투방 바닥 R02·R04·R05를 원화에 맞췄다. 월드 배치를 다시 풀고 공식 엄폐 재정착을 실행해 작전 2의 엄폐 4개를 이동했다. 다른 작전의 엄폐는 바뀌지 않았다. ↗ 통로 5장은 `ascending`, ↘ 갈래 2장은 비반전 `descending`이다. 14개 연결부의 보행 바닥 간격은 모두 **0.0px**다([실행 로그](walk_graph.log)).

[원본·파생·범위 독립 검증](scope_and_derivative_verification.json)은 **97/97 PASS**다. 원본·관리 스테이징·MASTER 해시, GAME의 전역 노출 픽셀 계산, 원본 크기와 RGB, import 설정, 포인터·문·데크, 작전 1·3·4·5의 데이터 불변을 검사했다. 기존 v1 원화는 삭제하지 않았다.

## 회귀 검사

`python tools/maintenance/run_regression_suite.py`로 [quick](regression/quick_SUMMARY_KO.md) **34/34 PASS**와 [full](regression/full_SUMMARY_KO.md) **55/55 PASS**를 확인했다. full에는 작전 1–5의 실제 풀플레이, 양방향 통로 정합성 390개, 전투방 기하 2,371개, 보행 감사 1,253개, Motion Studio Python/JS 검사가 포함된다. quick의 최종 실행은 기존 QA 기록 변경·삭제·추가 없이 보호 게이트도 PASS했다.

게임 캡처 원본 PNG와 작업 중간 파일은 프로젝트의 git-ignored `.cache/`에 남겨 두었다. 생성된 이미지와 관리 스테이징도 작업 중 삭제하지 않았다. GitHub 작업 없이 로컬 커밋만 한다. **단계 2에서 멈춘다.**
