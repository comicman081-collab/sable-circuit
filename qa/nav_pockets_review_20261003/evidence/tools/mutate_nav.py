"""Claude review helper (N-1): variants of Codex's cover_navigation.gd for the "break the rule" step.

usage: mutate_nav.py <variant> <source cover_navigation.gd> <target cover_navigation.gd>

variants
  over     _physics_ground_clear always says "clear"      (a lazy fix: every box-clipping edge becomes walkable)
  nophys   _physics_ground_clear always says "blocked"    (the narrow-phase refinement switched off; escape nodes remain)
  nonodes  the floor-clipped escape node is not kept      (the refinement stays; the new fixed node is gone)
  noswap   the direction swap that makes a cached pair symmetric is removed (a pair may answer differently from either end)
  nomargin the 3 px query margin is 0                     (the narrow phase accepts what the body only just fits)
Each variant is one textual replacement that must match exactly once, else the script stops.
"""
import sys
from pathlib import Path

REPLACE = {
    "over": (
        "static func _physics_ground_clear(actor: Node2D, a: Vector2, b: Vector2) -> bool:\n",
        "static func _physics_ground_clear(actor: Node2D, a: Vector2, b: Vector2) -> bool:\n    return true\n",
    ),
    "nophys": (
        "static func _physics_ground_clear(actor: Node2D, a: Vector2, b: Vector2) -> bool:\n",
        "static func _physics_ground_clear(actor: Node2D, a: Vector2, b: Vector2) -> bool:\n    return false\n",
    ),
    "nonodes": (
        'if floor_field == null or not floor_field.has_method("constrain") or _on_floor(actor,corner): continue',
        "continue",
    ),
    "noswap": (
        "    if b.x < a.x or (b.x == a.x and b.y < a.y):\n        var held := a\n        a = b\n        b = held\n",
        "",
    ),
    "nomargin": (
        "    query.margin = GROUND_MARGIN\n",
        "    query.margin = 0.0\n",
    ),
}


def main():
    variant, source, target = sys.argv[1:4]
    old, new = REPLACE[variant]
    text = Path(source).read_bytes().decode("utf-8")
    text = text.replace("\r\n", "\n")
    count = text.count(old)
    if count != 1:
        sys.exit("variant %s: pattern matches %d times (need exactly 1)" % (variant, count))
    Path(target).write_bytes(text.replace(old, new).encode("utf-8"))
    print("wrote %s -> %s" % (variant, target))


if __name__ == "__main__":
    main()
