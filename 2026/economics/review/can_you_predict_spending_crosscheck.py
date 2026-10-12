"""Independent cross-check of 2026/economics/can-you-predict-spending (branch econ-spend). Educational demo, not
research.

Shares no code with the toy. Reads BEA's bulk NipaDataQ.txt itself (pandas), builds the per-person series, and runs
every regression with statsmodels, linearmodels and SciPy. Adds what the toy does not compute: the Montiel Olea-Pflueger
effective first-stage F (robust to heteroskedasticity and autocorrelation), LIML, two-step and continuously-updated
GMM, a homoskedastic Anderson-Rubin set, Campbell and Mankiw's own window (1953Q1-1986Q4, their row 8 instrument
c - y lagged two quarters) and a Fisher-chained non-durables-plus-services series built from BEA's quantity indexes.
Re-runs the simulated control from the README's description with another seed. The toy's JSON is read only at the end.

Usage: python can_you_predict_spending_crosscheck.py <path to 2026/economics/can-you-predict-spending> [out.json]
(the toy's `python -m spend.fetch_data --refresh` puts the bulk file in data/raw/bea/)
Tested with Python 3.11, numpy 1.26.4, scipy 1.15.2, pandas 2.2.3, statsmodels 0.14.4, linearmodels 7.0.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.iv import IV2SLS, IVGMM, IVGMMCUE, IVLIML
from scipy import optimize, stats

NIPA_SHA256 = "7a577c587cecc4b9e07b2edae2684ed565e7aef477a563c2a03d076f55d848b8"  # release of 2026-09-30
CODES = ["DPCERX", "DPCERC", "A067RX", "B230RC", "DNDGRA", "DSERRA", "DNDGRC", "DSERRC", "DDURRA", "DDURRC",
         "DPCERA"]
HAC = {"maxlags": 4, "use_correction": False}
LINEAR_HAC = {"cov_type": "kernel", "kernel": "bartlett", "bandwidth": 4, "debiased": False}
SAMPLES = {"pre_2020": ("1960Q2", "2019Q4"), "full": ("1960Q2", "2026Q2"), "first_half": ("1960Q2", "1992Q4"),
           "second_half": ("1993Q1", "2026Q2"), "cm_window": ("1960Q2", "1986Q4"),
           "cm_exact": ("1953Q1", "1986Q4")}


# ---------- data ----------

def load(toy):
    path = toy / "data" / "raw" / "bea" / "NipaDataQ.txt"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == NIPA_SHA256, "not the pinned BEA release"
    raw = pd.read_csv(path, thousands=",", dtype={0: str, 1: str})
    raw.columns = ["code", "period", "value"]
    w = raw[raw.code.isin(CODES)].pivot(index="period", columns="code", values="value").sort_index()
    w = w.loc["1947Q1":]
    out = pd.DataFrame(index=w.index)
    pop = w.B230RC * 1e3                                  # thousands of persons
    out["lc"] = np.log(w.DPCERX * 1e6 / pop)              # millions of chained 2017 dollars
    out["ly"] = np.log(w.A067RX * 1e6 / pop)
    # Fisher chain of non-durables + services from BEA's quantity indexes and current-dollar values
    qa, qb, va, vb = w.DNDGRA, w.DSERRA, w.DNDGRC, w.DSERRC
    ra, rb = qa / qa.shift(), qb / qb.shift()
    lasp = (va.shift() * ra + vb.shift() * rb) / (va.shift() + vb.shift())
    paas = (va + vb) / (va / ra + vb / rb)
    rel = np.sqrt(lasp * paas).fillna(1.0)
    out["lcns"] = np.log(rel.cumprod() * 1e6 / pop)        # level arbitrary: only differences are used
    # the same Fisher formula on all three parts must give BEA's own total-PCE quantity index (DPCERA)
    r3 = [w[c] / w[c].shift() for c in ("DDURRA", "DNDGRA", "DSERRA")]
    v3 = [w[c] for c in ("DDURRC", "DNDGRC", "DSERRC")]
    l3 = sum(v.shift() * r for v, r in zip(v3, r3)) / sum(v.shift() for v in v3)
    p3 = sum(v3) / sum(v / r for v, r in zip(v3, r3))
    fisher_err = float((np.log(np.sqrt(l3 * p3)) - np.log(w.DPCERA / w.DPCERA.shift())).abs().max())
    chk = {"fisher_total_vs_DPCERA_max_abs_dlog": fisher_err,
           "dpcerx_2017": float(w.DPCERX.loc["2017Q1":"2017Q4"].mean()),
           "dpcerc_2017": float(w.DPCERC.loc["2017Q1":"2017Q4"].mean()),
           "first": w.index[0], "last": w.index[-1], "rows": len(w)}
    return out, chk


def design(lev, cname="lc"):
    g = pd.DataFrame({"dc": lev[cname].diff(), "dy": lev["ly"].diff(), "cy": lev[cname] - lev["ly"]})
    d = pd.DataFrame({"dc": g.dc, "dy": g.dy})
    for j in range(1, 5):
        d[f"dc{j}"], d[f"dy{j}"] = g.dc.shift(j), g.dy.shift(j)
    d["cy2"] = g.cy.shift(2)
    return d.dropna()


ZSETS = {"both": ["dy2", "dy3", "dy4", "dc2", "dc3", "dc4"], "income": ["dy2", "dy3", "dy4"],
         "consumption": ["dc2", "dc3", "dc4"], "row8": ["dy2", "dy3", "dy4", "dc2", "dc3", "dc4", "cy2"]}
HALL14 = ["dc1", "dc2", "dc3", "dc4", "dy1", "dy2", "dy3", "dy4"]


# ---------- tests ----------

def ftest(res, names):
    f = res.f_test(", ".join(f"{n} = 0" for n in names))
    return float(np.squeeze(f.fvalue)), float(f.pvalue)


def ols(y, X, **cov):
    return sm.OLS(y, sm.add_constant(X)).fit(cov_type="HAC", cov_kwds=cov or HAC)


def hall(d):
    y = d.dc
    a = ols(y, d[HALL14])
    b = ols(y, d[ZSETS["both"]])
    out = {"n": int(len(d)), "r2_pct": 100 * a.rsquared, "r2_adj_pct": 100 * a.rsquared_adj,
           "p_all_lags": ftest(a, HALL14)[1], "p_income_lags": ftest(a, HALL14[4:])[1],
           "p_consumption_lags": ftest(a, HALL14[:4])[1],
           "lags_2_4": {"r2_pct": 100 * b.rsquared, "r2_adj_pct": 100 * b.rsquared_adj,
                        "F": ftest(b, ZSETS["both"])[0], "p": ftest(b, ZSETS["both"])[1]}}
    # sensitivity of the lags 2-4 p-value to the HAC choices (not in the toy)
    out["lags_2_4"]["p_hac8"] = ftest(ols(y, d[ZSETS["both"]], maxlags=8, use_correction=False), ZSETS["both"])[1]
    out["lags_2_4"]["p_hac4_small_sample"] = ftest(ols(y, d[ZSETS["both"]], maxlags=4, use_correction=True),
                                                   ZSETS["both"])[1]
    return out


def oos(d, cols, start):
    y, X = d.dc.values, sm.add_constant(d[cols]).values
    i0 = list(d.index).index(start)
    em, eb = [], []
    for t in range(i0, len(y)):
        b = sm.OLS(y[:t], X[:t]).fit().params
        em.append(y[t] - X[t] @ b)
        eb.append(y[t] - y[:t].mean())
    em, eb = np.array(em), np.array(eb)
    return 100 * (1 - em @ em / (eb @ eb))


def effective_f(x, Z):
    """Montiel Olea and Pflueger (2013) effective F for one endogenous regressor, HAC (Bartlett, 4 lags)."""
    Zc = Z - Z.mean(0)
    fit = sm.OLS(x, sm.add_constant(Z)).fit(cov_type="HAC", cov_kwds=HAC)
    pi = np.asarray(fit.params)[1:]
    V = np.asarray(fit.cov_params())[1:, 1:]
    ZZ = Zc.T @ Zc
    return float(pi @ ZZ @ pi / np.trace(V @ ZZ))


def ar_stat(y, x, Z, lam, hac=True):
    r = sm.OLS(y - lam * x, sm.add_constant(Z)).fit(**({"cov_type": "HAC", "cov_kwds": HAC} if hac else {}))
    R = np.eye(Z.shape[1] + 1)[1:]
    return float(np.squeeze(r.f_test(R).fvalue))


def ar_set(y, x, Z, hac=True, lo=-10.0, hi=20.0, step=0.02):
    q, n = Z.shape[1], len(y)
    crit = stats.f.ppf(0.95, q, n - q - 1)
    grid = np.arange(lo, hi + step / 2, step)
    g = np.array([ar_stat(y, x, Z, v, hac) - crit for v in grid])
    inside = g < 0
    runs, i = [], 0
    while i < len(grid):
        if inside[i]:
            j = i
            while j + 1 < len(grid) and inside[j + 1]:
                j += 1
            a = grid[i] if i == 0 else optimize.brentq(lambda v: ar_stat(y, x, Z, v, hac) - crit, grid[i - 1],
                                                       grid[i], xtol=1e-7)
            b = grid[j] if j == len(grid) - 1 else optimize.brentq(lambda v: ar_stat(y, x, Z, v, hac) - crit,
                                                                   grid[j], grid[j + 1], xtol=1e-7)
            runs.append([float(a), float(b)])
            i = j + 1
        else:
            i += 1
    k = int(np.argmin(g))
    return {"set": runs, "crit": float(crit), "min_F": float(g[k] + crit), "min_at": float(grid[k])}


def iv(d, zname, with_ar=True):
    y, x, Z = d.dc, d.dy, d[ZSETS[zname]]
    const = pd.DataFrame({"const": np.ones(len(d))}, index=d.index)
    m = IV2SLS(y, const, x, Z).fit(**LINEAR_HAC)
    lam, se = float(m.params["dy"]), float(m.std_errors["dy"])
    first_classic = sm.OLS(x, sm.add_constant(Z)).fit()
    first_hac = ols(x, Z)
    out = {"lambda": lam, "se_hac": se, "ci95": [lam - 1.959963984540054 * se, lam + 1.959963984540054 * se],
           "first_stage_F": ftest(first_classic, ZSETS[zname])[0], "first_stage_F_hac": ftest(first_hac, ZSETS[zname])[0],
           "effective_F": effective_f(x.values, Z.values),
           "ols_lambda": float(ols(y, d[["dy"]]).params["dy"]),
           "liml": float(IVLIML(y, const, x, Z).fit(**LINEAR_HAC).params["dy"]),
           "gmm2": float(IVGMM(y, const, x, Z, weight_type="kernel", kernel="bartlett", bandwidth=4)
                         .fit(**LINEAR_HAC).params["dy"])}
    try:
        out["gmm_cue"] = float(IVGMMCUE(y, const, x, Z, weight_type="kernel", kernel="bartlett", bandwidth=4)
                               .fit(**LINEAR_HAC).params["dy"])
    except Exception as e:  # noqa: BLE001
        out["gmm_cue"] = repr(e)
    if with_ar:
        out["ar_hac"] = ar_set(y.values, x.values, Z.values, True)
        out["ar_classic"] = ar_set(y.values, x.values, Z.values, False)
    return out


# ---------- simulated control, from the README's description ----------

def sim_control(seed=7, reps=1000, n_growth=269):
    rng = np.random.default_rng(seed)
    g, sdu, share, sdn, burn = 0.005, 0.008, 0.5, 0.004, 200
    res = {}
    for name, lam, rho in (("hand_to_mouth", 0.3, 0.8), ("random_walk", 0.0, 0.8),
                           ("hand_to_mouth_weak", 0.3, 0.3), ("random_walk_weak", 0.0, 0.3)):
        acc = {"hall": 0, "cover": 0, "ar": 0, "lam": [], "F": [], "r224": []}
        for _ in range(reps):
            m = n_growth + burn
            u, news = rng.normal(0, sdu, m), rng.normal(0, sdn, m)
            dy = np.empty(m)
            prev = g
            for t in range(m):
                prev = dy[t] = g + rho * (prev - g) + u[t]
            fwd = g + share * u + news           # forward-looking consumption growth: news only
            dc = (lam * dy + (1 - lam) * fwd)[burn:]
            dy = dy[burn:]
            lev = pd.DataFrame({"lc": np.r_[0, np.cumsum(dc)], "ly": np.r_[0, np.cumsum(dy)]})
            d = design(lev)
            h = ols(d.dc, d[HALL14])
            acc["hall"] += ftest(h, HALL14)[1] < 0.05
            acc["r224"].append(ols(d.dc, d[ZSETS["both"]]).rsquared)
            Z = d[ZSETS["both"]]
            const = pd.DataFrame({"const": np.ones(len(d))}, index=d.index)
            mm = IV2SLS(d.dc, const, d.dy, Z).fit(**LINEAR_HAC)
            lh, se = float(mm.params["dy"]), float(mm.std_errors["dy"])
            acc["cover"] += abs(lh - lam) <= 1.959963984540054 * se
            arF = ar_stat(d.dc.values, d.dy.values, Z.values, lam)
            acc["ar"] += arF < stats.f.ppf(0.95, 6, len(d) - 7)
            acc["lam"].append(lh)
            acc["F"].append(ftest(sm.OLS(d.dy, sm.add_constant(Z)).fit(), ZSETS["both"])[0])
        res[name] = {"n_regression": int(len(d)), "hall_reject_pct": 100 * acc["hall"] / reps,
                     "ci95_coverage_pct": 100 * acc["cover"] / reps, "ar_coverage_pct": 100 * acc["ar"] / reps,
                     "median_lambda": float(np.median(acc["lam"])), "median_first_stage_F": float(np.median(acc["F"])),
                     "median_r2_lags_2_4_pct": 100 * float(np.median(acc["r224"]))}
    return res


# ---------- compare with the toy ----------

def close(mine, theirs, nd):
    return abs(mine - theirs) <= 0.5 * 10 ** (-nd) + 1e-9


def sig3(x):
    return float("%.3g" % x)


def compare(me, toy):
    rows = []

    def add(label, mine, theirs, nd=None):
        ok = (sig3(mine) == theirs) if nd is None else close(mine, theirs, nd)
        rows.append({"field": label, "ours": mine, "toy": theirs, "ok": bool(ok)})

    for s in ("full", "first_half", "second_half", "pre_2020"):
        a, b = me["hall"][s], toy["hall"][s]
        add(f"hall.{s}.n", a["n"], b["n"], 0)
        for k in ("r2_pct", "r2_adj_pct"):
            add(f"hall.{s}.{k}", a[k], b[k], 1)
            add(f"hall.{s}.lags_2_4.{k}", a["lags_2_4"][k], b["lags_2_4"][k], 1)
        for k in ("p_all_lags", "p_income_lags", "p_consumption_lags"):
            add(f"hall.{s}.{k}", a[k], b[k])
        add(f"hall.{s}.lags_2_4.p", a["lags_2_4"]["p"], b["lags_2_4"]["p"])
        add(f"hall.{s}.lags_2_4.F", a["lags_2_4"]["F"], b["lags_2_4"]["F"], 2)
    o, t = me["oos"], toy["hall"]["out_of_sample"]
    for k in ("full_r2_pct", "pre_2020_r2_pct", "lags_2_4_full_r2_pct", "lags_2_4_pre_2020_r2_pct"):
        add(f"hall.out_of_sample.{k}", o[k], t[k], 1)
    for s in ("pre_2020", "full", "first_half", "second_half", "cm_window"):
        add(f"lambda.{s}.ols.lambda", me["iv"][s]["both"]["ols_lambda"], toy["lambda"][s]["ols"]["lambda"], 3)
        for z in ("both", "income", "consumption"):
            a, b = me["iv"][s][z], toy["lambda"][s][z]
            add(f"lambda.{s}.{z}.lambda", a["lambda"], b["lambda"], 3)
            add(f"lambda.{s}.{z}.se_hac", a["se_hac"], b["se_hac"], 3)
            add(f"lambda.{s}.{z}.ci95[0]", a["ci95"][0], b["ci95"][0], 3)
            add(f"lambda.{s}.{z}.ci95[1]", a["ci95"][1], b["ci95"][1], 3)
            add(f"lambda.{s}.{z}.first_stage_F", a["first_stage_F"], b["first_stage_F"], 2)
            add(f"lambda.{s}.{z}.first_stage_F_hac", a["first_stage_F_hac"], b["first_stage_F_hac"], 2)
            ar_t = b["anderson_rubin"]
            mine_set = a["ar_hac"]["set"]
            # the toy's grid (step 0.001) keeps the first and last grid points inside each interval
            mine_grid = [[np.ceil(lo * 1000 - 1e-6) / 1000, np.floor(hi * 1000 + 1e-6) / 1000] for lo, hi in mine_set]
            if ar_t["open_at_grid_end"]:
                mine_grid = [[max(lo, -10.0), min(hi, 20.0)] for lo, hi in mine_grid]
            rows.append({"field": f"lambda.{s}.{z}.anderson_rubin.set95", "ours": mine_grid, "ours_exact": mine_set,
                         "toy": ar_t["set95"],
                         "ok": len(mine_grid) == len(ar_t["set95"]) and all(
                             abs(p - q) < 1.5e-3 for u, v in zip(mine_grid, ar_t["set95"]) for p, q in zip(u, v))})
    pan = toy["pandemic"]["quarters"]
    for q in pan:
        add(f"pandemic.{q}.dc_pct", me["pandemic"][q]["dc_pct"], pan[q]["dc_pct"], 1)
        add(f"pandemic.{q}.dy_pct", me["pandemic"][q]["dy_pct"], pan[q]["dy_pct"], 1)
    add("pandemic.sd_dc_pct_1960_2019", me["sd_dc_pct_to_2019"], toy["pandemic"]["sd_dc_pct_1960_2019"], 2)
    return rows


def full_precision(toy, d):
    """Import the toy's model only now and compare unrounded numbers with statsmodels / linearmodels."""
    sys.path.insert(0, str(toy))
    from spend import model as T  # noqa: E402
    q, lc, ly = T.load()
    qg, dc, dy = T.growth(q, lc, ly)
    td = T.design(dc, dy)
    rq = np.array(qg[T.C.LAGS:])
    out = {}
    for s, (a, b) in (("pre_2020", SAMPLES["pre_2020"]), ("full", SAMPLES["full"])):
        m = (rq >= a) & (rq <= b)
        mine = d.loc[a:b]
        h = T.hall_test(td["y"][m], td["x_hall"][m])["fit"]
        ref = ols(mine.dc, mine[HALL14])
        tv = T.iv_lambda(td["y"][m], td["x_iv"][m], td["z_both"][m])
        const = pd.DataFrame({"const": np.ones(len(mine))}, index=mine.index)
        lm = IV2SLS(mine.dc, const, mine.dy, mine[ZSETS["both"]]).fit(**LINEAR_HAC)
        out[s] = {"hall_coef": float(np.abs(h["b"] - ref.params.values).max()),
                  "hall_se_hac": float(np.abs(h["se"] - ref.bse.values).max()),
                  "iv_lambda": abs(tv["lambda"] - float(lm.params["dy"])),
                  "iv_se_hac": abs(tv["se"] - float(lm.std_errors["dy"])),
                  "first_stage_F": abs(tv["first_stage_F"] - ftest(sm.OLS(mine.dy, sm.add_constant(
                      mine[ZSETS["both"]])).fit(), ZSETS["both"])[0])}
    return out


def main(toy, out_path=None):
    lev, chk = load(toy)
    d = design(lev)
    mine_csv = pd.read_csv(toy / "data" / "quarterly.csv", index_col="quarter")
    diff = float(max((mine_csv.log_c_pc - lev.lc.loc[mine_csv.index]).abs().max(),
                     (mine_csv.log_y_pc - lev.ly.loc[mine_csv.index]).abs().max()))
    sub = {s: d.loc[a:b] for s, (a, b) in SAMPLES.items()}
    sub["cm_window"] = d.loc["1960Q2":"1986Q4"]
    me = {"data": {**chk, "max_abs_diff_log_pc_vs_toy_csv": diff},
          "hall": {s: hall(sub[s]) for s in ("full", "first_half", "second_half", "pre_2020", "cm_exact")}}
    pre = sub["pre_2020"]
    me["oos"] = {"full_r2_pct": oos(sub["full"], HALL14, "1993Q1"), "pre_2020_r2_pct": oos(pre, HALL14, "1993Q1"),
                 "lags_2_4_full_r2_pct": oos(sub["full"], ZSETS["both"], "1993Q1"),
                 "lags_2_4_pre_2020_r2_pct": oos(pre, ZSETS["both"], "1993Q1")}
    me["iv"] = {s: {z: iv(sub[s], z) for z in ("both", "income", "consumption")}
                for s in ("pre_2020", "full", "first_half", "second_half", "cm_window")}
    # Campbell and Mankiw's own window and their row 8 instrument set; and with non-durables + services
    me["cm_exact_total_pce"] = {z: iv(sub["cm_exact"], z) for z in ("income", "consumption", "both", "row8")}
    dns = design(lev, "lcns")
    me["cm_exact_nondurables_services"] = {z: iv(dns.loc["1953Q1":"1986Q4"], z)
                                           for z in ("income", "consumption", "both", "row8")}
    me["nondurables_services"] = {
        "hall_pre_2020": hall(dns.loc["1960Q2":"2019Q4"]), "hall_full": hall(dns.loc["1960Q2":"2026Q2"]),
        "iv_pre_2020_both": iv(dns.loc["1960Q2":"2019Q4"], "both"),
        "iv_full_both": iv(dns.loc["1960Q2":"2026Q2"], "both", with_ar=False)}
    g = pd.DataFrame({"dc": lev.lc.diff(), "dy": lev.ly.diff()}) * 100
    me["pandemic"] = {q: {"dc_pct": float(g.dc[q]), "dy_pct": float(g.dy[q])}
                      for q in ("2020Q1", "2020Q2", "2020Q3", "2020Q4", "2021Q1", "2021Q2")}
    me["sd_dc_pct_to_2019"] = float(g.dc.loc["1959Q2":"2019Q4"].std(ddof=1))
    me["control"] = sim_control()
    toy_json = json.loads((toy / "results" / "spending.json").read_text())
    me["comparison"] = compare(me, toy_json)
    bad = [r for r in me["comparison"] if not r["ok"]]
    me["comparison_summary"] = {"fields": len(me["comparison"]), "mismatches": len(bad)}
    me["full_precision_abs_diff"] = full_precision(toy, d)
    print("full precision:", me["full_precision_abs_diff"])
    text = json.dumps(me, indent=1, default=float)
    if out_path:
        Path(out_path).write_text(text + "\n")
    print("fields compared:", len(me["comparison"]), "mismatches:", len(bad))
    for r in bad:
        print("  MISMATCH", r)
    return me


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve(), sys.argv[2] if len(sys.argv) > 2 else None)
