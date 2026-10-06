"""Direction reconstruction: the closed-form line fit, then a single-photoelectron Pandel likelihood fit
seeded by it. Toy versions of the two classic first steps (in outline only; real reconstructions use far
richer likelihoods, ice tables and machine learning).
"""
import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln

from . import constants as K
from .events import perp_basis
from .light import PANDEL_RATE, direct_time, pandel_shape, track_coords

LOG_RATE = np.log(PANDEL_RATE)


def line_fit(r, t):
    """Least-squares fit of r_i = r0 + v t_i (each hit treated as a point moving at constant velocity).
    Closed form (Stokstad's "line fit"): v = sum (r_i - <r>)(t_i - <t>) / sum (t_i - <t>)^2.
    Returns (unit direction, the point <r>, |v| in m/ns)."""
    rb, tb = r.mean(0), t.mean()
    dt = t - tb
    v = ((r - rb) * dt[:, None]).sum(0) / (dt @ dt)
    speed = np.linalg.norm(v)
    return v / speed, rb, speed


def pandel_logpdf(tres, d):
    """Log of the single-photon Pandel delay pdf (gamma with shape r/lambda, rate 1/tau + c_ice/lambda_a),
    patched for the fit: flat below FIT_EARLY_SIGMA_NS (the pdf diverges at 0 for short distances),
    a Gaussian tail of width FIT_EARLY_SIGMA_NS for early hits, and a small floor for outliers."""
    xi = pandel_shape(d)
    s = K.FIT_EARLY_SIGMA_NS
    tt = np.maximum(tres, s)
    lp = xi * LOG_RATE + (xi - 1) * np.log(tt) - PANDEL_RATE * tt - gammaln(xi)
    early = np.minimum(tres, 0.0)
    lp = lp - 0.5 * (early / s) ** 2
    return np.logaddexp(lp, np.log(K.FIT_NOISE_FLOOR))


class PandelFit:
    """Negative log-likelihood over 5 parameters around a seed track: two small tilts of the direction
    (alpha, beta), a shift of the track in the plane perpendicular to the seed (a, b, metres) and the time
    t0 (ns) when the muon passes the shifted point."""

    def __init__(self, r, t, u_seed, p_seed):
        self.r, self.t = r, t
        self.u0, self.p0 = u_seed, p_seed
        self.e1, self.e2 = perp_basis(u_seed)

    def track(self, x):
        u = self.u0 + x[0] * self.e1 + x[1] * self.e2
        u = u / np.linalg.norm(u)
        return u, self.p0 + x[2] * self.e1 + x[3] * self.e2

    def nll(self, x):
        u, p = self.track(x)
        l, d = track_coords(self.r, p, u)
        tres = self.t - x[4] - direct_time(l, d)
        return -pandel_logpdf(tres, d).sum()


def pandel_fit(r, t, u_seed, p_seed):
    """Minimise the Pandel negative log-likelihood from the line-fit seed (Nelder-Mead, then one restart
    from the best point). The seed time t0 comes from a 1-D scan with the seed track held fixed."""
    f = PandelFit(r, t, u_seed, p_seed)
    l, d = track_coords(r, p_seed, u_seed)
    res0 = t - direct_time(l, d)
    grid = np.quantile(res0, np.linspace(0.0, 0.5, 26))
    t0 = grid[np.argmin([f.nll(np.array([0, 0, 0, 0, g])) for g in grid])]
    x = np.array([0.0, 0.0, 0.0, 0.0, t0])
    step = np.array([0.05, 0.05, 10.0, 10.0, 20.0])
    best = None
    for scale in (1.0, 0.3):
        simplex = np.vstack([x, x + np.diag(step * scale)])
        r_ = minimize(f.nll, x, method="Nelder-Mead",
                      options=dict(initial_simplex=simplex, maxiter=3000, xatol=1e-4, fatol=1e-4))
        if best is None or r_.fun <= best.fun:
            best = r_
        x = best.x
    u, p = f.track(best.x)
    return u, p, best


def angle_deg(u, v):
    return float(np.degrees(np.arccos(np.clip(np.dot(u, v), -1.0, 1.0))))
