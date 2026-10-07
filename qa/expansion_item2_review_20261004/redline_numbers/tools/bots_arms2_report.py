"""Claude review helper (REDLINE number study, 2026-10-04): table of bots_arms2.jsonl, one row per cell, plus the earlier session's
three arms (evidence/raw/bots_arms.jsonl of the item 2 review) for comparison.  Counts, not verdicts: a bot is one scripted player,
this PC's load moves its outcomes, and no human play is recorded.
usage (project root): python bots_arms2_report.py <bots_arms2.jsonl> <earlier bots_arms.jsonl> <out.md>"""
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

NEW = [json.loads(l) for l in Path(sys.argv[1]).read_text(encoding='utf-8').splitlines() if l.strip()]
OLD = [json.loads(l) for l in Path(sys.argv[2]).read_text(encoding='utf-8').splitlines() if l.strip()]
LABEL = {
    'P0': ('이전 값 (체력 1.50 / 피해 1.35 / 속도 1.15 / 간격 0.80)', '업그레이드 없음'),
    'M0': ('이후 값 = 결정 (1.35 / 1.25 / 1.12 / 0.85)', '업그레이드 없음'),
    'L0': ('더 약한 탐침 (1.25 / 1.20 / 1.05 / 0.90)', '업그레이드 없음'),
    'P1': ('이전 값 (1.50 / 1.35 / 1.15 / 0.80)', '병기고 6단계 (피해 ×1.48)'),
    'M1': ('이후 값 = 결정 (1.35 / 1.25 / 1.12 / 0.85)', '병기고 6단계 (피해 ×1.48)'),
}
ORDER = ['P0', 'M0', 'L0', 'P1', 'M1']


def ok(r):
    return r.get('outcome') == 'EXTRACTED' and not r.get('failures')


def fmt_list(vals, nd=0):
    return ' / '.join(('%.' + str(nd) + 'f') % v for v in vals) if vals else '-'


by = defaultdict(list)
for r in NEW:
    if 'error' in r:
        continue
    by[r['cell']].append(r)

lines = ['# REDLINE 수치 연구: 작전 1 봇 (2026-10-04)', '',
         '같은 사본(`f2cbe1d6`, 코드는 `b4aa2ae0`과 같다)에서 조합마다 라운드를 돌려 가며 한 번에 하나씩 돌렸다. 봇은 사람이 아니고 이 PC의 부하가 결과를 흔든다. 개수만 적고 판정하지 않는다.', '',
         '| 조합 | 적 배율 | 장비 | 판 수 | 추출 | 걸린 시간 s (추출한 판) | 받은 피해 HP (모든 판) | 전멸한 판 |',
         '|---|---|---|---:|---:|---|---|---|']
for cell in ORDER:
    rs = sorted(by.get(cell, []), key=lambda r: int(r['round']))
    if not rs:
        continue
    good = [r for r in rs if ok(r)]
    bad = [r for r in rs if not ok(r)]
    wipes = '; '.join('라운드 %s: %s, %.0f s, 마지막 방 단계 %s, 보스 남은 체력 %s' % (r['round'], r.get('outcome'), float(r['elapsed']), r.get('last_step'), r.get('boss_hp_left')) for r in bad) or '-'
    lines.append('| %s | %s | %s | %d | **%d** | %s | %s | %s |' % (
        cell, LABEL[cell][0], LABEL[cell][1], len(rs), len(good),
        fmt_list([float(r['elapsed']) for r in good], 0), fmt_list([float(r['damage']) for r in rs], 0), wipes))

lines += ['', '## 방(경로 단계)별 받은 피해 평균 (HP, 추출한 판만)', '', '| 조합 | 단계 1 | 단계 2 | 단계 3 | 단계 4 (보스방) |', '|---|---:|---:|---:|---:|']
for cell in ORDER:
    good = [r for r in by.get(cell, []) if ok(r)]
    if not good:
        continue
    cols = []
    for step in ('1', '2', '3', '4'):
        vals = [float(r['per_step'].get(step, 0)) for r in good]
        cols.append('%.0f' % statistics.mean(vals))
    lines.append('| %s | %s |' % (cell, ' | '.join('%s' % c for c in cols)))

# the earlier session of the item 2 review (same snapshot code), three arms
oby = defaultdict(list)
for r in OLD:
    oby[r['arm']].append(r)
lines += ['', '## 앞선 세션(항목 2 검수 5.3절, 다른 시각)', '', '| 갈래 | 판 수 | 추출 | 받은 피해 HP (모든 판) |', '|---|---:|---:|---|']
NAME = {'neutral': '중립 계약', 'default': '실제 run id의 기본 제안', 'redline': 'REDLINE (이전 값)'}
for arm in ('neutral', 'default', 'redline'):
    rs = sorted(oby.get(arm, []), key=lambda r: int(r['round']))
    lines.append('| %s | %d | **%d** | %s |' % (NAME[arm], len(rs), sum(1 for r in rs if ok(r)), fmt_list([float(r['damage']) for r in rs], 0)))

p0 = by.get('P0', [])
old_red = oby.get('redline', [])
lines += ['', '## 같은 값(이전 REDLINE 값, 업그레이드 없음)을 합치면', '',
          '- 앞선 세션 %d판 중 %d 추출, 이번 세션 %d판 중 %d 추출, 합쳐서 %d판 중 **%d** 추출.' % (
              len(old_red), sum(1 for r in old_red if ok(r)), len(p0), sum(1 for r in p0 if ok(r)),
              len(old_red) + len(p0), sum(1 for r in old_red if ok(r)) + sum(1 for r in p0 if ok(r))),
          '- 같은 값이 두 세션에서 다른 개수를 냈으므로, 이 봇의 추출 개수는 REDLINE 세기를 가르는 눈금으로 쓰지 않는다.']
Path(sys.argv[3]).write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
sys.stdout.buffer.write(('\n'.join(lines) + '\n').encode('utf-8'))
