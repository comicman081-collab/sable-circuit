# Ponytail FULL — MICA facial projection cause and limited repair

검수자: `/root/ponytail_motion_audit` (독립 Ponytail FULL)

실제 검수 시각: **2026-09-07 12:57:50 UTC / 21:57:50 KST**.
판정: **PASS_LIMITED_PROJECTION_MECHANISM_ONLY**. 새 정확한 제작 계획을 검토할 수 있다는 뜻이며, 실행 예약·native 첫 포즈·외형·모션 승인이 아닙니다.

## 실제 실패 원인

격리된 `mica_anatomical_model_r03/MESH_PREFLIGHT_RAW.json`(SHA `6836427d70f40ebdf387fb8144f2fbf81689ed817e2d2ff982a43c3e45623eac`)과 감사 결과를 직접 읽고 UV 값을 재계산했습니다. 원래 MICA_Head 1,404개 triangle 중 **45개**가 기존 UV 기준에 미달했습니다. 코트 1,536개는 모두 유효했습니다. 실제 감사의 유일한 오류는 `DEGENERATE_UV_TRIANGLE`이므로 렌더 전에 중단된 것은 올바릅니다.

`generation_harness.py:759–761`은 `abs(cross(UV))*width*height < .25`를 검사합니다. 이는 삼각형의 **두 배 면적(area2)**이며 실제 면적 기준으로는 .125 source px²입니다. 이 기준을 낮추거나 UV를 늘여 정답을 꾸미지 않습니다. R3 실패 triangle의 area2 최소는 0.00713163, 제외 대상 area2 합은 5.34508입니다.

정면 x/z 투영은 표면의 y 방향 깊이를 버립니다. 진단에 기록된 실제 제외 면 좌표로 법선을 계산하면, 재삼각화 후 제외 46개 중 29개는 정면축 법선 절대값이 0.1 미만인 거의 접선 면입니다. 나머지는 실제 3D 삼각형이 작아서 source 해상도 기준을 충족하지 못합니다. 따라서 모두 가려진 면이거나 원화 마스크 밖이었다고 해석하지 않습니다.

## 한정 수정과 직접 확인한 결과

검토한 helper: `tools/character_pipeline/facial_overlay_projection.py`, SHA `83d997d32e0ad811f675bbf780e2cfb16427c81f2815535fad91ca3e025bd8e2`.

실제 builder와 저장된 R3 snapshot의 diff는 얼굴 chart 적용 직후 helper 호출/기록 추가, `.blend` 저장 시 `relative_remap=False` 추가입니다. 현재 builder SHA는 `77a2f9d41c2288465eacbf179c3d5d1e65ac57e5556484fc577156230d08e902`입니다. 원래 인체·boot·source gate·UV 기준은 변경되지 않았습니다.

helper는 실제 `facial_surface` 덧면만 삼각화하고 기존 area2 기준 미달인 면만 제외합니다. 원래 닫힌 body/head, 좌표, face topology와 weights를 전후 비교해 같아야 합니다. 유지된 덧면 코너도 원래 위치·UV·weights의 부분집합인지 검사합니다. UV 신장·새 원화·인체 alpha 삭제·근접색 픽셀 대체가 없습니다. 미달 면이 10%를 넘으면 덧면 수정을 중단합니다. 이 안전 상한 자체가 얼굴 품질의 자동 기준은 아닙니다.

실제 저장 장면 진단 `mica_face_projection_r2/PROJECTION_DIAGNOSTIC.json` SHA:
`5ed582ab7cc14b8332d463037351112af081a94735802bb585c2b93238a60287`.

| 실제 확인 항목 | 결과 |
| --- | --- |
| 실제 collector 재실행 | errors `[]`, 판정 `HOLD_NATIVE_FIRST_POSE`; 완료 영수증 존재 |
| BEAUTY 재삼각화 후 덧면 | 46개 제외, 1,358개 유지. R3의 원래 45개와 다른 삼각분할임을 구분 |
| 유지 UV | 실제 RAW 재계산에서 area2 최소 0.26107013, .25 미만 0개 |
| body 보존 | 10,582정점/10,590면, body geometry/weights SHA 전후 `57b227da46527365ecc7a5e5240d1ca8f376993f2020d5f8ed912cdfc1519da1`로 동일 |
| 덧면 유지 코너 | 위치·UV·weight 보존 검사 통과, 기록 SHA `66dcc480b41c45c3c093411eea97da148f690184cdf1aafb8526efb2c2ce6c84` |
| 실제 다른 mesh 검사 | body, boots, coat의 collector 객체 내용이 R3와 동일. Body/boots의 닫힘·weight 오류 0 유지 |
| 원본 저장 장면 보존 | 격리 R3 `.blend` SHA `ae6cd906d568308c0999a516dbcf9acacaa13889257bab064ff29fe01517cb8f`가 현재도 일치 |

## 별도 재로드 경로 오류

진단 r1은 UV 수정 후에도 `CHART_NOT_ACTUAL_MATERIAL_IMAGE` 두 항목으로 FAIL이었습니다. 실제 RAW의 material 경로가 원래 `art_src/characters/mica/rigged_v2/source_front_r1/…`에서 격리 폴더 아래 `artifacts/quarantine/generation_diagnostics/source_front_r1/…`로 바뀐 것을 확인했습니다. `.blend` 이동 후 기존 상대 이미지 경로가 새 위치를 기준으로 해석된 문제입니다.

r2 진단은 원래 `.blend` bytes를 바꾸지 않고, 파생 장면에서 content-bound chart ref의 정확한 승인 이미지 SHA를 검증해 해당 이미지 경로만 복구합니다. 진단 코드 SHA `8136407658d61641e1abfe7e54718f2f5b22cffaa19d853ff8bc9612b19f2cd7`와 결과의 ref가 일치합니다. 이름만 같은 새 이미지/다른 원화로 대체하지 않습니다. 실패 r1은 성공으로 재표기하지 않습니다.

## 다음 경계

이 한정 수정에서 추가 실행 전 P1은 발견하지 못했습니다. 현재 helper·builder·진단을 새 R4 build plan에 결합한 뒤 별도 검수와 새 1회 예약을 받아야 합니다. 과거 R3 receipt/claim 재사용 권한은 없습니다.

이 진단은 렌더하지 않았습니다. 덧면 경계의 피부색 차이, 얼굴 닮음, 표면 겹침, 눈·코·입 위치와 전체 복장은 native 첫 포즈로 확인해야 합니다. UV 기술 통과가 이를 승인하지 않습니다. 보행·달리기·8방향 사격·접지·HTML·Luna는 이 보고서의 범위 밖이며 미완료입니다.

적용 지침: `sable-motion-production`과 Ponytail FULL. 이번 검수에서는 읽기 전용 코드/원장 분석과 이 보고서 작성만 수행했고, Blender·렌더·테스트 실행이나 소스 수정은 하지 않았습니다.
