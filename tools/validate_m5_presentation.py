#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

contracts = {
    "scripts/missions/site7_depth_pass.gd": [
        "class_name Site7DepthPass",
        "_draw_room_depth",
        "Raised top wall face",
    ],
    "scripts/ui/cinematic_field_overlay.gd": [
        "class_name CinematicFieldOverlay",
        "Multi-band vignette",
        "scanlines",
    ],
    "scripts/animation/operator_ground_shadow.gd": [
        "class_name OperatorGroundShadow",
        "actor.controlled",
    ],
    "scripts/animation/enemy_ground_shadow.gd": [
        "class_name EnemyGroundShadow",
        '"DRONE" in actor.enemy_id',
    ],
    "scripts/ui/enemy_overhead_ui.gd": [
        "class_name EnemyOverheadUI",
        "Segmented health fill",
        "phase",
    ],
    "scripts/combat/prototype_projectile.gd": [
        "Precision coil dart",
        "Heavy magnetic pellet",
        "Sensor pulse",
        "Phase lance",
    ],
    "scripts/vfx/combat_hit_vfx.gd": [
        "_base_flash",
        "_draw_aster",
        "_draw_rook",
        "_draw_mica",
        "_draw_anchor",
    ],
    "tests/render/runtime_capture.gd": [
        "19_direction_sector_7.png",
        "24_death_boss.png",
        "Mirror the live wide-echelon formation",
        "RUNTIME_CAPTURE: PASS",
    ],
    "scenes/mission/StoryStage01.tscn": [
        "Site7FacilityArchitecture",
        "site7_depth_pass.gd",
        "cinematic_field_overlay.gd",
    ],
    "scenes/actors/player/OperatorActor.tscn": [
        "operator_ground_shadow.gd",
        "PremiumPresentation",
    ],
    "scenes/actors/enemy/EnemyActor.tscn": [
        "enemy_ground_shadow.gd",
        "enemy_overhead_ui.gd",
    ],
}

errors = []
for rel, needles in contracts.items():
    path = ROOT / rel
    if not path.is_file():
        errors.append(f"missing M5 presentation file: {rel}")
        continue
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            errors.append(f"{rel} missing M5 presentation token: {needle}")

# Deployment remains explicitly out of scope while art/runtime is still in production.
workflow_dir = ROOT / ".github" / "workflows"
if workflow_dir.exists():
    for path in workflow_dir.glob("*.y*ml"):
        lower = path.read_text(encoding="utf-8", errors="replace").lower()
        if "actions/deploy-pages" in lower or "pages: write" in lower or "github-pages" in lower:
            errors.append(f"deployment forbidden during M5 production: {path.relative_to(ROOT)}")

if errors:
    print("M5_PRESENTATION_VALIDATION: FAIL")
    for error in errors:
        print(" -", error)
    sys.exit(1)

print("M5_PRESENTATION_VALIDATION: PASS")
print(f"checked {len(contracts)} M5 production presentation contracts")
