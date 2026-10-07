# 작전 8 Stage C — A1/A2 마무리 (2026-09-30)

Claude의 [작전 8 켜기 전 검증](../../../site7_op8_preenable_20260930/README_KO.md)을 읽고 남은 두 항목을 처리했다. 작전 8은 **출격 보류**다. 이번 작업의 ImageGen 호출은 **0회**이며, 15장 원화의 채택·거절 이력은 그대로다.

## A1. S8_O02 GAME 노출

`intake_one.py`와 같은 전체 이미지 단일 sRGB LUT를 사용했다. 각 RGB 채널에 `min(255, round(v × factor))`만 적용한다. 원화 크기 1672×941, source/game scale 1.0이다. 색조·채도·부분 보정·바닥 추적 변경은 없다.

| 항목 | 이전 | 현재 |
|---|---:|---:|
| 노출 계수 | 0.5396 | 0.5831 |
| 실제 등록 바닥 평균 휘도 | 0.166355103 | 0.179828927 |
| p10 | 0.102686271 | 0.110976472 |
| p90 | 0.222509816 | 0.240666673 |
| 바닥 채도 | 0.072310612 | 0.072475794 |

- 이전 GAME SHA-256: `0d5f1e24c79830668ecd05ed068e3eda6758256dbc637fc6937197a91bdc1b78`.
- 현재 GAME SHA-256: `d5cda0850278044cd06108a08d6f030a309b0af888a4e3fe5669c0ac4ce6567e`.
- RAW=MASTER SHA-256: `95999fdb6d60fa3e030834b340bd85b25761a863a80f9d57a0f7d0293b7116aa`. 두 파일 바이트는 불변이다. 이전 계수로 이전 GAME 픽셀이 재현되는 것도 확인했다.
- 이전 GAME은 `art_src/environments/site7_v2/_quarantine/S8_O02/game_exposure_20260930_before/`에 그대로 보존했다. [노출·전체 해시·실제 감사값](o02_exposure.json), [현재 45파일 검사](../source_integrity.json), [파생 이력이 포함된 호출 기록](../generation.json).
- LUT 계수 탐색에는 float64 히스토그램 추정값을 사용했다. 표는 실제 float32 감사값이며, 추정값과의 작은 차이도 JSON에 구분했다.

## A2. 새벽 배경 접촉 그림자 — 후보 2 채택

밝은 구름이 판의 경계에 닿는 부분만 어둡게 한다. 기존 허공 마스크의 실루엣에서 거리장을 계산하고 새벽 배경 셰이더가 이를 읽는다. 판의 알파·벽 홈·얇은 외곽선을 보존할 수 있어서 후보 2를 골랐다. 문턱을 높이지 않았고 `VOID_MAX=12`, 작전 8의 shadows/contrast와 판 셰이더는 그대로다.

- 작전 8 abyss에만 `contact_shadow_px=24`, `contact_shadow_strength=0.88`을 추가했다. 72 px 패딩, 원본의 1/4 해상도 거리장 15개를 `site7_contact_shadows.json`에 저장한다. 이는 원화 수정이나 생성 판이 아닌 코드 계산용 스칼라 데이터다.
- 런타임은 1928×1408 L8 아틀라스 하나를 한 번 만든다. 기존 심연 쿼드 하나에서 배경 색을 기저 색 쪽으로 낮춘다. 웹 안개 2옥타브 / 데스크톱 4옥타브는 그대로다. 로봇·작전자·엘리트·소품의 재질이나 색은 변경하지 않았다.
- 후보 1의 알파 페더 진단은 어두운 벽 홈까지 배경이 비쳐 **거절**했다. 런타임에는 페더 코드·설정이 남지 않으며 [거절 캡처](rejected_feather/)와 프로젝트 PNG 작업본을 보존했다.
- [작전 1–7 행 보존](preservation.json): 허공 마스크 105행과 램프 105행이 원래 JSON 행의 바이트 그대로다. 현재 마스크·램프 변경은 A1의 S8_O02 한 행뿐이다. 기존 작전 무드와 출격 관련 파일도 보존했다.
- [접촉 그림자 설정·이유](contact_shadow.json), [캡처 위치·해시](capture_comparison.json).

## 같은 1080p 카메라의 전후

실제 게임의 판·무드·심연을 native 1920×1080으로 렌더했다. 캡처 전용 복제 재질에서만 TIME=1.0을 고정하여 배경의 시간 변화가 대조에 섞이지 않게 했다. 같은 여섯 카메라, zoom=1.22, 게임 source/game scale=1.0, viewport canvas scale=1.5다. HUD와 배우를 숨긴 **그림 프리뷰**이며 플레이 캡처나 사람 승인이 아니다. 원본 PNG는 `.cache/diag/site7_ops_c_finish_20260930/`에 남고 QA WEBP는 픽셀이 동일한 lossless 변환이다.

| 위치 | 전후 1:1 픽셀 비교 | 전체 이전 | 전체 현재 |
|---|---|---|---|
| S8_R01 | [비교](comparison/S8_R01_before_after_native_1080p.webp) | [이전](before/S8_R01_native_1080p.webp) | [현재](after/S8_R01_native_1080p.webp) |
| S8_R05 | [비교](comparison/S8_R05_before_after_native_1080p.webp) | [이전](before/S8_R05_native_1080p.webp) | [현재](after/S8_R05_native_1080p.webp) |
| S8_O02 | [비교](comparison/S8_O02_before_after_native_1080p.webp) | [이전](before/S8_O02_native_1080p.webp) | [현재](after/S8_O02_native_1080p.webp) |
| S8_C03 | [비교](comparison/S8_C03_before_after_native_1080p.webp) | [이전](before/S8_C03_native_1080p.webp) | [현재](after/S8_C03_native_1080p.webp) |
| S8_C05 | [비교](comparison/S8_C05_before_after_native_1080p.webp) | [이전](before/S8_C05_native_1080p.webp) | [현재](after/S8_C05_native_1080p.webp) |
| S8_C06 | [비교](comparison/S8_C06_before_after_native_1080p.webp) | [이전](before/S8_C06_native_1080p.webp) | [현재](after/S8_C06_native_1080p.webp) |

C05의 수평 배관 사이와 기둥 바깥에 있던 거친 회색 띠가 접촉 그림자 안으로 정리된다. 다른 다섯 곳에서도 벽 외곽선과 난간이 유지되는지 확인했다. 비교 시트는 같은 화면 띠를 1:1로 잘라 위/아래에 놓았으며 확대·축소하지 않았다. O02의 전후는 A1 밝기 변경도 포함한다.

## 검증

| 항목 | 결과 |
|---|---|
| [strict 감사](strict_audit.json) | **PASS: 판 15/15, 이음부 14/14; 그중 3이음부 승인 예외 적용** |
| [월드 재생성](layout_build.log), [월드 --check](world_layout.log) | PASS, 8개 작전 |
| [무드 재생성](mood_build_final.log), [무드 --check](mood_light.log) | PASS, 120판·620풀·120허공 마스크·15접촉 거리장 |
| [접촉장 PNG 디코드 비교 대조](mood_contact.log) | PASS, 5대조 |
| [전투 지형](battle_geometry.log) | PASS, 4,038 검사 (Claude가 접촉 아틀라스 정합성 대조 추가) |
| [문턱 양방향 실제 WASD 횡단](connector_alignment.log) | PASS, 848 검사 (작전 1–8) |
| [1080p 컨테이너·디코드](visual_evidence_1080p.json) | PASS, 전후 12장·비교 6장·거절 진단 6장; 그림 품질 승인 아님 |
| [원화·기존 작전 행·출격 파일 보존](preservation.json) | PASS |

러너 실행 전 Python 프로세스 목록에 기존 러너가 없는 것을 확인했다. 등록된 네 검증을 **한 번** 실행했다:

`python tools/maintenance/run_regression_suite.py --only world_layout,mood_light,battle_geometry,connector_alignment`

첫 실행은 **3/4 PASS, 전체 FAIL**이다. 문턱 횡단이 900초 wall deadline에 걸렸다. 작전 1–6 완료 로그는 실패 0이며, 작전 7을 진행하던 중 중단됐다. [원래 요약](regression_initial_SUMMARY_KO.md), [원래 JSON](regression_initial_summary.json), [TIMEOUT 로그](connector_alignment_initial_timeout.log)를 보존했다. 이 결과를 PASS로 바꾸지 않았다.

문턱 검사만 호출 래퍼로 재실행한 18:28 실행은 작전 5까지 로그만 남기고 종료됐으며 요약이 없다([중단 기록](incomplete_retry.json)). 완료 PASS로 계산하지 않았다.

재개 시 공유 트리에 Claude의 접촉장 정합성 시험, 무드 PNG 비교 시험, 러너 시간 예산 1800초 변경이 들어와 있었다. 래퍼 없이 정식 러너를 그대로 실행하여 등록된 `world_layout,mood_light,mood_contact,battle_geometry,connector_alignment` **5검증을 백그라운드 러너에서 확인해 5/5 PASS**를 얻었다. 문턱 시험 스크립트·assertion·물리 설정·임무 선택은 바꾸지 않았고 동일한 작전 1–8 전체 WASD 검사 **848/848 PASS**다. 사용자는 Claude 소유 네 경로도 검증된 내용 그대로 포함해 커밋하도록 허용했다. `tests/smoke/site7_battle_geometry_smoke.gd`, `tests/test_site7_mood_contact_compare.py`, `tools/maintenance/run_regression_suite.py`와 공유 무드 빌더의 Claude 변경을 그대로 포함했다. full_op_08 등록은 없다.

같이 편집한 무드 빌더의 `same_contacts`는 Claude가 추가한 비교를 보존했다. PNG 압축 바이트 대신 디코드한 픽셀을 비교하고 1단계 반올림 차이는 허용하되 2단계·판 누락·패딩·스케일·크기·schema 차이는 거절하는 대조가 통과했다. 판 밝기·바닥 축·이음부 감사 기준의 변경이 아니다.

최종 러너 요약: `qa/regression_runs/20260930_191825_custom/SUMMARY_KO.md` ([복사본](regression_SUMMARY_KO.md), [JSON](regression_summary.json)). 최초와 최종의 완료 러너 모두 QA 보호 변경·삭제·추가 **0건**이다. 실행 중에는 기존 QA를 쓰지 않았고 종료 후 프로세스 목록을 확인하고 기록을 옮겼다([반입 확인](qa_transfer_guard.json)). 이번 수정 후 quick/full 전체 스위트를 반복하지 않았다. Stage C 최초 full의 실패와 수정 후 통과 기록은 역사 기록에 그대로 남는다.

### 이음부 예외의 출처

사용자 승인에 따라 Claude 커밋 `2d7a51a9`가 세 이름 지정 예외를 추가했다. 이 작업에서는 감사 도구·러너·예외 시험을 수정하지 않았다. C01/R01 채도비 1.95, C03/R04 2.1, C05/R05 1.9와 밝기 0.40 stops의 상한을 사용하고, 실행 시점 이음부 보정 후에는 원래 목표(채도비 1.5, 밝기 0.35 stops)를 만족해야 한다. 현재 보정 후 채도비는 약 1.41 / 1.28 / 1.27, 밝기 차는 +0.04 / −0.00 / −0.01 stops다. 원화 자체가 원래 세 이음부 목표를 모두 만족한다는 뜻은 아니다. [엄격 감사 로그](strict_audit.log).

## 멈추는 지점

작전 8 켜기, staging 제거, deployable/pending 변경, 작전 7 COMMAND 디브리프, full_op_08 등록은 하지 않았다. 작전 9·10과 보스 코드·패턴도 건드리지 않았다.

보스방의 실제 걷는 바닥은 이전과 같은 약 1467.90×569.88 px, 면적 522,646 px², 엄폐물 0개다. [기하](../boss_room_geometry.json)와 [실루엣 합성](../S8_R05_gantry_silhouette_review_1920x1080.webp)은 그대로이며 합성은 플레이 캡처가 아니다. Claude의 독립 검사에서 GANTRY 1.6초 예고로 100/50/25/20 px 격자의 공정성과 봇 완주가 통과했다는 기록은 pre-enable 문서에 있다. 이 작업은 그 결과를 재작성하거나 사람 플레이·그림·균형 승인으로 취급하지 않는다.

Claude가 사용자에게 켜라는 지시를 받은 뒤 활성화·실제 출격 목록의 검사·자기 방 보스 캡처·quick/full 검증을 담당한다. 사람의 새벽 테두리와 판 검토, 플레이·균형·FPS 검토는 별도다.
