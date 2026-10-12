"""Checks of the data files, the regressions (against stored statsmodels results), the simulated control and the
results JSON. Educational demo, not research."""
import csv
import hashlib
import json

import numpy as np
import pytest

from spend import constants as C
from spend import fetch_data as D
from spend import model as M
from spend import run_all as R

RES = json.loads((C.RESULTS / C.RESULTS_JSON).read_text())
REF = json.loads((C.HERE / "tests" / "statsmodels_reference.json").read_text())
TOL = 1e-8


def data():
    qg, _, _, d = R.prepare("nds")
    return qg, d


# ---------- the data ----------

@pytest.mark.parametrize("sid", list(C.SERIES))
def test_raw_sha256(sid):
    assert hashlib.sha256(D.raw_path(sid).read_bytes()).hexdigest() == C.SERIES[sid]["sha256"]
    assert RES["data"]["series"][sid]["sha256"] == C.SERIES[sid]["sha256"]


def test_register_extract_and_bulk_pins():
    assert hashlib.sha256((C.RAW / C.REGISTER_EXTRACT).read_bytes()).hexdigest() == C.REGISTER_EXTRACT_SHA256
    reg = D.read_register()
    assert set(reg) == set(C.SERIES)
    for sid, m in C.SERIES.items():
        assert reg[sid]["SeriesLabel"] == m["title"] and reg[sid]["MetricName"] == m["metric"]
    assert "T20100:37" in reg["A067RX"]["TableId:LineNo"] and "T20100:40" in reg["B230RC"]["TableId:LineNo"]
    assert "T10106:2" in reg["DPCERX"]["TableId:LineNo"]
    for sid, m in C.SERIES.items():  # "Table 1.1.3. ..., line 5" -> T10103:5; "Table 2.1. ..., line 37" -> T20100:37
        num, line = m["table"].split(". ")[0].split()[1], m["table"].rsplit("line ", 1)[1]
        parts = [int(p) for p in num.split(".")] + [0]
        tid = "T%d%02d%02d" % tuple(parts[:3])
        assert "%s:%s" % (tid, line) in reg[sid]["TableId:LineNo"].split("|"), sid
    assert {m["role"] for m in C.SERIES.values()} == {"headline", "robustness", "check"}
    assert D.url("NipaDataQ.txt") == "https://apps.bea.gov/national/Release/TXT/NipaDataQ.txt"
    assert all(len(m["sha256"]) == 64 for m in C.BULK.values()) and C.VINTAGE["release_date"] == "2026-09-30"
    assert "data/raw/bea/" in (C.HERE / ".gitignore").read_text()  # the 35 MB bulk file is not committed


def test_extract_is_the_bulk_lines_when_the_bulk_files_are_here():
    bulk = C.BULK_DIR / "NipaDataQ.txt"
    if not bulk.exists():
        pytest.skip("BEA bulk files not downloaded (python -m spend.fetch_data --refresh)")
    if hashlib.sha256(bulk.read_bytes()).hexdigest() != C.BULK["NipaDataQ.txt"]["sha256"]:
        pytest.skip("a different BEA vintage is in data/raw/bea/")
    want = {sid: [] for sid in C.SERIES}
    with open(bulk, encoding="utf-8", newline="") as f:
        for line in f:
            sid = line.split(",", 1)[0]
            if sid in want:
                want[sid].append(line.rstrip("\r\n"))
    for sid, lines in want.items():
        assert D.raw_path(sid).read_text().splitlines()[1:] == lines


def test_derived_sha256_columns_and_rebuild():
    assert hashlib.sha256(C.DERIVED.read_bytes()).hexdigest() == C.DERIVED_SHA256 == RES["data"]["derived"]["sha256"]
    with open(C.DERIVED, newline="") as f:
        rows = list(csv.DictReader(f))
    assert tuple(rows[0]) == C.DERIVED_COLUMNS
    assert rows == D.derived_rows()  # the committed file is exactly what the raw files give


@pytest.mark.parametrize("sid", list(C.SERIES))
def test_series_lengths_and_dates(sid):
    rows = D.read_series(sid)
    m = C.SERIES[sid]
    assert len(rows) == m["rows"] == RES["data"]["series"][sid]["rows"]
    assert rows[0][0] == m["first"] and rows[-1][0] == C.END_QUARTER
    assert [q for q, _ in rows] == D.quarters_between(m["first"], C.END_QUARTER)  # in order, no gaps
    assert all(v > 0 for _, v in rows)


def test_sample_dates():
    q, _, _ = M.load()
    assert q[0] == C.FIRST_QUARTER == "1951Q4" and q[-1] == C.END_QUARTER == "2026Q2" and len(q) == 299
    assert q == D.quarters_between(q[0], q[-1])
    s = RES["sample"]
    assert s["growth_quarters"] == 298 and s["n"] == 294 and s["regression_quarters"] == ["1953Q1", "2026Q2"]
    assert s["split_year"] == C.SPLIT_YEAR
    assert s["halves"] == {"first": ["1953Q1", "1989Q4"], "second": ["1990Q1", "2026Q2"]}
    h = RES["hall"]
    assert h["first_half"]["n"] + h["second_half"]["n"] == h["full"]["n"] == 294
    assert abs(h["first_half"]["n"] - h["second_half"]["n"]) <= 2  # halves
    # Campbell and Mankiw's own window, 1953:1 to 1986:4 (136 quarters)
    assert RES["lambda"]["cm_window"]["quarters"] == ["1953Q1", "1986Q4"] and RES["lambda"]["cm_window"]["n"] == 136


def test_per_capita_by_hand():
    row = D.derived_rows()[0]  # 1951Q4: PCE 1,561,670 million, income 1,789,803 million, population 155,344 thousand
    assert row["quarter"] == "1951Q4" and row["pce_real"] == "1561.670" and row["dpi_real"] == "1789.803"
    assert row["population"] == "155344"
    assert float(row["log_pce_pc"]) == pytest.approx(np.log(1561670e6 / 155344e3), abs=1e-9)
    assert float(row["log_y_pc"]) == pytest.approx(np.log(1789803e6 / 155344e3), abs=1e-9)
    assert float(row["log_c_pc"]) == pytest.approx(np.log(float(row["nds_real"]) * 1e9 / 155344e3), abs=1e-6)


# ---------- the Fisher chain ----------

def _arr(sid):
    return np.array([v for _, v in D.read_series(sid)])


def _fisher_numpy(parts):
    """The Fisher relatives again, written with NumPy arrays (independent of fetch_data's loops)."""
    q = np.column_stack([_arr(a) for a, _ in parts])
    v = np.column_stack([_arr(b) for _, b in parts])
    r = q[1:] / q[:-1]
    lasp = (v[:-1] * r).sum(1) / v[:-1].sum(1)
    paas = v[1:].sum(1) / (v[1:] / r).sum(1)
    return np.sqrt(lasp * paas)


def test_fisher_chain_reproduces_bea_total_pce():
    """The same Fisher formula on durables, non-durables and services reproduces BEA's own total-PCE quantity index
    (DPCERA) to 1.8e-4 in quarterly log growth at most: the method behind our non-durables + services series."""
    rel = _fisher_numpy(C.FISHER_PARTS["pce_check"])
    bea = _arr("DPCERA")
    err = np.abs(np.log(rel) - np.diff(np.log(bea)))
    assert err.max() < C.FISHER_CHECK_TOL == 2e-4 and err.max() == pytest.approx(1.82e-4, abs=5e-7)
    assert np.median(err) < 3e-5  # rounding of the 3-decimal indexes, not a different formula
    chk = RES["data"]["fisher_check"]
    assert chk["passes"] and chk["max_abs_dlog"] == float("%.3g" % err.max()) and chk["at"] == "1955Q1"
    d = D.fisher_check()
    assert d["max_abs_dlog"] == pytest.approx(err.max(), abs=1e-15) and d["quarters"] == len(bea) - 1 == 317
    # a plain sum of the parts' quantity indexes would not do: it misses BEA's total by far more
    naive = np.diff(np.log(sum(_arr(a) for a, _ in C.FISHER_PARTS["pce_check"])))
    assert np.abs(naive - np.diff(np.log(bea))).max() > 50 * err.max()


def test_nds_series_is_the_fisher_chain_in_chained_2017_dollars():
    rel = _fisher_numpy(C.FISHER_PARTS["nds"])
    lev = D.fisher_level(C.FISHER_PARTS["nds"])
    quarters = [q for q, _ in D.read_series("DNDGRA")]
    np.testing.assert_allclose(np.diff(np.log([lev[q] for q in quarters])), np.log(rel), rtol=0, atol=1e-12)
    ref = [q for q in quarters if q.startswith(C.REFERENCE_YEAR)]
    nominal = dict(zip(quarters, _arr("DNDGRC") + _arr("DSERRC")))
    assert np.mean([lev[q] for q in ref]) == pytest.approx(np.mean([nominal[q] for q in ref]), rel=1e-12)
    rows = {r["quarter"]: r for r in D.derived_rows()}  # the derived CSV carries that level, in billions
    assert float(rows["2017Q2"]["nds_real"]) == pytest.approx(lev["2017Q2"] / 1e3, abs=5e-4)


# ---------- the regressions reproduce statsmodels ----------

def test_hall_regression_matches_statsmodels():
    _, d = data()
    h = M.hall_test(d["y"], d["x_hall"])
    r = REF["hall_full"]
    np.testing.assert_allclose(h["fit"]["b"], r["params"], rtol=0, atol=TOL)
    np.testing.assert_allclose(h["fit"]["se"], r["bse_hac"], rtol=0, atol=TOL)
    np.testing.assert_allclose(np.sqrt(np.diag(h["fit"]["cov_classic"])), r["bse_classic"], rtol=0, atol=TOL)
    assert abs(h["fit"]["r2"] - r["rsquared"]) < TOL and abs(h["fit"]["r2_adj"] - r["rsquared_adj"]) < TOL
    for mine, theirs in ((h["all_lags"], r["f_all_hac"]), (h["income_lags"], r["f_income_hac"])):
        assert abs(mine["F"] - theirs["F"]) < TOL and abs(mine["p"] - theirs["p"]) < TOL
        assert mine["df"][1] == theirs["df_denom"]


def test_iv_and_first_stage_match_statsmodels():
    _, d = data()
    iv = M.iv_lambda(d["y"], d["x_iv"], d["z_both"])
    np.testing.assert_allclose(iv["iv"]["b"], REF["iv_both"]["params"], rtol=0, atol=TOL)
    np.testing.assert_allclose(iv["iv"]["b"], REF["iv_both"]["two_step_params"], rtol=0, atol=TOL)
    np.testing.assert_allclose(np.sqrt(np.diag(iv["iv"]["cov_classic"])), REF["iv_both"]["bse_classic"], rtol=0,
                               atol=TOL)
    fs = REF["first_stage_both"]
    assert abs(iv["first_stage_F"] - fs["f_excluded_classic"]["F"]) < TOL
    assert abs(iv["first_stage_F_hac"] - fs["f_excluded_hac"]["F"]) < TOL
    assert abs(iv["first_stage_r2_adj"] - fs["rsquared_adj"]) < TOL
    assert RES["lambda"]["full"]["both"]["lambda"] == round(REF["iv_both"]["params"][1], 3)


def test_effective_f_matches_statsmodels_and_the_classic_f_when_homoskedastic():
    qg, d = data()
    pre = np.array(qg[C.LAGS:]) <= C.PRE_2020_END
    for name, m in (("full", np.ones(len(d["y"]), bool)), ("pre_2020", pre)):
        for z, want in zip(("z_both", "z_dy", "z_dc", "z_row8"), REF["effective_F"][name]):
            assert abs(M.effective_f(d["x_iv"][m, 1], d[z][m]) - want) < TOL, (name, z)
    key = {"z_both": "both", "z_dy": "income", "z_dc": "consumption", "z_row8": "row8"}
    for z, want in zip(key, REF["effective_F"]["full"]):
        assert RES["lambda"]["full"][key[z]]["effective_F"] == round(want, 2)
    # with the classic covariance in place of the HAC one, the effective F is the classic first-stage F
    first = M.ols(d["x_iv"][:, 1], d["z_both"])
    classic = {**first, "cov": first["cov_classic"]}
    assert M.effective_f(d["x_iv"][:, 1], d["z_both"], classic) == pytest.approx(
        M.wald_f(first, list(range(1, 7)), "cov_classic")["F"], rel=1e-10)


def test_f_distribution_matches_scipy():
    for f, d1, d2, p in REF["f_sf"]:
        assert abs(M.f_sf(f, d1, d2) - p) < 1e-12, (f, d1, d2)
    for a, d1, d2, f in REF["f_isf"]:
        assert abs(M.f_isf(a, d1, d2) - f) < 1e-9, (a, d1, d2)
    assert M.normal_two_sided_p(C.Z95) == pytest.approx(0.05, abs=1e-12)


def test_anderson_rubin_matches_statsmodels():
    qg, d = data()
    m = np.array(qg[C.LAGS:]) <= C.PRE_2020_END
    y, x, Z = d["y"][m], d["x_iv"][m, 1], d["z_both"][m]
    ar = M.anderson_rubin(y, x, Z)
    for lam0, f, p, f_classic in REF["anderson_rubin_pre_2020"]:
        i = int(round((lam0 - C.AR_GRID[0]) / C.AR_GRID[2]))
        assert ar["lams"][i] == pytest.approx(lam0, abs=1e-9)
        assert abs(ar["stat"][i] - f) < 1e-8 and abs(M.ar_f(y, x, Z, lam0)["F"] - f) < 1e-8
        assert abs(ar["stat_classic"][i] - f_classic) < 1e-8
        assert (f < ar["crit"]) == any(lo <= lam0 <= hi for lo, hi in ar["intervals"])
        assert (f_classic < ar["crit"]) == any(lo <= lam0 <= hi for lo, hi in ar["intervals_classic"])
    # the ends of the set are where the statistic crosses the critical value
    for lo, hi in ar["intervals"]:
        assert M.ar_f(y, x, Z, lo)["F"] < ar["crit"] < M.ar_f(y, x, Z, lo - C.AR_GRID[2])["F"]
        assert M.ar_f(y, x, Z, hi)["F"] < ar["crit"] < M.ar_f(y, x, Z, hi + C.AR_GRID[2])["F"]
    # far from the data the statistic tends to the HAC first-stage F (so the set is bounded when that F is large)
    assert M.ar_f(y, x, Z, 1e7)["F"] == pytest.approx(ar["limit_F"], rel=1e-5)


def test_hac_by_hand():
    """The Bartlett long-run covariance, written as the textbook double sum."""
    rng = np.random.default_rng(1)
    xu = rng.normal(size=(12, 2))
    L = 3
    want = np.zeros((2, 2))
    for t in range(12):
        for s in range(12):
            lag = abs(t - s)
            if lag <= L:
                want += (1 - lag / (L + 1)) * np.outer(xu[t], xu[s])
    np.testing.assert_allclose(M.hac_meat(xu, L), want, atol=1e-12)


def test_reference_is_current_if_statsmodels_is_installed():
    sm = pytest.importorskip("statsmodels.api")
    _, d = data()
    fit = sm.OLS(d["y"], d["x_hall"]).fit(cov_type="HAC", cov_kwds={"maxlags": C.HAC_LAGS, "use_correction": False})
    np.testing.assert_allclose(fit.params, REF["hall_full"]["params"], rtol=0, atol=1e-12)
    np.testing.assert_allclose(fit.bse, REF["hall_full"]["bse_hac"], rtol=0, atol=1e-12)


# ---------- results ----------

def test_results_are_current():
    assert json.loads(json.dumps(R.summary())) == RES


def test_hall_fields():
    h = RES["hall"]
    for k in ("full", "first_half", "second_half", "pre_2020"):
        x = h[k]
        assert 0 <= x["r2_adj_pct"] < x["r2_pct"] < 100
        assert x["df_all"] == [8, x["n"] - 9] and x["df_income"] == [4, x["n"] - 9]
        assert len(x["coef"]) == len(x["se_hac"]) == 9
        assert x["lags_2_4"]["r2_pct"] < x["r2_pct"]
    assert h["pre_2020"]["lags_2_4"]["p"] < h["p_floor"] < h["full"]["lags_2_4"]["p"] < 0.01  # README wording
    # on non-durables + services the four income lags do not predict spending before 2020 (as in Hall 1978); on
    # total PCE they do (the robustness rows)
    rob = RES["robustness_total_pce"]["hall"]
    assert h["pre_2020"]["p_income_lags"] > 0.1 and rob["pre_2020"]["p_income_lags"] < 0.01
    assert set(rob) == set(h) - {"series", "time_aggregation", "hall_1978", "plain"}
    assert h["hall_1978"]["income_test_F"] < h["hall_1978"]["income_test_crit_5pct"]
    ser = h["series"]
    assert len(ser["quarters"]) == len(ser["dc_pct"]) == len(ser["fitted_lags_1_4_full_pct"]) == 294
    assert len(ser["fitted_lags_2_4_pre_2020_pct"]) == h["pre_2020"]["n"] == 268
    assert h["out_of_sample"]["from"] == "1990Q1"
    o = h["out_of_sample"]
    assert o["full_r2_pct"] < 0 < o["pre_2020_r2_pct"] and o["lags_2_4_full_r2_pct"] < 0 < o["lags_2_4_pre_2020_r2_pct"]
    assert o["mean_dc_pct_after_to_2019"] < o["mean_dc_pct_before"]  # README: the benchmark lags behind


SETS = ("both", "income", "consumption", "row8")


def test_lambda_fields_and_published_values():
    for L in (RES["lambda"], RES["robustness_total_pce"]["lambda"]):
        for k in ("full", "first_half", "second_half", "pre_2020", "cm_window"):
            for z in SETS:
                e = L[k][z]
                assert e["ci95"][0] < e["lambda"] < e["ci95"][1]
                # instruments count as strong only if the effective F is above 10 (not the classic F)
                assert e["weak"] == (not e["effective_F"] > C.WEAK_F) == (not e["effective_F_above_10"])
                assert e["passes_mop_tau10"] == (e["effective_F"] > C.MOP_CRIT_TAU10)
                assert e["instruments"] == {"both": 6, "row8": 7}.get(z, 3)
                a = e["anderson_rubin"]
                assert a["empty"] == (not a["set95"]) and a["df"][0] == e["instruments"]
                assert a["contains_2sls"] == any(lo <= e["lambda"] <= hi for lo, hi in a["set95"])
                assert a["empty"] == (a["min_F"] >= a["crit_F"])
                assert a["exceeds_1"] == any(hi > 1 for _, hi in a["set95"])
                assert a["classic_empty"] == (not a["classic_set95"])
    L = RES["lambda"]
    rows = L["published"]["rows"]
    assert [rows[k]["lambda"] for k in "123456789"] == [0.316, 0.417, 0.506, 0.419, 0.523, 0.698, 0.584, 0.351,
                                                        0.469]
    assert L["published"]["iv_range"] == [0.351, 0.698] and L["published"]["page"] == 192
    assert [c["their_row"] for c in L["comparison"]] == ["2", "4", "8"]
    assert [c["our_lambda"] for c in L["comparison"]] == [L["cm_window"][z]["lambda"] for z in ("income",
                                                                                                 "consumption", "row8")]
    # README: in every sample that ends before 2020 the instruments are weak by every F we report
    for k in ("first_half", "pre_2020", "cm_window"):
        for z in SETS:
            e = L[k][z]
            assert e["weak"] and max(e["first_stage_F"], e["first_stage_F_hac"], e["effective_F"]) < C.WEAK_F, (k, z)
    # README: with 2020-2026 the classic F says strong, the robust ones much less so; nothing passes the 23.11 test
    # except in the second half; income lags alone are weak in every sample
    full = L["full"]["both"]
    assert full["first_stage_F"] > C.WEAK_F and full["effective_F"] < full["first_stage_F"]
    assert not any(L["full"][z]["passes_mop_tau10"] for z in SETS)
    assert L["second_half"]["both"]["passes_mop_tau10"] and L["second_half"]["consumption"]["passes_mop_tau10"]
    assert all(L[k]["income"]["weak"] for k in ("full", "first_half", "second_half", "pre_2020", "cm_window"))
    assert L["full"]["both"]["anderson_rubin"]["empty"] and not L["full"]["both"]["anderson_rubin"]["classic_empty"]


def test_control_recovers_lambda_within_its_ci():
    ex = RES["control"]["example"]
    assert ex["covered"] and ex["ci95"][0] <= C.SIM["lambda"] <= ex["ci95"][1]
    assert ex["first_stage_F"] > C.WEAK_F and ex["p_all_lags"] < 0.001
    cs = RES["control"]["cases"]
    s = cs["hand_to_mouth"]
    assert abs(s["median_lambda"] - C.SIM["lambda"]) < 0.02 and 92 <= s["ci95_coverage_pct"] <= 97
    assert s["hall_reject_pct"] > 95
    assert abs(cs["random_walk"]["median_lambda"]) < 0.02
    # what the test cannot do: with weak instruments the interval misses the truth far more than 5 % of the time
    assert cs["hand_to_mouth_weak"]["ci95_coverage_pct"] < 80 and cs["random_walk_weak"]["ci95_coverage_pct"] < 80
    assert cs["random_walk_weak"]["median_lambda"] > 0.2  # a share that is not there
    # the Anderson-Rubin set holds the truth about as often whether the instruments are strong or weak, but less
    # than 95 % of the time: its HAC F test over-rejects in samples this size (README)
    ar = [c["ar_coverage_pct"] for c in cs.values()]
    assert 80 < min(ar) <= max(ar) < 95 and max(ar) - min(ar) < 5
    for c in cs.values():
        assert sum(c["lambda_hist"]) <= c["reps"] and c["reps"] == C.SIM["reps"]


def test_simulated_random_walk_is_unpredictable_by_hand():
    rng = np.random.default_rng(5)
    dc, dy = M.simulate(rng, 4000, 0.0, 0.8)
    # with no hand-to-mouth households, consumption growth = drift + news: no autocorrelation to speak of
    # (standard error about 0.016 for 4000 quarters), while income growth is persistent
    assert abs(np.corrcoef(dc[1:], dc[:-1])[0, 1]) < 0.05 < 0.7 < np.corrcoef(dy[1:], dy[:-1])[0, 1]
    assert dc.mean() == pytest.approx(C.SIM["growth"], abs=0.001)


def test_guess_answers():
    g, h, L = RES["guess"], RES["hall"], RES["lambda"]
    a = g["a"]
    assert a["answer_pct"] == h["pre_2020"]["lags_2_4"]["r2_pct"] and 0 <= a["answer_pct"] <= 100
    assert a["quarters"] == ["1953Q1", "2019Q4"] and a["full_sample_pct"] == h["full"]["lags_2_4"]["r2_pct"]
    assert a["secondary_lags_1_4_pct"] == h["pre_2020"]["r2_pct"] and a["why_lags_2_4"] == C.TIME_AGGREGATION
    assert "Working 1960" in a["why_lags_2_4"] and "2020-2021" in a["why_to_2019"]
    for cause in ("lockdown", "relief", "stimulus", "pandemic polic"):  # no unsourced cause in our voice
        assert cause not in a["why_to_2019"].lower()
    rob = RES["robustness_total_pce"]["hall"]["pre_2020"]
    assert a["total_pce_pct"] == rob["lags_2_4"]["r2_pct"] and a["income_lags_p"] == h["pre_2020"]["p_income_lags"]
    b = g["b"]
    pub, ours = b["published"], b["ours"]
    assert list(b) == ["question", "reads_as", "published", "ours"]  # the published benchmarks come first
    assert pub["campbell_mankiw_about_pct"] == 50 and "50 percent" in pub["campbell_mankiw_quote"]
    assert pub["campbell_mankiw_table1_iv_range"] == L["published"]["iv_range"]
    assert pub["hall_mishkin_pct"] == 20 and "20%" in pub["hall_mishkin_quote"]
    assert "answer_pct" not in ours and "lambda" not in ours  # no single point as the headline
    pre, full = L["pre_2020"]["both"], L["full"]["both"]
    assert ours["ci95_pct"] == pre["ci95_pct"] and ours["first_stage_F"] == pre["first_stage_F"] < C.WEAK_F
    assert ours["effective_F"] == pre["effective_F"] < C.WEAK_F and not ours["effective_F_above_10"]
    assert ours["first_stage_F_hac"] == pre["first_stage_F_hac"]
    assert ours["anderson_rubin_set95_pct"] == pre["anderson_rubin"]["set95_pct"]
    assert ours["anderson_rubin_exceeds_100"] and ours["share_above_100_impossible"]  # INSIGHTS 4 says so
    assert ours["with_2020_2026_effective_F"] == full["effective_F"] < C.MOP_CRIT_TAU10
    assert ours["with_2020_2026_first_stage_F_hac"] == full["first_stage_F_hac"]
    assert not ours["with_2020_2026_passes_mop_tau10"] and ours["with_2020_2026_anderson_rubin_empty"]
    assert ours["total_pce_ci95_pct"] == RES["robustness_total_pce"]["lambda"]["pre_2020"]["both"]["ci95_pct"]


def test_hall_quote_and_lambda_quote():
    assert "\u03bb" in C.CM_TABLE1["about_half"] and "estimates of A" not in C.CM_TABLE1["about_half"]
    assert C.CM_TABLE1["about_half"] == RES["lambda"]["published"]["about_half"]
    assert C.HALL_1978["income_test_page"] == 982 and "levels" in C.HALL_1978["income_test"]
