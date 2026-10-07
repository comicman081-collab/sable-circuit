# 회귀 실행 20260927_165002_full

- 결과: **PASS** (55/55 PASS)
- 묶음: full · 커밋: `b70b7ac43d` (작업 트리 변경 9개)
- 시작 2026-09-27T16:50:02 · 소요 2086초

| 테스트 | 결과 | 체크 수 | 시간(초) | 비고 |
|---|---|---:|---:|---|
| combat_density | PASS | 37 | 17.9 | COMBAT_DENSITY_SMOKE PASS (37 checks) {"attacks_started":32,"drone_orbit_split":[2,2],"frames_with_two_or_more_attackers":305,"hostiles":7,"max_concurrent_attac |
| cover_navigation | PASS | 15 | 1.2 | COVER_NAVIGATION_SMOKE: PASS / 15 checks |
| floor_segment | PASS | 13 | 22.4 | FLOOR_SEGMENT_SMOKE: PASS (13 checks) |
| combat_query_fastpath | PASS | 31 | 9.4 | COMBAT_QUERY_FASTPATH_SMOKE: PASS (31 checks) |
| player_cover | PASS | 5 | 6.8 | SITE7_PLAYER_COVER_COLLISION: PASS (5 checks) |
| cover_alpha_clip | PASS | 5 | 1.2 | SITE7_COVER_ALPHA_CLIP: PASS / 5 checks |
| cover_texture | PASS | 17 | 2.1 | COVER_TEXTURE_REDUCTION_SMOKE: PASS (17 checks) 63.3 MB -> 10.2 MB |
| battle_flow | PASS | - | 7.5 | SITE7_BATTLE_FLOW: PASS |
| combat_entry | PASS | - | 6.4 |  |
| drone_app | PASS | 171 | 1.9 | SITE7_DRONE_APP_SMOKE: PASS (171 checks) res://qa/regression_runs/20260927_165002_full/out/drone_app/drone_app.json |
| anchor_app | PASS | 271 | 1.4 | SITE7_ANCHOR_APP_SMOKE: PASS (271 checks) res://qa/regression_runs/20260927_165002_full/out/anchor_app/anchor_app.json |
| enemy_facing | PASS | 224 | 2.3 | SITE7_ENEMY_FACING_SMOKE: PASS (224 checks) |
| machine_source | PASS | 436 | 1.9 | SITE7_MACHINE_SOURCE_SMOKE: PASS (436 checks) |
| emission_owner | PASS | 870 | 3.4 | SITE7_EMISSION_OWNER_SMOKE: PASS (870 checks) res://qa/regression_runs/20260927_165002_full/out/emission_owner |
| m2_story | PASS | 27 | 4.4 | M2_STORY_FLOW_SMOKE: PASS |
| m9_skill | PASS | 44 | 3.8 | M9_OPERATOR_SKILL_SYNERGY_SMOKE: PASS |
| m10_base_ui | PASS | 10 | 0.6 | M10_BASE_UI_ACTION_SMOKE: PASS |
| m10_persistence | PASS | 27 | 0.4 | M10_PERSISTENCE_SMOKE: PASS |
| m12_revive | PASS | 25 | 4.2 | M12_SQUAD_REVIVE_SMOKE: PASS |
| play_log | PASS | 23 | 5.5 | PLAY_SESSION_LOG_SMOKE: PASS (23 checks) res://qa/regression_runs/20260927_165002_full/out/play_log |
| hit_hurt_vfx | PASS | 47 | 2.5 | COMBAT_HIT_HURT_VFX_SMOKE: PASS (47 checks) |
| combat_vfx | PASS | 154 | 2.8 | COMBAT_VFX_OVERHAUL_SMOKE: PASS (154 checks) |
| elite_affix | PASS | 43 | 4.2 | ELITE_AFFIX_SMOKE: PASS (43 checks) |
| zone_hazard | PASS | 115 | 19.9 | ZONE_HAZARD_SMOKE: PASS (115 checks, 5 rooms) |
| firing_lane | PASS | 163 | 11.7 | FIRING_LANE_SEARCH_SMOKE: PASS (163 checks) |
| platform_carry | PASS | 6 | 5.4 | ACTOR_PLATFORM_CARRY_SMOKE: PASS (6 checks) |
| contact_carry | PASS | 27 | 13.8 | ACTOR_CONTACT_CARRY_SMOKE: PASS (27 checks) |
| world_layout | PASS | - | 4.4 | SITE7_WORLD_LAYOUT PASS 5 missions |
| mood_light | PASS | - | 5.7 | SITE7_MOOD_LIGHT PASS 15 plates 85 pools 15 void masks |
| walk_registration | PASS | - | 1.0 | WALK_TORSO_REGISTRATION PASS |
| deploy_warmer | PASS | 76 | 6.2 | DEPLOY_WARMER_SMOKE: PASS (76 checks) |
| m13_migration | PASS | 9 | 0.6 | M13_WEAPON_BASE_MIGRATION_SMOKE: PASS |
| m13_campaign | PASS | 16 | 0.4 | M13_WEAPON_CAMPAIGN_SMOKE: PASS |
| m13_runtime | PASS | 18 | 4.0 | M13_WEAPON_RUNTIME_SMOKE: PASS |
| full_op_01 | PASS | - | 134.7 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_02 | PASS | - | 121.7 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_03 | PASS | - | 118.7 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_04 | PASS | - | 115.8 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_05 | PASS | - | 118.7 | SITE7_FULL_OPERATION_SMOKE: PASS |
| traversal_audit | PASS | 1253 | 376.0 | SITE7_TRAVERSAL_AUDIT: PASS (1253 checks, 0 failures) |
| enemy_cover_nav | PASS | - | 61.2 | ENEMY_COVER_NAVIGATION PASS res://qa/regression_runs/20260927_165002_full/out/enemy_cover_nav [] |
| cover_ai | PASS | 46 | 37.4 |  |
| world_route | PASS | 49 | 11.1 | SITE7_WORLD_ROUTE_NAVIGATION: PASS (49 checks) |
| connector_alignment | PASS | 390 | 420.5 | SITE7_CONNECTOR_ALIGNMENT PASS (390 checks) |
| battle_geometry | PASS | 2371 | 15.3 | SITE7_BATTLE_GEOMETRY_SMOKE: PASS (2371 checks) |
| combat_sfx | PASS | 558 | 5.3 | COMBAT_SFX_R04: PASS / 558 checks |
| demo_integration | PASS | 26 | 7.2 | DEMO_INTEGRATION PASS / 26 checks |
| m7_visual | PASS | 84 | 4.5 | M7_AUTHORED_VISUAL_SMOKE: PASS |
| m10_intel | PASS | 39 | 4.1 | M10_INTEL_LOADOUT_SMOKE: PASS |
| m13_loadout | PASS | 46 | 4.3 | M13_WEAPON_LOADOUT_SMOKE: PASS |
| campaign | PASS | 94 | 11.3 | SITE7_CAMPAIGN_PROGRESSION: PASS (94 checks) res://qa/regression_runs/20260927_165002_full/out/campaign |
| rook_app | PASS | 1895 | 98.1 | ROOK_MOTION_LAB_APP_SMOKE: PASS (1895 checks, 0 failures) |
| motion_lab_runtime | PASS | 106 | 11.3 | MOTION_LAB_CHARACTER_RUNTIME_SMOKE: PASS |
| motion_lab_python | PASS | 137 | 212.4 | OK |
| motion_lab_js | PASS | 30 | 0.4 |  |

## 기존 QA 기록 보호

- `qa/`, `motion_lab_v1/qa/`의 기존 파일 변경·삭제·추가 0건
