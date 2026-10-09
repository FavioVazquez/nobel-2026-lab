"""A tiny Kaplan-Meier estimator (survival, Greenwood log-log 95 % intervals, median), a log-rank test and a
cluster bootstrap. Tested on hand examples."""
import math
import random

import numpy as np

from . import constants as C


def kaplan_meier(times, events, z=C.Z95):
    """times: years observed; events: 1 = fighting resumed at that time, 0 = still holding when the data stop.
    Returns a list of steps (t, at_risk, events, S, lo, hi) at each time with an event, starting at t = 0."""
    data = sorted(zip(times, events))
    n, s, gw = len(data), 1.0, 0.0
    steps = [(0, n, 0, 1.0, 1.0, 1.0)]
    i = 0
    while i < len(data):
        t = data[i][0]
        d = sum(e for tt, e in data if tt == t)
        m = sum(1 for tt, _ in data if tt == t)
        if d:
            s *= 1 - d / n
            gw = gw + d / (n * (n - d)) if n > d else float("inf")
            if 0 < s < 1 and math.isfinite(gw):
                se = math.sqrt(gw) / abs(math.log(s))
                lo, hi = s ** math.exp(z * se), s ** math.exp(-z * se)
            else:
                lo, hi = (0.0, 0.0) if s == 0 else (s, s)
            steps.append((t, n, d, s, lo, hi))
        n -= m
        i += m
    return steps


def at(steps, t):
    """S, lo, hi at time t (the step function is right-continuous)."""
    row = [r for r in steps if r[0] <= t][-1]
    return row[3], row[4], row[5]


def first_below(steps, col, level=0.5):
    for r in steps:
        if r[col] <= level:
            return r[0]
    return None


def median(steps):
    """Median and its 95 % interval read off the band (None: not reached in the data)."""
    return first_below(steps, 3), first_below(steps, 4), first_below(steps, 5)


def chi2_p(x, df):
    """Upper tail of a chi-square with 1 or 2 degrees of freedom (closed forms)."""
    if df == 1:
        return math.erfc(math.sqrt(max(x, 0.0) / 2))
    if df == 2:
        return math.exp(-max(x, 0.0) / 2)
    raise ValueError("df must be 1 or 2")


def logrank(groups):
    """Log-rank test across groups, each (times, events). Returns (chi-square, df, p)."""
    k = len(groups)
    data = [(t, e, g) for g, (ts, es) in enumerate(groups) for t, e in zip(ts, es)]
    u, v = np.zeros(k), np.zeros((k, k))
    for t in sorted({t for t, e, _ in data if e}):
        n = np.array([sum(1 for tt, _, g in data if g == j and tt >= t) for j in range(k)], float)
        d = np.array([sum(1 for tt, e, g in data if g == j and tt == t and e) for j in range(k)], float)
        N, D = n.sum(), d.sum()
        u += d - D * n / N
        if N > 1:
            v += D * (N - D) / (N - 1) * (np.diag(n / N) - np.outer(n, n) / (N * N))
    x = float(u[:-1] @ np.linalg.solve(v[:-1, :-1], u[:-1]))
    return x, k - 1, chi2_p(x, k - 1)


NOT_REACHED = 10 ** 6  # stands in for a median not reached in a resample


def cluster_bootstrap(spells_by_group, reps=C.BOOT_REPS, seed=C.BOOT_SEED, horizons=C.HORIZONS):
    """Resample whole groups (lists of (years, event)) with replacement. Returns percentile 95 % intervals, as
    fractions, for S at each horizon and for the median (None: not reached in at least 2.5 % of resamples)."""
    rng = random.Random(seed)
    keys = list(spells_by_group)
    at_h = {h: [] for h in horizons}
    meds = []
    for _ in range(reps):
        sp = [s for key in (rng.choice(keys) for _ in keys) for s in spells_by_group[key]]
        steps = kaplan_meier([s[0] for s in sp], [s[1] for s in sp])
        for h in horizons:
            at_h[h].append(at(steps, h)[0])
        meds.append(median(steps)[0] or NOT_REACHED)
    out = {h: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for h, v in at_h.items()}
    lo, hi = np.percentile(meds, [2.5, 97.5])
    out["median"] = [None if x >= NOT_REACHED else (int(x) if float(x).is_integer() else round(float(x), 1))
                     for x in (lo, hi)]
    return out
