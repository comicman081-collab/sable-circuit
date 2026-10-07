"""Did a web_fps_ab run reach the op 1 field? Decided from its 1920x1080 field screenshot.

The squad cards (bottom left) are drawn only by the field HUD; title, base, briefing and
intro screens show something else there. A run counts as in the field when that region
is within MAX_MAD mean absolute difference (0-255) of a reference field capture.
The earlier rule (field FPS < 90) mistook fast field runs, near the 100 Hz display cap,
for menu runs.

usage: python field_check.py <web_fps_ab.json> <shots_dir> <out.json>   (re-summarise)
"""
from pathlib import Path
import json
import statistics
import sys

from PIL import Image, ImageChops, ImageStat

REFERENCE = Path(__file__).parent / 'field_reference_1080p.png'
REGION = (36, 816, 520, 1056)
MAX_MAD = 12.0


def field_mad(shot: Path) -> float:
    with Image.open(REFERENCE) as ref, Image.open(shot) as img:
        a = ref.convert('RGB').crop(REGION)
        b = img.convert('RGB').crop(REGION)
        return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3.0


def in_field(shot: Path) -> tuple:
    mad = field_mad(shot)
    return mad <= MAX_MAD, round(mad, 2)


def main():
    report = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    shots = Path(sys.argv[2])
    for row in report['runs']:
        if 'error' in row:
            row['valid'] = False
            continue
        shot = shots / f"{row['tag']}_{row['build']}_field.png"
        field, mad = in_field(shot)
        row['fps_rule_valid'] = row['valid']
        row['field_region_mad'] = mad
        row['valid'] = field and row['ready_s'] is not None and row['final_url'].startswith(row['url'])
    summary = {}
    for label in report['builds']:
        rows = [r for r in report['runs'] if r['build'] == label and r.get('valid')]
        summary[label] = {
            'valid_runs': len(rows),
            'title_median': statistics.median([r['title_fps']['fps'] for r in rows]) if rows else None,
            'field10_median': statistics.median([r['field_fps_10s']['fps'] for r in rows]) if rows else None,
            'late6_median': statistics.median([r['field_fps_late_6s']['fps'] for r in rows]) if rows else None,
            'field10_all': [r['field_fps_10s']['fps'] for r in rows],
            'late6_all': [r['field_fps_late_6s']['fps'] for r in rows],
            'field10_p95_ms_all': [r['field_fps_10s']['p95_ms'] for r in rows],
        }
    report['summary'] = summary
    report['validity_rule'] = f'field screenshot region {REGION} within MAD {MAX_MAD} of {REFERENCE.name}; ready and final URL unchanged'
    Path(sys.argv[3]).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    for row in report['runs']:
        print(row['tag'], row['build'], row.get('field_region_mad'), row.get('fps_rule_valid'), '->', row['valid'])
    for label, s in summary.items():
        print(label, s)


if __name__ == '__main__':
    main()
