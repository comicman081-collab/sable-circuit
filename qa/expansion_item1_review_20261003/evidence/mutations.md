# 규칙 깨기 표 (V-08) — Claude의 변형 14개

방법: 검수 대상 커밋 `a6eb1d35`의 작업 트리 사본(`.cache/claude_scratch/proj_after`)에서 한 번에 하나씩 코드·데이터를 고치고, 해당 시험을 돌린 뒤 `git show a6eb1d35:<파일>`로 원상 복구했다. 도구: `tools/mutate.py`.

| 변형 | 깬 규칙 | 시험 | 결과 | 시험의 한 줄 |
|---|---|---|---|---|
| `boss_accepts_affix` | V-02: `EliteAffix.apply`의 보스 거부 조건(`BOSS_` 접두사) 제거 | `elite_expansion_smoke.gd` | **CAUGHT** (exit 1) | ELITE_EXPANSION_SMOKE: FAIL (248 checks, 1 failures) — FAIL: boss refuses SHIELDED at application boundary / |
| `beacon_protects_itself` | V-06: BEACON이 자기 자신도 감쇠하게 함 | `elite_expansion_smoke.gd` | **CAUGHT** (exit 1) | ELITE_EXPANSION_SMOKE: FAIL (248 checks, 1 failures) — FAIL: a beacon does not protect itself / |
| `beacon_cap_removed_data_0_5` | V-06: `beacon_reduction`을 0.25 → 0.5로(상한 0.35 초과) | `elite_expansion_smoke.gd` | **CAUGHT** (exit 1) | ELITE_EXPANSION_SMOKE: FAIL (248 checks, 5 failures) — FAIL: beacon data stays inside reduction and link limits / |
| `brood_three_babies` | V-04/V-05: `brood_count` 2 → 3 | `elite_expansion_smoke.gd` | **CAUGHT** (exit 1) | ELITE_EXPANSION_SMOKE: FAIL (252 checks, 3 failures) — FAIL: both hatchlings are counted before the parent decrements / |
| `hatch_short_0_2` | V-04: `brood_hatch_windup` 0.6 → 0.2 | `elite_expansion_smoke.gd` | **CAUGHT** (exit 1) | ELITE_EXPANSION_SMOKE: FAIL (248 checks, 6 failures) — FAIL: hatch warning lasts at least 0.6 s / |
| `hatchling_fires_during_hatch` | V-04: 부화 중에도 공격하게 함 | `elite_expansion_smoke.gd` | **CAUGHT** (exit 1) | ELITE_EXPANSION_SMOKE: FAIL (248 checks, 4 failures) — FAIL: no projectile, legacy attack or normal controller attack during hatch / |
| `spore_damage_in_warning` | V-11: SPORE가 경고 구간에서도 지속 피해를 줌 | `hazard_expansion_smoke.gd` | **CAUGHT** (exit 1) | HAZARD_EXPANSION_SMOKE: FAIL (438 checks, 15 rooms) res://.cache/mut_report.json — FAIL: SPORE_CLOUD does no damage through the warning / |
| `spore_source_unattributed` | V-16: SPORE 피해 출처를 `HAZARD_SPORE_CLOUD` 대신 `HAZARD`로 기록 | `hazard_expansion_smoke.gd` | **CAUGHT** (exit 1) | HAZARD_EXPANSION_SMOKE: FAIL (438 checks, 15 rooms) res://.cache/mut_report.json — FAIL: SPORE_CLOUD attributes all operator damage / |
| `spore_warning_0_8` | V-13: SPORE 경고 1.2 → 0.8 s | `hazard_expansion_smoke.gd` | **CAUGHT** (exit 1) | HAZARD_EXPANSION_SMOKE: FAIL (438 checks, 15 rooms) res://.cache/mut_report.json — FAIL: SPORE_CLOUD innermost escape fits its warning at 138 px/s plus 0.25s / |
| `frost_cleanup_leaks` | V-18: 방 정리 때 `release_effects()`를 부르지 않아 서리 배율이 남음 | `hazard_expansion_smoke.gd` | **CAUGHT** (exit 1) | HAZARD_EXPANSION_SMOKE: FAIL (438 checks, 15 rooms) res://.cache/mut_report.json — FAIL: room cleanup removes frost and its factor in the same stack / |
| `dash_compounds_frost` | V-18: 대시 속도에 서리 배율을 현재 속도 기준으로 곱해 프레임마다 복리로 줄어듦 | `hazard_expansion_smoke.gd` | **CAUGHT** (exit 1) | HAZARD_EXPANSION_SMOKE: FAIL (438 checks, 15 rooms) res://.cache/mut_report.json — FAIL: SPACE dash uses 0.7 once and never compounds it on later frames / |
| `hazards_not_spread` | V-15: 배치 간격 규칙 2.6 × 반지름 → 0.5 × 반지름 | `hazard_expansion_smoke.gd` | **CAUGHT** (exit 1) | HAZARD_EXPANSION_SMOKE: FAIL (438 checks, 15 rooms) res://.cache/mut_report.json — FAIL: MIS_CH01_04 R04_LINE spreads mixed hazard bounding radii apart / |
| `hazards_not_spread` | V-15: 배치 간격 규칙 2.6 × 반지름 → 0.5 × 반지름 | `zone_hazard_smoke.gd` | **CAUGHT** (exit 1) | FAIL: MIS_CH01_04 R04_LINE: vents are spread apart | FAIL: MIS_CH01_04 R04_LINE: vents are spread apart | FAIL: MIS_CH01_05 R02_DEFENSE: vents are spread apart |  |
| `affix_tints_actor_modulate` | V-02: 변종이 루트 `EnemyActor.modulate`를 칠함 | `elite_expansion_smoke.gd` | **MISSED** (exit 0) | ELITE_EXPANSION_SMOKE: PASS (248 checks) |
| `affix_tints_sprite_modulate` | V-02: 변종이 스프라이트 `modulate`를 칠함 | `elite_expansion_smoke.gd` | **CAUGHT** (exit 1) | ELITE_EXPANSION_SMOKE: FAIL (248 checks, 10 failures) — FAIL: SHIELDED keeps common sprite material/modulation at HighResVisualRoot/UniqueMasterSprite / |

서로 다른 변형 14개 중 **13개 잡힘, 1개 놓침** (`affix_tints_actor_modulate`).

놓친 변형이 B-1이다: `elite_affix.gd`의 `apply`에서 `if affix_id == "BEACON": add_to_group("elite_beacons")` 바로 다음 줄에 `(get_parent() as CanvasItem).modulate = Color(0.7, 1.0, 0.7)`를 넣은 사본이 `ELITE_EXPANSION_SMOKE: PASS (248 checks)`다. 같은 줄을 스프라이트에 넣은 사본은 10개 실패한다. `hazards_not_spread`는 `hazard_expansion`과 `zone_hazard` 두 시험이 모두 잡았다(표의 두 줄).

## B-1 보강: 틴트를 *어디에* 거는가 (같은 시험 `elite_expansion_smoke.gd`, 수정 전 코드 `a6eb1d35`)

| 변형 | 칠한 노드 | 결과 |
|---|---|---|
| `affix_tints_sprite_modulate` | 스프라이트 `modulate` | **CAUGHT** (10 실패) |
| `affix_tints_sprite_self_modulate` | 스프라이트 `self_modulate` | **CAUGHT** (100 실패) |
| `affix_clears_sprite_material` | 스프라이트 `material`을 null로 | **CAUGHT** (10 실패) |
| `affix_tints_actor_modulate` | 루트 `EnemyActor.modulate` | **MISSED** (`PASS (248 checks)`) |
| `affix_tints_actor_self_modulate` | 루트 `EnemyActor.self_modulate` | **MISSED** (`PASS (248 checks)`) |
| `affix_tints_visual_root` | `HighResVisualRoot.modulate` (스프라이트의 부모 `Node2D`) | **MISSED** (`PASS (248 checks)`) |

스프라이트에 건 변형 3개는 모두 잡히고 조상 노드에 건 변형 3개는 모두 놓친다. 시험이 `Sprite2D` 노드만 보기 때문이다. 부모 노드의 `modulate`와 `self_modulate`는 자식 그림 전체에 곱해지므로 화면에서는 같은 틴트다. 원자료: `raw/mutations_main_results.json`(앞 14개), `raw/mutations_b1_extra_results.json`(위 6개 중 새 4개).

서로 다른 변형 18개 중 **15개 잡힘, 3개 놓침**(모두 B-1).
