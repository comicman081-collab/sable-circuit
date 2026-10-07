extends SceneTree
## Claude review helper (item 2): build a REAL save with the code of the snapshot it runs in (used on the 7b26a152 archive,
## so the file is what the shipped game would have written). usage: make_old_save.gd -- --save=res://.cache/in/old_v4.json
func _init() -> void:
    var save := "res://.cache/in/old_v4.json"
    for a in OS.get_cmdline_user_args():
        if a.begins_with("--save="): save = a.trim_prefix("--save=")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(save.get_base_dir()))
    if FileAccess.file_exists(save): DirAccess.remove_absolute(ProjectSettings.globalize_path(save))
    var p := CampaignProgression.new(true, save)
    p.debug_reset()
    var id := p.issue_run_id("CH01")
    p.commit_mission({"transaction_id": id, "mission_id": "MIS_CH01_01", "outcome": "EXTRACTED", "full_route_cleared": true,
        "secured_research": 220, "secured_salvage": 6, "secured_fragments": 3, "secured_intel": {"SECURITY": 2, "ABERRANT": 1, "ANCHOR": 1}})
    id = p.issue_run_id("CH01")
    p.commit_mission({"transaction_id": id, "mission_id": "MIS_CH01_02", "outcome": "EXTRACTED", "full_route_cleared": true,
        "secured_research": 410, "secured_salvage": 9, "secured_fragments": 4, "secured_intel": {"SECURITY": 1, "ABERRANT": 3}})
    id = p.issue_run_id("CH01")
    p.commit_mission({"transaction_id": id, "mission_id": "MIS_CH01_03", "outcome": "WIPED", "full_route_cleared": false,
        "secured_research": 35, "secured_salvage": 0, "secured_fragments": 0})
    p.purchase_upgrade("ARMORY_CALIBRATION")
    p.issue_run_id("CH01")
    print("MAKE_OLD_SAVE: ", save, " cleared=", p.cleared_missions, " serial=", p.run_serial)
    quit(0)
