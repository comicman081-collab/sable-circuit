extends SceneTree

## Current ROOK app routing, actual actor movement/fire, and both portrait UIs.
## Synthetic engine input/state tests are not a human gait-quality approval.
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
const LOBBY := preload("res://scenes/base/BaseLobby.tscn")
const HUD := preload("res://scripts/ui/story_stage_hud.gd")
const PROFILE := "res://motion_lab_v1/public/assets/atlas/rook/profile.json"
const PORTRAIT := "motion_lab_v1/public/assets/atlas/rook/portrait.png"
var failures: Array[String] = []
var checks := 0
var projectiles: Array[PrototypeProjectile] = []

func _init() -> void:
    call_deferred("run")

func check(condition: bool, label: String) -> void:
    checks += 1
    if not condition:
        failures.append(label)
        push_error(label)

func run() -> void:
    var profile := ArtProfileRegistry.get_profile("CHR_PROTO_02")
    check(profile.get("motion_lab_character_id") == "rook", "ROOK registry selects Motion Studio")
    check(not profile.has("authored_runtime_descriptor"), "No obsolete ROOK runtime pointer")
    check(profile.get("portrait_asset") == PORTRAIT, "Registry selects current approved portrait")
    var actor := OPERATOR.instantiate() as OperatorActor
    actor.configure("CHR_PROTO_02", "ROOK", Color("d39a58"))
    root.add_child(actor)
    actor.set_physics_process(false)
    actor.set_process(false)
    await process_frame
    await process_frame
    var runtime := actor.get_node("MotionLabCharacterRuntime") as MotionLabCharacterRuntime
    runtime.set_process(false)
    check(runtime.is_runtime_active(), "Current ROOK activates")
    if not runtime.is_runtime_active():
        finish()
        return
    check(runtime.debug_contract().profile_path == PROFILE, "Exact current profile loaded")
    check(is_equal_approx(float(runtime.debug_contract().display_height_px), 129.6), "User 1.8x map scale retained")
    check(not (actor.get_node("FastCharacterRuntime") as FastCharacterRuntime).is_runtime_active(), "Legacy raster is inactive")
    check(not (actor.get_node("AuthoredRasterPresentation") as OperatorAuthoredRasterPresentation).debug_loaded(), "Old static body is inactive")
    check(actor.magazine_size == 10 and is_equal_approx(actor.fire_interval, 0.42) and is_equal_approx(actor.reload_duration, 1.38), "10 round / .42s / 1.38s scattergun retained")
    actor.set_movement_bounds(Rect2(-10000,-10000,20000,20000))
    actor.projectile_spawned.connect(func(node: Node2D) -> void:
        var projectile := node as PrototypeProjectile
        projectile.set_physics_process(false)
        projectiles.append(projectile)
    )
    # Keep real CharacterBody2D displacement and the production physics method.
    # A large empty lane isolates the adapter from unrelated enemy/campaign AI.
    for hz in [30,60,120]:
        Engine.physics_ticks_per_second = hz
        var dt := 1.0 / float(hz)
        for running in [false,true]:
            for sector in range(8):
                var direction := Vector2.from_angle(float(sector) * PI / 4.0)
                actor.global_position = Vector2.ZERO
                actor.debug_drive(direction, direction)
                actor.set("_debug_run", running)
                var frames_seen: Dictionary = {}
                for tick in range(hz * 2):
                    await physics_frame
                    actor.call("_physics_process", dt)
                    frames_seen[runtime.debug_contract().frame] = true
                check(frames_seen.size() == 6, "All six frames %dHz run=%s direction=%d" % [hz,running,sector])
                check(runtime.debug_contract().action == "walk", "Whole-body walk/run reuse retained")
                var speed := actor.run_speed if running else actor.walk_speed
                check(absf(actor.global_position.length() - speed * 2.0) < 1.0, "Actual displacement retains game speed")
        for move_sector in range(8):
            actor.global_position = Vector2.ZERO
            var move := Vector2.from_angle(float(move_sector) * PI / 4.0)
            actor.debug_drive(move, move)
            actor.call("_physics_process", dt)
            for aim_sector in range(8):
                actor.reset_for_battle_preview()
                var aim := Vector2.from_angle(float(aim_sector) * PI / 4.0)
                var target := actor.global_position + aim * 600.0
                actor.set("_pointer_target", target)
                var phase_before: float = runtime.debug_contract().phase
                actor.call("_resolve_pointer_target")
                var shown := runtime.debug_contract()
                check(shown.sector == actor.facing_sector, "Immediate body direction matches latest aim")
                check(is_equal_approx(float(shown.phase), phase_before), "Aim does not reset gait phase")
                var muzzle := runtime.get_authored_muzzle_global_position()
                check(absf((target-muzzle).angle_to(actor.aim_world)) < 0.00001, "Muzzle ray converges before firing")
                var before := projectiles.size()
                check(actor.call("_try_fire", false), "First eligible trigger fires")
                check(projectiles.size() == before + 5 and actor.ammo == 9, "Five pellets consume one round")
                var center := projectiles[before + 2]
                check(center.global_position.distance_to(muzzle) < 0.001 and absf(center.direction.angle_to(actor.aim_world)) < 0.00001, "Center pellet uses exact current muzzle/ray")
                check(is_equal_approx(center.speed,760.0) and is_equal_approx(center.damage,7.0), "Projectile speed/damage unchanged")
                check(not actor.call("_try_fire", false), "Aim response does not bypass .42s cooldown")
                var old_direction := center.direction
                actor.set("_pointer_target", actor.global_position - aim * 600.0)
                actor.call("_resolve_pointer_target")
                check(center.direction == old_direction, "Previously fired pellets do not home")
                for projectile in projectiles:
                    projectile.free()
                projectiles.clear()
        actor.debug_drive(Vector2.ZERO, Vector2.RIGHT)
        actor.call("_physics_process", dt)
        var phase_before: float = runtime.debug_contract().phase
        actor.reset_for_battle_preview()
        actor.debug_fire_once()
        check(runtime.debug_contract().action == "idle" and is_equal_approx(float(runtime.debug_contract().phase), phase_before), "Stationary fire keeps idle feet planted")
        actor.debug_begin_reload()
        check(actor.is_reloading() and not actor.call("_try_fire", false), "Reload blocks firing")
        for tick in range(int(ceil(1.38 / dt)) + 1):
            actor.call("_physics_process", dt)
        check(actor.ammo == 10 and not actor.is_reloading(), "Reload restores actual magazine")
    Engine.physics_ticks_per_second = 60
    var lobby := LOBBY.instantiate()
    root.add_child(lobby)
    var lobby_portrait := lobby.find_child("Portrait_ROOK",true,false) as TextureRect
    var expected := preload("res://scripts/core/battle_texture_library.gd").portrait(profile) as AtlasTexture
    check(lobby_portrait != null and lobby_portrait.texture is AtlasTexture, "Lobby uses the new cropped portrait")
    if lobby_portrait and lobby_portrait.texture is AtlasTexture:
        check(lobby_portrait.texture.get_image().get_data() == expected.get_image().get_data(), "Lobby pixels match the approved current portrait crop")
    var hud := HUD.new()
    root.add_child(hud)
    await process_frame
    await process_frame
    var cards: Array = hud.get("_cards")
    var rook_card: TextureRect = cards[1].portrait
    check(rook_card.texture is AtlasTexture and rook_card.material == null, "Battle portrait uses genuine alpha, no old chroma shader")
    check(rook_card.texture.get_image().get_data() == expected.get_image().get_data(), "Battle and lobby use identical current portrait pixels")
    check(hud.debug_uses_unique_portraits(), "All three battle portraits remain distinct")
    for projectile in projectiles:
        projectile.free()
    actor.queue_free()
    lobby.queue_free()
    hud.queue_free()
    await process_frame
    finish()

func finish() -> void:
    print("ROOK_MOTION_LAB_APP_SMOKE: %s (%d checks, %d failures)" % ["PASS" if failures.is_empty() else "FAIL",checks,failures.size()])
    quit(0 if failures.is_empty() else 1)
