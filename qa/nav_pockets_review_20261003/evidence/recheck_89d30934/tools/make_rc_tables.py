"""Claude review helper (N-1 re-check): turn rc_matrix.jsonl into the Markdown tables of the record.
usage: make_rc_tables.py <rc_matrix.jsonl> <out .md>      (run from the project root)"""
import json
import sys
from pathlib import Path

rows = {}
for line in Path(sys.argv[1]).read_text(encoding='utf-8').splitlines():
    if line.strip():
        r = json.loads(line)
        rows[r['tag']] = r

DESC = {
    'over': '땅 검사의 물리 확인이 항상 "통과" (덮개를 뚫고 가는 길이 열림)',
    'nophys': '물리 확인이 항상 "막힘" (상자만 보는 옛 판정으로 돌아감)',
    'nonodes': '바닥에 걸린 모서리의 탈출 노드를 버림',
    'noswap': '끝점 정렬(A→B와 B→A의 답을 같게) 삭제',
    'nomargin': '3 px 여유를 0 px로',
    'nowaypoints': '저작된 경유점이 길 노드가 되지 않음 (길이 길어지거나 사라짐)',
    'revert': '수정 이전 파일로 되돌림 (`753cf029`의 `cover_navigation.gd`와 `site7_enemy_tactics.gd`)',
}


def verdict(r):
    return '**잡았다**' if r['exit'] != '0' else '통과(못 잡음)'


def counts(r):
    res = r['result']
    if 'FAIL' in res:
        return res.split(': ', 1)[1]
    return res.split(': ', 1)[1] if ': ' in res else res


out = []
out.append('#### B-3 `combat_query_fastpath` — 운영 코드를 부수고 시험을 돌린 결과 (새 사본에서, 한 번에 하나)')
out.append('')
out.append('기준 셋: 정상 사본 3회는 모두 `PASS (34 checks)`. 아래 "정확 비교 끔" 열은 시험 사본에서 `fast != ref` 한 줄만 꺼서 *새로 생긴 "새 길 ≤ 옛 길" 검사 단독*의 민감도를 본 것이다.')
out.append('')
out.append('| 부순 곳 | 설명 | 시험 그대로 | 정확 비교 끔(새 검사 단독) |')
out.append('|---|---|---|---|')
for v in ('over', 'nophys', 'nonodes', 'noswap', 'nomargin', 'nowaypoints', 'revert'):
    a, b = rows['fp_' + v], rows['fpx_' + v]
    out.append('| `%s` | %s | %s — %s | %s — %s |' % (v, DESC[v], verdict(a), counts(a), verdict(b), counts(b)))
out.append('')
out.append('읽는 법: "정확 비교 끔" 열에서 `over`·`nophys`·`nomargin`·`revert`가 안 잡히는 것은 맞다. 이들은 길을 *더 길게* 만들지 않으므로 "새 길 ≤ 옛 길" 검사 단독으로는 볼 수 없고, 정확 비교(왼쪽 열)가 잡는다. 길이 검사가 맡는 것은 `nowaypoints`처럼 길이 길어지거나 사라지는 고장이다.')
out.append('')
out.append('#### B-4 `hazard_expansion` — 시험과 운영 코드를 부수고 돌린 결과')
out.append('')
out.append('기준 셋: 정상 사본 3회는 모두 `PASS (438 checks, 15 rooms)`.')
out.append('')
out.append('| 부순 곳 | 설명 | 결과 | 실패한 "막힌 탈출 거절" 검사 |')
out.append('|---|---|---|---|')
out.append('| 시험: `noblocker` | Codex가 세운 실제 몸체를 씬에 넣지 않음 | %s | %s |' % (verdict(rows['hz_noblocker']), rows['hz_noblocker']['negative_control_fails']))
for v in ('over', 'nophys', 'nonodes', 'noswap', 'nomargin', 'nowaypoints', 'revert'):
    r = rows['hz_' + v]
    out.append('| 운영: `%s` | %s | %s | %s |' % (v, DESC[v], verdict(r), r['negative_control_fails']))
out.append('| 시험: `smallbox` | 상자와 몸체를 1000→100 px로 줄임 (몸체 있음) | 통과 (기대대로: 몸체가 있으면 28곳 모두 거절) | %s |' % rows['hz_smallbox']['negative_control_fails'])
out.append('| 시험: `smallbox`+`noblocker` | 같은 100 px 상자, 몸체 없음 | %s | %s |' % (verdict(rows['hz_smallbox_noblocker']), rows['hz_smallbox_noblocker']['negative_control_fails']))
text = '\n'.join(out) + '\n'
Path(sys.argv[2]).write_text(text, encoding='utf-8', newline='\n')
print(text)
