extends SceneTree

const GAME_FLOW := preload("res://scenes/bootstrap/GameFlow.tscn")

var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var flow := GAME_FLOW.instantiate() as GameFlow
    root.add_child(flow)
    await process_frame
    flow.debug_open_aster_static_pre_gate_preview()
    await process_frame
    await process_frame
    _check(flow.current_state == "QA_ASTER_STATIC_PRE_GATE", "GameFlow reaches isolated ASTER pre-gate preview")
    var preview := flow.current_view as AsterStaticPreGatePreview
    _check(preview != null, "pre-gate scene instantiates")
    if preview != null:
        var contract := preview.debug_contract()
        _check(bool(contract.get("pre_gate", false)), "pre-gate status is explicit")
        _check(bool(contract.get("nonpromoted", false)), "preview is nonpromoted")
        _check(bool(contract.get("static_preview", false)), "preview is static only")
        _check(not bool(contract.get("animation_or_skeleton_connected", true)), "no animation or skeleton is connected")
        _check(bool(contract.get("uses_mask_derived_rgba", false)), "mask-derived RGBA texture is loaded")
    if failures.is_empty():
        print("ASTER_STATIC_PRE_GATE_PREVIEW_SMOKE: PASS")
        quit(0)
        return
    print("ASTER_STATIC_PRE_GATE_PREVIEW_SMOKE: FAIL")
    for failure in failures:
        print(" - " + failure)
    quit(1)

func _check(condition: bool, label: String) -> void:
    if condition:
        print("PASS: " + label)
    else:
        failures.append(label)
        push_error("FAIL: " + label)
