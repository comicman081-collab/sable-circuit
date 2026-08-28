extends CharacterBody2D
class_name EnemyActor

const Projectile := preload("res://scripts/combat/prototype_projectile.gd")
const TILE := 512.0

signal defeated(enemy: EnemyActor)

@export var enemy_id := "ENM_SITE7_RIFLE_01"
@export var max_health := 100.0

var health := 100.0
var art_profile: Dictionary = {}
var home_position := Vector2.ZERO
var _phase := 0.0
var _attack_cd := 0.8
var _hit_flash := 0.0
var _lunge_left := 0.0
var _orbit_sign := 1.0
var _aim_dir := Vector2.LEFT

var _exposed_left := 0.0
var _stagger_left := 0.0
var _status_source := ""
var _last_consumed_source := ""

# M11 deployment-only modifiers. They are applied after authored encounter HP is
# configured and never written to CampaignProgression.
var run_health_multiplier := 1.0
var run_damage_multiplier := 1.0
var run_speed_multiplier := 1.0
var run_attack_interval_multiplier := 1.0

var _visual_root: Node2D
var _hidden_master: Sprite2D
var _rig: Skeleton2D
var _rig_texture: Texture2D
var _bones: Dictionary = {}
var _parts: Dictionary = {}
var _base_positions: Dictionary = {}

func _ready() -> void:
    add_to_group("prototype_targets")
    add_to_group("m3_enemies")
    art_profile = ArtProfileRegistry.get_profile(enemy_id)
    health = max_health
    home_position = global_position
    _orbit_sign = -1.0 if abs(enemy_id.hash()) % 2 == 0 else 1.0
    _build_high_res_visual()
    queue_redraw()

func configure(id_value: String, hp: float = -1.0) -> void:
    enemy_id = id_value
    art_profile = ArtProfileRegistry.get_profile(enemy_id)
    if hp > 0.0:
        max_health = hp
    health = max_health
    _exposed_left=0.0; _stagger_left=0.0; _status_source=""; _last_consumed_source=""
    if is_node_ready():
        _rebuild_visual()

func apply_run_modifiers(modifiers: Dictionary) -> void:
    run_health_multiplier = clampf(float(modifiers.get("enemy_health_multiplier",1.0)),0.5,3.0)
    run_damage_multiplier = clampf(float(modifiers.get("enemy_damage_multiplier",1.0)),0.5,3.0)
    run_speed_multiplier = clampf(float(modifiers.get("enemy_speed_multiplier",1.0)),0.5,2.0)
    run_attack_interval_multiplier = clampf(float(modifiers.get("enemy_attack_interval_multiplier",1.0)),0.5,2.0)
    max_health *= run_health_multiplier
    health = max_health

func apply_damage(amount: float) -> void:
    if amount<=0.0 or health<=0.0: return
    health = maxf(0.0, health - amount)
    _hit_flash = 1.0
    if health <= 0.0:
        remove_from_group("prototype_targets")
        defeated.emit(self)
        queue_free()
        return
    queue_redraw()

func apply_exposed(duration: float, source: String = "") -> void:
    if health<=0.0: return
    _exposed_left=maxf(_exposed_left,maxf(0.0,duration))
    _status_source=source
    queue_redraw()

func is_exposed() -> bool:
    return _exposed_left>0.0

func apply_stagger(duration: float, source: String = "") -> void:
    if health<=0.0: return
    var applied:=maxf(0.0,duration)
    if "BOSS" in enemy_id or "ANCHOR" in enemy_id: applied=minf(applied,1.2)
    _stagger_left=maxf(_stagger_left,applied)
    _status_source=source
    velocity=Vector2.ZERO
    queue_redraw()

func is_staggered() -> bool:
    return _stagger_left>0.0

func consume_exposed_for_stagger(duration: float, source: String = "") -> bool:
    if not is_exposed(): return false
    _last_consumed_source=_status_source
    _exposed_left=0.0
    apply_stagger(duration,source)
    return true

func _physics_process(delta: float) -> void:
    _phase += delta
    _attack_cd = maxf(0.0, _attack_cd - delta)
    _hit_flash = move_toward(_hit_flash, 0.0, delta * 4.5)
    _exposed_left=maxf(0.0,_exposed_left-delta)
    _stagger_left=maxf(0.0,_stagger_left-delta)
    if _stagger_left>0.0:
        velocity=Vector2.ZERO
    else:
        var target := _nearest_operator()
        if target:
            _update_tactics(target, delta)
            velocity *= run_speed_multiplier
        else:
            velocity = velocity.move_toward(Vector2.ZERO, 260.0 * delta)
    move_and_slide()
    _animate_identity()
    if is_instance_valid(_rig):
        var tint:=Color.WHITE
        if _exposed_left>0.0: tint=tint.lerp(Color("8ff5e8"),0.26)
        if _stagger_left>0.0: tint=tint.lerp(Color("ffd17d"),0.32)
        _rig.modulate = tint.lerp(Color("ff8a8a"), _hit_flash * 0.68)
    queue_redraw()

func _nearest_operator() -> OperatorActor:
    var best: OperatorActor = null
    var best_d2: float = INF
    for node in get_tree().get_nodes_in_group("operators"):
        if node is OperatorActor and not node.is_downed():
            var d2: float = global_position.distance_squared_to(node.global_position)
            if d2 < best_d2:
                best_d2 = d2
                best = node
    return best

func _update_tactics(target: OperatorActor, delta: float) -> void:
    var to_target := target.global_position - global_position
    var dist: float = to_target.length()
    var dir := to_target.normalized() if dist > 0.001 else Vector2.RIGHT
    _aim_dir = dir
    var motion := str(art_profile.get("motion_profile", ""))
    if "RIFLE" in motion:
        var radial: float = 0.0
        if dist > 350.0: radial = 1.0
        elif dist < 250.0: radial = -0.8
        var side := Vector2(-dir.y, dir.x) * sin(_phase * 2.2) * 0.72
        velocity = (dir * radial + side).limit_length(1.0) * 105.0
        _try_attack(dir, 1.05)
    elif "SHIELD" in motion:
        velocity = dir * (72.0 if dist > 190.0 else 18.0)
        _try_attack(dir, 1.65)
    elif "DRONE" in motion:
        var tangent := Vector2(-dir.y, dir.x) * _orbit_sign
        var radial: float = clampf((dist - 300.0) / 140.0, -0.7, 0.7)
        velocity = (tangent * 0.9 + dir * radial).normalized() * 138.0
        _try_attack(dir, 0.78)
    elif "ABERRANT" in motion:
        if _lunge_left > 0.0:
            _lunge_left = maxf(0.0, _lunge_left - delta)
            velocity = dir * 330.0
        elif dist > 130.0:
            velocity = dir * 126.0
            if dist < 270.0 and _attack_cd <= 0.0:
                _lunge_left = 0.22
                _attack_cd = 1.35 * run_attack_interval_multiplier
        else:
            velocity = Vector2.ZERO
            _try_attack(dir, 1.25)
    elif "BOSS" in motion or "ANCHOR" in motion:
        velocity = Vector2(sin(_phase * 0.7), cos(_phase * 0.53)) * 18.0
        _try_attack(dir.rotated(sin(_phase * 0.8) * 0.18), 1.18)
    else:
        velocity = dir * 80.0
        _try_attack(dir, 1.2)

func _try_attack(dir: Vector2, interval: float) -> void:
    if _attack_cd > 0.0 or _stagger_left>0.0:
        return
    _attack_cd = interval * run_attack_interval_multiplier
    CombatFeedback.play_fire(get_tree(), art_profile)
    _spawn_projectile(dir)
    if "BOSS" in str(art_profile.get("projectile_profile", "")):
        _spawn_projectile(dir.rotated(-0.16))
        _spawn_projectile(dir.rotated(0.16))

func _spawn_projectile(dir: Vector2) -> void:
    var projectile := Projectile.new()
    get_tree().root.add_child(projectile)
    projectile.setup(global_position + dir * _muzzle_distance(), dir, self, _projectile_color(), art_profile, "operators")
    projectile.damage *= run_damage_multiplier

func _muzzle_distance() -> float:
    if "BOSS" in enemy_id: return 92.0
    if "SHIELD" in enemy_id: return 44.0
    if "DRONE" in enemy_id: return 38.0
    return 34.0

func _projectile_color() -> Color:
    var p := str(art_profile.get("projectile_profile", ""))
    if "RIFLE" in p: return Color("d95c65")
    if "SHIELD" in p: return Color("e2a94e")
    if "DRONE" in p: return Color("d9577d")
    if "ABERRANT" in p: return Color("a055c5")
    if "ANCHOR" in p: return Color("9b7cff")
    return Color.WHITE

func _rebuild_visual() -> void:
    if is_instance_valid(_visual_root):
        _visual_root.queue_free()
    _bones.clear(); _parts.clear(); _base_positions.clear(); _rig_texture = null
    _build_high_res_visual()

func _build_high_res_visual() -> void:
    _visual_root = Node2D.new()
    _visual_root.name = "HighResVisualRoot"
    add_child(_visual_root)
    _hidden_master = Sprite2D.new(); _hidden_master.name="UniqueMasterSprite"; _hidden_master.visible=false
    var master_path := str(art_profile.get("master_asset", ""))
    if not master_path.is_empty() and ResourceLoader.exists("res://" + master_path): _hidden_master.texture=load("res://"+master_path) as Texture2D
    _visual_root.add_child(_hidden_master)
    var rig_path := str(art_profile.get("rig_sheet", ""))
    if not rig_path.is_empty() and ResourceLoader.exists("res://" + rig_path): _rig_texture=load("res://"+rig_path) as Texture2D
    _rig=Skeleton2D.new(); _rig.name="UniqueLayerRig"; _visual_root.add_child(_rig)
    if "RIFLE" in enemy_id: _build_rifle_rig()
    elif "SHIELD" in enemy_id: _build_shield_rig()
    elif "DRONE" in enemy_id: _build_drone_rig()
    elif "ABERRANT" in enemy_id: _build_aberrant_rig()
    elif "BOSS" in enemy_id: _build_boss_rig()
    for key in _bones.keys():
        var bone: Bone2D=_bones[key]; bone.rest=bone.transform; _base_positions[key]=bone.position

func _build_rifle_rig() -> void:
    var body:=_bone(_rig,"body",Vector2(0,-42)); var head:=_bone(body,"head",Vector2(0,-28)); var arm_l:=_bone(body,"arm_L",Vector2(-10,-2)); var arm_r:=_bone(body,"arm_R",Vector2(10,-2)); var leg_l:=_bone(body,"leg_L",Vector2(-7,23)); var shin_l:=_bone(leg_l,"shin_L",Vector2(0,18)); var leg_r:=_bone(body,"leg_R",Vector2(7,23)); var shin_r:=_bone(leg_r,"shin_R",Vector2(0,18)); var weapon:=_bone(body,"weapon",Vector2(3,0))
    _part(head,"Head",0,0,.115,3); _part(body,"RadioPack",1,0,.105,0); _part(body,"Torso",2,0,.108,1); _part(body,"Pelvis",3,0,.105,1); _part(arm_l,"ArmL",0,1,.105,2); _part(arm_r,"ArmR",2,1,.105,2); _part(leg_l,"ThighL",0,2,.105,0); _part(shin_l,"ShinL",1,2,.105,0); _part(leg_r,"ThighR",2,2,.105,0); _part(shin_r,"ShinR",3,2,.105,0); _part(weapon,"Rifle",2,3,.11,5)

func _build_shield_rig() -> void:
    var body:=_bone(_rig,"body",Vector2(0,-45)); var head:=_bone(body,"head",Vector2(5,-31)); var shield:=_bone(body,"shield",Vector2(-19,5)); var arm:=_bone(body,"hydraulic_arm",Vector2(14,-2)); var weapon:=_bone(arm,"weapon",Vector2(18,3)); var leg_l:=_bone(body,"leg_L",Vector2(-4,24)); var leg_r:=_bone(body,"leg_R",Vector2(9,24))
    _part(head,"WedgeHelmet",0,0,.12,4); _part(body,"Torso",1,0,.12,1); _part(body,"Pelvis",2,0,.11,1); _part(shield,"SlabShield",3,0,.13,6); _part(arm,"HydraulicArm",0,1,.12,3); _part(leg_l,"LegL",2,1,.115,0); _part(leg_r,"LegR",3,1,.115,0); _part(weapon,"RamPistol",2,2,.115,5); _part(body,"Cable",0,3,.11,2)

func _build_drone_rig() -> void:
    var chassis:=_bone(_rig,"chassis",Vector2(0,-56)); var eyes:=_bone(chassis,"sensor_cluster",Vector2(0,2)); var fins:=_bone(chassis,"fins",Vector2(0,-2)); var mast:=_bone(chassis,"mast",Vector2(0,-16)); var thruster:=_bone(chassis,"thruster",Vector2(0,20)); var emitter:=_bone(chassis,"emitter",Vector2(0,10))
    _part(chassis,"Crescent",0,0,.14,2); _part(eyes,"Eyes",1,0,.13,4); _part(fins,"Fins",2,0,.14,1); _part(mast,"Mast",3,0,.11,0); _part(thruster,"Thruster",0,1,.11,0); _part(emitter,"ScanArc",1,1,.12,3); _part(emitter,"Gun",0,2,.11,5); _part(chassis,"Glow",3,3,.12,0)

func _build_aberrant_rig() -> void:
    var torso:=_bone(_rig,"torso",Vector2(0,-42)); var skull:=_bone(torso,"skull",Vector2(0,-30)); var arm_l:=_bone(torso,"forelimb_L",Vector2(-13,-1)); var arm_r:=_bone(torso,"forelimb_R",Vector2(13,-1)); var leg_l:=_bone(torso,"leg_L",Vector2(-8,22)); var leg_r:=_bone(torso,"leg_R",Vector2(8,22)); var tail:=_bone(torso,"tail",Vector2(8,20)); var gland:=_bone(torso,"gland",Vector2(0,7))
    _part(skull,"SplitSkull",0,0,.12,4); _part(torso,"Torso",1,0,.112,1); _part(torso,"Pelvis",2,0,.105,1); _part(arm_r,"ForelimbR",3,0,.12,3); _part(arm_l,"ForelimbL",0,1,.12,3); _part(leg_l,"LegL",1,1,.115,0); _part(leg_r,"LegR",2,1,.115,0); _part(tail,"BioTail",1,2,.12,0); _part(gland,"Gland",3,1,.10,2)

func _build_boss_rig() -> void:
    var ring:=_bone(_rig,"ring",Vector2(0,-110)); var iris:=_bone(ring,"iris",Vector2.ZERO); var p1:=_bone(ring,"pylon_1",Vector2(-54,-54)); var p2:=_bone(ring,"pylon_2",Vector2(54,-54)); var p3:=_bone(ring,"pylon_3",Vector2(-54,54)); var p4:=_bone(ring,"pylon_4",Vector2(54,54)); var a1:=_bone(ring,"arm_1",Vector2(-58,-20)); var a2:=_bone(ring,"arm_2",Vector2(58,-20)); var a3:=_bone(ring,"arm_3",Vector2(-58,38)); var a4:=_bone(ring,"arm_4",Vector2(58,38)); var anchor:=_bone(ring,"anchor",Vector2(0,92)); var distortion:=_bone(ring,"distortion",Vector2.ZERO)
    _part(ring,"OuterRing",0,0,.27,1); _part(iris,"SignalIris",1,0,.24,5); _part(p1,"Pylon1",2,0,.18,2); _part(p2,"Pylon2",3,0,.18,2); _part(a1,"Arm1",0,1,.18,3); _part(a2,"Arm2",1,1,.18,3); _part(a3,"Arm3",2,1,.18,3); _part(a4,"Arm4",3,1,.18,3); _part(p3,"Pylon3",0,2,.18,2); _part(p4,"Pylon4",1,2,.18,2); _part(anchor,"Anchor",0,3,.18,0); _part(distortion,"Distortion",1,3,.24,0)

func _bone(parent: Node, bone_name: String, pos: Vector2) -> Bone2D:
    var bone:=Bone2D.new(); bone.name=bone_name; bone.position=pos; bone.set_autocalculate_length_and_angle(false); parent.add_child(bone); _bones[bone_name]=bone; return bone

func _part(parent:Node2D, part_name:String, col:int, row:int, scale_value:float, z:int) -> Sprite2D:
    var sprite:=Sprite2D.new(); sprite.name=part_name; sprite.texture=_rig_texture; sprite.region_enabled=true; sprite.region_rect=Rect2(col*TILE,row*TILE,TILE,TILE); sprite.centered=true; sprite.scale=Vector2.ONE*scale_value; sprite.z_index=z; sprite.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS; parent.add_child(sprite); _parts[part_name]=sprite; return sprite

func _animate_identity() -> void:
    if not is_instance_valid(_rig): return
    var motion:=str(art_profile.get("motion_profile", ""))
    if "RIFLE" in motion: _animate_rifle()
    elif "SHIELD" in motion: _animate_shield()
    elif "DRONE" in motion: _animate_drone()
    elif "ABERRANT" in motion: _animate_aberrant()
    elif "BOSS" in motion or "ANCHOR" in motion: _animate_boss()

func _animate_rifle() -> void:
    var gait:float=sin(_phase*7.2)*0.28*minf(1.0,velocity.length()/maxf(1.0,105.0*run_speed_multiplier)); (_bones["leg_L"] as Bone2D).rotation=gait; (_bones["leg_R"] as Bone2D).rotation=-gait; (_bones["shin_L"] as Bone2D).rotation=-gait*.55; (_bones["shin_R"] as Bone2D).rotation=gait*.55; (_bones["body"] as Bone2D).rotation=sin(_phase*3.6)*.018; (_bones["weapon"] as Bone2D).rotation=_aim_dir.angle(); (_bones["arm_L"] as Bone2D).rotation=_aim_dir.angle()+.10; (_bones["arm_R"] as Bone2D).rotation=_aim_dir.angle()-.08
func _animate_shield() -> void:
    var stomp:float=absf(sin(_phase*4.1)); (_bones["body"] as Bone2D).position=(_base_positions["body"] as Vector2)+Vector2(0,stomp*3.2); (_bones["shield"] as Bone2D).rotation=-.06+sin(_phase*2.0)*.025; (_bones["hydraulic_arm"] as Bone2D).rotation=_aim_dir.angle()*.45; (_bones["weapon"] as Bone2D).rotation=_aim_dir.angle()*.55
func _animate_drone() -> void:
    (_bones["chassis"] as Bone2D).position=(_base_positions["chassis"] as Vector2)+Vector2(0,sin(_phase*3.8)*7.0); (_bones["chassis"] as Bone2D).rotation=sin(_phase*2.6)*.10; (_bones["fins"] as Bone2D).rotation=-sin(_phase*3.3)*.13; (_bones["thruster"] as Bone2D).scale=Vector2(1.0,1.0+sin(_phase*8.0)*.18); (_bones["sensor_cluster"] as Bone2D).rotation=sin(_phase*1.7)*.09
func _animate_aberrant() -> void:
    var gait:float=sin(_phase*6.6); (_bones["torso"] as Bone2D).position=(_base_positions["torso"] as Vector2)+Vector2(0,absf(gait)*4.5); (_bones["forelimb_L"] as Bone2D).rotation=.42+gait*.34; (_bones["forelimb_R"] as Bone2D).rotation=-.38-gait*.31; (_bones["leg_L"] as Bone2D).rotation=-gait*.38; (_bones["leg_R"] as Bone2D).rotation=gait*.38; (_bones["tail"] as Bone2D).rotation=sin(_phase*3.1-.8)*.32; (_bones["skull"] as Bone2D).rotation=-sin(_phase*3.3)*.07
func _animate_boss() -> void:
    var ring:=_bones["ring"] as Bone2D; ring.position=(_base_positions["ring"] as Vector2)+Vector2(0,sin(_phase*1.2)*9.0); ring.rotation=sin(_phase*.72)*.035; (_bones["iris"] as Bone2D).rotation=-_phase*.22; (_bones["distortion"] as Bone2D).rotation=_phase*.15
    for i in range(1,5):
        var arm:=_bones["arm_%d"%i] as Bone2D; arm.rotation=sin(_phase*1.35+float(i)*.8)*.18
        var pylon:=_bones["pylon_%d"%i] as Bone2D; pylon.scale=Vector2.ONE*(1.0+sin(_phase*1.1+float(i))*.035)

func _draw() -> void:
    var ratio:=clampf(health/maxf(1.0,max_health),0.0,1.0); var width:=58.0 if "BOSS" not in enemy_id else 130.0; var bar_y:=-82.0 if "BOSS" not in enemy_id else -242.0
    var radius:=30.0 if "BOSS" not in enemy_id else 82.0; draw_circle(Vector2(0,5),radius,Color(0.02,0.03,0.04,0.26),true); draw_rect(Rect2(-width*.5,bar_y,width,5),Color("172028"),true); draw_rect(Rect2(-width*.5+1,bar_y+1,(width-2)*ratio,3),_projectile_color(),true)
    if _exposed_left>0.0:
        var sr:=radius+8.0; draw_arc(Vector2(0,5),sr,-2.7,-0.45,28,Color("70eadb",0.82),2.3); draw_arc(Vector2(0,5),sr,0.45,2.7,28,Color("70eadb",0.48),1.4)
    if _stagger_left>0.0:
        draw_arc(Vector2(0,5),radius+13.0,0.0,TAU,40,Color("ffc567",0.78),3.2)
        draw_line(Vector2(-12,bar_y-8),Vector2(12,bar_y-8),Color("ffdca0",0.85),2.0)

func debug_status_contract() -> Dictionary:
    return {"exposed":is_exposed(),"exposed_left":_exposed_left,"staggered":is_staggered(),"stagger_left":_stagger_left,"status_source":_status_source,"last_consumed_source":_last_consumed_source}

func debug_run_modifier_contract() -> Dictionary:
    return {
        "enemy_health_multiplier":run_health_multiplier,
        "enemy_damage_multiplier":run_damage_multiplier,
        "enemy_speed_multiplier":run_speed_multiplier,
        "enemy_attack_interval_multiplier":run_attack_interval_multiplier,
        "max_health":max_health,
        "health":health
    }
