"""Claude review helper (item 3): compare what the OLD code (381ef0fb, schema 5) and the NEW code (HEAD, schema 6) read from the same save.
usage: compare_saves.py <folder with old_<tag>_*.json and new_<tag>_*.json> <tag> [<tag> ...]
Prints one block per save: keys that differ, old-only and new-only keys, and the round-trip flags of each code version."""
import json
import sys
from pathlib import Path

OLD_SAMPLE_KEYS = ["SECURITY", "ABERRANT", "ANCHOR"]
ROW_ID = {"discoveries": "analysis_id", "weapon_catalog": "weapon_id", "missions": "mission_id"}


def load(folder, who, tag, part):
    p = Path(folder) / ("%s_%s_%s.json" % (who, tag, part))
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def rows_by_id(rows, key):
    return {r.get(key): r for r in rows if isinstance(r, dict)}


def main():
    folder = sys.argv[1]
    for tag in sys.argv[2:]:
        old = load(folder, "old", tag, "snapshot1")
        new = load(folder, "new", tag, "snapshot1")
        print("=== %s ===" % tag)
        if old is None or new is None:
            print("  missing dumps (old=%s new=%s)" % (old is not None, new is not None))
            continue
        for who in ("old", "new"):
            s1, s2 = load(folder, who, tag, "snapshot1"), load(folder, who, tag, "snapshot2")
            w1, w2 = load(folder, who, tag, "written1"), load(folder, who, tag, "written2")
            print("  %s code: snapshot after save+reload equal=%s  file stable after a second save=%s  schema in written file=%s  keys=%d"
                  % (who, s1 == s2, w1 == w2, (w1 or {}).get("schema_version"), len(s1)))
        diffs = []
        for key in sorted(set(old) & set(new)):
            if old[key] == new[key]:
                continue
            if key in ROW_ID and isinstance(old[key], list) and isinstance(new[key], list):
                o, n = rows_by_id(old[key], ROW_ID[key]), rows_by_id(new[key], ROW_ID[key])
                changed = [k for k in o if k in n and o[k] != n[k]]
                gone = [k for k in o if k not in n]
                added = [k for k in n if k not in o]
                diffs.append("%s: %d old rows, %d new rows; old rows changed=%s lost=%s; rows added=%s" % (key, len(o), len(n), changed, gone, added))
            elif key == "intel_samples":
                same_old = all(old[key].get(k) == new[key].get(k) for k in OLD_SAMPLE_KEYS)
                extra = {k: v for k, v in new[key].items() if k not in old[key]}
                diffs.append("intel_samples: old three keys equal=%s; extra new keys=%s" % (same_old, extra))
            else:
                diffs.append("%s: old=%s new=%s" % (key, json.dumps(old[key], ensure_ascii=False)[:120], json.dumps(new[key], ensure_ascii=False)[:120]))
        print("  keys with different values (%d):" % len(diffs))
        for d in diffs:
            print("    - " + d)
        print("  old-only keys: %s   new-only keys: %s" % (sorted(set(old) - set(new)), sorted(set(new) - set(old))))


if __name__ == "__main__":
    main()
