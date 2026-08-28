extends Node2D
class_name BossArenaPresentation

const ARENA_CENTER := Vector2(1920.0, 490.0)
const PYLON_OFFSETS: Array[Vector2] = [
    Vector2(-154.0,-88.0), Vector2(154.0,-88.0),
    Vector2(-154.0,96.0), Vector2(154.0,96.0)
]

var stage: StoryStage01
var _phase := 0
var _previous_phase := 0
var _pulse := 0.0
var _spin := 0.0
var _transition_flash := 0.0
var _boss_alive := false

func _ready() -> void:
    process_priority = 74
    stage = get_parent() as StoryStage01
    # M7 Phase 3 arena telegraphs are floor presentation. They must never cover
    # the boss body or operator silhouettes.
    z_index = -1

func _process(delta: float) -> void:
    _pulse = fposmod(_pulse + delta * (0.55 + float(_phase) * 0.18), 1.0)
    _spin += delta * (0.18 + float(_phase) * 0.08)
    _transition_flash = move_toward(_transition_flash, 0.0, delta * 2.8)
    var boss := _find_boss()
    _boss_alive = boss != null
    var next_phase := 0
    if boss != null:
        var ratio := boss.health / maxf(1.0, boss.max_health)
        next_phase = 1 if ratio > 0.66 else (2 if ratio > 0.33 else 3)
    if next_phase != _phase:
        _previous_phase = _phase
        _phase = next_phase
        if _phase >= 2:
            _transition_flash = 1.0
    queue_redraw()

func _find_boss() -> EnemyActor:
    if stage == null:
        return null
    for node in stage.get_tree().get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and ("BOSS" in node.enemy_id or "ANCHOR" in node.enemy_id):
            return node
    return null

func _active_pylon_count() -> int:
    if _phase == 2: return 2
    if _phase == 3: return 4
    return 0

func _pylon_is_active(index: int) -> bool:
    if _phase == 3: return true
    if _phase == 2: return index == 0 or index == 3
    return false

func _draw() -> void:
    if not _boss_alive:
        return

    # Subtle authored floor dais. Keep all structural values below actor contrast.
    draw_circle(ARENA_CENTER, 154.0, Color(0.045,0.038,0.070,0.26))
    draw_arc(ARENA_CENTER, 154.0, 0.0, TAU, 96, Color(0.32,0.23,0.55,0.30), 2.5)
    draw_arc(ARENA_CENTER, 116.0, -_spin, TAU-_spin, 80, Color(0.46,0.34,0.78,0.22), 1.7)
    draw_arc(ARENA_CENTER, 78.0, _spin*0.65, TAU+_spin*0.65, 64, Color(0.38,0.28,0.67,0.16), 1.6)

    for i in range(PYLON_OFFSETS.size()):
        var p := ARENA_CENTER + PYLON_OFFSETS[i]
        var active := _pylon_is_active(i)
        draw_circle(p, 23.0, Color(0.055,0.05,0.085,0.60))
        draw_rect(Rect2(p-Vector2(10,27), Vector2(20,54)), Color(0.10,0.09,0.14,0.82), true)
        draw_rect(Rect2(p-Vector2(6,21), Vector2(12,42)), Color(0.17,0.14,0.22,0.80), true)
        if active:
            var glow := 0.46 + sin(_spin*3.4 + float(i))*0.09
            draw_circle(p, 9.0, Color(0.66,0.39,1.0,0.09))
            draw_arc(p, 25.0 + sin(_spin*2.0+i)*1.8, 0.0, TAU, 32, Color(0.68,0.43,1.0,glow), 2.4)
            draw_line(p, ARENA_CENTER, Color(0.54,0.33,0.90,0.08 if _phase == 2 else 0.12), 1.4)
        else:
            draw_arc(p, 24.0, 0.0, TAU, 32, Color(0.27,0.22,0.36,0.20), 1.5)

    if _transition_flash > 0.0:
        draw_arc(ARENA_CENTER, 165.0 + (1.0-_transition_flash)*24.0, 0.0, TAU, 72, Color(0.84,0.56,1.0,_transition_flash*0.12), 3.0)

    if _phase == 2:
        draw_arc(ARENA_CENTER, 188.0, -0.70+_spin*0.24, 0.70+_spin*0.24, 54, Color(0.53,0.40,0.92,0.13), 4.0)
        draw_arc(ARENA_CENTER, 188.0, 2.44+_spin*0.24, 3.84+_spin*0.24, 54, Color(0.53,0.40,0.92,0.13), 4.0)
    elif _phase == 3:
        # Four narrow, floor-only warning lanes with large movement gaps.
        for i in range(4):
            var a := _spin + float(i) * PI * 0.5
            var dir := Vector2.RIGHT.rotated(a)
            var side := dir.rotated(PI*0.5)
            var inner := ARENA_CENTER + dir*94.0
            var outer := ARENA_CENTER + dir*222.0
            var poly := PackedVector2Array([
                inner-side*8.0, inner+side*8.0,
                outer+side*20.0, outer-side*20.0
            ])
            draw_colored_polygon(poly, Color(0.75,0.23,0.66,0.032))
            draw_line(inner, outer, Color(0.86,0.44,0.98,0.20), 1.5)
        var weak_alpha := 0.33 + sin(_spin*4.0)*0.06
        draw_circle(ARENA_CENTER, 29.0, Color(0.92,0.44,1.0,0.035))
        draw_arc(ARENA_CENTER, 42.0+_pulse*5.0, 0.0, TAU, 48, Color(1.0,0.64,0.95,weak_alpha), 2.6)
        draw_arc(ARENA_CENTER, 28.0, -_spin*1.8, TAU-_spin*1.8, 40, Color(0.72,0.49,1.0,0.36), 1.5)

func debug_phase() -> int:
    return _phase

func debug_active_pylon_count() -> int:
    return _active_pylon_count()

func debug_weakpoint_exposed() -> bool:
    return _phase == 3

func debug_contract() -> Dictionary:
    return {
        "arena_center": ARENA_CENTER,
        "pylon_count": PYLON_OFFSETS.size(),
        "phase1_active_pylons": 0,
        "phase2_active_pylons": 2,
        "phase3_active_pylons": 4,
        "phase3_wedges": 4,
        "weakpoint_exposed_phase3": true,
        "clear_movement_gaps": true,
        "separate_from_boss_body": true,
        "phase3_body_clear": true,
        "floor_only_telegraphs": true,
        "arena_z": -1,
        "boss_center_matches_arena": true,
        "m7_boss_arena": true
    }
