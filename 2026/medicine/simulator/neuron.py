"""Hodgkin-Huxley point neuron driven by a photocycle model; pulse-train following. Toy model.

Classic Hodgkin & Huxley 1952 squid-axon parameters (rest about -65 mV), our own NumPy code, with the
gate rates sped up 3x (PHI_T, equivalent to 16.3 C instead of 6.3 C; our choice, see README).
All conditions of one switch are integrated together, vectorised, with a fixed step of 0.01 ms (DT),
explicit midpoint rule (2nd-order Runge-Kutta). Every light edge is snapped to the step grid, so the light is constant inside each step:
this is the fixed-step form of the piecewise integration that data-and-tools.md asks for.
The step was chosen by convergence: at 0.01 ms the headline rates, and every following fraction up to
them, equal those at 0.005 ms (one fraction far above a first failure moves by two pulses; run_all
writes the check to run_summary.json). The earlier forward-Euler 0.025 ms step was not converged.
"""
from dataclasses import replace

import numpy as np

from . import opsin

DT = 0.01
DT_CHECK = 0.005  # finer step used by run_all to show the rates no longer move
C_M, G_NA, G_K, G_L, E_NA, E_K, E_L = 1.0, 120.0, 36.0, 0.3, 50.0, -77.0, -54.387
V_REST = -65.0
PHI_T = 3.0  # HH gate-rate factor 3**((T-6.3)/10): 3 = 16.3 C. Our choice (classic squid model is 6.3 C)


def _rates(V):
    am = 0.1 * (V + 40) / (1 - np.exp(-(V + 40) / 10))
    bm = 4 * np.exp(-(V + 65) / 18)
    ah = 0.07 * np.exp(-(V + 65) / 20)
    bh = 1 / (1 + np.exp(-(V + 35) / 10))
    an = 0.01 * (V + 55) / (1 - np.exp(-(V + 55) / 10))
    bn = 0.125 * np.exp(-(V + 65) / 80)
    return am * PHI_T, bm * PHI_T, ah * PHI_T, bh * PHI_T, an * PHI_T, bn * PHI_T


def pulse_mask(rates_hz, n_pulses, pulse_ms, irradiance, t_pad=60.0, dt=None):
    """Light (mW/mm^2) on the step grid, shape (n_steps, n_conditions), plus pulse onset steps."""
    dt = dt or DT
    rates_hz = np.atleast_1d(rates_hz).astype(float)
    t_end = max(n_pulses * 1000.0 / r for r in rates_hz) + t_pad
    n = int(np.ceil(t_end / dt))
    light = np.zeros((n, len(rates_hz)), dtype=np.float32)
    onsets = []
    w = int(round(pulse_ms / dt))
    for j, r in enumerate(rates_hz):
        on = np.round(20.0 / dt + np.arange(n_pulses) * (1000.0 / r) / dt).astype(int)
        for s in on:
            light[s:s + w, j] = irradiance
        onsets.append(on)
    return light, onsets


def simulate(sw, light, g, clamp_V=None, dt=None, record=True):
    """Integrate. light: (n_steps, n_cond) irradiance (mW/mm^2) on a grid of step dt (default DT), or a
    tuple (mask, idx, level): column j sees mask[:, idx[j]] * level[j] (mask bool, n_steps x n_patterns;
    saves memory for big batches). g: conductance density (mS/cm^2).
    record=True: returns V trace (n_steps, n_cond) and photocurrent density (uA/cm^2, inward negative).
    record=False: returns only the spike steps per column (upward 0 mV crossings, as spikes())."""
    step = dt or DT
    if isinstance(light, tuple):
        mask, idx, level = light
        n, k = mask.shape[0], len(idx)
        light_at = lambda i: mask[i, idx] * level
    else:
        (n, k), light_at = light.shape, light.__getitem__
    V = np.full(k, V_REST if clamp_V is None else clamp_V, float)
    am, bm, ah, bh, an, bn = _rates(V)
    m, h, nn = am / (am + bm), ah / (ah + bh), an / (an + bn)
    y = np.zeros((4, k))
    if record:
        Vs = np.empty((n, k), np.float32)
        Is = np.empty((n, k), np.float32)
    events = []

    def deriv(V, m, h, nn, y, I):
        i_op = g * opsin.open_fraction(sw, y) * opsin.drive(sw, V)
        dy = opsin.rhs(sw, y, V, I)
        if clamp_V is not None:
            return 0.0, 0.0, 0.0, 0.0, dy, i_op
        am, bm, ah, bh, an, bn = _rates(V)
        i_ion = G_NA * m**3 * h * (V - E_NA) + G_K * nn**4 * (V - E_K) + G_L * (V - E_L)
        return (-(i_ion + i_op) / C_M, am - (am + bm) * m, ah - (ah + bh) * h, an - (an + bn) * nn, dy, i_op)

    half = 0.5 * step
    for i in range(n):  # explicit midpoint (2nd-order Runge-Kutta); the light is constant inside a step
        I = light_at(i)
        dV, dm, dh, dn, dy, i_op = deriv(V, m, h, nn, y, I)
        dV, dm, dh, dn, dy, _ = deriv(V + half * dV, m + half * dm, h + half * dh, nn + half * dn, y + half * dy, I)
        V_old = V
        V, m, h, nn, y = V + step * dV, m + step * dm, h + step * dh, nn + step * dn, y + step * dy
        if record:
            Vs[i], Is[i] = V, i_op
        elif i:
            up = np.nonzero((V >= 0) & (V_old < 0))[0]
            if up.size:
                events.append((i, up))
    if record:
        return Vs, Is
    out = [[] for _ in range(k)]
    for i, cols in events:
        for c in cols:
            out[c].append(i)
    return [np.array(o, int) for o in out]


def spikes(Vtrace, threshold=0.0):
    up = (Vtrace[1:] >= threshold) & (Vtrace[:-1] < threshold)
    return [np.nonzero(up[:, j])[0] + 1 for j in range(Vtrace.shape[1])]


def scale_conductance(sw, irradiance, pulse_ms, target_peak=15.0, dt=None):
    """Conductance density giving a peak photocurrent of target_peak uA/cm^2 for one pulse at -65 mV.
    Used so every switch has the same peak current: the comparison then isolates kinetics."""
    dt = dt or DT
    light, _ = pulse_mask([1.0], 1, pulse_ms, irradiance, t_pad=0.0, dt=dt)
    light = light[: int(round((20 + pulse_ms + 30) / dt))]
    _, Is = simulate(sw, light, 1.0, clamp_V=V_REST, dt=dt)
    return target_peak / abs(Is.min())


def following(sws, rates_hz, irradiance=3.0, pulse_ms=2.0, n_pulses=20, fidelity=0.95, target_peak=15.0, dt=None):
    """Fraction of pulses followed by exactly one spike, per rate, and the headline following rate.

    'Following' at one rate = at least `fidelity` of the pulses each produce exactly one spike before the
    next pulse (with 20 pulses and 95 %, exactly one miss is allowed). The headline speed (max_rate) is the
    highest tested rate up to which EVERY tested rate follows: the first failure ends the run.
    Rates above the first failure that follow again are returned in `follows_again_Hz`: in this toy cell
    they are a resonance of the squid-axon neuron model, not a property of the light switch.
    Switches of the same model kind are integrated in one vectorised run (their parameters become
    per-column arrays). Returns {name: dict(rates, fraction, max_rate, first_failure_Hz, follows_again_Hz, g)}."""
    dt = dt or DT
    rates_hz = list(rates_hz)
    light1, onsets = pulse_mask(rates_hz, n_pulses, pulse_ms, irradiance, dt=dt)
    out = {}
    for kind in ("williams", "pyrho"):
        group = [s for s in sws if s.kind == kind]
        if not group:
            continue
        gs = [scale_conductance(s, irradiance, pulse_ms, target_peak, dt) for s in group]
        rep = lambda vals: np.repeat(np.asarray(vals, float), len(rates_hz))
        batch = replace(group[0], wavelength=rep([s.wavelength for s in group]),
                        gd_scale=rep([s.gd_scale for s in group]))
        Vs, _ = simulate(batch, np.tile(light1, (1, len(group))), rep(gs), dt=dt)
        sp_all = spikes(Vs)
        for gi, s in enumerate(group):
            frac = []
            for j in range(len(rates_hz)):
                sp, on = sp_all[gi * len(rates_hz) + j], onsets[j]
                edges = np.append(on, on[-1] + (on[1] - on[0] if n_pulses > 1 else len(Vs)))
                counts = np.histogram(sp, bins=edges)[0]
                frac.append((counts == 1).mean() if (sp < on[0]).sum() == 0 else 0.0)
            frac = np.array(frac)
            max_rate, first_fail, again = headline(rates_hz, frac, fidelity)
            out[s.name] = dict(rates=np.asarray(rates_hz, float), fraction=frac, max_rate=max_rate,
                               first_failure_Hz=first_fail, follows_again_Hz=again, g=gs[gi])
    return out


def headline(rates_hz, fraction, fidelity=0.95):
    """(headline rate, first failing rate, rates above the first failure that follow again).
    Headline = highest tested rate up to which every tested rate follows; 0 if the lowest rate fails."""
    ok = np.asarray(fraction) >= fidelity
    n_ok = len(ok) if ok.all() else int(np.argmin(ok))
    max_rate = float(rates_hz[n_ok - 1]) if n_ok else 0.0
    first_fail = float(rates_hz[n_ok]) if n_ok < len(ok) else None
    return max_rate, first_fail, [float(r) for r, o in zip(rates_hz[n_ok:], ok[n_ok:]) if o]


RATES_HZ = (10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 175, 200)
