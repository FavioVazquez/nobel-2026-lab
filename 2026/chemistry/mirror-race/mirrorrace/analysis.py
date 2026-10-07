"""Exact answers and statistical tests.

Educational demo made to show an open-source tool. Toy model, not research.

The exact check (Polya urn). With no antagonism (k2 = 0) every event uses up one A and adds one
molecule of one hand. The chance that the next one is "one hand" is
    (k0 A + k1 A one) / (2 k0 A + k1 A (one + mirror)) = (a + one) / (2a + one + mirror),  a = k0/k1,
because A cancels. That is a Polya urn that starts with weight a of each colour. After N events the
number of one-hand molecules is Beta-binomial(N, a + head start, a), exactly, for any N.
With a = 1 every count 0..N is equally likely: the ee histogram is flat.
"""
import numpy as np
from scipy import stats

EDGES41 = np.linspace(-1.0, 1.0, 42)


def polya_pmf(N, a, head_start=0):
    """P(X = k), k = 0..N, X = one-hand molecules made from A (not counting the head start)."""
    return stats.betabinom(N, a + head_start, a).pmf(np.arange(N + 1))


def polya_ee_values(N, head_start=0):
    k = np.arange(N + 1)
    return (2 * k + head_start - N) / (N + head_start)


def polya_std_exact(N, a):
    """Std of the final ee for a racemic start: Var(X) = N (2a + N) / (4 (2a + 1))."""
    return float(np.sqrt((2 * a + N) / (N * (2 * a + 1))))


def polya_std_large_n(a):
    """Std of 2 Beta(a, a) - 1."""
    return float(1.0 / np.sqrt(2 * a + 1))


def polya_binned(N, a, edges=EDGES41):
    """Exact probability of each ee bin (np.histogram convention: last bin closed)."""
    pmf = polya_pmf(N, a)
    idx = np.clip(np.searchsorted(edges, polya_ee_values(N), side="right") - 1, 0, len(edges) - 2)
    return np.bincount(idx, weights=pmf, minlength=len(edges) - 1)


def flatness_test(ee, N, a, edges=EDGES41):
    """Chi-square of the simulated ee histogram against the exact Polya answer."""
    obs, _ = np.histogram(ee, bins=edges)
    exp = polya_binned(N, a, edges) * len(ee)
    chi2, p = stats.chisquare(obs, exp)
    return float(chi2), float(p), obs, exp


def seeded_copy_only_exact(N, a, delta):
    """Exact P(seeded hand ends ahead) with copying only: X ~ BetaBin(N, a + delta, a); win if delta + X > N - X."""
    k = np.arange(N + 1)
    pmf = polya_pmf(N, a, delta)
    return float(pmf[2 * k + delta > N].sum())


def coin(one, mirror):
    """Two-sided exact binomial test of one:mirror against 50:50."""
    n = int(one + mirror)
    return float(stats.binomtest(int(one), n, 0.5).pvalue) if n else float("nan")


def wins(ee):
    return int(np.sum(ee > 0)), int(np.sum(ee < 0)), int(np.sum(ee == 0))


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return float(c - h), float(c + h)


def crossing(x, y, level):
    """First x where y reaches `level`, by linear interpolation (None if never)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    above = np.nonzero(y >= level)[0]
    if not above.size:
        return None
    i = above[0]
    if i == 0:
        return float(x[0])
    return float(x[i - 1] + (level - y[i - 1]) * (x[i] - x[i - 1]) / (y[i] - y[i - 1]))
