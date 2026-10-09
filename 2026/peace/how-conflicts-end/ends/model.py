"""Counts and shares of episode outcomes by decade, a Wilson interval and a small logistic trend test.
Pure functions on plain rows."""
import csv
import math

import numpy as np

from . import constants as C


def load(path=C.DERIVED):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def terminations(rows):
    """Rows where c_epterm = 1: the last active year of a conflict episode (the codebook's unit of outcome)."""
    return [r for r in rows if r["c_epterm"] == "1"]


def decade(year):
    return int(year) // 10 * 10


def by_decade(rows):
    """{decade: {outcome code: count}} over terminations, every outcome code present (zeros included)."""
    out = {}
    for r in terminations(rows):
        d = out.setdefault(decade(r["year"]), {k: 0 for k in C.OUTCOMES})
        d[r["c_outcome"]] += 1
    return dict(sorted(out.items()))


def wilson(k, n, z=C.Z95):
    """Wilson score interval for k successes in n trials, as fractions."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (mid - half, mid + half)


def pct(x, nd=1):
    return round(100.0 * x, nd)


def logistic(columns, y, iters=100):
    """Logistic regression of 0/1 y on the given columns plus an intercept, by Newton-Raphson.
    Returns (coefficients, standard errors, log-likelihood); the intercept comes first."""
    X = np.column_stack([np.ones(len(y))] + [np.asarray(c, float) for c in columns])
    yv = np.asarray(y, float)
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-X @ b))
        step = np.linalg.solve(X.T @ (X * (p * (1 - p))[:, None]), X.T @ (yv - p))
        b += step
        if np.max(np.abs(step)) < 1e-12:
            break
    p = 1 / (1 + np.exp(-X @ b))
    se = np.sqrt(np.diag(np.linalg.inv(X.T @ (X * (p * (1 - p))[:, None]))))
    return b, se, float(np.sum(yv * np.log(p) + (1 - yv) * np.log(1 - p)))


def normal_two_sided_p(z):
    return math.erfc(abs(z) / math.sqrt(2))


def chi2_1df_p(x):
    return math.erfc(math.sqrt(max(x, 0.0) / 2))


def trend(years, outcomes, z=C.Z95):
    """Logistic regression of a 0/1 outcome on the end year, in decades: the slope (log-odds per decade) with its
    Wald 95 % interval and p, the odds ratio per decade, and the likelihood-ratio p of adding a squared term
    (a test for a curve that rises and then falls, or the reverse)."""
    x = [(int(y) - C.TREND_CENTRE) / 10 for y in years]
    b, se, ll = logistic([x], outcomes)
    _, _, ll2 = logistic([x, [v * v for v in x]], outcomes)
    slope, half = float(b[1]), z * float(se[1])
    return {
        "endings": len(outcomes), "events": int(sum(outcomes)),
        "slope_log_odds_per_decade": round(slope, 3),
        "slope_ci95": [round(slope - half, 3), round(slope + half, 3)],
        "odds_ratio_per_decade": round(math.exp(slope), 3),
        "p": round(normal_two_sided_p(slope / float(se[1])), 3),
        "squared_term_p": round(chi2_1df_p(2 * (ll2 - ll)), 3),
    }
