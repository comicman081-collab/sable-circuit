# SABLE CIRCUIT — MICA C03 R20 R8C 60Hz 검수 요청

이번 첨부는 **R20 R8C 60Hz 게이트 후보**입니다. 첨부된 R20 MP4와 포터블 HTML/runtime atlas를 실제로 열어 연속 프레임을 확인하고, 새 이미지·접촉시트·생성 작업은 하지 말고 텍스트로만 판정해 주세요.

## 후보와 증거

- Godot native MP4: `MICA_C03_R20_R8C_60HZ_NATIVE_1920X1080_R3.mp4` — 1920×1080, 60fps, 960프레임, E→SE→S→SW→W→NW→N→NE, 방향당 120샘플(24 authored cell×2 cycle)
- Runtime evidence: `MICA_C03_R20_RUNTIME_60HZ_EVIDENCE.json` — active frame 00..23 두 사이클, 셀당 4–6틱, max hold 3틱, root factor 0.258947368
- Portable HTML: `MICA_C03_INTERACTIVE_STRIDE_FIRE.html` 및 `runtime/` 8방향 RGBA atlas
- HTML static validation은 `PASS_STATIC_CONFIG_ONLY`이며 동적 시각 PASS를 대신하지 않습니다.

## A~F 판정 요청

E/SE/S/SW/W/NW/N/NE 각각에 대해 `PASS/HOLD/FAIL`로 보수적으로 판정해 주세요.

- A: 실제 전진 방향, 왼발↔오른발 stance–swing 교대, 탭댄스/스케이트/다리 교차/팔자 발끝
- B: 다리 길이·폭·종아리 볼륨·허리/상체 snap 및 비균일 스케일
- C: 발목 90도, 부츠 반전, foot snap, sole 접지·관통·부유
- D: 두 support window의 실제 sole lock, F11→F12/F23→F00 handoff, 60Hz cadence 및 보폭
- E: 상체·골반·코트·무기 접합, z-order, green/alpha flicker, 총구와 projectile 축/탄생점
- F: 방향별 blocker와 유지 가능한 non-blocker

R20은 새 원화가 아니라 기존 Codex-authored MICA C03 원화와 Blender+UAL R8C move cell을 사용한 **런타임 스케일/캡처 하네스 후보**입니다. SW visible barrel/projectile 축은 아직 교정되지 않은 것으로 표시되어 있으므로 숫자 socket만으로 PASS하지 말고 화면 총열 끝과 실제 방향을 확인해 주세요.

후보 상태는 `UNREVIEWED_DO_NOT_PROMOTE`로 유지하고, 모든 visual/runtime/technical/pointer/package 게이트가 닫힐 때까지 production promotion은 `HOLD`로 기록해 주세요. R17/R18/R19 및 이전 FAIL/HOLD 자료는 삭제하지 말고 quarantine 보존으로 명시해 주세요.
