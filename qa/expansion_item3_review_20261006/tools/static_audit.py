import json, glob, re, subprocess, sys, os
os.environ["GIT_OPTIONAL_LOCKS"] = "0"
def git(*a): return subprocess.run(["git", *a], capture_output=True, text=True, encoding="utf-8").stdout
BASE = "453d20cb"
# a. protected paths and limits touched anywhere in the range
names = git("diff", "--name-only", f"{BASE}..HEAD").split()
prot = [n for n in names if re.match(r"^(assets/|art_src/|motion_lab_v1/|sound/|data/visual/|tests/smoke/site7_boss_)", n)]
print("files changed since", BASE, ":", len(names), "| protected-path hits:", prot or "none")
econ = [n for n in names if "upgrade" in n.lower() or "economy" in n.lower()]
print("economy-related files touched:", econ or "none")
# b. key mapping golden over every enemy id in the ten missions
def old_key(i):
    i = i.upper()
    if "BOSS" in i or "ANCHOR" in i: return "ANCHOR"
    if "ABERRANT" in i or "RAM_01" in i: return "ABERRANT"
    if any(t in i for t in ("RIFLE", "SHIELD", "DRONE", "BULWARK", "MORTAR")): return "SECURITY"
    return ""
NEW = {"BOSS_SITE7_AERATOR_01": "AERATOR", "BOSS_SITE7_CRYO_01": "CRYO", "BOSS_SITE7_GANTRY_01": "GANTRY",
       "BOSS_SITE7_ARCHIVE_01": "ARCHIVE", "BOSS_SITE7_ORIGIN_01": "ORIGIN"}
def new_key(i):
    i = i.upper()
    return NEW.get(i) or old_key(i)
ids = {}
def walk(o, mission):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "enemy_id" and isinstance(v, str): ids.setdefault(v, set()).add(mission)
            else: walk(v, mission)
    elif isinstance(o, list):
        for v in o: walk(v, mission)
for p in sorted(glob.glob("data/missions/MIS_CH01_*.json")):
    walk(json.load(open(p, encoding="utf-8")), os.path.basename(p)[-7:-5])
print("distinct enemy ids in ops 1-10:", len(ids))
diff = []
for i in sorted(ids):
    o, n = old_key(i), new_key(i)
    tag = "" if o == n else "  <-- changed"
    if o != n: diff.append(i)
    print("  %-26s ops %-22s old=%-9s new=%-9s%s" % (i, ",".join(sorted(ids[i])), o or "-", n or "-", tag))
print("changed ids:", diff, "| expected exactly the 5 new bosses:", sorted(diff) == sorted(NEW))
# the "BOSS"-first mutation: if the generic test ran first, every new boss would map to ANCHOR
print("negative control (generic BOSS first) would map:", {i: old_key(i) for i in NEW})
# c. weapon table
rows = json.load(open("data/progression/weapons.json", encoding="utf-8"))
rows = rows.get("weapons", rows) if isinstance(rows, dict) else rows
def dps(r):
    rounds = r["magazine_size"] / r["ammo_per_trigger"]; vol = r["damage"] * r["pellet_count"]
    return vol / r["fire_interval"], vol * rounds / (rounds * r["fire_interval"] + r["reload_duration"])
NEWW = {"WPN_DMR_RAIL_01", "WPN_SHOTGUN_NULL_01"}
best = {}
for r in rows:
    b, s = dps(r)
    if r["weapon_id"] not in NEWW:
        for op in r["compatible_operators"]: best[op] = max(best.get(op, 0), s)
for r in rows:
    b, s = dps(r)
    flag = ""
    if r["weapon_id"] in NEWW:
        ok = b <= 100 and s <= 78 and all(s <= best[op] for op in r["compatible_operators"])
        flag = "  NEW envelope " + ("OK" if ok else "VIOLATED") + " vs best legacy " + str({op: round(best[op], 1) for op in r["compatible_operators"]})
    print("  %-22s burst %5.1f sustained %5.1f flight %4.0f px range %s%s" % (r["weapon_id"], b, s, r["projectile_speed"] * r["projectile_lifetime"], r["engagement_range"], flag))
# d. analyses
an = json.load(open("data/progression/intel_discoveries.json", encoding="utf-8"))["discoveries"]
print("analyses:", len(an), "research sum", sum(a["research_cost"] for a in an), "new rows sum", sum(a["research_cost"] for a in an[3:]), "(headroom 952)")
need = ["analysis_id", "title", "sample_key", "sample_cost", "research_cost", "weakness_id", "module_id", "module_name", "operator_id", "effect_text"]
print("rows missing a required field:", [(a["analysis_id"], [k for k in need if k not in a]) for a in an if any(k not in a for k in need)] or "none")
sink_before, sink_after, income = 5180, 5180 + sum(a["research_cost"] for a in an[3:]), 4088
print("economy: research sink %d -> %d, authored income %d, ratio %.4f (band 0.9-1.5)" % (sink_before, sink_after, income, sink_after / income))
# e. module effects, read from operator_skill_controller.gd (constants copied by hand) against the L-11 caps
MODS = [("MOD_SPORE_FILTER", "duration", 5.0, 6.0), ("MOD_FROST_LENS", "cooldown", 4.0, 3.2), ("MOD_RAIL_SPOOL", "cooldown", 5.0, 4.0),
        ("MOD_RAIL_SPOOL", "distance", 150.0, 200.0), ("MOD_ECHO_RELAY", "duration", 4.0, 6.0), ("MOD_NULL_ANCHOR", "duration", 5.0, 6.5)]
for m, kind, a, b in MODS:
    if kind == "cooldown": ok, shown = (a - b) / a <= 0.25 + 1e-9, "-%.0f%%" % (100 * (a - b) / a)
    elif kind == "duration": ok, shown = b - a <= 2.0 + 1e-9, "+%.1fs" % (b - a)
    else: ok, shown = b - a <= 50.0 + 1e-9, "+%.0fpx" % (b - a)
    print("  %-17s %-9s %5.1f -> %5.1f  %-6s cap %s" % (m, kind, a, b, shown, "OK" if ok else "VIOLATED"))
# f. save fixture provenance
blob = lambda rev: git("rev-parse", rev + ":scripts/core/campaign_progression.gd").strip()
print("campaign_progression.gd blob  381ef0fb:", blob("381ef0fb")[:12], " BASE:", blob(BASE)[:12], " before fixture commit:", blob("4d0a63f2^")[:12])
import hashlib
print("save_v5.json sha256:", hashlib.sha256(open("tests/fixtures/run_contract/save_v5.json", "rb").read()).hexdigest())
fx = json.load(open("tests/fixtures/run_contract/save_v5.json", encoding="utf-8"))
print("save_v5.json: schema", fx.get("schema_version"), "intel keys", sorted(fx.get("intel_samples", {})), "analyses", len(fx.get("discoveries", [])), "weapons", len(fx.get("weapon_catalog", [])))
