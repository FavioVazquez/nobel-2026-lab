"""Build page/data.js from the two Peace toys (educational demos made to show an open-source tool; not research).

Reads, relative to this folder (where the toys live after the merge):
  ../how-conflicts-end/results   how_conflicts_end.json   (and ../how-conflicts-end/INSIGHTS.md)
  ../do-agreements-hold/results  do_agreements_hold.json  (and ../do-agreements-hold/INSIGHTS.md)
and writes data.js, a plain script that sets window.NOBEL_PEACE_DATA, so index.html works from file:// with no server
and no network. Every number the page shows comes from these files; nothing is typed into index.html. The narrator
sentences are the toys' INSIGHTS.md lines, unchanged. Python 3 standard library only.

    python3 build_data.py --from ENDS_RESULTS HOLD_RESULTS   # the toys' results folders anywhere (e.g. worktrees)
    python3 build_data.py                                   # from 2026/peace/page/ after the merge
    python3 build_data.py --fixtures                        # the copies in tests/fixtures (status "fixture")
    python3 build_data.py --out /tmp/data.js                # write somewhere else

It prints the status of each input file ("final", "preliminary", "fixture" or "missing"). A results file with no
"status" field counts as final (the toys' numbers are final once their branch is). The page shows a visible
"preliminary" box unless every input is "final".
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "tests" / "fixtures"
TOYS = ("how-conflicts-end", "do-agreements-hold")
FILES = ("how_conflicts_end.json", "do_agreements_hold.json")
DEFAULTS = tuple(HERE.parent / t / "results" for t in TOYS)
TAG = "Educational demos made to show an open-source tool. Not research."
GITHUB = "https://github.com/FavioVazquez/nobel-2026-lab/tree/main/2026/peace/"
SHOWTIME = "https://github.com/FavioVazquez/showtime"
STATUS_ORDER = ["missing", "fixture", "preliminary", "final"]

# ---- fixed facts (the Norwegian Nobel Committee, press release) -------------------------------------------------
PR = "https://www.nobelprize.org/prizes/peace/2026/press-release/"
PRIZE = {
    "year": 2026,
    "laureate": "Navanethem Pillay",
    "citation": "for her efforts to promote peace and international law",
    "by": "The Norwegian Nobel Committee, press release",
    "url": PR,
}
UCDP = "https://ucdp.uu.se/downloads/"
LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"
FONTS = {"sans": "IBM Plex Sans", "serif": "Source Serif 4", "licence": "SIL Open Font License 1.1", "file": "fonts/OFL.txt"}


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def status_of(obj):
    if obj is None:
        return "missing"
    if "status" not in obj:
        return "final"
    s = str(obj["status"]).lower()
    if s.startswith("final"):
        return "final"
    return s if s in ("preliminary", "fixture") else "preliminary"


def insights(results_dir):
    """The toy's INSIGHTS.md lines -> [{"text", "fields"}]: the sentence as written, and the JSON fields it names."""
    p = Path(results_dir).parent / "INSIGHTS.md"
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\d+\.\s+(.*?)\s*\(fields?:\s*(.*)\)\s*$", line)
        if m:
            out.append({"text": m.group(1), "fields": re.findall(r"`([^`]+)`", m.group(2))})
    return out


def _trend(t):
    keys = ("endings", "events", "slope_log_odds_per_decade", "slope_ci95", "odds_ratio_per_decade", "p",
            "squared_term_p", "years")
    return {k: t.get(k) for k in keys}


def ends_block(folder):
    d = load(Path(folder) / FILES[0])
    st = status_of(d)
    if d is None:
        return None, st
    decades = [{"decade": p["decade"], "years": p["years"], "n_years": p["n_years"], "n": p["episodes_ended"],
                "agree": p["agreement_or_ceasefire"], "pct": p["agreement_or_ceasefire_pct"],
                "ci": p["agreement_or_ceasefire_ci95_pct"], "low": p["low_activity_pct"],
                "clear_n": p["clear_outcome_endings"], "clear_pct": p["agreement_or_ceasefire_among_clear_pct"],
                "clear_ci": p["agreement_or_ceasefire_among_clear_ci95_pct"]} for p in d["by_decade"]]
    if sum(x["n"] for x in decades) != d["terminations"]:
        print(f"  WARNING: decades hold {sum(x['n'] for x in decades)} endings, terminations = {d['terminations']}")
    if sum(x["agree"] for x in decades) != d["agreement_or_ceasefire_all"]:
        print("  WARNING: the decades' agreements do not add up to agreement_or_ceasefire_all")
    T, ds = d["trends"], d["dataset"]
    return {
        "endings": d["terminations"], "agree": d["agreement_or_ceasefire_all"], "pct": d["agreement_or_ceasefire_all_pct"],
        "years": ds["coded_years"], "ci_level": d["answer"]["ci_level_pct"], "decades": decades,
        "second": d["second_view"],
        "trends": {"all": _trend(T["agreement_or_ceasefire_all_endings"]),
                   "since": _trend(T["agreement_or_ceasefire_since_1989"]),
                   "clear": _trend(T["agreement_or_ceasefire_among_clear_outcomes"]),
                   "low": _trend(T["low_activity"]), "p_floor": T["p_floor"]},
        "censoring": {"active": d["censoring"]["conflicts_active_in_last_year"], "last_year": d["censoring"]["last_year"]},
        "credit": {"name": ds["name"], "version": ds["version"], "citation": ds["citation"], "codebook": ds["codebook"],
                   "licence": ds["licence"], "url": ds["url"], "acd_version": ds["acd_version"]},
        "insights": insights(folder),
    }, st


def _curve(g, xmax):
    return [[c["t"], c["S"]] for c in g["curve"] if c["t"] <= xmax]


def _clock(c, xmax, h):
    a = c["groups"]["All"]
    return {"n": a["agreements"], "resumed": a["resumed"], "pct": a[f"holding_at_{h}_years_pct"],
            "ci": a[f"holding_at_{h}_years_cluster_ci95_pct"], "ci_greenwood": a[f"holding_at_{h}_years_ci95_pct"],
            "median": a["median_years"], "curve": _curve(a, xmax),
            "types": {k: g[f"holding_at_{h}_years_pct"] for k, g in c["groups"].items() if k != "All"},
            "logrank": {k: c["logrank"][k] for k in ("three_types_p", "full_vs_peace_process_p")}}


def hold_block(folder):
    d = load(Path(folder) / FILES[1])
    st = status_of(d)
    if d is None:
        return None, st
    M, S, D, ds = d["main"], d["strict"], d["dependence"], d["datasets"]
    xmax, h = d["definition"]["figure_years"], d["horizons_years"][0]
    main, strict = _clock(M, xmax, h), _clock(S, xmax, h)
    w = M["without_settled_late"]["All"]
    f = M["first_agreement_per_linked_group"]["All"]
    main.update({"reached": M["reached_a_quiet_year"], "never": M["never_below_threshold"]["All"],
                 "lag": M["years_from_signing_to_first_quiet_year"],
                 "without_late": {"n": w["agreements"], "pct": w[f"holding_at_{h}_years_pct"],
                                  "ci": w[f"holding_at_{h}_years_cluster_ci95_pct"]},
                 "first_per_group": {"n": f["agreements"], "pct": f[f"holding_at_{h}_years_pct"]}})
    strict.update({"next_year": S["groups"]["All"]["resumed_the_next_year"],
                   "both_active": S["next_year_and_signing_year_both_active"]})
    if main["reached"] + main["never"] != strict["n"]:
        print("  WARNING: reached + never below the threshold != all agreements")
    pa, tm = ds["peace_agreements"], ds["termination"]
    return {
        "horizon": h, "ci_level": d["ci_level_pct"], "agreements": strict["n"], "signed_years": pa["signed_years"],
        "threshold": d["definition"]["battle_deaths_threshold"], "last_year": tm["last_year"], "figure_years": xmax,
        "groups": D["linked_groups"], "largest": D["largest_group"], "resamples": D["bootstrap_resamples"],
        "main": main, "strict": strict,
        "credit": {"pa": {"name": pa["name"], "version": pa["version"], "citation": pa["citation"],
                          "codebook_citation": pa["codebook_citation"], "url": pa["url"]},
                   "term": {"name": tm["name"], "version": tm["version"], "citation": tm["citation"], "url": tm["url"]},
                   "licence": ds["licence"]},
        "insights": insights(folder),
    }, st


def build(ends_dir, hold_dir, fixtures=False):
    print("Peace page inputs:")
    ends, s1 = ends_block(ends_dir)
    hold, s2 = hold_block(hold_dir)
    inputs = {FILES[0]: s1, FILES[1]: s2}
    for (name, st), folder in zip(inputs.items(), (ends_dir, hold_dir)):
        print(f"  {st:12s}  {name:26s} ({folder})")
    return {
        "tag": TAG, "inputs": inputs,
        "preliminary": any(v != "final" for v in inputs.values()),
        "placeholder": fixtures or any(v == "fixture" for v in inputs.values()),
        "prize": PRIZE, "ends": ends, "hold": hold, "fonts": FONTS,
        "links": {"ucdp": UCDP, "licence": LICENCE_URL, "github": GITHUB, "showtime": SHOWTIME,
                  "ends": "../how-conflicts-end/", "hold": "../do-agreements-hold/"},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from", dest="src", nargs=2, metavar=("ENDS_RESULTS", "HOLD_RESULTS"))
    ap.add_argument("--fixtures", action="store_true")
    ap.add_argument("--out", default=str(HERE / "data.js"))
    a = ap.parse_args(argv)
    if a.fixtures:
        dirs = tuple(FIXTURES / t / "results" for t in TOYS)
    elif a.src:
        dirs = tuple(Path(p).resolve() for p in a.src)
    else:
        dirs = DEFAULTS
    data = build(*dirs, fixtures=a.fixtures)
    js = ("// Generated by build_data.py; do not edit. Educational demos made to show an open-source tool. Not research.\n"
          "window.NOBEL_PEACE_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + ";\n")
    Path(a.out).write_text(js, encoding="utf-8")
    print(f"wrote {a.out} ({len(js.encode()) / 1024:.1f} KB); preliminary box {'shown' if data['preliminary'] else 'hidden'}")
    return data


if __name__ == "__main__":
    main(sys.argv[1:])
