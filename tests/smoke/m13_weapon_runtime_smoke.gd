extends SceneTree

var failures:Array[String]=[]

func _init()->void: call_deferred("_run")

func _run()->void:
    var progression:=CampaignProgression.new(false)
    progression.commit_mission({"transaction_id":"M13-RUNTIME-SEED","outcome":"EXTRACTED","secured_research":1200,"secured_salvage":10,"secured_fragments":3,"secured_intel":{"ANCHOR":1}})
    progression.purchase_upgrade("ARMORY_CALIBRATION")
    progression.purchase_upgrade("ARMORY_CALIBRATION")
    progression.analyze_intel("ANL_ANCHOR_SIGNAL_MODEL")
    progression.equip_weapon("CHR_PROTO_01","WPN_AR_BURST_02")
    progression.equip_weapon("CHR_PROTO_03","WPN_SPECIAL_ARC_01")

    var flow:=GameFlow.new(); root.add_child(flow); await _frames(3); flow.campaign=progression; flow.deploy_stage_01(); await _frames(5)
    var stage:=flow.current_view as StoryStage01
    _check(stage!=null,"GameFlow deployment creates stage")
    if stage==null: _finish(); return
    var aster:=stage.squad.operators[0]; var rook:=stage.squad.operators[1]; var mica:=stage.squad.operators[2]
    _check(aster.debug_equipped_weapon()=="WPN_AR_BURST_02","ASTER injected burst")
    _check(rook.debug_equipped_weapon()=="WPN_SHOTGUN_MAG_01","ROOK injected shotgun")
    _check(mica.debug_equipped_weapon()=="WPN_SPECIAL_ARC_01","MICA injected special")
    for actor in stage.squad.operators: actor.set_physics_process(false)
    var campaign_damage:=float(progression.snapshot().get("damage_multiplier",1.0))

    var before:=aster.ammo; _clear_projectiles(); _check(aster.debug_fire_once(),"burst fires"); var shots:=_projectiles(aster)
    _check(aster.ammo==before-3,"burst consumes 3 ammo"); _check(shots.size()==3,"burst spawns 3 projectiles")
    for p in shots: _check(is_equal_approx(p.damage,7.2*campaign_damage) and is_equal_approx(p.speed,1100.0),"burst projectile spec")
    _clear_projectiles()

    before=rook.ammo; _check(rook.debug_fire_once(),"shotgun fires"); shots=_projectiles(rook)
    _check(rook.ammo==before-1,"shotgun consumes one shell"); _check(shots.size()==5,"shotgun spawns five pellets"); _clear_projectiles()

    before=mica.ammo; _check(mica.debug_fire_once(),"special fires"); shots=_projectiles(mica)
    _check(mica.ammo==before-1 and shots.size()==1,"special one cell/one projectile")
    if shots.size()==1: _check(is_equal_approx(shots[0].damage,28.0*campaign_damage) and is_equal_approx(shots[0].speed,520.0),"special projectile spec")
    _clear_projectiles()

    aster.ammo=2; _check(not aster.debug_fire_once(),"burst blocks partial trigger"); _check(aster.is_reloading(),"burst shortage starts reload")
    flow.queue_free(); await process_frame
    _finish()

func _projectiles(actor:OperatorActor)->Array[PrototypeProjectile]:
    var out:Array[PrototypeProjectile]=[]
    for node in root.get_children():
        if node is PrototypeProjectile and (node as PrototypeProjectile).owner_actor==actor: out.append(node as PrototypeProjectile)
    return out
func _clear_projectiles()->void:
    for node in root.get_children():
        if node is PrototypeProjectile: node.queue_free()
func _frames(count:int)->void:
    for _i in range(count): await process_frame
func _check(condition:bool,label:String)->void:
    if condition: print("PASS: "+label)
    else: failures.append(label); push_error("FAIL: "+label)
func _finish()->void:
    if failures.is_empty(): print("M13_WEAPON_RUNTIME_SMOKE: PASS"); quit(0); return
    print("M13_WEAPON_RUNTIME_SMOKE: FAIL (%d)"%failures.size()); quit(1)
