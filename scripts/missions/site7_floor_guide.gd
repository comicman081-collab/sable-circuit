extends Node2D
class_name Site7FloorGuide
## Painted wayfinding on the deck, after the mockup's "<- CONTROL RELAY" floor
## stencil: chevrons and the current objective room's name, laid on the floor
## plane along the real navigation path from the controlled operator to the
## objective. Presentation only; it never changes routing or objectives.

const NAV := preload("res://scripts/combat/cover_navigation.gd")
const FLOOR_SQUASH := 0.6
const STENCIL_AHEAD := 250.0
const CHEVRON_START := 120.0
const CHEVRON_SPACING := 38.0
const MIN_REMAINING := 280.0
const REPLAN_SECONDS := 0.45
const PAINT := Color(0.92, 0.86, 0.72)
const GLOW := Color(0.35, 0.92, 0.96)

var stage: StoryStage01
var _font: Font
var _nav := NAV.new()
var _path := PackedVector2Array()
var _replan_left := 0.0
var _planned_step := -1
var _planned_from := Vector2.INF
var _time := 0.0
var _alpha := 0.0
var _label := ""

func _ready() -> void:
    stage = get_parent() as StoryStage01
    z_as_relative = false
    z_index = -60
    _font = load("res://assets/fonts/demo_font.tres") as Font

func _process(delta: float) -> void:
    _time += delta
    var visible_target := _should_show()
    if visible_target:
        _replan_left -= delta
        var actor := stage.squad.get_active_operator()
        if _replan_left <= 0.0 or _planned_step != stage.current_step or actor.global_position.distance_to(_planned_from) > 140.0:
            _replan(actor)
    var combat_dim := 0.35 if bool(stage.get("_combat_started")) else 1.0
    var target_alpha := combat_dim if visible_target and _remaining() >= MIN_REMAINING else 0.0
    _alpha = move_toward(_alpha, target_alpha, delta * 2.5)
    queue_redraw()

func _should_show() -> bool:
    if stage == null or stage.squad == null or stage.battle_preview: return false
    if bool(stage.get("_mission_ended")) or bool(stage.get("_extraction_offer_active")): return false
    if stage.current_step < 0 or stage.current_step >= stage.main_route.size(): return false
    if stage.battlefield == null or not bool(stage.battlefield.get("world_ready")): return false
    return stage.squad.get_active_operator() != null

func _objective_point() -> Vector2:
    var row: Dictionary = stage.main_route[stage.current_step]
    return stage.constrain_battle_position(Vector2(float(row.x), float(row.y)))

func _replan(actor: OperatorActor) -> void:
    _replan_left = REPLAN_SECONDS
    _planned_step = stage.current_step
    _planned_from = actor.global_position
    var row: Dictionary = stage.main_route[stage.current_step]
    _label = str(row.get("title", "OBJECTIVE")).to_upper()
    var goal := _objective_point()
    var obstacles := NAV.ground_obstacles(actor)
    _path = PackedVector2Array([actor.global_position])
    if NAV._clear_ground(actor, actor.global_position, goal, obstacles):
        _path.append(goal)
    else:
        var plan := _nav._plan(actor, actor.global_position, goal, obstacles)
        if plan.is_empty():
            _path.clear()
            return
        _path.append_array(plan)

func _remaining() -> float:
    var total := 0.0
    for i in range(_path.size() - 1): total += _path[i].distance_to(_path[i + 1])
    return total

## Point and direction `distance` along the planned path.
func _sample(distance: float) -> Dictionary:
    var left := distance
    for i in range(_path.size() - 1):
        var a := _path[i]
        var b := _path[i + 1]
        var span := a.distance_to(b)
        if span <= 0.001: continue
        if left <= span:
            return {"point": a.lerp(b, left / span), "dir": (b - a) / span}
        left -= span
    if _path.size() >= 2:
        return {"point": _path[-1], "dir": (_path[-1] - _path[-2]).normalized()}
    return {}

## World transform for drawing on the floor plane at `point`, x along `dir`.
func _floor_transform(point: Vector2, dir: Vector2) -> Transform2D:
    var floor_dir := Vector2(dir.x, dir.y / FLOOR_SQUASH).normalized()
    return Transform2D(0.0, point) * Transform2D(0.0, Vector2(1.0, FLOOR_SQUASH), 0.0, Vector2.ZERO) * Transform2D(floor_dir.angle(), Vector2.ZERO)

func _draw() -> void:
    if _alpha <= 0.01 or _path.size() < 2: return
    var sweep := fmod(_time * 1.4, 1.0)
    # Chevron trail leading away from the squad along the route.
    for i in range(3):
        var s := _sample(CHEVRON_START + CHEVRON_SPACING * i)
        if s.is_empty(): continue
        var lit := 1.0 - clampf(absf(float(i) / 2.0 - sweep) * 2.2, 0.0, 1.0)
        draw_set_transform_matrix(_floor_transform(s.point, s.dir))
        var colour := Color(PAINT.lerp(GLOW, lit * 0.8), _alpha * (0.34 + 0.4 * lit))
        draw_polyline(PackedVector2Array([Vector2(-7, -13), Vector2(7, 0), Vector2(-7, 13)]), colour, 4.0, true)
    # Stencilled room name with an arrow, reading left-to-right.
    var stencil := _sample(STENCIL_AHEAD)
    if not stencil.is_empty():
        var dir: Vector2 = stencil.dir
        var leftward := dir.x < 0.0
        var text_dir := -dir if leftward else dir
        draw_set_transform_matrix(_floor_transform(stencil.point, text_dir))
        var size := 22
        var width := _font.get_string_size(_label, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x if _font else 120.0
        var paint := Color(PAINT, _alpha * 0.5)
        var arrow_x := -width * 0.5 - 30.0 if leftward else width * 0.5 + 14.0
        var arrow_sign := -1.0 if leftward else 1.0
        draw_colored_polygon(PackedVector2Array([
            Vector2(arrow_x + arrow_sign * 16.0, 0), Vector2(arrow_x, -9), Vector2(arrow_x, -3.5),
            Vector2(arrow_x - arrow_sign * 12.0, -3.5), Vector2(arrow_x - arrow_sign * 12.0, 3.5), Vector2(arrow_x, 3.5), Vector2(arrow_x, 9)]), paint)
        if _font:
            draw_string(_font, Vector2(-width * 0.5, size * 0.36), _label, HORIZONTAL_ALIGNMENT_LEFT, -1, size, paint)
        # Painted border strokes above and below the text, like floor markings.
        draw_line(Vector2(-width * 0.5 - 34.0, -18.0), Vector2(width * 0.5 + 34.0, -18.0), Color(PAINT, _alpha * 0.18), 2.0)
        draw_line(Vector2(-width * 0.5 - 34.0, 18.0), Vector2(width * 0.5 + 34.0, 18.0), Color(PAINT, _alpha * 0.18), 2.0)
    draw_set_transform_matrix(Transform2D.IDENTITY)

func debug_guide_state() -> Dictionary:
    return {"visible": _alpha > 0.01, "label": _label, "path_points": _path.size(), "remaining": _remaining(), "step": _planned_step}
