"""Claude review instrument (V-33): turn bots_ab.jsonl + the per-run full_operation.json files into the markdown table of the review record.
Usage: python bots_report.py > evidence/bots_ab.md"""
import json, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SNAP = ROOT / '.cache' / 'claude_scratch'
LOG = SNAP / 'item1_review' / 'bots_ab.jsonl'
STEP_NAME = {1: 'R02', 3: 'R04', 4: 'boss'}


def load(row):
    p = SNAP / f"proj_{row['build']}" / '.cache' / 'bot_out' / f"{row['build']}_{row['op']:02d}_{row['pair']}" / 'full_operation.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None


def summarize(row):
    d = load(row)
    s = {'build': row['build'], 'op': row['op'], 'pair': row['pair'], 'wall': row['wall_s'], 'stall': row.get('stall', False),
         'outcome': row.get('outcome') or ('STALL' if row.get('stall') else 'NONE'), 'kills': row.get('hostiles_defeated'), 'dmg': row.get('damage_total'),
         'by_step': {}, 'hazard': {}, 'game_s': None, 'final_hp': None, 'down': None, 'last_step': row.get('steps_reached')}
    if d:
        r = d.get('result') or {}
        s['game_s'] = round(float(r['elapsed_seconds']), 1) if r.get('elapsed_seconds') is not None else None
        tr = d.get('trace') or []
        if tr:
            s['final_hp'] = [round(float(h), 1) for h in tr[-1].get('health', [])]
            s['down'] = sum(1 for h in tr[-1].get('health', []) if float(h) <= 0.0)
        by = {}
        hz = {}
        for key, value in (d.get('damage_by_source') or {}).items():
            step, _op, source = key.split(':', 2)
            by[int(step)] = by.get(int(step), 0.0) + float(value)
            if source.startswith('HAZARD'):
                hz[source] = hz.get(source, 0.0) + float(value)
        s['by_step'] = {STEP_NAME.get(k, str(k)): round(v, 1) for k, v in sorted(by.items())}
        s['hazard'] = {k: round(v, 1) for k, v in hz.items()}
    return s


def main():
    rows = [json.loads(l) for l in LOG.read_text(encoding='utf-8').splitlines() if l.strip()]
    runs = [summarize(r) for r in rows]
    ops = sorted({r['op'] for r in runs})
    out = ['# 봇 짝 비교 (V-33) — 기준선 `7dfe367e` 대 검수 대상 `a6eb1d35`', '',
           '같은 전체 작전 봇(`site7_full_operation_smoke.gd`)을 두 사본에서 라운드마다 순서를 번갈아 직렬로 돌렸다. 두 사본의 봇에는 같은 정지 감지기(연속 300틱 길찾기 영벡터면 `NAV_ZERO_STALL`을 찍고 멈춤)가 들어 있다. 도구: `tools/bots_ab.py`, `tools/bots_report.py`. 봇은 균형 심판이 아니다.', '',
           '| 작전 | 짝 | 사본 | 결과 | 게임 시간 | 처치 | 받은 피해 | 방별 피해 | 장판 피해 | 마지막 체력 | 비고 |', '|---|---|---|---|---:|---:|---:|---|---|---|---|']
    for r in runs:
        note = []
        if r['stall']: note.append('길찾기 정지')
        if r['outcome'] not in ('EXTRACTED',): note.append(f"마지막 방 step {r['last_step']}")
        out.append(f"| {r['op']} | {r['pair']} | {'기준선' if r['build']=='base' else '변경'} | **{r['outcome']}** | {r['game_s'] if r['game_s'] is not None else '-'} | {r['kills'] if r['kills'] is not None else '-'} | {r['dmg'] if r['dmg'] is not None else '-'} | {r['by_step'] or '-'} | {r['hazard'] or '0'} | {r['final_hp'] or '-'} | {', '.join(note)} |")
    out += ['', '### 사본별 요약', '', '| 작전 | 사본 | 판 수 | EXTRACTED | WIPED | 그 밖 | 받은 피해 평균(범위) | 장판 피해 합 |', '|---|---|---:|---:|---:|---:|---|---|']
    for op in ops:
        for build in ('base', 'after'):
            sel = [r for r in runs if r['op'] == op and r['build'] == build]
            if not sel: continue
            ex = sum(1 for r in sel if r['outcome'] == 'EXTRACTED')
            wp = sum(1 for r in sel if r['outcome'] == 'WIPED')
            ot = len(sel) - ex - wp
            dm = [r['dmg'] for r in sel if r['dmg'] is not None]
            hz = {}
            for r in sel:
                for k, v in r['hazard'].items(): hz[k] = round(hz.get(k, 0.0) + v, 1)
            out.append(f"| {op} | {'기준선' if build=='base' else '변경'} | {len(sel)} | {ex} | {wp} | {ot} | {round(statistics.mean(dm), 1) if dm else '-'} ({min(dm) if dm else '-'}–{max(dm) if dm else '-'}) | {hz or '0'} |")
    print('\n'.join(out))


if __name__ == '__main__':
    main()
