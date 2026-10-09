"""Review checks for toy 2 (do-agreements-hold). Uses the toy's derived CSVs and its own KM; lifelines as cross-check."""
import json
import random
import sys
from pathlib import Path
import numpy as np

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "repos"
TOY = ROOT / "hold/2026/peace/do-agreements-hold"
sys.path.insert(0, str(TOY))
from holds import km as K, model as M, constants as C  # noqa: E402

agreements, active_rows = M.load()
act = M.active_years(active_rows)
LAST = C.LAST_YEAR
out = {}


def ids(r):
    return M.conflict_ids(r["conflict_id"])


def is_active(r, y):
    return any(y in act.get(c, ()) for c in ids(r))


def spell_orig(r):
    return M.spell(r, act)


def spell_quiet(r):
    """Clock starts at the first calendar year after signing with no listed conflict active (< 25 deaths).
    Time = years counted from the year before that first quiet year, so S(5) = share with 5+ quiet years,
    the same scale as the toy (where S(5) = no fighting in the 5 years after signing). None = never quiet by 2024."""
    y = int(r["year"])
    q = next((t for t in range(y + 1, LAST + 1) if not is_active(r, t)), None)
    if q is None:
        return None
    nxt = next((t for t in range(q + 1, LAST + 1) if is_active(r, t)), None)
    return (nxt - (q - 1), 1) if nxt else (LAST - (q - 1), 0), q - y


def stats(spells):
    t, e = [s[0] for s in spells], [s[1] for s in spells]
    st = K.kaplan_meier(t, e)
    med = K.median(st)
    o = {"n": len(spells), "resumed": sum(e), "median": med[0], "median_ci": [med[1], med[2]]}
    for h in (1, 5, 10):
        s, lo, hi = K.at(st, h)
        o[f"S{h}"] = round(100 * s, 1)
        o[f"S{h}_ci"] = [round(100 * lo, 1), round(100 * hi, 1)]
    return o


types = {"All": None, **{v: k for k, v in C.PA_TYPES.items()}}
orig = {r["paid"]: spell_orig(r) for r in agreements}
quiet = {}
never = []
lag = []
for r in agreements:
    s = spell_quiet(r)
    if s is None:
        never.append(r)
    else:
        quiet[r["paid"]] = s[0]
        lag.append(s[1])
out["quiet_clock"] = {
    "reached_a_quiet_year": len(quiet), "never_below_threshold_by_2024": len(never),
    "never_by_type": {n: sum(1 for r in never if c is None or r["pa_type"] == c) for n, c in types.items()},
    "never_signed_2015_or_later": sum(int(r["year"]) >= 2015 for r in never),
    "lag_years_to_first_quiet_year": {"1": lag.count(1), "2-4": sum(2 <= x <= 4 for x in lag), "5+": sum(x >= 5 for x in lag)},
    "first_quiet_year_is_next_year_share_of_all_pct": round(100 * lag.count(1) / len(agreements), 1),
}
out["orig"] = {n: stats([orig[r["paid"]] for r in agreements if c is None or r["pa_type"] == c]) for n, c in types.items()}
out["quiet"] = {n: stats([quiet[r["paid"]] for r in agreements if r["paid"] in quiet and (c is None or r["pa_type"] == c)])
                for n, c in types.items()}

# clusters: connected components of conflict ids (an agreement listing two ids joins them)
parent = {}


def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


for r in agreements:
    cs = ids(r)
    for c in cs[1:]:
        parent[find(c)] = find(cs[0])
clus = {r["paid"]: find(ids(r)[0]) for r in agreements}
out["clusters"] = len(set(clus.values()))
sizes = sorted([list(clus.values()).count(c) for c in set(clus.values())], reverse=True)
out["cluster_sizes"] = {"largest": sizes[0], "singletons": sizes.count(1), "share_of_agreements_in_clusters_of_5plus_pct":
                        round(100 * sum(s for s in sizes if s >= 5) / len(agreements), 1)}


def one_per_conflict(which):
    by = {}
    for r in sorted(agreements, key=lambda r: (int(r["year"]), int(r["paid"]))):
        c = clus[r["paid"]]
        if which == "first":
            by.setdefault(c, r)
        else:
            by[c] = r
    return list(by.values())


for which in ("first", "last"):
    sel = one_per_conflict(which)
    out[f"orig_{which}_per_conflict"] = {n: stats([orig[r["paid"]] for r in sel if c is None or r["pa_type"] == c])
                                         for n, c in types.items()}
    q = [r for r in sel if r["paid"] in quiet]
    out[f"quiet_{which}_per_conflict"] = {"All": stats([quiet[r["paid"]] for r in q]),
                                          "never_quiet": len(sel) - len(q)}


def boot(spell_map, rows, reps=2000, seed=2026):
    rng = random.Random(seed)
    groups = {}
    for r in rows:
        if r["paid"] in spell_map:
            groups.setdefault(clus[r["paid"]], []).append(spell_map[r["paid"]])
    keys = list(groups)
    res = {h: [] for h in (5, 10)}
    meds = []
    for _ in range(reps):
        sp = [s for k in (rng.choice(keys) for _ in keys) for s in groups[k]]
        st = K.kaplan_meier([s[0] for s in sp], [s[1] for s in sp])
        for h in res:
            res[h].append(K.at(st, h)[0])
        meds.append(K.median(st)[0] or 99)
    o = {f"S{h}_cluster_boot_ci": [round(100 * np.percentile(v, 2.5), 1), round(100 * np.percentile(v, 97.5), 1)]
         for h, v in res.items()}
    o["median_cluster_boot_ci"] = [None if v >= 99 else float(v) for v in np.percentile(meds, [2.5, 97.5])]  # None: not reached
    o["clusters"] = len(keys)
    return o


out["boot_orig"] = {n: boot(orig, [r for r in agreements if c is None or r["pa_type"] == c]) for n, c in types.items()}
out["boot_quiet"] = {n: boot(quiet, [r for r in agreements if c is None or r["pa_type"] == c]) for n, c in types.items()}

# lifelines cross-check of the toy's hand-written KM


def fin(x):
    return float(x) if np.isfinite(x) else None


from lifelines import KaplanMeierFitter  # noqa: E402
from lifelines.utils import median_survival_times  # noqa: E402
from lifelines.statistics import logrank_test, multivariate_logrank_test  # noqa: E402

res = json.loads((TOY / "results/do_agreements_hold.json").read_text())
xc = {}
for n, c in types.items():
    sp = [orig[r["paid"]] for r in agreements if c is None or r["pa_type"] == c]
    sq = [quiet[r["paid"]] for r in agreements if r["paid"] in quiet and (c is None or r["pa_type"] == c)]
    for label, spell_list in (("orig", sp), ("quiet", sq)):
        t, e = [s[0] for s in spell_list], [s[1] for s in spell_list]
        kmf = KaplanMeierFitter().fit(t, e)
        mine = K.kaplan_meier(t, e)
        ci = kmf.confidence_interval_survival_function_
        dmax_s = dmax_ci = 0.0
        for tt, _, _, s, lo, hi in mine:
            dmax_s = max(dmax_s, abs(kmf.survival_function_at_times(tt).iloc[0] - s))
            row = ci[ci.index <= tt].iloc[-1]
            dmax_ci = max(dmax_ci, abs(row.iloc[0] - lo), abs(row.iloc[1] - hi))
        mci = median_survival_times(ci)
        xc[f"{n}/{label}"] = {"max_abs_diff_S": float(dmax_s), "max_abs_diff_ci": float(dmax_ci),
                              "median_lifelines": float(kmf.median_survival_time_), "median_toy": K.median(mine)[0],
                              "median_ci_lifelines": [fin(mci.iloc[0, 0]), fin(mci.iloc[0, 1])],
                              "median_ci_toy": list(K.median(mine)[1:])}
out["lifelines_crosscheck"] = xc
out["json_matches_toy_rerun"] = all(
    res["groups"][n]["holding_at_5_years_pct"] == out["orig"][n]["S5"] and
    res["groups"][n]["holding_at_10_years_pct"] == out["orig"][n]["S10"] for n in types)


def lr(spell_map, a, b):
    A = [spell_map[r["paid"]] for r in agreements if r["pa_type"] == a and r["paid"] in spell_map]
    B = [spell_map[r["paid"]] for r in agreements if r["pa_type"] == b and r["paid"] in spell_map]
    return round(logrank_test([s[0] for s in A], [s[0] for s in B], [s[1] for s in A], [s[1] for s in B]).p_value, 3)


def lr3(spell_map):
    rows = [(spell_map[r["paid"]], r["pa_type"]) for r in agreements if r["paid"] in spell_map]
    return round(multivariate_logrank_test([s[0] for s, _ in rows], [g for _, g in rows], [s[1] for s, _ in rows]).p_value, 3)


out["logrank_naive_p"] = {"orig_3_types": lr3(orig), "orig_full_vs_process": lr(orig, "1", "3"),
                          "quiet_3_types": lr3(quiet), "quiet_full_vs_process": lr(quiet, "1", "3")}
print(json.dumps(out, indent=1, default=str))
