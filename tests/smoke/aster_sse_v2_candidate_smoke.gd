extends SceneTree

## One-shot, project-local smoke for the ASTER SSE V2 candidate atlas.
## It never changes the live V6 runtime authority and exits after one run.

const ATLAS_PATH := "res://art_src/pilot_v2/aster_v2/animation_360/fire_upper_16_sse_blender_v2/runtime/current/ASTER_FIRE_SSE_V16_67_5_UAL6_RUNTIME_ATLAS_RGBA.png"
const EVIDENCE_PATH := "res://art_src/pilot_v2/aster_v2/animation_360/fire_upper_16_sse_blender_v2/qa/current/ASTER_FIRE_SSE_V2_GODOT_RUNTIME_SMOKE.json"
const PHASES := ["aim_set", "preload", "muzzle_contact", "recoil_peak", "recover", "ready_return"]
const EXPECTED_MUZZLES := [Vector2i(261, 306), Vector2i(258, 304), Vector2i(260, 305), Vector2i(260, 306), Vector2i(261, 306), Vector2i(261, 306)]
const CELL_SIZE := Vector2i(384, 384)
const TARGET_TANGENT_DEGREES := 67.5

var failures: Array[String] = []
var checks: Array[Dictionary] = []


func _initialize() -> void:
    call_deferred("_run")


func _check(condition: bool, label: String) -> void:
    checks.append({"label": label, "pass": condition})
    if not condition:
        failures.append(label)


func _strong_chroma_opaque_count(image: Image) -> int:
    var count := 0
    for y in range(image.get_height()):
        for x in range(image.get_width()):
            var pixel := image.get_pixel(x, y)
            if pixel.a <= 0.0:
                continue
            var r := int(round(pixel.r * 255.0))
            var g := int(round(pixel.g * 255.0))
            var b := int(round(pixel.b * 255.0))
            if g >= 180 and g - r >= 100 and g - b >= 100:
                count += 1
    return count


func _opaque_count(image: Image) -> int:
    var count := 0
    for y in range(image.get_height()):
        for x in range(image.get_width()):
            if image.get_pixel(x, y).a > 0.0:
                count += 1
    return count


func _alpha_bbox_center(image: Image) -> Vector2:
    var minimum := Vector2i(image.get_width(), image.get_height())
    var maximum := Vector2i(-1, -1)
    for y in range(image.get_height()):
        for x in range(image.get_width()):
            if image.get_pixel(x, y).a >= 0.5:
                minimum.x = mini(minimum.x, x)
                minimum.y = mini(minimum.y, y)
                maximum.x = maxi(maximum.x, x)
                maximum.y = maxi(maximum.y, y)
    if maximum.x < minimum.x:
        return Vector2.INF
    return (Vector2(minimum) + Vector2(maximum)) * 0.5


func _detect_muzzle(image: Image) -> Vector2i:
    var tangent := Vector2.from_angle(deg_to_rad(TARGET_TANGENT_DEGREES))
    var best := Vector2i(-1, -1)
    var best_projection := -INF
    for y in range(250, 340):
        for x in range(235, 290):
            if image.get_pixel(x, y).a < 0.5:
                continue
            var projection := Vector2(x, y).dot(tangent)
            if projection > best_projection:
                best_projection = projection
                best = Vector2i(x, y)
    return best


func _run() -> void:
    var atlas := Image.load_from_file(ATLAS_PATH)
    _check(not atlas.is_empty(), "V2 runtime atlas decodes in Godot")
    _check(atlas.get_size() == Vector2i(2304, 384), "atlas is exactly 6x384 by 384")
    _check(atlas.detect_alpha() != Image.ALPHA_NONE, "atlas exposes genuine alpha")

    var atlas_texture := ImageTexture.create_from_image(atlas)
    var sprite_frames := SpriteFrames.new()
    sprite_frames.add_animation("fire")
    sprite_frames.set_animation_speed("fire", 12.0)
    sprite_frames.set_animation_loop("fire", true)
    var cells: Array[Image] = []
    var muzzle_points: Array[Vector2i] = []
    var bbox_centers: Array[Vector2] = []
    var phase_records: Array[Dictionary] = []
    for index in range(PHASES.size()):
        var region := Rect2(index * CELL_SIZE.x, 0, CELL_SIZE.x, CELL_SIZE.y)
        var frame_texture := AtlasTexture.new()
        frame_texture.atlas = atlas_texture
        frame_texture.region = region
        sprite_frames.add_frame("fire", frame_texture)
        var cell := atlas.get_region(Rect2i(index * CELL_SIZE.x, 0, CELL_SIZE.x, CELL_SIZE.y))
        cells.append(cell)
        var opaque := _opaque_count(cell)
        var chroma := _strong_chroma_opaque_count(cell)
        var muzzle := _detect_muzzle(cell)
        var center := _alpha_bbox_center(cell)
        muzzle_points.append(muzzle)
        bbox_centers.append(center)
        _check(opaque > 1000, "%s cell has visible authored pixels" % PHASES[index])
        _check(chroma == 0, "%s cell has zero opaque strong chroma" % PHASES[index])
        _check(muzzle == EXPECTED_MUZZLES[index], "%s uses the locked visible muzzle socket" % PHASES[index])
        phase_records.append({
            "phase": PHASES[index],
            "opaque_pixels": opaque,
            "opaque_strong_chroma_pixels": chroma,
            "muzzle_xy": [muzzle.x, muzzle.y],
            "alpha_bbox_center": [center.x, center.y],
        })

    _check(sprite_frames.get_frame_count("fire") == 6, "SpriteFrames contains exactly six ordered cells")
    var sprite := AnimatedSprite2D.new()
    sprite.sprite_frames = sprite_frames
    sprite.animation = "fire"
    get_root().add_child(sprite)
    sprite.play("fire")
    _check(sprite.is_playing(), "Godot AnimatedSprite2D accepts looping playback")
    var observed: Array[int] = []
    for index in range(PHASES.size()):
        sprite.frame = index
        observed.append(sprite.frame)
        var texture := sprite_frames.get_frame_texture("fire", index) as AtlasTexture
        _check(texture != null and texture.region.position.x == index * CELL_SIZE.x, "%s maps to atlas cell %d" % [PHASES[index], index])
    _check(observed == [0, 1, 2, 3, 4, 5], "runtime frame order is aim/pre/contact/peak/recover/return")
    _check(cells[0].get_data() == cells[5].get_data(), "F00 and F05 atlas cells are byte-identical")

    var max_anchor_delta := 0.0
    var max_muzzle_delta := 0.0
    for index in range(PHASES.size()):
        max_anchor_delta = maxf(max_anchor_delta, bbox_centers[index].distance_to(bbox_centers[0]))
        max_muzzle_delta = maxf(max_muzzle_delta, Vector2(muzzle_points[index]).distance_to(Vector2(muzzle_points[0])))
        var flash := Node2D.new()
        var projectile := Node2D.new()
        sprite.add_child(flash)
        sprite.add_child(projectile)
        flash.position = Vector2(muzzle_points[index])
        projectile.position = Vector2(muzzle_points[index])
        _check(flash.position.distance_to(projectile.position) <= 0.001, "%s projectile birth equals visible muzzle/flash socket" % PHASES[index])
        flash.queue_free()
        projectile.queue_free()
    _check(max_anchor_delta <= 5.0, "six-phase full-pose anchor drift stays within five runtime pixels")
    _check(max_muzzle_delta <= 4.0, "six-phase muzzle socket drift stays within four runtime pixels")

    var payload := {
        "schema": 1,
        "generated_at_utc": Time.get_datetime_string_from_system(true),
        "role": "ASTER SSE V2 candidate one-shot Godot runtime smoke",
        "result": "PASS" if failures.is_empty() else "FAIL",
        "live_v6_authority_modified": false,
        "atlas": ATLAS_PATH,
        "atlas_sha256": FileAccess.get_sha256(ATLAS_PATH),
        "phase_order": PHASES,
        "target_tangent_degrees": TARGET_TANGENT_DEGREES,
        "max_anchor_delta_px": max_anchor_delta,
        "max_muzzle_delta_px": max_muzzle_delta,
        "checks": checks,
        "failures": failures,
        "phases": phase_records,
    }
    var output_path := ProjectSettings.globalize_path(EVIDENCE_PATH)
    var handle := FileAccess.open(output_path, FileAccess.WRITE)
    _check(handle != null, "Godot can write project-local smoke evidence")
    if handle != null:
        handle.store_string(JSON.stringify(payload, "  ") + "\n")
        handle.close()
    print("ASTER_SSE_V2_GODOT_SMOKE=" + JSON.stringify({"result": payload["result"], "evidence": output_path, "failures": failures}))
    sprite.queue_free()
    quit(0 if failures.is_empty() else 1)
