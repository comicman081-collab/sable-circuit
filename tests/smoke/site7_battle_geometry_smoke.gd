extends SceneTree

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const HIT := preload("res://scripts/combat/combat_hit_geometry.gd")
const MOOD := preload("res://scripts/missions/site7_mood.gd")
const ABYSS := preload("res://scripts/missions/site7_abyss_backdrop.gd")
var failed := false
var checks := 0

class TargetFixture extends Node2D:
    var health := 100.0
    func get_combat_hit_rect() -> Rect2:
        return Rect2(global_position + Vector2(-8,-100), Vector2(16,100))
    func apply_damage(amount: float) -> void:
        health -= amount

func _init() -> void:
    call_deferred("run")

func check(value: bool, message: String) -> void:
    checks += 1
    if not value:
        failed = true
        push_error(message)

## Two plate grades within the shared-light threshold (exposure and tint).
func grade_near(a: Vector4, b: Vector4) -> bool:
    return Vector3(a.x-b.x, a.y-b.y, a.z-b.z).length() < 0.05

func frames(count: int = 3) -> void:
    for i in range(count):
        await physics_frame
        await process_frame

## The strongest contact field the abyss shader reads at a world point (every padded plate rectangle that holds it),
## through the shader's own world-to-atlas mapping. `shift` moves every rectangle (a negative control).
func contact_value(shader: ShaderMaterial, atlas: Image, world: Vector2, shift: Vector2 = Vector2.ZERO) -> float:
    var rects: PackedVector4Array = shader.get_shader_parameter("contact_rect")
    var uvs: PackedVector4Array = shader.get_shader_parameter("contact_uv")
    var value := 0.0
    for index in int(shader.get_shader_parameter("contact_count")):
        var q := (world - Vector2(rects[index].x, rects[index].y) - shift) / Vector2(rects[index].z, rects[index].w)
        if q.x < 0.0 or q.y < 0.0 or q.x > 1.0 or q.y > 1.0: continue
        var uv := Vector2(uvs[index].x, uvs[index].y) + q * Vector2(uvs[index].z, uvs[index].w)
        value = maxf(value, atlas.get_pixel(clampi(int(uv.x * atlas.get_width()), 0, atlas.get_width() - 1), clampi(int(uv.y * atlas.get_height()), 0, atlas.get_height() - 1)).r)
    return value

## Up to `count` world points on a plate's opaque pixels along the edge of its see-through void: the void mask is
## opaque there and see-through a few mask pixels away. The contact field is at full strength on such points.
func edge_points(plate: Sprite2D, count: int) -> Array[Vector2]:
    var found: Array[Vector2] = []
    var mask := MOOD.void_mask(str(plate.get_meta("asset","")))
    if mask == null: return found
    var size := plate.texture.get_size()
    var ratio := Vector2(mask.get_size()) / size
    var reach := 5
    for y in range(reach, mask.get_height() - reach, 4):
        for x in range(reach, mask.get_width() - reach, 4):
            if mask.get_pixel(x, y).r > 0.03: continue
            if mask.get_pixel(x + reach, y).r < 0.9 and mask.get_pixel(x - reach, y).r < 0.9 and mask.get_pixel(x, y + reach).r < 0.9 and mask.get_pixel(x, y - reach).r < 0.9: continue
            found.append(plate.global_position + (Vector2(x + 0.5, y + 0.5) / ratio - size * 0.5) * plate.scale)
    var spread: Array[Vector2] = []
    for index in mini(count, found.size()):
        spread.append(found[int(float(index) * float(found.size()) / float(count))])
    return spread

func sweep_tests() -> void:
    for hz in [30,60,120]:
        # Far target enters the group first: order must not override contact.
        var far := TargetFixture.new()
        var near := TargetFixture.new()
        root.add_child(far)
        root.add_child(near)
        far.position = Vector2(70,100)
        near.position = Vector2(25,100)
        far.add_to_group("sweep_fixture")
        near.add_to_group("sweep_fixture")
        var shot := PrototypeProjectile.new()
        root.add_child(shot)
        shot.setup(Vector2(0,45),Vector2.RIGHT,null,Color.WHITE,{},"sweep_fixture")
        shot.set_physics_process(false)
        shot.speed = 2400.0
        shot._physics_process(1.0/float(hz))
        check(near.health < 100.0, "Visible chest missed at %d Hz" % hz)
        check(far.health == 100.0, "Far target won over nearer hit at %d Hz" % hz)
        shot.free()
        near.free()
        far.free()
    var box := Rect2(10,20,30,80)
    check(HIT.hit_point(Vector2(0,60),Vector2(100,60),box).is_equal_approx(Vector2(10,60)),"Swept contact is not at visible body edge")
    check(HIT.hit_point(Vector2(0,0),Vector2(100,0),box) == Vector2.INF,"Shot outside body hit target")
    check(HIT.hit_point(Vector2(20,60),Vector2(100,60),box) == Vector2(20,60),"Inside-body origin skipped hit")

func run() -> void:
    sweep_tests()
    var abyss_styles: Array[String] = []
    var shared_light := {}
    var shared_connector_light := {}
    var plate_uses := {}
    for number in range(1,11):
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = "MIS_CH01_%02d" % number
        stage.battle_preview = true
        root.add_child(stage)
        await frames()
        for step in [1,3,4]:
            stage.start_battle_preview(step)
            for actor in stage.squad.operators: actor.debug_drive(Vector2.ZERO,Vector2.RIGHT)
            for enemy in get_nodes_in_group("m3_enemies"):
                if not enemy.is_queued_for_deletion(): enemy.set_physics_process(false)
            await frames()
            var floor_node := stage.battlefield
            check(stage.has_battle_floor(), "Missing floor S%d encounter%d" % [number,step])
            for actor in stage.squad.operators:
                check(floor_node.call("contains",actor.global_position),"Squad spawned off floor")
                check(actor.get_node("GroundShadow").z_index > stage.get_node("RoomArtLayer").z_index,"Ground shadow hidden under plate")
            for enemy in get_nodes_in_group("m3_enemies"):
                check(floor_node.call("contains",enemy.global_position),"Hostile spawned off floor")
                if "ABERRANT" in enemy.enemy_id:
                    var premium := enemy.get_node("PremiumPresentation") as PremiumEnemyPresentation
                    premium.set("_hit_kick",0.9)
                    for tick in range(120): premium.call("_apply_unique_hit_reaction")
                    var torso: Bone2D = enemy.get("_bones").get("torso")
                    check(absf(torso.rotation) <= 0.24,"Repeated hit feedback rolls a living enemy upside down")
                    premium.set("_hit_kick",0.0)
                    premium.call("_apply_unique_hit_reaction")
                    check(is_zero_approx(torso.rotation),"Enemy hit reaction never returns upright")
            var center: Vector2 = floor_node.get("_center")
            for angle in range(16):
                var outside := center+Vector2.RIGHT.rotated(TAU*float(angle)/16.0)*2000.0
                var result: Vector2 = floor_node.call("constrain",outside)
                check(floor_node.call("contains",result),"Constraint leaves actor outside polygon")
                check(result.distance_to(floor_node.call("constrain",result)) < 0.001,"Floor constraint jitters at rest")
                check(floor_node.call("is_walkable",result),"Constraint keeps a full actor clearance from painted room walls")
            var player := stage.squad.operators[0]
            var runtime := player.get_node("MotionLabCharacterRuntime") as MotionLabCharacterRuntime
            # A prop may deliberately own one diagonal from the visual center.
            # The app contract is that a player has at least one real diagonal
            # lane, not that every input can phase through cover.
            var diagonal_lane := false
            for move in [Vector2(1,1),Vector2(1,-1),Vector2(-1,1),Vector2(-1,-1)]:
                player.position = center
                player.velocity = Vector2.ZERO
                player.debug_drive(move.normalized(),Vector2.RIGHT)
                await frames(8)
                var travel := player.position-center
                if absf(travel.x)>2.0 and absf(travel.y)>2.0:
                    diagonal_lane=true
                    break
            player.debug_drive(Vector2.ZERO,Vector2.RIGHT)
            check(diagonal_lane,"At least one diagonal movement lane remains inside encounter floor")
            player.debug_drive(Vector2.ZERO,Vector2.RIGHT)
            await frames(2)
            var phase := float(runtime.debug_contract().phase)
            await frames(5)
            check(is_equal_approx(phase,float(runtime.debug_contract().phase)),"Stopped actor continues gait phase")
            check(runtime.debug_contract().action == "idle","Stopped actor keeps walking artwork")
            # An encounter never hides the rest of the connected level.
            var art := stage.get_node("RoomArtLayer") as Site7RoomArtLayer
            check(art.debug_streaming_state().visible_ids.size() == 15,"Mission plates were swapped instead of sharing one map")
        var ground := stage.battlefield
        check(bool(ground.get("world_ready")),"Continuous mission ground did not build")
        # Each deck runs into both rooms' painted floors: its doors lie on the
        # shared floor and the deck between them is one unbroken walkable run.
        var doors: Dictionary = ground.get("connector_doors")
        check(doors.size() == 7,"Every authored connector has deck doors")
        for index: int in doors:
            var door_a: Vector2 = doors[index][0]
            var door_b: Vector2 = doors[index][1]
            check(ground.call("segment_walkable",door_a,door_b),"Painted deck has an invisible ground break S%d connector%d" % [number,index])
            check(float(ground.join_gaps.get("%d_a" % index,INF)) < 0.5 and float(ground.join_gaps.get("%d_b" % index,INF)) < 0.5,"Deck misses a room floor S%d connector%d" % [number,index])
        var connector := (stage.get_node("RoomArtLayer") as Site7RoomArtLayer).get_connector_plate(0)
        var floor_sample := connector.global_position + (Vector2(0.72,0.32)-Vector2.ONE*0.5)*connector.texture.get_size()*connector.scale
        var wall_sample := connector.global_position + (Vector2(0.25,0.10)-Vector2.ONE*0.5)*connector.texture.get_size()*connector.scale
        check(ground.call("is_walkable",floor_sample),"Visible diagonal connector deck is blocked")
        check(not ground.call("is_walkable",wall_sample),"Painted connector wall is traversable")
        # Plate borders fade instead of cutting straight: each connector fades its
        # top and bottom off its deck, each room fades all four sides short of its floor.
        var art_layer := stage.get_node("RoomArtLayer") as Site7RoomArtLayer
        for index: int in doors:
            var plate := art_layer.get_connector_plate(index)
            check(plate != null and float(plate.get_meta("cap_fade",0.0)) > 0.0,"Connector border cuts straight S%d connector%d" % [number,index])
            # Each connector takes the seam light that grades it to its rooms'
            # brightness and saturation (site7_seam_light.json).
            var connector_shader := plate.material as ShaderMaterial if plate else null
            check(connector_shader != null and plate.has_meta("seam_light") and connector_shader.get_shader_parameter("seam_light") is Texture2D and float(connector_shader.get_shader_parameter("seam_light_range")) > 0.0,"Connector has no seam light S%d connector%d" % [number,index])
        check(Site7RoomArtLayer.ROOM_EDGE_FADE <= Site7RoomArtLayer.MASK_EDGE_FADE*0.5,"Room border fade reaches walkable floor")
        for room: Dictionary in stage.main_route + stage.optional_rooms:
            var room_plate := art_layer.get_room_plate(str(room.id))
            var plate_shader := room_plate.material as ShaderMaterial if room_plate else null
            check(plate_shader != null and float(plate_shader.get_shader_parameter("cap_width")) > 0.0 and float(plate_shader.get_shader_parameter("edge_width")) > 0.0,"Room plate border cuts straight S%d %s" % [number,str(room.id)])
        # Mood light (site7_mood.json): a mission with a mood row lights every
        # plate, keeps every light that reaches a plate, turns each connector
        # between its rooms' grades and shows the abyss where a plate's void mask
        # makes its outer void see-through; a mission without one is untouched.
        var lit := MOOD.has_mission(stage.mission_id)
        var plates: Array[Sprite2D] = []
        for room: Dictionary in stage.main_route + stage.optional_rooms: plates.append(art_layer.get_room_plate(str(room.id)))
        for index: int in doors: plates.append(art_layer.get_connector_plate(index))
        for plate in plates:
            if plate == null: continue
            var used_asset := str(plate.get_meta("asset", ""))
            if plate_uses.has(used_asset):
                check(false, "Plate %s used by %s and %s" % [used_asset, plate_uses[used_asset], stage.mission_id])
            else:
                plate_uses[used_asset] = stage.mission_id
        var masked := 0
        for plate in plates:
            var plate_shader := plate.material as ShaderMaterial if plate else null
            if plate_shader == null: continue
            var asset := str(plate.get_meta("asset",""))
            check((plate_shader.get_shader_parameter("mood") == true) == lit,"Plate mood light does not follow the mission row S%d %s" % [number,asset])
            if not lit: continue
            check(int(plate.get_meta("mood_lights_dropped",-1)) == 0,"Plate drops lights that reach it S%d %s" % [number,asset])
            check(plate.has_meta("void_mask") == (MOOD.void_mask(asset) != null),"Plate void mask not applied S%d %s" % [number,asset])
            if plate.has_meta("void_mask"): masked += 1
        for index: int in doors:
            var connector_shader := art_layer.get_connector_plate(index).material as ShaderMaterial
            if lit: check((connector_shader.get_shader_parameter("mood_axis") as Vector4) != Vector4.ZERO,"Connector mood has no door axis S%d connector%d" % [number,index])
        if number <= 2: check(masked == 15,"A v2 mission %d plate keeps its black outer void" % number)
        # Each mission's style: its contrast and shadow colour on every plate, and
        # its own abyss style (no two missions share one).
        if lit:
            var style := MOOD.mission_style(stage.mission_id)
            for plate in plates:
                var plate_shader := plate.material as ShaderMaterial if plate else null
                if plate_shader == null: continue
                check((plate_shader.get_shader_parameter("mood_contrast") as Vector2).is_equal_approx(Vector2(float(style.contrast), float(style.pivot))) and (plate_shader.get_shader_parameter("mood_shadow") as Vector4).is_equal_approx(style.shadow),"Plate misses the mission style S%d %s" % [number,str(plate.get_meta("asset",""))])
        # A plate that several missions share keeps its light per mission
        # (the mission row's "plates"), so the same room never looks repeated.
        if lit:
            for room: Dictionary in stage.main_route + stage.optional_rooms:
                var room_asset := str(art_layer.get_room_plate(str(room.id)).get_meta("asset",""))
                var rows: Array = shared_light.get(room_asset, [])
                rows.append({"mission": stage.mission_id, "grade": art_layer.call("_room_grade", str(room.id)),
                        "lights": JSON.stringify([MOOD.plate_lights(room_asset, stage.mission_id), MOOD.plate_fill(room_asset, stage.mission_id)])})
                shared_light[room_asset] = rows
            # A connector turns between its rooms' grades, so one that several
            # missions share must not meet the same grades at both ends.
            for index: int in doors:
                var shared_connector := art_layer.get_connector_plate(index)
                var connector_shader := shared_connector.material as ShaderMaterial
                var connector_asset := str(shared_connector.get_meta("asset",""))
                var rows: Array = shared_connector_light.get(connector_asset, [])
                rows.append({"mission": stage.mission_id, "ends": [connector_shader.get_shader_parameter("mood_room_a"), connector_shader.get_shader_parameter("mood_room_b")]})
                shared_connector_light[connector_asset] = rows
        var abyss := art_layer.get_node_or_null("AbyssBackdrop") as Node2D
        check((abyss != null) == lit,"Abyss backdrop does not follow the mission row S%d" % number)
        if abyss:
            check(int(abyss.get_meta("glows",0)) > 0,"Abyss haze has no plate glows S%d" % number)
            check(abyss.z_index < 0 and abyss.get_index() == 0,"Abyss backdrop draws over a plate S%d" % number)
            var style_name := str(MOOD.abyss(stage.mission_id).get("style", "shaft"))
            check(int((abyss.material as ShaderMaterial).get_shader_parameter("style")) == ABYSS.STYLES.find(style_name) and ABYSS.STYLES.has(style_name),"Abyss style does not follow the mission row S%d" % number)
            check(not abyss_styles.has(style_name),"Abyss style %s repeats in S%d" % [style_name,number])
            abyss_styles.append(style_name)
            # A dawn row's contact field (site7_mood.json "contact_shadow_px", site7_contact_shadows.json) shades the
            # haze beside every plate's silhouette so a dark fringe never stands out against the bright cloud; any other
            # style carries none. The field must lie on its plate: opaque pixels along the void's edge read full strength
            # through the shader's own mapping, and the same read fails once every field is shifted 12 px (control).
            var abyss_shader := abyss.material as ShaderMaterial
            var shaded := style_name == "dawn" and float(MOOD.abyss(stage.mission_id).get("contact_shadow_strength", 0.0)) > 0.0
            var contact_strength: Variant = abyss_shader.get_shader_parameter("contact_strength")
            check(shaded == (contact_strength != null and float(contact_strength) > 0.0),"Abyss contact strength does not follow the mission row S%d" % number)
            var fielded := 0
            for plate in plates:
                if plate != null and not MOOD.contact_shadow(str(plate.get_meta("asset",""))).is_empty(): fielded += 1
            check(int(abyss.get_meta("contact_shadows",0)) == (fielded if shaded else 0),"Abyss contact fields do not follow the plates S%d" % number)
            if shaded:
                check(fielded == plates.size() and fielded <= ABYSS.MAX_CONTACTS,"A dawn plate lacks its contact field S%d" % number)
                var atlas_texture := abyss_shader.get_shader_parameter("contact_atlas") as Texture2D
                var atlas := atlas_texture.get_image() if atlas_texture != null else null
                check(atlas != null and Vector2i(atlas.get_size()) == (abyss.get_meta("contact_atlas_size",Vector2i.ZERO) as Vector2i),"Abyss contact atlas is missing S%d" % number)
                if atlas != null:
                    var missed := 0
                    var shifted_missed := 0
                    var read := 0
                    for plate in plates:
                        if plate == null: continue
                        check(plate.scale.x > 0.0 and plate.scale.y > 0.0,"A mirrored plate cannot carry a contact field S%d %s" % [number,str(plate.get_meta("asset",""))])
                        var points := edge_points(plate,8)
                        check(points.size() >= 4,"Plate has no void edge to read its contact field against S%d %s" % [number,str(plate.get_meta("asset",""))])
                        for point in points:
                            read += 1
                            if contact_value(abyss_shader,atlas,point) < 0.95: missed += 1
                            if contact_value(abyss_shader,atlas,point,Vector2(12,12)) < 0.95: shifted_missed += 1
                    check(missed == 0,"Contact field misses its plate's wall S%d (%d of %d edge points)" % [number,missed,read])
                    check(shifted_missed > 0,"A contact field shifted 12 px still reads full on every edge point S%d" % number)
        for index in [0,2]:
            var actor := stage.squad.operators[index]
            var runtime := actor.get_node("MotionLabCharacterRuntime") as MotionLabCharacterRuntime
            actor.set_physics_process(false)
            # Check every real gait cell at every aim direction. No ray is
            # tested against a different-frame muzzle or against the feet.
            for phase_index in range(6):
                runtime.set("_phase",float(phase_index)/6.0+0.005)
                runtime.set("_moving",true)
                for direction in range(8):
                    var target := actor.global_position+Vector2.RIGHT.rotated(float(direction)*PI/4.0)*600.0
                    var phase_before: float = runtime.get("_phase")
                    var resolved := runtime.resolve_pointer_aim(target)
                    actor.facing_sector = int(resolved.direction)
                    runtime.call("_show_current_frame")
                    var ray := (target-runtime.get_authored_muzzle_global_position()).normalized()
                    check(bool(resolved.converges) and ray.dot(resolved.aim)>0.99999,"Aim ray misses pointer from actual illustrated muzzle")
                    check(is_equal_approx(phase_before,runtime.get("_phase")),"Aim turn resets gait phase")
            var near_target := runtime.resolve_pointer_aim(actor.global_position+Vector2(1,1))
            check(not bool(near_target.converges),"Inside-weapon target falsely reported exact convergence")
            check((near_target.aim as Vector2).is_finite(),"Close pointer creates invalid aim")
        stage.queue_free()
        for node in root.get_children():
            if node is PrototypeProjectile: node.queue_free()
        await frames()
    for room_asset: String in shared_light:
        var rows: Array = shared_light[room_asset]
        for i in range(rows.size()):
            for j in range(i+1, rows.size()):
                var a: Dictionary = rows[i]
                var b: Dictionary = rows[j]
                var grade_a: Vector4 = a.grade
                var grade_b: Vector4 = b.grade
                check(Vector3(grade_a.x-grade_b.x, grade_a.y-grade_b.y, grade_a.z-grade_b.z).length() >= 0.05 and a.lights != b.lights,
                    "Shared plate lit alike in %s and %s: %s" % [a.mission, b.mission, room_asset])
    var connector_pairs := 0
    for connector_asset: String in shared_connector_light:
        var rows: Array = shared_connector_light[connector_asset]
        for i in range(rows.size()):
            for j in range(i+1, rows.size()):
                var a: Dictionary = rows[i]
                var b: Dictionary = rows[j]
                if a.mission == b.mission: continue
                connector_pairs += 1
                var same := (grade_near(a.ends[0], b.ends[0]) and grade_near(a.ends[1], b.ends[1])) or (grade_near(a.ends[0], b.ends[1]) and grade_near(a.ends[1], b.ends[0]))
                check(not same, "Shared connector lit alike in %s and %s: %s" % [a.mission, b.mission, connector_asset])
    check(plate_uses.size() == 150, "Ten missions did not use 150 unique plates")
    print("SITE7_BATTLE_GEOMETRY_SMOKE: %s (%d checks)" % ["FAIL" if failed else "PASS",checks])
    quit(1 if failed else 0)
