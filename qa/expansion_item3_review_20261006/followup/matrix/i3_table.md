| 부순 곳 | 설명 | intel | module | weapon | lab | csave | m10p | m13mig | econ | m10ui | m10intel | m13load | campaign | labcap | hitvfx | m13camp | m13run | 잡은 시험 수 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `key_generic_boss_first` | enemy_key tests the generic BOSS branch before the five new bosses (all five become ANCHOR) | **21/83** |  |  |  |  |  |  |  |  | - |  | - |  |  |  |  | 1 |
| `key_old_chain` | enemy_key is the old three-key chain again (no new-boss lines) | **21/83** |  |  |  |  |  |  |  |  | - |  | - |  |  |  |  | 1 |
| `lost_three_keys` | lost_intel_samples sums only the three old keys | **5/83** |  |  |  |  |  |  |  |  | - |  | - |  |  |  |  | 1 |
| `intel_keys_campaign_three` | CampaignProgression.INTEL_KEYS is the three old keys (commit drops the new samples) | **6/83** |  |  |  | - | - | - |  |  | - |  | - |  |  |  |  | 1 |
| `intel_keys_stage_three` | StoryStage01.INTEL_KEYS is the three old keys (extraction secures only three) | **5/83** |  |  |  |  |  |  |  |  | - |  | - |  |  |  |  | 1 |
| `sanitize_three_keys` | _sanitize_intel reads only the three old keys (new samples dropped on commit and load) | **7/83** |  |  |  | - | - | - |  |  | - |  |  |  |  |  |  | 1 |
| `secured_skips_origin` | extraction leaves the ORIGIN sample out of secured_intel | **5/83** |  |  |  |  |  |  |  |  | - |  | - |  |  |  |  | 1 |
| `weapon_hit_profile_not_overridden` | _weapon_art_profile overrides only the projectile family, not hit_vfx_profile |  |  | **3/131** |  |  |  |  |  |  |  |  |  |  | - | - | - | 1 |
| `rail_damage_40` | RAIL CARBINE damage 40 instead of 22 (burst 105, sustained above 78) |  |  | **3/131** |  |  |  |  | - |  |  | **3/53** |  |  |  | - |  | 2 |
| `rail_unlock_removed` | the ANL_GANTRY_RAIL_MODEL -> RAIL CARBINE unlock rule is deleted |  |  | **3/131** |  |  |  | - |  |  |  | - |  |  |  |  |  | 1 |
| `null_unlock_removed` | the ANL_ORIGIN_NULL_MODEL -> NULL BREACHER unlock rule is deleted |  |  | **2/131** |  |  |  | - |  |  |  | - |  |  |  |  |  | 1 |
| `research_plus_52` | new research costs +52 (6,132 = exactly 1.5x: boundary, expected to PASS) |  |  |  |  |  |  |  | - |  | - |  |  |  |  |  |  | 0 |
| `research_plus_53` | new research costs +53 (6,133 = 1.5002x: expected to FAIL) |  |  |  |  |  |  |  | **1/225** |  | - |  |  |  |  |  |  | 1 |
| `research_plus_60` | new research costs +60 (6,140 = 1.502x) |  |  |  |  |  |  |  | **1/225** |  | - |  |  |  |  |  |  | 1 |
| `mod_frost_lens_off` | FROST LENS hook never fires |  | **1/86** |  |  |  |  |  |  |  | - |  |  |  |  |  |  | 1 |
| `mod_rail_spool_cooldown_off` | RAIL SPOOL cooldown hook never fires |  | **1/86** |  |  |  |  |  |  |  | - |  |  |  |  |  |  | 1 |
| `mod_rail_spool_distance_off` | RAIL SPOOL distance hook never fires |  | **1/86** |  |  |  |  |  |  |  | - |  |  |  |  |  |  | 1 |
| `mod_spore_filter_off` | SPORE FILTER hook never fires |  | **1/86** |  |  |  |  |  |  |  | - |  |  |  |  |  |  | 1 |
| `mod_echo_relay_off` | ECHO RELAY hook never fires |  | **1/86** |  |  |  |  |  |  |  | - |  |  |  |  |  |  | 1 |
| `mod_null_anchor_off` | NULL ANCHOR hook never fires |  | **1/86** |  |  |  |  |  |  |  | - |  |  |  |  |  |  | 1 |
| `results_rail_old_position` | T-1: the COMMAND rail is back at y 404, 88 px (touches the INTEL line) |  |  |  | **2/4005** |  |  |  |  |  |  |  |  |  |  |  |  | 1 |
| `lab_effect_font_9` | T-3: analysis effect text capped at 9 px (fits, but below the 10 px floor) |  |  |  | **32/4005** |  |  |  |  |  |  |  |  |  |  |  |  | 1 |
| `lab_status_overlap` | the lab status label is moved onto the heading |  |  |  | **15/4005** |  |  |  |  | - |  |  |  |  |  |  |  | 1 |
| `cache_ignores_weapon_change` | T-4: the cached shot profile is not rebuilt when the weapon row changes |  |  | **6/131** |  |  |  |  |  |  |  |  |  |  |  |  |  | 1 |
| `cache_ignores_art_replace` | T-4: the cached shot profile is not rebuilt when the operator profile is replaced |  |  | **3/131** |  |  |  |  |  |  |  |  |  |  |  |  |  | 1 |
| `per_shot_copy_restored` | T-4 undone: a fresh deep copy for every shot (the old behaviour, same values) |  |  | **3/131** |  |  |  |  |  |  |  |  |  |  |  |  |  | 1 |

칸: `-` 통과(못 잡음), `n/T` 변형 없는 실행의 전체 T개 중 n개 검사가 실패(잡음), `SE` 스크립트 오류로 멈춤, `HANG` 스크립트 오류 뒤 종료하지 못하고 시간 제한에서 중단(러너는 TIMEOUT으로 빨갛게 표시), 빈칸은 그 변형이 해당 시험을 돌리지 않음. 마지막 열은 SE·HANG을 포함해 빨갛게 된 시험 수.

기준(변형 없음) 줄의 `ERROR:` 개수: 모두 0
기준 줄의 전체 검사 수: intel 83, module 86, weapon 131, lab 4005, csave 175, m10p 27, m13mig 9, econ 225, m10ui 10, m10intel 39, m13load 53, campaign 235, labcap 5, hitvfx 47, m13camp 16, m13run 18

아무 시험도 못 잡은 변형 1개: `capture_wait_1s`
경계 확인 `research_plus_52`: 잡힌 시험 0개 (0이어야 정상)
