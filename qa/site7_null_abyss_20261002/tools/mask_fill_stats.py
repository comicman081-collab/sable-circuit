"""Per plate of one mission: how much of the stored void mask the `void_fill_px` pocket fill made opaque (Claude, 2026-10-02).

    git show e97fb6ac:data/visual/site7_void_masks.json > .cache/null_abyss/void_masks_before.json
    python qa/site7_null_abyss_20261002/tools/mask_fill_stats.py --before=.cache/null_abyss/void_masks_before.json \
        --after=data/visual/site7_void_masks.json --prefix=stage10 --out=qa/site7_null_abyss_20261002/void_mask_fill.json

A mask pixel is void where it reads >= 128 (the masks are kept at VOID_SCALE of the plate). `made_opaque` is void before
and not after, `added` the other way round; the fill may only remove void, so `added` must be 0. Plates of other
missions are compared byte for byte (`other_plates_changed`)."""
import argparse
import base64
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image


def void_of(entry: str) -> np.ndarray:
    return np.asarray(Image.open(io.BytesIO(base64.b64decode(entry))).convert('L')) >= 128


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--before', required=True)
    parser.add_argument('--after', required=True)
    parser.add_argument('--prefix', default='stage10')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    before = json.loads(Path(args.before).read_text(encoding='utf-8'))['plates']
    after = json.loads(Path(args.after).read_text(encoding='utf-8'))['plates']
    assert sorted(before) == sorted(after), 'the plate lists differ'
    rows, total, opaque, added = [], 0, 0, 0
    for asset in sorted(after):
        if '/' + args.prefix + '/' not in asset and not Path(asset).name.startswith('S10_'):
            continue
        b, a = void_of(before[asset]), void_of(after[asset])
        assert b.shape == a.shape
        row = {'asset': asset, 'size': [int(a.shape[1]), int(a.shape[0])], 'void_before': int(b.sum()),
               'void_after': int(a.sum()), 'made_opaque': int((b & ~a).sum()), 'added': int((a & ~b).sum())}
        row['made_opaque_%_of_void'] = round(100.0 * row['made_opaque'] / row['void_before'], 2)
        rows.append(row)
        total += row['void_before']
        opaque += row['made_opaque']
        added += row['added']
    other = [asset for asset in after if asset not in {row['asset'] for row in rows} and before[asset] != after[asset]]
    report = {'plates': rows, 'void_before_total': total, 'made_opaque_total': opaque, 'added_total': added,
              'made_opaque_%_of_void': round(100.0 * opaque / total, 2), 'other_plates_changed': other}
    Path(args.out).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    for row in rows:
        print('%-8s %6.2f %%  (%d of %d, added %d)' % (Path(row['asset']).parent.name, row['made_opaque_%_of_void'],
                                                      row['made_opaque'], row['void_before'], row['added']))
    print('total %d of %d = %.2f %%, added %d, other plates changed: %d' % (opaque, total, report['made_opaque_%_of_void'],
                                                                              added, len(other)))


if __name__ == '__main__':
    main()
