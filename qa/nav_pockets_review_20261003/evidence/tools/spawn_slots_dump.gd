extends SceneTree
## Claude review instrument (N-1 side effects): does the navigation fix move anything the encounter is built from?
## BattleField._build_spawn_points keeps a farthest-point candidate only if BattleField._reaches (CoverNavigation._clear_ground /
## _plan with the first operator as the probe) finds a ground route to the squad. The fix changed _clear_ground, so slots 3+ of a
## room, and the hazards placed away from the first four slots, could move. This dumps, for the three combat rooms of every
## mission, the ten enemy spawn slots, the hostiles as spawned, and the hazards, so two trees can be diffed.
##
## Godot --headless --path <project> -s res://.cache/spawn_slots_dump.gd -- --out=res://.cache/spawn_slots.csv [--missions=1,2]
## CSV rows: kind,mission,room,index_or_id,x,y     kind S = spawn slot, E = hostile at spawn, H = hazard
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const STEPS: Array[int] = [1, 3, 4]
var out := ""
var missions: Array[String] = []
var lines := PackedStringArray()

func _init() -> void:
    call_deferred("_run")

func _frames(count: int) -> void:
    for _i in range(count):
        await physics_frame
        await process_frame

func _run() -> void:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.get_slice("=", 1)
        if arg.begins_with("--missions="):
            for number in arg.get_slice("=", 1).split(","): missions.append("MIS_CH01_%02d" % int(number))
    if missions.is_empty():
        for number in range(1, 11): missions.append("MIS_CH01_%02d" % number)
    for mission_id in missions:
        for step in STEPS: await _room(mission_id, step)
    if out != "":
        DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out).get_base_dir())
        var file := FileAccess.open(out, FileAccess.WRITE)
        if file != null:
            file.store_string("\n".join(lines) + "\n")
            file.close()
    print("SPAWN_SLOTS_DUMP: %d rows" % lines.size())
    quit(0)

func _room(mission_id: String, step: int) -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission_id
    stage.battle_preview = true
    root.add_child(stage)
    await _frames(8)
    stage.start_battle_preview(step)
    await _frames(4)
    var room_id := str(stage.main_route[stage.current_step].id)
    var field: Node = stage.battlefield
    for index in range(10):
        var spot: Vector2 = field.call("enemy_spawn", index)
        lines.append("S,%s,%s,%d,%.1f,%.1f" % [mission_id, room_id, index, spot.x, spot.y])
    var enemies: Array[String] = []
    for node in get_nodes_in_group("m3_enemies"):
        var actor := node as Node2D
        if actor == null: continue
        enemies.append("%s,%s,%s,%s,%.1f,%.1f" % ["E", mission_id, room_id, str(actor.get("enemy_id")), actor.global_position.x, actor.global_position.y])
    enemies.sort()
    lines.append_array(enemies)
    var hazards: Array[String] = []
    for node in stage.find_children("*", "", true, false):
        if node is ZoneHazard:
            var hazard := node as ZoneHazard
            hazards.append("H,%s,%s,%s,%.1f,%.1f" % [mission_id, room_id, hazard.hazard_id, hazard.global_position.x, hazard.global_position.y])
    hazards.sort()
    lines.append_array(hazards)
    print("SPAWN_ROOM %s %s slots=10 hostiles=%d hazards=%d" % [mission_id, room_id, enemies.size(), hazards.size()])
    stage.free()
    await _frames(3)
