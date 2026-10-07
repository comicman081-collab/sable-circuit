# 회귀 실행 20260927_124809_full

- 결과: **PASS** (54/54 PASS)
- 묶음: full · 커밋: `492311f603` (작업 트리 변경 31개)
- 시작 2026-09-27T12:48:09 · 소요 1964초

| 테스트 | 결과 | 체크 수 | 시간(초) | 비고 |
|---|---|---:|---:|---|
| combat_density | PASS | 37 | 17.7 | COMBAT_DENSITY_SMOKE PASS (37 checks) {"attacks_started":41,"drone_orbit_split":[2,2],"frames_with_two_or_more_attackers":505,"hostiles":7,"max_concurrent_attac |
| cover_navigation | PASS | 15 | 1.3 | COVER_NAVIGATION_SMOKE: PASS / 15 checks |
| floor_segment | PASS | 13 | 22.1 | FLOOR_SEGMENT_SMOKE: PASS (13 checks) |
| combat_query_fastpath | PASS | 31 | 8.6 | COMBAT_QUERY_FASTPATH_SMOKE: PASS (31 checks) |
| player_cover | PASS | 5 | 6.1 | SITE7_PLAYER_COVER_COLLISION: PASS (5 checks) |
| cover_alpha_clip | PASS | 5 | 1.1 | SITE7_COVER_ALPHA_CLIP: PASS / 5 checks |
| cover_texture | PASS | 17 | 1.9 | COVER_TEXTURE_REDUCTION_SMOKE: PASS (17 checks) 63.3 MB -> 10.2 MB |
| battle_flow | PASS | - | 6.7 | SITE7_BATTLE_FLOW: PASS |
| combat_entry | PASS | - | 5.9 |  |
| drone_app | PASS | 171 | 1.7 | SITE7_DRONE_APP_SMOKE: PASS (171 checks) res://qa/regression_runs/20260927_124809_full/out/drone_app/drone_app.json |
| anchor_app | PASS | 271 | 1.3 | SITE7_ANCHOR_APP_SMOKE: PASS (271 checks) res://qa/regression_runs/20260927_124809_full/out/anchor_app/anchor_app.json |
| enemy_facing | PASS | 224 | 2.1 | SITE7_ENEMY_FACING_SMOKE: PASS (224 checks) |
| machine_source | PASS | 436 | 1.7 | SITE7_MACHINE_SOURCE_SMOKE: PASS (436 checks) |
| emission_owner | PASS | 870 | 3.2 | SITE7_EMISSION_OWNER_SMOKE: PASS (870 checks) res://qa/regression_runs/20260927_124809_full/out/emission_owner |
| m2_story | PASS | 27 | 4.2 | M2_STORY_FLOW_SMOKE: PASS |
| m9_skill | PASS | 44 | 3.4 | M9_OPERATOR_SKILL_SYNERGY_SMOKE: PASS |
| m10_base_ui | PASS | 10 | 0.7 | M10_BASE_UI_ACTION_SMOKE: PASS |
| m10_persistence | PASS | 27 | 0.4 | M10_PERSISTENCE_SMOKE: PASS |
| m12_revive | PASS | 25 | 3.4 | M12_SQUAD_REVIVE_SMOKE: PASS |
| play_log | PASS | 23 | 4.2 | PLAY_SESSION_LOG_SMOKE: PASS (23 checks) res://qa/regression_runs/20260927_124809_full/out/play_log |
| hit_hurt_vfx | PASS | 47 | 1.9 | COMBAT_HIT_HURT_VFX_SMOKE: PASS (47 checks) |
| combat_vfx | PASS | 154 | 2.1 | COMBAT_VFX_OVERHAUL_SMOKE: PASS (154 checks) |
| elite_affix | PASS | 43 | 4.0 | ELITE_AFFIX_SMOKE: PASS (43 checks) |
| zone_hazard | PASS | 115 | 19.2 | ZONE_HAZARD_SMOKE: PASS (115 checks, 5 rooms) |
| firing_lane | PASS | 163 | 10.7 | FIRING_LANE_SEARCH_SMOKE: PASS (163 checks) |
| platform_carry | PASS | 6 | 4.9 | ACTOR_PLATFORM_CARRY_SMOKE: PASS (6 checks) |
| contact_carry | PASS | 27 | 13.3 | ACTOR_CONTACT_CARRY_SMOKE: PASS (27 checks) |
| world_layout | PASS | - | 4.6 | SITE7_WORLD_LAYOUT PASS 5 missions |
| walk_registration | PASS | - | 0.8 | WALK_TORSO_REGISTRATION PASS |
| deploy_warmer | PASS | 76 | 5.2 | DEPLOY_WARMER_SMOKE: PASS (76 checks) |
| m13_migration | PASS | 9 | 0.7 | M13_WEAPON_BASE_MIGRATION_SMOKE: PASS |
| m13_campaign | PASS | 16 | 0.4 | M13_WEAPON_CAMPAIGN_SMOKE: PASS |
| m13_runtime | PASS | 18 | 3.4 | M13_WEAPON_RUNTIME_SMOKE: PASS |
| full_op_01 | PASS | - | 131.2 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_02 | PASS | - | 115.3 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_03 | PASS | - | 114.2 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_04 | PASS | - | 125.2 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_05 | PASS | - | 117.6 | SITE7_FULL_OPERATION_SMOKE: PASS |
| traversal_audit | PASS | 1253 | 360.4 | SITE7_TRAVERSAL_AUDIT: PASS (1253 checks, 0 failures) |
| enemy_cover_nav | PASS | - | 60.1 | ENEMY_COVER_NAVIGATION PASS res://qa/regression_runs/20260927_124809_full/out/enemy_cover_nav [] |
| cover_ai | PASS | 46 | 37.2 |  |
| world_route | PASS | 49 | 9.7 | SITE7_WORLD_ROUTE_NAVIGATION: PASS (49 checks) |
| connector_alignment | PASS | 355 | 400.9 | SITE7_CONNECTOR_ALIGNMENT PASS (355 checks) |
| battle_geometry | PASS | 2134 | 13.1 | SITE7_BATTLE_GEOMETRY_SMOKE: PASS (2134 checks) |
| combat_sfx | PASS | 558 | 4.2 | COMBAT_SFX_R04: PASS / 558 checks |
| demo_integration | PASS | 26 | 6.3 | DEMO_INTEGRATION PASS / 26 checks |
| m7_visual | PASS | 84 | 3.8 | M7_AUTHORED_VISUAL_SMOKE: PASS |
| m10_intel | PASS | 39 | 3.4 | M10_INTEL_LOADOUT_SMOKE: PASS |
| m13_loadout | PASS | 46 | 3.6 | M13_WEAPON_LOADOUT_SMOKE: PASS |
| campaign | PASS | 94 | 9.7 | SITE7_CAMPAIGN_PROGRESSION: PASS (94 checks) res://qa/regression_runs/20260927_124809_full/out/campaign |
| rook_app | PASS | 1895 | 97.5 | ROOK_MOTION_LAB_APP_SMOKE: PASS (1895 checks, 0 failures) |
| motion_lab_runtime | PASS | 106 | 10.4 | MOTION_LAB_CHARACTER_RUNTIME_SMOKE: PASS |
| motion_lab_python | PASS | 137 | 165.1 | OK |
| motion_lab_js | PASS | 30 | 0.4 |  |

## 기존 QA 기록 보호

- `qa/`, `motion_lab_v1/qa/`의 기존 파일 변경·삭제·추가 0건
