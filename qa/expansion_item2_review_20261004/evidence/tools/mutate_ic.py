"""Claude review helper (item 2 review of Codex's e091e25f): break the new rules on a scratch snapshot, one at a time.

usage: mutate_ic.py list                      print every mutant and the tests it is run against
       mutate_ic.py apply <snapshot> <name>   restore the pristine files, then apply the mutant (exactly-once replacements)
       mutate_ic.py restore <snapshot>        restore the pristine files

A mutant is  name: (description, [tests], [(file, old, new), ...]).  Every `old` must match exactly once, else the script stops.
Tests: o = contract_offers, u = contract_ui, r = redline, s = contract_save, m = run_contract (m11), p = play_log, b = boss_duel,
       c = campaign (full-only)
"""
import shutil
import sys
from pathlib import Path

RC = "scripts/core/run_contract.gd"
GF = "scripts/core/game_flow.gd"
CP = "scripts/core/campaign_progression.gd"
SS = "scripts/missions/story_stage_01.gd"
PL = "scripts/core/play_session_log.gd"
MR = "scripts/ui/mission_results.gd"
BL = "scripts/ui/base_lobby.gd"
BS = "scripts/ui/briefing_screen.gd"
FILES = [RC, GF, CP, SS, PL, MR, BL, BS]

CLEAR_LINE = "    var redline_clear := clear and RunContract.redline_available(mission_id, cleared_missions) and RunContract.is_redline(summary.get(\"run_contract\", {}))\n"

M = {
    # ---- the contract itself (RunContract) -------------------------------------------------------------
    "offers_random": ("offers: the alternative pair is chosen by randi() (not deterministic)", "o", [(RC,
        "    var offset := _stable_index(run_id + \"|\" + mission_id + \"|OFFERS\", others.size())\n",
        "    var offset := randi() % maxi(1, others.size())\n")]),
    "offers_default_last": ("offers: the shipped default is returned last, not first", "oup", [(RC,
        "        out.append(offer)\n    return out\n",
        "        out.append(offer)\n    out.push_back(out.pop_front())\n    return out\n")]),
    "offers_dup_pair": ("offers: the third offer repeats the default pair", "o", [(RC,
        "        out.append(offer)\n    return out\n",
        "        out.append(first.duplicate(true) if out.size() == 2 else offer)\n    return out\n")]),
    "offers_reward_flat": ("offers: alternatives lose their hazard reward (risk no longer pays)", "o", [(RC,
        "        var reward := clampf(float(hazard.get(\"reward_multiplier\", 1.0)), 1.0, 2.0)\n",
        "        var reward := 1.0\n")]),
    "offers_no_hazard_stats": ("offers: alternatives keep the default's enemy multipliers (only the label changes)", "orm", [(RC,
        "            offer[key] = clampf(float(hazard.get(key, 1.0)), 0.5, 2.0 if key in [\"enemy_speed_multiplier\", \"enemy_attack_interval_multiplier\"] else 3.0)\n",
        "            pass\n")]),
    "redline_reward_low": ("REDLINE reward 1.0 (not above the offers)", "o", [(RC, "const REDLINE_HAZARD_REWARD := 1.60", "const REDLINE_HAZARD_REWARD := 1.00")]),
    "redline_reward_high": ("REDLINE hazard reward 1.70 (above the 1.6 proposal range)", "o", [(RC, "const REDLINE_HAZARD_REWARD := 1.60", "const REDLINE_HAZARD_REWARD := 1.70")]),
    "redline_hp_high": ("REDLINE HP 1.60 (above the 1.5 proposal range)", "or", [(RC, "const REDLINE_HEALTH := 1.50", "const REDLINE_HEALTH := 1.60")]),
    "redline_interval_low": ("REDLINE attack interval 0.70 (below the 0.80 proposal range)", "or", [(RC, "const REDLINE_INTERVAL := 0.80", "const REDLINE_INTERVAL := 0.70")]),
    "redline_speed_high": ("REDLINE speed 1.30 (above the 1.15 proposal range)", "or", [(RC, "const REDLINE_SPEED := 1.15", "const REDLINE_SPEED := 1.30")]),
    "redline_dmg_high": ("REDLINE damage 1.60 (above the 1.35 proposal range)", "or", [(RC, "const REDLINE_DAMAGE := 1.35", "const REDLINE_DAMAGE := 1.60")]),
    "redline_always_available": ("redline_available() is always true", "ur", [(RC,
        "    return cleared.has(mission_id) and MissionCatalog.available(mission_id, cleared)\n", "    return true\n")]),
    "redline_ignores_clear": ("redline_available() only needs the operation to be unlocked, not cleared", "ur", [(RC,
        "    return cleared.has(mission_id) and MissionCatalog.available(mission_id, cleared)\n",
        "    return MissionCatalog.available(mission_id, cleared)\n")]),
    "boss_not_exempt": ("bosses get REDLINE speed and attack interval too", "rb", [(RC,
        "    if is_redline(contract) and enemy_id.begins_with(\"BOSS_\"):\n", "    if false:\n")]),
    "boss_hp_exempt": ("bosses get no REDLINE HP", "rb", [(RC,
        "        out[\"enemy_speed_multiplier\"] = 1.0\n", "        out[\"enemy_speed_multiplier\"] = 1.0\n        out[\"enemy_health_multiplier\"] = 1.0\n")]),
    "boss_dmg_exempt": ("bosses get no REDLINE damage", "rb", [(RC,
        "        out[\"enemy_speed_multiplier\"] = 1.0\n", "        out[\"enemy_speed_multiplier\"] = 1.0\n        out[\"enemy_damage_multiplier\"] = 1.0\n")]),
    "boss_prefix_other": ("the boss test looks for an 'ENM_' prefix instead of 'BOSS_'", "rb", [(RC,
        "    if is_redline(contract) and enemy_id.begins_with(\"BOSS_\"):\n", "    if is_redline(contract) and enemy_id.begins_with(\"ENM_\"):\n")]),
    # ---- the stage ----------------------------------------------------------------------------------------
    "double_apply": ("the modifiers are applied twice at every encounter spawn (Codex's own control)", "rb", [(SS,
        "        enemy.apply_run_modifiers(RunContract.enemy_modifiers(_enemy_run_modifiers_with_mode(), identity))\n",
        "        enemy.apply_run_modifiers(RunContract.enemy_modifiers(_enemy_run_modifiers_with_mode(), identity))\n"
        "        enemy.apply_run_modifiers(RunContract.enemy_modifiers(_enemy_run_modifiers_with_mode(), identity))\n")]),
    "mode_ids_dropped": ("the stage forgets to pass hazard/opportunity ids, so REDLINE is never recognised per enemy", "rb", [(SS,
        "    modifiers[\"hazard_id\"] = _run_contract.get(\"hazard_id\", \"\")\n", "    pass\n")]),
    "reward_research_skipped": ("the research reward multiplier is never applied", "rm", [(SS,
        "    _run_research_reward_multiplier = clampf(float(_run_contract.get(\"research_reward_multiplier\",1.0)),0.5,4.0)\n",
        "    _run_research_reward_multiplier = 1.0\n")]),
    "reward_clamp_raised": ("the stage reward clamp is raised 4.0 -> 8.0 (a limit raised)", "r", [(SS,
        "    _run_research_reward_multiplier = clampf(float(_run_contract.get(\"research_reward_multiplier\",1.0)),0.5,4.0)\n",
        "    _run_research_reward_multiplier = clampf(float(_run_contract.get(\"research_reward_multiplier\",1.0)),0.5,8.0)\n")]),
    # ---- deploy path ----------------------------------------------------------------------------------------
    "deploy_off_by_one": ("deploy takes choice index+1 (the untouched default would not be the default)", "u", [(GF,
        "    if contract_index >= 0 and contract_index < choices.size(): last_run_contract = choices[contract_index]\n",
        "    if contract_index >= 0 and contract_index < choices.size(): last_run_contract = choices[(contract_index + 1) % choices.size()]\n")]),
    "deploy_redline_unvalidated": ("deploy_mission(id, 3) starts REDLINE even on an operation that is not cleared", "u", [(GF,
        "    elif contract_index == 3 and RunContract.redline_available(id, campaign.cleared_missions): last_run_contract",
        "    elif contract_index == 3: last_run_contract")]),
    "briefing_consumes_serial": ("opening a briefing consumes a run serial (issue_run_id instead of next_run_id)", "u", [(GF,
        "\"contract_run_id\":campaign.next_run_id()", "\"contract_run_id\":campaign.issue_run_id()")]),
    "briefing_redline_always": ("the briefing always offers REDLINE", "u", [(GF,
        "\"allow_redline\":RunContract.redline_available(id, campaign.cleared_missions)", "\"allow_redline\":true")]),
    "mission_id_restored": ("FIX, not a mutant: restore the deleted `last_run_contract[\"mission_id\"] = id` line", "c", [(GF,
        "    view.configure_campaign(snapshot,run_id,last_run_contract)\n",
        "    last_run_contract[\"mission_id\"] = id\n    view.configure_campaign(snapshot,run_id,last_run_contract)\n")]),
    # ---- save / progression ------------------------------------------------------------------------------------
    "schema_4": ("save schema stays 4", "s", [(CP, "const SAVE_SCHEMA_VERSION := 5", "const SAVE_SCHEMA_VERSION := 4")]),
    "redline_on_wipe": ("a REDLINE record is written even when the run was not a clear", "rs", [(CP, CLEAR_LINE,
        "    var redline_clear := RunContract.redline_available(mission_id, cleared_missions) and RunContract.is_redline(summary.get(\"run_contract\", {}))\n")]),
    "redline_on_early": ("a REDLINE record is written on an early extraction (full_route_cleared ignored)", "rs", [(CP, CLEAR_LINE,
        "    var redline_clear := outcome == \"EXTRACTED\" and RunContract.redline_available(mission_id, cleared_missions) and RunContract.is_redline(summary.get(\"run_contract\", {}))\n")]),
    "commit_gate_off": ("a REDLINE summary on an uncleared operation is committed", "r", [(CP,
        "    if RunContract.is_redline(summary.get(\"run_contract\", {})) and not RunContract.redline_available(requested_mission, cleared_missions):\n        return {\"committed\":false,\"reason\":\"REDLINE_NOT_CLEARED\",\"campaign\":snapshot()}\n", "")]),
    "sanitize_off": ("redline_cleared is read back without sanitising (unknown / uncleared ids are kept)", "s", [(CP,
        "        for id in cleared_missions:\n            if saved_redline.has(id): _append_unique(redline_cleared, id)\n",
        "        for id in saved_redline:\n            if id is String: _append_unique(redline_cleared, id)\n")]),
    "snapshot_no_redline": ("redline_cleared is left out of the saved snapshot", "sur", [(CP,
        "    output[\"redline_cleared\"] = redline_cleared.duplicate()\n", "")]),
    "contract_persisted": ("the campaign snapshot carries a run_contract", "ms", [(CP,
        "    output[\"redline_cleared\"] = redline_cleared.duplicate()\n",
        "    output[\"redline_cleared\"] = redline_cleared.duplicate()\n    output[\"run_contract\"] = {}\n")]),
    "debug_reset_keeps": ("debug_reset forgets to clear redline_cleared", "s", [(CP,
        "    cleared_missions.clear()\n    redline_cleared.clear()\n", "    cleared_missions.clear()\n")]),
    # ---- play log, results, lobby, briefing UI ----------------------------------------------------------------------
    "playlog_no_id": ("play log record has no contract_id", "p", [(PL,
        "        \"contract_id\": RunContract.identity(_stage.debug_run_contract()) if _stage != null else \"NEUTRAL\",\n", "")]),
    "playlog_no_redline": ("play log record has no redline flag", "p", [(PL,
        "        \"redline\": RunContract.is_redline(_stage.debug_run_contract()) if _stage != null else false,\n", "")]),
    "results_neutral": ("the results screen always shows the neutral contract", "u", [(MR,
        "    var contract: Dictionary = _summary.get(\"run_contract\", {})\n", "    var contract: Dictionary = {}\n")]),
    "lobby_no_mark": ("the lobby selector no longer marks REDLINE CLEARED", "u", [(BL,
        "        if (_campaign.get(\"redline_cleared\", []) as Array).has(row.mission_id): note = \" / REDLINE CLEARED\"\n", "")]),
    "lobby_no_status": ("the lobby status line no longer says REDLINE CLEARED", "u", [(BL,
        "    if (_campaign.get(\"redline_cleared\", []) as Array).has(selected_mission_id): _mission_status.text = \"REDLINE CLEARED // REPLAY AVAILABLE\"\n", "")]),
    "ui_button_overlap": ("the contract button sits on top of BACK", "u", [(BS,
        "    _contract_button.position = Vector2(280, 622)\n", "    _contract_button.position = Vector2(100, 622)\n")]),
    "ui_choice_short": ("choice buttons are 40 px high instead of 72", "u", [(BS,
        "        choice.size = Vector2(714, 72)\n", "        choice.size = Vector2(714, 40)\n")]),
    "ui_panel_wide": ("the contract panel is 900 px wide (leaves 1280x720)", "u", [(BS,
        "    _contract_panel.size = Vector2(758, 400)\n", "    _contract_panel.size = Vector2(900, 400)\n")]),
    "ui_panel_over_route": ("the contract panel starts at x=300 (over the route panel)", "u", [(BS,
        "    _contract_panel.position = Vector2(476, 196)\n", "    _contract_panel.position = Vector2(300, 196)\n")]),
    "ui_no_reveal": ("the contract panel is not shown when the dialogue ends", "u", [(BS,
        "    _deploy_button.visible = true\n    _show_contracts(true)\n", "    _deploy_button.visible = true\n")]),
    "ui_choice_inert": ("clicking or pressing a choice does nothing", "u", [(BS,
        "        choice.pressed.connect(func() -> void: _select_contract(i))\n", "        pass\n")]),
    "ui_default_unpressed": ("the default choice is not shown as pressed", "u", [(BS,
        "    _contract_choices[0].set_pressed_no_signal(true)\n", "    pass\n")]),
    "ui_no_effect_text": ("the choices show no effect text, only their names", "u", [(BS,
        "        choice.text = \"%s  //  %s%s\\n%s\" % [c.hazard_title, c.opportunity_title, \"  [DEFAULT]\" if i == 0 else \"\", RunContract.effect_text(c)]\n",
        "        choice.text = \"%s  //  %s%s\" % [c.hazard_title, c.opportunity_title, \"  [DEFAULT]\" if i == 0 else \"\"]\n")]),
}


def pristine_dir(snapshot: Path) -> Path:
    return snapshot / ".cache" / "ic_pristine"


def restore(snapshot: Path) -> None:
    pd = pristine_dir(snapshot)
    pd.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        saved = pd / f.replace("/", "__")
        if not saved.exists():
            shutil.copyfile(snapshot / f, saved)
        else:
            shutil.copyfile(saved, snapshot / f)


def apply(snapshot: Path, name: str) -> None:
    restore(snapshot)
    patches = M[name][2]
    by_file = {}
    for f, old, new in patches:
        by_file.setdefault(f, []).append((old, new))
    for f, rows in by_file.items():
        target = snapshot / f
        text = target.read_bytes().decode("utf-8").replace("\r\n", "\n")
        for old, new in rows:
            n = text.count(old)
            if n != 1:
                sys.exit("%s: pattern in %s matches %d times (need 1): %r" % (name, f, n, old[:90]))
            text = text.replace(old, new)
        target.write_bytes(text.encode("utf-8"))
    print("applied %s: %s" % (name, M[name][0]))


def main() -> None:
    cmd = sys.argv[1]
    if cmd == "list":
        for k, (d, t, p) in M.items():
            print("%-26s tests=%-4s %s" % (k, t, d))
        print(len(M), "mutants")
    elif cmd == "apply":
        apply(Path(sys.argv[2]), sys.argv[3])
    elif cmd == "restore":
        restore(Path(sys.argv[2]))
        print("restored")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
