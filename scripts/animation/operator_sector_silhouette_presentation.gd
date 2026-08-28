extends Node2D
class_name OperatorSectorSilhouettePresentation

# M7 visual-acceptance layer. The underlying articulated rig remains authoritative,
# but the eight facing sectors must produce visibly different body silhouettes rather
# than changing only weapon aim. This layer runs after locomotion/upright shaping and
# immediately before weapon IK so shoulder compression is included in the IK solve.

var actor: OperatorActor
var visual: OperatorVisual
var _bones: Dictionary = {}
var _sprite_base_scales: Dictionary = {}
var _last_sector := -1
var _last_body_width := 1.0
var _last_shoulder_width := 1.0
var _last_hip_width := 1.0
var _last_face_width := 1.0

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
    _cache_sprite_scale("HeadHR")
    _cache_sprite_scale("HairHR")
    _cache_sprite_scale("TorsoHR")
    _cache_sprite_scale("PelvisHR")

func _cache_sprite_scale(name: String) -> void:
    var sprite := visual.find_child(name, true, false) as Sprite2D
    if sprite != null:
        _sprite_base_scales[name] = sprite.scale

func _process(_delta: float) -> void:
    if actor == null or visual == null:
        return
    if _bones.is_empty():
        _bind()
        if _bones.is_empty():
            return

    var sector := posmod(actor.facing_sector, 8)
    var side := sector in [0, 4]
    var diagonal := sector in [1, 3, 5, 7]
    var rear := sector in [5, 6, 7]
    var left := sector in [3, 4, 5]
    var side_sign := -1.0 if left else (1.0 if sector in [0, 1, 7] else 0.0)

    # Strong enough to read at the actual 1280x720 gameplay scale. Side sectors are
    # true profile silhouettes, diagonals sit between profile and front/rear views.
    _last_body_width = 0.72 if side else (0.86 if diagonal else 1.0)
    _last_shoulder_width = 0.58 if side else (0.78 if diagonal else 1.0)
    _last_hip_width = 0.64 if side else (0.82 if diagonal else 1.0)
    _last_face_width = 0.46 if side else (0.72 if diagonal else 1.0)

    _apply_core_width("HeadHR", 0.80 if side else (0.90 if diagonal else 1.0))
    _apply_core_width("HairHR", 0.82 if side else (0.91 if diagonal else 1.0))
    _apply_core_width("TorsoHR", _last_body_width)
    _apply_core_width("PelvisHR", 0.76 if side else (0.88 if diagonal else 1.0))

    var base_positions: Dictionary = visual.get("_base_positions")
    var torso := _bones.get("torso") as Bone2D
    var head := _bones.get("head") as Bone2D
    var ul := _bones.get("upper_arm_L") as Bone2D
    var ur := _bones.get("upper_arm_R") as Bone2D
    var tl := _bones.get("thigh_L") as Bone2D
    var tr := _bones.get("thigh_R") as Bone2D

    if torso:
        var torso_base: Vector2 = base_positions.get("torso", torso.position)
        torso.position.x = torso_base.x + side_sign * (1.9 if side else (0.9 if diagonal else 0.0))
    if head:
        var head_base: Vector2 = base_positions.get("head", head.position)
        head.position.x = head_base.x + side_sign * (4.4 if side else (2.4 if diagonal else 0.0))
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
    _apply_face_profile(side_sign, rear)
    _last_sector = sector

func _apply_core_width(name: String, width: float) -> void:
    var sprite := visual.find_child(name, true, false) as Sprite2D
    if sprite == null:
        return
    if not _sprite_base_scales.has(name):
        _sprite_base_scales[name] = sprite.scale
    var base_scale: Vector2 = _sprite_base_scales[name]
    sprite.scale = Vector2(base_scale.x * width, base_scale.y)

func _apply_limb_depth(sector: int) -> void:
    var side_or_diagonal := sector in [0, 1, 3, 4, 5, 7]
    var left_facing := sector in [3, 4, 5]
    var rear := sector in [5, 6, 7]
    var ul := _bones.get("upper_arm_L") as Bone2D
    var ur := _bones.get("upper_arm_R") as Bone2D
    var tl := _bones.get("thigh_L") as Bone2D
    var tr := _bones.get("thigh_R") as Bone2D

    # PremiumOperatorPresentation already establishes front/rear depth. For profile
    # and diagonal sectors, explicitly separate near/far limbs so the silhouette is
    # not a mirrored front-facing paper doll.
    if side_or_diagonal:
        if left_facing:
            if ul: ul.z_index = 5
            if ur: ur.z_index = -3
            if tl: tl.z_index = 2
            if tr: tr.z_index = -2
            _set_limb_alpha("UpperArmLHR", 1.0)
            _set_limb_alpha("LowerArmLHR", 1.0)
            _set_limb_alpha("ThighLHR", 1.0)
            _set_limb_alpha("ShinLHR", 1.0)
            _set_limb_alpha("UpperArmRHR", 0.58)
            _set_limb_alpha("LowerArmRHR", 0.58)
            _set_limb_alpha("ThighRHR", 0.68)
            _set_limb_alpha("ShinRHR", 0.68)
        else:
            if ur: ur.z_index = 5
            if ul: ul.z_index = -3
            if tr: tr.z_index = 2
            if tl: tl.z_index = -2
            _set_limb_alpha("UpperArmRHR", 1.0)
            _set_limb_alpha("LowerArmRHR", 1.0)
            _set_limb_alpha("ThighRHR", 1.0)
            _set_limb_alpha("ShinRHR", 1.0)
            _set_limb_alpha("UpperArmLHR", 0.58)
            _set_limb_alpha("LowerArmLHR", 0.58)
            _set_limb_alpha("ThighLHR", 0.68)
            _set_limb_alpha("ShinLHR", 0.68)
    else:
        if ul: ul.z_index = -2 if rear else 3
        if ur: ur.z_index = -1 if rear else 4
        if tl: tl.z_index = 0
        if tr: tr.z_index = 0
        for name in ["UpperArmLHR","LowerArmLHR","UpperArmRHR","LowerArmRHR","ThighLHR","ShinLHR","ThighRHR","ShinRHR"]:
            _set_limb_alpha(name, 1.0)

func _set_limb_alpha(name: String, alpha: float) -> void:
    var sprite := visual.find_child(name, true, false) as Sprite2D
    if sprite != null:
        sprite.self_modulate = Color(1.0, 1.0, 1.0, alpha)

func _apply_face_profile(side_sign: float, rear: bool) -> void:
    var face := visual.find_child("FaceMicroRig", true, false) as Node2D
    if face == null:
        return
    if rear:
        face.visible = false
        face.scale = Vector2.ONE
        face.position = Vector2(0, -1.5)
        return
    face.scale = Vector2(_last_face_width, 0.96 if _last_face_width < 1.0 else 1.0)
    face.position = Vector2(side_sign * (2.6 if _last_face_width < 0.6 else (1.3 if _last_face_width < 1.0 else 0.0)), -1.5)

func debug_current_contract() -> Dictionary:
    return {
        "sector": _last_sector,
        "body_width": _last_body_width,
        "shoulder_width": _last_shoulder_width,
        "hip_width": _last_hip_width,
        "face_width": _last_face_width,
        "rear": _last_sector in [5, 6, 7],
        "profile": _last_sector in [0, 4]
    }
