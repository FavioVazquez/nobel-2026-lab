"""Run everything: python -m ends.run_all (from 2026/peace/how-conflicts-end/). Writes results/."""
import argparse
import json

from . import constants as C
from . import figures as F
from . import model as M


def _share(k, n):
    lo, hi = M.wilson(k, n)
    return M.pct(k / n), [M.pct(lo), M.pct(hi)]


def _trend(sub, codes):
    years = [int(r["year"]) for r in sub]
    return {"years": [min(years), max(years)],
            **M.trend(years, [int(r["c_outcome"] in codes) for r in sub])}


def summary(rows):
    term = M.terminations(rows)
    dec = M.by_decade(rows)
    per = []
    for d, counts in dec.items():
        n = sum(counts.values())
        k = sum(counts[c] for c in C.AGREEMENT)
        n_clear = sum(counts[c] for c in C.CLEAR)
        share, ci = _share(k, n)
        clear_share, clear_ci = _share(k, n_clear)
        last = min(d + 9, C.CODED_LAST)
        per.append({
            "decade": "%ds" % d,
            "years": "%d-%d" % (max(d, C.CODED_FIRST), last),
            "n_years": last - max(d, C.CODED_FIRST) + 1,
            "episodes_ended": n,
            "counts": {C.OUTCOMES[c]: counts[c] for c in C.OUTCOMES},
            "shares_pct": {C.OUTCOMES[c]: M.pct(counts[c] / n) for c in C.OUTCOMES},
            "agreement_or_ceasefire": k,
            "agreement_or_ceasefire_pct": share,
            "agreement_or_ceasefire_ci95_pct": ci,
            "low_activity_pct": M.pct(counts[C.LOW_ACTIVITY] / n),
            "clear_outcome_endings": n_clear,
            "agreement_or_ceasefire_among_clear_pct": clear_share,
            "agreement_or_ceasefire_among_clear_ci95_pct": clear_ci,
        })
    totals = {C.OUTCOMES[c]: sum(1 for r in term if r["c_outcome"] == c) for c in C.OUTCOMES}
    k_all = sum(totals[C.OUTCOMES[c]] for c in C.AGREEMENT)
    ongoing = sum(1 for r in rows if int(r["year"]) == C.ACTIVE_LAST_YEAR)
    first, best = per[0], max(per, key=lambda p: p["agreement_or_ceasefire_pct"])
    ids = [r["c_epid"] for r in term]
    endings = sorted((int(r["year"]), C.OUTCOMES[r["c_outcome"]]) for r in term)
    clear = [r for r in term if r["c_outcome"] in C.CLEAR]
    n_clear = len(clear)
    k_clear = sum(r["c_outcome"] in C.AGREEMENT for r in clear)
    before = [p for p in per if int(p["decade"][:4]) < 1990]
    since = [p for p in per if 1990 <= int(p["decade"][:4]) <= C.LAST_COMPLETE_DECADE_END]
    return {
        "label": C.LABEL,
        "prize": C.PRIZE,
        "dataset": {
            "name": "UCDP Conflict Termination Dataset, conflict level", "version": C.VERSION,
            "version_field": C.VERSION_FIELD, "url": C.DATA_URL, "sha256": C.DATA_SHA256, "licence": C.LICENCE,
            "citation": C.CITATION, "codebook": C.CODEBOOK, "acd_version": C.ACD_VERSION,
            "rows": len(rows), "coded_years": [C.CODED_FIRST, C.CODED_LAST],
        },
        "unit": "one conflict-year row with c_epterm = 1 (the last active year of an episode); outcome = c_outcome",
        "terminations": len(term),
        "episodes": len(term),
        "episode_ids_used_twice": sum(1 for i in set(ids) if ids.count(i) == 2),
        "episode_ids_note": "every row with c_epterm = 1 ends one episode; two c_epid values are each used for two "
                            "separate episodes (different start years in the raw file), so 507 endings are 507 "
                            "episodes but only 505 distinct c_epid values",
        "totals": totals,
        "totals_sum": sum(totals.values()),
        "ending_years": [y for y, _ in endings],
        "ending_outcomes_by_year": [o for _, o in endings],
        "ending_order": "one entry per ending (c_epterm = 1 row), sorted by end year, then by outcome name; "
                        "ending_outcomes_by_year[i] is the codebook outcome of the ending in ending_years[i]",
        "agreement_or_ceasefire_all": k_all,
        "agreement_or_ceasefire_all_pct": M.pct(k_all / len(term)),
        "by_decade": per,
        "answer": {
            "question": "has the share of episodes ending in a peace agreement or ceasefire risen since the 1940s?",
            "first_decade": first["decade"], "first_decade_pct": first["agreement_or_ceasefire_pct"],
            "highest_decade": best["decade"], "highest_decade_pct": best["agreement_or_ceasefire_pct"],
            "last_decade": per[-1]["decade"], "last_decade_pct": per[-1]["agreement_or_ceasefire_pct"],
            "last_decade_n": per[-1]["episodes_ended"], "last_decade_years": per[-1]["n_years"],
            "ci_level_pct": 95,
        },
        "second_view": {
            "clear_outcomes": [C.OUTCOMES[c] for c in C.CLEAR],
            "clear_outcome_endings": n_clear,
            "agreement_or_ceasefire_among_clear": k_clear,
            "agreement_or_ceasefire_among_clear_pct": M.pct(k_clear / n_clear),
            "before_1990_max_pct": max(p["agreement_or_ceasefire_among_clear_pct"] for p in before),
            "complete_decades_since_1990_min_pct": min(p["agreement_or_ceasefire_among_clear_pct"] for p in since),
            "low_activity_first_decade_pct": per[0]["low_activity_pct"],
            "low_activity_2010s_pct": next(p["low_activity_pct"] for p in per if p["decade"] == "2010s"),
            "low_activity_last_decade_pct": per[-1]["low_activity_pct"],
        },
        "trends": {
            "method": "logistic regression of a 0/1 outcome on the year the episode ended (in decades); Wald 95 % "
                      "interval; squared_term_p tests for a curve (rise then fall, or the reverse)",
            "p_floor": C.P_FLOOR,
            "agreement_or_ceasefire_all_endings": _trend(term, C.AGREEMENT),
            "agreement_or_ceasefire_complete_decades": _trend(
                [r for r in term if int(r["year"]) <= C.LAST_COMPLETE_DECADE_END], C.AGREEMENT),
            "agreement_or_ceasefire_since_1989": _trend([r for r in term if int(r["year"]) >= C.TREND_SINCE],
                                                        C.AGREEMENT),
            "peace_agreement_only": _trend(term, ("1",)),
            "ceasefire_only": _trend(term, ("2",)),
            "low_activity": _trend(term, (C.LOW_ACTIVITY,)),
            "agreement_or_ceasefire_among_clear_outcomes": _trend(clear, C.AGREEMENT),
        },
        "censoring": {
            "conflicts_active_in_last_year": ongoing, "last_year": C.ACTIVE_LAST_YEAR,
            "note": "grouped by the year an episode ended, every decade up to the 2010s is complete: any episode that "
                    "ended then is in the file. Conflicts active in 2024 have no outcome yet and can only add endings "
                    "to the 2020s (which hold only 2020-2023) or later. An episode that ended in low activity can "
                    "restart as a new episode",
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-figures", action="store_true")
    a = ap.parse_args(argv)
    s = summary(M.load())
    F.RESULTS.mkdir(parents=True, exist_ok=True)
    (F.RESULTS / "how_conflicts_end.json").write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n")
    if not a.no_figures:
        F.fig_shares(s)
        F.fig_agreement(s)
    for p in s["by_decade"]:
        print(p["decade"], p["episodes_ended"], p["agreement_or_ceasefire_pct"], p["agreement_or_ceasefire_ci95_pct"])
    print({k: v for k, v in s.items() if k in ("terminations", "totals", "answer", "second_view", "censoring")})
    for k, v in s["trends"].items():
        print(k, v)


if __name__ == "__main__":
    main()
