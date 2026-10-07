# 회귀 실행 20261005_210052_custom

- 결과: **FAIL** (28/30 PASS)
- 묶음: custom · 커밋: `04eba6c345`
- 시작 2026-10-05T21:00:52 · 소요 3803초

| 테스트 | 결과 | 체크 수 | 시간(초) | 비고 |
|---|---|---:|---:|---|
| battle_flow | PASS | - | 13.0 | SITE7_BATTLE_FLOW: PASS |
| combat_entry | PASS | - | 7.6 |  |
| contract_ui | PASS | 484 | 9.2 | RUN_CONTRACT_UI_SMOKE: PASS (484 checks) |
| hazard_expansion | PASS | 438 | 27.9 | HAZARD_EXPANSION_SMOKE: PASS (438 checks, 15 rooms) res://qa/regression_runs/20261005_210052_custom/out/hazard_expansion/hazard_expansion.json |
| full_op_01 | PASS | - | 133.6 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_02 | PASS | - | 123.6 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_03 | PASS | - | 144.1 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_04 | PASS | - | 162.0 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_05 | PASS | - | 160.9 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_06 | FAIL | - | 164.9 | SITE7_FULL_OPERATION_SMOKE: FAIL |
| full_op_07 | PASS | - | 233.9 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_08 | PASS | - | 197.1 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_09 | PASS | - | 180.6 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_10 | FAIL | - | 176.0 | SITE7_FULL_OPERATION_SMOKE: FAIL |
| boss_capture_geometry | PASS | - | 22.1 | SITE7_BOSS_PATTERN_CAPTURE: PASS res://qa/regression_runs/20261005_210052_custom/out/boss_capture_geometry |
| variety_capture | PASS | 96 | 14.0 | EXPANSION_ITEM1_CAPTURE: PASS (96 checks) res://qa/regression_runs/20261005_210052_custom/out/variety_capture |
| nav_pockets | PASS | - | 71.3 | NAV_POCKET_AUDIT: PASS (0 dead-end cells in 0 of 30 rooms, cell 12 px) |
| connector_alignment | PASS | 1060 | 1436.8 | SITE7_CONNECTOR_ALIGNMENT PASS (1060 checks) |
| battle_geometry | PASS | 5039 | 30.3 | SITE7_BATTLE_GEOMETRY_SMOKE: PASS (5039 checks) |
| walk_graph_capture | PASS | - | 6.4 | SITE7_WALK_GRAPH_HEADLESS: PASS (15 plates) |
| combat_sfx | PASS | 572 | 7.2 | COMBAT_SFX_R04: PASS / 572 checks |
| demo_integration | PASS | 26 | 8.8 | DEMO_INTEGRATION PASS / 26 checks |
| m7_visual | PASS | 84 | 5.4 | M7_AUTHORED_VISUAL_SMOKE: PASS |
| m10_intel | PASS | 39 | 5.0 | M10_INTEL_LOADOUT_SMOKE: PASS |
| m13_loadout | PASS | 46 | 5.8 | M13_WEAPON_LOADOUT_SMOKE: PASS |
| campaign | PASS | 235 | 25.3 | SITE7_CAMPAIGN_PROGRESSION: PASS (235 checks) res://qa/regression_runs/20261005_210052_custom/out/campaign |
| rook_app | PASS | 1895 | 98.4 | ROOK_MOTION_LAB_APP_SMOKE: PASS (1895 checks, 0 failures) |
| motion_lab_runtime | PASS | 106 | 11.8 | MOTION_LAB_CHARACTER_RUNTIME_SMOKE: PASS |
| motion_lab_python | PASS | 137 | 269.3 | OK |
| motion_lab_js | PASS | 30 | 0.4 |  |

## 기존 QA 기록 보호

- `qa/`, `motion_lab_v1/qa/`의 기존 파일 변경·삭제·추가 0건
