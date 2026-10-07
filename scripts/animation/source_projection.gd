extends RefCounted
## Shared source camera and ground-distance interpretation. No appearance fallback.

static func resolve(value: Variant) -> Dictionary:
    if value == null:
        return {"size": 2.0, "center_height": 0.875, "screen_center_height": 0.875,
            "forward": Vector3.FORWARD, "up": Vector3.UP, "ground_vertical_scale": 1.0}
    if not value is Dictionary or value.get("schema") != 1 or value.get("kind") != "source_orthographic_elevation":
        return {}
    for key in ["elevation_degrees", "camera_center_height_m", "orthographic_size_m"]:
        if not (value.get(key) is float or value.get(key) is int) or not is_finite(float(value[key])):
            return {}
    var elevation := float(value["elevation_degrees"])
    var center := float(value["camera_center_height_m"])
    var size := float(value["orthographic_size_m"])
    if elevation < 5.0 or elevation > 60.0 or center <= 0.0 or size <= 0.0:
        return {}
    var angle := deg_to_rad(elevation)
    return {"size": size, "center_height": center, "screen_center_height": center*cos(angle),
        "forward": Vector3(0, -sin(angle), -cos(angle)), "up": Vector3(0, cos(angle), -sin(angle)),
        "ground_vertical_scale": sin(angle)}
