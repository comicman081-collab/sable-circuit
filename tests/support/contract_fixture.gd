extends RefCounted
## JSON decodes integers as floats. Preserve every key/value while accepting
## that storage-type difference and JSON's float round-trip precision only.
static func equal(a: Variant, b: Variant) -> bool:
    if (a is int or a is float) and (b is int or b is float): return absf(float(a)-float(b)) <= 0.000000001
    if a is Dictionary and b is Dictionary:
        if a.size() != b.size(): return false
        for key in a:
            if not b.has(key) or not equal(a[key], b[key]): return false
        return true
    if a is Array and b is Array:
        if a.size() != b.size(): return false
        for i in range(a.size()):
            if not equal(a[i], b[i]): return false
        return true
    return a == b
