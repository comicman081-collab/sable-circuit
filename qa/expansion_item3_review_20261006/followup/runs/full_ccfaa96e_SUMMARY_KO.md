# 회귀 실행 20261006_185434_full

- 결과: **FAIL** (87/88 PASS)
- 묶음: full · 커밋: `ccfaa96ed7`
- 시작 2026-10-06T18:54:35 · 소요 5268초

| 테스트 | 결과 | 체크 수 | 시간(초) | 비고 |
|---|---|---:|---:|---|
| combat_density | PASS | 67 | 19.7 | COMBAT_DENSITY_SMOKE PASS (67 checks) {"attacks_started":29,"drone_orbit_split":[2,2],"frames_with_two_or_more_attackers":292,"hostiles":7,"max_concurrent_attac |
| cover_navigation | PASS | 43 | 19.4 | COVER_NAVIGATION_SMOKE: PASS / 43 checks |
| floor_segment | PASS | 23 | 40.5 | FLOOR_SEGMENT_SMOKE: PASS (23 checks) |
| combat_query_fastpath | PASS | 34 | 12.6 | COMBAT_QUERY_FASTPATH_SMOKE: PASS (34 checks) |
| player_cover | PASS | 5 | 7.6 | SITE7_PLAYER_COVER_COLLISION: PASS (5 checks) |
| cover_alpha_clip | PASS | 5 | 2.0 | SITE7_COVER_ALPHA_CLIP: PASS / 5 checks |
| cover_texture | PASS | 17 | 3.0 | COVER_TEXTURE_REDUCTION_SMOKE: PASS (17 checks) 63.3 MB -> 10.2 MB |
| battle_flow | PASS | - | 9.2 | SITE7_BATTLE_FLOW: PASS |
| combat_entry | PASS | - | 7.2 |  |
| drone_app | PASS | 171 | 2.6 | SITE7_DRONE_APP_SMOKE: PASS (171 checks) res://qa/regression_runs/20261006_185434_full/out/drone_app/drone_app.json |
| anchor_app | PASS | 271 | 2.4 | SITE7_ANCHOR_APP_SMOKE: PASS (271 checks) res://qa/regression_runs/20261006_185434_full/out/anchor_app/anchor_app.json |
| campaign_data | PASS | 292 | 0.8 | SITE7_CAMPAIGN_DATA: PASS (292 checks) |
| upgrade_economy | PASS | 225 | 2.2 | UPGRADE_ECONOMY: PASS (225 checks) |
| boss_registry | PASS | 163 | 16.1 | SITE7_BOSS_REGISTRY_SMOKE: PASS (163 checks) |
| boss_pattern | PASS | 978 | 3.4 | SITE7_BOSS_PATTERN_SMOKE: PASS (978 checks) res://qa/regression_runs/20261006_185434_full/out/boss_pattern/pattern.json |
| boss_duel | PASS | 2184 | 56.3 | SITE7_BOSS_DUEL_SMOKE: PASS (2184 checks) res://qa/regression_runs/20261006_185434_full/out/boss_duel/duel.json |
| boss_room_fairness | PASS | 21 | 19.2 | SITE7_BOSS_ROOM_FAIRNESS: PASS (21 checks) res://qa/regression_runs/20261006_185434_full/out/boss_room_fairness/room_fairness.json |
| robot_roster | PASS | 302 | 9.0 | SITE7_ROBOT_ROSTER: PASS / 302 checks |
| enemy_facing | PASS | 224 | 3.0 | SITE7_ENEMY_FACING_SMOKE: PASS (224 checks) |
| machine_source | PASS | 436 | 2.6 | SITE7_MACHINE_SOURCE_SMOKE: PASS (436 checks) |
| emission_owner | PASS | 1293 | 5.2 | SITE7_EMISSION_OWNER_SMOKE: PASS (1293 checks) res://qa/regression_runs/20261006_185434_full/out/emission_owner |
| m2_story | PASS | 27 | 6.0 | M2_STORY_FLOW_SMOKE: PASS |
| m9_skill | PASS | 44 | 5.2 | M9_OPERATOR_SKILL_SYNERGY_SMOKE: PASS |
| m10_base_ui | PASS | 10 | 1.0 | M10_BASE_UI_ACTION_SMOKE: PASS |
| m10_persistence | PASS | 27 | 0.8 | M10_PERSISTENCE_SMOKE: PASS |
| run_contract | PASS | 34 | 6.8 | M11_RUN_CONTRACT_SMOKE: PASS |
| contract_offers | PASS | 26950 | 2.4 | RUN_CONTRACT_OFFERS_SMOKE: PASS (26950 checks) |
| contract_ui | PASS | 484 | 10.8 | RUN_CONTRACT_UI_SMOKE: PASS (484 checks) |
| redline | PASS | 78 | 6.0 | REDLINE_SMOKE: PASS (78 checks) |
| contract_save | PASS | 175 | 1.0 | RUN_CONTRACT_SAVE_SMOKE: PASS (175 checks) |
| intel_supply | PASS | 83 | 2.4 | INTEL_SUPPLY_SMOKE: PASS (83 checks) |
| module_expansion | PASS | 86 | 3.4 | MODULE_EXPANSION_SMOKE: PASS (86 checks) |
| weapon_expansion | PASS | 131 | 3.2 | WEAPON_EXPANSION_SMOKE: PASS (131 checks) |
| lab_geometry | PASS | 4005 | 6.0 | LAB_GEOMETRY_SMOKE: PASS (4005 checks) |
| m12_revive | PASS | 25 | 5.0 | M12_SQUAD_REVIVE_SMOKE: PASS |
| play_log | PASS | 25 | 6.4 | PLAY_SESSION_LOG_SMOKE: PASS (25 checks) res://qa/regression_runs/20261006_185434_full/out/play_log |
| hit_hurt_vfx | PASS | 47 | 3.0 | COMBAT_HIT_HURT_VFX_SMOKE: PASS (47 checks) |
| combat_vfx | PASS | 195 | 3.2 | COMBAT_VFX_OVERHAUL_SMOKE: PASS (195 checks) |
| elite_affix | PASS | 71 | 5.6 | ELITE_AFFIX_SMOKE: PASS (71 checks) |
| elite_expansion | PASS | 438 | 7.8 | ELITE_EXPANSION_SMOKE: PASS (438 checks) |
| zone_hazard | PASS | 366 | 50.9 | ZONE_HAZARD_SMOKE: PASS (366 checks, 15 rooms) |
| hazard_expansion | PASS | 438 | 27.1 | HAZARD_EXPANSION_SMOKE: PASS (438 checks, 15 rooms) res://qa/regression_runs/20261006_185434_full/out/hazard_expansion/hazard_expansion.json |
| firing_lane | PASS | 325 | 28.9 | FIRING_LANE_SEARCH_SMOKE: PASS (325 checks) |
| platform_carry | PASS | 6 | 6.2 | ACTOR_PLATFORM_CARRY_SMOKE: PASS (6 checks) |
| contact_carry | PASS | 27 | 15.2 | ACTOR_CONTACT_CARRY_SMOKE: PASS (27 checks) |
| world_layout | PASS | - | 15.4 | SITE7_WORLD_LAYOUT PASS 10 missions |
| mood_light | PASS | - | 74.8 | SITE7_MOOD_LIGHT PASS 150 plates 788 pools 150 void masks 15 contact shadows |
| walk_registration | PASS | - | 1.2 | WALK_TORSO_REGISTRATION PASS |
| plate_axis | PASS | 2 | 2.6 | OK |
| variety_placement | PASS | 10 | 1.6 | OK |
| seam_waiver | PASS | 10 | 2.0 | OK |
| mood_contact | PASS | 13 | 2.8 | OK |
| deploy_warmer | PASS | 83 | 7.8 | DEPLOY_WARMER_SMOKE: PASS (83 checks) |
| m13_migration | PASS | 9 | 0.8 | M13_WEAPON_BASE_MIGRATION_SMOKE: PASS |
| m13_campaign | PASS | 16 | 0.6 | M13_WEAPON_CAMPAIGN_SMOKE: PASS |
| m13_runtime | PASS | 18 | 5.4 | M13_WEAPON_RUNTIME_SMOKE: PASS |
| full_op_01 | PASS | - | 135.5 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_02 | PASS | - | 124.8 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_03 | PASS | - | 142.0 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_04 | PASS | - | 166.4 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_05 | PASS | - | 158.1 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_06 | PASS | - | 181.8 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_07 | PASS | - | 226.5 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_08 | FAIL | - | 135.4 | SITE7_FULL_OPERATION_SMOKE: FAIL |
| full_op_09 | PASS | - | 167.6 | SITE7_FULL_OPERATION_SMOKE: PASS |
| full_op_10 | PASS | - | 207.7 | SITE7_FULL_OPERATION_SMOKE: PASS |
| traversal_audit | PASS | 2394 | 891.1 | SITE7_TRAVERSAL_AUDIT: PASS (2394 checks, 0 failures) |
| enemy_cover_nav | PASS | - | 40.1 | ENEMY_COVER_NAVIGATION PASS res://qa/regression_runs/20261006_185434_full/out/enemy_cover_nav [] |
| cover_ai | PASS | 46 | 37.9 |  |
| boss_capture_geometry | PASS | - | 22.9 | SITE7_BOSS_PATTERN_CAPTURE: PASS res://qa/regression_runs/20261006_185434_full/out/boss_capture_geometry |
| lab_capture_geometry | PASS | 5 | 7.6 | EXPANSION_ITEM3_CAPTURE: PASS (5 checks) |
| boss_lineup | PASS | - | 2.6 | SITE7_BOSS_LINEUP_CAPTURE: PASS res://qa/regression_runs/20261006_185434_full/out/boss_lineup |
| variety_capture | PASS | 96 | 14.6 | EXPANSION_ITEM1_CAPTURE: PASS (96 checks) res://qa/regression_runs/20261006_185434_full/out/variety_capture |
| world_route | PASS | 94 | 18.4 | SITE7_WORLD_ROUTE_NAVIGATION: PASS (94 checks) |
| nav_pockets | PASS | - | 72.3 | NAV_POCKET_AUDIT: PASS (0 dead-end cells in 0 of 30 rooms, cell 12 px) |
| connector_alignment | PASS | 1060 | 1435.3 | SITE7_CONNECTOR_ALIGNMENT PASS (1060 checks) |
| battle_geometry | PASS | 5039 | 27.9 | SITE7_BATTLE_GEOMETRY_SMOKE: PASS (5039 checks) |
| walk_graph_capture | PASS | - | 6.0 | SITE7_WALK_GRAPH_HEADLESS: PASS (15 plates) |
| combat_sfx | PASS | 572 | 6.8 | COMBAT_SFX_R04: PASS / 572 checks |
| demo_integration | PASS | 26 | 8.6 | DEMO_INTEGRATION PASS / 26 checks |
| m7_visual | PASS | 84 | 5.6 | M7_AUTHORED_VISUAL_SMOKE: PASS |
| m10_intel | PASS | 39 | 5.0 | M10_INTEL_LOADOUT_SMOKE: PASS |
| m13_loadout | PASS | 53 | 5.2 | M13_WEAPON_LOADOUT_SMOKE: PASS |
| campaign | PASS | 235 | 26.1 | SITE7_CAMPAIGN_PROGRESSION: PASS (235 checks) res://qa/regression_runs/20261006_185434_full/out/campaign |
| rook_app | PASS | 1895 | 98.4 | ROOK_MOTION_LAB_APP_SMOKE: PASS (1895 checks, 0 failures) |
| motion_lab_runtime | PASS | 106 | 12.2 | MOTION_LAB_CHARACTER_RUNTIME_SMOKE: PASS |
| motion_lab_python | PASS | 137 | 247.5 | OK |
| motion_lab_js | PASS | 30 | 0.4 |  |

## 기존 QA 기록 보호

- `qa/`, `motion_lab_v1/qa/`의 기존 파일 변경·삭제·추가 0건
