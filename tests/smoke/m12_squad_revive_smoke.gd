extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")

var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var stage:=STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene=stage
    await _frames(4)
    stage.configure_campaign({},"M12-REVIVE-SMOKE")

    var squad:=stage.squad
    var aster:=squad.operators[0]
    var rook:=squad.operators[1]
    var mica:=squad.operators[2]
    squad.request_control(0)
    aster.global_position=Vector2(500,500)
    rook.global_position=Vector2(550,500)
    mica.global_position=Vector2(800,500)

    rook.apply_damage(99999.0)
    _check(rook.is_downed(),"ROOK enters downed state at zero HP")
    _check(squad.get_active_operator()==aster,"active operator remains controllable when a companion goes down")
    squad.request_control(1)
    _check(squad.get_active_operator()==aster,"downed operator cannot be selected directly")
    _check(squad.debug_has_revivable_target_in_range(),"nearby downed squadmate is a revivable target")
    _check(stage.debug_interaction_reserved_for_revive(),"nearby revive reserves shared F interaction before mission actions")

    squad.debug_step_revive(1.0,true)
    var partial:=squad.debug_revive_contract()
    _check(bool(partial.get("active",false)),"holding F begins authoritative revive transaction")
    _check(str(partial.get("reviver_id",""))==aster.operator_id and str(partial.get("target_id",""))==rook.operator_id,"revive authority records reviver and target")
    _check(float(partial.get("progress",0.0))>0.40 and float(partial.get("progress",0.0))<0.50,"one second produces partial progress on 2.2 second revive")
    _check(rook.is_downed(),"partial revive never restores target early")

    squad.debug_step_revive(0.0,false)
    var released:=squad.debug_revive_contract()
    _check(not bool(released.get("active",true)) and is_equal_approx(float(released.get("progress",-1.0)),0.0),"releasing F cancels and resets revive progress")

    rook.global_position=Vector2(700,500)
    squad.debug_step_revive(1.0,true)
    var out_of_range:=squad.debug_revive_contract()
    _check(not bool(out_of_range.get("active",true)) and is_equal_approx(float(out_of_range.get("progress",-1.0)),0.0),"out-of-range target cannot accumulate revive progress")

    rook.global_position=Vector2(550,500)
    squad.debug_step_revive(0.8,true)
    _check(float(squad.debug_revive_contract().get("progress",0.0))>0.30,"revive can restart after cancellation")
    squad.request_control(2)
    _check(not bool(squad.debug_revive_contract().get("active",true)) and is_equal_approx(float(squad.debug_revive_contract().get("progress",-1.0)),0.0),"changing reviver resets in-progress revive transaction")

    mica.global_position=Vector2(520,500)
    squad.debug_step_revive(2.19,true)
    _check(rook.is_downed(),"revive remains downed before full 2.2 second hold")
    squad.debug_step_revive(0.02,true)
    _check(not rook.is_downed(),"full uninterrupted hold revives downed squadmate")
    _check(is_equal_approx(rook.health,rook.max_health*0.35),"revived operator returns at exactly 35 percent HP")
    var post_revive:=squad.debug_revive_contract()
    _check(int(post_revive.get("completed_revives",0))==1 and str(post_revive.get("last_revived_operator_id",""))==rook.operator_id,"squad records exactly one completed revive")
    var protection:=rook.debug_runtime_skill_buffs()
    _check(float(protection.get("guard_left",0.0))>=1.24 and is_equal_approx(float(protection.get("guard_reduction",0.0)),0.65),"revive grants 1.25 second 65 percent protection")
    var hp_before_guard:=rook.health
    rook.apply_damage(20.0)
    _check(is_equal_approx(hp_before_guard-rook.health,7.0),"revive protection changes actual incoming damage authority")

    # A second down/revive attempt proves distance interruption is authoritative.
    rook.apply_damage(99999.0)
    _check(rook.is_downed(),"revived operator can be downed again normally")
    mica.global_position=Vector2(520,500)
    rook.global_position=Vector2(550,500)
    squad.debug_step_revive(0.6,true)
    _check(float(squad.debug_revive_contract().get("progress",0.0))>0.25,"second revive begins normally")
    mica.global_position=Vector2(800,500)
    squad.debug_step_revive(0.1,true)
    _check(is_equal_approx(float(squad.debug_revive_contract().get("progress",-1.0)),0.0),"moving reviver outside range cancels revive progress")

    mica.global_position=Vector2(520,500)
    stage.debug_offer_extraction("R03_ARCHIVE")
    _check(stage.debug_extraction_active(),"test extraction window is active")
    _check(stage.debug_interaction_reserved_for_revive(),"revive priority remains active inside extraction window")

    # Revive state is deployment-only and never part of campaign persistence.
    var campaign:=CampaignProgression.new(false)
    var snapshot:=campaign.snapshot()
    _check(not snapshot.has("completed_revives") and not snapshot.has("last_revived_operator_id"),"campaign persistence contains no revive transaction state")

    stage.queue_free()
    await process_frame
    _finish()

func _frames(count:int)->void:
    for _i in range(count): await process_frame

func _check(condition:bool,label:String)->void:
    if condition: print("PASS: "+label)
    else: failures.append(label); push_error("FAIL: "+label)

func _finish()->void:
    if failures.is_empty():
        print("M12_SQUAD_REVIVE_SMOKE: PASS")
        quit(0)
        return
    print("M12_SQUAD_REVIVE_SMOKE: FAIL (%d)"%failures.size())
    for failure in failures: print(" - "+failure)
    quit(1)
