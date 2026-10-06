"""Shared pieces: B's cached light maps, B's heat model scaled by power, figure saving. Toy model.

Nothing here re-implements physics: light comes from simulator.light (cached .npz maps), warming from
simulator.heat.Grid (Pennes bioheat). The heat model is linear in power, so one solve per colour at
1 mW is scaled to any power.
"""
from functools import lru_cache
from pathlib import Path

import numpy as np

from simulator import heat, light
from simulator.common import (DEMO_TAG, RESULTS as SIM_RESULTS, THEMES, WAVELENGTH_COLOURS,  # noqa: F401
                              apply_theme, titles)

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
LIMITS_C = (0.5, 1.0, 2.0)
DEFAULT_LIMIT_C = 1.0
TOP_LINE = "Educational demo, toy model. Not research, not for lab or clinical use."


@lru_cache(maxsize=None)
def light_map(wl):
    """B's light map at one colour: fluence per watt (W/mm^2 per W = mW/mm^2 per mW) on the r-z grid.
    Uses B's cached file; if it is missing, runs B's Monte Carlo with B's settings (200 000 photons)."""
    path = SIM_RESULTS / f"light_fibre200um_{wl}nm.npz"
    if not path.exists():
        light.run(200_000, (wl,), seed=light.WAVELENGTHS.index(wl))
    d = np.load(path)
    return dict(r_edges=d["r_edges"], z_edges=d["z_edges"], fluence=d["fluence_per_W"].astype(float),
                mua=float(d["meta"][3]))


@lru_cache(maxsize=None)
def grid():
    m = light_map(light.WAVELENGTHS[0])
    return heat.Grid(m["r_edges"], m["z_edges"])


def source_per_mW(wl):
    """Absorbed power density (W/mm^3) for 1 mW leaving the fibre: fluence x mu_a (B's heat source)."""
    m = light_map(wl)
    return m["fluence"] * m["mua"] * 1e-3


@lru_cache(maxsize=None)
def steady_per_mW(wl):
    """Steady warming at the hottest point (C) per mW of continuous light (B's Pennes model)."""
    return float(grid().steady(source_per_mW(wl)).max())


@lru_cache(maxsize=None)
def single_pulse_rise(wl, t_max_ms=10.0, dt_ms=0.05):
    """Peak warming (C per mW) at the end of ONE pulse of each length up to t_max_ms, from rest
    (B's backward-Euler transient). Returns (times_ms, peak_C_per_mW)."""
    tt, pk, _, _ = grid().transient(source_per_mW(wl), [(t_max_ms * 1e-3, 1.0)], dt_ms * 1e-3)
    return tt * 1e3, pk


def warming_C(wl, peak_mW, width_ms, rate_hz):
    """Estimated peak warming at the hottest point for a long pulse train (run until steady, ~1 min).

    By linearity: (steady warming of the AVERAGE power) + (rise during one pulse), capped at the
    continuous-light steady value at the same peak power. This is an upper estimate: it adds the full
    one-pulse rise on top of the mean, and pulses cannot heat more than continuous light at peak power.
    """
    tt, pk = single_pulse_rise(wl)
    width_ms = np.asarray(width_ms, float)
    if np.any(width_ms > tt[-1] + 1e-6):
        raise ValueError(f"pulse widths above {tt[-1]} ms need a longer single_pulse_rise run")
    duty = np.minimum(width_ms * np.asarray(rate_hz, float) / 1000.0, 1.0)
    k = steady_per_mW(wl)
    return np.asarray(peak_mW, float) * np.minimum(duty * k + np.interp(width_ms, tt, pk), k)


def save_themed(make_fig, stem, dpi=200):
    """make_fig(theme) -> Figure; saved as results/<stem>_{light,dark}.png."""
    import matplotlib.pyplot as plt

    RESULTS.mkdir(parents=True, exist_ok=True)
    paths = []
    for theme in ("light", "dark"):
        fig = make_fig(theme)
        p = RESULTS / f"{stem}_{theme}.png"
        fig.savefig(p, dpi=dpi, facecolor=fig.get_facecolor())
        plt.close(fig)
        paths.append(p)
    return paths
