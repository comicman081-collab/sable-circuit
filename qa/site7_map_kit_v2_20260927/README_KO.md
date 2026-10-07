# SITE-7 맵 키트 v2 — 단계 0 파일럿 HOLD

2026-09-27. `AGENTS.md`를 먼저 읽고 `docs/production/SITE7_MAP_KIT_V2_CODEX_PROMPT_KO.md`를 끝까지 읽은 뒤 단계 0만 시도했다.

**단계 0은 완료되지 않았다.** 첫 대상 `S1_R02`가 내장 ImageGen 3회 안에 문/에이프런과 바닥 조명 규격을 함께 만족하지 못해, 작업 지시서 6절의 중단 조건에 따라 HOLD로 멈췄다. `S1_C01`, `S1_C06`은 생성하지 않았다. 단계 1 이후는 시작하지 않았다.

## HOLD의 근거

- 1회차: 바닥 평균 휘도 0.254로 상한 0.24 초과. 실제 바닥이 테두리 8% 안쪽 규격을 침범하고 문 밖 에이프런도 불완전했다.
- 2회차: 주 바닥의 조명 audit는 통과했지만, SW 문 밖 바닥이 검정으로 흐려졌다. 문 개구부도 약 300px 목표보다 크게 좁았다.
- 3회차: 에이프런의 흐림은 고쳐졌지만 SW 문 개구부는 수동 추적으로 약 166px(추정 오차 약 15px)에 그쳤다. 목표 약 300px의 약 55%이다. 바닥 평균 휘도도 0.267로 다시 상한을 초과했다.
- 최종 원본은 요청한 2048×1152와 달리 **1672×941 RGB**로 반환됐다. 세 번 모두 같은 크기였다. 확대하거나 수작업으로 칠하지 않았다. 이 파일을 네이티브 1080p 원화로 주장하지 않는다.

문 너비 측정은 실제 그림의 SW 문 기둥 사이 바닥 경계 `(370,636)`–`(520,708)`을 원본 픽셀에서 수동 추적한 값이다. 자동 문 검출이나 런타임 통행 테스트가 아니다. 바닥 조명 PASS가 문 규격 PASS를 대신하지 않는다.

## 게임 내 네이티브 1080p 캡처

실제 Godot `StoryStage01` 장면에서 대원 3명을 유지한 채, 같은 카메라·같은 대원 위치로 v1과 3회차 후보를 비교했다. 창과 렌더 버퍼는 1920×1080, 콘텐츠 크기도 1920×1080, 카메라 줌은 1.0이다. 후보 판 배율은 1.0이며 **원본 1픽셀을 화면 1픽셀 크기로** 표시했다. 작은 완성 화면을 확대하지 않았다.

- [v1 같은 카메라](hold_capture/v1_R02_same_camera.webp)
- [v2 후보 3회차 — HOLD](hold_capture/v2_R02_hold_same_camera.webp)
- [문 너비·바닥 추적 표시](hold_capture/v2_R02_hold_door_measurement.webp)

이것은 **장면 내 격리 원화·축척 진단 캡처**이다. 메모리에서 R02의 Sprite2D 텍스처만 교체했고, 원본 픽셀을 보기 위해 후보의 이음매 셰이더를 껐다. 다른 판은 숨겼다. 충돌, 내비게이션, 문 앵커, 엄폐물, 스폰은 v2로 교체하지 않았다. 연결 완료·실제 플레이·미술 승인 증거가 아니다.

지시된 `plate_seam_capture.gd`도 `.cache/diag/`로 복사하여 v1 작전 1 전체를 촬영했다. [baseline](baseline/)에는 통로 7장과 방 16장, 합계 23장의 1920×1080 캡처가 있다. v2 격리 진단 3장을 합쳐 **26장**이다. 보존본은 무손실 WebP이며, PNG 캡처와 디코딩한 RGBA 픽셀 일치를 확인했다.

캡처 스크립트: [원배율 진단](probe/room_hold_capture.gd), [v1 이음매](probe/plate_seam_capture.gd). 실행 가능한 작업 사본은 `.cache/site7_v2_pilot/room_hold_capture.gd`, `.cache/diag/plate_seam_capture.gd`이다. 출력은 반드시 `--out=res://.cache/...`로 지정했다. QA 폴더에 스크립트를 직접 실행해 기록을 덮어쓰지 않는다.

## audit 결과

`audit_site7_plate_lighting.py`의 원화 픽셀 측정 함수를 그대로 사용했다. 후보의 바닥은 그림을 수동 추적했으며, 원화·판정 상수·audit 도구 코드는 수정하지 않았다.

| 대상 | 평균 휘도 | p10 | p90 | 평균색 채도 | 바닥 축 | 주 바닥 조명/축 결과 |
|---|---:|---:|---:|---:|---:|---|
| v1 R02 | 0.156 | 0.077 | 0.234 | 0.300 | 30.9° | FAIL |
| v2 R02 1회 | 0.254 | 0.193 | 0.328 | 0.010 | 27.6° | FAIL — 평균 휘도 |
| v2 R02 2회 | 0.238 | 0.207 | 0.264 | 0.009 | 24.6° | PASS — 주 바닥만; 문/에이프런 FAIL |
| v2 R02 3회 | 0.267 | 0.239 | 0.295 | 0.006 | 24.9° | FAIL — 평균 휘도 |

목표: 평균 휘도 0.17–0.24, p10 ≥0.07, p90 ≤0.38, 채도 ≤0.15, 축 22.5–30.5°.

후보 수치는 **주 바닥만** 측정한 값이다. 문 밖 에이프런과 방 전체의 형상은 별도 시각 검사 대상이다. 후보가 런타임에 연결되지 않았으므로 v2 이음매 수치나 `--strict` PASS는 없다.

- [후보별 audit JSON](audit_S1_R02_candidates.json): 정확한 수치와 추적 좌표.
- [v1 작전 1 audit JSON](audit_v1_mission01.json): 현재 런타임 기준. 판 15장 중 11장, 이음매 14곳 모두 FAIL. 합계 **25개 판/이음매 기준 밖**.
- [최종 런타임 audit 로그](final_runtime_audit.log): `SITE7_PLATE_LIGHTING FAIL (25 plates/seams off target)`.

전후 판정은 동일하다. 변경 없는 v1 C06에서 부동소수점 값 3개만 달랐고 최대 차이는 색조 0.0000294°였다. 0.0001 절대 오차 안에서 수치 재현성을 확인했으며, 바이트 단위 JSON 일치로 주장하지 않는다. [최종 무결성 검사](verification_summary.json)에는 이 차이와 원본/프롬프트/참조/캡처 해시 검증 결과가 있다.

실행한 명령:

```text
python tools/environment/audit_site7_plate_lighting.py --mission MIS_CH01_01 --out .cache/site7_v2_pilot/final_runtime_audit.json
python -B .cache/site7_v2_pilot/audit_candidates.py
```

이 환경의 PATH에 Python이 없고 기본 샌드박스에서 venv의 원본 인터프리터 실행이 차단되어, 기존 `C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe`를 승인된 실행 권한으로 사용했다. 런타임은 수정하지 않았고, `PYTHONDONTWRITEBYTECODE=1`, TEMP/TMP는 프로젝트 `.cache/`로 지정했다. Python 도구의 사본·라이브러리를 새로 설치하지 않았다.

## 보존·검증 범위

- [생성 매니페스트](../../art_src/environments/site7_v2/SITE7_MAP_KIT_V2_MANIFEST.md)에 세 번의 **프롬프트 전문**, 참조 경로·해시, 원본 해시, 네이티브 크기와 거절 사유를 기록했다.
- 세 후보는 `art_src/environments/site7_v2/_quarantine/S1_R02/attempt01`–`attempt03`에 보존했다. MASTER/GAME 파생본은 만들지 않았다. 노출·화이트밸런스·크롭·축소·확대 등 픽셀 변환도 없다.
- 내장 도구의 C 드라이브 관리 스테이징 사본은 각각 프로젝트 복사 후 SHA-256 일치를 확인하고 그 파일만 삭제했다.
- 게임 데이터, 런타임 코드, 기존 v1 원화, `AGENTS.md`, 테스트 기준은 그대로다. 사용자 세이브와 설정을 저장하지 않았다.
- `validate_visual_evidence_1080p.py --require-dynamic-capture`로 26장 모두를 검사했다. [검사 JSON](visual_evidence_1080p.json)은 해상도/디코딩 검사이며 미술 승인과 무관하다.
- **quick/full 회귀는 실행하지 않았다.** 원화 단계에서 HOLD되어 런타임 통합 자체를 시작하지 않았다. 따라서 회귀 PASS, 문 정렬, 갈래 비반전, 새 바닥 경로, 새 맵 전체 조감은 주장하지 않는다.
- 네이티브 캡처 로그에 기존 `Loaded resource as image file`, `M7_RASTER_QUARANTINED` 경고와 샌드박스의 인증서 저장소 읽기 오류가 있다. 캡처 프로세스는 종료 코드 0으로 끝났고 26장의 해상도와 디코딩을 별도 검사했다. 최초 v1 캡처의 상대 log 경로는 Godot가 `user://`로 해석해 디렉터리 생성에 실패했다. 이후에는 D: 프로젝트의 절대 log 경로를 사용했다.
- [증거 매니페스트](evidence_manifest.json)에 캡처 해시와 정확한 범위를 기록했다. GitHub push, PR, Pages, Actions, 웹 배포는 없다.

**이 HOLD 결과를 보고하고 멈춘다. 추가 ImageGen 시도나 후속 판 생성은 수행하지 않는다.**
