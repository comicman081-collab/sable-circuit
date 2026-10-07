extends SceneTree
## Explicit static-position aiming fixture, not traversal or playthrough proof.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
func _init() -> void: call_deferred("run")
func run() -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id="MIS_CH01_03"; stage.battle_preview=true
    root.add_child(stage)
    for i in range(3): await process_frame
    stage.start_battle_preview(1)
    for i in range(3): await process_frame
    stage.set_process(false); stage.squad.set_process(false); stage.squad.set_physics_process(false)
    for op in stage.squad.operators: op.set_physics_process(false)
    var player := stage.squad.get_active_operator()
    var start := player.global_position
    var target: EnemyActor
    for enemy in get_nodes_in_group("m3_enemies"):
        enemy.set_physics_process(false)
        if enemy.enemy_id=="ENM_SITE7_MORTAR_01": target=enemy
    var obstacles := NAV.ground_obstacles(player)
    var planner := NAV.new()
    var rows: Array[Dictionary]=[]
    var count := 0
    var free := 0
    for radius in [100.0,160.0,220.0,280.0,360.0]:
        for index in range(32):
            var point: Vector2=target.global_position+Vector2.from_angle(index*TAU/32.0)*float(radius)
            if not NAV._on_floor(player,point) or not NAV._clear_ground(player,point,point,obstacles): continue
            free+=1
            player.global_position=point
            player.debug_drive(Vector2.ZERO,point.direction_to(target.global_position))
            player._pointer_target=target.get_combat_aim_point(); player._resolve_pointer_target()
            var muzzle := player._get_projectile_spawn_origin()
            var clear := NAV.clear_shot(self,muzzle,target)
            var path := planner._plan(player,start,point,obstacles)
            if clear and not path.is_empty(): count+=1
            var cover := NAV.first_cover(self,muzzle,target.get_combat_aim_point())
            rows.append({"point":point,"muzzle":muzzle,"clear":clear,"reachable":not path.is_empty(),"blocker":cover.name if cover else "","path":path})
    var file := FileAccess.open("res://qa/stage_enemies_20260919/mortar_lane_diagnostic.json",FileAccess.WRITE)
    file.store_string(JSON.stringify({"static_fixture":true,"start":start,"target":target.global_position,"hit_rect":target.get_combat_hit_rect(),"free_points":free,"clear_reachable_points":count,"rows":rows},"  ")); file.close()
    print("MORTAR_LANES free=%d clear_reachable=%d"%[free,count])
    stage.queue_free(); await process_frame; quit(0 if count>0 else 1)
