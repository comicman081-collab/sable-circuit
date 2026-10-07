extends RefCounted
## Runtime mood light for the SITE-7 background plates. The v2 plates are painted
## under one neutral light so their seams match, and each room's mood is added at
## runtime instead: data/visual/site7_mood.json holds the authored grades, lamp
## tuning, extra lights and abyss backdrop per mission; site7_mood_lamps.json the
## lamp pools and site7_void_masks.json the see-through outer void of each plate
## (both from tools/environment/build_site7_mood_light.py). Only plates, never
## robot or operator art, take this light.

const PATH := "res://data/visual/site7_mood.json"
const LAMPS_PATH := "res://data/visual/site7_mood_lamps.json"
const VOID_PATH := "res://data/visual/site7_void_masks.json"
const CONTACT_PATH := "res://data/visual/site7_contact_shadows.json"
const LUMA := Vector3(0.299, 0.587, 0.114)
static var _mood: Dictionary = {}
static var _lamps: Dictionary = {}
static var _voids: Dictionary = {}
static var _contacts: Dictionary = {}
static var _loaded := false

static func _read(path: String) -> Dictionary:
    if not FileAccess.file_exists(path): return {}
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
    return parsed if parsed is Dictionary else {}

static func _load() -> void:
    if _loaded: return
    _loaded = true
    _mood = _read(PATH)
    _lamps = (_read(LAMPS_PATH).get("plates", {}) as Dictionary)
    _voids = (_read(VOID_PATH).get("plates", {}) as Dictionary)
    _contacts = (_read(CONTACT_PATH).get("plates", {}) as Dictionary)

static func _mission_row(mission_id: String) -> Dictionary:
    _load()
    var row: Variant = (_mood.get("missions", {}) as Dictionary).get(mission_id.to_upper(), {})
    return row if row is Dictionary else {}

## A plate's row: its shared row with the mission's own row for it (the mission
## row's "plates") laid over key by key, so a plate several missions share can
## light each of them differently.
static func _plate_row(asset: String, mission_id: String = "") -> Dictionary:
    _load()
    var row: Variant = (_mood.get("plates", {}) as Dictionary).get(asset, {})
    var merged: Dictionary = (row as Dictionary).duplicate() if row is Dictionary else {}
    var own: Variant = (_mission_row(mission_id).get("plates", {}) as Dictionary).get(asset, {}) if not mission_id.is_empty() else {}
    if own is Dictionary: merged.merge(own, true)
    return merged

## Whether the mission has a mood row (its plates, void and backdrop are lit).
static func has_mission(mission_id: String) -> bool:
    return not _mission_row(mission_id).is_empty()

## (r, g, b) light multiplier and saturation factor of a row's exposure, tint and
## saturation. The tint keeps luminance; exposure alone sets brightness.
static func _grade(row: Dictionary) -> Vector4:
    var tint := Vector3.ONE
    var value: Variant = row.get("tint", [1.0, 1.0, 1.0])
    if value is Array and (value as Array).size() >= 3: tint = Vector3(float(value[0]), float(value[1]), float(value[2]))
    tint /= maxf(0.001, tint.dot(LUMA))
    tint *= pow(2.0, float(row.get("exposure", 0.0)))
    return Vector4(tint.x, tint.y, tint.z, float(row.get("saturation", 1.0)))

static func mission_grade(mission_id: String) -> Vector4:
    return _grade(_mission_row(mission_id))

## The mission's plate style: {contrast, pivot (the luminance contrast turns
## around), shadow: Vector4 (rgb colour lifted into the dark tones, a = amount)}.
static func mission_style(mission_id: String) -> Dictionary:
    var row := _mission_row(mission_id)
    var shadow := Vector4.ZERO
    var shadows: Variant = row.get("shadows", {})
    if shadows is Dictionary:
        var color: Array = (shadows as Dictionary).get("color", [0.0, 0.0, 0.0])
        shadow = Vector4(float(color[0]), float(color[1]), float(color[2]), float((shadows as Dictionary).get("strength", 0.0)))
    return {"contrast": float(row.get("contrast", 1.0)), "pivot": float(row.get("pivot", 0.18)), "shadow": shadow}

## A room plate's own grade in the mission (white for a plate without one).
static func plate_grade(asset: String, mission_id: String = "") -> Vector4:
    return _grade(_plate_row(asset, mission_id))

## The plate's lights in its texture coordinates: its lamp pools (tuned by its
## "lamps" row) then its extra "lights". Each: {at: Vector2 uv, radius: world px,
## color: Vector3 (already times strength), hz, depth}.
static func plate_lights(asset: String, mission_id: String = "") -> Array[Dictionary]:
    var row := _plate_row(asset, mission_id)
    var result: Array[Dictionary] = []
    var tuning: Dictionary = row.get("lamps", {})
    var pulse: Array = tuning.get("pulse", [0.0, 0.0])
    for lamp: Array in _lamps.get(asset, []) if not tuning.is_empty() else []:
        var strength := float(tuning.get("strength", 0.5)) * (0.5 + 0.5 * float(lamp[5]))
        result.append({"at": Vector2(float(lamp[0]), float(lamp[1])), "radius": float(tuning.get("radius", 200.0)),
                "color": Vector3(float(lamp[2]), float(lamp[3]), float(lamp[4])) * strength,
                "hz": float(pulse[0]), "depth": float(pulse[1])})
    for light: Dictionary in row.get("lights", []):
        var at: Array = light.get("at", [0.5, 0.5])
        var color: Array = light.get("color", [1.0, 1.0, 1.0])
        var light_pulse: Array = light.get("pulse", [0.0, 0.0])
        result.append({"at": Vector2(float(at[0]), float(at[1])), "radius": float(light.get("radius", 300.0)),
                "color": Vector3(float(color[0]), float(color[1]), float(color[2])) * float(light.get("strength", 0.4)),
                "hz": float(light_pulse[0]), "depth": float(light_pulse[1])})
    return result

## The room's overhead fill over the middle of its floor: {color: Vector3 (times
## strength), reach: radius as a share of the floor's larger side}; empty for none.
static func plate_fill(asset: String, mission_id: String = "") -> Dictionary:
    var fill: Variant = _plate_row(asset, mission_id).get("fill", {})
    if not (fill is Dictionary) or float((fill as Dictionary).get("strength", 0.0)) <= 0.0: return {}
    var color: Array = (fill as Dictionary).get("color", [1.0, 1.0, 1.0])
    return {"color": Vector3(float(color[0]), float(color[1]), float(color[2])) * float(fill.strength), "reach": float((fill as Dictionary).get("reach", 0.55))}

## Colour the plate's lamps throw into the haze around it (their weighted mean,
## scaled so the strongest channel is 1), or white.
static func plate_haze(asset: String, mission_id: String = "") -> Vector3:
    var row := _plate_row(asset, mission_id)
    var value: Variant = row.get("haze", null)
    if value is Array and (value as Array).size() >= 3: return Vector3(float(value[0]), float(value[1]), float(value[2]))
    var sum := Vector3.ZERO
    for lamp: Array in _lamps.get(asset, []):
        sum += Vector3(float(lamp[2]), float(lamp[3]), float(lamp[4])) * float(lamp[5])
    var peak := maxf(sum.x, maxf(sum.y, sum.z))
    return sum / peak if peak > 0.0 else Vector3.ONE

## Greyscale mask over the plate's texture, white where its flat outer void is
## see-through; null when the plate has none.
static func void_mask(asset: String) -> Image:
    _load()
    var encoded := str(_voids.get(asset, ""))
    if encoded.is_empty(): return null
    var image := Image.new()
    if image.load_png_from_buffer(Marshalls.base64_to_raw(encoded)) != OK: return null
    return image

## The mission's abyss backdrop settings (site7_abyss_backdrop.gd), empty for none.
static func abyss(mission_id: String) -> Dictionary:
    return _mission_row(mission_id).get("abyss", {})

## Optional backdrop contact field. The plate's own void mask stays unchanged.
static func contact_shadow(asset: String) -> Dictionary:
    _load()
    var row: Dictionary = _contacts.get(asset, {})
    if row.is_empty(): return {}
    var image := Image.new()
    if image.load_png_from_buffer(Marshalls.base64_to_raw(str(row.get("mask", "")))) != OK: return {}
    return {"image": image, "padding_px": float(row.get("padding_px", 0.0))}
