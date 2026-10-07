extends SceneTree
## The title's campaign bar draws one segment per authored operation. Its fixed 60 px step
## ran operations 7-10 past the right edge of the 1280 x 720 canvas (the counter read
## "10 / 10" over a bar six segments long); the segments now fit the bar's own box for any
## campaign length. The old layout is the negative control.
const Output := preload("res://tests/support/test_output.gd")
const MissionCatalog := preload("res://scripts/core/site7_campaign.gd")
const CANVAS := Rect2(0, 0, 1280, 720)
const MIN_SEGMENT := 8.0
const MIN_GAP := 2.0
var checks := 0
var failures: Array[String] = []
var evidence: Array = []

func _init() -> void: call_deferred("run")

func settle(count: int) -> void:
    for _i in range(count):
        await process_frame
        await physics_frame

## True when every rect lies inside [0, width], is wide enough to read and leaves a gap to its neighbour.
func fits(rects: Array[Rect2], width: float) -> bool:
    for i in range(rects.size()):
        var rect := rects[i]
        if rect.position.x < 0.0 or rect.end.x > width + 0.01 or rect.size.x < MIN_SEGMENT: return false
        if i > 0 and rect.position.x - rects[i - 1].end.x < MIN_GAP: return false
    return true

func run() -> void:
    root.size = Vector2i(1280, 720)
    # 1. The layout alone, for every campaign length up to twenty operations.
    for count in range(1, 21):
        var rects := TitleScreen.campaign_segments(count, 300.0)
        check(rects.size() == count, "%d operations give %d segments" % [count, rects.size()])
        check(fits(rects, 300.0), "%d operations fit the 300 px box with a readable segment and a gap" % count)
        if count <= 5:
            check(is_equal_approx(rects[0].size.x, 54.0) and (count < 2 or is_equal_approx(rects[1].position.x, 60.0)), "%d operations keep the original 60 px step and 54 px segment" % count)
    # Negative controls: the old fixed step is refused by the same predicate once there are ten operations,
    # and so is a layout that lets a segment touch its neighbour.
    var old: Array[Rect2] = []
    for i in range(10): old.append(Rect2(i * 60.0, 24.0, 54.0, 4.0))
    check(not fits(old, 300.0), "negative control: the old 60 px step with ten operations is refused")
    var touching: Array[Rect2] = [Rect2(0, 24, 30, 4), Rect2(30, 24, 30, 4)]
    check(not fits(touching, 300.0), "negative control: touching segments are refused")
    # 2. The live title with nothing cleared and with every operation cleared.
    var rows := MissionCatalog.rows()
    check(rows.size() >= 10, "the catalog lists at least the ten shipped operations")
    var flow := GameFlow.new()
    flow.persist_campaign = false
    root.add_child(flow)
    await settle(4)
    for stage in ["fresh", "all_cleared"]:
        if stage == "all_cleared":
            for row: Dictionary in rows:
                flow.campaign.commit_mission({"transaction_id": "TITLE-GEOMETRY-" + str(row.mission_id), "mission_id": row.mission_id, "outcome": "EXTRACTED", "full_route_cleared": true})
        flow.show_title()
        await settle(30)
        var widget := flow.current_view.get_node_or_null("CampaignProgress") as Control
        check(widget != null, stage + ": the title carries its campaign bar")
        if widget == null: continue
        var segments: Array[Rect2] = []
        var labels: Array[Rect2] = []
        for child in widget.get_children():
            var absolute := Rect2(widget.position + (child as Control).position, (child as Control).size)
            if child is ColorRect: segments.append(absolute)
            elif child is Label: labels.append(absolute)
        check(segments.size() == rows.size(), "%s: one segment per operation (%d of %d)" % [stage, segments.size(), rows.size()])
        for i in range(segments.size()):
            check(CANVAS.encloses(segments[i]), "%s: segment %d lies inside the 1280 x 720 canvas %s" % [stage, i + 1, str(segments[i])])
            check(segments[i].end.x <= widget.position.x + widget.size.x + 0.01, "%s: segment %d stays inside the bar's own box" % [stage, i + 1])
            if i > 0: check(not segments[i].intersects(segments[i - 1]), "%s: segment %d does not touch segment %d" % [stage, i + 1, i])
        for label_rect in labels:
            check(CANVAS.encloses(label_rect), "%s: bar label %s lies inside the canvas" % [stage, str(label_rect)])
        evidence.append({"stage": stage, "segments": segments.map(func(r: Rect2) -> String: return str(r)), "labels": labels.map(func(r: Rect2) -> String: return str(r))})
    var out := Output.path("res://.cache/tests/title_geometry.json")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var file := FileAccess.open(out, FileAccess.WRITE)
    file.store_string(JSON.stringify({"checks": checks, "operations": rows.size(), "title": evidence, "failures": failures}, "  "))
    file.close()
    flow.queue_free()
    await process_frame
    print("TITLE_GEOMETRY_SMOKE: ", "PASS" if failures.is_empty() else "FAIL", " (", checks, " checks)")
    quit(0 if failures.is_empty() else 1)

func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok:
        failures.append(label)
        push_error(label)
