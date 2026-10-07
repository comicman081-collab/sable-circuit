# 회귀 실행 20261004_215901_quick

- 결과: **PASS** (52/52 PASS)
- 묶음: quick · 커밋: `f2cbe1d653` (작업 트리 변경 2개)
- 시작 2026-10-04T21:59:01 · 소요 563초

| 테스트 | 결과 | 체크 수 | 시간(초) | 비고 |
|---|---|---:|---:|---|
| combat_density | PASS | 67 | 18.8 | COMBAT_DENSITY_SMOKE PASS (67 checks) {"attacks_started":29,"drone_orbit_split":[2,2],"frames_with_two_or_more_attackers":292,"hostiles":7,"max_concurrent_attac |
| cover_navigation | PASS | 43 | 20.7 | COVER_NAVIGATION_SMOKE: PASS / 43 checks |
| floor_segment | PASS | 23 | 42.5 | FLOOR_SEGMENT_SMOKE: PASS (23 checks) |
| combat_query_fastpath | PASS | 34 | 13.2 | COMBAT_QUERY_FASTPATH_SMOKE: PASS (34 checks) |
| player_cover | PASS | 5 | 7.6 | SITE7_PLAYER_COVER_COLLISION: PASS (5 checks) |
| cover_alpha_clip | PASS | 5 | 2.0 | SITE7_COVER_ALPHA_CLIP: PASS / 5 checks |
| cover_texture | PASS | 17 | 2.6 | COVER_TEXTURE_REDUCTION_SMOKE: PASS (17 checks) 63.3 MB -> 10.2 MB |
| battle_flow | PASS | - | 9.0 | SITE7_BATTLE_FLOW: PASS |
| combat_entry | PASS | - | 7.4 |  |
| drone_app | PASS | 171 | 2.4 | SITE7_DRONE_APP_SMOKE: PASS (171 checks) res://qa/regression_runs/20261004_215901_quick/out/drone_app/drone_app.json |
| anchor_app | PASS | 271 | 1.8 | SITE7_ANCHOR_APP_SMOKE: PASS (271 checks) res://qa/regression_runs/20261004_215901_quick/out/anchor_app/anchor_app.json |
| campaign_data | PASS | 292 | 0.6 | SITE7_CAMPAIGN_DATA: PASS (292 checks) |
| upgrade_economy | PASS | 225 | 1.6 | UPGRADE_ECONOMY: PASS (225 checks) |
| boss_registry | PASS | 163 | 15.5 | SITE7_BOSS_REGISTRY_SMOKE: PASS (163 checks) |
| boss_pattern | PASS | 978 | 3.2 | SITE7_BOSS_PATTERN_SMOKE: PASS (978 checks) res://qa/regression_runs/20261004_215901_quick/out/boss_pattern/pattern.json |
| boss_duel | PASS | 2184 | 55.9 | SITE7_BOSS_DUEL_SMOKE: PASS (2184 checks) res://qa/regression_runs/20261004_215901_quick/out/boss_duel/duel.json |
| boss_room_fairness | PASS | 21 | 18.0 | SITE7_BOSS_ROOM_FAIRNESS: PASS (21 checks) res://qa/regression_runs/20261004_215901_quick/out/boss_room_fairness/room_fairness.json |
| robot_roster | PASS | 302 | 8.8 | SITE7_ROBOT_ROSTER: PASS / 302 checks |
| enemy_facing | PASS | 224 | 2.8 | SITE7_ENEMY_FACING_SMOKE: PASS (224 checks) |
| machine_source | PASS | 436 | 2.6 | SITE7_MACHINE_SOURCE_SMOKE: PASS (436 checks) |
| emission_owner | PASS | 1293 | 5.2 | SITE7_EMISSION_OWNER_SMOKE: PASS (1293 checks) res://qa/regression_runs/20261004_215901_quick/out/emission_owner |
| m2_story | PASS | 27 | 5.6 | M2_STORY_FLOW_SMOKE: PASS |
| m9_skill | PASS | 44 | 4.8 | M9_OPERATOR_SKILL_SYNERGY_SMOKE: PASS |
| m10_base_ui | PASS | 10 | 1.0 | M10_BASE_UI_ACTION_SMOKE: PASS |
| m10_persistence | PASS | 27 | 0.6 | M10_PERSISTENCE_SMOKE: PASS |
| run_contract | PASS | 34 | 5.8 | M11_RUN_CONTRACT_SMOKE: PASS |
| contract_offers | PASS | 26950 | 2.0 | RUN_CONTRACT_OFFERS_SMOKE: PASS (26950 checks) |
| contract_ui | PASS | 484 | 8.8 | RUN_CONTRACT_UI_SMOKE: PASS (484 checks) |
| redline | PASS | 77 | 5.2 | REDLINE_SMOKE: PASS (77 checks) |
| contract_save | PASS | 69 | 0.8 | RUN_CONTRACT_SAVE_SMOKE: PASS (69 checks) |
| m12_revive | PASS | 25 | 4.8 | M12_SQUAD_REVIVE_SMOKE: PASS |
| play_log | PASS | 25 | 6.2 | PLAY_SESSION_LOG_SMOKE: PASS (25 checks) res://qa/regression_runs/20261004_215901_quick/out/play_log |
| hit_hurt_vfx | PASS | 47 | 2.8 | COMBAT_HIT_HURT_VFX_SMOKE: PASS (47 checks) |
| combat_vfx | PASS | 189 | 3.0 | COMBAT_VFX_OVERHAUL_SMOKE: PASS (189 checks) |
| elite_affix | PASS | 71 | 5.4 | ELITE_AFFIX_SMOKE: PASS (71 checks) |
| elite_expansion | PASS | 438 | 7.4 | ELITE_EXPANSION_SMOKE: PASS (438 checks) |
| zone_hazard | PASS | 366 | 48.1 | ZONE_HAZARD_SMOKE: PASS (366 checks, 15 rooms) |
| hazard_expansion | PASS | 438 | 25.1 | HAZARD_EXPANSION_SMOKE: PASS (438 checks, 15 rooms) res://qa/regression_runs/20261004_215901_quick/out/hazard_expansion/hazard_expansion.json |
| firing_lane | PASS | 325 | 27.7 | FIRING_LANE_SEARCH_SMOKE: PASS (325 checks) |
| platform_carry | PASS | 6 | 5.8 | ACTOR_PLATFORM_CARRY_SMOKE: PASS (6 checks) |
| contact_carry | PASS | 27 | 14.4 | ACTOR_CONTACT_CARRY_SMOKE: PASS (27 checks) |
| world_layout | PASS | - | 17.2 | SITE7_WORLD_LAYOUT PASS 10 missions |
| mood_light | PASS | - | 77.0 | SITE7_MOOD_LIGHT PASS 150 plates 788 pools 150 void masks 15 contact shadows |
| walk_registration | PASS | - | 1.2 | WALK_TORSO_REGISTRATION PASS |
| plate_axis | PASS | 2 | 2.8 | OK |
| variety_placement | PASS | 10 | 1.6 | OK |
| seam_waiver | PASS | 10 | 2.2 | OK |
| mood_contact | PASS | 13 | 3.0 | OK |
| deploy_warmer | PASS | 83 | 7.2 | DEPLOY_WARMER_SMOKE: PASS (83 checks) |
| m13_migration | PASS | 9 | 0.8 | M13_WEAPON_BASE_MIGRATION_SMOKE: PASS |
| m13_campaign | PASS | 16 | 0.6 | M13_WEAPON_CAMPAIGN_SMOKE: PASS |
| m13_runtime | PASS | 18 | 5.0 | M13_WEAPON_RUNTIME_SMOKE: PASS |

## 기존 QA 기록 보호

- `qa/`, `motion_lab_v1/qa/`의 기존 파일 변경·삭제·추가 0건
