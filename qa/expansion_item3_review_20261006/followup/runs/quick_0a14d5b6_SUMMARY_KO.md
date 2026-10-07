# 회귀 실행 20261006_182512_quick

- 결과: **PASS** (56/56 PASS)
- 묶음: quick · 커밋: `0a14d5b61f`
- 시작 2026-10-06T18:25:12 · 소요 621초

| 테스트 | 결과 | 체크 수 | 시간(초) | 비고 |
|---|---|---:|---:|---|
| combat_density | PASS | 67 | 19.9 | COMBAT_DENSITY_SMOKE PASS (67 checks) {"attacks_started":29,"drone_orbit_split":[2,2],"frames_with_two_or_more_attackers":292,"hostiles":7,"max_concurrent_attac |
| cover_navigation | PASS | 43 | 21.1 | COVER_NAVIGATION_SMOKE: PASS / 43 checks |
| floor_segment | PASS | 23 | 44.3 | FLOOR_SEGMENT_SMOKE: PASS (23 checks) |
| combat_query_fastpath | PASS | 34 | 13.9 | COMBAT_QUERY_FASTPATH_SMOKE: PASS (34 checks) |
| player_cover | PASS | 5 | 8.4 | SITE7_PLAYER_COVER_COLLISION: PASS (5 checks) |
| cover_alpha_clip | PASS | 5 | 2.2 | SITE7_COVER_ALPHA_CLIP: PASS / 5 checks |
| cover_texture | PASS | 17 | 3.4 | COVER_TEXTURE_REDUCTION_SMOKE: PASS (17 checks) 63.3 MB -> 10.2 MB |
| battle_flow | PASS | - | 11.7 | SITE7_BATTLE_FLOW: PASS |
| combat_entry | PASS | - | 8.2 |  |
| drone_app | PASS | 171 | 3.2 | SITE7_DRONE_APP_SMOKE: PASS (171 checks) res://qa/regression_runs/20261006_182512_quick/out/drone_app/drone_app.json |
| anchor_app | PASS | 271 | 2.8 | SITE7_ANCHOR_APP_SMOKE: PASS (271 checks) res://qa/regression_runs/20261006_182512_quick/out/anchor_app/anchor_app.json |
| campaign_data | PASS | 292 | 1.0 | SITE7_CAMPAIGN_DATA: PASS (292 checks) |
| upgrade_economy | PASS | 225 | 2.6 | UPGRADE_ECONOMY: PASS (225 checks) |
| boss_registry | PASS | 163 | 18.3 | SITE7_BOSS_REGISTRY_SMOKE: PASS (163 checks) |
| boss_pattern | PASS | 978 | 3.8 | SITE7_BOSS_PATTERN_SMOKE: PASS (978 checks) res://qa/regression_runs/20261006_182512_quick/out/boss_pattern/pattern.json |
| boss_duel | PASS | 2184 | 56.7 | SITE7_BOSS_DUEL_SMOKE: PASS (2184 checks) res://qa/regression_runs/20261006_182512_quick/out/boss_duel/duel.json |
| boss_room_fairness | PASS | 21 | 20.5 | SITE7_BOSS_ROOM_FAIRNESS: PASS (21 checks) res://qa/regression_runs/20261006_182512_quick/out/boss_room_fairness/room_fairness.json |
| robot_roster | PASS | 302 | 9.2 | SITE7_ROBOT_ROSTER: PASS / 302 checks |
| enemy_facing | PASS | 224 | 3.4 | SITE7_ENEMY_FACING_SMOKE: PASS (224 checks) |
| machine_source | PASS | 436 | 2.6 | SITE7_MACHINE_SOURCE_SMOKE: PASS (436 checks) |
| emission_owner | PASS | 1293 | 5.4 | SITE7_EMISSION_OWNER_SMOKE: PASS (1293 checks) res://qa/regression_runs/20261006_182512_quick/out/emission_owner |
| m2_story | PASS | 27 | 6.0 | M2_STORY_FLOW_SMOKE: PASS |
| m9_skill | PASS | 44 | 5.2 | M9_OPERATOR_SKILL_SYNERGY_SMOKE: PASS |
| m10_base_ui | PASS | 10 | 1.0 | M10_BASE_UI_ACTION_SMOKE: PASS |
| m10_persistence | PASS | 27 | 1.0 | M10_PERSISTENCE_SMOKE: PASS |
| run_contract | PASS | 34 | 6.4 | M11_RUN_CONTRACT_SMOKE: PASS |
| contract_offers | PASS | 26950 | 2.4 | RUN_CONTRACT_OFFERS_SMOKE: PASS (26950 checks) |
| contract_ui | PASS | 484 | 10.1 | RUN_CONTRACT_UI_SMOKE: PASS (484 checks) |
| redline | PASS | 78 | 5.8 | REDLINE_SMOKE: PASS (78 checks) |
| contract_save | PASS | 175 | 0.8 | RUN_CONTRACT_SAVE_SMOKE: PASS (175 checks) |
| intel_supply | PASS | 83 | 2.0 | INTEL_SUPPLY_SMOKE: PASS (83 checks) |
| module_expansion | PASS | 86 | 3.6 | MODULE_EXPANSION_SMOKE: PASS (86 checks) |
| weapon_expansion | PASS | 131 | 3.8 | WEAPON_EXPANSION_SMOKE: PASS (131 checks) |
| lab_geometry | PASS | 4005 | 6.2 | LAB_GEOMETRY_SMOKE: PASS (4005 checks) |
| m12_revive | PASS | 25 | 4.8 | M12_SQUAD_REVIVE_SMOKE: PASS |
| play_log | PASS | 25 | 6.8 | PLAY_SESSION_LOG_SMOKE: PASS (25 checks) res://qa/regression_runs/20261006_182512_quick/out/play_log |
| hit_hurt_vfx | PASS | 47 | 3.0 | COMBAT_HIT_HURT_VFX_SMOKE: PASS (47 checks) |
| combat_vfx | PASS | 195 | 3.8 | COMBAT_VFX_OVERHAUL_SMOKE: PASS (195 checks) |
| elite_affix | PASS | 71 | 5.2 | ELITE_AFFIX_SMOKE: PASS (71 checks) |
| elite_expansion | PASS | 438 | 7.8 | ELITE_EXPANSION_SMOKE: PASS (438 checks) |
| zone_hazard | PASS | 366 | 50.7 | ZONE_HAZARD_SMOKE: PASS (366 checks, 15 rooms) |
| hazard_expansion | PASS | 438 | 29.1 | HAZARD_EXPANSION_SMOKE: PASS (438 checks, 15 rooms) res://qa/regression_runs/20261006_182512_quick/out/hazard_expansion/hazard_expansion.json |
| firing_lane | PASS | 325 | 28.1 | FIRING_LANE_SEARCH_SMOKE: PASS (325 checks) |
| platform_carry | PASS | 6 | 6.0 | ACTOR_PLATFORM_CARRY_SMOKE: PASS (6 checks) |
| contact_carry | PASS | 27 | 15.2 | ACTOR_CONTACT_CARRY_SMOKE: PASS (27 checks) |
| world_layout | PASS | - | 17.1 | SITE7_WORLD_LAYOUT PASS 10 missions |
| mood_light | PASS | - | 76.8 | SITE7_MOOD_LIGHT PASS 150 plates 788 pools 150 void masks 15 contact shadows |
| walk_registration | PASS | - | 1.4 | WALK_TORSO_REGISTRATION PASS |
| plate_axis | PASS | 2 | 2.8 | OK |
| variety_placement | PASS | 10 | 1.4 | OK |
| seam_waiver | PASS | 10 | 2.2 | OK |
| mood_contact | PASS | 13 | 3.0 | OK |
| deploy_warmer | PASS | 83 | 9.7 | DEPLOY_WARMER_SMOKE: PASS (83 checks) |
| m13_migration | PASS | 9 | 1.0 | M13_WEAPON_BASE_MIGRATION_SMOKE: PASS |
| m13_campaign | PASS | 16 | 0.6 | M13_WEAPON_CAMPAIGN_SMOKE: PASS |
| m13_runtime | PASS | 18 | 6.8 | M13_WEAPON_RUNTIME_SMOKE: PASS |

## 기존 QA 기록 보호

- `qa/`, `motion_lab_v1/qa/`의 기존 파일 변경·삭제·추가 0건
