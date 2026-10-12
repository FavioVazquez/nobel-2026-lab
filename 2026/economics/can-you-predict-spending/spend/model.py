"""OLS with Newey-West (HAC) standard errors, Wald F tests, two-stage least squares, Hall's test, the
Campbell-Mankiw lambda and the simulated household mix. NumPy only; checked against statsmodels in the tests.
Educational demo, not research."""
import csv
import math

import numpy as np

from . import constants as C


# ---------- distributions (no SciPy) ----------

def _betacf(a, b, x, eps=1e-15, itmax=500):
    """Continued fraction for the incomplete beta function (modified Lentz)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            return h
    raise RuntimeError("betacf did not converge")


def betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def f_sf(f, d1, d2):
    """P(F > f) for an F(d1, d2) variable."""
    if f <= 0:
        return 1.0
    return betainc(d2 / 2, d1 / 2, d2 / (d2 + d1 * f))


def f_isf(alpha, d1, d2):
    """The f with P(F > f) = alpha, by bisection on f_sf."""
    lo, hi = 0.0, 1.0
    while f_sf(hi, d1, d2) > alpha:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f_sf(mid, d1, d2) > alpha else (lo, mid)
    return (lo + hi) / 2


def normal_two_sided_p(z):
    return math.erfc(abs(z) / math.sqrt(2))


# ---------- regressions ----------

def hac_meat(xu, lags):
    """Newey-West (Bartlett) long-run covariance of the score rows xu (n x k), unscaled (sums, not means)."""
    s = xu.T @ xu
    for lag in range(1, lags + 1):
        w = 1 - lag / (lags + 1)
        g = xu[lag:].T @ xu[:-lag]
        s += w * (g + g.T)
    return s


def ols(y, X, hac_lags=C.HAC_LAGS):
    """OLS with HAC covariance (Bartlett kernel, no small-sample factor: statsmodels' default for cov_type='HAC')."""
    y, X = np.asarray(y, float), np.asarray(X, float)
    n, k = X.shape
    xtx_inv = np.linalg.inv(X.T @ X)
    b = xtx_inv @ X.T @ y
    u = y - X @ b
    cov = xtx_inv @ hac_meat(X * u[:, None], hac_lags) @ xtx_inv
    tss = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (u @ u) / tss
    return {"b": b, "cov": cov, "se": np.sqrt(np.diag(cov)), "resid": u, "n": n, "k": k, "r2": r2,
            "r2_adj": 1 - (1 - r2) * (n - 1) / (n - k), "cov_classic": xtx_inv * (u @ u) / (n - k)}


def wald_f(fit, idx, cov="cov"):
    """F test that the coefficients in idx are all zero, with the chosen covariance; F(q, n - k) p-value."""
    b, V = fit["b"][idx], fit[cov][np.ix_(idx, idx)]
    q = len(idx)
    f = float(b @ np.linalg.solve(V, b)) / q
    return {"F": f, "df": [q, fit["n"] - fit["k"]], "p": f_sf(f, q, fit["n"] - fit["k"])}


def tsls(y, X, Z, hac_lags=C.HAC_LAGS):
    """Two-stage least squares; HAC covariance from the structural residuals (same kernel as ols)."""
    y, X, Z = np.asarray(y, float), np.asarray(X, float), np.asarray(Z, float)
    n, k = X.shape
    Xh = Z @ np.linalg.lstsq(Z, X, rcond=None)[0]
    a_inv = np.linalg.inv(Xh.T @ X)
    b = a_inv @ Xh.T @ y
    u = y - X @ b
    cov = a_inv @ hac_meat(Xh * u[:, None], hac_lags) @ a_inv.T
    return {"b": b, "cov": cov, "se": np.sqrt(np.diag(cov)), "resid": u, "n": n, "k": k,
            "cov_classic": a_inv * (u @ u) / (n - k)}


# ---------- data ----------

CONSUMPTION = {"nds": "log_c_pc", "pce": "log_pce_pc"}  # headline: non-durables + services; robustness: total PCE


def load(consumption="nds"):
    with open(C.DERIVED, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return ([r["quarter"] for r in rows], np.array([float(r[CONSUMPTION[consumption]]) for r in rows]),
            np.array([float(r["log_y_pc"]) for r in rows]))


def growth(quarters, log_c, log_y):
    """Quarterly growth (log points) of per-capita consumption and income, labelled by the later quarter."""
    return quarters[1:], np.diff(log_c), np.diff(log_y)


def log_ratio(log_c, log_y):
    """log(c / y) in the quarters of the growth rates (Campbell and Mankiw's row 8 instrument, lagged in design)."""
    return (log_c - log_y)[1:]


def lags(x, which):
    """Columns x[t - j] for j in which, for the rows t = LAGS .. len(x) - 1."""
    n = len(x)
    return np.column_stack([x[C.LAGS - j:n - j] for j in which])


def design(dc, dy, cy=None):
    """Rows t = LAGS..: dependent dc[t]; Hall regressors (const, dc lags 1-4, dy lags 1-4); IV pieces. With cy
    (log_ratio), also Campbell and Mankiw's row 8 set: both sets of lags 2-4 plus log(c / y) lagged two quarters."""
    one = np.ones(len(dc) - C.LAGS)
    lag14 = range(1, C.LAGS + 1)
    d = {
        "y": dc[C.LAGS:],
        "x_hall": np.column_stack([one, lags(dc, lag14), lags(dy, lag14)]),
        "x_iv": np.column_stack([one, dy[C.LAGS:]]),
        "z_dy": np.column_stack([one, lags(dy, C.IV_LAGS)]),
        "z_dc": np.column_stack([one, lags(dc, C.IV_LAGS)]),
        "z_both": np.column_stack([one, lags(dy, C.IV_LAGS), lags(dc, C.IV_LAGS)]),
    }
    if cy is not None:
        d["z_row8"] = np.column_stack([d["z_both"], lags(cy, (2,))])
    return d


IDX_ALL = list(range(1, 2 * C.LAGS + 1))
IDX_C = list(range(1, C.LAGS + 1))
IDX_Y = list(range(C.LAGS + 1, 2 * C.LAGS + 1))


def hall_test(y, X):
    fit = ols(y, X)
    return {"fit": fit, "all_lags": wald_f(fit, IDX_ALL), "income_lags": wald_f(fit, IDX_Y),
            "consumption_lags": wald_f(fit, IDX_C)}


def effective_f(x, Z, first=None):
    """Montiel Olea and Pflueger (2013) effective first-stage F for one endogenous regressor x: pi' Z'Z pi /
    tr(V Z'Z), with pi the first-stage coefficients on the instruments (Z without its constant, demeaned, so the
    constant is partialled out) and V their HAC covariance. With homoskedastic, serially uncorrelated errors it is
    the classic first-stage F."""
    first = first or ols(x, Z)
    idx = list(range(1, Z.shape[1]))
    Zc = Z[:, idx] - Z[:, idx].mean(0)
    pi, V, zz = first["b"][idx], first["cov"][np.ix_(idx, idx)], Zc.T @ Zc
    return float(pi @ zz @ pi / np.trace(V @ zz))


def iv_lambda(y, X, Z):
    iv = tsls(y, X, Z)
    first = ols(X[:, 1], Z)
    idx = list(range(1, Z.shape[1]))
    lam, se = float(iv["b"][1]), float(iv["se"][1])
    f_eff = effective_f(X[:, 1], Z, first)
    return {"iv": iv, "lambda": lam, "se": se, "ci95": [lam - C.Z95 * se, lam + C.Z95 * se],
            "p_lambda_zero": normal_two_sided_p(lam / se),
            "first_stage_F": wald_f(first, idx, "cov_classic")["F"],
            "first_stage_F_hac": wald_f(first, idx)["F"], "effective_F": f_eff, "strong": f_eff > C.WEAK_F,
            "first_stage_r2_adj": first["r2_adj"], "instruments": len(idx)}


def ar_f(y, x, Z, lam0):
    """Anderson-Rubin statistic at lam0: HAC Wald F that the instruments (Z without its constant) do not predict
    y - lam0 * x. Under lambda = lam0 it does not depend on how strongly Z predicts x."""
    fit = ols(y - lam0 * x, Z)
    return wald_f(fit, list(range(1, Z.shape[1])))


def anderson_rubin(y, x, Z, grid=C.AR_GRID, level=C.AR_LEVEL):
    """The Anderson-Rubin set for lambda: every grid value lam0 where ar_f is below the F(q, n - k) critical value.
    Vectorised: the coefficients are linear in lam0 and the HAC middle matrix is quadratic in it (three
    evaluations fix it exactly). As lam0 goes to +/- infinity the statistic tends to the HAC first-stage F, so the set
    is unbounded when that F is below the critical value."""
    y, x, Z = np.asarray(y, float), np.asarray(x, float), np.asarray(Z, float)
    n, k = Z.shape
    idx = list(range(1, k))
    zz_inv = np.linalg.inv(Z.T @ Z)
    pa, pb = zz_inv @ Z.T @ y, zz_inv @ Z.T @ x
    ua, ub = y - Z @ pa, x - Z @ pb
    m0, m1, m2 = (hac_meat(Z * (ua - s * ub)[:, None], C.HAC_LAGS) for s in (0.0, 1.0, -1.0))
    qa, qb = (m1 - m2) / 2, (m1 + m2) / 2 - m0  # meat(lam0) = m0 + lam0 * qa + lam0^2 * qb
    lams = np.round(np.arange(grid[0], grid[1] + grid[2] / 2, grid[2]), 6)
    meat = m0 + lams[:, None, None] * qa + lams[:, None, None] ** 2 * qb
    V = (zz_inv @ meat @ zz_inv)[:, idx][:, :, idx]
    b = (pa[idx] - lams[:, None] * pb[idx])
    stat = np.einsum("gi,gi->g", b, np.linalg.solve(V, b[:, :, None])[:, :, 0]) / len(idx)
    # the same test with the classic (homoskedastic) covariance s^2 (Z'Z)^-1
    s2 = ((ua @ ua) - 2 * lams * (ua @ ub) + lams ** 2 * (ub @ ub)) / (n - k)
    w = np.linalg.inv(zz_inv[np.ix_(idx, idx)])
    stat_classic = np.einsum("gi,ij,gj->g", b, w, b) / (len(idx) * s2)
    crit = f_isf(level, len(idx), n - k)
    first = ols(x, Z)
    limit, limit_classic = wald_f(first, idx)["F"], wald_f(first, idx, "cov_classic")["F"]
    return {"intervals": _runs(lams, stat < crit), "intervals_classic": _runs(lams, stat_classic < crit),
            "crit": crit, "df": [len(idx), n - k], "grid": list(grid), "bounded": bool(limit > crit),
            "bounded_classic": bool(limit_classic > crit), "limit_F": limit, "stat": stat,
            "stat_classic": stat_classic, "lams": lams}


def _runs(lams, keep):
    """The grid intervals [first, last] where keep is True."""
    runs, start = [], None
    for i, ok in enumerate(keep):
        if ok and start is None:
            start = i
        if start is not None and (not ok or i == len(keep) - 1):
            end = i if ok else i - 1
            runs.append([float(lams[start]), float(lams[end])])
            start = None
    return runs


def oos_r2(y, X, start):
    """Pseudo out-of-sample R^2 of the Hall regression for rows start.. (each fitted on the rows before it),
    against the historical mean of consumption growth."""
    e_model, e_mean = [], []
    for t in range(start, len(y)):
        b = np.linalg.lstsq(X[:t], y[:t], rcond=None)[0]
        e_model.append(y[t] - X[t] @ b)
        e_mean.append(y[t] - y[:t].mean())
    e_model, e_mean = np.array(e_model), np.array(e_mean)
    return 1 - (e_model @ e_model) / (e_mean @ e_mean)


# ---------- the simulated control ----------

def simulate(rng, n_growth, lam, rho, p=C.SIM):
    """Income growth is AR(1) around g. Forward-looking households' consumption is a random walk with drift g:
    each quarter it moves only by news (a share of the income surprise plus other news), so its change cannot be
    predicted. Hand-to-mouth households, with a share lam of income, spend what they earn. Aggregate (log-linear,
    as in Campbell and Mankiw 1989): dc = lam * dy + (1 - lam) * (g + news)."""
    m = n_growth + p["burn_in"]
    u = rng.normal(0, p["sd_income"], m)
    other = rng.normal(0, p["sd_news"], m)
    dy = np.empty(m)
    prev = p["growth"]
    for t in range(m):
        prev = dy[t] = p["growth"] + rho * (prev - p["growth"]) + u[t]
    dc = lam * dy + (1 - lam) * (p["growth"] + p["surprise_share"] * u + other)
    return dc[p["burn_in"]:], dy[p["burn_in"]:]


def sim_case(rng, n_growth, lam, rho, reps):
    out = {"hall_reject": 0, "income_reject": 0, "covered": 0, "ar_covered": 0, "weak": 0, "r2": [], "lambda": [],
           "F": [], "F_eff": [], "ci_width": [], "r2_lags_2_4": []}
    for _ in range(reps):
        dc, dy = simulate(rng, n_growth, lam, rho)
        d = design(dc, dy)
        h = hall_test(d["y"], d["x_hall"])
        iv = iv_lambda(d["y"], d["x_iv"], d["z_both"])
        out["hall_reject"] += h["all_lags"]["p"] < 0.05
        out["income_reject"] += h["income_lags"]["p"] < 0.05
        out["covered"] += iv["ci95"][0] <= lam <= iv["ci95"][1]
        out["ar_covered"] += ar_f(d["y"], d["x_iv"][:, 1], d["z_both"], lam)["p"] >= C.AR_LEVEL
        out["r2_lags_2_4"].append(ols(d["y"], d["z_both"])["r2"])
        out["weak"] += iv["first_stage_F"] < C.WEAK_F
        out["r2"].append(h["fit"]["r2"])
        out["lambda"].append(iv["lambda"])
        out["F"].append(iv["first_stage_F"])
        out["F_eff"].append(iv["effective_F"])
        out["ci_width"].append(iv["ci95"][1] - iv["ci95"][0])
    return out
