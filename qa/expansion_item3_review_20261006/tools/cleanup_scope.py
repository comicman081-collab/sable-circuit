import json
BS = chr(92)
m = json.load(open('qa/expansion_item3_20261006/records/cleanup_manifest.json', encoding='utf-8'))
print(type(m).__name__, list(m.keys())[:14] if isinstance(m, dict) else len(m))
rows = []
if isinstance(m, dict):
    for k in ('files', 'deleted', 'rows', 'entries', 'removed'):
        if k in m and isinstance(m[k], list):
            rows = m[k]; break
print("rows:", len(rows))
roots = {}
tot = 0
for r in rows:
    p = r.get('path') if isinstance(r, dict) else str(r)
    sz = (r.get('bytes') or r.get('size') or 0) if isinstance(r, dict) else 0
    tot += int(sz)
    parts = p.replace(BS, '/').split('/')
    key = '/'.join(parts[:4])
    roots[key] = roots.get(key, 0) + 1
for k, v in sorted(roots.items()):
    print("%4d  %s" % (v, k))
print("bytes total:", tot, "=", round(tot / 1048576, 1), "MiB")
if isinstance(m, dict):
    for k in m:
        if k not in ('files', 'deleted', 'rows', 'entries', 'removed'):
            print(k, ":", str(m[k])[:240])
