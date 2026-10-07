extends Node2D
class_name OperatorVisual

const TILE := 512.0

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
var _hit_flash := 0.0
var _identity := "GENERIC"
## Whether the last _draw included the muzzle flash. Only the flash changes from
## frame to frame; the rings change through configure / set_selected, which redraw.
var _drawn_flash := false

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
var _secondary_delay := 0.045

var skeleton: Skeleton2D
var animation_player: AnimationPlayer
var animation_tree: AnimationTree
var muzzle_socket: Node2D

var _bones: Dictionary = {}
var _base_positions: Dictionary = {}
var _secondary_parts: Array[Node2D] = []
var _rig_texture: Texture2D
# A rig sheet exists for this profile even while its pixels are released, so
# the sheet-part skeleton (and its muzzle/support sockets) stays identical.
var _has_rig_sheet := false
var _art_released := false

func _ready() -> void:
    _build_runtime_rig()
    queue_redraw()

func configure(label: String, color: Color, profile: Dictionary = {}) -> void:
    operator_label = label
    accent_color = color
    art_profile = profile.duplicate(true)
    _identity = str(art_profile.get("visual_profile", label)).to_upper()
    _apply_motion_profile()
    _load_rig_texture()
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

func trigger_hit() -> void:
    _hit_flash = 1.0

func get_muzzle_global_position() -> Vector2:
    return muzzle_socket.global_position if is_instance_valid(muzzle_socket) else global_position

func _process(delta: float) -> void:
    _phase += delta * lerpf(3.0, _cadence, clampf(speed_norm, 0.0, 1.0))
    _recoil = move_toward(_recoil, 0.0, delta * _recoil_recover)
    _evade_flash = move_toward(_evade_flash, 0.0, delta * 5.0)
    _hit_flash = move_toward(_hit_flash, 0.0, delta * 5.5)
    _pose_rig()
    if is_instance_valid(skeleton):
        skeleton.modulate = Color.WHITE.lerp(Color("ff9a9a"), _hit_flash * 0.58)
    # Redrawing unchanged rings every frame rebuilt their polylines (a vertex array
    # and buffers each on the web renderer).
    if _recoil > .12 or _drawn_flash:
        queue_redraw()

func _load_rig_texture() -> void:
    _rig_texture = null
    var path := str(art_profile.get("rig_sheet", ""))
    _has_rig_sheet = not path.is_empty() and ResourceLoader.exists("res://" + path)
    if _has_rig_sheet and not _art_released:
        _rig_texture = load("res://" + path) as Texture2D
        _has_rig_sheet = _rig_texture != null

## Called when a raster runtime owns the visible body. Bones, sockets and
## timing keep running; only the invisible sheet/detail pixels leave VRAM.
func release_hidden_art() -> void:
    _art_released = true
    _rig_texture = null
    _clear_sprite_textures(self)

func restore_hidden_art() -> void:
    if not _art_released:
        return
    _art_released = false
    _load_rig_texture()
    if is_node_ready():
        _rebuild_runtime_rig()

func _clear_sprite_textures(node: Node) -> void:
    for child in node.get_children():
        if child is Sprite2D:
            (child as Sprite2D).texture = null
        _clear_sprite_textures(child)

func _apply_motion_profile() -> void:
    match str(art_profile.get("motion_profile", "")):
        "MOT_ASTER_01":
            _cadence=11.2; _gait_amp=0.58; _bob_amp=1.9; _torso_sway=0.026; _head_lag=0.48; _recoil_amp=0.060; _recoil_recover=12.0; _reload_fold_amp=0.48; _evade_x=0.18; _evade_y=0.06; _secondary_delay=0.065
        "MOT_ROOK_01":
            _cadence=7.0; _gait_amp=0.43; _bob_amp=3.8; _torso_sway=0.062; _head_lag=0.72; _recoil_amp=0.145; _recoil_recover=5.2; _reload_fold_amp=0.78; _evade_x=0.10; _evade_y=0.12; _secondary_delay=0.038
        "MOT_MICA_01":
            _cadence=8.4; _gait_amp=0.38; _bob_amp=1.35; _torso_sway=0.020; _head_lag=0.34; _recoil_amp=0.042; _recoil_recover=7.0; _reload_fold_amp=0.40; _evade_x=0.12; _evade_y=0.05; _secondary_delay=0.082

func _rebuild_runtime_rig() -> void:
    if is_instance_valid(animation_tree): animation_tree.queue_free()
    if is_instance_valid(animation_player): animation_player.queue_free()
    if is_instance_valid(skeleton): skeleton.queue_free()
    skeleton=null; animation_player=null; animation_tree=null; muzzle_socket=null
    _bones.clear(); _base_positions.clear(); _secondary_parts.clear()
    _build_runtime_rig()

func _build_runtime_rig() -> void:
    skeleton = Skeleton2D.new()
    skeleton.name = "Skeleton2D"
    add_child(skeleton)

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

    if _rig_texture != null or (_art_released and _has_rig_sheet):
        _build_high_res_parts(pelvis, torso, head, upper_l, lower_l, upper_r, lower_r, weapon, thigh_l, shin_l, foot_l, thigh_r, shin_r, foot_r)
    else:
        _build_fallback_parts(pelvis, torso, head, upper_l, lower_l, upper_r, lower_r, weapon, thigh_l, shin_l, foot_l, thigh_r, shin_r, foot_r)

    animation_player = AnimationPlayer.new()
    animation_player.name = "AnimationPlayer"
    add_child(animation_player)
    var library := AnimationLibrary.new()
    for clip_name in ["IdleExplore", "Move", "FireSingle", "Reload", "Evade", "HitLight"]:
        var anim := Animation.new()
        anim.length = 1.0
        anim.loop_mode = Animation.LOOP_LINEAR if clip_name in ["IdleExplore", "Move"] else Animation.LOOP_NONE
        library.add_animation(clip_name, anim)
    animation_player.add_animation_library("", library)

    animation_tree = AnimationTree.new()
    animation_tree.name = "AnimationTree"
    add_child(animation_tree)
    animation_tree.anim_player = NodePath("../AnimationPlayer")
    var root_anim := AnimationNodeAnimation.new()
    root_anim.animation = &"IdleExplore"
    animation_tree.tree_root = root_anim
    animation_tree.active = true

    for bone_name in _bones.keys():
        var bone: Bone2D = _bones[bone_name]
        bone.rest = bone.transform
        _base_positions[bone_name] = bone.position

func _build_high_res_parts(pelvis:Bone2D, torso:Bone2D, head:Bone2D, ul:Bone2D, ll:Bone2D, ur:Bone2D, lr:Bone2D, weapon:Bone2D, tl:Bone2D, sl:Bone2D, fl:Bone2D, tr:Bone2D, sr:Bone2D, fr:Bone2D) -> void:
    var scale_head := 0.125
    var scale_body := 0.112
    var scale_limb := 0.108
    var scale_weapon := 0.112
    if "ROOK" in _identity:
        scale_body = 0.118; scale_limb = 0.116; scale_weapon = 0.118
    elif "MICA" in _identity:
        scale_body = 0.110; scale_limb = 0.105; scale_weapon = 0.110

    _sheet_part(head,"HeadHR",0,0,scale_head,Vector2.ZERO,4)
    var hair := _sheet_part(head,"HairHR",1,0,scale_head,Vector2.ZERO,5); _secondary_parts.append(hair)
    _sheet_part(torso,"TorsoHR",2,0,scale_body,Vector2.ZERO,1)
    _sheet_part(pelvis,"PelvisHR",3,0,scale_body,Vector2.ZERO,1)
    _sheet_part(ul,"UpperArmLHR",0,1,scale_limb,Vector2.ZERO,2)
    _sheet_part(ll,"LowerArmLHR",1,1,scale_limb,Vector2.ZERO,3)
    _sheet_part(ur,"UpperArmRHR",2,1,scale_limb,Vector2.ZERO,2)
    _sheet_part(lr,"LowerArmRHR",3,1,scale_limb,Vector2.ZERO,3)
    _sheet_part(tl,"ThighLHR",0,2,scale_limb,Vector2.ZERO,0)
    _sheet_part(sl,"ShinLHR",1,2,scale_limb,Vector2.ZERO,0)
    _sheet_part(tr,"ThighRHR",2,2,scale_limb,Vector2.ZERO,0)
    _sheet_part(sr,"ShinRHR",3,2,scale_limb,Vector2.ZERO,0)
    _sheet_part(fl,"FootLHR",0,3,scale_limb,Vector2.ZERO,0)
    _sheet_part(fr,"FootRHR",1,3,scale_limb,Vector2.ZERO,0)
    _sheet_part(weapon,"WeaponHR",2,3,scale_weapon,Vector2.ZERO,6)
    var accessory_parent: Node2D = pelvis if "MICA" in _identity else torso
    var accessory := _sheet_part(accessory_parent,"AccessoryHR",3,3,scale_body,Vector2.ZERO,0); _secondary_parts.append(accessory)

    var muzzle_x := 31.0 if "ASTER" in _identity else (30.0 if "ROOK" in _identity else 28.0)
    _make_sockets(weapon, muzzle_x, 7.0)

func _build_fallback_parts(pelvis:Bone2D, torso:Bone2D, head:Bone2D, ul:Bone2D, ll:Bone2D, ur:Bone2D, lr:Bone2D, weapon:Bone2D, tl:Bone2D, sl:Bone2D, fl:Bone2D, tr:Bone2D, sr:Bone2D, fr:Bone2D) -> void:
    _rect_part(pelvis,"PelvisPart",Vector2(23,15),Vector2(0,3),accent_color.darkened(0.32))
    _rect_part(torso,"TorsoPart",Vector2(29,29),Vector2(0,1),accent_color.darkened(0.10))
    _circle_part(head,"HeadPart",17.0,Color("f1d7c7"))
    _limb_part(ul,"UpperArmL",17,7,accent_color); _limb_part(ll,"LowerArmL",15,6,Color("e8cdbd")); _limb_part(ur,"UpperArmR",17,7,accent_color); _limb_part(lr,"LowerArmR",15,6,Color("e8cdbd"))
    _vertical_limb_part(tl,"ThighL",20,8,accent_color.darkened(0.35)); _vertical_limb_part(sl,"ShinL",18,7,Color("4e5a66")); _vertical_limb_part(fl,"FootL",12,9,Color("202936")); _vertical_limb_part(tr,"ThighR",20,8,accent_color.darkened(0.35)); _vertical_limb_part(sr,"ShinR",18,7,Color("4e5a66")); _vertical_limb_part(fr,"FootR",12,9,Color("202936"))
    _rect_part(weapon,"WeaponPart",Vector2(44,8),Vector2(22,0),Color("28333d")); _make_sockets(weapon,46.0,15.0)

func _sheet_part(parent:Node2D, part_name:String, col:int, row:int, scale_value:float, offset:Vector2, z:int) -> Sprite2D:
    var sprite := Sprite2D.new()
    sprite.name = part_name
    sprite.texture = _rig_texture
    sprite.region_enabled = true
    sprite.region_rect = Rect2(float(col) * TILE, float(row) * TILE, TILE, TILE)
    sprite.centered = true
    sprite.position = offset
    sprite.scale = Vector2.ONE * scale_value
    sprite.z_index = z
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
    parent.add_child(sprite)
    return sprite

func _make_sockets(weapon: Bone2D, muzzle_x: float, support_x: float) -> void:
    muzzle_socket=Node2D.new(); muzzle_socket.name="muzzle_socket"; muzzle_socket.position=Vector2(muzzle_x,0); weapon.add_child(muzzle_socket)
    var support:=Node2D.new(); support.name="support_hand_socket"; support.position=Vector2(support_x,0); weapon.add_child(support)
    var fx:=Node2D.new(); fx.name="fx_root"; weapon.add_child(fx)

func _bone(parent: Node, bone_name: String, pos: Vector2) -> Bone2D:
    var bone:=Bone2D.new(); bone.name=bone_name; bone.position=pos; bone.set_autocalculate_length_and_angle(false); parent.add_child(bone); _bones[bone_name]=bone; return bone

func _rect_part(parent:Node2D,n:String,size:Vector2,center:Vector2,color:Color)->Polygon2D:
    var p:=Polygon2D.new(); p.name=n; p.polygon=PackedVector2Array([center+Vector2(-size.x*.5,-size.y*.5),center+Vector2(size.x*.5,-size.y*.5),center+Vector2(size.x*.5,size.y*.5),center+Vector2(-size.x*.5,size.y*.5)]); p.color=color; parent.add_child(p); return p
func _circle_part(parent:Node2D,n:String,r:float,color:Color)->Polygon2D:
    var pts:=PackedVector2Array(); for i in range(20): pts.append(Vector2.RIGHT.rotated(TAU*float(i)/20.0)*r)
    var p:=Polygon2D.new(); p.name=n; p.polygon=pts; p.color=color; parent.add_child(p); return p
func _limb_part(parent:Node2D,n:String,length:float,width:float,color:Color)->Polygon2D: return _rect_part(parent,n,Vector2(length,width),Vector2(length*.5,0),color)
func _vertical_limb_part(parent:Node2D,n:String,length:float,width:float,color:Color)->Polygon2D: return _rect_part(parent,n,Vector2(width,length),Vector2(0,length*.5),color)

func _pose_rig() -> void:
    if _bones.is_empty(): return
    var pelvis:Bone2D=_bones["pelvis"]; var torso:Bone2D=_bones["torso"]; var head:Bone2D=_bones["head"]
    var tl:Bone2D=_bones["thigh_L"]; var tr:Bone2D=_bones["thigh_R"]; var sl:Bone2D=_bones["shin_L"]; var sr:Bone2D=_bones["shin_R"]
    var ul:Bone2D=_bones["upper_arm_L"]; var ur:Bone2D=_bones["upper_arm_R"]; var ll:Bone2D=_bones["lower_arm_L"]; var lr:Bone2D=_bones["lower_arm_R"]; var weapon:Bone2D=_bones["weapon_root"]
    var gait:=sin(_phase)*_gait_amp*minf(speed_norm,1.0)
    var bob:=absf(sin(_phase))*_bob_amp*minf(speed_norm,1.0)
    pelvis.position=(_base_positions["pelvis"] as Vector2)+Vector2(0,bob)
    torso.rotation=sin(_phase*.5)*_torso_sway*minf(speed_norm,1.0)
    head.rotation=-torso.rotation*_head_lag+sin(_phase*.43)*.012
    tl.rotation=gait; tr.rotation=-gait; sl.rotation=-gait*.62; sr.rotation=gait*.62

    var aim:=aim_world.angle(); var fold:=sin(reload_progress*PI) if is_reloading else 0.0; var kick:=_recoil*_recoil_amp
    if "ROOK" in _identity:
        ur.rotation=aim-.16-kick-fold*.68; lr.rotation=.14+kick*.45+fold*.82; ul.rotation=aim+.04-kick*.5+fold*.18; ll.rotation=-.10+fold*.42
    elif "MICA" in _identity:
        ur.rotation=aim-.06-kick-fold*.38; lr.rotation=.04+fold*.52; ul.rotation=aim+.18-kick*.45+fold*.22; ll.rotation=-.24+fold*.48
    else:
        ur.rotation=aim-.10-kick-fold*.55; lr.rotation=.08+kick*.5+fold*.75; ul.rotation=aim+.13-kick*.7+fold*.30; ll.rotation=-.18+fold*.55
    weapon.rotation=aim-kick+fold*_reload_fold_amp
    weapon.position=(_base_positions["weapon_root"] as Vector2)-aim_world*(_recoil*(6.0 if "ROOK" in _identity else 3.5))+Vector2(0,fold*5.0)

    for i in range(_secondary_parts.size()):
        var part:=_secondary_parts[i]
        if is_instance_valid(part):
            part.rotation=sin(_phase*.55-float(i)*.7)*(_secondary_delay+.025*speed_norm)
    skeleton.scale=Vector2(1.0+_evade_flash*_evade_x,1.0-_evade_flash*_evade_y) if _evade_flash>0.0 else Vector2.ONE

func _draw() -> void:
    var ring:=accent_color if _selected else Color(0.25,0.30,0.36,0.55)
    draw_arc(Vector2(0,4),24.0,0.0,TAU,32,ring,2.5 if _selected else 1.0)
    if _selected: draw_arc(Vector2(0,4),29.0,-PI*.85,-PI*.15,18,Color(accent_color,0.65),2.0)
    # With a raster runtime owning the body this socket belongs to the hidden rig, so its
    # flash sat off the visible gun; CombatMuzzleVFX flashes at the real projectile origin.
    _drawn_flash = _recoil>.12 and is_instance_valid(muzzle_socket) and not _art_released
    if _drawn_flash:
        var m:=to_local(muzzle_socket.global_position)
        if "ASTER" in _identity:
            draw_line(m,m+aim_world*(25+_recoil*14),Color("e8f7ff"),2.2); draw_circle(m+aim_world*8,3.0,Color("ffcf70"))
        elif "ROOK" in _identity:
            draw_arc(m,8+_recoil*10,-.6,.6,12,Color("ffb06f"),5.0); draw_line(m,m+aim_world*18,Color("ffe09a"),7.0)
        elif "MICA" in _identity:
            draw_circle(m,8+_recoil*5,Color("7cf4e7",.75),false,2.5); draw_circle(m,3.0,Color("e9ffe0"))
        else:
            draw_line(m,m+aim_world*(18+_recoil*12),Color("fff0a8"),4.0)
