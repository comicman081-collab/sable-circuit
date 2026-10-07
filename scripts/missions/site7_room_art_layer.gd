extends Node2D
class_name Site7RoomArtLayer

const MANIFEST_PATH := "res://data/visual/site7_battle_art.json"
const WORLD_LAYOUT := preload("res://scripts/missions/site7_world_layout.gd")
const MASK_MAX_POLYGONS := 8
const MASK_MAX_POINTS := 128
# Matches the battlefield's ACTOR_EDGE_CLEARANCE: an earlier plate's floor is fully
# uncovered where actors can stand on it.
const MASK_FEATHER := 20.0
## The plates darken toward their borders. A mask fades out over this fraction of
## the earlier plate's width and height, so a later plate is never cut away over
## that near-black band (build_site7_world_layout.py LIT_INSET).
const MASK_EDGE_FADE := 0.15
## A connector's painted deck is lit right up to its top and bottom borders, where it
## met the room plates under it in a straight cut. Those borders fade over this
## fraction of the plate height, except on the deck actors walk (its own floor).
const CAP_FADE := 0.1
const CAP_MAX_POINTS := 24
## Room plates fade out over this fraction of each side, so where a room meets the
## unlit void outside the level its border is a vignette rather than a straight cut.
## Room floors stop 7.5 % inside the border, so no walkable floor fades.
const ROOM_EDGE_FADE := 0.05
# Connectors fade their two cut ends (seam); every plate is also transparent over
# the painted floor of any plate drawn before it, so no later plate's walls or void
# cover floor the actors walk on. A connector is also graded by its seam light
# (site7_world_layout.gd seam_light): each plate was painted under its own lighting,
# and the light brings the deck to the brightness and saturation of the room floor
# it runs into, turning from one room's light to the other's along the deck. Hue
# is never shifted.
# Then the mood light (site7_mood.gd): the v2 plates are painted under one neutral
# light, so each room's mood is lit here. A plate takes its room's grade (a light
# multiplier and saturation; a connector turns from one room's grade to the
# other's along its deck, mood_axis between its doors) plus the pools of the lamps
# near it, in world space so overlapping plates agree. Pools lie on the floor
# (half as tall as wide) and may pulse. Lamps and glows themselves keep their
# painted colour. The plate's flat outer void (void_mask) is see-through, so the
# abyss backdrop shows there.
const MOOD := preload("res://scripts/missions/site7_mood.gd")
const ABYSS := preload("res://scripts/missions/site7_abyss_backdrop.gd")
const SEALED_BULKHEAD := preload("res://scripts/missions/site7_sealed_bulkhead.gd")
const MOOD_MAX_LIGHTS := 24
const PLATE_SHADER := """shader_type canvas_item;
uniform float edge_width = 0.12;
uniform bool vertical = false;
uniform int poly_count = 0;
uniform int poly_end[8];
uniform vec4 poly_box[8];
uniform vec4 poly_rect[8];
uniform vec2 poly_fade[8];
uniform vec2 poly_point[128];
uniform float feather = 24.0;
uniform float cap_width = 0.0;
uniform int keep_end = 0;
uniform vec2 keep_point[24];
uniform sampler2D seam_light : filter_linear, repeat_disable;
uniform float seam_light_range = 0.0;
uniform sampler2D void_mask : filter_linear, repeat_disable;
uniform bool use_void_mask = false;
uniform bool mood = false;
uniform vec4 mood_room_a = vec4(1.0);
uniform vec4 mood_room_b = vec4(1.0);
uniform vec4 mood_axis = vec4(0.0);
uniform int mood_light_count = 0;
uniform vec4 mood_light[24];
uniform vec4 mood_light_color[24];
uniform vec2 mood_contrast = vec2(1.0, 0.18);
uniform vec4 mood_shadow = vec4(0.0);
varying vec2 local_pos;
varying vec2 world_pos;
void vertex() {
    local_pos = VERTEX;
    world_pos = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}
void fragment() {
    vec4 pixel = texture(TEXTURE, UV);
    float axis = vertical ? UV.y : UV.x;
    float weight = edge_width > 0.0 ? smoothstep(0.0, edge_width, axis) * smoothstep(0.0, edge_width, 1.0 - axis) : 1.0;
    float hide = 0.0;
    int start = 0;
    for (int p = 0; p < 8; p++) {
        if (p >= poly_count) { break; }
        int end = poly_end[p];
        vec4 box = poly_box[p];
        if (local_pos.x >= box.x && local_pos.y >= box.y && local_pos.x <= box.z && local_pos.y <= box.w) {
            bool within = false;
            float d2 = 1e12;
            for (int i = start; i < end; i++) {
                vec2 a = poly_point[i];
                vec2 b = poly_point[i + 1 < end ? i + 1 : start];
                if ((a.y > local_pos.y) != (b.y > local_pos.y) && local_pos.x < (b.x - a.x) * (local_pos.y - a.y) / (b.y - a.y) + a.x) { within = !within; }
                vec2 ab = b - a;
                vec2 q = local_pos - a - ab * clamp(dot(local_pos - a, ab) / max(dot(ab, ab), 0.0001), 0.0, 1.0);
                d2 = min(d2, dot(q, q));
            }
            if (within) {
                vec4 r = poly_rect[p];
                float edge = smoothstep(0.0, poly_fade[p].x, min(local_pos.x - r.x, r.z - local_pos.x)) * smoothstep(0.0, poly_fade[p].y, min(local_pos.y - r.y, r.w - local_pos.y));
                hide = max(hide, smoothstep(0.0, feather, sqrt(d2)) * edge);
            }
        }
        start = end;
    }
    float cap = 1.0;
    if (cap_width > 0.0) {
        float across = vertical ? UV.x : UV.y;
        cap = smoothstep(0.0, cap_width, across) * smoothstep(0.0, cap_width, 1.0 - across);
        if (cap < 1.0 && keep_end >= 3) {
            bool on_deck = false;
            float k2 = 1e12;
            for (int i = 0; i < 24; i++) {
                if (i >= keep_end) { break; }
                vec2 a = keep_point[i];
                vec2 b = keep_point[i + 1 < keep_end ? i + 1 : 0];
                if ((a.y > local_pos.y) != (b.y > local_pos.y) && local_pos.x < (b.x - a.x) * (local_pos.y - a.y) / (b.y - a.y) + a.x) { on_deck = !on_deck; }
                vec2 ab = b - a;
                vec2 q = local_pos - a - ab * clamp(dot(local_pos - a, ab) / max(dot(ab, ab), 0.0001), 0.0, 1.0);
                k2 = min(k2, dot(q, q));
            }
            if (on_deck) { cap = max(cap, smoothstep(0.0, feather, sqrt(k2))); }
        }
    }
    vec3 rgb = pixel.rgb;
    if (seam_light_range > 0.0) {
        // x: brightness gain, y: saturation around luminance. Already bright pixels
        // are neither brightened nor resaturated, so lamps keep their look
        // (build_site7_world_layout.py apply_light, LIGHT_KNEE).
        vec2 light = exp2((texture(seam_light, UV).rg * 2.0 - 1.0) * seam_light_range);
        float keep = smoothstep(0.45, 0.85, max(rgb.r, max(rgb.g, rgb.b)));
        rgb *= mix(light.x, min(light.x, 1.0), keep);
        float luma = dot(rgb, vec3(0.299, 0.587, 0.114));
        rgb = clamp(vec3(luma) + (rgb - vec3(luma)) * mix(light.y, 1.0, keep), 0.0, 1.0);
    }
    if (mood) {
        vec4 grade = mood_room_a;
        vec2 span = mood_axis.zw - mood_axis.xy;
        if (dot(span, span) > 1.0) {
            float t = clamp(dot(world_pos - mood_axis.xy, span) / dot(span, span), 0.0, 1.0);
            grade = mix(mood_room_a, mood_room_b, smoothstep(0.2, 0.8, t));
        }
        vec3 light = grade.rgb;
        for (int i = 0; i < 24; i++) {
            if (i >= mood_light_count) { break; }
            vec4 lamp = mood_light[i];
            vec2 d = (world_pos - lamp.xy) * vec2(1.0, 2.0);
            float f = 1.0 - dot(d, d) / (lamp.z * lamp.z);
            if (f <= 0.0) { continue; }
            float pulse = 1.0 + mood_light_color[i].a * sin(TIME * 6.2831853 * lamp.w);
            light += mood_light_color[i].rgb * (f * f * pulse);
        }
        vec3 lit = rgb * light;
        float lit_luma = dot(lit, vec3(0.299, 0.587, 0.114));
        lit = vec3(lit_luma) + (lit - vec3(lit_luma)) * grade.a;
        // The mission's style: contrast around a dark pivot, then its colour in the shadows.
        lit = mix(vec3(mood_contrast.y), lit, mood_contrast.x);
        lit += mood_shadow.rgb * (mood_shadow.a * (1.0 - smoothstep(0.0, 0.3, dot(lit, vec3(0.299, 0.587, 0.114)))));
        float glow = smoothstep(0.45, 0.85, max(pixel.r, max(pixel.g, pixel.b)));
        rgb = clamp(mix(lit, rgb, glow), 0.0, 1.0);
    }
    float see_through = use_void_mask ? texture(void_mask, UV).r : 0.0;
    COLOR = vec4(rgb, pixel.a * weight * cap * (1.0 - hide) * (1.0 - see_through));
}
"""
static var _shader: Shader

static func _plate_shader() -> Shader:
    if _shader == null:
        _shader = Shader.new()
        _shader.code = PLATE_SHADER
    return _shader

var _room_asset_paths: Array[String] = []
var _sprites: Array[Sprite2D] = []
var _connector_plates: Array[Sprite2D] = []
var _room_count := 0
var _connector_count := 0
var _load_failures := 0
var _stage: StoryStage01
var _selected_mission_id := "UNBOUND"
var _production_assets_available := false
var _world_bounds := Rect2()
var _horizontal_seam_material: ShaderMaterial
var _vertical_seam_material: ShaderMaterial

# All authored plates are one world-space level. The camera follows the squad
# across their union; entering combat cannot exchange the background image.

func _ready() -> void:
    # Ground shadows (-30) must remain ABOVE the opaque floor plate.
    z_index = -100
    add_to_group("m6_room_art")
    _stage = get_parent() as StoryStage01
    call_deferred("_load_manifest")

func _load_manifest() -> void:
    if not _sprites.is_empty():
        return
    if not FileAccess.file_exists(MANIFEST_PATH):
        push_error("Site7RoomArtLayer missing manifest")
        _load_failures += 1
        return
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST_PATH))
    if not (parsed is Dictionary):
        push_error("Site7RoomArtLayer manifest parse failed")
        _load_failures += 1
        return
    var mission_id := "MIS_CH01_01"
    if _stage != null and not _stage.mission.is_empty():
        mission_id = str(_stage.mission.get("mission_id", mission_id)).to_upper()
    _selected_mission_id = mission_id
    var missions_value: Variant = parsed.get("missions", {})
    if not (missions_value is Dictionary):
        push_error("Site7RoomArtLayer mission manifest missing missions")
        _load_failures += 1
        return
    var mission_manifest_value: Variant = (missions_value as Dictionary).get(mission_id, {})
    if not (mission_manifest_value is Dictionary) or (mission_manifest_value as Dictionary).is_empty():
        # Stage data may ship before its dedicated art set. Keep the authored
        # lower facility layer visible and do not substitute another mission's
        # backgrounds or treat missing future art as corrupt existing content.
        _production_assets_available = false
        return
    _production_assets_available = true
    _horizontal_seam_material = ShaderMaterial.new()
    _horizontal_seam_material.shader = _plate_shader()
    _vertical_seam_material = ShaderMaterial.new()
    _vertical_seam_material.shader = _plate_shader()
    _vertical_seam_material.set_shader_parameter("vertical", true)
    var mission_manifest: Dictionary = mission_manifest_value
    var placed_connectors: Array = WORLD_LAYOUT.mission_connectors(mission_id)
    var room_centers: Dictionary = {}
    if _stage:
        for room: Dictionary in _stage.main_route + _stage.optional_rooms:
            room_centers[str(room.id)] = Vector2(float(room.x), float(room.y))
    for collection_name in ["rooms", "connectors"]:
        var collection_index := 0
        for row_variant in mission_manifest.get(collection_name, []):
            if not (row_variant is Dictionary):
                continue
            var row: Dictionary = row_variant
            var rel_path := str(row.get("asset", ""))
            var resource_path := "res://" + rel_path
            if rel_path.is_empty() or not preload("res://scripts/core/battle_texture_library.gd").has_texture(resource_path):
                push_error("Site7RoomArtLayer missing asset: " + rel_path)
                _load_failures += 1
                continue
            var texture := preload("res://scripts/core/battle_texture_library.gd").texture(resource_path)
            if texture == null:
                push_error("Site7RoomArtLayer asset failed to import: " + rel_path)
                _load_failures += 1
                continue
            var sprite := Sprite2D.new()
            sprite.name = str(row.get("asset_id", "RoomArt"))
            sprite.set_meta("room_id", str(row.get("room_id", "")))
            sprite.set_meta("asset", rel_path)
            sprite.set_meta("seam_fade", float(row.get("seam_fade", 0.12)))
            sprite.texture = texture
            sprite.centered = true
            var pos_value: Variant = row.get("position", [0, 0])
            if pos_value is Array and pos_value.size() >= 2:
                sprite.position = Vector2(float(pos_value[0]), float(pos_value[1]))
            sprite.scale = Vector2.ONE * float(row.get("scale", 0.30))
            if collection_name == "rooms" and room_centers.has(str(row.get("room_id", ""))):
                sprite.position = room_centers[str(row.room_id)]
            elif collection_name == "connectors" and collection_index < placed_connectors.size():
                # Solved layout: the painted deck runs into both rooms' floors.
                # Authored descending decks stay unmirrored; only legacy branch
                # art uses the solved mirror. No plate is ever rotated.
                var placed: Dictionary = placed_connectors[collection_index]
                var at: Array = placed.get("position", [0, 0])
                sprite.position = Vector2(float(at[0]), float(at[1]))
                if bool(placed.get("mirror", false)): sprite.scale.x = -sprite.scale.x
                sprite.set_meta("reverse", bool(placed.get("reverse", false)))
            elif collection_name == "connectors" and _stage:
                var a: Dictionary = _stage.main_route[collection_index] if collection_index < 5 else _stage.branch_parent(collection_index - 5)
                var b: Dictionary = _stage.main_route[collection_index + 1] if collection_index < 5 else _stage.optional_rooms[collection_index - 5]
                sprite.position = Vector2(float(a.x), float(a.y)).lerp(Vector2(float(b.x), float(b.y)), 0.5)
            collection_index += 1
            sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
            sprite.modulate = Color.WHITE
            sprite.visible = true
            if collection_name == "connectors":
                sprite.material = _horizontal_seam_material
            add_child(sprite)
            _sprites.append(sprite)
            var local_half := texture.get_size() * 0.5
            var plate_bounds := Rect2(sprite.to_global(-local_half), Vector2.ZERO)
            for corner in [Vector2(local_half.x, -local_half.y), Vector2(local_half.x, local_half.y), Vector2(-local_half.x, local_half.y)]:
                plate_bounds = plate_bounds.expand(sprite.to_global(corner))
            _world_bounds = plate_bounds if _world_bounds.size == Vector2.ZERO else _world_bounds.merge(plate_bounds)
            if collection_name == "rooms":
                _room_count += 1
                _room_asset_paths.append(rel_path)
            else:
                _connector_count += 1
                _connector_plates.append(sprite)
    _build_sealed_doors(placed_connectors)

## All three operations use the same eight Stage 3 room plates in different
## orders. A painted opening is sealed when this mission has no link on its side.
func _build_sealed_doors(placed_connectors: Array) -> void:
    if _selected_mission_id not in ["MIS_CH01_03", "MIS_CH01_04", "MIS_CH01_05"]:
        return
    const FLOOR_PATH := "res://data/visual/site7_plate_floors.json"
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(FLOOR_PATH))
    if not (parsed is Dictionary): return
    var plates: Dictionary = (parsed as Dictionary).get("plates", {})
    var used := {}
    for conn: Dictionary in placed_connectors:
        for anchor: Dictionary in conn.get("door_anchors", []):
            used[str(anchor.get("room", "")) + ":" + str(anchor.get("side", ""))] = true
    for sprite in _sprites:
        if _connector_plates.has(sprite): continue
        var asset := str(sprite.get_meta("asset", ""))
        if not asset.begins_with("assets/environments/site7_v2/stage03/"): continue
        var room_id := str(sprite.get_meta("room_id", ""))
        var dimensions := sprite.texture.get_size()
        var doors: Dictionary = (plates.get(asset, {}) as Dictionary).get("doors", {})
        for side: String in doors:
            if used.has(room_id + ":" + side): continue
            var door: Array = doors[side]
            var centre := sprite.to_global(Vector2((float(door[0]) - 0.5) * dimensions.x, (float(door[1]) - 0.5) * dimensions.y))
            var span := float(door[2]) * dimensions.x * absf(sprite.scale.x)
            var tangent := Vector2(2.0, 1.0).normalized() if side in ["NE", "SW"] else Vector2(2.0, -1.0).normalized()
            var wall_height := 120.0 if side in ["NE", "NW"] else 88.0
            var panel: Site7SealedBulkhead = SEALED_BULKHEAD.new().setup(room_id, side, centre - tangent * span * 0.5, centre + tangent * span * 0.5, wall_height)
            add_child(panel)
func constrain_camera(target: Vector2, zoom: float) -> Vector2:
    if _world_bounds.size == Vector2.ZERO:
        return target
    var view_half := get_viewport_rect().size / maxf(zoom, 0.1) * 0.5
    var low := _world_bounds.position + view_half
    var high := _world_bounds.end - view_half
    if low.x > high.x: low.x = _world_bounds.get_center().x; high.x = low.x
    if low.y > high.y: low.y = _world_bounds.get_center().y; high.y = low.y
    return target.clamp(low, high)

## `floors` maps plate sprites to their painted floor (world polygon). Each plate is
## made transparent over the floors of the plates drawn before it (feathered by
## MASK_FEATHER). Connectors keep their seam fade, fade their top and bottom
## borders off their deck (CAP_FADE) and take their seam light; rooms fade every
## border (ROOM_EDGE_FADE). A mission with a mood row also lights every plate
## (_apply_mood; `doors` maps connector indices to their [room a, room b] door
## points) and gets the abyss backdrop.
func apply_floor_masks(floors: Dictionary, doors: Dictionary = {}) -> void:
    var lights := _mood_lights(floors)
    var earlier: Array[PackedVector2Array] = []
    var earlier_rects: Array[Rect2] = []
    for sprite in _sprites:
        var connector := _connector_plates.has(sprite)
        var half := sprite.texture.get_size() * 0.5
        var plate_rect := Rect2(sprite.to_global(-half), Vector2.ZERO)
        for corner in [Vector2(half.x, -half.y), half, Vector2(-half.x, half.y)]: plate_rect = plate_rect.expand(sprite.to_global(corner))
        var ends := PackedInt32Array()
        var boxes := PackedVector4Array()
        var rects := PackedVector4Array()
        var fades := PackedVector2Array()
        var points := PackedVector2Array()
        var own_scale := sprite.scale.abs()
        for earlier_index in range(earlier.size()):
            var shape := earlier[earlier_index]
            if ends.size() >= MASK_MAX_POLYGONS: break
            var world_box := Rect2(shape[0], Vector2.ZERO)
            for vertex in shape: world_box = world_box.expand(vertex)
            if not world_box.intersects(plate_rect) or points.size() + shape.size() > MASK_MAX_POINTS: continue
            var local_box := Rect2(sprite.to_local(shape[0]), Vector2.ZERO)
            for vertex in shape:
                var local := sprite.to_local(vertex)
                points.append(local)
                local_box = local_box.expand(local)
            local_box = local_box.grow(2.0)
            ends.append(points.size())
            boxes.append(Vector4(local_box.position.x, local_box.position.y, local_box.end.x, local_box.end.y))
            # Plates are never rotated, so the earlier plate's rect stays axis-aligned here.
            var under := earlier_rects[earlier_index]
            var a := sprite.to_local(under.position)
            var b := sprite.to_local(under.end)
            rects.append(Vector4(minf(a.x, b.x), minf(a.y, b.y), maxf(a.x, b.x), maxf(a.y, b.y)))
            fades.append(under.size * MASK_EDGE_FADE / Vector2(maxf(0.01, own_scale.x), maxf(0.01, own_scale.y)))
        var own: PackedVector2Array = floors.get(sprite, PackedVector2Array())
        if own.size() >= 3:
            earlier.append(own)
            earlier_rects.append(plate_rect)
        var material := ShaderMaterial.new()
        material.shader = _plate_shader()
        material.set_shader_parameter("edge_width", float(sprite.get_meta("seam_fade", 0.12)) if connector else ROOM_EDGE_FADE)
        if not connector:
            material.set_shader_parameter("cap_width", ROOM_EDGE_FADE)
        if connector and own.size() >= 3 and own.size() <= CAP_MAX_POINTS:
            var keep := PackedVector2Array()
            for vertex in own: keep.append(sprite.to_local(vertex))
            var keep_count := keep.size()
            keep.resize(CAP_MAX_POINTS)
            material.set_shader_parameter("cap_width", CAP_FADE)
            material.set_shader_parameter("keep_end", keep_count)
            material.set_shader_parameter("keep_point", keep)
            sprite.set_meta("cap_fade", CAP_FADE)
        var light: Image = WORLD_LAYOUT.seam_light(_selected_mission_id, _connector_plates.find(sprite)) if connector else null
        if light:
            material.set_shader_parameter("seam_light", ImageTexture.create_from_image(light))
            material.set_shader_parameter("seam_light_range", WORLD_LAYOUT.seam_light_range())
            sprite.set_meta("seam_light", true)
        material.set_shader_parameter("feather", MASK_FEATHER / maxf(0.01, absf(sprite.scale.y)))
        material.set_shader_parameter("poly_count", ends.size())
        sprite.set_meta("floor_masks", ends.size())
        while ends.size() < MASK_MAX_POLYGONS:
            ends.append(points.size())
            boxes.append(Vector4.ZERO)
            rects.append(Vector4.ZERO)
            fades.append(Vector2.ONE)
        points.resize(MASK_MAX_POINTS)
        material.set_shader_parameter("poly_end", ends)
        material.set_shader_parameter("poly_box", boxes)
        material.set_shader_parameter("poly_rect", rects)
        material.set_shader_parameter("poly_fade", fades)
        material.set_shader_parameter("poly_point", points)
        _apply_mood(sprite, material, plate_rect, lights, doors)
        sprite.material = material
    if MOOD.has_mission(_selected_mission_id):
        _build_abyss(floors)

## Every mood light of the mission in world space: each plate's lights (texture
## coordinates) through its transform and its overhead fill over the middle of its
## floor, tinted by the mission grade.
func _mood_lights(floors: Dictionary) -> Array[Dictionary]:
    var result: Array[Dictionary] = []
    if not MOOD.has_mission(_selected_mission_id): return result
    var mission := MOOD.mission_grade(_selected_mission_id)
    var tint := Vector3(mission.x, mission.y, mission.z)
    for sprite in _sprites:
        var size := sprite.texture.get_size()
        var asset := str(sprite.get_meta("asset", ""))
        for light: Dictionary in MOOD.plate_lights(asset, _selected_mission_id):
            var at: Vector2 = light.at
            result.append({"position": sprite.to_global((at - Vector2(0.5, 0.5)) * size), "radius": float(light.radius),
                    "color": (light.color as Vector3) * tint, "hz": float(light.hz), "depth": float(light.depth)})
        var fill := MOOD.plate_fill(asset, _selected_mission_id)
        var floor_shape: PackedVector2Array = floors.get(sprite, PackedVector2Array())
        if fill.is_empty() or floor_shape.size() < 3: continue
        var center := Vector2.ZERO
        var box := Rect2(floor_shape[0], Vector2.ZERO)
        for vertex in floor_shape:
            center += vertex
            box = box.expand(vertex)
        result.append({"position": center / float(floor_shape.size()), "radius": maxf(box.size.x, box.size.y) * float(fill.get("reach", 0.55)),
                "color": (fill.color as Vector3) * tint, "hz": 0.0, "depth": 0.0})
    return result

## A room's grade under the mission's.
func _room_grade(room_id: String) -> Vector4:
    var mission := MOOD.mission_grade(_selected_mission_id)
    var plate := get_room_plate(room_id)
    var own := MOOD.plate_grade(str(plate.get_meta("asset", "")), _selected_mission_id) if plate else Vector4.ONE
    return Vector4(own.x * mission.x, own.y * mission.y, own.z * mission.z, own.w * mission.w)

## [room a, room b] ids of a connector, as the battlefield links them: the main
## route in order, then each branch from its parent room.
func _connector_rooms(index: int) -> Array[String]:
    if _stage == null: return []
    var main: Array = _stage.main_route
    if index < main.size() - 1: return [str(main[index].id), str(main[index + 1].id)]
    var branch := index - (main.size() - 1)
    if branch < 0 or branch >= _stage.optional_rooms.size(): return []
    return [str(_stage.branch_parent(branch).id), str(_stage.optional_rooms[branch].id)]

func _apply_mood(sprite: Sprite2D, material: ShaderMaterial, plate_rect: Rect2, lights: Array[Dictionary], doors: Dictionary) -> void:
    if not MOOD.has_mission(_selected_mission_id): return
    var asset := str(sprite.get_meta("asset", ""))
    var mask := MOOD.void_mask(asset)
    if mask:
        material.set_shader_parameter("void_mask", ImageTexture.create_from_image(mask))
        material.set_shader_parameter("use_void_mask", true)
        sprite.set_meta("void_mask", true)
    var grade_a := _room_grade(str(sprite.get_meta("room_id", "")))
    var grade_b := grade_a
    var axis := Vector4.ZERO
    var index := _connector_plates.find(sprite)
    if index >= 0:
        var rooms := _connector_rooms(index)
        if rooms.size() == 2:
            grade_a = _room_grade(rooms[0])
            grade_b = _room_grade(rooms[1])
            var ends: Array = doors.get(index, [])
            if ends.size() < 2:
                var plate_a := get_room_plate(rooms[0])
                var plate_b := get_room_plate(rooms[1])
                if plate_a and plate_b: ends = [plate_a.global_position, plate_b.global_position]
            if ends.size() >= 2: axis = Vector4(ends[0].x, ends[0].y, ends[1].x, ends[1].y)
    material.set_shader_parameter("mood", true)
    material.set_shader_parameter("mood_room_a", grade_a)
    material.set_shader_parameter("mood_room_b", grade_b)
    material.set_shader_parameter("mood_axis", axis)
    var style := MOOD.mission_style(_selected_mission_id)
    material.set_shader_parameter("mood_contrast", Vector2(float(style.contrast), float(style.pivot)))
    material.set_shader_parameter("mood_shadow", style.shadow)
    # Every light whose pool reaches the plate, so plates that overlap light the
    # same world point alike; the strongest first if more than the shader holds.
    var reaching: Array[Dictionary] = []
    for light in lights:
        var radius := float(light.radius)
        if Rect2(light.position - Vector2(radius, radius * 0.5), Vector2(radius * 2.0, radius)).intersects(plate_rect): reaching.append(light)
    reaching.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return (a.color as Vector3).length() * float(a.radius) > (b.color as Vector3).length() * float(b.radius))
    var positions := PackedVector4Array()
    var colors := PackedVector4Array()
    for light in reaching.slice(0, MOOD_MAX_LIGHTS):
        positions.append(Vector4(light.position.x, light.position.y, float(light.radius), float(light.hz)))
        colors.append(Vector4(light.color.x, light.color.y, light.color.z, float(light.depth)))
    sprite.set_meta("mood_lights", positions.size())
    sprite.set_meta("mood_lights_dropped", maxi(0, reaching.size() - MOOD_MAX_LIGHTS))
    material.set_shader_parameter("mood_light_count", positions.size())
    positions.resize(MOOD_MAX_LIGHTS)
    colors.resize(MOOD_MAX_LIGHTS)
    material.set_shader_parameter("mood_light", positions)
    material.set_shader_parameter("mood_light_color", colors)

## The abyss behind the level: haze lit by each plate's lamps under its floor.
func _build_abyss(floors: Dictionary) -> void:
    var glows: Array[Dictionary] = []
    var contacts: Array[Dictionary] = []
    var settings := MOOD.abyss(_selected_mission_id)
    var mission := MOOD.mission_grade(_selected_mission_id)
    for sprite in _sprites:
        if str(settings.get("style", "")) == "dawn" and float(settings.get("contact_shadow_strength", 0.0)) > 0.0:
            var contact := MOOD.contact_shadow(str(sprite.get_meta("asset", "")))
            if not contact.is_empty():
                var size := Vector2(sprite.texture.get_size()) * sprite.scale.abs()
                var padding := Vector2.ONE * float(contact.padding_px) * sprite.scale.abs()
                contacts.append({"image": contact.image, "rect": Rect2(sprite.global_position - size * 0.5 - padding, size + padding * 2.0)})
        var floor_shape: PackedVector2Array = floors.get(sprite, PackedVector2Array())
        if floor_shape.size() < 3: continue
        var center := Vector2.ZERO
        var box := Rect2(floor_shape[0], Vector2.ZERO)
        for vertex in floor_shape:
            center += vertex
            box = box.expand(vertex)
        center /= float(floor_shape.size())
        var connector := _connector_plates.has(sprite)
        var grade := _room_grade(str(sprite.get_meta("room_id", ""))) if not connector else mission
        var tint := Vector3(grade.x, grade.y, grade.z) / maxf(0.001, maxf(grade.x, maxf(grade.y, grade.z)))
        glows.append({"position": center, "radius": maxf(box.size.x, box.size.y) * (0.45 if connector else 0.6),
                "color": MOOD.plate_haze(str(sprite.get_meta("asset", "")), _selected_mission_id) * tint, "strength": 0.6 if connector else 1.0})
    var backdrop := get_node_or_null("AbyssBackdrop") as Node2D
    if backdrop == null:
        backdrop = ABYSS.new()
        backdrop.name = "AbyssBackdrop"
        add_child(backdrop)
        move_child(backdrop, 0)
    backdrop.call("setup", _world_bounds.grow(800.0), settings, glows, contacts)

func lock_combat_room(_value: String) -> void:
    # Kept as a compatibility entry point; combat does not replace map art.
    pass

func get_room_plate(value: String) -> Sprite2D:
    for sprite in _sprites:
        if str(sprite.get_meta("room_id", "")) == value: return sprite
    return null

func get_connector_plate(index: int) -> Sprite2D:
    return _connector_plates[index] if index >= 0 and index < _connector_plates.size() else null

func debug_asset_count() -> int:
    return _room_count

func debug_unique_asset_count() -> int:
    var unique: Dictionary = {}
    for path in _room_asset_paths:
        unique[path] = true
    return unique.size()

func debug_all_assets_loaded() -> bool:
    return _load_failures == 0 and _room_count == 8 and _connector_count == 7 and debug_unique_asset_count() == 8

func debug_primary_art_layer() -> bool:
    return z_index < 0

func debug_m7_blended_deck() -> bool:
    return z_index < 0

func debug_local_plate_contract() -> Dictionary:
    return {
        "continuous_route_preserved": true,
        "world_anchored_opaque_segment_streaming": false,
        "traversal_selection": "single_world_all_plates",
        "combat_plate_lock": "",
        "uncropped_continuity_overscan": true,
        "max_visible_plates": _sprites.size(),
        "room_plate_count": _room_count,
        "connector_plate_count": _connector_count,
        "selected_mission_id": _selected_mission_id,
        "production_assets_available": _production_assets_available,
        "procedural_fallback_active": not _production_assets_available
    }

func debug_streaming_state() -> Dictionary:
    var visible_ids: Array[String] = []
    var opacities: Dictionary = {}
    for sprite in _sprites:
        if sprite.visible:
            visible_ids.append(sprite.name)
            opacities[sprite.name] = snappedf(sprite.modulate.a, 0.001)
    visible_ids.sort()
    return {"visible_ids":visible_ids,"opacities":opacities}
