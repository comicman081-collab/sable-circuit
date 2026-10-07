import sys, zipfile, io
def leb(b, i):
    r = s = 0
    while True:
        x = b[i]; i += 1
        r |= (x & 0x7f) << s; s += 7
        if x < 0x80: return r, i
def sections(b):
    assert b[:4] == b'\0asm'
    i = 8; out = []
    while i < len(b):
        sid = b[i]; i += 1
        size, i = leb(b, i)
        name = None
        if sid == 0:
            n, j = leb(b, i); name = b[j:j+n].decode('utf8', 'replace')
        out.append((sid, size, name)); i += size
    return out
for p in sys.argv[1:]:
    if p.endswith('.zip'):
        z = zipfile.ZipFile(p)
        for n in z.namelist():
            if n.endswith('.wasm'):
                b = z.read(n)
                print(p, n, len(b), [(s, sz, nm) for s, sz, nm in sections(b) if s == 0])
    else:
        b = open(p, 'rb').read()
        print(p, len(b), [(s, sz, nm) for s, sz, nm in sections(b) if s == 0])
