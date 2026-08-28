extends Node
class_name OperatorDirectionalScaleGuard

# Runs immediately after OperatorSectorSilhouettePresentation. The directional
# replacement plates are authored in bone-local pixels, while the legacy frontal
# head is a cropped 512-tile sprite. This guard normalizes side/rear head scale so
# switching sectors does not make a 3-4-head operator's skull visibly pump in size.

const PROFILE_HEAD_SCALE := 0.82
const REAR_HEAD_SCALE := 0.84

var actor: OperatorActor
var visual: OperatorVisual
var _last_sector := -1
var _last_head_scale := 1.0

func _ready() -> void:
    process_priority = 113
    actor = get_parent() as OperatorActor
    if actor:
        visual = actor.get_node_or_null("VisualRoot") as OperatorVisual

func _process(_delta: float) -> void:
    sync_now()

func sync_now() -> void:
    if actor == null or visual == null:
        return
    var sector := posmod(actor.facing_sector,8)
    _last_sector = sector
    if sector in [0,4]:
        _last_head_scale = PROFILE_HEAD_SCALE
        _scale_directional_head("M7Profile", PROFILE_HEAD_SCALE, -1.0 if sector == 4 else 1.0, 1.0)
    elif sector in [5,6,7]:
        _last_head_scale = REAR_HEAD_SCALE
        var turn_width := 0.92 if sector != 6 else 1.0
        _scale_directional_head("M7Rear", REAR_HEAD_SCALE, turn_width, REAR_HEAD_SCALE)
    else:
        _last_head_scale = 1.0

func _scale_directional_head(prefix: String, uniform_scale: float, x_sign_or_width: float, y_scale: float) -> void:
    var head_bone := visual.find_child("head",true,false) as Bone2D
    if head_bone == null:
        return
    for child in head_bone.get_children():
        if child is CanvasItem and child.name.begins_with(prefix):
            var item := child as CanvasItem
            if prefix == "M7Profile":
                item.scale = Vector2(x_sign_or_width * uniform_scale, uniform_scale)
            else:
                item.scale = Vector2(x_sign_or_width * uniform_scale, y_scale)

func debug_contract() -> Dictionary:
    return {
        "profile_head_scale":PROFILE_HEAD_SCALE,
        "rear_head_scale":REAR_HEAD_SCALE,
        "last_sector":_last_sector,
        "last_head_scale":_last_head_scale,
        "prevents_direction_size_pumping":true
    }
