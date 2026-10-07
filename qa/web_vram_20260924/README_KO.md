# 웹 출격 시 WebGL 컨텍스트 손실 조사 — 2026-09-24

## 증상
공개 Site v11에서 1작전 출격 직후 화면이 하얗게 멈춤(WebGL 컨텍스트 손실,
`CanvasShaderGLES3` 컴파일 실패). 같은 수정 전 빌드를 로컬에서 다시 돌렸을 때는
재현되지 않아 간헐적 문제로 판단.

## 원인
작전 하나를 불러오면 GPU 텍스처 메모리가 네이티브 기준 약 1.5GB, 웹 기준 약
450~500MB까지 올라감. 그중 화면에 전혀 보이지 않는 텍스처가 큰 비중을 차지함.

- `AsterV4LocomotionPreview`: Motion Studio 런타임이 ASTER를 대체하기 전에
  384×9216 아틀라스 수십 장(588MB)을 먼저 디코딩한 뒤 숨김. 텍스처는 계속 보유.
  (웹 팩에서는 `assets/units`가 빠져 있어 네이티브에만 해당)
- 조작 캐릭터 3명의 옛 벡터 리그(`OperatorVisual`) 2048² SVG 시트 +
  디테일 오버레이: 알파 0으로 숨겨진 상태에서 128MB 보유(웹·네이티브 공통).

## 수정
- `motion_lab_character_runtime.gd`: `activation_pending()` 추가, 활성화 시
  숨긴 벡터 리그/디테일 오버레이 텍스처 해제, 비활성화 시 복원.
- `aster_v4_locomotion_preview.gd`: Motion Studio 결정 전에는 디코딩하지 않고
  대기, 대체되면 아틀라스 배열과 스프라이트 텍스처 해제(파일은 그대로, 재활성화 시
  `_load_textures()`가 다시 채움).
- `operator_visual.gd`: `release_hidden_art()` / `restore_hidden_art()`.
  뼈대·소켓·타이밍은 그대로 두고 픽셀만 해제. 재구성 시에도 같은 파츠 형상 유지.
- `operator_detail_overlay_presentation.gd`: Motion Studio 활성 시 바인딩 생략,
  `release_hidden_art()`.

## 결과 (`measurements.json`)
- 네이티브: 1546 → 830MB(1작전), 1619 → 902MB(4·5작전)
- 웹 환경 재현: 1작전 494 → 366MB(−26%), 5작전 448 → 320MB
- 수정 후 로컬 웹 빌드: 타이틀 → 브리핑 → 1작전 출격, 전투 시작 후 컨텍스트 유지

## 회귀
PASS: motion_lab_character_runtime_smoke, rook_motion_lab_app_smoke(1895),
site7_player_cover_collision_smoke, demo_integration_check(26).
기존부터 FAIL(수정 전 복사본에서 동일하게 재현, 이번 변경과 무관):
m7_authored_visual_smoke(보스 카메라 3), m2_story_flow_smoke(경로 경계 1),
m13_weapon_loadout_smoke(ROOK/MICA 투사체 수 2).

## 남은 부담 / 범위 밖
남은 웹 텍스처는 모션 아틀라스 126MB, 배경 99MB, 적 51MB, 엄폐물 42MB.
엄폐물은 1920×1080 원본을 폭 110~216px로 표시하므로 GPU 사본만 축소하면 추가
절감이 가능하지만, 투사체 알파 판정 좌표와 묶여 있어 이번에는 손대지 않음.
배포, 모바일·저사양 GPU 검증, 사람 플레이테스트는 수행하지 않음.
