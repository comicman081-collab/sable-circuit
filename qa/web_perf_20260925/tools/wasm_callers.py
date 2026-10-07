import sys, json
sys.path.insert(0, sys.argv[3])
from wasm_names import Wasm, import_names
w = Wasm(open(sys.argv[1], 'rb').read()); imap = import_names(open(sys.argv[2], encoding='utf8').read())
want = set(sys.argv[4].split(','))
idx = {i: imap.get(n, n) for i, (m, n) in enumerate(w.imports)}
targets = {i for i, n in idx.items() if n in want}
res = {}
for f in range(w.nimp, w.nimp + len(w.bodies)):
    consts, calls, ind, brt, size = w.decode(f)
    hit = [idx[c] for c in set(calls) if c in targets]
    if hit:
        strs = [s for s in (w.cstr(c) for c in consts) if s]
        fn = [s for s in strs if '.cpp' in s or '.h' in s][:2]
        names = [s for s in strs if s.isidentifier()][:4]
        res[f] = (sorted(set(hit)), fn, names)
for f, (h, fn, names) in res.items(): print(f, h, fn, names)
