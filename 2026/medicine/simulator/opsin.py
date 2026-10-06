"""Four-state photocycle models of light-gated channels (C1, O1, O2, C2). Educational demo, toy model.

Two published ChR2 parameter sets, restated with citation (see SOURCES.md):
  * Williams et al. 2013, PLoS Comput Biol 9:e1003220, Table 1 (CC BY). ChR2(H134R), 22 C values.
  * PyRhO (Evans et al. 2016), pyrho/parameters.py, modelFits['4']['ChR2'] (BSD-3-Clause).
Two SIMPLIFIED switches built on the Williams structure, where only the two closing rates (Gd1, Gd2)
are rescaled so the model's off time constant after a 2 ms pulse matches a published tau_off
(Klapoetke et al. 2014, Nat Methods 11:338): Chronos 3.6 ms, ChrimsonR 15.8 ms. Everything else
(light sensitivity, desensitisation, recovery) is borrowed from ChR2 - a strong simplification.

Light is given as irradiance I in mW/mm^2 at wavelength lam_nm. States y = [O1, O2, C2, p];
for PyRhO p is unused. Current density: i = g * (O1 + gamma*O2) * f(V)*(V - E)  [uA/cm^2 if g in mS/cm^2].
"""
from dataclasses import dataclass, field, replace

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

HC = 1.986446e-25  # J m (Williams 2013 Table 1)


@dataclass(frozen=True)
class Switch:
    name: str
    kind: str  # "williams" or "pyrho"
    wavelength: float  # drive wavelength used in this demo, nm
    status: str  # "published" or "simplified"
    gd_scale: float = 1.0  # multiplies Gd1, Gd2 (simplified switches only)
    tau_off_target_ms: float = float("nan")
    note: str = ""
    p: dict = field(default_factory=dict)


WILLIAMS = dict(
    eps1=0.8535, eps2=0.14, sigma_ret=12e-20, w_loss=0.77, tau_chr=1.3, gamma=0.1,
    e12d=0.011, c1_12=0.005, c2_12=0.024, e21d=0.008, c1_21=0.004, c2_21=0.024, gd2=0.05,
    # Table 1 prints Gr = 4.34587 * 10^5 * exp(-0.0211539274 V). With 10^+5 the recovery would take
    # nanoseconds, contradicting the paper's seconds-long recovery and its quoted comparison values
    # (0.004; 0.0004 ms^-1). We read it as 10^-5 (our interpretation, flagged in SOURCES.md).
    gr_a=4.34587e-5, gr_b=-0.0211539274, E=0.0,
)
PYRHO = dict(
    gam=0.00742, phi_m=2.33e17, k1=4.15, k2=0.868, p=0.833, Gf0=0.0373, k_f=0.0581, Gb0=0.0161,
    k_b=0.063, q=1.94, Gd1=0.105, Gd2=0.0138, Gr0=0.00033, E=0.0, v0=43.0, v1=17.1,
)


def flux_williams(I, lam_nm, p=WILLIAMS):
    """Photons per molecule per ms: sigma_ret*I/(E_ph*w_loss) (Williams 2013, = 0.0006*I*lam/w_loss)."""
    return p["sigma_ret"] * (I * 1e3) * (lam_nm * 1e-9) / HC / p["w_loss"] * 1e-3


def photon_flux_per_mm2_s(I, lam_nm):
    """Irradiance (mW/mm^2) to photons/mm^2/s, the unit PyRhO's phi_m uses."""
    return I * 1e-3 * lam_nm * 1e-9 / HC


def gd1_williams(V):
    return 0.075 + 0.043 * np.tanh((V + 20) / -20)


def rhs(sw, y, V, I):
    """Time derivative (per ms) of [O1, O2, C2, p] at voltage V (mV) and irradiance I (mW/mm^2)."""
    O1, O2, C2, pp = y[0], y[1], y[2], y[3]
    C1 = 1 - O1 - O2 - C2
    if sw.kind == "williams":
        w = WILLIAMS
        F = flux_williams(I, sw.wavelength)
        k1, k2 = w["eps1"] * F * pp, w["eps2"] * F * pp
        gd1, gd2 = gd1_williams(V) * sw.gd_scale, w["gd2"] * sw.gd_scale
        gr = w["gr_a"] * np.exp(w["gr_b"] * V)
        e12 = w["e12d"] + w["c1_12"] * np.log1p(I / w["c2_12"])
        e21 = w["e21d"] + w["c1_21"] * np.log1p(I / w["c2_21"])
        s0 = 0.5 * (1 + np.tanh(120 * (100 * I - 0.1)))
        dp = (s0 - pp) / w["tau_chr"]
    else:
        q = PYRHO
        phi = photon_flux_per_mm2_s(I, sw.wavelength)
        hp = phi ** q["p"] / (phi ** q["p"] + q["phi_m"] ** q["p"])
        hq = phi ** q["q"] / (phi ** q["q"] + q["phi_m"] ** q["q"])
        k1, k2 = q["k1"] * hp, q["k2"] * hp
        e12, e21 = q["k_f"] * hq + q["Gf0"], q["k_b"] * hq + q["Gb0"]
        gd1, gd2, gr = q["Gd1"] * sw.gd_scale, q["Gd2"] * sw.gd_scale, q["Gr0"]
        dp = 0 * pp
    dO1 = k1 * C1 - (gd1 + e12) * O1 + e21 * O2
    dO2 = k2 * C2 + e12 * O1 - (gd2 + e21) * O2
    dC2 = gd2 * O2 - (k2 + gr) * C2
    return np.array([dO1, dO2, dC2, dp])


def open_fraction(sw, y):
    g = WILLIAMS["gamma"] if sw.kind == "williams" else PYRHO["gam"]
    return y[0] + g * y[1]


def drive(sw, V):
    """f(V)*(V-E) in mV for the model's rectification (E = 0 for both sets)."""
    if sw.kind == "williams":
        return 10.6408 - 14.6408 * np.exp(-V / 42.7671)  # G(V)*(V-E), Williams 2013 Table 1
    q = PYRHO
    return q["v1"] * (1 - np.exp(-(V - q["E"]) / q["v0"]))  # f_v*(V-E), PyRhO RhO_4states


DARK = np.array([0.0, 0.0, 0.0, 0.0])


def clamp_trace(sw, segments, V=-70.0, dt_out=0.05, y0=DARK):
    """Voltage-clamp photocycle with piecewise integration.

    segments: list of (duration_ms, irradiance). Each constant-light segment is integrated on its own
    (an adaptive solver otherwise steps straight over a short pulse defined inside the RHS).
    Returns t (ms), open fraction, states.
    """
    ts, ys, t0, y = [], [], 0.0, np.array(y0, float)
    for dur, I in segments:
        if dur <= 0:  # a zero-length segment (e.g. a 0 ms off-time) changes nothing
            continue
        n = max(2, int(round(dur / dt_out)) + 1)
        sol = solve_ivp(lambda t, s: rhs(sw, s, V, I), (0, dur), y, method="LSODA",
                        t_eval=np.linspace(0, dur, n), rtol=1e-8, atol=1e-10)
        ts.append(sol.t[:-1] + t0)
        ys.append(sol.y[:, :-1])
        y = sol.y[:, -1]
        t0 += dur
    t = np.concatenate(ts + [[t0]])
    Y = np.concatenate(ys + [y[:, None]], axis=1)
    return t, open_fraction(sw, Y), Y


def tau_off(sw, I=5.0, pulse_ms=2.0, V=-70.0):
    """Mono-exponential off time constant after a short pulse (Klapoetke 2014 Methods: 2 ms pulses)."""
    t, o, _ = clamp_trace(sw, [(10.0, 0.0), (pulse_ms, I), (150.0, 0.0)], V=V, dt_out=0.02)
    m = t >= 10.0 + pulse_ms
    tt, oo = t[m] - t[m][0], o[m]
    keep = oo > oo[0] * 0.02
    return -1.0 / np.polyfit(tt[keep], np.log(oo[keep]), 1)[0]


def calibrate(sw):
    """Find gd_scale so that tau_off matches sw.tau_off_target_ms."""
    f = lambda s: tau_off(replace(sw, gd_scale=s)) - sw.tau_off_target_ms
    guess = tau_off(replace(sw, gd_scale=1.0)) / sw.tau_off_target_ms
    return replace(sw, gd_scale=brentq(f, 0.6 * guess, 1.6 * guess, xtol=1e-4))


def switches(calibrated=True):
    base = [
        Switch("ChR2 (Williams 2013)", "williams", 470, "published",
               note="ChR2(H134R) 4-state, Table 1, 22 C values"),
        Switch("ChR2 (PyRhO fit)", "pyrho", 470, "published",
               note="PyRhO modelFits['4']['ChR2']"),
        Switch("Chronos (simplified)", "williams", 470, "simplified", tau_off_target_ms=3.6,
               note="Williams structure, closing rates rescaled to tau_off 3.6 ms (Klapoetke 2014)"),
        Switch("ChrimsonR (simplified)", "williams", 590, "simplified", tau_off_target_ms=15.8,
               note="Williams structure, closing rates rescaled to tau_off 15.8 ms (Klapoetke 2014); "
                    "driven at 590 nm, Chrimson's peak"),
    ]
    return [calibrate(s) if calibrated and s.status == "simplified" else s for s in base]
