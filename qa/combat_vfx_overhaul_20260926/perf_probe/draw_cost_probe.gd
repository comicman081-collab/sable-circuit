extends SceneTree
## Pure GDScript geometry cost: calls each effect's _draw() directly over its lifetime
## (headless) and reports mean microseconds per frame and the mean triangle count.
const EXP := preload("res://scripts/vfx/combat_explosion_vfx.gd")
const HIT := preload("res://scripts/vfx/combat_hit_vfx.gd")
const MUZ := preload("res://scripts/vfx/combat_muzzle_vfx.gd")

func _init(): call_deferred("_run")

func _tri(p) -> int:
    var n := 0
    for key in ["_points", "points", "_verts", "verts"]:
        var v = p.get(key)
        if v is PackedVector2Array: n += v.size() / 3
    return n

func _time(node: Node, duration: float, painters: Array) -> Array:
    var total := 0
    var tris := 0
    var frames := 0
    var age := 0.0
    while age < duration:
        if node.get("age") != null: node.set("age", age)
        elif node.get("_age") != null: node.set("_age", age)
        var t := Time.get_ticks_usec()
        node.call("_draw")
        total += Time.get_ticks_usec() - t
        for key in painters:
            var p = node.get(key)
            if p != null: tris += p.triangle_count()
        frames += 1
        age += 1.0 / 60.0
    return [float(total) / frames, float(tris) / frames]

func _run():
    await process_frame
    VfxPainter.profile_atlas()
    for rep in range(2):
        await _all(rep)
    quit()

func _all(rep: int):
    for kind in EXP.KINDS:
        var fx := EXP.new()
        root.add_child(fx)
        fx.setup(kind, Color("ff9a4a"), 18.0 if kind == "SMOLDER" else 70.0, Vector2.RIGHT, 300.0)
        if kind == "TRAIL": fx.set("_trail", PackedVector2Array([Vector2(0, 0), Vector2(60, -20), Vector2(120, 0), Vector2(180, 30), Vector2(240, 0)]))
        var r := _time(fx, fx.duration, ["_paint", "_smoke"])
        if rep == 1: print("DRAW %-12s %7.1f us/frame  %6.0f tris" % [kind, r[0], r[1]])
        fx.free()
    for profile in ["HIT_GENERIC", "HIT_ARMOR_DEFLECT_01"]:
        var h := HIT.new()
        root.add_child(h)
        h.setup(profile, Color("ffb060"), Vector2.LEFT)
        var r2 := _time(h, 0.4, ["_paint"])
        if rep == 1: print("DRAW %-12s %7.1f us/frame  %6.0f tris" % [profile.substr(0, 12), r2[0], r2[1]])
        h.free()
    var m := MUZ.new()
    root.add_child(m)
    m.setup("PRJ_ROOK_SCATTER", Color("ffb060"), Vector2.RIGHT)
    var r3 := _time(m, 0.1, ["_paint"])
    if rep == 1: print("DRAW %-12s %7.1f us/frame  %6.0f tris" % ["MUZZLE_ROOK", r3[0], r3[1]])
    m.free()
