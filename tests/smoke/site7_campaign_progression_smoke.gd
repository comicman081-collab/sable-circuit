extends SceneTree
const Catalog := preload("res://scripts/core/site7_campaign.gd")
const FLOW := preload("res://scripts/core/game_flow.gd")
const TestOutput := preload("res://tests/support/test_output.gd")
var failures: Array[String] = []
var checks := 0
var out := TestOutput.path("res://qa/campaign_20260919/flow_" + str(Time.get_unix_time_from_system()).replace(".","_"))

func _init() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok: failures.append(label); push_error(label)
func settle() -> void:
    for _i in range(5): await process_frame; await physics_frame
func summary(id: String, serial: String, full: bool = true) -> Dictionary:
    return {"mission_id":id,"transaction_id":serial,"outcome":"EXTRACTED","full_route_cleared":full,"extraction_depth":6 if full else 3,"secured_research":200,"secured_salvage":3,"secured_fragments":1}

func run() -> void:
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    var prop_manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/visual/site7_environment_props.json"))["missions"]
    # All persistence fixtures are project-local. Never touch the player's save.
    var save := out+"/campaign.json"
    var old := {"schema_version":3,"research_value":777,"salvage":8,"armory_level":1,"completed_runs":4,"extracted_runs":4,"run_serial":4,"equipped_weapons":{"CHR_PROTO_01":"WPN_AR_BURST_02"}}
    var file := FileAccess.open(save,FileAccess.WRITE); file.store_string(JSON.stringify(old)); file.close()
    var campaign := CampaignProgression.new(true,save)
    check(campaign.research_value==777 and campaign.armory_level==1,"v3 migration preserves wallet and upgrade")
    check(campaign.equipped_weapons.CHR_PROTO_01=="WPN_AR_BURST_02","v3 migration preserves weapon")
    check(campaign.cleared_missions.is_empty(),"Old extracted runs do not fabricate full clears")
    check(not Catalog.available("MIS_CH01_02",campaign.cleared_missions),"Stage 2 starts locked")
    var preview := summary("MIS_CH01_01","PREVIEW"); preview["battle_preview"]=true
    campaign.commit_mission(preview)
    check(campaign.research_value==777 and campaign.cleared_missions.is_empty(),"Preview earns no wallet or progression")
    campaign.commit_mission(summary("MIS_CH01_01","EARLY",false))
    var wipe := summary("MIS_CH01_01","WIPE"); wipe["outcome"]="WIPED"; campaign.commit_mission(wipe)
    campaign.commit_mission(summary("MIS_CH01_03","LOCKED"))
    check(campaign.cleared_missions.is_empty(),"Early extraction, wipe and out-of-order clears do not unlock")
    var flow := FLOW.new(); flow.persist_campaign=false; root.add_child(flow); await settle()
    flow.campaign=campaign
    var playable_count := Catalog.playable_ids().size()
    for number in range(1,playable_count+1):
        var id := "MIS_CH01_%02d" % number
        flow.enter_base(); await settle()
        var lobby := flow.current_view as BaseLobby
        check(lobby.selected_mission_id==id,"Base recommends operation %d"%number)
        lobby.mission_selected_requested.emit(id); await settle()
        var briefing := flow.current_view as BriefingScreen
        check(briefing!=null and briefing.mission_id==id,"Selected briefing owns mission %d"%number)
        check(briefing._briefing.size()>=4,"Mission-specific comms exist %d"%number)
        briefing.debug_complete_briefing(); briefing.debug_deploy(); await settle()
        var stage := flow.current_view as StoryStage01
        check(stage!=null and stage.mission_id==id and stage.mission.mission_id==id,"Pre-ready mission assignment %d"%number)
        check(stage.get_node("RoomArtLayer")._selected_mission_id==id,"Art matches selected mission %d"%number)
        var expected_props := 0
        for room_props: Array in prop_manifest[id].values(): expected_props += room_props.size()
        # The campaign_data gate already requires cover props in every room, so the floor is one per room
        # (operations 1-5 author 12-15 props, operation 6 authors 11) and every authored prop must attach.
        check(expected_props >= (prop_manifest[id] as Dictionary).size() and stage.get_node("EnvironmentProps").entries.size() == expected_props,
            "Every authored cover prop attached to operation %d" % number)
        check(stage.squad.operators[0].equipped_weapon_id=="WPN_AR_BURST_02","Saved weapon injected %d"%number)
        check(stage._run_contract.mission_id==id,"Run contract scoped %d"%number)
        # Exercise actual interaction and authored reward handler, not a field flag.
        stage.current_step=2
        var room: Dictionary=stage.main_route[2]
        var actor := stage.squad.get_active_operator()
        actor.global_position=Vector2(float(room.x),float(room.y))
        # The opening access beat now completes on the first live tick and
        # banks its own reward, so measure only this room's authored payout.
        var research_before: int = stage._cargo_common_research
        stage._handle_interaction(actor)
        check(stage._ledger_recovered,"Mission-specific evidence recovered %d"%number)
        check(stage._cargo_common_research-research_before==int(room.get("loot",[{"quantity":45}])[0].quantity),"Mission-specific research reward %d"%number)
        if number>=2:
            stage._award_authored_loot(stage.optional_rooms[1].loot)
            check(stage._cargo_intel.ABERRANT==1,"Robot research yields legacy-compatible mechanical sample %d"%number)
            var research := CampaignProgression.new(false)
            research.commit_mission({"transaction_id":"LAB","secured_research":140,"secured_intel":{"ABERRANT":1}})
            check(research.analyze_intel("ANL_ABERRANT_JOINT_MAP").success,"ROOK module obtainable without a humanoid enemy %d"%number)
        # Both optional rooms recover through the real interaction, whatever the mission calls them
        # (operations 6-10 name them for the place, which the stage once did not recognise).
        for index in range(stage.optional_rooms.size()):
            var optional: Dictionary = stage.optional_rooms[index]
            actor.global_position=Vector2(float(optional.x),float(optional.y))
            check(not stage.optional_recovered(index),"Optional room %s starts unrecovered in operation %d"%[optional.id,number])
            stage._handle_interaction(actor)
            check(stage.optional_recovered(index),"Optional room %s recovers through interaction in operation %d"%[optional.id,number])
        check(stage._supply_found and stage._signal_found,"Supply cache and signal fragment both recovered in operation %d"%number)
        var completed := summary(id,stage._run_id)
        flow.show_results(completed); await settle()
        var result := flow.current_view as MissionResults
        check(campaign.cleared_missions.has(id),"Full clear persisted %d"%number)
        var wallet := campaign.research_value
        campaign.commit_mission(completed)
        check(campaign.research_value==wallet,"Duplicate result cannot repay %d"%number)
        check(result._next_id==("MIS_CH01_%02d"%(number+1) if number<playable_count else ""),"Next operation result link %d"%number)
        if number<playable_count:
            result.debug_next(); await settle()
            check(flow.current_view.mission_id=="MIS_CH01_%02d"%(number+1),"Next button opens correct briefing %d"%number)
        campaign=CampaignProgression.new(true,save); flow.campaign=campaign
        check(campaign.cleared_missions.size()==number,"Reload preserves ordered clears %d"%number)
    # Operations 6-10 are listed but held back until their art is integrated, so clearing
    # every playable operation finishes what can be played without completing the chapter.
    var playable: Array[String] = Catalog.playable_ids()
    var held_back: Array[String] = []
    for row: Dictionary in Catalog.rows():
        if not bool(row.get("deployable",true)): held_back.append(str(row.mission_id))
    var finished := campaign.snapshot()
    check(finished.playable_complete,"Every playable operation is cleared once each has been extracted")
    check(bool(finished.chapter_complete)==held_back.is_empty(),"The chapter completes only when no operation is held back")
    for id in playable: check(Catalog.available(id,campaign.cleared_missions),"Completed operation replayable "+id)
    if not held_back.is_empty():
        flow.enter_base(); await settle()
        var lobby := flow.current_view as BaseLobby
        check(lobby.selected_mission_id==playable.back(),"Base recommends the last playable operation once all are cleared")
        for id in held_back:
            var slot := -1
            for index in range(lobby._mission_selector.item_count):
                if str(lobby._mission_selector.get_item_metadata(index))==id: slot=index
            check(slot>=0 and lobby._mission_selector.is_item_disabled(slot),"Held-back operation is listed but not selectable "+id)
            check(slot>=0 and lobby._mission_selector.get_item_text(slot).contains("IN PREPARATION"),"Held-back operation says it is in preparation "+id)
        check(lobby._mission_status.text.contains("IN PREPARATION"),"Base tells the player the next operation is in preparation")
        flow.open_mission_briefing(held_back[0]); await settle()
        check(flow.current_state=="BASE","A held-back operation opens no briefing")
        flow.deploy_mission(held_back[0]); await settle()
        check(flow.current_state=="BASE" and flow.selected_mission_id!=held_back[0],"A held-back operation cannot be deployed")
        var wallet_before := campaign.research_value
        var forced := campaign.commit_mission(summary(held_back[0],"HELD-BACK"))
        check(not bool(forced.get("committed",true)) and str(forced.get("reason",""))=="MISSION_LOCKED","A result for a held-back operation is refused")
        check(campaign.research_value==wallet_before and not campaign.cleared_missions.has(held_back[0]),"A held-back operation earns and clears nothing")
        check(flow.campaign.snapshot().recommended_mission_id==playable.back(),"The recommended operation stays playable")
    flow.queue_free(); await settle()
    file=FileAccess.open(out+"/check.json",FileAccess.WRITE)
    file.store_string(JSON.stringify({"checks":checks,"failures":failures,"status":"PASS" if failures.is_empty() else "FAIL","scope":"Synthetic campaign transactions/UI/data wiring; not a combat playthrough","save_path":save},"  ")); file.close()
    print("SITE7_CAMPAIGN_PROGRESSION: %s (%d checks) %s"%["PASS" if failures.is_empty() else "FAIL",checks,out])
    quit(0 if failures.is_empty() else 1)
