extends Node2D
class_name OperatorVisual

var accent_color := Color("69d2ff")
var operator_label := "ALPHA"
var art_profile: Dictionary = {}
var facing_sector := 0
var speed_norm := 0.0
var move_world := Vector2.ZERO
var aim_world := Vector2.RIGHT
var is_combat := true
var reload_progress := 0.0
var is_reloading := false

var _phase := 0.0
var _recoil := 0.0
var _evade_flash := 0.0
var _selected := false

var _cadence := 9.2
var _gait_amp := 0.50
var _bob_amp := 2.8
var _torso_sway := 0.035
var _head_lag := 0.60
var _recoil_amp := 0.08
var _recoil_recover := 8.0
var _reload_fold_amp := 0.55
var _evade_x := 0.14
var _evade_y := 0.08

var skeleton: Skeleton2D
var animation_player: AnimationPlayer
var animation_tree: AnimationTree
var muzzle_socket: Node2D

var _bones: Dictionary = {}
var _base_positions: Dictionary = {}
var _secondary_parts: Array[Node2D] = []
var _identity := "GENERIC"

func _ready() -> void:
    _build_runtime_rig()
    queue_redraw()

func configure(label: String, color: Color, profile: Dictionary = {}) -> void:
    operator_label = label
    accent_color = color
    art_profile = profile.duplicate(true)
    _identity = str(art_profile.get("visual_profile", label)).to_upper()
    _apply_motion_profile()
    if is_node_ready():
        _rebuild_runtime_rig()
        queue_redraw()

func set_selected(value: bool) -> void:
    _selected = value
    queue_redraw()

func set_runtime_state(move_vec: Vector2, aim_vec: Vector2, normalized_speed: float, combat: bool, sector: int, reloading: bool, reload_t: float) -> void:
    move_world = move_vec
    if aim_vec.length_squared() > 0.0001:
        aim_world = aim_vec.normalized()
    speed_norm = clampf(normalized_speed, 0.0, 1.35)
    is_combat = combat
    facing_sector = sector
    is_reloading = reloading
    reload_progress = clampf(reload_t, 0.0, 1.0)

func trigger_fire() -> void:
    _recoil = 1.0

func trigger_evade() -> void:
    _evade_flash = 1.0

func get_muzzle_global_position() -> Vector2:
    return muzzle_socket.global_position if is_instance_valid(muzzle_socket) else global_position

func _process(delta: float) -> void:
    _phase += delta * lerpf(3.0, _cadence, clampf(speed_norm, 0.0, 1.0))
    _recoil = move_toward(_recoil, 0.0, delta * _recoil_recover)
    _evade_flash = move_toward(_evade_flash, 0.0, delta * 5.0)
    _pose_rig()
    queue_redraw()

func _apply_motion_profile() -> void:
    match str(art_profile.get("motion_profile", "")):
        "MOT_ASTER_01":
            _cadence=11.2; _gait_amp=0.58; _bob_amp=1.9; _torso_sway=0.026; _head_lag=0.48; _recoil_amp=0.060; _recoil_recover=12.0; _reload_fold_amp=0.48; _evade_x=0.18; _evade_y=0.06
        "MOT_ROOK_01":
            _cadence=7.0; _gait_amp=0.43; _bob_amp=3.8; _torso_sway=0.062; _head_lag=0.72; _recoil_amp=0.145; _recoil_recover=5.2; _reload_fold_amp=0.78; _evade_x=0.10; _evade_y=0.12
        "MOT_MICA_01":
            _cadence=8.4; _gait_amp=0.38; _bob_amp=1.35; _torso_sway=0.020; _head_lag=0.34; _recoil_amp=0.042; _recoil_recover=7.0; _reload_fold_amp=0.40; _evade_x=0.12; _evade_y=0.05

func _rebuild_runtime_rig() -> void:
    if is_instance_valid(animation_tree): animation_tree.queue_free()
    if is_instance_valid(animation_player): animation_player.queue_free()
    if is_instance_valid(skeleton): skeleton.queue_free()
    skeleton=null; animation_player=null; animation_tree=null; muzzle_socket=null
    _bones.clear(); _base_positions.clear(); _secondary_parts.clear()
    _build_runtime_rig()

func _build_runtime_rig() -> void:
    skeleton = Skeleton2D.new(); skeleton.name = "Skeleton2D"; add_child(skeleton)
    var pelvis := _bone(skeleton, "pelvis", Vector2(0, -28))
    var torso := _bone(pelvis, "torso", Vector2(0, -20))
    var head := _bone(torso, "head", Vector2(0, -21))
    var upper_l := _bone(torso, "upper_arm_L", Vector2(-12, -3))
    var lower_l := _bone(upper_l, "lower_arm_L", Vector2(15, 0))
    var upper_r := _bone(torso, "upper_arm_R", Vector2(12, -3))
    var lower_r := _bone(upper_r, "lower_arm_R", Vector2(15, 0))
    var weapon := _bone(torso, "weapon_root", Vector2(1, 0))
    var thigh_l := _bone(pelvis, "thigh_L", Vector2(-7, 5))
    var shin_l := _bone(thigh_l, "shin_L", Vector2(0, 18))
    var foot_l := _bone(shin_l, "foot_L", Vector2(0, 16))
    var thigh_r := _bone(pelvis, "thigh_R", Vector2(7, 5))
    var shin_r := _bone(thigh_r, "shin_R", Vector2(0, 18))
    var foot_r := _bone(shin_r, "foot_R", Vector2(0, 16))

    if "ASTER" in _identity:
        _build_aster_parts(pelvis, torso, head, upper_l, lower_l, upper_r, lower_r, weapon, thigh_l, shin_l, foot_l, thigh_r, shin_r, foot_r)
    elif "ROOK" in _identity:
        _build_rook_parts(pelvis, torso, head, upper_l, lower_l, upper_r, lower_r, weapon, thigh_l, shin_l, foot_l, thigh_r, shin_r, foot_r)
    elif "MICA" in _identity:
        _build_mica_parts(pelvis, torso, head, upper_l, lower_l, upper_r, lower_r, weapon, thigh_l, shin_l, foot_l, thigh_r, shin_r, foot_r)
    else:
        _build_generic_parts(pelvis, torso, head, upper_l, lower_l, upper_r, lower_r, weapon, thigh_l, shin_l, foot_l, thigh_r, shin_r, foot_r)

    animation_player = AnimationPlayer.new(); animation_player.name = "AnimationPlayer"; add_child(animation_player)
    var library := AnimationLibrary.new()
    for clip_name in ["IdleExplore", "Move", "FireSingle", "Reload", "Evade"]:
        var anim := Animation.new(); anim.length = 1.0
        anim.loop_mode = Animation.LOOP_LINEAR if clip_name in ["IdleExplore", "Move"] else Animation.LOOP_NONE
        library.add_animation(clip_name, anim)
    animation_player.add_animation_library("", library)
    animation_tree = AnimationTree.new(); animation_tree.name = "AnimationTree"; add_child(animation_tree)
    animation_tree.anim_player = NodePath("../AnimationPlayer")
    var root_anim := AnimationNodeAnimation.new(); root_anim.animation = &"IdleExplore"
    animation_tree.tree_root = root_anim; animation_tree.active = true

    for bone_name in _bones.keys():
        var bone: Bone2D = _bones[bone_name]
        bone.rest = bone.transform
        _base_positions[bone_name] = bone.position

func _build_aster_parts(pelvis:Bone2D, torso:Bone2D, head:Bone2D, ul:Bone2D, ll:Bone2D, ur:Bone2D, lr:Bone2D, weapon:Bone2D, tl:Bone2D, sl:Bone2D, fl:Bone2D, tr:Bone2D, sr:Bone2D, fr:Bone2D) -> void:
    _rect_part(pelvis,"PelvisPart",Vector2(20,13),Vector2(0,3),Color("20566d"))
    _poly_part(torso,"Jacket",PackedVector2Array([Vector2(-15,-15),Vector2(14,-13),Vector2(18,13),Vector2(-12,17),Vector2(-19,4)]),Color("2c7693"))
    _circle_part(head,"HeadPart",16.5,Vector2.ZERO,Color("f1d7c7")); _poly_part(head,"Hair",PackedVector2Array([Vector2(-18,-9),Vector2(-8,-20),Vector2(16,-17),Vector2(20,-5),Vector2(6,-9),Vector2(-6,3)]),Color("16475e"))
    var tail:=_poly_part(head,"CometTail",PackedVector2Array([Vector2(10,-10),Vector2(32,-3),Vector2(45,14),Vector2(26,10),Vector2(14,22)]),Color("247492")); _secondary_parts.append(tail)
    _limb_part(ul,"UpperArmL",17,6,Color("2b6f89")); _limb_part(ll,"LowerArmL",15,5,Color("e8cdbd")); _limb_part(ur,"UpperArmR",17,7,Color("55b8d8")); _limb_part(lr,"LowerArmR",15,5,Color("e8cdbd"))
    var shoulder:=_poly_part(torso,"RightShoulderPlate",PackedVector2Array([Vector2(8,-12),Vector2(24,-7),Vector2(19,5),Vector2(7,2)]),Color("79d8ff")); shoulder.z_index=2
    _vertical_limb_part(tl,"ThighL",20,7,Color("173746")); _vertical_limb_part(sl,"ShinL",18,6,Color("466775")); _vertical_limb_part(fl,"FootL",12,8,Color("102530")); _vertical_limb_part(tr,"ThighR",20,7,Color("173746")); _vertical_limb_part(sr,"ShinR",18,6,Color("466775")); _vertical_limb_part(fr,"FootR",12,8,Color("102530"))
    _poly_part(weapon,"PrecisionRifle",PackedVector2Array([Vector2(0,-4),Vector2(50,-3),Vector2(58,0),Vector2(49,4),Vector2(15,5),Vector2(8,10),Vector2(3,8)]),Color("d7edf5")); _rect_part(weapon,"RifleCore",Vector2(17,3),Vector2(29,-1),Color("79d8ff")); _make_sockets(weapon,58.0,17.0)

func _build_rook_parts(pelvis:Bone2D, torso:Bone2D, head:Bone2D, ul:Bone2D, ll:Bone2D, ur:Bone2D, lr:Bone2D, weapon:Bone2D, tl:Bone2D, sl:Bone2D, fl:Bone2D, tr:Bone2D, sr:Bone2D, fr:Bone2D) -> void:
    _rect_part(pelvis,"PelvisPart",Vector2(30,17),Vector2(0,4),Color("4b292c")); _poly_part(torso,"HeavyTorso",PackedVector2Array([Vector2(-20,-15),Vector2(20,-14),Vector2(24,14),Vector2(-22,17)]),Color("7c3e36"))
    var mantle:=_poly_part(torso,"Mantle",PackedVector2Array([Vector2(-30,-16),Vector2(30,-14),Vector2(36,-3),Vector2(20,2),Vector2(-24,3),Vector2(-36,-4)]),Color("4a272b")); _secondary_parts.append(mantle)
    _circle_part(head,"HeadPart",17.5,Vector2.ZERO,Color("efc9b5")); _rect_part(head,"BluntBob",Vector2(38,15),Vector2(0,-8),Color("3c2429"))
    _limb_part(ul,"HeavyGauntletUpper",19,10,Color("5a3031")); _limb_part(ll,"HeavyGauntletLower",18,12,Color("ff9566")); _limb_part(ur,"UpperArmR",19,9,Color("6e3835")); _limb_part(lr,"LowerArmR",17,7,Color("efc9b5"))
    _vertical_limb_part(tl,"ThighL",22,10,Color("402329")); _vertical_limb_part(sl,"ShinL",19,9,Color("553037")); _vertical_limb_part(fl,"BootL",14,12,Color("211719")); _vertical_limb_part(tr,"ThighR",22,10,Color("402329")); _vertical_limb_part(sr,"ShinR",19,9,Color("553037")); _vertical_limb_part(fr,"BootR",14,12,Color("211719"))
    _poly_part(weapon,"Scattergun",PackedVector2Array([Vector2(-2,-7),Vector2(47,-7),Vector2(56,-2),Vector2(55,7),Vector2(12,8),Vector2(4,14),Vector2(-3,11)]),Color("6b4638")); _rect_part(weapon,"ScatterVent",Vector2(23,4),Vector2(29,-1),Color("ffe09a")); _make_sockets(weapon,56.0,18.0)

func _build_mica_parts(pelvis:Bone2D, torso:Bone2D, head:Bone2D, ul:Bone2D, ll:Bone2D, ur:Bone2D, lr:Bone2D, weapon:Bone2D, tl:Bone2D, sl:Bone2D, fl:Bone2D, tr:Bone2D, sr:Bone2D, fr:Bone2D) -> void:
    _rect_part(pelvis,"PelvisPart",Vector2(22,14),Vector2(0,3),Color("22513f")); _poly_part(torso,"TechCoat",PackedVector2Array([Vector2(-16,-15),Vector2(16,-14),Vector2(20,15),Vector2(-18,16)]),Color("3d7658"))
    var coat_l:=_poly_part(pelvis,"CoatTailL",PackedVector2Array([Vector2(-10,6),Vector2(-2,7),Vector2(-5,44),Vector2(-15,53)]),Color("2b654c")); var coat_r:=_poly_part(pelvis,"CoatTailR",PackedVector2Array([Vector2(2,7),Vector2(11,5),Vector2(17,51),Vector2(6,43)]),Color("367a59")); _secondary_parts.append(coat_l); _secondary_parts.append(coat_r)
    _circle_part(head,"HeadPart",16.5,Vector2.ZERO,Color("efd2bf")); _poly_part(head,"Hair",PackedVector2Array([Vector2(-18,-9),Vector2(-10,-20),Vector2(15,-17),Vector2(19,-5),Vector2(8,-7),Vector2(-8,3)]),Color("335b49")); var braid:=_circle_part(head,"SideBraid",6.0,Vector2(19,13),Color("3d6855")); _secondary_parts.append(braid)
    var fin_l:=_poly_part(torso,"SensorFinL",PackedVector2Array([Vector2(-12,-12),Vector2(-25,-35),Vector2(-18,-40),Vector2(-5,-14)]),Color("7cf4e7")); var fin_r:=_poly_part(torso,"SensorFinR",PackedVector2Array([Vector2(10,-12),Vector2(24,-36),Vector2(31,-29),Vector2(17,-8)]),Color("a8f07a")); _secondary_parts.append(fin_l); _secondary_parts.append(fin_r)
    _limb_part(ul,"UpperArmL",17,6,Color("336d50")); _limb_part(ll,"LowerArmL",15,5,Color("edd2bf")); _limb_part(ur,"UpperArmR",17,6,Color("2d654c")); _limb_part(lr,"LowerArmR",15,5,Color("edd2bf"))
    _vertical_limb_part(tl,"ThighL",20,7,Color("17372d")); _vertical_limb_part(sl,"ShinL",18,6,Color("315847")); _vertical_limb_part(fl,"FootL",12,8,Color("10261f")); _vertical_limb_part(tr,"ThighR",20,7,Color("17372d")); _vertical_limb_part(sr,"ShinR",18,6,Color("315847")); _vertical_limb_part(fr,"FootR",12,8,Color("10261f"))
    _poly_part(weapon,"SensorCarbine",PackedVector2Array([Vector2(0,-5),Vector2(41,-5),Vector2(50,0),Vector2(40,6),Vector2(8,7),Vector2(2,11),Vector2(-3,8)]),Color("24483e")); _circle_part(weapon,"EmitterRing",8.0,Vector2(35,0),Color("7cf4e7"),false,2.5); _make_sockets(weapon,50.0,15.0)

func _build_generic_parts(pelvis:Bone2D, torso:Bone2D, head:Bone2D, ul:Bone2D, ll:Bone2D, ur:Bone2D, lr:Bone2D, weapon:Bone2D, tl:Bone2D, sl:Bone2D, fl:Bone2D, tr:Bone2D, sr:Bone2D, fr:Bone2D) -> void:
    _rect_part(pelvis,"PelvisPart",Vector2(23,15),Vector2(0,3),accent_color.darkened(0.32)); _rect_part(torso,"TorsoPart",Vector2(29,29),Vector2(0,1),accent_color.darkened(0.10)); _circle_part(head,"HeadPart",17.0,Vector2.ZERO,Color("f1d7c7")); _rect_part(head,"HairPart",Vector2(36,13),Vector2(0,-7),accent_color.darkened(0.55))
    _limb_part(ul,"UpperArmL",17,7,accent_color); _limb_part(ll,"LowerArmL",15,6,Color("e8cdbd")); _limb_part(ur,"UpperArmR",17,7,accent_color); _limb_part(lr,"LowerArmR",15,6,Color("e8cdbd")); _vertical_limb_part(tl,"ThighL",20,8,accent_color.darkened(0.35)); _vertical_limb_part(sl,"ShinL",18,7,Color("4e5a66")); _vertical_limb_part(fl,"FootL",12,9,Color("202936")); _vertical_limb_part(tr,"ThighR",20,8,accent_color.darkened(0.35)); _vertical_limb_part(sr,"ShinR",18,7,Color("4e5a66")); _vertical_limb_part(fr,"FootR",12,9,Color("202936")); _rect_part(weapon,"WeaponPart",Vector2(44,8),Vector2(22,0),Color("28333d")); _make_sockets(weapon,46.0,15.0)

func _make_sockets(weapon: Bone2D, muzzle_x: float, support_x: float) -> void:
    muzzle_socket=Node2D.new(); muzzle_socket.name="muzzle_socket"; muzzle_socket.position=Vector2(muzzle_x,0); weapon.add_child(muzzle_socket)
    var support:=Node2D.new(); support.name="support_hand_socket"; support.position=Vector2(support_x,0); weapon.add_child(support)
    var fx:=Node2D.new(); fx.name="fx_root"; weapon.add_child(fx)

func _bone(parent: Node, bone_name: String, pos: Vector2) -> Bone2D:
    var bone:=Bone2D.new(); bone.name=bone_name; bone.position=pos; bone.set_autocalculate_length_and_angle(false); parent.add_child(bone); _bones[bone_name]=bone; return bone
func _rect_part(parent:Node2D,n:String,size:Vector2,center:Vector2,color:Color)->Polygon2D:
    return _poly_part(parent,n,PackedVector2Array([center+Vector2(-size.x*.5,-size.y*.5),center+Vector2(size.x*.5,-size.y*.5),center+Vector2(size.x*.5,size.y*.5),center+Vector2(-size.x*.5,size.y*.5)]),color)
func _poly_part(parent:Node2D,n:String,points:PackedVector2Array,color:Color)->Polygon2D:
    var p:=Polygon2D.new(); p.name=n; p.polygon=points; p.color=color; parent.add_child(p); return p
func _circle_part(parent:Node2D,n:String,r:float,center:Vector2,color:Color,filled:bool=true,width:float=1.0)->Polygon2D:
    var pts:=PackedVector2Array(); for i in range(20): pts.append(center+Vector2.RIGHT.rotated(TAU*float(i)/20.0)*r)
    var p:=Polygon2D.new(); p.name=n; p.polygon=pts; p.color=color if filled else Color(color,0.22); parent.add_child(p)
    if not filled:
        var line:=Line2D.new(); line.width=width; line.default_color=color; line.closed=true; line.points=pts; parent.add_child(line)
    return p
func _limb_part(parent:Node2D,n:String,length:float,width:float,color:Color)->Polygon2D: return _rect_part(parent,n,Vector2(length,width),Vector2(length*.5,0),color)
func _vertical_limb_part(parent:Node2D,n:String,length:float,width:float,color:Color)->Polygon2D: return _rect_part(parent,n,Vector2(width,length),Vector2(0,length*.5),color)

func _pose_rig() -> void:
    if _bones.is_empty(): return
    var pelvis:Bone2D=_bones["pelvis"]; var torso:Bone2D=_bones["torso"]; var head:Bone2D=_bones["head"]
    var tl:Bone2D=_bones["thigh_L"]; var tr:Bone2D=_bones["thigh_R"]; var sl:Bone2D=_bones["shin_L"]; var sr:Bone2D=_bones["shin_R"]
    var ul:Bone2D=_bones["upper_arm_L"]; var ur:Bone2D=_bones["upper_arm_R"]; var ll:Bone2D=_bones["lower_arm_L"]; var lr:Bone2D=_bones["lower_arm_R"]; var weapon:Bone2D=_bones["weapon_root"]
    var gait:=sin(_phase)*_gait_amp*minf(speed_norm,1.0); var bob:=absf(sin(_phase))*_bob_amp*minf(speed_norm,1.0)
    pelvis.position=(_base_positions["pelvis"] as Vector2)+Vector2(0,bob); torso.rotation=sin(_phase*.5)*_torso_sway*minf(speed_norm,1.0); head.rotation=-torso.rotation*_head_lag+sin(_phase*.43)*.012
    tl.rotation=gait; tr.rotation=-gait; sl.rotation=-gait*.62; sr.rotation=gait*.62
    var aim:=aim_world.angle(); var fold:=sin(reload_progress*PI) if is_reloading else 0.0; var kick:=_recoil*_recoil_amp
    if "ROOK" in _identity:
        ur.rotation=aim-.16-kick-fold*.68; lr.rotation=.14+kick*.45+fold*.82; ul.rotation=aim+.04-kick*.5+fold*.18; ll.rotation=-.10+fold*.42
    elif "MICA" in _identity:
        ur.rotation=aim-.06-kick-fold*.38; lr.rotation=.04+fold*.52; ul.rotation=aim+.18-kick*.45+fold*.22; ll.rotation=-.24+fold*.48
    else:
        ur.rotation=aim-.10-kick-fold*.55; lr.rotation=.08+kick*.5+fold*.75; ul.rotation=aim+.13-kick*.7+fold*.30; ll.rotation=-.18+fold*.55
    weapon.rotation=aim-kick+fold*_reload_fold_amp; weapon.position=(_base_positions["weapon_root"] as Vector2)-aim_world*(_recoil*(6.0 if "ROOK" in _identity else 3.5))+Vector2(0,fold*5.0)
    for i in range(_secondary_parts.size()):
        var part:=_secondary_parts[i]; if is_instance_valid(part): part.rotation=sin(_phase*.55-float(i)*.7)*(.045+.025*speed_norm)
    skeleton.scale=Vector2(1.0+_evade_flash*_evade_x,1.0-_evade_flash*_evade_y) if _evade_flash>0.0 else Vector2.ONE

func _draw() -> void:
    var ring:=accent_color if _selected else Color(0.25,0.30,0.36,0.55); draw_arc(Vector2(0,4),24.0,0.0,TAU,32,ring,2.5 if _selected else 1.0)
    if _selected: draw_arc(Vector2(0,4),29.0,-PI*.85,-PI*.15,18,Color(accent_color,0.65),2.0)
    if _recoil>.12 and is_instance_valid(muzzle_socket):
        var m:=to_local(muzzle_socket.global_position)
        if "ASTER" in _identity:
            draw_line(m,m+aim_world*(25+_recoil*14),Color("e8f7ff"),2.2); draw_circle(m+aim_world*8,3.0,Color("ffcf70"))
        elif "ROOK" in _identity:
            draw_arc(m,8+_recoil*10,-.6,.6,12,Color("ffb06f"),5.0); draw_line(m,m+aim_world*18,Color("ffe09a"),7.0)
        elif "MICA" in _identity:
            draw_circle(m,8+_recoil*5,Color("7cf4e7",.75),false,2.5); draw_circle(m,3.0,Color("e9ffe0"))
        else: draw_line(m,m+aim_world*(18+_recoil*12),Color("fff0a8"),4.0)
