"""Run everything: python -m holds.run_all (from 2026/peace/do-agreements-hold/). Writes results/."""
import argparse
import json

from . import constants as C
from . import figures as F
from . import km as K
from . import model as M


def pct(x):
    return None if x is None else round(100.0 * x, 1)


def group_stats(spells, by_group=None):
    """KM summary of (years, event) spells; with by_group ({linked group: spells}) also cluster-bootstrap intervals."""
    t = [s[0] for s in spells]
    e = [s[1] for s in spells]
    steps = K.kaplan_meier(t, e)
    med, med_lo, med_hi = K.median(steps)
    out = {
        "agreements": len(spells), "resumed": sum(e), "still_holding_when_data_stop": len(e) - sum(e),
        "resumed_the_next_year": sum(1 for a, b in spells if b and a == 1),
        "median_years": med, "median_ci95_years": [med_lo, med_hi],
    }
    for h in C.HORIZONS:
        s, lo, hi = K.at(steps, h)
        out["holding_at_%d_years_pct" % h] = pct(s)
        out["holding_at_%d_years_ci95_pct" % h] = [pct(lo), pct(hi)]
    if by_group is not None:
        boot = K.cluster_bootstrap(by_group)
        out["linked_groups"] = len(by_group)
        out["median_cluster_ci95_years"] = boot["median"]
        for h in C.HORIZONS:
            out["holding_at_%d_years_cluster_ci95_pct" % h] = [pct(x) for x in boot[h]]
    out["curve"] = [{"t": a, "at_risk": n, "resumed": d, "S": round(s, 4), "lo": round(lo, 4), "hi": round(hi, 4)}
                    for a, n, d, s, lo, hi in steps]
    return out


def _types(agreements):
    return {"All": agreements, **{name: [r for r in agreements if r["pa_type"] == code]
                                  for code, name in C.PA_TYPES.items()}}


def _by_group(rows, spells, group):
    out = {}
    for r in rows:
        if r["paid"] in spells:
            out.setdefault(group[r["paid"]], []).append(spells[r["paid"]])
    return out


def _groups(agreements, spells, group):
    return {name: group_stats([spells[r["paid"]] for r in rows if r["paid"] in spells],
                              _by_group(rows, spells, group))
            for name, rows in _types(agreements).items()}


def _logrank(agreements, spells):
    def sel(code):
        sp = [spells[r["paid"]] for r in agreements if r["pa_type"] == code and r["paid"] in spells]
        return [s[0] for s in sp], [s[1] for s in sp]
    three = K.logrank([sel(c) for c in C.PA_TYPES])
    two = K.logrank([sel("1"), sel("3")])
    return {"three_types_p": round(three[2], 3), "full_vs_peace_process_p": round(two[2], 3),
            "note": "naive: treats agreements as independent"}


def _first_per_group(agreements, group):
    first = {}
    for r in sorted(agreements, key=lambda r: (int(r["year"]), int(r["paid"]))):
        first.setdefault(group[r["paid"]], r)
    return list(first.values())


def summary(agreements, active_rows):
    act = M.active_years(active_rows)
    group = M.linked_groups(agreements)
    strict = {r["paid"]: M.spell(r, act) for r in agreements}
    quiet_full = {r["paid"]: M.quiet_spell(r, act) for r in agreements}
    quiet = {k: v[:2] for k, v in quiet_full.items() if v is not None}
    lag = {k: v[2] for k, v in quiet_full.items() if v is not None}
    never = [r for r in agreements if quiet_full[r["paid"]] is None]
    early = {k: v for k, v in quiet.items() if lag[k] < C.SETTLED_LATE_YEARS}
    first = _first_per_group(agreements, group)
    sizes = sorted((list(group.values()).count(g) for g in set(group.values())), reverse=True)
    both = sum(1 for r in agreements if M.is_active(r, act, int(r["year"]) + 1) and M.is_active(r, act, int(r["year"])))
    years = [int(r["year"]) for r in agreements]
    first_quiet = [r for r in first if r["paid"] in quiet]
    return {
        "label": C.LABEL,
        "prize": C.PRIZE,
        "datasets": {
            "peace_agreements": {"name": "UCDP Peace Agreement Dataset", "version": C.PA_VERSION, "url": C.PA_URL,
                                 "sha256": C.PA_SHA256, "rows": len(agreements), "codebook": C.PA_CODEBOOK,
                                 "citation": C.PA_CITATION, "codebook_citation": C.PA_CODEBOOK_CITATION,
                                 "signed_years": [min(years), max(years)]},
            "termination": {"name": "UCDP Conflict Termination Dataset, conflict level (active conflict-years)",
                            "version": C.TERM_VERSION, "url": C.TERM_URL, "sha256": C.TERM_SHA256,
                            "rows": len(active_rows), "citation": C.TERM_CITATION, "acd_version": C.ACD_VERSION,
                            "last_year": C.LAST_YEAR},
            "licence": C.LICENCE,
        },
        "definition": {
            "active": "a conflict id is active in a calendar year with at least 25 battle-related deaths; a year "
                      "with fewer is quiet",
            "battle_deaths_threshold": 25,
            "main": "the agreement first has to bring the fighting below the threshold: the clock starts at the first "
                    "calendar year after signing in which no conflict id the agreement lists is active, and runs to "
                    "the next active year (counted from the year before the first quiet year, so holding at 5 years "
                    "means 5 or more quiet years in a row); agreements that never got below the threshold by 2024 "
                    "are reported apart",
            "strict": "the clock starts at the signing year and runs to the first later active year, so fighting "
                      "that never stopped counts as resumed",
            "settled_late": "the first quiet year came 5 or more years after signing, which is hard to credit to "
                            "the agreement",
            "censoring": "agreements with no later active year are still holding when the data stop (2024)",
            "unit": "one agreement; agreements in linked conflicts are not independent",
            "figure_years": C.FIGURE_YEARS,
            "intervals": "main intervals: 95 % percentile cluster bootstrap over linked conflict groups (2000 "
                         "resamples, seed 2026); Greenwood log-log intervals are kept for reference and are too "
                         "narrow",
        },
        "pa_type_counts": {name: sum(r["pa_type"] == code for r in agreements) for code, name in C.PA_TYPES.items()},
        "horizons_years": list(C.HORIZONS),
        "ci_level_pct": 95,
        "dependence": {
            "linked_groups": len(sizes), "largest_group": sizes[0], "single_agreement_groups": sizes.count(1),
            "group_sizes": sorted(sizes, reverse=True),
            "share_in_groups_of_5_or_more_pct": pct(sum(x for x in sizes if x >= 5) / len(agreements)),
            "bootstrap_resamples": C.BOOT_REPS, "bootstrap_seed": C.BOOT_SEED,
        },
        "main": {
            "reached_a_quiet_year": len(quiet),
            "never_below_threshold": {name: sum(1 for r in rows if r in never)
                                      for name, rows in _types(agreements).items()},
            "never_below_threshold_signed_2015_or_later": sum(int(r["year"]) >= 2015 for r in never),
            "years_from_signing_to_first_quiet_year": {
                "1": sum(v == 1 for v in lag.values()),
                "2-4": sum(2 <= v < C.SETTLED_LATE_YEARS for v in lag.values()),
                "5_or_more": sum(v >= C.SETTLED_LATE_YEARS for v in lag.values())},
            "groups": _groups(agreements, quiet, group),
            "without_settled_late": _groups(agreements, early, group),
            "first_agreement_per_linked_group": {
                "never_below_threshold": len(first) - len(first_quiet),
                "All": group_stats([quiet[r["paid"]] for r in first_quiet])},
            "logrank": _logrank(agreements, quiet),
        },
        "strict": {
            "groups": _groups(agreements, strict, group),
            "next_year_and_signing_year_both_active": both,
            "first_agreement_per_linked_group": {"All": group_stats([strict[r["paid"]] for r in first])},
            "logrank": _logrank(agreements, strict),
        },
        "signing_context": {name: {
            "signed_in_an_active_year_pct": pct(sum(M.is_active(r, act, int(r["year"])) for r in rows) / len(rows)),
            "next_year_active_pct": pct(sum(M.is_active(r, act, int(r["year"]) + 1) for r in rows) / len(rows))}
            for name, rows in _types(agreements).items()},
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-figures", action="store_true")
    a = ap.parse_args(argv)
    s = summary(*M.load())
    F.RESULTS.mkdir(parents=True, exist_ok=True)
    (F.RESULTS / "do_agreements_hold.json").write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n")
    if not a.no_figures:
        F.fig_km(s)
    for clock in ("main", "strict"):
        for g, v in s[clock]["groups"].items():
            print(clock, g, {k: x for k, x in v.items() if k != "curve"})
    print({k: v for k, v in s["main"].items() if k not in ("groups", "without_settled_late")})
    for g, v in s["main"]["without_settled_late"].items():
        print("without settled late", g, {k: x for k, x in v.items() if k != "curve"})
    print(s["dependence"], s["strict"]["next_year_and_signing_year_both_active"], s["strict"]["logrank"])
    print(s["signing_context"])


if __name__ == "__main__":
    main()
