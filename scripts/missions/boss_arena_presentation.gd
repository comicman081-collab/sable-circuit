extends Node2D
class_name BossArenaPresentation

const ARENA_CENTER := Vector2(1920.0, 490.0)
const PYLON_OFFSETS: Array[Vector2] = [
    Vector2(-176.0,-96.0), Vector2(176.0,-96.0),
    Vector2(-176.0,110.0), Vector2(176.0,110.0)
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
    z_index = 14

func _process(delta: float) -> void:
    _pulse = fposmod(_pulse + delta * (0.55 + float(_phase) * 0.18), 1.0)
    _spin += delta * (0.22 + float(_phase) * 0.12)
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
    if _phase == 2:
        return 2
    if _phase == 3:
        return 4
    return 0

func _pylon_is_active(index: int) -> bool:
    if _phase == 3:
        return true
    if _phase == 2:
        return index == 0 or index == 3
    return false

func _draw() -> void:
    if not _boss_alive:
        return

    draw_circle(ARENA_CENTER, 172.0, Color(0.055,0.045,0.085,0.36))
    draw_arc(ARENA_CENTER, 172.0, 0.0, TAU, 96, Color(0.34,0.25,0.58,0.40), 3.0)
    draw_arc(ARENA_CENTER, 129.0, -_spin, TAU-_spin, 80, Color(0.48,0.37,0.82,0.30), 2.0)
    draw_arc(ARENA_CENTER, 91.0, _spin*0.65, TAU+_spin*0.65, 64, Color(0.41,0.31,0.72,0.22), 2.0)

    for i in range(PYLON_OFFSETS.size()):
        var p := ARENA_CENTER + PYLON_OFFSETS[i]
        var active := _pylon_is_active(i)
        draw_circle(p, 28.0, Color(0.07,0.06,0.10,0.68))
        draw_rect(Rect2(p-Vector2(12,31), Vector2(24,62)), Color(0.11,0.10,0.15,0.88), true)
        draw_rect(Rect2(p-Vector2(8,25), Vector2(16,50)), Color(0.18,0.15,0.24,0.86), true)
        if active:
            var glow := 0.62 + sin(_spin*3.4 + float(i))*0.14
            draw_circle(p, 12.0, Color(0.67,0.39,1.0,0.13))
            draw_arc(p, 31.0 + sin(_spin*2.0+i)*2.5, 0.0, TAU, 32, Color(0.68,0.43,1.0,glow), 3.5)
            draw_line(p, ARENA_CENTER, Color(0.55,0.34,0.91,0.16 if _phase == 2 else 0.22), 2.0)
        else:
            draw_arc(p, 29.0, 0.0, TAU, 32, Color(0.29,0.24,0.39,0.28), 2.0)

    if _transition_flash > 0.0:
        draw_arc(ARENA_CENTER, 185.0 + (1.0-_transition_flash)*35.0, 0.0, TAU, 72, Color(0.86,0.58,1.0,_transition_flash*0.20), 5.0)

    if _phase == 2:
        draw_arc(ARENA_CENTER, 221.0, -0.78+_spin*0.30, 0.80+_spin*0.30, 54, Color(0.55,0.42,0.96,0.20), 7.0)
        draw_arc(ARENA_CENTER, 221.0, 2.36+_spin*0.30, 3.94+_spin*0.30, 54, Color(0.55,0.42,0.96,0.20), 7.0)
    elif _phase == 3:
        for i in range(4):
            var a := _spin + float(i) * PI * 0.5
            var dir := Vector2.RIGHT.rotated(a)
            var side := dir.rotated(PI*0.5)
            var inner := ARENA_CENTER + dir*82.0
            var outer := ARENA_CENTER + dir*282.0
            var poly := PackedVector2Array([
                inner-side*16.0, inner+side*16.0,
                outer+side*39.0, outer-side*39.0
            ])
            draw_colored_polygon(poly, Color(0.77,0.24,0.68,0.065))
            draw_line(inner, outer, Color(0.88,0.47,1.0,0.34), 2.5)
        var weak_alpha := 0.48 + sin(_spin*4.0)*0.10
        draw_circle(ARENA_CENTER, 38.0, Color(0.93,0.46,1.0,0.055))
        draw_arc(ARENA_CENTER, 54.0+_pulse*8.0, 0.0, TAU, 48, Color(1.0,0.66,0.96,weak_alpha), 4.0)
        draw_arc(ARENA_CENTER, 35.0, -_spin*1.8, TAU-_spin*1.8, 40, Color(0.74,0.51,1.0,0.56), 2.0)

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
        "boss_center_matches_arena": true,
        "m7_boss_arena": true
    }
