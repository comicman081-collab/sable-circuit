# 회귀 실행 20261001_211310_quick

- 결과: **PASS** (44/44 PASS)
- 묶음: quick · 커밋: `f0edcfbf53` (작업 트리 변경 61개)
- 시작 2026-10-01T21:14:23 · 소요 443초

| 테스트 | 결과 | 체크 수 | 시간(초) | 비고 |
|---|---|---:|---:|---|
| combat_density | PASS | 67 | 19.0 | COMBAT_DENSITY_SMOKE PASS (67 checks) {"attacks_started":32,"drone_orbit_split":[2,2],"frames_with_two_or_more_attackers":305,"hostiles":7,"max_concurrent_attac |
| cover_navigation | PASS | 15 | 1.6 | COVER_NAVIGATION_SMOKE: PASS / 15 checks |
| floor_segment | PASS | 23 | 38.5 | FLOOR_SEGMENT_SMOKE: PASS (23 checks) |
| combat_query_fastpath | PASS | 31 | 10.8 | COMBAT_QUERY_FASTPATH_SMOKE: PASS (31 checks) |
| player_cover | PASS | 5 | 7.2 | SITE7_PLAYER_COVER_COLLISION: PASS (5 checks) |
| cover_alpha_clip | PASS | 5 | 1.6 | SITE7_COVER_ALPHA_CLIP: PASS / 5 checks |
| cover_texture | PASS | 17 | 2.4 | COVER_TEXTURE_REDUCTION_SMOKE: PASS (17 checks) 63.3 MB -> 10.2 MB |
| battle_flow | PASS | - | 9.2 | SITE7_BATTLE_FLOW: PASS |
| combat_entry | PASS | - | 7.0 |  |
| drone_app | PASS | 171 | 2.0 | SITE7_DRONE_APP_SMOKE: PASS (171 checks) res://qa/regression_runs/20261001_211310_quick/out/drone_app/drone_app.json |
| anchor_app | PASS | 271 | 1.8 | SITE7_ANCHOR_APP_SMOKE: PASS (271 checks) res://qa/regression_runs/20261001_211310_quick/out/anchor_app/anchor_app.json |
| campaign_data | PASS | 297 | 0.6 | SITE7_CAMPAIGN_DATA: PASS (297 checks) |
| upgrade_economy | PASS | 225 | 1.6 | UPGRADE_ECONOMY: PASS (225 checks) |
| boss_registry | PASS | 162 | 13.6 | SITE7_BOSS_REGISTRY_SMOKE: PASS (162 checks) |
| boss_pattern | PASS | 978 | 3.0 | SITE7_BOSS_PATTERN_SMOKE: PASS (978 checks) res://qa/regression_runs/20261001_211310_quick/out/boss_pattern/pattern.json |
| boss_duel | PASS | 1124 | 36.9 | SITE7_BOSS_DUEL_SMOKE: PASS (1124 checks) res://qa/regression_runs/20261001_211310_quick/out/boss_duel/duel.json |
| boss_room_fairness | PASS | 17 | 14.2 | SITE7_BOSS_ROOM_FAIRNESS: PASS (17 checks) res://qa/regression_runs/20261001_211310_quick/out/boss_room_fairness/room_fairness.json |
| robot_roster | PASS | 302 | 7.8 | SITE7_ROBOT_ROSTER: PASS / 302 checks |
| enemy_facing | PASS | 224 | 2.8 | SITE7_ENEMY_FACING_SMOKE: PASS (224 checks) |
| machine_source | PASS | 436 | 2.0 | SITE7_MACHINE_SOURCE_SMOKE: PASS (436 checks) |
| emission_owner | PASS | 1293 | 4.2 | SITE7_EMISSION_OWNER_SMOKE: PASS (1293 checks) res://qa/regression_runs/20261001_211310_quick/out/emission_owner |
| m2_story | PASS | 27 | 5.0 | M2_STORY_FLOW_SMOKE: PASS |
| m9_skill | PASS | 44 | 4.4 | M9_OPERATOR_SKILL_SYNERGY_SMOKE: PASS |
| m10_base_ui | PASS | 10 | 0.8 | M10_BASE_UI_ACTION_SMOKE: PASS |
| m10_persistence | PASS | 27 | 0.6 | M10_PERSISTENCE_SMOKE: PASS |
| m12_revive | PASS | 25 | 4.4 | M12_SQUAD_REVIVE_SMOKE: PASS |
| play_log | PASS | 23 | 5.8 | PLAY_SESSION_LOG_SMOKE: PASS (23 checks) res://qa/regression_runs/20261001_211310_quick/out/play_log |
| hit_hurt_vfx | PASS | 47 | 2.4 | COMBAT_HIT_HURT_VFX_SMOKE: PASS (47 checks) |
| combat_vfx | PASS | 189 | 2.6 | COMBAT_VFX_OVERHAUL_SMOKE: PASS (189 checks) |
| elite_affix | PASS | 69 | 4.6 | ELITE_AFFIX_SMOKE: PASS (69 checks) |
| zone_hazard | PASS | 345 | 48.9 | ZONE_HAZARD_SMOKE: PASS (345 checks, 15 rooms) |
| firing_lane | PASS | 325 | 30.7 | FIRING_LANE_SEARCH_SMOKE: PASS (325 checks) |
| platform_carry | PASS | 6 | 6.4 | ACTOR_PLATFORM_CARRY_SMOKE: PASS (6 checks) |
| contact_carry | PASS | 27 | 15.8 | ACTOR_CONTACT_CARRY_SMOKE: PASS (27 checks) |
| world_layout | PASS | - | 13.8 | SITE7_WORLD_LAYOUT PASS 10 missions |
| mood_light | PASS | - | 72.4 | SITE7_MOOD_LIGHT PASS 150 plates 788 pools 150 void masks 15 contact shadows |
| walk_registration | PASS | - | 2.4 | WALK_TORSO_REGISTRATION PASS |
| plate_axis | PASS | 2 | 3.2 | OK |
| seam_waiver | PASS | 10 | 2.0 | OK |
| mood_contact | PASS | 5 | 1.0 | OK |
| deploy_warmer | PASS | 83 | 7.4 | DEPLOY_WARMER_SMOKE: PASS (83 checks) |
| m13_migration | PASS | 9 | 0.8 | M13_WEAPON_BASE_MIGRATION_SMOKE: PASS |
| m13_campaign | PASS | 16 | 0.6 | M13_WEAPON_CAMPAIGN_SMOKE: PASS |
| m13_runtime | PASS | 18 | 4.6 | M13_WEAPON_RUNTIME_SMOKE: PASS |

## 기존 QA 기록 보호

- `qa/`, `motion_lab_v1/qa/`의 기존 파일 변경·삭제·추가 0건
