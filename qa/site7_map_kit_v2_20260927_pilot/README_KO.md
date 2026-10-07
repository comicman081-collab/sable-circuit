# SITE-7 맵 키트 v2 — 단계 0 파일럿 결과

2026-09-27. 대상은 **S1_R02 / S1_C01 / S1_C06 세 장**이다. 게임 연결과 기술 검증을 완료했다. 단계 1 작업은 하지 않았다. 최초 3회 시도 후 HOLD 기록은 별도 이전 폴더에 그대로 보존하고, 사용자의 계속 진행 지시 이후 결과를 여기에 기록한다.

## 게임 화면

- [실제 전투 장면, native 1920×1080, 카메라 1:1](hero/R02_game_1to1.webp)
- [v1 / v2 동일 방·동일 카메라 비교](R02_v1_v2_compare.webp): 1920×1080 두 장을 확대 없이 나란히 배치.
- [새 오르막 C01](game/MIS_CH01_01_C0.webp), [새 내리막 C06](game/MIS_CH01_01_C5.webp)
- [전체 조감](overview/MIS_CH01_01_overview.webp), [R02 바닥·엄폐·스폰 오버레이](walk_graph/01_01_ENV_S01_DECON.webp)
- game/ 통로 7장 + 방 16장, hero/ 4장, walk_graph/ 16장, overview/ 8장, 비교 1장: 총 52장 무손실 WebP.

Godot StoryStage01을 실제 네이티브 렌더러에서 실행했다. 전투 프리뷰를 12프레임 진행하고 고정한 장면이며 사람의 플레이 승인을 뜻하지 않는다. game/은 기존 1280×720 논리 화면을 1920×1080으로 렌더링한다. 큰 새 통로는 양끝이 화면에 들어오도록 캡처 카메라만 축소했다. hero/는 1920×1080 논리 화면, 카메라 1.0으로 원화 1픽셀 = 화면 1픽셀이다. 이미지 파일 자체를 확대해 해상도를 꾸미지 않았다. overview/는 풀이 도구의 합성 조감이며 게임 캡처와 구별한다.

## audit_site7_plate_lighting.py

명령: `python tools/environment/audit_site7_plate_lighting.py --mission MIS_CH01_01 --out .cache/site7_v2_pilot/audit_integrated.json`

| 판 | 평균 휘도 | p10 | p90 | 채도 | 축 | 파일럿 판정 |
|---|---:|---:|---:|---:|---:|---|
| S1_R02_GAME | 0.212 | 0.175 | 0.246 | 0.010 | 26.1° | PASS |
| S1_C01_GAME | 0.210 | 0.163 | 0.245 | 0.010 | 27.2° | PASS |
| S1_C06_GAME | 0.209 | 0.162 | 0.245 | 0.004 | 28.8° | PASS |

새 C01 ↔ 새 R02 이음매: **-0.114 stop**, 기준 ±0.35 이내, 채도·색조 검사도 PASS.

전체 작전 출력은 **SITE7_PLATE_LIGHTING FAIL (21 plates/seams off target)** 이다. 남아 있는 v1 판과 v1이 포함된 이음매 때문에 전체 PASS라고 보고하지 않는다. 단계 0 지시대로 `--strict`를 쓰지 않았으며, 종료 코드 0을 전체 판정 PASS로 해석하지 않았다. 전체 [audit JSON](audit_integrated.json)과 [파일럿 범위 판정](pilot_audit_scope.json)을 함께 보존한다.

| 파일럿에 닿는 이음매 (C0=C01, C1=기존 C02, C5=C06) | 밝기 차(stop) | 데크/방 채도 | 원화 기준 결과 |
|---|---:|---:|---|
| C0 → R01_ENTRY | -0.292 | 0.050 / 0.229 | saturation 0.05 vs 0.23 |
| C0 → R02_CORRIDOR | -0.114 | 0.102 / 0.018 | PASS |
| C1 → R02_CORRIDOR | -0.764 | 0.629 / 0.010 | brightness step -0.76 stops; saturation 0.63 vs 0.01 |
| C5 → R03_ARCHIVE | -0.143 | 0.018 / 0.148 | PASS |
| C5 → O01_SUPPLY | -0.386 | 0.009 / 0.320 | brightness step -0.39 stops; saturation 0.01 vs 0.32 |

새 판의 수치는 GAME 원화에서 잰 값으로 런타임 이음매 조명 적용 전이다. 기존 C02의 푸른 문틀과 색 번짐, C06 끝의 기존 보급방 색 차이는 v1 교체 전까지 남는 참고 항목이다.

## 기하와 원본

- R02: 바닥 바운딩박스 1277×627px, 캔버스 면적의 30.4%. SW 문 315px / NE 문 295px. 문 중심 정렬 허용 오차 0.5px.
- C01: 데크 수직 폭 278.4–279.3px, 축 27.2°. C06: 양끝 모두 291.1px, 축 28.8°. C06은 새 ↘ 원화이며 반전 없음.
- 끝 페이드 안쪽의 명목 중심선 길이는 C01 약 1261px(끝 10%), C06 약 1216px(끝 7.5%). 실제로 보이는 길이는 이웃 방과 겹치는 정도에도 영향을 받는다.
- 새 판 scale 1.0, 대원 크기 유지. R02 엄폐 캐비닛 한 개를 공식 재정착 도구가 33.4px 이동했다. 최종 재정착 실행은 추가 이동 0개였다.
- R02 NE 문 앞 바닥은 문틀에 일부 가려져 보이는 길이가 설계 목표 195px보다 짧다. 이 항목을 수치 검사의 PASS로 미술 승인 처리하지 않는다.
- 최종 선택은 R02 9번째 / C01 4번째 / C06 7번째. 이전 후보 원본은 모두 보존했다. 사용자 보존 지시 이후 작업·스테이징 이미지를 삭제하지 않았으며, C06 5번째의 기존 GAME과 원본·수치도 격리 보존했다.
- ImageGen 반환 원본: R02 1672×941, C01 1402×1122, C06 1254×1254. 1920×1080로 생성된 마스터라는 주장은 하지 않는다. 선택된 RAW와 MASTER는 바이트 동일, 크롭·리사이즈·부분 칠·미러·회전 없음.
- GAME만 전체 RGB에 동일한 1회 노출 계수를 적용: R02 0.79 / C01 0.86 / C06 0.82. 화이트밸런스 변경 없음. `.import`는 compress/mode=0, mipmaps/generate=false.
- 상세 프롬프트·참조·시도·SHA-256: [원본 매니페스트](../../art_src/environments/site7_v2/SITE7_MAP_KIT_V2_MANIFEST.md), [파생 검증](scope_and_derivative_verification.json).

## 코드와 검증

`deck` 값을 읽어 새 ↘ 원화를 비반전으로 배치한다. 교체하지 않은 v1 갈래만 기존 반전을 유지한다. `doors` 중심에 통로 끝을 맞추고, 실제 방 Sprite 변환으로 문 중심을 독립 계산하여 정렬을 검사한다. 바닥 경계와 R02 전투 배치를 새 원화에 맞췄으며, 나머지 작전 2–5 데이터는 동일하다. 기존 WASD 양방향 횡단·벽 충돌·엄폐 경로 검사를 유지한다.

최종 세 장이 적용된 상태에서 지정된 회귀 러너로 실행했다.

- quick **33/33 PASS**: `qa/regression_runs/20260927_113809_quick` ([요약](regression/quick_SUMMARY_KO.md))
- full **54/54 PASS**: `qa/regression_runs/20260927_113925_full` ([요약](regression/full_SUMMARY_KO.md))
- 두 실행 모두 기존 QA 파일 변경·삭제·추가 **0개**. full에는 작전 5개 풀플레이, 적 엄폐 이동, 문 정렬 326개, 바닥 기하 2134개, Python/JS Motion Studio 검사가 포함된다.
- [원본·파생·범위 검사](scope_and_derivative_verification.json): 36개 PASS. RAW/MASTER/GAME 해시, 허용된 전역 보정, 교체 포인터 3개와 작전 2–5 불변을 검사했다.
- [1080p 검사](resolution_validation.json): `--require-dynamic-capture`; 해상도·디코딩 컨테이너 판정이며 화질 승인과 별개다.

캡처 스크립트와 원본 PNG/무손실 WebP 해시는 capture_scripts/ 및 evidence_manifest.json에 있다. 테스트 출력은 러너 전용 폴더, 캡처 중간 파일은 프로젝트 .cache/에만 썼다. 기존 날짜별 QA 기록은 덮어쓰지 않았다. 로컬 커밋만 하며 push·PR·배포는 수행하지 않는다. **사용자 검토를 위해 단계 0에서 멈춘다.**
