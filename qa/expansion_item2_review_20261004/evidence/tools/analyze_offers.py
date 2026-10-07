"""Claude review helper (item 2): read the offers dumps and measure K-02 / K-03 / K-09 independently of Codex's smoke.

usage: analyze_offers.py <offers_a.json> <offers_b.json> <build_old.json> <build_new.json> <out.md>
  offers_a / offers_b  two dumps of the same ids from two separate Godot processes (determinism across processes)
  build_old / build_new  RunContract.build() of the 7b26a152 archive and of the item-2 snapshot (K-01: byte-identical)
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

a = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
b = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
old = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
new = json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
out = []

# ---- K-01: build() unchanged --------------------------------------------------------------------------------------------
same = sum(1 for k in old if old[k] == new.get(k))
out.append("## K-01 `build()` 바이트 비교 (7b26a152 압축본 대 e091e25f)")
out.append("")
out.append("run id %d개, 같은 JSON 문자열 %d개, 다른 것 %d개." % (len(old), same, len(old) - same))
diffs = [k for k in old if old[k] != new.get(k)]
if diffs:
    out.append("다른 id 예: " + ", ".join(diffs[:5]))
out.append("")

# ---- determinism across processes ------------------------------------------------------------------------------------------
out.append("## K-02 두 프로세스의 `offers()` 비교")
out.append("")
out.append("두 번의 별도 Godot 실행에서 같은 id %d개 × 작전 10개 × 제안 3개: %s" % (len(a), "완전히 같다" if a == b else "다르다"))
out.append("")

# ---- structure ----------------------------------------------------------------------------------------------------------------
n_cells = 0
bad_first = bad_pairs = bad_clamp = bad_rr = same_opp = bad_size = 0
slot_hazards = [Counter(), Counter(), Counter()]
reward_gap = []        # (max - min) of the research reward across the three offers
risk_set = Counter()
pair_ct = Counter()
opp_ct = Counter()
mission_variants = defaultdict(set)
KEYS = ["research_reward_multiplier", "salvage_reward_multiplier", "fragment_reward_multiplier"]
for rid, per in a.items():
    for m, offers in per.items():
        if m == "REDLINE":
            continue
        n_cells += 1
        if len(offers) != 3:
            bad_size += 1
            continue
        first = json.loads(old[rid]) if rid in old else None
        if first is None or offers[0] != first:
            # offers[0] must equal build(rid) exactly
            bad_first += 1
        pairs = {(o["hazard_id"], o["opportunity_id"]) for o in offers}
        if len(pairs) != 3:
            bad_pairs += 1
        if len({o["opportunity_id"] for o in offers}) == 1:
            same_opp += 1
        for s, o in enumerate(offers):
            slot_hazards[s][o["hazard_id"]] += 1
            risk_set[(o["hazard_id"], o["risk_score"])] += 1
            for k in ("enemy_health_multiplier", "enemy_damage_multiplier"):
                if not (0.5 <= o[k] <= 3.0):
                    bad_clamp += 1
            for k in ("enemy_speed_multiplier", "enemy_attack_interval_multiplier"):
                if not (0.5 <= o[k] <= 2.0):
                    bad_clamp += 1
            for k in KEYS:
                if not (0.5 <= o[k] <= 4.0):
                    bad_clamp += 1
        opp_ct[offers[0]["opportunity_id"]] += 1
        for x in offers:
            for y in offers:
                if x["risk_score"] > y["risk_score"]:
                    for k in KEYS:
                        if x[k] < y[k] - 1e-9:
                            bad_rr += 1
        r = [o["research_reward_multiplier"] for o in offers]
        reward_gap.append(max(r) - min(r))
        pair_ct[tuple(sorted((o["hazard_id"]) for o in offers))] += 1
        mission_variants[rid].add(tuple(o["hazard_id"] for o in offers))

out.append("## K-02 / K-03 구조 측정 (run id %d개 × 작전 10개 = 칸 %d개)" % (len(a), n_cells))
out.append("")
out.append("| 검사 | 어긋난 칸 |")
out.append("|---|---|")
out.append("| 제안이 3개가 아닌 칸 | %d |" % bad_size)
out.append("| 첫 제안이 `build(run id)`와 다른 칸 | %d |" % bad_first)
out.append("| (위험, 기회) 쌍이 3개로 구별되지 않는 칸 | %d |" % bad_pairs)
out.append("| 클램프 밖의 값 | %d |" % bad_clamp)
out.append("| 위험이 높은데 보상이 낮은 쌍(자원 3종 각각) | %d |" % bad_rr)
out.append("")
out.append("- **세 제안의 기회 카드가 모두 같은 칸:** %d / %d (제안은 위험 카드만 바꾸고 기회 카드는 바꾸지 않는다)" % (same_opp, n_cells))
out.append("- 제안 사이의 연구 보상 차이(최대 − 최소): 최소 %.3f, 최대 %.3f, 평균 %.3f" % (min(reward_gap), max(reward_gap), sum(reward_gap) / len(reward_gap)))
out.append("")
out.append("위험 카드가 나오는 자리별 횟수 (0 = 기본 제안, 1·2 = 대안)")
out.append("")
hz = sorted({h for c in slot_hazards for h in c})
out.append("| 위험 카드 | 위험도 | 0번(기본) | 1번 | 2번 |")
out.append("|---|---|---|---|---|")
for h in hz:
    rs = sorted({r for (hh, r) in risk_set if hh == h})
    out.append("| %s | %s | %d | %d | %d |" % (h, "/".join(map(str, rs)), slot_hazards[0][h], slot_hazards[1][h], slot_hazards[2][h]))
out.append("")
out.append("한 run id에서 작전을 바꾸면 대안 둘이 바뀌는 정도: 작전 10개 중 서로 다른 (기본, 대안1, 대안2) 순서쌍의 개수 = 평균 %.2f" % (sum(len(v) for v in mission_variants.values()) / len(mission_variants)))
out.append("")
out.append("한 제안 세트에 들어간 위험 카드 조합(순서 무시)")
out.append("")
for combo, c in pair_ct.most_common():
    out.append("- %s: %d칸" % (" + ".join(combo), c))
out.append("")

# ---- every offer carries its own card's numbers (a gap no Codex test guards: mutant offers_no_hazard_stats) ---------------------------------
STAT = ("enemy_health_multiplier", "enemy_damage_multiplier", "enemy_speed_multiplier", "enemy_attack_interval_multiplier")
by_h = defaultdict(Counter)
by_h_build = defaultdict(Counter)
by_ho = defaultdict(set)
by_ho_build = defaultdict(set)
for rid, per in a.items():
    for m, offers in per.items():
        if m == "REDLINE":
            continue
        for o in offers:
            by_h[o["hazard_id"]][tuple(round(o[k], 6) for k in STAT)] += 1
            by_ho[(o["hazard_id"], o["opportunity_id"])].add(tuple(round(o[k], 6) for k in KEYS))
for rid, js in old.items():
    o = json.loads(js)
    by_h_build[o["hazard_id"]][tuple(round(o[k], 6) for k in STAT)] += 1
    by_ho_build[(o["hazard_id"], o["opportunity_id"])].add(tuple(round(o[k], 6) for k in KEYS))
out.append("## K-02 덧붙임 — 대안은 제 위험 카드의 수치를 가진다")
out.append("")
out.append("제안 전체(3,640칸 × 3개)에서 위험 카드마다 (체력, 피해, 속도, 간격) 배율이 한 가지뿐이고 `build()`의 같은 카드와 같은가:")
out.append("")
out.append("| 위험 카드 | 제안에서 나온 배율(개수) | `build()`의 카드 |")
out.append("|---|---|---|")
bad_stats = 0
for h in sorted(by_h):
    same = len(by_h[h]) == 1 and set(by_h[h]) == set(by_h_build[h])
    bad_stats += 0 if same else 1
    out.append("| %s | %s | %s |" % (h, ", ".join("%s ×%d" % (t, c) for t, c in by_h[h].items()), ", ".join("%s" % (t,) for t in by_h_build[h])))
out.append("")
mism = [k for k in by_ho if k in by_ho_build and by_ho[k] != by_ho_build[k]]
out.append("- 배율이 `build()`의 카드와 다른 위험 카드: %d" % bad_stats)
out.append("- (위험, 기회) 쌍 %d가지, 보상 3종이 둘 이상인 쌍 %d, `build()`에도 나온 쌍 %d 중 보상이 다른 쌍 %d" % (len(by_ho), sum(1 for v in by_ho.values() if len(v) > 1), sum(1 for k in by_ho if k in by_ho_build), len(mism)))
out.append("")

# ---- REDLINE vs offers ----------------------------------------------------------------------------------------------------------------
red = {rid: per["REDLINE"] for rid, per in a.items()}
reds = {json.dumps(v, sort_keys=True) for v in red.values()}
sample = next(iter(red.values()))
out.append("## K-09 REDLINE 수치와 제안의 최댓값 비교")
out.append("")
mx = defaultdict(float)
mn = defaultdict(lambda: 99.0)
for rid, per in a.items():
    for m, offers in per.items():
        if m == "REDLINE":
            continue
        for o in offers:
            for k in ("enemy_health_multiplier", "enemy_damage_multiplier", "enemy_speed_multiplier") + tuple(KEYS):
                mx[k] = max(mx[k], o[k])
            mn["enemy_attack_interval_multiplier"] = min(mn["enemy_attack_interval_multiplier"], o["enemy_attack_interval_multiplier"])
            mx["risk_score"] = max(mx["risk_score"], o["risk_score"])
out.append("| 값 | 제안 중 가장 센 것 | REDLINE | 제안 범위(주문서 4.2) |")
out.append("|---|---|---|---|")
rows = [("적 체력", "enemy_health_multiplier", "≤ 1.5"), ("적 피해", "enemy_damage_multiplier", "≤ 1.35"), ("적 속도", "enemy_speed_multiplier", "≤ 1.15")]
for label, k, rng in rows:
    out.append("| %s | %.3f | %.3f | %s |" % (label, mx[k], sample[k], rng))
out.append("| 공격 간격 | %.3f | %.3f | ≥ 0.80 |" % (mn["enemy_attack_interval_multiplier"], sample["enemy_attack_interval_multiplier"]))
for label, k in (("연구 보상", KEYS[0]), ("분석 보상(salvage)", KEYS[1]), ("신호 조각 보상", KEYS[2])):
    out.append("| %s | %.3f | %.3f | 위험 보상 ≤ 1.6 (기회 보상은 별도) |" % (label, mx[k], sample[k]))
out.append("| 위험도(risk_score) | %d | %d | — |" % (mx["risk_score"], sample["risk_score"]))
out.append("")
out.append("REDLINE 계약은 run id %d개에서 모두 같은 값인가: %s" % (len(red), "예" if len({json.dumps({k: v for k, v in r.items() if k not in ('run_id', 'seed_signature')}, sort_keys=True) for r in red.values()}) == 1 else "아니오"))
Path(sys.argv[5]).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print("\n".join(out))
