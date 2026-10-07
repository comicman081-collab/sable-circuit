extends SceneTree
## Claude review helper (item 2): with the NEW code, clear operations 1-2 and record a REDLINE clear of operation 1 (real commit path),
## so the file carries schema 5 + redline_cleared. usage: make_new_save.gd -- --save=res://.cache/in/new_v5.json
func _init() -> void:
    var save := "res://.cache/in/new_v5.json"
    for a in OS.get_cmdline_user_args():
        if a.begins_with("--save="): save = a.trim_prefix("--save=")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(save.get_base_dir()))
    if FileAccess.file_exists(save): DirAccess.remove_absolute(ProjectSettings.globalize_path(save))
    var p := CampaignProgression.new(true, save)
    p.debug_reset()
    var id := p.issue_run_id("CH01")
    p.commit_mission({"transaction_id": id, "mission_id": "MIS_CH01_01", "outcome": "EXTRACTED", "full_route_cleared": true, "secured_research": 220, "secured_salvage": 6, "secured_fragments": 3})
    id = p.issue_run_id("CH01")
    p.commit_mission({"transaction_id": id, "mission_id": "MIS_CH01_02", "outcome": "EXTRACTED", "full_route_cleared": true, "secured_research": 410, "secured_salvage": 9, "secured_fragments": 4})
    id = p.issue_run_id("CH01")
    var r := p.commit_mission({"transaction_id": id, "mission_id": "MIS_CH01_01", "outcome": "EXTRACTED", "full_route_cleared": true, "secured_research": 530, "secured_salvage": 14, "secured_fragments": 7, "run_contract": RunContract.redline(id)})
    print("MAKE_NEW_SAVE: ", save, " cleared=", p.cleared_missions, " redline=", p.redline_cleared, " last=", r.get("redline_cleared"))
    quit(0)
