| 부순 곳 | 설명 | offers | ui | redline | save | m11 | playlog | duel | campaign | 잡은 시험 수 |
|---|---|---|---|---|---|---|---|---|---|---|
| `offers_random` | offers: the alternative pair is chosen by randi() (not deterministic) | **413/26950** | **1/484** | - | - | - | - |  |  | 2 |
| `offers_default_last` | offers: the shipped default is returned last, not first | **640/26950** | **2/484** | - | - | - | - |  |  | 2 |
| `offers_dup_pair` | offers: the third offer repeats the default pair | **640/25654** | - | - | - | - | - |  |  | 1 |
| `offers_reward_flat` | offers: alternatives lose their hazard reward (risk no longer pays) | **1275/26950** | - | - | - | - | - |  |  | 1 |
| `offers_no_hazard_stats` | offers: alternatives keep the default's enemy multipliers (only the label changes) | - | - | - | - | - | - |  |  | 0 |
| `redline_reward_low` | REDLINE reward 1.0 (not above the offers) | **1350/26950** | **1/484** | **1/77** | - | - | - |  |  | 3 |
| `redline_reward_high` | REDLINE hazard reward 1.70 (above the 1.6 proposal range) | **1/26950** | **1/484** | **1/77** | - | - | - |  |  | 3 |
| `redline_hp_high` | REDLINE HP 1.60 (above the 1.5 proposal range) | **1/26950** | - | **7/77** | - | - | - |  |  | 2 |
| `redline_interval_low` | REDLINE attack interval 0.70 (below the 0.80 proposal range) | **1/26950** | - | **6/77** | - | - | - |  |  | 2 |
| `redline_speed_high` | REDLINE speed 1.30 (above the 1.15 proposal range) | **1/26950** | - | **6/77** | - | - | - |  |  | 2 |
| `redline_dmg_high` | REDLINE damage 1.60 (above the 1.35 proposal range) | **1/26950** | - | **14/77** | - | - | - |  |  | 2 |
| `redline_always_available` | redline_available() is always true | - | **1/490** | **6/77** | - | - | - |  |  | 2 |
| `redline_ignores_clear` | redline_available() only needs the operation to be unlocked, not cleared | - | **1/490** | **4/77** | - | - | - |  |  | 2 |
| `boss_not_exempt` | bosses get REDLINE speed and attack interval too | - | - | **2/77** | - | - | - | **61/2184** |  | 2 |
| `boss_hp_exempt` | bosses get no REDLINE HP | - | - | **1/77** | - | - | - | **10/2184** |  | 2 |
| `boss_dmg_exempt` | bosses get no REDLINE damage | - | - | **2/77** | - | - | - | **80/2184** |  | 2 |
| `boss_prefix_other` | the boss test looks for an 'ENM_' prefix instead of 'BOSS_' | - | - | **18/77** | - | - | - | **61/2184** |  | 2 |
| `double_apply` | the modifiers are applied twice at every encounter spawn (Codex's own control) | - | - | **7/77** | - | **1/?** | - | - |  | 2 |
| `mode_ids_dropped` | the stage forgets to pass hazard/opportunity ids, so REDLINE is never recognised per enemy | - | - | **2/77** | - | - | - | - |  | 1 |
| `reward_research_skipped` | the research reward multiplier is never applied | - | - | **2/77** | - | **1/?** | - |  |  | 2 |
| `reward_clamp_raised` | the stage reward clamp is raised 4.0 -> 8.0 (a limit raised) | - | - | **1/77** | - | - | - |  |  | 1 |
| `deploy_off_by_one` | deploy takes choice index+1 (the untouched default would not be the default) | - | **2/484** | - | - | - | - |  |  | 1 |
| `deploy_redline_unvalidated` | deploy_mission(id, 3) starts REDLINE even on an operation that is not cleared | - | - | - | - | - | - |  |  | 0 |
| `briefing_consumes_serial` | opening a briefing consumes a run serial (issue_run_id instead of next_run_id) | - | **3/484** | - | - | - | - |  |  | 1 |
| `briefing_redline_always` | the briefing always offers REDLINE | - | **1/490** | - | - | - | - |  |  | 1 |
| `mission_id_restored` | FIX, not a mutant: restore the deleted `last_run_contract["mission_id"] = id` line | - | **3/484** | - | - | - | - |  | - | 1 |
| `schema_4` | save schema stays 4 | - | - | - | **1/69** | - | - |  |  | 1 |
| `redline_on_wipe` | a REDLINE record is written even when the run was not a clear | - | - | **2/77** | - | - | - |  |  | 1 |
| `redline_on_early` | a REDLINE record is written on an early extraction (full_route_cleared ignored) | - | - | **1/77** | - | - | - |  |  | 1 |
| `commit_gate_off` | a REDLINE summary on an uncleared operation is committed | - | - | **2/77** | - | - | - |  |  | 1 |
| `sanitize_off` | redline_cleared is read back without sanitising (unknown / uncleared ids are kept) | - | - | - | **1/69** | - | - |  |  | 1 |
| `snapshot_no_redline` | redline_cleared is left out of the saved snapshot | - | **2/484** | - | HANG | - | - |  |  | 2 |
| `contract_persisted` | the campaign snapshot carries a run_contract | - | - | - | **3/69** | **1/?** | - |  |  | 2 |
| `debug_reset_keeps` | debug_reset forgets to clear redline_cleared | - | - | - | - | - | - |  |  | 0 |
| `playlog_no_id` | play log record has no contract_id | - | - | - | - | - | **3/?** |  |  | 1 |
| `playlog_no_redline` | play log record has no redline flag | - | - | - | - | - | **3/?** |  |  | 1 |
| `results_neutral` | the results screen always shows the neutral contract | - | **1/484** | - | - | - | - |  |  | 1 |
| `lobby_no_mark` | the lobby selector no longer marks REDLINE CLEARED | - | **1/484** | - | - | - | - |  |  | 1 |
| `lobby_no_status` | the lobby status line no longer says REDLINE CLEARED | - | **1/484** | - | - | - | - |  |  | 1 |
| `ui_button_overlap` | the contract button sits on top of BACK | - | **24/484** | - | - | - | - |  |  | 1 |
| `ui_choice_short` | choice buttons are 40 px high instead of 72 | - | - | - | - | - | - |  |  | 0 |
| `ui_panel_wide` | the contract panel is 900 px wide (leaves 1280x720) | - | **12/484** | - | - | - | - |  |  | 1 |
| `ui_panel_over_route` | the contract panel starts at x=300 (over the route panel) | - | **24/484** | - | - | - | - |  |  | 1 |
| `ui_no_reveal` | the contract panel is not shown when the dialogue ends | - | **10/484** | - | - | - | - |  |  | 1 |
| `ui_choice_inert` | clicking or pressing a choice does nothing | - | **7/484** | - | - | - | - |  |  | 1 |
| `ui_default_unpressed` | the default choice is not shown as pressed | - | - | - | - | - | - |  |  | 0 |
| `ui_no_effect_text` | the choices show no effect text, only their names | - | - | - | - | - | - |  |  | 0 |

칸: `-` 통과(못 잡음), `n/T` 전체 T개 중 n개 검사가 실패(잡음), `SE` 스크립트 오류로 멈춤, `HANG` 스크립트 오류 뒤 종료하지 못하고 200 s 제한에서 중단(러너는 TIMEOUT으로 빨갛게 표시), 빈칸은 그 변형이 해당 시험을 돌리지 않음. 마지막 열은 SE·HANG을 포함해 빨갛게 된 시험 수.

기준(변형 없음) 줄의 `ERROR:` 개수: playlog 1 (play_log가 만들기 전의 폴더를 여는 무해한 한 줄).

아무 시험도 못 잡은 변형 6개: `offers_no_hazard_stats`, `deploy_redline_unvalidated`, `debug_reset_keeps`, `ui_choice_short`, `ui_default_unpressed`, `ui_no_effect_text`
