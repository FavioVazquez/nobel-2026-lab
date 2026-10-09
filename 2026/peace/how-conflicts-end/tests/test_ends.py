"""Checks of the data, the counts, the README numbers and the figures. Educational demo, not research."""
import csv
import hashlib
import json
import re

import pytest
from matplotlib.image import imread

from ends import constants as C
from ends import model as M
from ends import run_all as R

HERE = C.HERE
RES = json.loads((HERE / "results" / "how_conflicts_end.json").read_text())
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
        out |= set(NUM.findall(str(obj)))  # unsigned, as the prose regex reads "-0.008" as "0.008"
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
        m = re.fullmatch(r"(.*?)\[(\d+)\]", part)
        v = v[m.group(1)][int(m.group(2))] if m else v[part]
    return v


def test_raw_sha256():
    if not C.RAW.exists():
        pytest.skip("raw file not fetched (python -m ends.fetch_data)")
    assert hashlib.sha256(C.RAW.read_bytes()).hexdigest() == C.DATA_SHA256


def test_derived_sha256_and_columns():
    assert hashlib.sha256(C.DERIVED.read_bytes()).hexdigest() == C.DERIVED_SHA256
    with open(C.DERIVED, newline="") as f:
        assert tuple(next(csv.reader(f))) == C.DERIVED_COLUMNS
    assert RES["dataset"]["sha256"] == C.DATA_SHA256


def test_derived_matches_raw():
    if not C.RAW.exists():
        pytest.skip("raw file not fetched")
    with open(C.RAW, newline="", encoding="utf-8") as f:
        raw = [{k: r[k] for k in C.DERIVED_COLUMNS} for r in csv.DictReader(f)]
    assert raw == M.load()


def test_category_totals_match_row_counts():
    rows = M.load()
    assert len(rows) == C.RAW_ROWS == RES["dataset"]["rows"]
    n_term = sum(r["c_epterm"] == "1" for r in rows)
    assert n_term == RES["terminations"] == RES["totals_sum"] == sum(RES["totals"].values())
    assert all(r["c_outcome"] in C.OUTCOMES for r in rows if r["c_epterm"] == "1")
    assert sum(p["episodes_ended"] for p in RES["by_decade"]) == n_term
    for name in C.OUTCOMES.values():
        assert sum(p["counts"][name] for p in RES["by_decade"]) == RES["totals"][name]
    for p in RES["by_decade"]:
        assert sum(p["counts"].values()) == p["episodes_ended"]
        assert sum(p["shares_pct"].values()) == pytest.approx(100, abs=0.3)
    assert RES["censoring"]["conflicts_active_in_last_year"] == sum(r["c_epterm"] == "" for r in rows)


def test_results_are_current():
    assert json.loads(json.dumps(R.summary(M.load()))) == RES


def test_hand_example():
    rows = [{"c_epid": "1", "year": "1946", "c_epterm": "0", "c_outcome": ""},
            {"c_epid": "1", "year": "1947", "c_epterm": "1", "c_outcome": "1"},
            {"c_epid": "2", "year": "1949", "c_epterm": "1", "c_outcome": "5"},
            {"c_epid": "3", "year": "1950", "c_epterm": "1", "c_outcome": "2"},
            {"c_epid": "4", "year": "2024", "c_epterm": "", "c_outcome": ""}]
    d = M.by_decade(rows)
    assert list(d) == [1940, 1950]
    assert d[1940] == {"1": 1, "2": 0, "3": 0, "4": 0, "5": 1, "6": 0}
    assert d[1950]["2"] == 1 and sum(d[1950].values()) == 1
    # Wilson 95 % for 3 of 10, by hand: centre (0.3 + z²/20)/(1 + z²/10) = 0.355507, half-width 0.247715
    lo, hi = M.wilson(3, 10)
    assert (lo, hi) == pytest.approx((0.107791, 0.603222), abs=1e-6)
    assert M.pct(3 / 10) == 30.0


def test_logistic_hand_example():
    # one 0/1 predictor: the slope is the log odds ratio and its se is sqrt(1/a + 1/b + 1/c + 1/d), by hand
    # x = 0: 3 events, 7 non-events; x = 1: 6 events, 4 non-events -> ln((6/4)/(3/7)) = ln 3.5 = 1.252763,
    # se = sqrt(1/3 + 1/7 + 1/6 + 1/4) = 0.944911
    x = [0] * 10 + [1] * 10
    y = [1] * 3 + [0] * 7 + [1] * 6 + [0] * 4
    b, se, _ = M.logistic([x], y)
    assert b[1] == pytest.approx(1.252763, abs=1e-6) and se[1] == pytest.approx(0.944911, abs=1e-6)
    assert M.normal_two_sided_p(1.959963984540054) == pytest.approx(0.05, abs=1e-9)
    assert M.chi2_1df_p(3.841458820694124) == pytest.approx(0.05, abs=1e-9)


def test_trend_fields_match_counts():
    T = RES["trends"]
    a = T["agreement_or_ceasefire_all_endings"]
    assert a["endings"] == RES["terminations"] and a["events"] == RES["agreement_or_ceasefire_all"]
    assert a["slope_ci95"][0] < a["slope_log_odds_per_decade"] < a["slope_ci95"][1]
    assert a["slope_ci95"][0] < 0 < a["slope_ci95"][1]  # the README's "no steady rise"
    c = T["agreement_or_ceasefire_among_clear_outcomes"]
    v = RES["second_view"]
    assert c["endings"] == v["clear_outcome_endings"] == sum(p["clear_outcome_endings"] for p in RES["by_decade"])
    assert c["events"] == v["agreement_or_ceasefire_among_clear"] == RES["agreement_or_ceasefire_all"]
    assert c["slope_ci95"][0] > 0 and c["p"] < T["p_floor"] and T["low_activity"]["p"] < T["p_floor"]
    assert T["peace_agreement_only"]["events"] + T["ceasefire_only"]["events"] == a["events"]
    assert T["low_activity"]["events"] == RES["totals"]["Low activity"]
    for p in RES["by_decade"]:
        assert p["clear_outcome_endings"] == sum(p["counts"][C.OUTCOMES[k]] for k in C.CLEAR)
    assert v["before_1990_max_pct"] < 50 < v["complete_decades_since_1990_min_pct"]  # INSIGHTS 4, "most common"


def test_reused_episode_ids_are_separate_episodes():
    assert RES["episodes"] == RES["terminations"] and RES["episode_ids_used_twice"] == 2
    ids = [r["c_epid"] for r in M.terminations(M.load())]
    assert len(set(ids)) == RES["terminations"] - RES["episode_ids_used_twice"]
    if not C.RAW.exists():
        pytest.skip("raw file not fetched")
    with open(C.RAW, newline="", encoding="utf-8") as f:
        ends = [r for r in csv.DictReader(f) if r["c_epterm"] == "1"]
    for i in {i for i in ids if ids.count(i) == 2}:
        assert len({r["c_ep_startyear"] for r in ends if r["c_epid"] == i}) == 2


def test_every_readme_number_is_in_the_json():
    have = tokens(RES)
    missing = sorted(set(NUM.findall(prose((HERE / "README.md").read_text()))) - have)
    assert not missing, missing


def test_insights_are_traced_to_json_fields():
    lines = [ln for ln in (HERE / "INSIGHTS.md").read_text().splitlines() if ln.startswith(("1.", "2.", "3.", "4.",
                                                                                              "5."))]
    assert 3 <= len(lines) <= 5
    for ln in lines:
        text, _, refs = ln[2:].partition("(fields:")
        paths = re.findall(r"`([^`]+)`", refs)
        assert paths, ln
        have = set().union(*(tokens(resolve(p)) for p in paths))
        assert set(NUM.findall(text)) <= have, (ln, set(NUM.findall(text)) - have)


@pytest.mark.parametrize("stem", ["ends_by_decade", "agreement_share"])
def test_figures_light_and_dark(stem):
    light = imread(HERE / "results" / f"{stem}_light.png")
    dark = imread(HERE / "results" / f"{stem}_dark.png")
    assert light[2, 2, :3].mean() > 0.9 and dark[2, 2, :3].mean() < 0.2


def test_ending_years_and_outcomes():
    years, outs = RES["ending_years"], RES["ending_outcomes_by_year"]
    assert len(years) == len(outs) == RES["terminations"] == 507
    assert years == sorted(years)
    assert RES["dataset"]["coded_years"][0] <= years[0] and years[-1] <= RES["dataset"]["coded_years"][1]
    assert set(outs) <= set(C.OUTCOMES.values())
    assert {o: outs.count(o) for o in RES["totals"]} == RES["totals"]
    for p in RES["by_decade"]:
        d = int(p["decade"][:4])
        assert sum(d <= y <= d + 9 for y in years) == p["episodes_ended"]
        assert {o: sum(1 for y, x in zip(years, outs) if d <= y <= d + 9 and x == o) for o in p["counts"]} == p["counts"]
