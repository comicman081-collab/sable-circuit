extends SceneTree
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
func _init() -> void: call_deferred("run")
func run() -> void:
    var suggestions: Dictionary = {}
    for number in [2,3]:
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id="MIS_CH01_%02d"%number; stage.battle_preview=true
        root.add_child(stage)
        for _i in range(6): await process_frame; await physics_frame
        var rooms: Dictionary = {}
        for step in [1,3,4]:
            stage.start_battle_preview(step)
            # Inspect spawn positions before movement changes them.
            for entry: Dictionary in stage.get_node("EnvironmentProps").entries: entry.prop.set_active(entry.room_id==stage.main_route[step].id)
            var actor := stage.squad.operators[0]
            var protected: Array[Vector2] = []
            for i in range(3): protected.append(stage.battlefield.squad_spawn(i))
            for i in range((stage.main_route[step].encounter as Array).size()): protected.append(stage.battlefield.enemy_spawn(i))
            var placed: Array[Rect2] = []
            var rows: Array = []
            for entry: Dictionary in stage.get_node("EnvironmentProps").entries: entry.prop.set_active(false)
            for entry: Dictionary in stage.get_node("EnvironmentProps").entries:
                if entry.room_id != stage.main_route[step].id: continue
                var prop: StaticBody2D = entry.prop
                prop.set_active(true)
                var original := prop.global_position
                var rect := Rect2(prop.to_global(prop.ground[0]),Vector2.ZERO)
                for point: Vector2 in prop.ground: rect=rect.expand(prop.to_global(point))
                var best := Vector2.INF
                var best_distance := INF
                for ix in range(20,81,2):
                    for iy in range(28,83,2):
                        var norm := Vector2(ix,iy)/100.0
                        var world: Vector2=stage.battlefield.normalized_to_world(norm)
                        var delta := world-original
                        var candidate := Rect2(rect.position+delta,rect.size)
                        var collision := candidate.grow(26)
                        collision.position.y+=18 # real operator shape center
                        var good := true
                        for spawn in protected:
                            if collision.has_point(spawn): good=false; break
                        if not good: continue
                        for corner: Vector2 in prop.ground:
                            if not stage.battlefield.contains(original+corner+delta): good=false; break
                        if not good: continue
                        for previous in placed:
                            if previous.grow(16).intersects(candidate): good=false; break
                        if good and delta.length_squared()<best_distance:
                            prop.global_position=world
                            var obstacles := NAV.ground_obstacles(actor)
                            var planner := NAV.new()
                            for i in range((stage.main_route[step].encounter as Array).size()):
                                if planner._plan(actor,protected[0],stage.battlefield.enemy_spawn(i),obstacles).is_empty(): good=false; break
                        if good and delta.length_squared()<best_distance:
                            best=norm; best_distance=delta.length_squared()
                if best.is_finite():
                    var delta: Vector2=stage.battlefield.normalized_to_world(best)-original
                    prop.global_position=original+delta
                    placed.append(Rect2(rect.position+delta,rect.size))
                    rows.append({"asset":entry.asset,"point":[best.x,best.y]})
                else:
                    prop.global_position=original; prop.set_active(false)
                    rows.append({"asset":entry.asset,"error":"NO_SAFE_POSITION"})
            rooms[stage.main_route[step].id]=rows
        suggestions[stage.mission_id]=rooms
        stage.queue_free(); await process_frame
        for node in root.get_children():
            if node is PrototypeProjectile: node.queue_free()
    print("PLACEMENT_SUGGESTIONS "+JSON.stringify(suggestions))
    quit()
