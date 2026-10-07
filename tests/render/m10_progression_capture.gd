extends SceneTree

const LOBBY_SCENE := preload("res://scenes/base/BaseLobby.tscn")
const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const OUT_DIR := "res://artifacts/runtime_capture"

var capture_failed := false

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    DisplayServer.window_set_size(Vector2i(1280,720))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
    var campaign:=CampaignProgression.new(false)
    campaign.commit_mission({
        "transaction_id":"M10-CAPTURE-SEED","outcome":"EXTRACTED","secured_research":900,"secured_salvage":4,"secured_fragments":2,
        "secured_intel":{"SECURITY":2,"ABERRANT":1,"ANCHOR":1}
    })
    await _capture_lab_ready(campaign.snapshot())

    if not bool(campaign.analyze_intel("ANL_SECURITY_ARC_GAP").get("success",false)): _fail("SECURITY analysis failed during capture")
    if not bool(campaign.analyze_intel("ANL_ABERRANT_JOINT_MAP").get("success",false)): _fail("ABERRANT analysis failed during capture")
    if not bool(campaign.analyze_intel("ANL_ANCHOR_SIGNAL_MODEL").get("success",false)): _fail("ANCHOR analysis failed during capture")
    if not bool(campaign.equip_module("CHR_PROTO_01","MOD_PRISM_FOCUS").get("success",false)): _fail("ASTER module equip failed during capture")
    if not bool(campaign.equip_module("CHR_PROTO_02","MOD_BREACH_LINER").get("success",false)): _fail("ROOK module equip failed during capture")
    if not bool(campaign.equip_module("CHR_PROTO_03","MOD_SENSOR_ARRAY").get("success",false)): _fail("MICA module equip failed during capture")
    await _capture_armory_loadout(campaign.snapshot())
    await _capture_field_intel(campaign.snapshot())

    if capture_failed or not _verify(): quit(1); return
    print("M10_PROGRESSION_CAPTURE: PASS")
    quit(0)

func _capture_lab_ready(snapshot: Dictionary) -> void:
    var layer:=CanvasLayer.new(); layer.layer=100; root.add_child(layer)
    var lobby:=LOBBY_SCENE.instantiate() as BaseLobby
    lobby.configure_campaign(snapshot); layer.add_child(lobby); await _frames(3); lobby.call("_show_facility","LAB"); await _frames(2)
    var contract:=lobby.debug_m10_contract(); var samples:Dictionary=contract.get("intel_samples",{})
    if int(samples.get("SECURITY",0))!=2 or int(samples.get("ABERRANT",0))!=1 or int(samples.get("ANCHOR",0))!=1: _fail("Lab capture sample counts mismatch")
    await _save("32_m10_lab_analysis_ready.png")
    layer.queue_free(); await process_frame

func _capture_armory_loadout(snapshot: Dictionary) -> void:
    var layer:=CanvasLayer.new(); layer.layer=100; root.add_child(layer)
    var lobby:=LOBBY_SCENE.instantiate() as BaseLobby
    lobby.configure_campaign(snapshot); layer.add_child(lobby); await _frames(3); lobby.call("_show_facility","ARMORY"); await _frames(2)
    var contract:=lobby.debug_m10_contract(); var equipped:Dictionary=contract.get("equipped_modules",{})
    if str(equipped.get("CHR_PROTO_01",""))!="MOD_PRISM_FOCUS" or str(equipped.get("CHR_PROTO_02",""))!="MOD_BREACH_LINER" or str(equipped.get("CHR_PROTO_03",""))!="MOD_SENSOR_ARRAY": _fail("Armory capture loadout mismatch")
    await _save("33_m10_armory_loadout.png")
    layer.queue_free(); await process_frame

func _capture_field_intel(snapshot: Dictionary) -> void:
    var stage:=STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage); current_scene=stage; await _frames(6)
    stage.configure_campaign(snapshot,"M10-CAPTURE-FIELD")
    stage.current_step=3; stage.call("_activate_step"); stage.debug_seed_intel(2,1,1)
    var aster:=stage.squad.operators[0]; var rook:=stage.squad.operators[1]; var mica:=stage.squad.operators[2]
    if aster.debug_equipped_module()!="MOD_PRISM_FOCUS" or rook.debug_equipped_module()!="MOD_BREACH_LINER" or mica.debug_equipped_module()!="MOD_SENSOR_ARRAY": _fail("field loadout injection mismatch")
    stage.hud.set_story("LOADOUT ACTIVE // ASTER PRISM FOCUS · ROOK BREACH LINER · MICA SENSOR ARRAY")
    stage.hud.set_objective("Carry SEC / ABR / ANC intel to the next extraction window",false)
    var camera:=stage.get_node("Camera2D") as Camera2D; camera.enabled=true; camera.position_smoothing_enabled=false; camera.global_position=Vector2(1510,480); camera.zoom=Vector2.ONE*1.25
    var camera_presentation:=stage.get_node_or_null("SquadCameraPresentation") as SquadCameraPresentation
    if camera_presentation!=null: camera_presentation.set_process(false)
    await _frames(3)
    var intel_text:=stage.hud.debug_intel_text()
    if not ("SEC 02" in intel_text and "ABR 01" in intel_text and "ANC 01" in intel_text): _fail("field intel HUD mismatch: "+intel_text)
    await _save("34_m10_field_intel_loadout.png")
    stage.queue_free(); await process_frame

func _frames(count:int)->void:
    for _i in range(count): await process_frame

func _save(filename:String)->void:
    await RenderingServer.frame_post_draw
    var image:=root.get_texture().get_image(); var bright:=0
    for y in range(70,680,4):
        for x in range(20,1260,4):
            var p:=image.get_pixel(x,y)
            if maxf(p.r,maxf(p.g,p.b))>0.22: bright+=1
    print("M10_UI_EVIDENCE %s bright_samples=%d"%[filename,bright])
    if bright<180: _fail("M10 evidence visually empty/off-canvas: %s samples=%d"%[filename,bright])
    var path:=ProjectSettings.globalize_path(OUT_DIR+"/"+filename); var err:=image.save_png(path)
    if err!=OK: _fail("M10 capture save failed: %s err=%d"%[path,err])

func _verify()->bool:
    for filename in ["32_m10_lab_analysis_ready.png","33_m10_armory_loadout.png","34_m10_field_intel_loadout.png"]:
        if not FileAccess.file_exists(ProjectSettings.globalize_path(OUT_DIR+"/"+filename)):
            push_error("missing M10 runtime evidence: "+filename); return false
    return true

func _fail(message:String)->void:
    capture_failed=true; push_error(message)
