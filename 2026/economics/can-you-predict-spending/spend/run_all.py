"""Run everything: python -m spend.run_all (from 2026/economics/can-you-predict-spending/). Writes results/."""
import argparse
import json

import numpy as np

from . import constants as C
from . import fetch_data as D
from . import model as M


def r(x, nd=3):
    return round(float(x), nd)


def sig(x, n=3):
    """p-values: three significant figures (they can be tiny)."""
    return float("%.*g" % (n, float(x)))


def pct(x, nd=1):
    return round(100 * float(x), nd)


def data_block():
    q, _, _ = M.load()
    reg = D.read_register()
    series = {}
    for sid, m in C.SERIES.items():
        rows = D.read_series(sid)
        series[sid] = {"title": m["title"], "metric": m["metric"], "units": m["units"], "frequency": "quarterly",
                       "table": m["table"], "role": m["role"], "register": reg[sid],
                       "file": "data/raw/%s.csv" % sid, "sha256": m["sha256"], "rows": len(rows),
                       "first": rows[0][0], "last": rows[-1][0]}
    chk = D.fisher_check()
    return {
        "series": series,
        "source": C.SOURCE_CREDIT, "downloaded": C.DOWNLOADED, "end_quarter": C.END_QUARTER,
        "vintage": C.VINTAGE,
        "bulk": {name: {**m, "url": D.url(name), "committed": False} for name, m in C.BULK.items()},
        "register_extract": {"file": "data/raw/" + C.REGISTER_EXTRACT, "sha256": C.REGISTER_EXTRACT_SHA256},
        "licence": {"bea_url": C.BEA_URL, "bea_faq": C.BEA_FAQ_TITLE, "bea_line": C.BEA_LINE},
        "derived": {"file": "data/quarterly.csv", "sha256": C.DERIVED_SHA256, "quarters": len(q), "first": q[0],
                    "last": q[-1], "columns": list(C.DERIVED_COLUMNS)},
        "fisher": {"formula": C.FISHER_FORMULA, "parts": {k: [list(p) for p in v] for k, v in C.FISHER_PARTS.items()},
                   "reference_year": C.REFERENCE_YEAR},
        "fisher_check": {**chk, "max_abs_dlog": sig(chk["max_abs_dlog"]), "mean_abs_dlog": sig(chk["mean_abs_dlog"]),
                         "passes": chk["max_abs_dlog"] < C.FISHER_CHECK_TOL},
        "choices": {
            "consumption": "real spending on non-durable goods and services, Fisher-chained from BEA's quantity "
                           "indexes DNDGRA and DSERRA with the current-dollar values DNDGRC and DSERRC (chained 2017 "
                           "dollars)",
            "why_nds": C.WHY_NDS,
            "robustness": "total real personal consumption expenditures (DPCERX), which includes durable goods",
            "income": "real disposable personal income (A067RX), quarterly",
            "population": "B230RC, quarterly",
            "why_population": C.WHY_POPULATION,
            "start": C.FIRST_QUARTER,
            "why_start": C.WHY_START,
            "chained_2017_check": C.CHAINED_2017_CHECK,
            "per_capita": "chained 2017 dollars per person (annual rate); growth = 100 x change in the log, "
                          "in log points (about per cent)",
        },
    }


def sample_masks(rq):
    qa = np.array(rq)
    yr = np.array([int(x[:4]) for x in rq])
    return {
        "full": np.ones(len(rq), bool),
        "first_half": yr < C.SPLIT_YEAR,
        "second_half": yr >= C.SPLIT_YEAR,
        "pre_2020": qa <= C.PRE_2020_END,
        "cm_window": qa <= C.CM_SAMPLE_END,
    }


def _span(rq, mask):
    sel = [x for x, m in zip(rq, mask) if m]
    return [sel[0], sel[-1]]


HALL_SAMPLES = ("full", "first_half", "second_half", "pre_2020")


def hall_block(d, rq, masks, with_series=True):
    out = {}
    for name in HALL_SAMPLES:
        m = masks[name]
        h = M.hall_test(d["y"][m], d["x_hall"][m])
        f = h["fit"]
        out[name] = {
            "quarters": _span(rq, m), "n": f["n"], "r2_pct": pct(f["r2"]), "r2_adj_pct": pct(f["r2_adj"]),
            "p_all_lags": sig(h["all_lags"]["p"]), "F_all_lags": r(h["all_lags"]["F"], 2),
            "p_income_lags": sig(h["income_lags"]["p"]), "F_income_lags": r(h["income_lags"]["F"], 2),
            "p_consumption_lags": sig(h["consumption_lags"]["p"]),
            "F_consumption_lags": r(h["consumption_lags"]["F"], 2), "df_all": h["all_lags"]["df"],
            "df_income": h["income_lags"]["df"],
            "coef": [r(v, 4) for v in f["b"]], "se_hac": [r(v, 4) for v in f["se"]],
        }
        # the same test with lags 2-4 only (the first lag is not a fair test if quarterly averages are measured)
        g = M.ols(d["y"][m], d["z_both"][m])
        w = M.wald_f(g, list(range(1, d["z_both"].shape[1])))
        out[name]["lags_2_4"] = {"r2_pct": pct(g["r2"]), "r2_adj_pct": pct(g["r2_adj"]), "p": sig(w["p"]),
                                 "F": r(w["F"], 2)}
    pre = masks["pre_2020"]
    full_start = int(masks["first_half"].sum())
    pre_start = int((masks["first_half"] & pre).sum())
    before, after = 100 * d["y"][:full_start].mean(), 100 * d["y"][pre][pre_start:].mean()
    out["out_of_sample"] = {
        "method": "each quarter from %d on is predicted by the regression fitted on all earlier quarters; R^2 "
                  "against the mean of all earlier quarters (negative = worse than that mean)" % C.SPLIT_YEAR,
        "from": rq[full_start],
        "full_r2_pct": pct(M.oos_r2(d["y"], d["x_hall"], full_start)),
        "pre_2020_r2_pct": pct(M.oos_r2(d["y"][pre], d["x_hall"][pre], pre_start)),
        "lags_2_4_full_r2_pct": pct(M.oos_r2(d["y"], d["z_both"], full_start)),
        "lags_2_4_pre_2020_r2_pct": pct(M.oos_r2(d["y"][pre], d["z_both"][pre], pre_start)),
        "mean_dc_pct_before": r(before, 2),
        "mean_dc_pct_after_to_2019": r(after, 2),
        "benchmark_note": ("the benchmark is the average of all earlier quarters; average growth was %s after %d "
                           "than before" % ("lower" if after < before else "higher", C.SPLIT_YEAR)),
    }
    out["p_floor"] = C.P_FLOOR
    if not with_series:
        return out
    p24, f24 = out["pre_2020"], out["full"]
    out["time_aggregation"] = C.TIME_AGGREGATION
    out["hall_1978"] = C.HALL_1978
    out["plain"] = ("Using spending and income growth from two to four quarters back, a regression explains %.1f %% of "
                    "the quarter-to-quarter changes in US spending per person on non-durables and services, %s to %s "
                    "(in-sample; %.1f %% adjusted for the number of lags), and %.1f %% for %s to %s. With the most "
                    "recent quarter added (lags 1-4) the shares are %.1f %% and %.1f %%, but part of that is the "
                    "averaging within quarters." % (
                        p24["lags_2_4"]["r2_pct"], p24["quarters"][0], p24["quarters"][1],
                        p24["lags_2_4"]["r2_adj_pct"], f24["lags_2_4"]["r2_pct"], f24["quarters"][0],
                        f24["quarters"][1], p24["r2_pct"], f24["r2_pct"]))
    full = M.hall_test(d["y"], d["x_hall"])["fit"]
    g24 = M.ols(d["y"][pre], d["z_both"][pre])
    out["series"] = {"quarters": list(rq), "dc_pct": [r(100 * v, 3) for v in d["y"]],
                     "fitted_lags_1_4_full_pct": [r(100 * v, 3) for v in d["y"] - full["resid"]],
                     "fitted_lags_2_4_pre_2020_pct": [r(100 * v, 3) for v in d["y"][pre] - g24["resid"]]}
    return out


IV_SETS = {"both": "z_both", "income": "z_dy", "consumption": "z_dc", "row8": "z_row8"}
IV_NAMES = {"both": "income and consumption growth, lags 2-4", "income": "income growth, lags 2-4",
            "consumption": "consumption growth, lags 2-4",
            "row8": "income and consumption growth, lags 2-4, plus log(c / y) lagged two quarters"}
LAMBDA_SAMPLES = ("full", "first_half", "second_half", "pre_2020", "cm_window")


def _intervals(runs, f=r):
    return [[f(lo), f(hi)] for lo, hi in runs]


def lambda_block(d, rq, masks, with_published=True):
    out = {"instrument_sets": IV_NAMES, "hac_lags": C.HAC_LAGS, "weak_F_rule": C.WEAK_F,
           "strong_rule": C.STRONG_RULE, "mop_critical_value_tau10": C.MOP_CRIT_TAU10}
    for name in LAMBDA_SAMPLES:
        m = masks[name]
        ols = M.ols(d["y"][m], d["x_iv"][m])
        res = {"quarters": _span(rq, m), "n": int(m.sum()),
               "ols": {"lambda": r(ols["b"][1]), "se_hac": r(ols["se"][1])}}
        for key, z in IV_SETS.items():
            iv = M.iv_lambda(d["y"][m], d["x_iv"][m], d[z][m])
            res[key] = {"lambda": r(iv["lambda"]), "se_hac": r(iv["se"]), "ci95": [r(v) for v in iv["ci95"]],
                        "lambda_pct": pct(iv["lambda"]), "ci95_pct": [pct(v) for v in iv["ci95"]],
                        "p_lambda_zero": sig(iv["p_lambda_zero"]), "first_stage_F": r(iv["first_stage_F"], 2),
                        "first_stage_F_hac": r(iv["first_stage_F_hac"], 2), "effective_F": r(iv["effective_F"], 2),
                        "effective_F_above_10": bool(iv["strong"]), "weak": not iv["strong"],
                        "passes_mop_tau10": bool(iv["effective_F"] > C.MOP_CRIT_TAU10),
                        "first_stage_r2_adj_pct": pct(iv["first_stage_r2_adj"]), "instruments": iv["instruments"]}
            ar = M.anderson_rubin(d["y"][m], d["x_iv"][m, 1], d[z][m])
            g = int(np.argmin(ar["stat"]))
            res[key]["anderson_rubin"] = {
                "set95": _intervals(ar["intervals"]), "set95_pct": _intervals(ar["intervals"], pct),
                "empty": not ar["intervals"], "bounded": ar["bounded"],
                "open_at_grid_end": bool(ar["intervals"] and (ar["intervals"][0][0] <= ar["grid"][0]
                                                              or ar["intervals"][-1][1] >= ar["grid"][1])),
                "contains_2sls": any(lo <= iv["lambda"] <= hi for lo, hi in ar["intervals"]),
                "exceeds_1": any(hi > 1 for _, hi in ar["intervals"]),
                "crit_F": r(ar["crit"], 3), "df": ar["df"], "min_F": r(float(ar["stat"][g]), 2),
                "min_at": r(float(ar["lams"][g])), "limit_F": r(ar["limit_F"], 2),
                "classic_set95": _intervals(ar["intervals_classic"]),
                "classic_set95_pct": _intervals(ar["intervals_classic"], pct),
                "classic_empty": not ar["intervals_classic"], "classic_bounded": ar["bounded_classic"]}
        out[name] = res
    out["anderson_rubin"] = C.AR_NOTE
    if not with_published:
        return out
    t = C.CM_TABLE1
    out["published"] = {k: v for k, v in t.items() if k != "rows"}
    out["published"]["rows"] = {k: {**v, "ci95": [r(v["lambda"] - C.Z95 * v["se"]), r(v["lambda"] + C.Z95 * v["se"])]}
                                for k, v in t["rows"].items()}
    out["published"]["url"] = C.CM_URL
    iv_l = [t["rows"][k]["lambda"] for k in t["iv_rows"]]
    out["published"]["iv_range"] = [min(iv_l), max(iv_l)]
    out["published"]["iv_range_pct"] = [pct(min(iv_l)), pct(max(iv_l))]
    cm = out["cm_window"]
    out["comparison"] = [
        {"instruments": IV_NAMES[key], "their_row": row, "their_sample": t["sample"],
         "their_lambda": t["rows"][row]["lambda"], "their_se": t["rows"][row]["se"],
         "our_sample": cm["quarters"], "our_lambda": cm[key]["lambda"], "our_se": cm[key]["se_hac"],
         "our_ci95": cm[key]["ci95"], "our_first_stage_F": cm[key]["first_stage_F"],
         "our_effective_F": cm[key]["effective_F"]}
        for key, row in (("income", "2"), ("consumption", "4"), ("row8", "8"))]
    out["comparison_note"] = ("same window (1953:1 to 1986:4), same consumption concept (non-durables and services) "
                              "and the same instruments as their rows 2, 4 and 8; their data are the 1989 vintage in "
                              "1982 dollars, ours BEA's release of 30 September 2026, Fisher-chained in 2017 "
                              "dollars, and their standard errors are not computed the way ours are")
    return out


def pandemic_block(qg, dc, dy, dc_pce):
    keep = ("2020Q1", "2020Q2", "2020Q3", "2020Q4", "2021Q1", "2021Q2")
    idx = {x: i for i, x in enumerate(qg)}
    end = list(qg).index(C.PRE_2020_END) + 1
    first = 0  # every growth rate from the first one (1952Q1) to 2019Q4
    sd_dc, sd_dy = (100 * v[first:end].std(ddof=1) for v in (dc, dy))
    return {"quarters": {x: {"dc_pct": r(100 * dc[idx[x]], 1), "dy_pct": r(100 * dy[idx[x]], 1),
                             "dc_change_pct": pct(np.expm1(dc[idx[x]])), "dy_change_pct": pct(np.expm1(dy[idx[x]])),
                             "dc_total_pce_pct": r(100 * dc_pce[idx[x]], 1)}
                         for x in keep},
            "sd_quarters": [qg[first], C.PRE_2020_END], "sd_dc_pct_before_2020": r(sd_dc, 2),
            "sd_dy_pct_before_2020": r(sd_dy, 2),
            "note": "dc_pct, dy_pct: growth in log points (about per cent) from the previous quarter, per person "
                    "(dc: non-durables and services; dc_total_pce: total PCE); *_change_pct: the same change in "
                    "per cent; sd_*: standard deviation of quarterly growth over sd_quarters"}


def control_block(n_growth):
    p = C.SIM
    rng = np.random.default_rng(p["seed"])
    cases = {"hand_to_mouth": (p["lambda"], p["rho"]), "random_walk": (0.0, p["rho"]),
             "hand_to_mouth_weak": (p["lambda"], p["rho_weak"]), "random_walk_weak": (0.0, p["rho_weak"])}
    dc, dy = M.simulate(rng, n_growth, p["lambda"], p["rho"])
    d = M.design(dc, dy)
    h = M.hall_test(d["y"], d["x_hall"])
    iv = M.iv_lambda(d["y"], d["x_iv"], d["z_both"])
    ols = M.ols(d["y"], d["x_iv"])
    out = {"params": dict(p), "n_growth_quarters": n_growth, "n_regression": int(len(d["y"])),
           "example": {"lambda_true": p["lambda"], "lambda": r(iv["lambda"]), "ci95": [r(v) for v in iv["ci95"]],
                       "first_stage_F": r(iv["first_stage_F"], 2), "effective_F": r(iv["effective_F"], 2),
                       "ols_lambda": r(ols["b"][1]),
                       "r2_pct": pct(h["fit"]["r2"]), "p_all_lags": sig(h["all_lags"]["p"]),
                       "p_income_lags": sig(h["income_lags"]["p"]),
                       "covered": bool(iv["ci95"][0] <= p["lambda"] <= iv["ci95"][1])},
           "cases": {}}
    for name, (lam, rho) in cases.items():
        o = M.sim_case(rng, n_growth, lam, rho, p["reps"])
        n = p["reps"]
        lam_hat = np.array(o["lambda"])
        out["cases"][name] = {
            "lambda_true": lam, "rho": rho, "reps": n,
            "hall_reject_pct": pct(o["hall_reject"] / n), "income_lags_reject_pct": pct(o["income_reject"] / n),
            "median_r2_pct": pct(np.median(o["r2"])), "median_r2_lags_2_4_pct": pct(np.median(o["r2_lags_2_4"])),
            "ar_coverage_pct": pct(o["ar_covered"] / n),
            "median_lambda": r(np.median(lam_hat)), "lambda_p5": r(np.percentile(lam_hat, 5)),
            "lambda_p95": r(np.percentile(lam_hat, 95)), "ci95_coverage_pct": pct(o["covered"] / n),
            "median_first_stage_F": r(np.median(o["F"]), 1), "median_effective_F": r(np.median(o["F_eff"]), 1),
            "weak_pct": pct(o["weak"] / n),
            "median_ci_width": r(np.median(o["ci_width"])),
            "lambda_hist": np.histogram(lam_hat, bins=C.HIST_BINS)[0].tolist(),
        }
    out["hist_bins"] = [r(v, 2) for v in C.HIST_BINS]
    out["test_level_pct"] = 5
    return out


def robustness_block(hall, lam):
    """Total PCE (durables included) through the same tests; the headline is non-durables + services."""
    return {"consumption": "total real personal consumption expenditures (DPCERX), which includes durable goods",
            "hall": hall, "lambda": lam}


def guess_block(hall, lam, pan, rob):
    p24, pre_b, full_b = hall["pre_2020"], lam["pre_2020"]["both"], lam["full"]["both"]
    t, hm, q2 = C.CM_TABLE1, C.COMMITTEE, pan["quarters"]["2020Q2"]
    ar, far = pre_b["anderson_rubin"], full_b["anderson_rubin"]
    rh, rl = rob["hall"]["pre_2020"], rob["lambda"]["pre_2020"]["both"]
    return {
        "a": {"question": "From the last year of data, how much of next quarter's change in US consumer spending "
                          "can be predicted? (0-100 %)",
              "reads_as": "predictors = spending and income growth per person two to four quarters back; share of "
                          "the variance of next quarter's growth in spending on non-durables and services explained "
                          "(R^2, in-sample)",
              "answer_pct": p24["lags_2_4"]["r2_pct"], "quarters": p24["quarters"],
              "adjusted_pct": p24["lags_2_4"]["r2_adj_pct"], "p": p24["lags_2_4"]["p"],
              "full_sample_pct": hall["full"]["lags_2_4"]["r2_pct"], "full_sample_quarters": hall["full"]["quarters"],
              "full_sample_p": hall["full"]["lags_2_4"]["p"],
              "out_of_sample_pct": hall["out_of_sample"]["lags_2_4_pre_2020_r2_pct"],
              "out_of_sample_full_pct": hall["out_of_sample"]["lags_2_4_full_r2_pct"],
              "secondary_lags_1_4_pct": p24["r2_pct"], "secondary_lags_1_4_full_pct": hall["full"]["r2_pct"],
              "income_lags_p": p24["p_income_lags"],
              "total_pce_pct": rh["lags_2_4"]["r2_pct"], "total_pce_p": rh["lags_2_4"]["p"],
              "total_pce_income_lags_p": rh["p_income_lags"],
              "why_lags_2_4": C.TIME_AGGREGATION,
              "why_to_2019": ("2020-2021 are left out because in those quarters spending and income per person moved "
                              "by many times their usual quarterly change, often in opposite directions (%s: "
                              "spending %+.1f, income %+.1f log points; before 2020 the standard deviation of "
                              "quarterly growth was %.2f for spending and %.2f for income), so a few quarters "
                              "dominate the fit; with lags they also reach into the following quarters, so the "
                              "sample stops at %s. The full sample is reported next to it." % (
                                  "2020Q2", q2["dc_pct"], q2["dy_pct"], pan["sd_dc_pct_before_2020"],
                                  pan["sd_dy_pct_before_2020"], C.PRE_2020_END)),
              "hall_benchmark_pct": 0},
        "b": {"question": "What share of income goes to households who spend as they earn?",
              "reads_as": "Campbell and Mankiw's lambda: the instrumental-variables slope of consumption growth on "
                          "income growth (aggregate data)",
              "published": {
                  "campbell_mankiw_about_pct": 50, "campbell_mankiw_quote": t["conclusion"],
                  "campbell_mankiw_page": t["conclusion_page"],
                  "campbell_mankiw_table1_iv_range": lam["published"]["iv_range"], "campbell_mankiw_table1_page": t["page"],
                  "campbell_mankiw_sample": t["sample"],
                  "hall_mishkin_pct": hm["sb_hall_mishkin_pct"], "hall_mishkin_quote": hm["sb_hall_mishkin"],
                  "hall_mishkin_source": hm["sb_source"], "hall_mishkin_sample": hm["sb_hall_mishkin_sample"]},
              "ours": {
                  "headline": "very uncertain on these data",
                  "quarters": lam["pre_2020"]["quarters"], "instruments": IV_NAMES["both"],
                  "ci95_pct": pre_b["ci95_pct"], "first_stage_F": pre_b["first_stage_F"],
                  "first_stage_F_hac": pre_b["first_stage_F_hac"], "effective_F": pre_b["effective_F"],
                  "effective_F_above_10": pre_b["effective_F_above_10"], "weak_F_rule": C.WEAK_F,
                  "strong_rule": C.STRONG_RULE,
                  "anderson_rubin_set95_pct": ar["set95_pct"], "anderson_rubin_contains_2sls": ar["contains_2sls"],
                  "anderson_rubin_classic_set95_pct": ar["classic_set95_pct"],
                  "anderson_rubin_exceeds_100": ar["exceeds_1"],
                  "share_above_100_impossible": True, "share_max_pct": 100,
                  "with_2020_2026_quarters": lam["full"]["quarters"],
                  "with_2020_2026_ci95_pct": full_b["ci95_pct"],
                  "with_2020_2026_first_stage_F": full_b["first_stage_F"],
                  "with_2020_2026_first_stage_F_hac": full_b["first_stage_F_hac"],
                  "with_2020_2026_effective_F": full_b["effective_F"],
                  "with_2020_2026_effective_F_above_10": full_b["effective_F_above_10"],
                  "with_2020_2026_passes_mop_tau10": full_b["passes_mop_tau10"],
                  "mop_critical_value_tau10": C.MOP_CRIT_TAU10,
                  "with_2020_2026_anderson_rubin_empty": far["empty"],
                  "with_2020_2026_anderson_rubin_classic_set95_pct": far["classic_set95_pct"],
                  "total_pce_ci95_pct": rl["ci95_pct"], "total_pce_effective_F": rl["effective_F"],
                  "no_point_headline": "the point estimate is in lambda.pre_2020.both; it is not a headline here"}},
    }


def prepare(consumption):
    q, lc, ly = M.load(consumption)
    qg, dc, dy = M.growth(q, lc, ly)
    return qg, dc, dy, M.design(dc, dy, M.log_ratio(lc, ly))


def summary():
    qg, dc, dy, d = prepare("nds")
    _, dc_pce, _, d_pce = prepare("pce")
    rq = qg[C.LAGS:]
    masks = sample_masks(rq)
    hall = hall_block(d, rq, masks)
    lam = lambda_block(d, rq, masks)
    rob = robustness_block(hall_block(d_pce, rq, masks, with_series=False),
                           lambda_block(d_pce, rq, masks, with_published=False))
    pan = pandemic_block(qg, dc, dy, dc_pce)
    return {
        "label": C.LABEL, "prize": C.PRIZE, "committee": C.COMMITTEE, "citations": C.CITATIONS,
        "method": {"checked_against": C.CHECKED_AGAINST, "hac": "Newey-West (Bartlett kernel), %d lags, no "
                   "small-sample factor; F tests use F(q, n - k)" % C.HAC_LAGS,
                   "iv": "two-stage least squares; HAC covariance from the structural residuals; 95 %% interval = "
                         "lambda +/- %.2f standard errors" % C.Z95,
                   "effective_F": "Montiel Olea and Pflueger (2013): pi' Z'Z pi / tr(V Z'Z), V = HAC covariance "
                                  "of the first-stage coefficients pi, constant partialled out",
                   "strong_rule": C.STRONG_RULE, "anderson_rubin": C.AR_NOTE},
        "data": data_block(),
        "sample": {"growth_quarters": len(qg), "regression_quarters": [rq[0], rq[-1]], "n": len(rq),
                   "lags": C.LAGS, "iv_lags": list(C.IV_LAGS), "hac_lags": C.HAC_LAGS, "split_year": C.SPLIT_YEAR,
                   "halves": {"first": _span(rq, masks["first_half"]), "second": _span(rq, masks["second_half"])},
                   "pre_2020_end": C.PRE_2020_END, "cm_window": _span(rq, masks["cm_window"]),
                   "ci_level_pct": 95},
        "hall": hall,
        "lambda": lam,
        "robustness_total_pce": rob,
        "pandemic": pan,
        "control": control_block(len(qg)),
        "guess": guess_block(hall, lam, pan, rob),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-figures", action="store_true")
    a = ap.parse_args(argv)
    s = summary()
    C.RESULTS.mkdir(parents=True, exist_ok=True)
    (C.RESULTS / C.RESULTS_JSON).write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n")
    if not a.no_figures:
        from . import figures as F
        F.fig_hall(s)
        F.fig_lambda(s)
        F.fig_control(s)
    g = s["guess"]
    for label, h, l in (("nds", s["hall"], s["lambda"]),
                        ("pce", s["robustness_total_pce"]["hall"], s["robustness_total_pce"]["lambda"])):
        for k in HALL_SAMPLES:
            print(label, "hall", k, h[k]["quarters"], h[k]["n"], h[k]["r2_pct"], h[k]["p_all_lags"],
                  h[k]["p_income_lags"], h[k]["lags_2_4"])
        print(label, "oos", h["out_of_sample"])
        for k in LAMBDA_SAMPLES:
            print(label, "lambda", k, l[k]["quarters"],
                  {z: (l[k][z]["lambda"], l[k][z]["ci95"], l[k][z]["first_stage_F"], l[k][z]["first_stage_F_hac"],
                       l[k][z]["effective_F"], l[k][z]["anderson_rubin"]["set95"],
                       l[k][z]["anderson_rubin"]["classic_set95"]) for z in IV_SETS}, "ols", l[k]["ols"])
    for k, v in s["control"]["cases"].items():
        print("control", k, {x: y for x, y in v.items() if x != "lambda_hist"})
    print("example", s["control"]["example"])
    print("fisher_check", s["data"]["fisher_check"])
    print("guess", json.dumps(g, ensure_ascii=False))


if __name__ == "__main__":
    main()
