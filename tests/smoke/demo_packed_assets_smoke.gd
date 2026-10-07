extends SceneTree

func _initialize() -> void:
    var failures: Array[String] = []
    var projectile_path := "res://assets/units/operators/aster/vfx/ASTER_COIL_PROJECTILE_V6_RGBA.webp"
    var raw := FileAccess.get_file_as_bytes(projectile_path)
    var image := Image.new()
    if raw.is_empty() or image.load_webp_from_buffer(raw) != OK or image.get_size() != Vector2i(768,192):
        failures.append("Packed authored ASTER projectile must decode at original size")
    var intro_audio_path := "res://assets/cinematics/sable_intro_original_bgm.ogv"
    if FileAccess.get_file_as_bytes(intro_audio_path).size() < 55_000_000:
        failures.append("Packed intro must contain the original-audio OGV")
    var catalog_path := "res://sound/music/catalog.json"
    if not FileAccess.file_exists(catalog_path):
        failures.append("Packed music catalog missing")
    if not FileAccess.file_exists("res://data/art_profiles/playable_profiles.json"):
        failures.append("Packed playable profiles missing")
    for character_id in ["aster", "mica", "rook"]:
        var atlas_path := "res://motion_lab_v1/public/assets/atlas/%s/E_walk.web.webp" % character_id
        var atlas_bytes := FileAccess.get_file_as_bytes(atlas_path)
        var atlas := Image.new()
        if atlas_bytes.is_empty() or atlas.load_webp_from_buffer(atlas_bytes) != OK or atlas.get_size() != Vector2i(1152, 768):
            failures.append("Packed half-resolution Web motion atlas missing: " + character_id)
    for machine_path in [
        "res://assets/enemies/recon_drone/authored_yaw8_v1/E.web.webp",
        "res://assets/enemies/signal_anchor_guardian/authored_core_v1/anchor.web.webp"
    ]:
        var machine_bytes := FileAccess.get_file_as_bytes(machine_path)
        var machine := Image.new()
        if machine_bytes.is_empty() or machine.load_webp_from_buffer(machine_bytes) != OK or machine.get_width() < 400:
            failures.append("Packed half-resolution Web machine view missing: " + machine_path)
    var report := {"pass":failures.is_empty(),"failed":failures,"projectile_bytes":raw.size(),"packed_resource_check":true}
    print("DEMO_PACKED_ASSETS ",JSON.stringify(report))
    quit(0 if failures.is_empty() else 1)
