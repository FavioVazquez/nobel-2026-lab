"""Soai's amplifier: three published-style toy models in dimensionless model units. Toy model, not research.

Layer 1 (Blackmond-Brown dimer model): product molecules sit in pairs at random (K = 4); a same-hand pair copies its
hand, a mixed pair does nothing. Then dR/dS = R^2/S^2, so 1/S - 1/R is conserved and everything is exact.

Layer 2 (our labelled toy): the same structure with a free pairing constant K. The pool of product is Kagan's ML2
mixture fed back on itself: the ee of new product is the g = 0 Kagan curve f(e) = e/(1 - z(e)). With P = amount of
product (seed = 1), P de/dP = f(e) - e, i.e.

    d ln(e) / d ln(P) = beta(e) = z / (1 - z)

the mixed-to-same-hand ratio. For K = 4, beta = (1 - e^2)/(1 + e^2), which integrates to e/(1 - e^2) = const * P.

Layer 3 (Buhse-Micheau monomer-active model, Buhse 2005 J. Mex. Chem. Soc. 49, 328, reactions [1']-[10']):
    A + Z -> R, A + Z -> S                (k0, racemic background)
    A + Z + R -> 2R, A + Z + S -> 2S      (k1, the monomer copies its hand)
    R + S <-> RS                          (k2 forward, k3 back: mixed pair)
    R + R <-> RR, S + S <-> SS            (k4 forward, k5 back: same-hand pairs)
Written in sums and differences (sigma = R + S, delta = R - S, ...) so that an exactly racemic start stays exactly
racemic: every term of the difference equations is proportional to a difference.
"""
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq


# ---------------- shared: Kagan's ML2 mixed fraction (same formula as ../kagan-curve/kagan/model.py) ----------------
def mixed_fraction(e, K):
    q = 1.0 - e * e
    return K * q / (K + np.sqrt(K * (4.0 * q + K * e * e)))


def growth_exponent(e, K):
    """beta(e) = z/(1 - z) = d ln(e) / d ln(P)."""
    z = mixed_fraction(e, K)
    return z / (1.0 - z)


# ---------------- layer 1: K = 4, exact ----------------
def layer1_ee(ee0, total_factor):
    """Exact ee after the product pool has grown by total_factor = P/P0 = 1 + turnovers, from ee0 (fractions)."""
    a = np.asarray(ee0, float) * np.asarray(total_factor, float) / (1.0 - np.asarray(ee0, float) ** 2)
    return np.where(a == 0, 0.0, (np.sqrt(1.0 + 4.0 * a * a) - 1.0) / (2.0 * np.where(a == 0, 1.0, a)))


def layer1_factor_needed(ee0, ee_target):
    """Growth factor P/P0 that K = 4 needs to go from ee0 to ee_target (exact, from the conserved quantity)."""
    return (ee_target / (1.0 - ee_target ** 2)) * (1.0 - ee0 ** 2) / ee0


def layer1_conserved(R, S):
    return 1.0 / S - 1.0 / R


# ---------------- layer 2: general K ----------------
def toy_ee(ee0, total_factors, K, ee_max=1.0):
    """ee after the pool grows by each factor in total_factors (increasing), for pairing constant K. Fractions.

    ee_max < 1: a same-hand pair makes its own hand only with that selectivity, so new product has ee = ee_max * f(e)
    and d ln(e)/d ln(P) = ee_max / (1 - z) - 1 (equal to beta when ee_max = 1)."""
    f = np.atleast_1d(np.asarray(total_factors, float))
    if K == 4.0 and ee_max == 1.0:
        return layer1_ee(ee0, f)
    s_end = float(np.log(f.max()))
    if s_end == 0:
        return np.full_like(f, ee0)
    rate = ((lambda e: growth_exponent(e, K)) if ee_max == 1.0
            else (lambda e: ee_max / (1.0 - mixed_fraction(e, K)) - 1.0))
    sol = solve_ivp(lambda s, y: [rate(math.exp(y[0]))], (0.0, s_end), [math.log(ee0)],
                    t_eval=np.log(f), method="LSODA", rtol=1e-11, atol=1e-12)
    return np.exp(sol.y[0])


def toy_rounds(ee0, K, turnovers_per_round, rounds=3, ee_max=1.0):
    """Each round's whole product seeds the next, so round k ends at P/P0 = (1 + N)^k. Returns ee after each round."""
    return toy_ee(ee0, [(1.0 + turnovers_per_round) ** k for k in range(1, rounds + 1)], K, ee_max)


def turnovers_for_round1(ee0, ee1, K):
    """Turnovers per round N that bring round 1 from ee0 to ee1 for this K."""
    g = lambda lnN: toy_rounds(ee0, K, math.exp(lnN), 1)[0] - ee1  # noqa: E731
    return math.exp(brentq(g, math.log(1e-3), math.log(1e9), xtol=1e-12))


def fit_two_rounds(ee0, ee1, ee2, K_lo=5.0, K_hi=1e5):
    """Find (K, N) so that round 1 gives ee1 and round 2 gives ee2. Returns K, N."""
    def miss(lnK):
        K = math.exp(lnK)
        N = turnovers_for_round1(ee0, ee1, K)
        return toy_rounds(ee0, K, N, 2)[1] - ee2
    K = math.exp(brentq(miss, math.log(K_lo), math.log(K_hi), xtol=1e-10))
    return K, turnovers_for_round1(ee0, ee1, K)


def hand_amounts(ee, total):
    """Amounts of one hand and mirror hand, given ee and the total pool (both relative to the round-0 seed)."""
    ee, total = np.asarray(ee, float), np.asarray(total, float)
    return total * (1.0 + ee) / 2.0, total * (1.0 - ee) / 2.0


# ---------------- layer 3: Buhse-Micheau monomer-active model ----------------
BUHSE_FIG1 = dict(k0=1e-6, k1=1.0, k2=1e5, k3=10.0, k4=10.0, k5=10.0)


def _buhse_rhs(t, u, k0, k1, k2, k3, k4, k5):
    A, Z, sg, dl, P, Q, M = u
    az = A * Z
    return [
        -2 * k0 * az - k1 * az * sg,
        -2 * k0 * az - k1 * az * sg,
        2 * k0 * az + k1 * az * sg - 0.5 * k2 * (sg * sg - dl * dl) + 2 * k3 * M - k4 * (sg * sg + dl * dl) + 2 * k5 * P,
        k1 * az * dl - 2 * k4 * sg * dl + 2 * k5 * Q,
        0.5 * k4 * (sg * sg + dl * dl) - k5 * P,
        k4 * sg * dl - k5 * Q,
        0.25 * k2 * (sg * sg - dl * dl) - k3 * M,
    ]


def _buhse_jac(t, u, k0, k1, k2, k3, k4, k5):
    A, Z, sg, dl, P, Q, M = u
    az = A * Z
    dA = [-(2 * k0 + k1 * sg) * Z, -(2 * k0 + k1 * sg) * A, -k1 * az, 0, 0, 0, 0]
    return np.array([
        dA,
        dA,
        [(2 * k0 + k1 * sg) * Z, (2 * k0 + k1 * sg) * A, k1 * az - k2 * sg - 2 * k4 * sg, k2 * dl - 2 * k4 * dl,
         2 * k5, 0, 2 * k3],
        [k1 * Z * dl, k1 * A * dl, -2 * k4 * dl, k1 * az - 2 * k4 * sg, 0, 2 * k5, 0],
        [0, 0, k4 * sg, k4 * dl, -k5, 0, 0],
        [0, 0, k4 * dl, k4 * sg, 0, -k5, 0],
        [0, 0, 0.5 * k2 * sg, -0.5 * k2 * dl, 0, 0, -k3],
    ])


def buhse_run(ee0, cat0=0.1, A0=1.0, Z0=1.0, t_end=1e4, t_eval=None, **k):
    """Integrate layer 3 from a monomer seed cat0 with ee0 (fraction). Returns dict with final ee and the solution."""
    p = {**BUHSE_FIG1, **k}
    u0 = [A0, Z0, cat0, cat0 * ee0, 0.0, 0.0, 0.0]
    atol = [1e-14, 1e-14, 1e-14, 1e-30, 1e-14, 1e-30, 1e-14]
    sol = solve_ivp(_buhse_rhs, (0.0, t_end), u0, method="Radau", jac=_buhse_jac, args=tuple(p[n] for n in
                    ("k0", "k1", "k2", "k3", "k4", "k5")), rtol=1e-10, atol=atol, t_eval=t_eval)
    A, Z, sg, dl, P, Q, M = sol.y
    ee = (dl + 2 * Q) / (sg + 2 * P + 2 * M)
    return {"ee": ee, "t": sol.t, "A": A, "ee_final": float(ee[-1]), "A_final": float(A[-1]), "ok": sol.success}


def _naive_rhs(t, u, k0, k1, k2, k3, k4, k5):
    A, Z, R, S, RR, SS, RS = u
    az = A * Z
    return [-2 * k0 * az - k1 * az * (R + S), -2 * k0 * az - k1 * az * (R + S),
            k0 * az + k1 * az * R - k2 * R * S + k3 * RS - 2 * k4 * R * R + 2 * k5 * RR,
            k0 * az + k1 * az * S - k2 * R * S + k3 * RS - 2 * k4 * S * S + 2 * k5 * SS,
            k4 * R * R - k5 * RR, k4 * S * S - k5 * SS, k2 * R * S - k3 * RS]


def buhse_naive_racemic(cat0=0.1, t_end=1e4, method="LSODA", rtol=1e-10, atol=1e-22):
    """The pitfall: hand-by-hand variables, a stiff solver with a finite-difference Jacobian, exactly racemic start."""
    p = BUHSE_FIG1
    sol = solve_ivp(_naive_rhs, (0.0, t_end), [1.0, 1.0, cat0 / 2, cat0 / 2, 0, 0, 0], method=method,
                    args=tuple(p[n] for n in ("k0", "k1", "k2", "k3", "k4", "k5")), rtol=rtol, atol=atol)
    A, Z, R, S, RR, SS, RS = sol.y[:, -1]
    return float((R + 2 * RR - S - 2 * SS) / (R + S + 2 * RR + 2 * SS + 2 * RS))
