extends SceneTree
## Claude review helper (item 2): drive the REAL GameFlow for all ten operations, look at the briefing the way a player does
## and follow each choice into the stage.  Everything is project-local (persist_campaign = false), nothing touches user://.
##   - every briefing: choice count (3, or 4 once the operation is cleared), all visible controls, overlaps, 1280x720, text fit
##   - every choice: deploy through the briefing's own signal, compare the stage's contract with the one that was displayed,
##     spawn the first combat room and the boss room, check HP / damage / speed / interval of each robot against the contract,
##     read the extraction reward
##   - negative paths: deploy_mission() with an index the briefing never offers
## usage: flow_audit.gd -- --out=res://.cache/out/flow_audit.json [--native=1 to keep the text-fit numbers meaningful]
const Flow := preload("res://scenes/bootstrap/GameFlow.tscn")
var rows: Array = []
var geo: Array = []
var failures: Array[String] = []
var checks := 0
var out := "res://.cache/out/flow_audit.json"
var only := 0

func _init() -> void: call_deferred("run")

func frames(n: int) -> void:
    for _i in range(n): await process_frame

func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok:
        failures.append(label)
        print("FAIL: ", label)

func canon(v: Variant) -> String: return JSON.stringify(v, "", true)

func _prepare(flow: GameFlow, n: int, cleared_self: bool) -> void:
    flow.campaign.debug_reset()
    for k in range(1, n + (1 if cleared_self else 0)):
        var r := flow.campaign.commit_mission({"transaction_id": "AUDIT-%02d-%s" % [k, str(cleared_self)], "mission_id": "MIS_CH01_%02d" % k,
            "outcome": "EXTRACTED", "full_route_cleared": true})
        if not bool(r.get("committed", false)): print("PREPARE FAILED for ", k, " ", r)
    flow.enter_base()

func _rects_overlap(a: Control, b: Control) -> bool:
    if a.is_ancestor_of(b) or b.is_ancestor_of(a): return false
    return a.get_global_rect().intersects(b.get_global_rect())

func _collect(node: Node, list: Array) -> void:
    for c in node.get_children():
        if c is Control and (c as Control).is_visible_in_tree():
            list.append(c)
        _collect(c, list)

func geometry(screen: Control, tag: String) -> void:
    var list: Array = []
    _collect(screen, list)
    var buttons: Array = []
    var info: Array = []
    for c: Control in list:
        var r := c.get_global_rect()
        var row := {"name": str(c.name), "class": c.get_class(), "rect": [r.position.x, r.position.y, r.size.x, r.size.y]}
        if c is Button or c is Label:
            var text := str(c.get("text"))
            if text != "":
                var msz := c.get_combined_minimum_size()
                row["text"] = text.substr(0, 60)
                row["min"] = [msz.x, msz.y]
                row["fits"] = msz.x <= c.size.x + 0.5 and msz.y <= c.size.y + 0.5
                if c is Button:
                    var font := c.get_theme_font("font")
                    var fs := c.get_theme_font_size("font_size")
                    var ts := font.get_multiline_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs)
                    var sb: StyleBox = c.get_theme_stylebox("normal")
                    var inner := c.size - sb.get_minimum_size()
                    row["text_extent"] = [ts.x, ts.y]
                    row["inner"] = [inner.x, inner.y]
                    row["text_fits_inner"] = ts.x <= inner.x + 0.5 and ts.y <= inner.y + 0.5
                    buttons.append(c)
        if not Rect2(0, 0, 1280, 720).encloses(r) and r.size.x < 1279:
            row["outside_1280x720"] = true
        info.append(row)
    var overlaps: Array = []
    for i in range(buttons.size()):
        for j in range(i + 1, buttons.size()):
            if _rects_overlap(buttons[i], buttons[j]): overlaps.append([str(buttons[i].name), str(buttons[j].name)])
    # a button against the big panels it is not a child of
    var panels: Array = []
    for c: Control in list:
        if c is Panel and c.size.x > 300 and c.size.y > 150: panels.append(c)
    for b: Control in buttons:
        for p: Control in panels:
            if _rects_overlap(b, p): overlaps.append([str(b.name), str(p.name)])
    for i in range(panels.size()):
        for j in range(i + 1, panels.size()):
            if _rects_overlap(panels[i], panels[j]): overlaps.append([str(panels[i].name), str(panels[j].name)])
    geo.append({"tag": tag, "controls": info, "overlaps": overlaps})
    check(overlaps.is_empty(), tag + " no overlap between visible buttons/panels: " + str(overlaps))
    for row in info:
        if row.has("outside_1280x720"): check(false, tag + " " + str(row.name) + " outside 1280x720")
        if row.has("fits") and not bool(row.fits): check(false, tag + " " + str(row.name) + " text minimum larger than its rectangle")
        if row.has("text_fits_inner") and not bool(row.text_fits_inner): check(false, tag + " " + str(row.name) + " drawn text larger than the button's inner rectangle")

func _freeze_and_read(stage: StoryStage01, step: int, contract: Dictionary, tag: String, redline: bool) -> Array:
    var ids := stage.debug_spawn_encounter_for_step(step)
    await frames(2)
    var result: Array = []
    var room: Dictionary = stage.main_route[step]
    var idx := 0
    for node in get_nodes_in_group("m3_enemies"):
        if not (node is EnemyActor): continue
        var e := node as EnemyActor
        e.set_physics_process(false)
        var authored_row: Dictionary = (room.encounter as Array)[idx] if idx < (room.encounter as Array).size() else {}
        idx += 1
        var boss := e.enemy_id.begins_with("BOSS_")
        var authored := float(authored_row.get("health", 0.0))
        var want_hp := authored * float(contract.enemy_health_multiplier)
        # an elite affix may add a barrier but not HP; hatchlings are not part of the authored rows
        check(str(authored_row.get("enemy_id", "")) == e.enemy_id and authored > 0.0 and is_equal_approx(e.max_health, want_hp),
            "%s %s HP authored %.1f x %.3f = %.1f, actual %.1f" % [tag, e.enemy_id, authored, float(contract.enemy_health_multiplier), want_hp, e.max_health])
        if str(authored_row.get("affix", "")) == "":
            check(is_equal_approx(e.run_damage_multiplier, float(contract.enemy_damage_multiplier)), tag + " " + e.enemy_id + " damage multiplier")
        var want_speed := 1.0 if (redline and boss) else float(contract.enemy_speed_multiplier)
        var want_interval := 1.0 if (redline and boss) else float(contract.enemy_attack_interval_multiplier)
        # an elite affix multiplies on top (EliteAffix.apply); compare against the base only when the row has no affix
        if str(authored_row.get("affix", "")) == "":
            check(is_equal_approx(e.run_speed_multiplier, want_speed), "%s %s speed factor %.3f (want %.3f)" % [tag, e.enemy_id, e.run_speed_multiplier, want_speed])
            check(is_equal_approx(e.run_attack_interval_multiplier, want_interval), "%s %s interval factor %.3f (want %.3f)" % [tag, e.enemy_id, e.run_attack_interval_multiplier, want_interval])
        result.append({"enemy": e.enemy_id, "affix": str(authored_row.get("affix", "")), "authored_hp": authored, "hp": e.max_health, "damage": e.run_damage_multiplier,
            "speed": e.run_speed_multiplier, "interval": e.run_attack_interval_multiplier, "boss": boss})
        e.queue_free()
    await frames(2)
    return result

func run() -> void:
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    for a in OS.get_cmdline_user_args():
        if a.begins_with("--out="): out = a.trim_prefix("--out=")
        if a.begins_with("--only="): only = int(a.trim_prefix("--only="))
    var flow := Flow.instantiate() as GameFlow
    flow.persist_campaign = false
    root.add_child(flow)
    await frames(3)
    for n in range(1, 11):
        if only != 0 and n != only: continue
        var id := "MIS_CH01_%02d" % n
        for cleared_self in [false, true]:
            _prepare(flow, n, cleared_self)
            await frames(3)
            var indices: Array = [0, 1, 2] if not cleared_self else [3]
            for i in indices:
                flow.open_mission_briefing(id)
                await frames(3)
                var screen := flow.current_view as BriefingScreen
                if screen == null:
                    check(false, "%s briefing opened" % id); continue
                var want_count := 4 if cleared_self else 3
                check(screen._contracts.size() == want_count, "%s (%s) briefing shows %d choices, got %d" % [id, "cleared" if cleared_self else "new", want_count, screen._contracts.size()])
                screen.debug_complete_briefing()
                await frames(3)
                if i == indices[0]: geometry(screen, "%s %s" % [id, "cleared" if cleared_self else "new"])
                screen._select_contract(i)
                var shown := screen.selected_contract()
                var shown_run_id := screen.contract_run_id
                var serial_before := flow.campaign.run_serial
                var effect := RunContract.effect_text(shown)
                screen.debug_deploy()
                await frames(4)
                var stage := flow.current_view as StoryStage01
                if stage == null:
                    check(false, "%s choice %d reaches a stage" % [id, i]); continue
                check(flow.campaign.run_serial == serial_before + 1, "%s choice %d consumed exactly one run serial at deploy" % [id, i])
                check(stage._run_id == shown_run_id, "%s choice %d: stage run id %s equals the briefing's %s" % [id, i, stage._run_id, shown_run_id])
                var got := stage.debug_run_contract()
                check(canon(got) == canon(shown), "%s choice %d: stage contract equals the displayed one" % [id, i])
                var is_red := RunContract.is_redline(got)
                check(is_red == (i == 3), "%s choice %d REDLINE flag %s" % [id, i, str(is_red)])
                var tag := "%s c%d" % [id, i]
                var first := await _freeze_and_read(stage, 1, got, tag + " room1", is_red)
                var boss_step := -1
                for s in range(stage.main_route.size()):
                    if str((stage.main_route[s] as Dictionary).get("type", "")) == "BOSS": boss_step = s
                var bossrows: Array = []
                if boss_step >= 0: bossrows = await _freeze_and_read(stage, boss_step, got, tag + " boss", is_red)
                check(boss_step >= 0 and bossrows.size() >= 1, tag + " has a boss room with a boss")
                stage.debug_seed_cargo(100, 40, 10, 10, true, 6)
                var summary := stage.debug_extraction_summary("R06_EXTRACT")
                var rw := {"research": int(summary.secured_research), "salvage": int(summary.secured_salvage), "fragments": int(summary.secured_fragments)}
                var want_r := 140.0 * float(got.research_reward_multiplier)
                var want_s := 10.0 * float(got.salvage_reward_multiplier)
                var want_f := 10.0 * float(got.fragment_reward_multiplier)
                check(absf(rw.research - want_r) <= 1.0 and absf(rw.salvage - want_s) <= 1.0 and absf(rw.fragments - want_f) <= 1.0,
                    "%s rewards %s vs 140/10/10 x (%.3f, %.3f, %.3f)" % [tag, str(rw), float(got.research_reward_multiplier), float(got.salvage_reward_multiplier), float(got.fragment_reward_multiplier)])
                check(canon(summary.run_contract) == canon(got), tag + " the extraction summary keeps the chosen contract")
                rows.append({"mission": id, "choice": i, "cleared_before": cleared_self, "identity": RunContract.identity(got), "run_id": stage._run_id,
                    "effect_text": effect, "first_room": first, "boss": bossrows, "rewards": rw})
                flow.enter_base()
                await frames(4)
    # indices the briefing never offers: the deploy must fall back to the untouched default
    _prepare(flow, 1, false)
    await frames(3)
    for bad in [3, 4, 9, -1, 100]:
        var serial := flow.campaign.run_serial
        flow.deploy_mission("MIS_CH01_01", bad)
        await frames(4)
        var st := flow.current_view as StoryStage01
        if st == null: check(false, "bad index %d reaches a stage" % bad); continue
        check(canon(st.debug_run_contract()) == canon(RunContract.build(st._run_id)), "deploy_mission(op1 not cleared, index %d) falls back to the default contract, got %s" % [bad, RunContract.identity(st.debug_run_contract())])
        rows.append({"mission": "MIS_CH01_01", "bad_index": bad, "identity": RunContract.identity(st.debug_run_contract())})
        flow.enter_base()
        await frames(4)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var f := FileAccess.open(out, FileAccess.WRITE)
    f.store_string(JSON.stringify({"checks": checks, "failures": failures, "rows": rows, "geometry": geo, "native": DisplayServer.get_name() != "headless"}, "  ", true)); f.close()
    print("FLOW_AUDIT: ", "PASS" if failures.is_empty() else "FAIL", " (", checks, " checks, ", failures.size(), " failing)")
    quit(0 if failures.is_empty() else 1)
