extends Node2D
class_name OperatorSectorSilhouettePresentation

# M7 directional identity pass.
#
# The original 2048x2048 articulated sheet is authored as a frontal paper-doll.
# Compressing that sheet can improve depth ordering but can never become a true
# profile/rear view because eyes, mouth and chest panels are baked into the source.
# Exact left/right profiles and rear-facing sectors therefore replace the baked
# head/torso/pelvis plates with identity-specific directional vector plates while
# preserving the authoritative Bone2D skeleton, arms, legs, weapon and sockets.
#
# Sector convention matches OperatorActor:
# 0=RIGHT profile, 1=DOWN-RIGHT, 2=DOWN/front, 3=DOWN-LEFT,
# 4=LEFT profile, 5=UP-LEFT, 6=UP/rear, 7=UP-RIGHT.

var actor: OperatorActor
var visual: OperatorVisual
var _bones: Dictionary = {}
var _sprite_base_scales: Dictionary = {}
var _last_sector := -1
var _last_body_width := 1.0
var _last_shoulder_width := 1.0
var _last_hip_width := 1.0
var _last_face_width := 1.0
var _identity := "GENERIC"

var _profile_nodes: Array[CanvasItem] = []
var _rear_nodes: Array[CanvasItem] = []
var _replacement_generation := 0

func _ready() -> void:
    process_priority = 112
    actor = get_parent() as OperatorActor
    if actor:
        visual = actor.get_node_or_null("VisualRoot") as OperatorVisual
    call_deferred("_bind")

func _bind() -> void:
    if visual == null:
        return
    _bones = visual.get("_bones")
    _identity = str(visual.get("_identity")).to_upper()
    _cache_sprite_scale("HeadHR")
    _cache_sprite_scale("HairHR")
    _cache_sprite_scale("TorsoHR")
    _cache_sprite_scale("PelvisHR")
    _ensure_directional_replacements()
    sync_now()

func _cache_sprite_scale(name: String) -> void:
    var sprite := visual.find_child(name, true, false) as Sprite2D
    if sprite != null:
        _sprite_base_scales[name] = sprite.scale

func _process(_delta: float) -> void:
    sync_now()

func sync_now() -> void:
    if actor == null or visual == null:
        return
    if _bones.is_empty() or not is_instance_valid(_bones.get("head")):
        _bones = visual.get("_bones")
        _identity = str(visual.get("_identity")).to_upper()
        if _bones.is_empty():
            return
        _profile_nodes.clear()
        _rear_nodes.clear()
        _ensure_directional_replacements()
    elif _profile_nodes.is_empty() or not is_instance_valid(_profile_nodes[0]):
        _ensure_directional_replacements()

    var sector: int = posmod(actor.facing_sector, 8)
    var side: bool = sector == 0 or sector == 4
    var diagonal: bool = sector in [1, 3, 5, 7]
    var rear: bool = sector in [5, 6, 7]
    var left: bool = sector in [3, 4, 5]
    var side_sign: float = -1.0 if left else (1.0 if sector in [0, 1, 7] else 0.0)

    _last_body_width = 0.70 if side else (0.86 if diagonal else 1.0)
    _last_shoulder_width = 0.56 if side else (0.78 if diagonal else 1.0)
    _last_hip_width = 0.62 if side else (0.82 if diagonal else 1.0)
    _last_face_width = 0.44 if side else (0.72 if diagonal else 1.0)

    # Front/forward-diagonal sectors retain the authored sheet. Exact profile and
    # all rear-facing sectors use directional replacements so baked facial/chest
    # artwork can never leak into a side/back view.
    _set_directional_visibility(side, rear)

    if not side and not rear:
        _apply_core_width("HeadHR", 0.90 if diagonal else 1.0)
        _apply_core_width("HairHR", 0.91 if diagonal else 1.0)
        _apply_core_width("TorsoHR", 0.86 if diagonal else 1.0)
        _apply_core_width("PelvisHR", 0.88 if diagonal else 1.0)

    var base_positions: Dictionary = visual.get("_base_positions")
    var torso := _bones.get("torso") as Bone2D
    var head := _bones.get("head") as Bone2D
    var ul := _bones.get("upper_arm_L") as Bone2D
    var ur := _bones.get("upper_arm_R") as Bone2D
    var tl := _bones.get("thigh_L") as Bone2D
    var tr := _bones.get("thigh_R") as Bone2D

    if torso:
        var torso_base: Vector2 = base_positions.get("torso", torso.position)
        torso.position.x = torso_base.x + side_sign * (2.2 if side else (1.0 if diagonal else 0.0))
    if head:
        var head_base: Vector2 = base_positions.get("head", head.position)
        head.position.x = head_base.x + side_sign * (4.8 if side else (2.5 if diagonal else 0.0))
        if rear:
            head.position.y = minf(head.position.y, head_base.y - 1.5)

    if ul:
        var base_ul: Vector2 = base_positions.get("upper_arm_L", ul.position)
        ul.position.x = base_ul.x * _last_shoulder_width
    if ur:
        var base_ur: Vector2 = base_positions.get("upper_arm_R", ur.position)
        ur.position.x = base_ur.x * _last_shoulder_width
    if tl:
        var base_tl: Vector2 = base_positions.get("thigh_L", tl.position)
        tl.position.x = base_tl.x * _last_hip_width
    if tr:
        var base_tr: Vector2 = base_positions.get("thigh_R", tr.position)
        tr.position.x = base_tr.x * _last_hip_width

    _apply_limb_depth(sector)
    _apply_directional_plate_pose(sector, side_sign)
    _apply_face_profile(side, rear)
    _last_sector = sector

func _ensure_directional_replacements() -> void:
    if _bones.is_empty():
        return
    var head := _bones.get("head") as Bone2D
    var torso := _bones.get("torso") as Bone2D
    var pelvis := _bones.get("pelvis") as Bone2D
    if head == null or torso == null or pelvis == null:
        return

    # Do not duplicate plates when _bind is called more than once for the same rig.
    var existing := head.get_node_or_null("M7ProfileHeadOutline") as CanvasItem
    if existing != null:
        _collect_existing_replacements()
        return

    _replacement_generation += 1
    var colors := _identity_colors()
    var ink: Color = colors["ink"]
    var skin: Color = colors["skin"]
    var hair: Color = colors["hair"]
    var hair_shadow: Color = colors["hair_shadow"]
    var body: Color = colors["body"]
    var body_dark: Color = colors["body_dark"]
    var accent: Color = colors["accent"]
    var metal: Color = colors["metal"]

    # Profile head: asymmetric forehead/nose/chin silhouette with one visible eye.
    var profile_head_shape := PackedVector2Array([
        Vector2(-11,-15), Vector2(-4,-19), Vector2(5,-18), Vector2(10,-14),
        Vector2(12,-8), Vector2(17,-5), Vector2(20,-1), Vector2(15,2),
        Vector2(14,8), Vector2(9,14), Vector2(1,17), Vector2(-8,15),
        Vector2(-13,8), Vector2(-14,-5)
    ])
    _profile_nodes.append(_poly(head,"M7ProfileHeadOutline",_inflate(profile_head_shape,1.10),ink,4))
    _profile_nodes.append(_poly(head,"M7ProfileHeadSkin",profile_head_shape,skin,5))

    var profile_hair_shape := _profile_hair_shape()
    _profile_nodes.append(_poly(head,"M7ProfileHair",profile_hair_shape,hair,6))
    _profile_nodes.append(_poly(head,"M7ProfileHairShadow",_profile_hair_shadow_shape(),hair_shadow,6))
    _profile_nodes.append(_poly(head,"M7ProfileEye",PackedVector2Array([
        Vector2(7,-5),Vector2(11,-6),Vector2(12,-3),Vector2(8,-2)
    ]),accent.lightened(0.28),7))
    _profile_nodes.append(_poly(head,"M7ProfileJawShadow",PackedVector2Array([
        Vector2(4,7),Vector2(13,4),Vector2(11,10),Vector2(4,14),Vector2(-2,13)
    ]),Color(skin,0.68).darkened(0.16),6))

    # Identity hair/accessory pieces are intentionally large enough to read at the
    # actual ~70px field-character scale, not only in isolated art inspection.
    if "ASTER" in _identity:
        _profile_nodes.append(_poly(head,"M7ProfileIdentityHair",PackedVector2Array([
            Vector2(-9,-10),Vector2(-21,-7),Vector2(-30,1),Vector2(-38,12),
            Vector2(-27,10),Vector2(-18,4),Vector2(-10,3)
        ]),hair,5))
        _profile_nodes.append(_poly(head,"M7ProfileIdentityAccent",PackedVector2Array([
            Vector2(-18,1),Vector2(-28,8),Vector2(-18,7),Vector2(-8,2)
        ]),accent,6))
    elif "ROOK" in _identity:
        _profile_nodes.append(_poly(head,"M7ProfileIdentityHair",PackedVector2Array([
            Vector2(-16,-10),Vector2(-11,-19),Vector2(0,-23),Vector2(10,-19),
            Vector2(5,-14),Vector2(-4,-12)
        ]),hair.lightened(0.04),7))
    elif "MICA" in _identity:
        _profile_nodes.append(_poly(head,"M7ProfileIdentityHair",PackedVector2Array([
            Vector2(-10,-6),Vector2(-21,0),Vector2(-26,10),Vector2(-20,19),
            Vector2(-12,27),Vector2(-7,21),Vector2(-13,13),Vector2(-8,5)
        ]),hair_shadow,5))
        _profile_nodes.append(_poly(head,"M7ProfileIdentityAccent",PackedVector2Array([
            Vector2(-7,-16),Vector2(-18,-13),Vector2(-21,-7),Vector2(-10,-9)
        ]),accent,7))

    var profile_torso_shape := _profile_torso_shape()
    _profile_nodes.append(_poly(torso,"M7ProfileTorsoOutline",_inflate(profile_torso_shape,1.08),ink,0))
    _profile_nodes.append(_poly(torso,"M7ProfileTorso",profile_torso_shape,body,1))
    _profile_nodes.append(_poly(torso,"M7ProfileChestPanel",PackedVector2Array([
        Vector2(1,-13),Vector2(10,-10),Vector2(11,5),Vector2(4,10),Vector2(0,4)
    ]),accent.darkened(0.35),2))
    _profile_nodes.append(_poly(torso,"M7ProfileChestLight",PackedVector2Array([
        Vector2(5,-9),Vector2(10,-7),Vector2(10,-4),Vector2(5,-5)
    ]),accent.lightened(0.22),3))
    var profile_pelvis_shape := PackedVector2Array([
        Vector2(-7,-4),Vector2(8,-4),Vector2(11,5),Vector2(6,11),Vector2(-6,10),Vector2(-10,4)
    ])
    _profile_nodes.append(_poly(pelvis,"M7ProfilePelvisOutline",_inflate(profile_pelvis_shape,1.10),ink,0))
    _profile_nodes.append(_poly(pelvis,"M7ProfilePelvis",profile_pelvis_shape,body_dark,1))

    # Rear plates: no skin/eyes. Hair/back-of-head and a dedicated rear armor panel
    # replace the frontal baked art in sectors 5/6/7.
    var rear_hair_shape := _rear_hair_shape()
    _rear_nodes.append(_poly(head,"M7RearHeadOutline",_inflate(rear_hair_shape,1.10),ink,4))
    _rear_nodes.append(_poly(head,"M7RearHair",rear_hair_shape,hair,5))
    _rear_nodes.append(_poly(head,"M7RearHairShadow",_rear_hair_shadow_shape(),hair_shadow,6))
    if "ASTER" in _identity:
        _rear_nodes.append(_poly(head,"M7RearIdentityHair",PackedVector2Array([
            Vector2(-8,4),Vector2(-20,8),Vector2(-31,18),Vector2(-17,17),
            Vector2(-4,11),Vector2(8,16),Vector2(24,20),Vector2(13,9)
        ]),hair,4))
        _rear_nodes.append(_poly(head,"M7RearIdentityAccent",PackedVector2Array([
            Vector2(-18,11),Vector2(-5,8),Vector2(5,11),Vector2(-5,14)
        ]),accent,6))
    elif "ROOK" in _identity:
        _rear_nodes.append(_poly(head,"M7RearIdentityHair",PackedVector2Array([
            Vector2(-15,-9),Vector2(-10,-19),Vector2(0,-23),Vector2(12,-18),
            Vector2(16,-8),Vector2(8,-11),Vector2(-4,-12)
        ]),hair.lightened(0.04),6))
    elif "MICA" in _identity:
        _rear_nodes.append(_poly(head,"M7RearIdentityHair",PackedVector2Array([
            Vector2(8,2),Vector2(17,7),Vector2(20,16),Vector2(14,25),
            Vector2(8,31),Vector2(3,25),Vector2(8,18),Vector2(4,10)
        ]),hair_shadow,4))
        _rear_nodes.append(_poly(head,"M7RearIdentityAccent",PackedVector2Array([
            Vector2(-17,-12),Vector2(-9,-17),Vector2(-7,-8),Vector2(-15,-5)
        ]),accent,7))

    var rear_torso_shape := _rear_torso_shape()
    _rear_nodes.append(_poly(torso,"M7RearTorsoOutline",_inflate(rear_torso_shape,1.07),ink,0))
    _rear_nodes.append(_poly(torso,"M7RearTorso",rear_torso_shape,body_dark,1))
    _rear_nodes.append(_poly(torso,"M7RearBackPanel",PackedVector2Array([
        Vector2(-12,-10),Vector2(12,-10),Vector2(14,7),Vector2(7,13),
        Vector2(-8,12),Vector2(-14,5)
    ]),body,2))
    _rear_nodes.append(_poly(torso,"M7RearSpineLight",PackedVector2Array([
        Vector2(-2,-8),Vector2(3,-8),Vector2(3,8),Vector2(-2,8)
    ]),accent.darkened(0.18),3))
    if "ROOK" in _identity:
        _rear_nodes.append(_poly(torso,"M7RearMantle",PackedVector2Array([
            Vector2(-22,-13),Vector2(22,-13),Vector2(19,-3),Vector2(-19,-3)
        ]),metal.darkened(0.28),3))
    elif "MICA" in _identity:
        _rear_nodes.append(_poly(torso,"M7RearCoat",PackedVector2Array([
            Vector2(-14,8),Vector2(-4,8),Vector2(-7,25),Vector2(-17,30),
            Vector2(-12,17),Vector2(4,8),Vector2(14,9),Vector2(17,29),
            Vector2(7,25),Vector2(4,9)
        ]),body,0))

    var rear_pelvis_shape := PackedVector2Array([
        Vector2(-12,-5),Vector2(12,-5),Vector2(13,7),Vector2(7,12),Vector2(-8,12),Vector2(-13,6)
    ])
    _rear_nodes.append(_poly(pelvis,"M7RearPelvisOutline",_inflate(rear_pelvis_shape,1.08),ink,0))
    _rear_nodes.append(_poly(pelvis,"M7RearPelvis",rear_pelvis_shape,body_dark,1))

    _set_canvas_group_visible(_profile_nodes,false)
    _set_canvas_group_visible(_rear_nodes,false)

func _collect_existing_replacements() -> void:
    _profile_nodes.clear()
    _rear_nodes.clear()
    for bone_name in ["head","torso","pelvis"]:
        var bone := _bones.get(bone_name) as Bone2D
        if bone == null:
            continue
        for child in bone.get_children():
            if child is CanvasItem:
                if child.name.begins_with("M7Profile"):
                    _profile_nodes.append(child as CanvasItem)
                elif child.name.begins_with("M7Rear"):
                    _rear_nodes.append(child as CanvasItem)

func _identity_colors() -> Dictionary:
    if "ROOK" in _identity:
        return {
            "ink":Color("11171b"),"skin":Color("e8cdbd"),"hair":Color("f0ede7"),
            "hair_shadow":Color("9ea4a7"),"body":Color("2d3338"),"body_dark":Color("171c20"),
            "accent":Color("d39a58"),"metal":Color("8d969b")
        }
    if "MICA" in _identity:
        return {
            "ink":Color("10191b"),"skin":Color("e2c7b6"),"hair":Color("d8c2ac"),
            "hair_shadow":Color("8f7968"),"body":Color("263b3f"),"body_dark":Color("132326"),
            "accent":Color("62d8c8"),"metal":Color("71858a")
        }
    return {
        "ink":Color("10181d"),"skin":Color("f1d7c7"),"hair":Color("e8f7ff"),
        "hair_shadow":Color("8fabb9"),"body":Color("16374a"),"body_dark":Color("0b202c"),
        "accent":Color("79d8ff"),"metal":Color("879ca7")
    }

func _profile_hair_shape() -> PackedVector2Array:
    if "ROOK" in _identity:
        return PackedVector2Array([
            Vector2(-14,-8),Vector2(-13,-16),Vector2(-5,-21),Vector2(7,-20),
            Vector2(14,-15),Vector2(12,-9),Vector2(4,-12),Vector2(-5,-9),Vector2(-10,-2)
        ])
    if "MICA" in _identity:
        return PackedVector2Array([
            Vector2(-14,-8),Vector2(-12,-17),Vector2(-3,-21),Vector2(8,-19),
            Vector2(14,-12),Vector2(10,-7),Vector2(2,-10),Vector2(-7,-6),Vector2(-13,1)
        ])
    return PackedVector2Array([
        Vector2(-15,-7),Vector2(-13,-17),Vector2(-4,-22),Vector2(8,-20),
        Vector2(14,-14),Vector2(11,-8),Vector2(2,-11),Vector2(-8,-6),Vector2(-14,2)
    ])

func _profile_hair_shadow_shape() -> PackedVector2Array:
    return PackedVector2Array([
        Vector2(-13,-6),Vector2(-7,-11),Vector2(1,-13),Vector2(3,-7),
        Vector2(-3,-2),Vector2(-10,3),Vector2(-14,1)
    ])

func _profile_torso_shape() -> PackedVector2Array:
    if "ROOK" in _identity:
        return PackedVector2Array([
            Vector2(-9,-17),Vector2(10,-17),Vector2(16,-10),Vector2(17,8),
            Vector2(10,18),Vector2(-8,17),Vector2(-13,8),Vector2(-13,-9)
        ])
    if "MICA" in _identity:
        return PackedVector2Array([
            Vector2(-8,-17),Vector2(9,-16),Vector2(13,-9),Vector2(12,14),
            Vector2(6,23),Vector2(-7,21),Vector2(-11,11),Vector2(-11,-9)
        ])
    return PackedVector2Array([
        Vector2(-8,-17),Vector2(9,-17),Vector2(14,-10),Vector2(13,13),
        Vector2(7,18),Vector2(-7,17),Vector2(-11,8),Vector2(-11,-9)
    ])

func _rear_hair_shape() -> PackedVector2Array:
    if "ROOK" in _identity:
        return PackedVector2Array([
            Vector2(-15,-9),Vector2(-12,-18),Vector2(-3,-22),Vector2(8,-20),
            Vector2(15,-13),Vector2(15,-2),Vector2(10,10),Vector2(0,14),
            Vector2(-11,10),Vector2(-16,1)
        ])
    if "MICA" in _identity:
        return PackedVector2Array([
            Vector2(-15,-8),Vector2(-12,-18),Vector2(-3,-22),Vector2(8,-20),
            Vector2(15,-12),Vector2(15,1),Vector2(10,13),Vector2(1,17),
            Vector2(-11,12),Vector2(-16,2)
        ])
    return PackedVector2Array([
        Vector2(-16,-7),Vector2(-13,-18),Vector2(-3,-22),Vector2(9,-20),
        Vector2(16,-11),Vector2(16,2),Vector2(10,13),Vector2(0,17),
        Vector2(-11,12),Vector2(-17,2)
    ])

func _rear_hair_shadow_shape() -> PackedVector2Array:
    return PackedVector2Array([
        Vector2(-13,-2),Vector2(-7,-8),Vector2(1,-10),Vector2(10,-7),
        Vector2(13,1),Vector2(8,10),Vector2(0,13),Vector2(-9,9)
    ])

func _rear_torso_shape() -> PackedVector2Array:
    if "ROOK" in _identity:
        return PackedVector2Array([
            Vector2(-22,-16),Vector2(22,-16),Vector2(24,-7),Vector2(19,16),
            Vector2(9,21),Vector2(-10,20),Vector2(-20,15),Vector2(-25,-5)
        ])
    if "MICA" in _identity:
        return PackedVector2Array([
            Vector2(-16,-16),Vector2(16,-16),Vector2(20,-7),Vector2(17,18),
            Vector2(7,24),Vector2(-8,24),Vector2(-17,17),Vector2(-20,-7)
        ])
    return PackedVector2Array([
        Vector2(-18,-16),Vector2(18,-16),Vector2(21,-7),Vector2(17,17),
        Vector2(8,21),Vector2(-8,21),Vector2(-17,16),Vector2(-21,-7)
    ])

func _poly(parent: Node2D, name_value: String, points: PackedVector2Array, color: Color, z: int) -> Polygon2D:
    var node := Polygon2D.new()
    node.name = name_value
    node.polygon = points
    node.color = color
    node.z_index = z
    parent.add_child(node)
    return node

func _inflate(points: PackedVector2Array, factor: float) -> PackedVector2Array:
    var out := PackedVector2Array()
    for point in points:
        out.append(point * factor)
    return out

func _set_directional_visibility(profile: bool, rear: bool) -> void:
    _set_canvas_group_visible(_profile_nodes,profile)
    _set_canvas_group_visible(_rear_nodes,rear)
    var use_baked_core := not profile and not rear
    for name in ["HeadHR","HairHR","TorsoHR","PelvisHR"]:
        var sprite := visual.find_child(name,true,false) as Sprite2D
        if sprite != null:
            sprite.visible = use_baked_core

func _set_canvas_group_visible(group: Array[CanvasItem], value: bool) -> void:
    for node in group:
        if is_instance_valid(node):
            node.visible = value

func _apply_directional_plate_pose(sector: int, side_sign: float) -> void:
    if sector == 0 or sector == 4:
        for node in _profile_nodes:
            if is_instance_valid(node):
                node.scale = Vector2(side_sign,1.0)
                node.position = Vector2.ZERO
    elif sector in [5,6,7]:
        var rear_turn := -1.0 if sector == 5 else (1.0 if sector == 7 else 0.0)
        for node in _rear_nodes:
            if is_instance_valid(node):
                node.scale = Vector2(0.92 if sector != 6 else 1.0,1.0)
                node.position = Vector2(rear_turn*2.2,0.0)

func _apply_core_width(name: String, width: float) -> void:
    var sprite := visual.find_child(name, true, false) as Sprite2D
    if sprite == null:
        return
    if not _sprite_base_scales.has(name):
        _sprite_base_scales[name] = sprite.scale
    var base_scale: Vector2 = _sprite_base_scales[name]
    sprite.scale = Vector2(base_scale.x * width, base_scale.y)

func _apply_limb_depth(sector: int) -> void:
    var side_or_diagonal := sector in [0,1,3,4,5,7]
    var left_facing := sector in [3,4,5]
    var rear := sector in [5,6,7]
    var ul := _bones.get("upper_arm_L") as Bone2D
    var ur := _bones.get("upper_arm_R") as Bone2D
    var tl := _bones.get("thigh_L") as Bone2D
    var tr := _bones.get("thigh_R") as Bone2D

    if side_or_diagonal:
        if left_facing:
            if ul: ul.z_index = 5
            if ur: ur.z_index = -3
            if tl: tl.z_index = 2
            if tr: tr.z_index = -2
            _set_limb_alpha("UpperArmLHR",1.0); _set_limb_alpha("LowerArmLHR",1.0)
            _set_limb_alpha("ThighLHR",1.0); _set_limb_alpha("ShinLHR",1.0)
            _set_limb_alpha("UpperArmRHR",0.56); _set_limb_alpha("LowerArmRHR",0.56)
            _set_limb_alpha("ThighRHR",0.66); _set_limb_alpha("ShinRHR",0.66)
        else:
            if ur: ur.z_index = 5
            if ul: ul.z_index = -3
            if tr: tr.z_index = 2
            if tl: tl.z_index = -2
            _set_limb_alpha("UpperArmRHR",1.0); _set_limb_alpha("LowerArmRHR",1.0)
            _set_limb_alpha("ThighRHR",1.0); _set_limb_alpha("ShinRHR",1.0)
            _set_limb_alpha("UpperArmLHR",0.56); _set_limb_alpha("LowerArmLHR",0.56)
            _set_limb_alpha("ThighLHR",0.66); _set_limb_alpha("ShinLHR",0.66)
    else:
        if ul: ul.z_index = -2 if rear else 3
        if ur: ur.z_index = -1 if rear else 4
        if tl: tl.z_index = 0
        if tr: tr.z_index = 0
        for name in ["UpperArmLHR","LowerArmLHR","UpperArmRHR","LowerArmRHR","ThighLHR","ShinLHR","ThighRHR","ShinRHR"]:
            _set_limb_alpha(name,1.0)

func _set_limb_alpha(name: String, alpha: float) -> void:
    var sprite := visual.find_child(name,true,false) as Sprite2D
    if sprite != null:
        sprite.self_modulate = Color(1.0,1.0,1.0,alpha)

func _apply_face_profile(side: bool, rear: bool) -> void:
    var face := visual.find_child("FaceMicroRig",true,false) as Node2D
    if face == null:
        return
    # Directional replacement owns its own one-eye profile and rear has no face.
    if side or rear:
        face.visible = false
        face.scale = Vector2.ONE
        face.position = Vector2(0,-1.5)
        return
    face.visible = true
    face.scale = Vector2(_last_face_width,0.95 if _last_face_width < 1.0 else 1.0)
    var sign := -1.0 if _last_sector == 3 else (1.0 if _last_sector == 1 else 0.0)
    face.position = Vector2(sign*(1.4 if _last_face_width < 1.0 else 0.0),-1.5)

func debug_current_contract() -> Dictionary:
    var baked_head := visual.find_child("HeadHR",true,false) as Sprite2D if visual != null else null
    return {
        "sector":_last_sector,
        "body_width":_last_body_width,
        "shoulder_width":_last_shoulder_width,
        "hip_width":_last_hip_width,
        "face_width":_last_face_width,
        "rear":_last_sector in [5,6,7],
        "profile":_last_sector in [0,4],
        "identity":_identity,
        "directional_profile_plate_count":_profile_nodes.size(),
        "directional_rear_plate_count":_rear_nodes.size(),
        "profile_replacement_active":_last_sector in [0,4] and _any_visible(_profile_nodes),
        "rear_replacement_active":_last_sector in [5,6,7] and _any_visible(_rear_nodes),
        "baked_head_visible":baked_head.visible if baked_head != null else false,
        "baked_front_core_suppressed":baked_head != null and not baked_head.visible if _last_sector in [0,4,5,6,7] else true,
        "replacement_generation":_replacement_generation
    }

func _any_visible(group: Array[CanvasItem]) -> bool:
    for node in group:
        if is_instance_valid(node) and node.visible:
            return true
    return false
