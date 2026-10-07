"""Kagan's ML2 model of the non-linear effect, in closed form. Dimensionless; toy model, not research.

A metal M holds two chiral ligands. A ligand mixture with enantiomeric excess ee_L forms three complexes:
x = one-hand pair, y = mirror-hand pair, z = mixed pair (heterochiral, "meso"). As fractions of all complexes:

    x + y + z = 1,   x - y = ee_L,   K = z^2 / (x y)

so z solves (4 - K) z^2 + 2 K z - K (1 - ee_L^2) = 0. We use the root written in a form that is stable for every K > 0,
K = 4 included (no division by 4 - K):

    z = K (1 - ee_L^2) / (K + sqrt(K (4 (1 - ee_L^2) + K ee_L^2)))

Then beta = z / (x + y) = z / (1 - z), g = r_mixed / r_same, and (SCI eqs. 2-3; Buhse 2005 eqs. 3-7)

    ee_prod = ee_max * ee_L * (1 + beta) / (1 + g beta) = ee_max * ee_L / (1 - z + g z)
"""
import math

import numpy as np


def mixed_fraction(ee_L, K):
    """Fraction z of all complexes that are mixed pairs. K = inf means the mixed pair always forms first."""
    e = np.asarray(ee_L, dtype=float)
    if math.isinf(K):
        return 1.0 - np.abs(e)
    if K <= 0:
        return np.zeros_like(e)
    q = 1.0 - e * e
    return K * q / (K + np.sqrt(K * (4.0 * q + K * e * e)))


def complexes(ee_L, K):
    """(x, y, z): one-hand pair, mirror-hand pair, mixed pair, as fractions of all complexes."""
    z = mixed_fraction(ee_L, K)
    e = np.asarray(ee_L, dtype=float)
    return (1.0 - z + e) / 2.0, (1.0 - z - e) / 2.0, z


def beta(ee_L, K):
    z = mixed_fraction(ee_L, K)
    return z / (1.0 - z)


def ee_prod(ee_L, K=4.0, g=0.0, ee_max=1.0):
    """Product ee from the ML2 model. ee_L, ee_max as fractions (0..1); g = r_mixed / r_same."""
    e = np.asarray(ee_L, dtype=float)
    z = mixed_fraction(e, K)
    den = 1.0 - z + g * z
    with np.errstate(invalid="ignore", divide="ignore"):
        out = np.where(e == 0, 0.0, ee_max * e / np.where(den == 0, 1.0, den))
    return out if out.ndim else float(out)


def effective_split(ee_L, K=4.0, g=0.0):
    """Share of product made by each hand's catalysts, (one hand, mirror hand), in per cent."""
    x, y, z = complexes(ee_L, K)
    rx, ry, rz = float(x), float(y), g * float(z)
    tot = rx + ry + rz
    one = rx + rz / 2.0
    return 100.0 * one / tot, 100.0 * (tot - one) / tot


def pie(one_hand_ligand_pct=75.0, K=4.0, g=0.0, ee_max=1.0):
    """The Nobel popular-information example in numbers: ligand split -> complexes -> effective split -> product ee."""
    e = (2.0 * one_hand_ligand_pct - 100.0) / 100.0
    x, y, z = (float(v) for v in complexes(e, K))
    eff = effective_split(e, K, g)
    return {
        "ligand": [one_hand_ligand_pct, 100.0 - one_hand_ligand_pct],
        "ee_L_pct": 100.0 * e,
        "catalysts_pct": [100.0 * x, 100.0 * z, 100.0 * y],
        "effective": [eff[0], eff[1]],
        "ee_prod_pct": 100.0 * float(ee_prod(e, K, g, ee_max)),
    }


def reservoir_k4_g0(ee_L, ee_max=1.0):
    """Exact special case K = 4, g = 0: ee_prod = ee_max * 2 ee_L / (1 + ee_L^2)."""
    e = np.asarray(ee_L, dtype=float)
    return ee_max * 2.0 * e / (1.0 + e * e)


def erosion(ee_max=0.9, rounds=6, start=1.0):
    """Plain copying with no non-linear effect (SCI p. 10): each round's product ee = ee_max * the catalyst's ee."""
    out = [start]
    for _ in range(rounds):
        out.append(out[-1] * ee_max)
    return out
