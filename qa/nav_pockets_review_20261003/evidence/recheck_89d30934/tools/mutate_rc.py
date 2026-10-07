"""Claude review helper (N-1 re-check of Codex's 89d30934): break the rules on a scratch copy.

usage: mutate_rc.py <kind> <variant> <source file> <target file>

kind prod     variants of scripts/combat/cover_navigation.gd (the production planner)
  over        _physics_ground_clear always says "clear"       (every box-clipping edge becomes walkable)
  nophys      _physics_ground_clear always says "blocked"     (narrow phase off: the old box-only verdict)
  nonodes     the floor-clipped escape node is not kept
  noswap      the endpoint swap that makes a cached pair symmetric is removed
  nomargin    the 3 px query margin is 0
  nowaypoints authored waypoints are no longer graph nodes    (routes get longer or vanish)
kind test_fp  variants of tests/smoke/combat_query_fastpath_smoke.gd
  noexact     the bit-for-bit "fast != ref" test is switched off, so only the new "no longer than the old planner" check remains
kind test_hz  variants of tests/smoke/hazard_expansion_smoke.gd
  noblocker   the real layer-1 body is never added to the scene          (Codex's own counterfactual)
  smallbox    broad-phase rectangle AND body shrink from 1000 to 100 px  (a control smaller than the escape search radius)
Each replacement must match exactly once, else the script stops.
"""
import sys
from pathlib import Path

PROD = {
    "over": [("static func _physics_ground_clear(actor: Node2D, a: Vector2, b: Vector2) -> bool:\n",
              "static func _physics_ground_clear(actor: Node2D, a: Vector2, b: Vector2) -> bool:\n    return true\n")],
    "nophys": [("static func _physics_ground_clear(actor: Node2D, a: Vector2, b: Vector2) -> bool:\n",
                "static func _physics_ground_clear(actor: Node2D, a: Vector2, b: Vector2) -> bool:\n    return false\n")],
    "nonodes": [('if floor_field == null or not floor_field.has_method("constrain") or _on_floor(actor,corner): continue',
                 "continue")],
    "noswap": [("    if b.x < a.x or (b.x == a.x and b.y < a.y):\n        var held := a\n        a = b\n        b = held\n", "")],
    "nomargin": [("    query.margin = GROUND_MARGIN\n", "    query.margin = 0.0\n")],
    "nowaypoints": [("        if _clear_ground(actor,waypoint,waypoint,obstacles): fixed.append(waypoint)\n", "        pass\n")],
}
TEST_FP = {
    "noexact": [("            if fast != ref:\n", "            if false:\n")],
}
TEST_HZ = {
    "noblocker": [("    stage.add_child(blocker)\n", "    pass\n")],
    "smallbox": [
        ("var blocked: Array[Rect2] = [Rect2(hazard.global_position - Vector2(500, 500), Vector2(1000, 1000))]",
         "var blocked: Array[Rect2] = [Rect2(hazard.global_position - Vector2(50, 50), Vector2(100, 100))]"),
        ("    shape.size = Vector2(1000, 1000)\n", "    shape.size = Vector2(100, 100)\n"),
    ],
}
TABLES = {"prod": PROD, "test_fp": TEST_FP, "test_hz": TEST_HZ}


def main():
    kind, variant, source, target = sys.argv[1:5]
    text = Path(source).read_bytes().decode("utf-8").replace("\r\n", "\n")
    for old, new in TABLES[kind][variant]:
        count = text.count(old)
        if count != 1:
            sys.exit("%s/%s: pattern matches %d times (need exactly 1): %r" % (kind, variant, count, old[:80]))
        text = text.replace(old, new)
    Path(target).write_bytes(text.encode("utf-8"))
    print("wrote %s/%s -> %s" % (kind, variant, target))


if __name__ == "__main__":
    main()
