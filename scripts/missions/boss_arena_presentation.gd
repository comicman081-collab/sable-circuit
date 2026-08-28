extends Node2D
class_name BossArenaPresentation

const ARENA_CENTER := Vector2(1920.0, 490.0)
const PYLON_OFFSETS: Array[Vector2] = [
    Vector2(-190.0,-92.0), Vector2(190.0,-92.0),
    Vector2(-190.0,108.0), Vector2(190.0,108.0)
]

var stage: StoryStage01
var _phase := 0
var _pulse := 0.0
var _spin := 0.0
var _boss_alive := false

func _ready() -> void:
    process_priority = 74
    stage = get_parent() as StoryStage01
    z_index = 14

func _process(delta: float) -> void:
    _pulse = fposmod(_pulse + delta * (0.55 + float(_phase) * 0.18), 1.0)
    _spin += delta * (0.22 + float(_phase) * 0.12)
    var boss := _find_boss()
    _boss_alive = boss != null
    if boss != null:
        var ratio := boss.health / maxf(1.0, boss.max_health)
        _phase = 1 if ratio > 0.66 else (2 if ratio > 0.33 else 3)
    else:
        _phase = 0
    queue_redraw()

func _find_boss() -> EnemyActor:
    if stage == null:
        return null
    for node in stage.get_tree().get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and ("BOSS" in node.enemy_id or "ANCHOR" in node.enemy_id):
            return node
    return null

func _draw() -> void:
    if not _boss_alive:
        return
    # Core dais: persistent mechanical plate; phase color is restrained so the
    # generated room art remains the dominant environment layer.
    draw_circle(ARENA_CENTER, 168.0, Color(0.08,0.07,0.13,0.34))
    draw_arc(ARENA_CENTER, 168.0, 0.0, TAU, 96, Color(0.42,0.31,0.72,0.42), 3.0)
    draw_arc(ARENA_CENTER, 126.0, -_spin, TAU-_spin, 80, Color(0.51,0.40,0.88,0.32), 2.0)

    for i in range(PYLON_OFFSETS.size()):
        var p := ARENA_CENTER + PYLON_OFFSETS[i]
        var base_alpha := 0.34 if _phase == 1 else (0.48 if _phase == 2 else 0.62)
        draw_circle(p, 25.0, Color(0.12,0.10,0.18,0.58))
        draw_arc(p, 29.0 + sin(_spin*2.0+i)*3.0, 0.0, TAU, 32, Color(0.54,0.38,0.93,base_alpha), 3.0)
        if _phase >= 2:
            draw_line(p, ARENA_CENTER, Color(0.48,0.32,0.84,0.13 if _phase==2 else 0.20), 2.0)

    if _phase == 2:
        # Two broad safe/readable orbit lanes rather than screen-filling rings.
        draw_arc(ARENA_CENTER, 220.0, -0.75+_spin*0.35, 0.82+_spin*0.35, 54, Color(0.55,0.42,0.96,0.22), 8.0)
        draw_arc(ARENA_CENTER, 220.0, 2.35+_spin*0.35, 3.92+_spin*0.35, 54, Color(0.55,0.42,0.96,0.22), 8.0)
    elif _phase == 3:
        # Four rotating wedge telegraphs leave large clean gaps for squad motion.
        for i in range(4):
            var a := _spin + float(i) * PI * 0.5
            var dir := Vector2.RIGHT.rotated(a)
            var side := dir.rotated(PI*0.5)
            var inner := ARENA_CENTER + dir*78.0
            var outer := ARENA_CENTER + dir*286.0
            var poly := PackedVector2Array([
                inner-side*18.0, inner+side*18.0,
                outer+side*44.0, outer-side*44.0
            ])
            draw_colored_polygon(poly, Color(0.77,0.24,0.68,0.075))
            draw_line(inner, outer, Color(0.88,0.47,1.0,0.38), 3.0)
        var weak_alpha := 0.42 + sin(_spin*4.0)*0.10
        draw_arc(ARENA_CENTER, 58.0+_pulse*10.0, 0.0, TAU, 48, Color(0.98,0.56,0.92,weak_alpha), 4.0)

func debug_phase() -> int:
    return _phase

func debug_contract() -> Dictionary:
    return {
        "arena_center": ARENA_CENTER,
        "pylon_count": PYLON_OFFSETS.size(),
        "phase3_wedges": 4,
        "clear_movement_gaps": true,
        "separate_from_boss_body": true,
        "m7_boss_arena": true
    }
