extends SceneTree
## Controlled real-physics fixtures, not playthrough evidence. Same app floor,
## spawn, props, collider, tactics and artwork for all ten regular combat rooms
## of the five operations.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const TestOutput := preload("res://tests/support/test_output.gd")
var failures: Array[String]=[]
var rows: Array[Dictionary]=[]
var out := TestOutput.path("res://qa/enemy_cover_repair_20260919/navigation_"+str(Time.get_unix_time_from_system()).replace(".","_"))
func _init() -> void: call_deferred("run")
func settle(n: int) -> void:
    for _i in range(n): await process_frame
func run() -> void:
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    for number in [1,2,3,4,5]:
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id="MIS_CH01_%02d"%number; stage.battle_preview=true
        root.add_child(stage); await settle(8)
        for step in [1,3]:
            stage.start_battle_preview(step)
            # Disable automatic fixture updates BEFORE a combat tick changes spawns.
            stage.set_process(false); stage.set_physics_process(false)
            stage.squad.set_process(false); stage.squad.set_physics_process(false)
            var player := stage.squad.get_active_operator()
            for actor in stage.squad.operators:
                actor.set_process(false); actor.set_physics_process(false)
                if actor!=player: actor.remove_from_group("operators")
            var enemies := get_nodes_in_group("m3_enemies")
            for enemy in enemies: enemy.set_physics_process(false)
            await settle(2)
            # start_battle_preview queues the prior room's actors for disposal.
            enemies=get_nodes_in_group("m3_enemies")
            for index in range(enemies.size()):
                var enemy := enemies[index] as EnemyActor
                if enemy==null or enemy.enemy_id not in ["ENM_SITE7_DRONE_01","ENM_SITE7_BULWARK_01","ENM_SITE7_RAM_01"]: continue
                enemy.global_position=stage.battlefield.enemy_spawn(index)
                player.global_position=stage.battlefield.squad_spawn(0)
                enemy.tactics.state="REPOSITION"; enemy.tactics.state_left=0
                enemy.tactics._flank_goal=Vector2.INF
                var start := enemy.global_position
                var distance := 0.0
                var still := 0.0
                var longest_still := 0.0
                var reached := false
                var ticks := 0
                for tick in range(60*14):
                    await physics_frame
                    var before := enemy.global_position
                    enemy._physics_process(1.0/60.0)
                    var moved := before.distance_to(enemy.global_position)
                    distance+=moved; ticks=tick+1
                    if enemy.tactics.state=="REPOSITION" and moved<0.08: still+=1.0/60.0
                    else: still=0
                    longest_still=maxf(longest_still,still)
                    if enemy.tactics.state=="WINDUP":
                        reached=NAV._clear_ground(enemy,enemy.global_position,player.global_position,NAV.ground_obstacles(enemy)) if enemy.enemy_id=="ENM_SITE7_RAM_01" else NAV.clear_shot(self,enemy.projectile_origin(enemy.tactics.locked_aim),player)
                        break
                var label := "%s room%d %s spawn%d"%[stage.mission_id,step,enemy.enemy_id,index]
                if not reached: failures.append(label+" failed to reach an attack lane")
                if longest_still>0.8: failures.append(label+" navigation stationary %.2fs"%longest_still)
                rows.append({"case":label,"reached_attack_lane":reached,"seconds":ticks/60.0,"path_length":distance,
                    "displacement":start.distance_to(enemy.global_position),"longest_reposition_still_seconds":longest_still,
                    "start":str(start),"end":str(enemy.global_position),"player":str(player.global_position),
                    "player_health":player.health,"downed":player.is_downed(),"state":enemy.tactics.state,"state_left":enemy.tactics.state_left,
                    "flank":str(enemy.tactics._flank_goal),"path":str(enemy.tactics._cover_navigation._path),
                    "obstacles":str(NAV.ground_obstacles(enemy)),"floor":str(stage.battlefield.polygon),
                    "test_path":str(NAV.new()._plan(enemy,enemy.global_position,player.global_position,NAV.ground_obstacles(enemy)))})
            stage.set_process(true); stage.set_physics_process(true)
        stage.queue_free(); await settle(4)
    var hashes: Dictionary={}
    for path in ["scripts/combat/cover_navigation.gd","scripts/combat/site7_enemy_tactics.gd","scripts/animation/site7_machine_sprite.gd","scripts/actors/enemy_actor.gd","data/visual/site7_environment_props.json","data/visual/site7_battle_layouts.json","tests/render/enemy_cover_navigation_regression.gd"]:
        hashes[path]=FileAccess.get_sha256("res://"+path)
    FileAccess.open(out+"/check.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS" if failures.is_empty() else "FAIL","failures":failures,"cases":rows,"physics_hz":60,"sha256":hashes},"  "))
    print("ENEMY_COVER_NAVIGATION ","PASS" if failures.is_empty() else "FAIL"," ",out," ",failures); quit(0 if failures.is_empty() else 1)
