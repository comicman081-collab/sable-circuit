extends Node2D
class_name AsterStaticPreGatePreview

## Isolated visual-comparison scene. This is deliberately not an OperatorActor:
## it owns no controls, collision, targeting, combat, skeleton, or animation.

const MASK_DERIVED_RGBA_PATH := "res://assets/units/operators/aster/pre_gate/ASTER_STATIC_MASTER_PRE_GATE_RGBA.png"

@onready var preview_sprite: Sprite2D = $PRE_GATE_NONPROMOTED_ASTER_STATIC_PREVIEW

func _ready() -> void:
    add_to_group("aster_static_pre_gate_preview")
    var image := Image.new()
    var load_error := image.load(MASK_DERIVED_RGBA_PATH)
    if load_error == OK and not image.is_empty():
        preview_sprite.texture = ImageTexture.create_from_image(image)
    queue_redraw()
    if preview_sprite.texture == null:
        push_error("ASTER_PRE_GATE_STATIC_PREVIEW missing RGBA derivative")

func _draw() -> void:
    # A lightweight contact shadow is QA context only; it is not painted into
    # either the locked #00FF00 source or the mask-derived RGBA texture.
    draw_set_transform(Vector2(612, 420), 0.0, Vector2.ONE)
    _draw_qa_ellipse(Vector2.ZERO, Vector2(42, 11), Color(0.0, 0.0, 0.0, 0.34))
    draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

func _draw_qa_ellipse(center: Vector2, radii: Vector2, color: Color) -> void:
    var points := PackedVector2Array()
    for index in range(32):
        points.append(center + Vector2(cos(TAU * float(index) / 32.0) * radii.x, sin(TAU * float(index) / 32.0) * radii.y))
    draw_colored_polygon(points, color)

func debug_contract() -> Dictionary:
    return {
        "pre_gate": true,
        "nonpromoted": true,
        "static_preview": true,
        "operator_actor_used": false,
        "animation_or_skeleton_connected": false,
        "gameplay_data_changed": false,
        "uses_mask_derived_rgba": preview_sprite != null and preview_sprite.texture != null,
        "source_green_runtime_visible": false,
    }
