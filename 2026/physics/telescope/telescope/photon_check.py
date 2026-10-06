"""Tier B: check the analytic light model against a brute-force photon random walk in the same toy ice.

Photons leave a straight muon track (the z axis) at the Cherenkov angle, then scatter (Henyey-Greenstein,
g = 0.9, geometric scattering length lambda_e (1 - g)) and are absorbed (weight exp(-path / lambda_a)) in
homogeneous ice with the SPICE-averaged lengths of constants.py. Because an infinite track looks the same
at every height, one emission point stands for all of them: a step at (rho, z) counts for a sensor at
distance rho, and its delay is measured against that sensor's direct-light time (z + rho tan theta_c) / c.

Two comparisons, both "how wrong is our shortcut inside our own toy ice", not a check against IceCube:
  * light reaching distance rho (track-length estimator) vs the diffusion formula K0(rho / L) / (2 pi D);
  * the delay distribution at a few distances vs the Pandel delay used in the sweep (whose parameters are
    AMANDA's fitted values, not derived from these lengths, so they are not expected to agree exactly).
"""
import numpy as np
from scipy.special import k0

from . import constants as K
from .light import PANDEL_RATE, TAN_C, THETA_C, pandel_shape

G = 0.9                      # mean scattering cosine of South Pole ice (icecube/ppc cfg.txt: g = 0.9) [verified]
RHO_EDGES = np.arange(0.0, 205.0, 5.0)
DELAY_EDGES = np.linspace(0.0, 3000.0, 61)
CHECK_DISTANCES_M = (20.0, 50.0, 100.0)


def walk(n_photons=200_000, seed=3, max_path_m=None):
    rng = np.random.default_rng(seed)
    lam_s = K.LAMBDA_E_M * (1 - G)
    max_path_m = max_path_m or 8 * K.LAMBDA_ABS_M
    phi = rng.uniform(0, 2 * np.pi, n_photons)
    st, ct = np.sin(THETA_C), np.cos(THETA_C)
    d = np.column_stack([st * np.cos(phi), st * np.sin(phi), np.full(n_photons, ct)])
    x = np.zeros((n_photons, 3))
    path = np.zeros(n_photons)
    nr, nt = len(RHO_EDGES) - 1, len(DELAY_EDGES) - 1
    flu = np.zeros(nr)
    hist = np.zeros((nr, nt))
    alive = np.arange(n_photons)
    while alive.size:
        s = -lam_s * np.log(rng.random(alive.size))
        mid = x[alive] + 0.5 * s[:, None] * d[alive]
        pm = path[alive] + 0.5 * s
        w = s * np.exp(-pm / K.LAMBDA_ABS_M)
        rho = np.hypot(mid[:, 0], mid[:, 1])
        delay = pm * K.N_ICE / K.C_VAC - (mid[:, 2] + rho * TAN_C) / K.C_VAC
        ir = np.searchsorted(RHO_EDGES, rho, side="right") - 1
        ok = ir < nr
        np.add.at(flu, ir[ok], w[ok])
        it = np.searchsorted(DELAY_EDGES, delay, side="right") - 1
        ok2 = ok & (it >= 0) & (it < nt)
        np.add.at(hist, (ir[ok2], it[ok2]), w[ok2])
        x[alive] += s[:, None] * d[alive]
        path[alive] += s
        # Henyey-Greenstein scattering
        u = rng.random(alive.size)
        cs = (1 + G * G - ((1 - G * G) / (1 - G + 2 * G * u)) ** 2) / (2 * G)
        sn = np.sqrt(np.clip(1 - cs * cs, 0, None))
        ps = rng.uniform(0, 2 * np.pi, alive.size)
        dv = d[alive]
        a = np.where(np.abs(dv[:, 2:3]) < 0.9, [[0, 0, 1.0]], [[1.0, 0, 0]])
        e1 = np.cross(dv, a)
        e1 /= np.linalg.norm(e1, axis=1)[:, None]
        e2 = np.cross(dv, e1)
        d[alive] = cs[:, None] * dv + sn[:, None] * (np.cos(ps)[:, None] * e1 + np.sin(ps)[:, None] * e2)
        far = np.hypot(x[alive, 0], x[alive, 1]) > RHO_EDGES[-1] + 50
        alive = alive[(path[alive] < max_path_m) & ~far]
    rc = 0.5 * (RHO_EDGES[1:] + RHO_EDGES[:-1])
    fluence = flu / (n_photons * 2 * np.pi * rc * np.diff(RHO_EDGES))
    return rc, fluence, hist


def diffusion_fluence(rho):
    D = K.LAMBDA_E_M / 3.0
    return k0(np.maximum(rho, K.D_MIN_M) / K.diffusion_length_m()) / (2 * np.pi * D)


def pandel_pdf(t, rho):
    from scipy.stats import gamma
    return gamma.pdf(t, pandel_shape(rho), scale=1 / PANDEL_RATE)


def fit_pandel(rc, hist, rmin=10.0, rmax=150.0):
    """Pandel (lambda, tau) that best describe the walk's delays from rmin to rmax (lambda_a fixed to our
    ice's absorption length): minimise the mean cross-entropy, each distance bin weighted equally."""
    from scipy.optimize import minimize
    from scipy.stats import gamma
    tc = 0.5 * (DELAY_EDGES[1:] + DELAY_EDGES[:-1])
    sel = [i for i, r in enumerate(rc) if rmin <= r <= rmax and hist[i].sum() > 0]
    rate_abs = (K.C_VAC / K.N_ICE) / K.LAMBDA_ABS_M

    def loss(p):
        lam, tau = np.exp(p)
        tot = 0.0
        for i in sel:
            pdf = gamma.pdf(tc, rc[i] / np.sin(THETA_C) / lam, scale=1 / (1 / tau + rate_abs))
            pdf = pdf / max(pdf.sum(), 1e-300)
            tot -= (hist[i] / hist[i].sum()) @ np.log(np.maximum(pdf, 1e-300))
        return tot / len(sel)

    r = minimize(loss, np.log([K.PANDEL_LAMBDA_M, K.PANDEL_TAU_NS]), method="Nelder-Mead")
    lam, tau = np.exp(r.x)
    return dict(lambda_m=float(lam), tau_ns=float(tau), lambda_a_m=K.LAMBDA_ABS_M, fit_range_m=[rmin, rmax])


def run(n_photons=200_000, seed=3):
    rc, flu, hist = walk(n_photons, seed)
    tc = 0.5 * (DELAY_EDGES[1:] + DELAY_EDGES[:-1])
    out = dict(label="our toy model, trend only", n_photons=n_photons, g=G,
               rho_m=rc.tolist(), fluence_walk=flu.tolist(), fluence_diffusion=diffusion_fluence(rc).tolist(),
               delay_ns=tc.tolist(), delay_pdf_walk={}, delay_pdf_pandel={}, summary={},
               pandel_fitted_to_walk=fit_pandel(rc, hist),
               pandel_literature=dict(lambda_m=K.PANDEL_LAMBDA_M, tau_ns=K.PANDEL_TAU_NS,
                                      lambda_a_m=K.PANDEL_LAMBDA_A_M))
    for r in CHECK_DISTANCES_M:
        i = int(np.searchsorted(RHO_EDGES, r, side="right") - 1)
        h = hist[i] / (hist[i].sum() * np.diff(DELAY_EDGES))
        p = pandel_pdf(tc, rc[i])
        cdf_w, cdf_p = np.cumsum(h) * np.diff(DELAY_EDGES), np.cumsum(p) * np.diff(DELAY_EDGES)
        key = f"{r:g}"
        out["delay_pdf_walk"][key] = h.tolist()
        out["delay_pdf_pandel"][key] = p.tolist()
        out["summary"][key] = dict(
            rho_bin_centre_m=float(rc[i]),
            fluence_ratio_walk_over_diffusion=float(flu[i] / diffusion_fluence(rc[i])),
            median_delay_walk_ns=float(np.interp(0.5, cdf_w, tc)),
            median_delay_pandel_ns=float(np.interp(0.5, cdf_p / cdf_p[-1], tc)))
    return out
