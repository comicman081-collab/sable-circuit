"""Claude review helper (item 3 review of Codex's 98292b3d plus my polish 0a14d5b6): break the new rules on a scratch snapshot, one at a time.

usage: mutate_i3.py list                       print every mutant and the tests it is run against
       mutate_i3.py check [root]               every pattern must match exactly once in the files under root (default: the main tree)
       mutate_i3.py apply <snapshot> <name>    restore the pristine files, then apply the mutant (exactly-once replacements)
       mutate_i3.py restore <snapshot>         restore the pristine files

A mutant is  name: (description, tests, [(file, old, new), ...]).  Every `old` must match exactly once, else the script stops.
Tests (letters): i intel_supply  m module_expansion  w weapon_expansion  l lab_geometry  s contract_save  p m10_persistence
                 g m13_migration  e upgrade_economy  b m10_base_ui  n m10_intel (full-only)  o m13_loadout (full-only)
                 c campaign (full-only)  t lab_capture_geometry (full-only)  h hit_hurt_vfx  q m13_campaign  r m13_runtime
"""
import shutil
import sys
from pathlib import Path

IS = "scripts/core/intel_samples.gd"
CP = "scripts/core/campaign_progression.gd"
SS = "scripts/missions/story_stage_01.gd"
OA = "scripts/actors/operator_actor.gd"
SK = "scripts/combat/operator_skill_controller.gd"
MR = "scripts/ui/mission_results.gd"
BL = "scripts/ui/base_lobby.gd"
CAP = "tests/render/expansion_item3_capture.gd"
WJ = "data/progression/weapons.json"
DJ = "data/progression/intel_discoveries.json"
FILES = [IS, CP, SS, OA, SK, MR, BL, CAP, WJ, DJ]

ECHO = '"research_cost": 200,\n      "weakness_id": "ARCHIVE_ECHO_MODEL"'


def research(value: int):
    return [(DJ, ECHO, ECHO.replace("200", str(value)))]


M = {
    # ---- sample keys ----------------------------------------------------------------------------------
    "key_generic_boss_first": ("enemy_key tests the generic BOSS branch before the five new bosses (all five become ANCHOR)", "inc", [(IS,
        '    var id := enemy_id.to_upper()\n    if id == "BOSS_SITE7_AERATOR_01": return "AERATOR"\n',
        '    var id := enemy_id.to_upper()\n    if "BOSS" in id: return "ANCHOR"\n    if id == "BOSS_SITE7_AERATOR_01": return "AERATOR"\n')]),
    "key_old_chain": ("enemy_key is the old three-key chain again (no new-boss lines)", "inc", [(IS,
        '    if id == "BOSS_SITE7_AERATOR_01": return "AERATOR"\n    elif id == "BOSS_SITE7_CRYO_01": return "CRYO"\n    elif id == "BOSS_SITE7_GANTRY_01": return "GANTRY"\n'
        '    elif id == "BOSS_SITE7_ARCHIVE_01": return "ARCHIVE"\n    elif id == "BOSS_SITE7_ORIGIN_01": return "ORIGIN"\n    elif "BOSS" in id or "ANCHOR" in id: return "ANCHOR"\n',
        '    if "BOSS" in id or "ANCHOR" in id: return "ANCHOR"\n')]),
    "lost_three_keys": ("lost_intel_samples sums only the three old keys", "inc", [(SS,
        '"lost_intel_samples": 0 if not wiped else IntelSamples.total(_cargo_intel),',
        '"lost_intel_samples": 0 if not wiped else int(_cargo_intel.get("SECURITY",0))+int(_cargo_intel.get("ABERRANT",0))+int(_cargo_intel.get("ANCHOR",0)),')]),
    "intel_keys_campaign_three": ("CampaignProgression.INTEL_KEYS is the three old keys (commit drops the new samples)", "ipsgnc", [(CP,
        "const INTEL_KEYS := IntelSamples.KEYS\n", 'const INTEL_KEYS := ["SECURITY", "ABERRANT", "ANCHOR"]\n')]),
    "intel_keys_stage_three": ("StoryStage01.INTEL_KEYS is the three old keys (extraction secures only three)", "inc", [(SS,
        "const INTEL_KEYS := IntelSamples.KEYS\n", 'const INTEL_KEYS := ["SECURITY", "ABERRANT", "ANCHOR"]\n')]),
    "sanitize_three_keys": ("_sanitize_intel reads only the three old keys (new samples dropped on commit and load)", "ipsgn", [(CP,
        "func _sanitize_intel(value:Variant)->Dictionary:\n    return IntelSamples.sanitize(value)\n",
        'func _sanitize_intel(value:Variant)->Dictionary:\n    var out:Dictionary=IntelSamples.empty()\n    for key in ["SECURITY","ABERRANT","ANCHOR"]: out[key]=maxi(0,int(value.get(key,0))) if value is Dictionary else 0\n    return out\n')]),
    "secured_skips_origin": ("extraction leaves the ORIGIN sample out of secured_intel", "inc", [(SS,
        "        for key in INTEL_KEYS: secured_intel[key] = int(_cargo_intel.get(key,0))\n",
        '        for key in INTEL_KEYS:\n            if key != "ORIGIN": secured_intel[key] = int(_cargo_intel.get(key,0))\n')]),
    # ---- weapons ----------------------------------------------------------------------------------------
    "weapon_hit_profile_not_overridden": ("_weapon_art_profile overrides only the projectile family, not hit_vfx_profile", "whqr", [(OA,
        'for key in ["projectile_profile", "hit_vfx_profile"]:', 'for key in ["projectile_profile"]:')]),
    "rail_damage_40": ("RAIL CARBINE damage 40 instead of 22 (burst 105, sustained above 78)", "woqe", [(WJ,
        '"damage":22.0,"projectile_speed":1320.0', '"damage":40.0,"projectile_speed":1320.0')]),
    "rail_unlock_removed": ("the ANL_GANTRY_RAIL_MODEL -> RAIL CARBINE unlock rule is deleted", "wog", [(CP,
        '    if _analyzed_intel.has("ANL_GANTRY_RAIL_MODEL"): _append_unique(_unlocked_weapons,"WPN_DMR_RAIL_01")\n', "")]),
    "null_unlock_removed": ("the ANL_ORIGIN_NULL_MODEL -> NULL BREACHER unlock rule is deleted", "wog", [(CP,
        '    if _analyzed_intel.has("ANL_ORIGIN_NULL_MODEL"): _append_unique(_unlocked_weapons,"WPN_SHOTGUN_NULL_01")\n', "")]),
    # ---- economy: sink 6,080 of income 4,088 = 1.4873x, band top 6,132 (= +52) ----------------------------
    "research_plus_52": ("new research costs +52 (6,132 = exactly 1.5x: boundary, expected to PASS)", "en", research(252)),
    "research_plus_53": ("new research costs +53 (6,133 = 1.5002x: expected to FAIL)", "en", research(253)),
    "research_plus_60": ("new research costs +60 (6,140 = 1.502x)", "en", research(260)),
    # ---- the six module hooks ---------------------------------------------------------------------------
    "mod_frost_lens_off": ("FROST LENS hook never fires", "mn", [(SK, 'actor.has_module("MOD_FROST_LENS"): return 3.2', "false: return 3.2")]),
    "mod_rail_spool_cooldown_off": ("RAIL SPOOL cooldown hook never fires", "mn", [(SK, 'actor.has_module("MOD_RAIL_SPOOL"): return 4.0', "false: return 4.0")]),
    "mod_rail_spool_distance_off": ("RAIL SPOOL distance hook never fires", "mn", [(SK,
        'return 200.0 if actor and actor.has_module("MOD_RAIL_SPOOL") else 150.0', "return 150.0")]),
    "mod_spore_filter_off": ("SPORE FILTER hook never fires", "mn", [(SK, 'return 6.0 if actor and actor.has_module("MOD_SPORE_FILTER") else 5.0', "return 5.0")]),
    "mod_echo_relay_off": ("ECHO RELAY hook never fires", "mn", [(SK, 'return 6.0 if actor and actor.has_module("MOD_ECHO_RELAY") else 4.0', "return 4.0")]),
    "mod_null_anchor_off": ("NULL ANCHOR hook never fires", "mn", [(SK, 'return 6.5 if actor and actor.has_module("MOD_NULL_ANCHOR") else 5.0', "return 5.0")]),
    # ---- my polish (0a14d5b6): do its own checks bite? ------------------------------------------------------
    "results_rail_old_position": ("T-1: the COMMAND rail is back at y 404, 88 px (touches the INTEL line)", "l", [(MR,
        "comms_bar.position = Vector2(34, 416); comms_bar.size = Vector2(3, 82)", "comms_bar.position = Vector2(34, 404); comms_bar.size = Vector2(3, 88)")]),
    "lab_effect_font_9": ("T-3: analysis effect text capped at 9 px (fits, but below the 10 px floor)", "l", [(BL,
        "_fit_lab_label(effect,10,Vector2(306,38))", "_fit_lab_label(effect,9,Vector2(306,38))")]),
    "lab_status_overlap": ("the lab status label is moved onto the heading", "lb", [(BL,
        "_m10_status_label.position=Vector2(824,14)", "_m10_status_label.position=Vector2(400,14)")]),
    "cache_ignores_weapon_change": ("T-4: the cached shot profile is not rebuilt when the weapon row changes", "w", [(OA,
        " or not is_same(_shot_profile_spec, weapon_spec):", ":")]),
    "cache_ignores_art_replace": ("T-4: the cached shot profile is not rebuilt when the operator profile is replaced", "w", [(OA,
        " or not is_same(_shot_profile_art, art_profile)", "")]),
    "per_shot_copy_restored": ("T-4 undone: a fresh deep copy for every shot (the old behaviour, same values)", "w", [(OA,
        "    if _shot_profile.is_empty() or not is_same(_shot_profile_art, art_profile) or not is_same(_shot_profile_spec, weapon_spec):\n", "    if true:\n")]),
    "capture_wait_1s": ("T-8: the results capture waits 1.0 s again (count-up unfinished; only the native 1080p capture can catch it, run by hand)", "", [(CAP,
        "await create_timer(2.0).timeout", "await create_timer(1.0).timeout")]),
}


def pristine_dir(snapshot: Path) -> Path:
    return snapshot / ".cache" / "i3_pristine"


def restore(snapshot: Path) -> None:
    pd = pristine_dir(snapshot)
    pd.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        saved = pd / f.replace("/", "__")
        if not saved.exists():
            shutil.copyfile(snapshot / f, saved)
        else:
            shutil.copyfile(saved, snapshot / f)


def patch_text(name: str, f: str, text: str, rows) -> str:
    for old, new in rows:
        n = text.count(old)
        if n != 1:
            sys.exit("%s: pattern in %s matches %d times (need 1): %r" % (name, f, n, old[:90]))
        text = text.replace(old, new)
    return text


def by_file(patches):
    out = {}
    for f, old, new in patches:
        out.setdefault(f, []).append((old, new))
    return out


def apply(snapshot: Path, name: str) -> None:
    restore(snapshot)
    for f, rows in by_file(M[name][2]).items():
        target = snapshot / f
        text = target.read_bytes().decode("utf-8").replace("\r\n", "\n")
        target.write_bytes(patch_text(name, f, text, rows).encode("utf-8"))
    print("applied %s: %s" % (name, M[name][0]))


def check(root: Path) -> None:
    for name, (_d, _t, patches) in M.items():
        for f, rows in by_file(patches).items():
            text = (root / f).read_bytes().decode("utf-8").replace("\r\n", "\n")
            patch_text(name, f, text, rows)
    print("all %d mutants: every pattern matches exactly once under %s" % (len(M), root))


def main() -> None:
    cmd = sys.argv[1]
    if cmd == "list":
        for k, (d, t, _p) in M.items():
            print("%-34s tests=%-7s %s" % (k, t, d))
        print(len(M), "mutants")
    elif cmd == "check":
        check(Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parents[3])
    elif cmd == "apply":
        apply(Path(sys.argv[2]), sys.argv[3])
    elif cmd == "restore":
        restore(Path(sys.argv[2]))
        print("restored")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
