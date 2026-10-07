"""Static naming of functions in a stripped Emscripten wasm.

For each function: calls (direct), imported-callee names (from the JS glue import map),
and C strings referenced through i32.const addresses in active data segments.
"""
import sys, re, json, struct
def uleb(b, i):
    r = s = 0
    while True:
        x = b[i]; i += 1; r |= (x & 0x7f) << s; s += 7
        if x < 0x80: return r, i
def sleb(b, i, bits=64):
    r = s = 0
    while True:
        x = b[i]; i += 1; r |= (x & 0x7f) << s; s += 7
        if x < 0x80:
            if x & 0x40: r -= 1 << s
            return r, i
def name(b, i):
    n, i = uleb(b, i); return b[i:i+n].decode('utf8', 'replace'), i + n

class Wasm:
    def __init__(self, b):
        self.b = b; i = 8; self.secs = {}
        while i < len(b):
            sid = b[i]; i += 1; size, i = uleb(b, i); self.secs.setdefault(sid, []).append((i, size)); i += size
        self.imports = []
        off, size = self.secs[2][0]; n, j = uleb(b, off)
        for _ in range(n):
            m, j = name(b, j); f, j = name(b, j); kind = b[j]; j += 1
            if kind == 0: _, j = uleb(b, j); self.imports.append((m, f))
            elif kind == 1: j += 1; fl, j = uleb(b, j); _, j = uleb(b, j); j = uleb(b, j)[1] if fl & 1 else j
            elif kind == 2: fl, j = uleb(b, j); _, j = uleb(b, j); j = uleb(b, j)[1] if fl & 1 else j
            elif kind == 3: j += 2
            elif kind == 4: j += 1; _, j = uleb(b, j)
        self.nimp = len(self.imports)
        self.bodies = []
        off, size = self.secs[10][0]; n, j = uleb(b, off)
        for _ in range(n):
            sz, j = uleb(b, j); self.bodies.append((j, sz)); j += sz
        self.mem = {}
        self.segs = []
        off, size = self.secs[11][0]; n, j = uleb(b, off)
        for _ in range(n):
            flag, j = uleb(b, j)
            if flag == 1:
                ln, j = uleb(b, j); j += ln; continue
            if flag == 2: _, j = uleb(b, j)
            assert b[j] == 0x41; addr, j = sleb(b, j + 1); assert b[j] == 0x0b; j += 1
            ln, j = uleb(b, j); self.segs.append((addr, j, ln)); j += ln
    def cstr(self, addr):
        for base, off, ln in self.segs:
            if base <= addr < base + ln:
                k = off + (addr - base); end = self.b.find(b'\0', k, off + ln)
                if end < 0 or end - k < 3 or end - k > 200: return None
                s = self.b[k:end]
                if all(32 <= c < 127 or c in (9, 10) for c in s): return s.decode()
                return None
        return None
    def decode(self, fidx):
        b = self.b; start, size = self.bodies[fidx - self.nimp]; i = start; end = start + size
        nloc, i = uleb(b, i)
        for _ in range(nloc): _, i = uleb(b, i); i += 1
        consts = []; calls = []; indirect = 0; brtab = 0
        while i < end:
            op = b[i]; i += 1
            if op in (0x02, 0x03, 0x04, 0x06): _, i = sleb(b, i)
            elif op in (0x0c, 0x0d, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x07, 0x08, 0x09, 0x18, 0xd2): _, i = uleb(b, i)
            elif op == 0x0e:
                n, i = uleb(b, i); brtab = max(brtab, n)
                for _ in range(n + 1): _, i = uleb(b, i)
            elif op in (0x10, 0x12): f, i = uleb(b, i); calls.append(f)
            elif op in (0x11, 0x13): _, i = uleb(b, i); _, i = uleb(b, i); indirect += 1
            elif op == 0x1c:
                n, i = uleb(b, i); i += n
            elif 0x28 <= op <= 0x3e: _, i = uleb(b, i); _, i = uleb(b, i)
            elif op in (0x3f, 0x40): _, i = uleb(b, i)
            elif op == 0x41: v, i = sleb(b, i); consts.append(v & 0xffffffff)
            elif op == 0x42: _, i = sleb(b, i)
            elif op == 0x43: i += 4
            elif op == 0x44: i += 8
            elif op == 0xd0: i += 1
            elif op == 0xfc:
                sub, i = uleb(b, i)
                if sub in (8, 12, 14): _, i = uleb(b, i); _, i = uleb(b, i)
                elif sub == 10: _, i = uleb(b, i); _, i = uleb(b, i)
                elif sub in (9, 11, 13, 15, 16, 17): _, i = uleb(b, i)
            elif op == 0xfd:
                sub, i = uleb(b, i)
                if sub <= 11 or sub in (92, 93): _, i = uleb(b, i); _, i = uleb(b, i)
                elif 84 <= sub <= 91: _, i = uleb(b, i); _, i = uleb(b, i); i += 1
                elif sub in (12, 13): i += 16
                elif 21 <= sub <= 34: i += 1
            elif op in (0x00, 0x01, 0x05, 0x0b, 0x0f, 0x1a, 0x1b, 0xd1, 0x19) or 0x45 <= op <= 0xc4: pass
            else: raise ValueError(f'op {op:#x} at {i-1-start} in f{fidx}')
        assert i == end and b[end - 1] == 0x0b, (fidx, i, end)
        return consts, calls, indirect, brtab, size

def import_names(js):
    # var wasmImports={a:___assert_fail,b:_glGetIntegerv,...}
    m = re.search(r'wasmImports\s*=\s*\{([^}]*)\}', js)
    out = {}
    for pair in m.group(1).split(','):
        k, _, v = pair.partition(':'); out[k.strip()] = v.strip()
    return out

if __name__ == '__main__':
    wasm = Wasm(open(sys.argv[1], 'rb').read()); js = open(sys.argv[2], encoding='utf8').read()
    imap = import_names(js)
    targets = [int(x) for x in sys.argv[3].split(',')]
    def fname(f):
        if f < wasm.nimp: m, n = wasm.imports[f]; return 'import:' + imap.get(n, n)
        return f'f{f}'
    for t in targets:
        consts, calls, ind, brtab, size = wasm.decode(t)
        strs = []
        for c in consts:
            s = wasm.cstr(c)
            if s and s not in strs: strs.append(s)
        callees = []
        for c in calls:
            n = fname(c)
            if n not in callees: callees.append(n)
        print(f'== f{t} size={size} indirect_calls={ind} max_br_table={brtab}')
        print('   strings:', strs[:25])
        print('   callees:', callees[:40])
