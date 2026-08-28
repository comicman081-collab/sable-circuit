extends SceneTree

const LOBBY_SCENE := preload("res://scenes/base/BaseLobby.tscn")

var failures: Array[String] = []
var analysis_events: Array[String] = []
var module_events: Array[Array] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var campaign := CampaignProgression.new(false)
    campaign.commit_mission({
        "transaction_id":"M10-UI-SEED",
        "outcome":"EXTRACTED",
        "secured_research":900,
        "secured_intel":{"SECURITY":2,"ABERRANT":1,"ANCHOR":1}
    })

    var lobby := LOBBY_SCENE.instantiate() as BaseLobby
    lobby.configure_campaign(campaign.snapshot())
    lobby.analysis_requested.connect(_on_analysis_requested)
    root.add_child(lobby)
    await _frames(3)

    var analyze_buttons: Array[Button] = []
    for node in lobby.find_children("*","Button",true,false):
        if node is Button and (node as Button).text == "ANALYZE":
            analyze_buttons.append(node as Button)
    _check(analyze_buttons.size()==3,"M10 Base renders three actionable Lab analysis buttons")
    for button in analyze_buttons:
        button.pressed.emit()
    _check(analysis_events==["ANL_SECURITY_ARC_GAP","ANL_ABERRANT_JOINT_MAP","ANL_ANCHOR_SIGNAL_MODEL"],"dynamic Lab buttons preserve their own authored analysis IDs")

    lobby.queue_free()
    await process_frame

    _check(bool(campaign.analyze_intel("ANL_SECURITY_ARC_GAP").get("success",false)),"UI loadout seed analyzes SECURITY")
    _check(bool(campaign.analyze_intel("ANL_ABERRANT_JOINT_MAP").get("success",false)),"UI loadout seed analyzes ABERRANT")
    _check(bool(campaign.analyze_intel("ANL_ANCHOR_SIGNAL_MODEL").get("success",false)),"UI loadout seed analyzes ANCHOR")

    var loadout_lobby := LOBBY_SCENE.instantiate() as BaseLobby
    loadout_lobby.configure_campaign(campaign.snapshot())
    loadout_lobby.module_equip_requested.connect(_on_module_requested)
    root.add_child(loadout_lobby)
    await _frames(3)

    var equip_buttons: Array[Button] = []
    for node in loadout_lobby.find_children("*","Button",true,false):
        if node is Button and (node as Button).text == "EQUIP":
            equip_buttons.append(node as Button)
    _check(equip_buttons.size()==3,"M10 Base renders three unlocked operator EQUIP buttons")
    for button in equip_buttons:
        button.pressed.emit()
    _check(module_events.size()==3,"all three loadout buttons emit module requests")
    if module_events.size()==3:
        _check(module_events[0]==["CHR_PROTO_01","MOD_PRISM_FOCUS"],"ASTER loadout button preserves PRISM FOCUS binding")
        _check(module_events[1]==["CHR_PROTO_02","MOD_BREACH_LINER"],"ROOK loadout button preserves BREACH LINER binding")
        _check(module_events[2]==["CHR_PROTO_03","MOD_SENSOR_ARRAY"],"MICA loadout button preserves SENSOR ARRAY binding")

    loadout_lobby.queue_free()
    await process_frame
    _finish()

func _on_analysis_requested(analysis_id:String)->void:
    analysis_events.append(analysis_id)

func _on_module_requested(operator_id:String,module_id:String)->void:
    module_events.append([operator_id,module_id])

func _frames(count:int)->void:
    for _i in range(count): await process_frame

func _check(condition:bool,label:String)->void:
    if condition: print("PASS: "+label)
    else: failures.append(label); push_error("FAIL: "+label)

func _finish()->void:
    if failures.is_empty():
        print("M10_BASE_UI_ACTION_SMOKE: PASS")
        quit(0)
        return
    print("M10_BASE_UI_ACTION_SMOKE: FAIL (%d)"%failures.size())
    for failure in failures: print(" - "+failure)
    quit(1)
