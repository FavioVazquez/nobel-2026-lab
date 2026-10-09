"""Checks of the data, the Kaplan-Meier code, the README numbers and the figures. Educational demo, not research."""
import csv
import hashlib
import json
import re

import pytest
from matplotlib.image import imread

from holds import constants as C
from holds import fetch_data as D
from holds import km as K
from holds import model as M
from holds import run_all as R

HERE = C.HERE
RES = json.loads((HERE / "results" / "do_agreements_hold.json").read_text())
NUM = re.compile(r"\d+(?:\.\d+)?")


def tokens(obj):
    """Every number written anywhere in a JSON value: keys, strings and numbers."""
    out = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            out |= tokens(k) | tokens(v)
    elif isinstance(obj, list):
        for v in obj:
            out |= tokens(v)
    elif isinstance(obj, bool) or obj is None:
        pass
    elif isinstance(obj, (int, float)):
        out |= set(NUM.findall(str(obj)))
    else:
        out |= set(NUM.findall(str(obj)))
    return out


def prose(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    return re.sub(r"https?://\S+", " ", text)


def resolve(path):
    v = RES
    for part in path.split("."):
        v = v[part]
    return v


@pytest.mark.parametrize("path,digest", [(C.PA_RAW, C.PA_SHA256), (C.TERM_RAW, C.TERM_SHA256)])
def test_raw_sha256(path, digest):
    if not path.exists():
        pytest.skip("raw file not fetched (python -m holds.fetch_data)")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest


def test_derived_sha256_and_columns():
    for path, digest, cols in ((C.AGREEMENTS, C.AGREEMENTS_SHA256, C.AGREEMENT_COLUMNS),
                               (C.ACTIVE, C.ACTIVE_SHA256, C.ACTIVE_COLUMNS)):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
        with open(path, newline="") as f:
            assert tuple(next(csv.reader(f))) == cols


def test_derived_matches_raw():
    if not (C.PA_RAW.exists() and C.TERM_RAW.exists()):
        pytest.skip("raw files not fetched")
    agreements, active = M.load()
    assert D.read_agreements() == agreements
    assert D.read_active() == active


def test_category_totals_match_row_counts():
    agreements, active = M.load()
    assert len(agreements) == C.PA_ROWS == RES["datasets"]["peace_agreements"]["rows"]
    assert len(active) == C.TERM_ROWS == RES["datasets"]["termination"]["rows"]
    assert {r["pa_type"] for r in agreements} == set(C.PA_TYPES)
    strict, main = RES["strict"]["groups"], RES["main"]["groups"]
    assert sum(RES["pa_type_counts"].values()) == len(agreements) == strict["All"]["agreements"]
    for name, n in RES["pa_type_counts"].items():
        assert strict[name]["agreements"] == n == main[name]["agreements"] + RES["main"]["never_below_threshold"][name]
    assert main["All"]["agreements"] == RES["main"]["reached_a_quiet_year"]
    assert main["All"]["agreements"] + RES["main"]["never_below_threshold"]["All"] == len(agreements)
    lag = RES["main"]["years_from_signing_to_first_quiet_year"]
    assert sum(lag.values()) == RES["main"]["reached_a_quiet_year"]
    assert RES["main"]["without_settled_late"]["All"]["agreements"] == main["All"]["agreements"] - lag["5_or_more"]
    for clock in (strict, main, RES["main"]["without_settled_late"]):
        for g in clock.values():
            assert g["resumed"] + g["still_holding_when_data_stop"] == g["agreements"]
            assert g["curve"][0]["at_risk"] == g["agreements"]
            assert sum(c["resumed"] for c in g["curve"]) == g["resumed"]
            for h in C.HORIZONS:
                lo, hi = g["holding_at_%d_years_cluster_ci95_pct" % h]
                assert lo <= g["holding_at_%d_years_pct" % h] <= hi
    assert strict["All"]["linked_groups"] == RES["dependence"]["linked_groups"]
    assert RES["main"]["first_agreement_per_linked_group"]["All"]["agreements"] + \
        RES["main"]["first_agreement_per_linked_group"]["never_below_threshold"] == RES["dependence"]["linked_groups"]
    assert RES["strict"]["next_year_and_signing_year_both_active"] <= strict["All"]["resumed_the_next_year"]
    assert all(c in M.active_years(active) for r in agreements for c in M.conflict_ids(r["conflict_id"]))


def test_results_are_current():
    assert json.loads(json.dumps(R.summary(*M.load()))) == RES


def test_km_hand_example():
    # times 1, 2, 2, 3, 4; events 1, 1, 0, 1, 0 (the censored 2 leaves after the event at 2)
    steps = K.kaplan_meier([1, 2, 2, 3, 4], [1, 1, 0, 1, 0])
    assert [(t, n, d) for t, n, d, *_ in steps] == [(0, 5, 0), (1, 5, 1), (2, 4, 1), (3, 2, 1)]
    assert [s for *_, s, _, _ in steps] == pytest.approx([1.0, 0.8, 0.6, 0.3])
    assert K.at(steps, 4)[0] == pytest.approx(0.3) and K.at(steps, 2.5)[0] == pytest.approx(0.6)
    assert K.median(steps)[0] == 3
    # Greenwood at t = 2: 1/(5*4) + 1/(4*3) = 0.133333; se of log(-log S) = sqrt(0.133333)/|ln 0.6| = 0.714820;
    # band 0.6 ** exp(+-1.959964 * 0.714820) = 0.12573 .. 0.88176
    assert K.at(steps, 2)[1:] == pytest.approx((0.12573, 0.88176), abs=2e-4)


def test_km_all_censored_never_drops():
    steps = K.kaplan_meier([3, 5, 8], [0, 0, 0])
    assert K.at(steps, 10) == (1.0, 1.0, 1.0) and K.median(steps) == (None, None, None)


def test_spell_hand_example():
    active = {"7": {2000, 2001, 2005}, "8": {2003}}
    assert M.spell({"year": "2001", "conflict_id": "7"}, active) == (4, 1)
    assert M.spell({"year": "2005", "conflict_id": "7"}, active) == (C.LAST_YEAR - 2005, 0)
    assert M.spell({"year": "2001", "conflict_id": "7, 8"}, active) == (2, 1)


def test_quiet_spell_hand_example():
    active = {"7": {2000, 2001, 2002, 2006}, "9": set(range(2010, C.LAST_YEAR + 1))}
    # signed 2001, fighting in 2002, first quiet year 2003, fighting again 2006: counted from 2002, 4 years
    assert M.first_quiet_year({"year": "2001", "conflict_id": "7"}, active) == 2003
    assert M.quiet_spell({"year": "2001", "conflict_id": "7"}, active) == (4, 1, 2)
    assert M.quiet_spell({"year": "2006", "conflict_id": "7"}, active) == (C.LAST_YEAR - 2006, 0, 1)
    assert M.quiet_spell({"year": "2012", "conflict_id": "9"}, active) is None


def test_linked_groups_hand_example():
    g = M.linked_groups([{"paid": "a", "conflict_id": "1"}, {"paid": "b", "conflict_id": "1, 2"},
                         {"paid": "c", "conflict_id": "3"}, {"paid": "d", "conflict_id": "2"}])
    assert g["a"] == g["b"] == g["d"] != g["c"]


def test_logrank_hand_example():
    # one event in each group, at t = 1 and t = 2: at t = 1, O - E = 1 - 1/2, variance 1/4 -> chi-square 1
    x, df, p = K.logrank([([1], [1]), ([2], [1])])
    assert (x, df) == (pytest.approx(1.0), 1) and p == pytest.approx(0.317311, abs=1e-6)
    assert K.chi2_p(5.991464547107979, 2) == pytest.approx(0.05)


def test_cluster_bootstrap_one_group_is_the_point_estimate():
    b = K.cluster_bootstrap({"a": [(1, 1), (3, 0)]}, reps=20)
    assert b[5] == [0.5, 0.5] and b[10] == [0.5, 0.5] and b["median"] == [1, 1]
    two = {"a": [(1, 1)], "b": [(4, 0)]}
    assert K.cluster_bootstrap(two, reps=50) == K.cluster_bootstrap(two, reps=50)  # fixed seed


def test_every_readme_number_is_in_the_json():
    text = (HERE / "README.md").read_text()
    assert text.index("## What it does not show") < text.index("## What it shows")
    missing = sorted(set(NUM.findall(prose(text))) - tokens(RES))
    assert not missing, missing


def test_insights_are_traced_to_json_fields():
    lines = [ln for ln in (HERE / "INSIGHTS.md").read_text().splitlines() if re.match(r"[1-5]\. ", ln)]
    assert 3 <= len(lines) <= 5
    for ln in lines:
        text, _, refs = ln[2:].partition("(fields:")
        paths = re.findall(r"`([^`]+)`", refs)
        assert paths, ln
        have = set().union(*(tokens(resolve(p)) for p in paths))
        assert set(NUM.findall(text)) <= have, (ln, set(NUM.findall(text)) - have)


def test_figures_light_and_dark():
    light = imread(HERE / "results" / "km_by_type_light.png")
    dark = imread(HERE / "results" / "km_by_type_dark.png")
    assert light[2, 2, :3].mean() > 0.9 and dark[2, 2, :3].mean() < 0.2


def test_group_sizes():
    g, dep = RES["dependence"]["group_sizes"], RES["dependence"]
    assert g == sorted(g, reverse=True)
    assert sum(g) == RES["strict"]["groups"]["All"]["agreements"] == 374
    assert len(g) == dep["linked_groups"] == 72
    assert max(g) == dep["largest_group"] == 34
    assert g.count(1) == dep["single_agreement_groups"] == 24
    assert round(100 * sum(x for x in g if x >= 5) / sum(g), 1) == dep["share_in_groups_of_5_or_more_pct"]
