extends SceneTree
## The ten bosses side by side at one game scale, each with its health bar, on a plain backdrop. It needs no
## room, so it also shows the bosses of operations 6-10, which have no plates yet. Every boss is drawn at one
## scale (a world pixel is 1.333 frame pixels; the stage camera would show 1.83), so sizes compare true to
## each other. Sizes are the machine's own mass (`visible_rect_px`) in that frame.
## Run windowed (not --headless) for the frame; headless still checks every boss's size and bounds.
##   Godot --path . -s res://tests/render/site7_boss_lineup_capture.gd -- --out=res://<folder>
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const TestOutput := preload("res://tests/support/test_output.gd")
const BOSSES := ["BOSS_SITE7_ANCHOR_01", "BOSS_SITE7_RELAY_01", "BOSS_SITE7_REMNANT_01", "BOSS_SITE7_FORGE_01", "BOSS_SITE7_CARRIER_01",
    "BOSS_SITE7_AERATOR_01", "BOSS_SITE7_CRYO_01", "BOSS_SITE7_GANTRY_01", "BOSS_SITE7_ARCHIVE_01", "BOSS_SITE7_ORIGIN_01"]
## Content space is 1440x810; the window scales it to 1920x1080.
const CONTENT := Vector2(1440.0, 810.0)
const FRAME_SCALE := 1920.0 / 1440.0
const FEET_Y := [385.0, 745.0]
## Content pixels between two machines of a row.
const GAP := 28.0
## A boss stands within this share of the ten bosses' median height.
const HEIGHT_BAND := Vector2(0.8, 1.25)
var failures: Array[String] = []
var rows: Array[Dictionary] = []

func _init() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
    if not ok: failures.append(label); push_error(label)

func run() -> void:
    var out := TestOutput.path("res://.cache/site7_boss_lineup")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(CONTENT)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    var native_capture := DisplayServer.get_name() != "headless"
    if native_capture:
        DisplayServer.window_set_size(Vector2i(1920, 1080))
    var backdrop := CanvasLayer.new()
    backdrop.layer = -10
    root.add_child(backdrop)
    var floor_color := ColorRect.new()
    floor_color.color = Color(0.11, 0.125, 0.15)
    floor_color.size = CONTENT
    backdrop.add_child(floor_color)
    var labels := CanvasLayer.new()
    labels.layer = 50
    root.add_child(labels)
    var bosses: Array[EnemyActor] = []
    for index in range(BOSSES.size()):
        var actor := ENEMY.instantiate() as EnemyActor
        check(actor.configure(BOSSES[index], 1000.0), BOSSES[index] + " configures")
        actor.position = Vector2(CONTENT.x * 0.5, FEET_Y[index / 5])
        root.add_child(actor)
        actor.set_physics_process(false)
        bosses.append(actor)
    for _i in range(6):
        await process_frame
    # Machines differ in width, so each row is packed by measured bounds and centred.
    for row_index in range(2):
        var members := bosses.slice(row_index * 5, row_index * 5 + 5)
        var total := GAP * float(members.size() - 1)
        for actor in members: total += _bounds(actor).size.x
        var cursor := (CONTENT.x - total) * 0.5
        for actor in members:
            var bounds := _bounds(actor)
            actor.position.x += cursor - bounds.position.x
            # A boss is pinned to where it spawned (BossAnchorLockPresentation), so the pin moves with it.
            actor.home_position = actor.global_position
            cursor += bounds.size.x + GAP
    for index in range(bosses.size()):
        var label := Label.new()
        label.text = "%02d  %s" % [index + 1, str(BOSSES[index]).trim_prefix("BOSS_SITE7_").trim_suffix("_01")]
        label.position = Vector2(_bounds(bosses[index]).get_center().x - 46.0, FEET_Y[index / 5] + 16.0)
        label.add_theme_font_size_override("font_size", 15)
        label.add_theme_color_override("font_color", Color(0.92, 0.95, 1.0))
        label.add_theme_color_override("font_outline_color", Color(0, 0, 0))
        label.add_theme_constant_override("outline_size", 4)
        labels.add_child(label)
    for _i in range(3):
        await process_frame
    var heights: Array[float] = []
    for actor in bosses:
        var machine: Node2D = actor.machine_sprite
        check(is_instance_valid(machine) and machine.configured, actor.enemy_id + " authored renderer")
        if not is_instance_valid(machine) or not machine.configured: continue
        var bounds := _bounds(actor)
        heights.append(bounds.size.y * FRAME_SCALE)
        check(Rect2(Vector2.ZERO, CONTENT).grow(-6.0).encloses(bounds), actor.enemy_id + " inside the frame")
        rows.append({"enemy_id": actor.enemy_id, "frame_bounds_px": Rect2(bounds.position * FRAME_SCALE, bounds.size * FRAME_SCALE),
            "screen_height_px": snappedf(bounds.size.y * FRAME_SCALE, 0.1), "screen_width_px": snappedf(bounds.size.x * FRAME_SCALE, 0.1)})
    for row_index in range(2):
        for index in range(row_index * 5, row_index * 5 + 4):
            check(_bounds(bosses[index]).end.x <= _bounds(bosses[index + 1]).position.x, "%s and %s do not overlap" % [BOSSES[index], BOSSES[index + 1]])
    var sorted := heights.duplicate()
    sorted.sort()
    var median: float = sorted[sorted.size() / 2] if not sorted.is_empty() else 0.0
    for row in rows:
        var ratio: float = float(row.screen_height_px) / maxf(1.0, median)
        row["height_vs_median"] = snappedf(ratio, 0.001)
        check(ratio >= HEIGHT_BAND.x and ratio <= HEIGHT_BAND.y, "%s stands %.2fx the median boss" % [row.enemy_id, ratio])
    if native_capture:
        await RenderingServer.frame_post_draw
        var image := root.get_texture().get_image()
        check(image.get_size() == Vector2i(1920, 1080), "native 1080p frame")
        check(image.save_png(ProjectSettings.globalize_path(out.path_join("bosses_01_10_game_scale.png"))) == OK, "save frame")
    var file := FileAccess.open(out.path_join("lineup_report.json"), FileAccess.WRITE)
    file.store_string(JSON.stringify({"status": "PASS_TECHNICAL_ONLY" if failures.is_empty() else "FAIL", "failures": failures,
        "native_capture": native_capture, "native_resolution": [1920, 1080] if native_capture else [],
        "scale_note": "1 world px = 1.333 frame px (content scale 1440x810 to 1080p); the stage camera would show 1.83",
        "median_screen_height_px": snappedf(median, 0.1), "visual_approval": false, "rows": rows}, "  "))
    file.close()
    print("SITE7_BOSS_LINEUP_CAPTURE: ", "PASS" if failures.is_empty() else "FAIL", " ", out)
    quit(0 if failures.is_empty() else 1)

## The machine's own mass in content pixels.
func _bounds(actor: EnemyActor) -> Rect2:
    var machine: Node2D = actor.machine_sprite
    var art: Rect2 = machine.visible_rect
    var transform: Transform2D = machine.sprite.get_global_transform_with_canvas()
    var bounds := Rect2(transform * art.position, Vector2.ZERO)
    for corner in [art.position + Vector2(art.size.x, 0.0), art.end, art.position + Vector2(0.0, art.size.y)]:
        bounds = bounds.expand(transform * corner)
    return bounds
