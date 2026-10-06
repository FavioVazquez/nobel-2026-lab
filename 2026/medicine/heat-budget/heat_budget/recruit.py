"""A population of neurons in 3D: how many does each mW, and each degree of warming, recruit? Toy model.

* Somata are scattered at a uniform density (DENSITY_PER_MM3, Keller, Ero & Markram 2018, Table 1,
  "Cortex (General)", which cites Schuz & Palm 1989) over B's whole light grid (25 um cells to 6 mm,
  then growing cells to about 45 mm), minus the fibre body (r < 0.1 mm above the tip).
* HEADLINE_COLOURS (470, 590 nm) are the headline pair. 635 nm is reported only as a labelled toy upper
  bound: no absorption outside blood, no 635 nm switch (ChR2's sensitivity and threshold), and a uniform
  block far larger than a thin cortex.
* Each neuron gets a relative expression level e, lognormal with median 1 and log-spread SIGMA
  (an ASSUMPTION; the result is shown for SIGMAS).
* A neuron is recruited when (light at its cell of B's fluence map) x e >= THRESHOLD (3 mW/mm^2, B's
  one illustrative activation level). So neuron i is recruited at fibre power P >= THRESHOLD / (e_i phi_i).
* Warming = P x (steady C per mW at the hottest point, B's Pennes model): continuous light.

Sampling is exact and cheap: per grid cell, only the neurons that can be recruited at the top power are
drawn (a thinned Poisson process: count ~ Poisson(density x volume x P(e >= cut)), expression from the
lognormal tail above the cut). Every count below the top power is then exact for that sample.
"""
import json

import numpy as np
from scipy.stats import norm

from simulator import light
from simulator.tradeoff import THRESHOLD

from .common import DEMO_TAG, LIMITS_C, RESULTS, WAVELENGTH_COLOURS, apply_theme, light_map, save_themed, steady_per_mW

DENSITY_PER_MM3 = 92_000.0
SIGMAS = (0.25, 0.5, 1.0)
SIGMA = 0.5
WAVELENGTHS = light.WAVELENGTHS
HEADLINE_COLOURS = (470, 590)
UPPER_BOUND_NOTE = ("635 nm: toy upper bound only (no absorption outside blood, no 635 nm switch, "
                    "uniform block much bigger than a thin cortex)")
CORE_MM = 0.1
N_POWERS = 121
SEED = 2026


def is_recruited(phi_mW_mm2, expression, threshold=THRESHOLD):
    """A neuron fires when its light level times its relative expression reaches the threshold."""
    return np.asarray(phi_mW_mm2) * np.asarray(expression) >= threshold


def tissue_cells(wl):
    """Flattened cells of B's grid that hold tissue and see light: fluence per mW, volume, edges, edge flag."""
    m = light_map(wl)
    r_e, z_e = m["r_edges"], m["z_edges"]
    rc, zc = 0.5 * (r_e[1:] + r_e[:-1]), 0.5 * (z_e[1:] + z_e[:-1])
    vol = light.cell_volumes(r_e, z_e)
    fibre = (rc[:, None] < CORE_MM) & (zc[None, :] < 0)
    keep = (~fibre) & (m["fluence"] > 0)
    ir, iz = np.nonzero(keep)
    near_edge = (r_e[ir + 1] > r_e[-1] - 0.5) | (z_e[iz] < z_e[0] + 0.5) | (z_e[iz + 1] > z_e[-1] - 0.5)
    return dict(phi=m["fluence"][keep], vol=vol[keep], r0=r_e[ir], r1=r_e[ir + 1], z0=z_e[iz], z1=z_e[iz + 1],
                near_edge=near_edge)


def expected_count(cells, powers, sigma=SIGMA, density=DENSITY_PER_MM3, threshold=THRESHOLD):
    """Expected number recruited at each power (exact mean of the model; used as a check on the sample)."""
    out = []
    for p in np.atleast_1d(powers):
        if p <= 0:
            out.append(0.0)
            continue
        out.append(float((density * cells["vol"] * norm.sf(np.log(threshold / (p * cells["phi"])) / sigma)).sum()))
    return np.array(out)


def sample(cells, p_max, sigma=SIGMA, density=DENSITY_PER_MM3, seed=SEED, threshold=THRESHOLD, positions=False):
    """Draw every neuron that is recruited at or below p_max. Returns recruitment power per neuron (mW),
    its expression and light per mW, and optionally positions (mm; z = depth below the tip)."""
    rng = np.random.default_rng(seed)
    cut = np.log(threshold / (p_max * cells["phi"])) / sigma
    prob = norm.sf(cut)
    n = rng.poisson(density * cells["vol"] * prob)
    c = np.repeat(np.arange(n.size), n)
    expr = np.exp(sigma * norm.isf(rng.random(c.size) * prob[c]))
    out = dict(p_star=threshold / (expr * cells["phi"][c]), expression=expr, phi_per_mW=cells["phi"][c],
               near_edge=cells["near_edge"][c])
    if positions:
        r = np.sqrt(cells["r0"][c] ** 2 + rng.random(c.size) * (cells["r1"][c] ** 2 - cells["r0"][c] ** 2))
        th = 2 * np.pi * rng.random(c.size)
        out.update(x=r * np.cos(th), y=r * np.sin(th),
                   z=cells["z0"][c] + rng.random(c.size) * (cells["z1"][c] - cells["z0"][c]))
    return out


def counts(p_star, powers):
    return np.searchsorted(np.sort(p_star), powers, side="right")


def run(density=DENSITY_PER_MM3, sigmas=SIGMAS, wavelengths=WAVELENGTHS, n_powers=N_POWERS, seed=SEED, figures=True):
    res = dict(tag=f"{DEMO_TAG}. Not research, not for lab or clinical use.",
               assumptions=dict(density_per_mm3=density, threshold_mW_mm2=THRESHOLD, expression="lognormal, median 1",
                                sigmas=list(sigmas), default_sigma=SIGMA, seed=seed,
                                warming="continuous light, steady state, hottest point (B's Pennes model)",
                                domain=f"B's light grid (r <= {light_map(wavelengths[0])['r_edges'][-1]:.1f} mm, "
                                       f"z {light_map(wavelengths[0])['z_edges'][0]:.1f}..{light_map(wavelengths[0])['z_edges'][-1]:.1f} mm) "
                                       "minus the fibre body",
                                headline_colours=list(HEADLINE_COLOURS), upper_bound_635nm=UPPER_BOUND_NOTE),
               colours={})
    for wl in wavelengths:
        cells = tissue_cells(wl)
        k = steady_per_mW(wl)
        p_lim = {lim: lim / k for lim in LIMITS_C}
        p_max = max(p_lim.values())
        powers = np.linspace(0, p_max, n_powers)
        entry = dict(C_per_mW=k, power_mW=powers.round(5).tolist(), warming_C=(powers * k).round(5).tolist(),
                     power_at_limit_mW={f"{l:g}": v for l, v in p_lim.items()}, by_sigma={})
        for j, s in enumerate(sigmas):
            pop = sample(cells, p_max, s, density, seed + 100 * j + wl)
            n_s = counts(pop["p_star"], powers)
            n_lim = counts(pop["p_star"], np.array(list(p_lim.values())))
            entry["by_sigma"][f"{s:g}"] = dict(
                recruited=n_s.tolist(), expected=expected_count(cells, powers, s, density).round(1).tolist(),
                at_limit={f"{l:g}": dict(recruited=int(n), per_mW=float(n / p_lim[l]), per_C=float(n / l))
                          for l, n in zip(LIMITS_C, n_lim)},
                share_near_grid_edge_at_top=float(pop["near_edge"].mean()) if pop["near_edge"].size else 0.0)
        res["colours"][str(wl)] = entry
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "recruitment.json").write_text(json.dumps(res, separators=(",", ":")))
    if figures:
        plot(res)
    return res


def plot(res):
    import matplotlib.pyplot as plt

    def make(theme):
        fig, axes = plt.subplots(2, 1, figsize=(8, 10), layout="constrained")
        t = apply_theme(fig, axes, theme)
        for wl, e in res["colours"].items():
            c = WAVELENGTH_COLOURS[int(wl)]
            by = e["by_sigma"]
            lo, mid, hi = (np.array(by[f"{s:g}"]["recruited"], float) for s in (min(SIGMAS), SIGMA, max(SIGMAS)))
            head = int(wl) in HEADLINE_COLOURS
            for ax, x in zip(axes, (np.array(e["power_mW"]), np.array(e["warming_C"]))):
                ax.fill_between(x, np.minimum(lo, hi), np.maximum(lo, hi), color=c, alpha=0.18 if head else 0.08, lw=0)
                ax.plot(x, mid, color=c, lw=3.2 if head else 2.0, ls="-" if head else "--",
                        label=f"{wl} nm" if head else f"{wl} nm: toy upper bound only")
            n1 = by[f"{SIGMA:g}"]["at_limit"]["1"]["recruited"]
            if head:
                axes[1].plot([1.0], [n1], "o", color=c, ms=9)
                axes[1].annotate(f"{n1:,.0f}", (1.0, n1), xytext=(10, 6 if int(wl) != 470 else -18), textcoords="offset points", color=c, fontsize=13,
                                 fontweight="bold")
        for ax in axes:
            ax.set_yscale("log")
            ax.set_ylim(1e2, None)
            ax.set_ylabel("Neurons recruited (log scale)", fontsize=15)
        axes[0].set_xscale("log")
        axes[0].set_xlim(0.1, None)
        axes[0].set_xlabel("Continuous light out of the fibre (mW, log scale)", fontsize=15)
        axes[1].set_xlim(0, max(LIMITS_C))
        axes[1].axvline(1.0, color=t["muted"], ls="--", lw=1.5)
        axes[1].set_xlabel("Warming at the hottest point (°C)", fontsize=15)
        leg = axes[0].legend(fontsize=14, frameon=False, loc="upper left")
        for txt in leg.get_texts():
            txt.set_color(t["fg"])
        fig.suptitle("How many neurons can one degree of warming buy?", fontsize=17, fontweight="bold", color=t["fg"],
                     x=0.02, ha="left")
        axes[0].set_title(f"{DEMO_TAG} · {res['assumptions']['density_per_mm3']:,.0f} neurons/mm³, one threshold "
                          f"({THRESHOLD:g} mW/mm²)\nlognormal expression: line spread {SIGMA:g}, band {min(SIGMAS):g} to "
                          f"{max(SIGMAS):g} · continuous light\nHeadline: 470 and 590 nm · dashed 635 nm: toy upper bound only\n"
                          "(no absorption outside blood, no 635 nm switch, block much bigger than a thin cortex)",
                          loc="left", color=t["muted"], fontsize=10.5, pad=10)
        return fig

    return save_themed(make, "recruit_vs_warming")
