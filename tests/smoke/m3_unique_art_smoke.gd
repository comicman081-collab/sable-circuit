extends SceneTree

const OPERATOR_SCENE := preload("res://scenes/actors/player/OperatorActor.tscn")
const ENEMY_SCENE := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const PROJECTILE := preload("res://scripts/combat/prototype_projectile.gd")

var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var playable_ids:Array[String]=["CHR_PROTO_01","CHR_PROTO_02","CHR_PROTO_03"]
    var enemy_ids:Array[String]=["ENM_SITE7_RIFLE_01","ENM_SITE7_SHIELD_01","ENM_SITE7_DRONE_01","ENM_SITE7_ABERRANT_01","BOSS_SITE7_ANCHOR_01"]
    var fields:Array[String]=["visual_profile","motion_profile","projectile_profile","hit_vfx_profile","fire_sfx_profile","impact_sfx_profile","master_asset","rig_sheet"]
    var seen:Dictionary={}; var all_ids:Array[String]=playable_ids.duplicate(); all_ids.append_array(enemy_ids)

    for identity:String in all_ids:
        var profile:Dictionary=ArtProfileRegistry.get_profile(identity)
        _check(not profile.is_empty(),identity+" profile loads")
        for field:String in fields:
            var value:String=str(profile.get(field,"")); _check(not value.is_empty(),identity+" has "+field)
            var key:String=field+"::"+value; _check(not seen.has(key),identity+" has unique "+field); seen[key]=identity
        _check(ResourceLoader.exists("res://"+str(profile.get("master_asset",""))),identity+" master asset imports")
        _check(ResourceLoader.exists("res://"+str(profile.get("rig_sheet",""))),identity+" layered rig sheet imports")

    var names:Array[String]=["ASTER","ROOK","MICA"]; var colors:Array[Color]=[Color("69d2ff"),Color("ff9d6c"),Color("a8f07a")]
    var damage_target:OperatorActor=null
    for i:int in range(playable_ids.size()):
        var actor:=OPERATOR_SCENE.instantiate() as OperatorActor; actor.configure(playable_ids[i],names[i],colors[i]); actor.global_position=Vector2(320+i*90,320); root.add_child(actor); await process_frame
        var visual:=actor.get_node_or_null("VisualRoot") as OperatorVisual
        _check(visual!=null and visual.skeleton!=null,names[i]+" runtime Skeleton2D exists")
        _check(visual!=null and visual.muzzle_socket!=null,names[i]+" unique muzzle exists")
        var hr_parts:Array[Node]=visual.skeleton.find_children("*HR","Sprite2D",true,false) if visual and visual.skeleton else []
        _check(hr_parts.size()>=15,names[i]+" uses 15+ high-resolution SVG rig layers")
        if not hr_parts.is_empty(): _check((hr_parts[0] as Sprite2D).texture!=null,names[i]+" high-resolution layer texture bound")
        if i==0: damage_target=actor
        else: actor.queue_free(); await process_frame

    for enemy_id:String in enemy_ids:
        var enemy:=ENEMY_SCENE.instantiate() as EnemyActor; enemy.configure(enemy_id,100.0); enemy.global_position=Vector2(700,360); root.add_child(enemy); await process_frame
        var hidden:=enemy.get_node_or_null("HighResVisualRoot/UniqueMasterSprite") as Sprite2D
        var rig:=enemy.get_node_or_null("HighResVisualRoot/UniqueLayerRig") as Skeleton2D
        _check(hidden!=null and hidden.texture!=null,enemy_id+" audit master texture bound")
        _check(rig!=null,enemy_id+" identity-specific Skeleton2D rig exists")
        var layered:Array[Node]=rig.find_children("*","Sprite2D",true,false) if rig else []
        _check(layered.size()>=7,enemy_id+" uses multiple high-resolution articulated layers")
        enemy.queue_free(); await process_frame

    if damage_target:
        var before:float=damage_target.health
        var hostile_profile:Dictionary=ArtProfileRegistry.get_profile("ENM_SITE7_RIFLE_01")
        var projectile:=PROJECTILE.new() as PrototypeProjectile; root.add_child(projectile)
        projectile.setup(damage_target.global_position-Vector2(22,0),Vector2.RIGHT,null,Color("d95c65"),hostile_profile,"operators")
        for _i:int in range(5): await physics_frame
        _check(damage_target.health<before,"enemy-profile projectile damages operator health")
        damage_target.queue_free(); await process_frame

    var stage:=STAGE_SCENE.instantiate() as StoryStage01; root.add_child(stage); await process_frame
    var combat_ids:Array[String]=stage.debug_spawn_encounter_for_step(1); _check(combat_ids==["ENM_SITE7_RIFLE_01","ENM_SITE7_DRONE_01","ENM_SITE7_ABERRANT_01"],"Decon Corridor uses three distinct authored enemy identities")
    await process_frame
    var elite_ids:Array[String]=stage.debug_spawn_encounter_for_step(3); _check(elite_ids==["ENM_SITE7_SHIELD_01","ENM_SITE7_RIFLE_01"],"Containment Junction uses unique Shield elite plus rifle support")
    await process_frame
    var boss_ids:Array[String]=stage.debug_spawn_encounter_for_step(4); _check(boss_ids==["BOSS_SITE7_ANCHOR_01"],"Core C uses unique Signal Anchor Guardian boss")
    stage.queue_free(); await process_frame

    if failures.is_empty():
        print("M3_UNIQUE_ART_SMOKE: PASS"); quit(0); return
    print("M3_UNIQUE_ART_SMOKE: FAIL (%d)"%failures.size())
    for failure:String in failures: print(" - "+failure)
    quit(1)

func _check(condition:bool,label:String)->void:
    if condition: print("PASS: "+label)
    else: failures.append(label); push_error("FAIL: "+label)
