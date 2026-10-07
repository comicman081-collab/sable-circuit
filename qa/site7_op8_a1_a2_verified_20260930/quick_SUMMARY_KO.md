# 회귀 실행 20260930_194406_quick

- 결과: **PASS** (44/44 PASS)
- 묶음: quick · 커밋: `2d7a51a9a9` (작업 트리 변경 21개)
- 시작 2026-09-30T19:44:06 · 소요 424초

| 테스트 | 결과 | 체크 수 | 시간(초) | 비고 |
|---|---|---:|---:|---|
| combat_density | PASS | 55 | 18.8 | COMBAT_DENSITY_SMOKE PASS (55 checks) {"attacks_started":32,"drone_orbit_split":[2,2],"frames_with_two_or_more_attackers":354,"hostiles":7,"max_concurrent_attac |
| cover_navigation | PASS | 15 | 1.8 | COVER_NAVIGATION_SMOKE: PASS / 15 checks |
| floor_segment | PASS | 19 | 36.1 | FLOOR_SEGMENT_SMOKE: PASS (19 checks) |
| combat_query_fastpath | PASS | 31 | 12.0 | COMBAT_QUERY_FASTPATH_SMOKE: PASS (31 checks) |
| player_cover | PASS | 5 | 8.0 | SITE7_PLAYER_COVER_COLLISION: PASS (5 checks) |
| cover_alpha_clip | PASS | 5 | 1.8 | SITE7_COVER_ALPHA_CLIP: PASS / 5 checks |
| cover_texture | PASS | 17 | 2.6 | COVER_TEXTURE_REDUCTION_SMOKE: PASS (17 checks) 63.3 MB -> 10.2 MB |
| battle_flow | PASS | - | 9.6 | SITE7_BATTLE_FLOW: PASS |
| combat_entry | PASS | - | 7.4 |  |
| drone_app | PASS | 171 | 3.8 | SITE7_DRONE_APP_SMOKE: PASS (171 checks) res://qa/regression_runs/20260930_194406_quick/out/drone_app/drone_app.json |
| anchor_app | PASS | 271 | 2.6 | SITE7_ANCHOR_APP_SMOKE: PASS (271 checks) res://qa/regression_runs/20260930_194406_quick/out/anchor_app/anchor_app.json |
| campaign_data | PASS | 279 | 0.6 | SITE7_CAMPAIGN_DATA: PASS (279 checks) |
| upgrade_economy | PASS | 225 | 1.6 | UPGRADE_ECONOMY: PASS (225 checks) |
| boss_registry | PASS | 160 | 11.0 | SITE7_BOSS_REGISTRY_SMOKE: PASS (160 checks) |
| boss_pattern | PASS | 959 | 3.6 | SITE7_BOSS_PATTERN_SMOKE: PASS (959 checks) res://qa/regression_runs/20260930_194406_quick/out/boss_pattern/pattern.json |
| boss_duel | PASS | 1124 | 37.3 | SITE7_BOSS_DUEL_SMOKE: PASS (1124 checks) res://qa/regression_runs/20260930_194406_quick/out/boss_duel/duel.json |
| boss_room_fairness | PASS | 9 | 10.0 | SITE7_BOSS_ROOM_FAIRNESS: PASS (9 checks) res://qa/regression_runs/20260930_194406_quick/out/boss_room_fairness/room_fairness.json |
| robot_roster | PASS | 302 | 10.4 | SITE7_ROBOT_ROSTER: PASS / 302 checks |
| enemy_facing | PASS | 224 | 3.0 | SITE7_ENEMY_FACING_SMOKE: PASS (224 checks) |
| machine_source | PASS | 436 | 3.0 | SITE7_MACHINE_SOURCE_SMOKE: PASS (436 checks) |
| emission_owner | PASS | 1293 | 6.0 | SITE7_EMISSION_OWNER_SMOKE: PASS (1293 checks) res://qa/regression_runs/20260930_194406_quick/out/emission_owner |
| m2_story | PASS | 27 | 7.2 | M2_STORY_FLOW_SMOKE: PASS |
| m9_skill | PASS | 44 | 5.2 | M9_OPERATOR_SKILL_SYNERGY_SMOKE: PASS |
| m10_base_ui | PASS | 10 | 0.8 | M10_BASE_UI_ACTION_SMOKE: PASS |
| m10_persistence | PASS | 27 | 0.6 | M10_PERSISTENCE_SMOKE: PASS |
| m12_revive | PASS | 25 | 6.2 | M12_SQUAD_REVIVE_SMOKE: PASS |
| play_log | PASS | 23 | 7.4 | PLAY_SESSION_LOG_SMOKE: PASS (23 checks) res://qa/regression_runs/20260930_194406_quick/out/play_log |
| hit_hurt_vfx | PASS | 47 | 3.8 | COMBAT_HIT_HURT_VFX_SMOKE: PASS (47 checks) |
| combat_vfx | PASS | 189 | 3.6 | COMBAT_VFX_OVERHAUL_SMOKE: PASS (189 checks) |
| elite_affix | PASS | 58 | 6.8 | ELITE_AFFIX_SMOKE: PASS (58 checks) |
| zone_hazard | PASS | 253 | 41.5 | ZONE_HAZARD_SMOKE: PASS (253 checks, 11 rooms) |
| firing_lane | PASS | 259 | 25.1 | FIRING_LANE_SEARCH_SMOKE: PASS (259 checks) |
| platform_carry | PASS | 6 | 6.4 | ACTOR_PLATFORM_CARRY_SMOKE: PASS (6 checks) |
| contact_carry | PASS | 27 | 15.0 | ACTOR_CONTACT_CARRY_SMOKE: PASS (27 checks) |
| world_layout | PASS | - | 11.2 | SITE7_WORLD_LAYOUT PASS 8 missions |
| mood_light | PASS | - | 57.3 | SITE7_MOOD_LIGHT PASS 120 plates 620 pools 120 void masks 15 contact shadows |
| walk_registration | PASS | - | 1.4 | WALK_TORSO_REGISTRATION PASS |
| plate_axis | PASS | 2 | 1.6 | OK |
| seam_waiver | PASS | 10 | 1.8 | OK |
| mood_contact | PASS | 5 | 0.6 | OK |
| deploy_warmer | PASS | 83 | 7.8 | DEPLOY_WARMER_SMOKE: PASS (83 checks) |
| m13_migration | PASS | 9 | 0.8 | M13_WEAPON_BASE_MIGRATION_SMOKE: PASS |
| m13_campaign | PASS | 16 | 0.8 | M13_WEAPON_CAMPAIGN_SMOKE: PASS |
| m13_runtime | PASS | 18 | 6.0 | M13_WEAPON_RUNTIME_SMOKE: PASS |

## 기존 QA 기록 보호

- `qa/`, `motion_lab_v1/qa/`의 기존 파일 변경·삭제·추가 0건
