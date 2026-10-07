# 회귀 실행 20260928_000111_quick

- 결과: **PASS** (34/34 PASS)
- 묶음: quick · 커밋: `4ab553d192` (작업 트리 변경 16개)
- 시작 2026-09-28T00:02:27 · 소요 270초

| 테스트 | 결과 | 체크 수 | 시간(초) | 비고 |
|---|---|---:|---:|---|
| combat_density | PASS | 37 | 21.6 | COMBAT_DENSITY_SMOKE PASS (37 checks) {"attacks_started":32,"drone_orbit_split":[2,2],"frames_with_two_or_more_attackers":354,"hostiles":7,"max_concurrent_attac |
| cover_navigation | PASS | 15 | 2.3 | COVER_NAVIGATION_SMOKE: PASS / 15 checks |
| floor_segment | PASS | 13 | 31.3 | FLOOR_SEGMENT_SMOKE: PASS (13 checks) |
| combat_query_fastpath | PASS | 31 | 12.7 | COMBAT_QUERY_FASTPATH_SMOKE: PASS (31 checks) |
| player_cover | PASS | 5 | 8.3 | SITE7_PLAYER_COVER_COLLISION: PASS (5 checks) |
| cover_alpha_clip | PASS | 5 | 1.8 | SITE7_COVER_ALPHA_CLIP: PASS / 5 checks |
| cover_texture | PASS | 17 | 3.2 | COVER_TEXTURE_REDUCTION_SMOKE: PASS (17 checks) 63.3 MB -> 10.2 MB |
| battle_flow | PASS | - | 7.2 | SITE7_BATTLE_FLOW: PASS |
| combat_entry | PASS | - | 6.2 |  |
| drone_app | PASS | 171 | 2.8 | SITE7_DRONE_APP_SMOKE: PASS (171 checks) res://qa/regression_runs/20260928_000111_quick/out/drone_app/drone_app.json |
| anchor_app | PASS | 271 | 2.4 | SITE7_ANCHOR_APP_SMOKE: PASS (271 checks) res://qa/regression_runs/20260928_000111_quick/out/anchor_app/anchor_app.json |
| enemy_facing | PASS | 224 | 3.2 | SITE7_ENEMY_FACING_SMOKE: PASS (224 checks) |
| machine_source | PASS | 436 | 3.1 | SITE7_MACHINE_SOURCE_SMOKE: PASS (436 checks) |
| emission_owner | PASS | 870 | 5.5 | SITE7_EMISSION_OWNER_SMOKE: PASS (870 checks) res://qa/regression_runs/20260928_000111_quick/out/emission_owner |
| m2_story | PASS | 27 | 6.7 | M2_STORY_FLOW_SMOKE: PASS |
| m9_skill | PASS | 44 | 6.1 | M9_OPERATOR_SKILL_SYNERGY_SMOKE: PASS |
| m10_base_ui | PASS | 10 | 1.0 | M10_BASE_UI_ACTION_SMOKE: PASS |
| m10_persistence | PASS | 27 | 0.6 | M10_PERSISTENCE_SMOKE: PASS |
| m12_revive | PASS | 25 | 5.7 | M12_SQUAD_REVIVE_SMOKE: PASS |
| play_log | PASS | 23 | 7.3 | PLAY_SESSION_LOG_SMOKE: PASS (23 checks) res://qa/regression_runs/20260928_000111_quick/out/play_log |
| hit_hurt_vfx | PASS | 47 | 3.2 | COMBAT_HIT_HURT_VFX_SMOKE: PASS (47 checks) |
| combat_vfx | PASS | 154 | 3.2 | COMBAT_VFX_OVERHAUL_SMOKE: PASS (154 checks) |
| elite_affix | PASS | 43 | 5.9 | ELITE_AFFIX_SMOKE: PASS (43 checks) |
| zone_hazard | PASS | 115 | 23.6 | ZONE_HAZARD_SMOKE: PASS (115 checks, 5 rooms) |
| firing_lane | PASS | 163 | 19.4 | FIRING_LANE_SEARCH_SMOKE: PASS (163 checks) |
| platform_carry | PASS | 6 | 7.1 | ACTOR_PLATFORM_CARRY_SMOKE: PASS (6 checks) |
| contact_carry | PASS | 27 | 16.8 | ACTOR_CONTACT_CARRY_SMOKE: PASS (27 checks) |
| world_layout | PASS | - | 6.0 | SITE7_WORLD_LAYOUT PASS 5 missions |
| mood_light | PASS | - | 24.3 | SITE7_MOOD_LIGHT PASS 61 plates 349 pools 61 void masks |
| walk_registration | PASS | - | 1.0 | WALK_TORSO_REGISTRATION PASS |
| deploy_warmer | PASS | 76 | 6.4 | DEPLOY_WARMER_SMOKE: PASS (76 checks) |
| m13_migration | PASS | 9 | 0.6 | M13_WEAPON_BASE_MIGRATION_SMOKE: PASS |
| m13_campaign | PASS | 16 | 0.4 | M13_WEAPON_CAMPAIGN_SMOKE: PASS |
| m13_runtime | PASS | 18 | 4.4 | M13_WEAPON_RUNTIME_SMOKE: PASS |

## 기존 QA 기록 보호

- `qa/`, `motion_lab_v1/qa/`의 기존 파일 변경·삭제·추가 0건
