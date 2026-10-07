# 회귀 실행 20261003_170533_full

- 결과: **FAIL** (74/78 PASS)
- 묶음: full · 커밋: `4e3ac9e61b`
- 시작 2026-10-03T17:05:34 · 소요 5202초

| 테스트 | 결과 | 체크 수 | 시간(초) | 비고 |
|---|---|---:|---:|---|
| combat_density | PASS | 67 | 19.4 | COMBAT_DENSITY_SMOKE PASS (67 checks) {"attacks_started":29,"drone_orbit_split":[2,2],"frames_with_two_or_more_attackers":292,"hostiles":7,"max_concurrent_attac |
| cover_navigation | PASS | 43 | 17.8 | COVER_NAVIGATION_SMOKE: PASS / 43 checks |
| floor_segment | PASS | 23 | 37.1 | FLOOR_SEGMENT_SMOKE: PASS (23 checks) |
| combat_query_fastpath | FAIL | 31 | 11.0 | COMBAT_QUERY_FASTPATH_SMOKE: FAIL (12 of 31 checks) |
| player_cover | PASS | 5 | 7.2 | SITE7_PLAYER_COVER_COLLISION: PASS (5 checks) |
| cover_alpha_clip | PASS | 5 | 1.6 | SITE7_COVER_ALPHA_CLIP: PASS / 5 checks |
| cover_texture | PASS | 17 | 2.6 | COVER_TEXTURE_REDUCTION_SMOKE: PASS (17 checks) 63.3 MB -> 10.2 MB |
| battle_flow | PASS | - | 10.0 | SITE7_BATTLE_FLOW: PASS |
| combat_entry | PASS | - | 7.6 |  |
| drone_app | PASS | 171 | 2.2 | SITE7_DRONE_APP_SMOKE: PASS (171 checks) res://qa/regression_runs/20261003_170533_full/out/drone_app/drone_app.json |
| anchor_app | PASS | 271 | 2.0 | SITE7_ANCHOR_APP_SMOKE: PASS (271 checks) res://qa/regression_runs/20261003_170533_full/out/anchor_app/anchor_app.json |
| campaign_data | PASS | 292 | 0.6 | SITE7_CAMPAIGN_DATA: PASS (292 checks) |
| upgrade_economy | PASS | 225 | 1.6 | UPGRADE_ECONOMY: PASS (225 checks) |
| boss_registry | PASS | 163 | 16.2 | SITE7_BOSS_REGISTRY_SMOKE: PASS (163 checks) |
| boss_pattern | PASS | 978 | 4.2 | SITE7_BOSS_PATTERN_SMOKE: PASS (978 checks) res://qa/regression_runs/20261003_170533_full/out/boss_pattern/pattern.json |
| boss_duel | PASS | 1124 | 37.7 | SITE7_BOSS_DUEL_SMOKE: PASS (1124 checks) res://qa/regression_runs/20261003_170533_full/out/boss_duel/duel.json |
| boss_room_fairness | PASS | 21 | 22.9 | SITE7_BOSS_ROOM_FAIRNESS: PASS (21 checks) res://qa/regression_runs/20261003_170533_full/out/boss_room_fairness/room_fairness.json |
| robot_roster | PASS | 302 | 9.2 | SITE7_ROBOT_ROSTER: PASS / 302 checks |
| enemy_facing | PASS | 224 | 3.4 | SITE7_ENEMY_FACING_SMOKE: PASS (224 checks) |
| machine_source | PASS | 436 | 2.6 | SITE7_MACHINE_SOURCE_SMOKE: PASS (436 checks) |
| emission_owner | PASS | 1293 | 5.2 | SITE7_EMISSION_OWNER_SMOKE: PASS (1293 checks) res://qa/regression_runs/20261003_170533_full/out/emission_owner |
| m2_story | PASS | 27 | 7.2 | M2_STORY_FLOW_SMOKE: PASS |
| m9_skill | PASS | 44 | 5.4 | M9_OPERATOR_SKILL_SYNERGY_SMOKE: PASS |
| m10_base_ui | PASS | 10 | 1.2 | M10_BASE_UI_ACTION_SMOKE: PASS |
| m10_persistence | PASS | 27 | 0.6 | M10_PERSISTENCE_SMOKE: PASS |
| m12_revive | PASS | 25 | 5.8 | M12_SQUAD_REVIVE_SMOKE: PASS |
| play_log | PASS | 23 | 7.2 | PLAY_SESSION_LOG_SMOKE: PASS (23 checks) res://qa/regression_runs/20261003_170533_full/out/play_log |
| hit_hurt_vfx | PASS | 47 | 3.0 | COMBAT_HIT_HURT_VFX_SMOKE: PASS (47 checks) |
| combat_vfx | PASS | 189 | 3.4 | COMBAT_VFX_OVERHAUL_SMOKE: PASS (189 checks) |
| elite_affix | PASS | 71 | 5.6 | ELITE_AFFIX_SMOKE: PASS (71 checks) |
| elite_expansion | PASS | 438 | 8.2 | ELITE_EXPANSION_SMOKE: PASS (438 checks) |
| zone_hazard | PASS | 366 | 51.1 | ZONE_HAZARD_SMOKE: PASS (366 checks, 15 rooms) |
| hazard_expansion | FAIL | 438 | 26.5 | HAZARD_EXPANSION_SMOKE: FAIL (438 checks, 15 rooms) res://qa/regression_runs/20261003_170533_full/out/hazard_expansion/hazard_expansion.json |
| firing_lane | PASS | 325 | 30.7 | FIRING_LANE_SEARCH_SMOKE: PASS (325 checks) |
| platform_carry | PASS | 6 | 5.8 | ACTOR_PLATFORM_CARRY_SMOKE: PASS (6 checks) |
| contact_carry | PASS | 27 | 14.7 | ACTOR_CONTACT_CARRY_SMOKE: PASS (27 checks) |
| world_layout | PASS | - | 13.5 | SITE7_WORLD_LAYOUT PASS 10 missions |
| mood_light | PASS | - | 71.9 | SITE7_MOOD_LIGHT PASS 150 plates 788 pools 150 void masks 15 contact shadows |
| walk_registration | PASS | - | 1.2 | WALK_TORSO_REGISTRATION PASS |
| plate_axis | PASS | 2 | 2.6 | OK |
| variety_placement | PASS | 10 | 1.0 | OK |
| seam_waiver | PASS | 10 | 1.8 | OK |
| mood_contact | PASS | 13 | 2.4 | OK |
| deploy_warmer | PASS | 83 | 7.0 | DEPLOY_WARMER_SMOKE: PASS (83 checks) |
| m13_migration | PASS | 9 | 0.8 | M13_WEAPON_BASE_MIGRATION_SMOKE: PASS |
| m13_campaign | PASS | 16 | 0.4 | M13_WEAPON_CAMPAIGN_SMOKE: PASS |
| m13_runtime | PASS | 18 | 4.8 | M13_WEAPON_RUNTIME_SMOKE: PASS |
| full_op_01 | PASS | - | 137.9 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_02 | PASS | - | 121.0 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_03 | PASS | - | 150.7 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_04 | PASS | - | 155.7 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_05 | PASS | - | 157.1 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_06 | FAIL | - | 165.6 | SITE7_FULL_OPERATION_SMOKE: FAIL |
| full_op_07 | PASS | - | 223.8 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_08 | FAIL | - | 154.3 | SITE7_FULL_OPERATION_SMOKE: FAIL |
| full_op_09 | PASS | - | 170.8 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_10 | PASS | - | 220.7 | SITE7_FULL_OPERATION_SMOKE: PASS |
| traversal_audit | PASS | 2394 | 891.3 | SITE7_TRAVERSAL_AUDIT: PASS (2394 checks, 0 failures) |
| enemy_cover_nav | PASS | - | 41.5 | ENEMY_COVER_NAVIGATION PASS res://qa/regression_runs/20261003_170533_full/out/enemy_cover_nav [] |
| cover_ai | PASS | 46 | 38.5 |  |
| boss_capture_geometry | PASS | - | 34.8 | SITE7_BOSS_PATTERN_CAPTURE: PASS res://qa/regression_runs/20261003_170533_full/out/boss_capture_geometry |
| boss_lineup | PASS | - | 2.2 | SITE7_BOSS_LINEUP_CAPTURE: PASS res://qa/regression_runs/20261003_170533_full/out/boss_lineup |
| variety_capture | PASS | 96 | 13.8 | EXPANSION_ITEM1_CAPTURE: PASS (96 checks) res://qa/regression_runs/20261003_170533_full/out/variety_capture |
| world_route | PASS | 94 | 19.8 | SITE7_WORLD_ROUTE_NAVIGATION: PASS (94 checks) |
| nav_pockets | PASS | - | 70.3 | NAV_POCKET_AUDIT: PASS (0 dead-end cells in 0 of 30 rooms, cell 12 px) |
| connector_alignment | PASS | 1060 | 1435.9 | SITE7_CONNECTOR_ALIGNMENT PASS (1060 checks) |
| battle_geometry | PASS | 5039 | 30.5 | SITE7_BATTLE_GEOMETRY_SMOKE: PASS (5039 checks) |
| walk_graph_capture | PASS | - | 5.4 | SITE7_WALK_GRAPH_HEADLESS: PASS (15 plates) |
| combat_sfx | PASS | 572 | 6.2 | COMBAT_SFX_R04: PASS / 572 checks |
| demo_integration | PASS | 26 | 7.8 | DEMO_INTEGRATION PASS / 26 checks |
| m7_visual | PASS | 84 | 4.6 | M7_AUTHORED_VISUAL_SMOKE: PASS |
| m10_intel | PASS | 39 | 4.4 | M10_INTEL_LOADOUT_SMOKE: PASS |
| m13_loadout | PASS | 46 | 5.2 | M13_WEAPON_LOADOUT_SMOKE: PASS |
| campaign | PASS | 235 | 25.3 | SITE7_CAMPAIGN_PROGRESSION: PASS (235 checks) res://qa/regression_runs/20261003_170533_full/out/campaign |
| rook_app | PASS | 1895 | 98.4 | ROOK_MOTION_LAB_APP_SMOKE: PASS (1895 checks, 0 failures) |
| motion_lab_runtime | PASS | 106 | 11.6 | MOTION_LAB_CHARACTER_RUNTIME_SMOKE: PASS |
| motion_lab_python | PASS | 137 | 247.4 | OK |
| motion_lab_js | PASS | 30 | 0.4 |  |

## 기존 QA 기록 보호

- `qa/`, `motion_lab_v1/qa/`의 기존 파일 변경·삭제·추가 0건
