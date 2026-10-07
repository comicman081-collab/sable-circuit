extends SceneTree
## Dense-encounter contract: authored rooms field more simultaneous hostiles
## than the former three, while only MAX_CONCURRENT_ATTACKERS robots commit a
## warning/shot/charge at once, same-type robots fan out (alternating orbit),
## and mobile robots do not stack into one silhouette. Isolated live fixture:
## operator health is raised so the window measures enemy discipline only; this
## is not playthrough, balance or visual approval.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const TACTICS := preload("res://scripts/combat/site7_enemy_tactics.gd")
const DEFAULT_OUT := "res://qa/combat_density_20260924/density_contract.json"
var checks := 0
var failures: Array[String] = []
var report := {"missions": {}, "fixture": {}}

func _init() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok:
        failures.append(label)
        push_error(label)

func run() -> void:
    # 1. Authored peak simultaneous hostiles per combat room.
    for index in range(1, 11):
        var mission_id := "MIS_CH01_%02d" % index
        var mission: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/missions/%s.json" % mission_id))
        var total := 0
        var rooms := {}
        for room: Dictionary in mission.main_route:
            var first: Array = room.get("encounter", [])
            if first.is_empty(): continue
            var waves: Array = [first]
            waves.append_array(room.get("reinforcements", []))
            var reinforce_at := int(room.get("reinforce_at", 0))
            var peak := first.size()
            for wave_index in range(1, waves.size()):
                peak = maxi(peak, reinforce_at + (waves[wave_index] as Array).size())
            for wave: Array in waves: total += wave.size()
            rooms[room.id] = {"type": room.type, "waves": waves.size(), "peak_simultaneous": peak, "reinforce_at": reinforce_at}
            if room.type in ["COMBAT", "ELITE"]:
                check(peak >= 5, "%s %s fields at least five hostiles at once (%d)" % [mission_id, room.id, peak])
            check(waves.size() >= 2 and reinforce_at >= 1, "%s %s has a live reinforcement wave" % [mission_id, room.id])
        report.missions[mission_id] = {"hostiles": total, "rooms": rooms}
        check(total >= 18, "%s fields at least eighteen hostiles (%d)" % [mission_id, total])
    # 2. Live fixture: the game's own wave spawner, full physics.
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = "MIS_CH01_02"
    root.add_child(stage)
    stage.configure_campaign({}, "COMBAT-DENSITY-FIXTURE", {})
    for i in range(3): await physics_frame
    for member in stage.squad.operators:
        member.max_health = 5000.0
        member.health = 5000.0
    var room: Dictionary = stage.main_route[1]
    # The first combat room opens on its own; add its reinforcement at once.
    for i in range(30):
        await physics_frame
        if stage.enemies_alive > 0: break
    check(stage.enemies_alive >= 4, "First combat room opened through the game trigger (%d)" % stage.enemies_alive)
    stage._wave_index = 1
    stage._spawn_wave(room)
    await physics_frame
    var enemies: Array[EnemyActor] = []
    var signs := {}
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor:
            enemies.append(node)
            signs[node.enemy_id + str(node._orbit_sign)] = true
    check(enemies.size() >= 7, "Seven hostiles on the floor at once (%d)" % enemies.size())
    var drones_cw := 0
    var drones_ccw := 0
    for enemy in enemies:
        if enemy.enemy_id == "ENM_SITE7_DRONE_01":
            if enemy._orbit_sign > 0.0: drones_cw += 1
            else: drones_ccw += 1
    check(drones_cw > 0 and drones_ccw > 0, "Same-type drones orbit in both directions (%d/%d)" % [drones_cw, drones_ccw])
    var max_attackers := 0
    var frames_with_two := 0
    var near_pairs := 0
    var pair_samples := 0
    var serial_before := 0
    for enemy in enemies: serial_before += int(enemy.tactics.attack_serial)
    for frame in range(60 * 14):
        await physics_frame
        var attackers := 0
        var mobile: Array[EnemyActor] = []
        for node in get_nodes_in_group("m3_enemies"):
            if not node is EnemyActor or node.health <= 0.0: continue
            if node.tactics.state in ["WINDUP", "BURST", "LUNGE"]: attackers += 1
            if str(TACTICS.ROLES.get(node.enemy_id, "")) in ["drone", "skimmer", "shield", "melee"]: mobile.append(node)
        max_attackers = maxi(max_attackers, attackers)
        if attackers >= 2: frames_with_two += 1
        if frame >= 180 and frame % 10 == 0:
            for a in range(mobile.size()):
                for b in range(a + 1, mobile.size()):
                    pair_samples += 1
                    if mobile[a].global_position.distance_to(mobile[b].global_position) < 48.0: near_pairs += 1
    var attacks := -serial_before
    for enemy in enemies:
        if is_instance_valid(enemy): attacks += int(enemy.tactics.attack_serial)
    var stacked_ratio := float(near_pairs) / maxf(1.0, float(pair_samples))
    check(max_attackers <= TACTICS.MAX_CONCURRENT_ATTACKERS, "At most %d robots commit an attack at once (%d)" % [TACTICS.MAX_CONCURRENT_ATTACKERS, max_attackers])
    check(frames_with_two > 0, "Tokens are shared, not starved: several robots attack together")
    check(attacks >= 8, "Dense room keeps up real pressure (%d attacks in 14 s)" % attacks)
    check(stacked_ratio < 0.05, "Mobile robots rarely overlap (%.3f of pair samples under 48 px)" % stacked_ratio)
    report.fixture = {"mission": "MIS_CH01_02", "room": room.id, "hostiles": enemies.size(), "max_concurrent_attackers": max_attackers,
        "frames_with_two_or_more_attackers": frames_with_two, "attacks_started": attacks, "stacked_pair_ratio": stacked_ratio,
        "drone_orbit_split": [drones_cw, drones_ccw], "operator_health_raised_for_fixture": true}
    stage.queue_free()
    await process_frame
    report["checks"] = checks
    report["failures"] = failures
    report["status"] = "PASS" if failures.is_empty() else "FAIL"
    report["recorded_utc"] = Time.get_datetime_string_from_system(true)
    var out := DEFAULT_OUT
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.trim_prefix("--out=")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var file := FileAccess.open(out, FileAccess.WRITE)
    file.store_string(JSON.stringify(report, "  "))
    file.close()
    print("COMBAT_DENSITY_SMOKE %s (%d checks) %s" % [report.status, checks, JSON.stringify(report.fixture)])
    for failure in failures: print(" - " + failure)
    quit(0 if failures.is_empty() else 1)
