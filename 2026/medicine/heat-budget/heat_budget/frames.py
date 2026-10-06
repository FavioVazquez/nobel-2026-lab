"""3D scatter PNG sequence: fibre power rises from 0 to the heat limit and neurons light up. Toy model.

    python -m heat_budget.frames                 # 60 frames, 1920x1080, results/recruit_frames/
    python -m heat_budget.frames --vertical      # 1080x1920, results/recruit_frames_vertical/
    python -m heat_budget.frames --colour 590 --limit 2

Only a thinned sample of neurons is drawn (1 in THIN, inside a 1 mm radius, 2 mm tall cylinder); the
count printed on each frame is the full-density count from recruit.py (whole light grid, same seed).
"""
import argparse

import numpy as np

from simulator.tradeoff import THRESHOLD

from . import recruit
from .common import DEFAULT_LIMIT_C, LIMITS_C, RESULTS, THEMES, WAVELENGTH_COLOURS, light_map, steady_per_mW

THIN = 40
R_SHOW, Z_TOP, Z_BOTTOM = 1.0, -0.45, 1.6  # mm; z is depth below the fibre tip
DIM = "#3a414b"


def display_population(wl, sigma=recruit.SIGMA, thin=THIN, seed=recruit.SEED + 7):
    """Uniform somata in the display cylinder at density/thin, each with its own expression and light."""
    rng = np.random.default_rng(seed)
    vol = np.pi * R_SHOW ** 2 * (Z_BOTTOM - Z_TOP)
    n = rng.poisson(recruit.DENSITY_PER_MM3 / thin * vol)
    r, th = R_SHOW * np.sqrt(rng.random(n)), 2 * np.pi * rng.random(n)
    z = Z_TOP + (Z_BOTTOM - Z_TOP) * rng.random(n)
    keep = ~((r < recruit.CORE_MM) & (z < 0))
    r, th, z = r[keep], th[keep], z[keep]
    m = light_map(wl)
    ir = np.searchsorted(m["r_edges"], r, side="right") - 1
    iz = np.searchsorted(m["z_edges"], z, side="right") - 1
    phi = m["fluence"][ir, iz]
    expr = np.exp(sigma * rng.standard_normal(r.size))
    with np.errstate(divide="ignore"):
        p_star = THRESHOLD / (expr * phi)
    return dict(x=r * np.cos(th), y=r * np.sin(th), z=z, p_star=p_star)


def render(wl=470, limit=DEFAULT_LIMIT_C, n_frames=60, vertical=False, sigma=recruit.SIGMA, out=None):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = out or RESULTS / ("recruit_frames_vertical" if vertical else "recruit_frames")
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("frame_*.png"):
        old.unlink()
    t = THEMES["dark"]
    col = WAVELENGTH_COLOURS[wl]
    k = steady_per_mW(wl)
    p_lim = limit / k
    pop = display_population(wl, sigma)
    # same draw as recruit.run (same top power and seed), so the frame counts match results/recruitment.json
    full = recruit.sample(recruit.tissue_cells(wl), max(LIMITS_C) / k, sigma,
                          seed=recruit.SEED + 100 * recruit.SIGMAS.index(sigma) + wl)
    powers = np.linspace(0, p_lim, n_frames)
    n_full = recruit.counts(full["p_star"], powers)
    w, h = (10.8, 19.2) if vertical else (19.2, 10.8)
    zz, tt = np.meshgrid(np.linspace(Z_TOP - 0.1, 0, 2), np.linspace(0, 2 * np.pi, 40))
    paths = []
    for i, p in enumerate(powers):
        fig = plt.figure(figsize=(w, h), dpi=100, facecolor=t["bg"])
        ax = fig.add_axes([-0.12, 0.2, 1.24, 0.72] if vertical else [0.18, -0.06, 0.82, 1.12], projection="3d")
        ax.set_facecolor(t["bg"])
        ax.set_axis_off()
        lit = pop["p_star"] <= p if p > 0 else np.zeros(pop["x"].size, bool)
        ax.scatter(pop["x"][~lit], pop["y"][~lit], -pop["z"][~lit], s=3, c=DIM, alpha=0.45, lw=0, depthshade=False)
        ax.scatter(pop["x"][lit], pop["y"][lit], -pop["z"][lit], s=70, c=col, alpha=0.12, lw=0, depthshade=False)
        ax.scatter(pop["x"][lit], pop["y"][lit], -pop["z"][lit], s=12, c="#ffffff", alpha=0.95, lw=0, depthshade=False)
        ax.plot_surface(0.1 * np.cos(tt), 0.1 * np.sin(tt), -zz, color="#c9d1d9", alpha=0.9, lw=0, shade=True)
        ax.plot([-R_SHOW, -R_SHOW + 1.0], [R_SHOW, R_SHOW], [-Z_BOTTOM] * 2, color=t["muted"], lw=2)
        ax.text(-R_SHOW + 0.5, R_SHOW, -Z_BOTTOM - 0.12, "1 mm", color=t["muted"], fontsize=13, ha="center")
        ax.set_xlim(-R_SHOW, R_SHOW)
        ax.set_ylim(-R_SHOW, R_SHOW)
        ax.set_zlim(-Z_BOTTOM, -Z_TOP)
        ax.set_box_aspect((2 * R_SHOW, 2 * R_SHOW, Z_BOTTOM - Z_TOP), zoom=1.25 if vertical else 1.0)
        ax.view_init(elev=14, azim=-60 + 40 * i / max(1, n_frames - 1))
        x0, ytop = (0.06, 0.955) if vertical else (0.04, 0.92)
        fig.text(x0, ytop, "How many neurons can\none degree buy?" if vertical else "How many neurons can one degree buy?",
                 color=t["fg"], fontsize=40 if vertical else 36, fontweight="bold", va="top")
        fig.text(x0, ytop - (0.062 if vertical else 0.075), f"{wl} nm light from a 200 µm fibre · heat limit {limit:g} °C"
                 + (" · toy upper bound only" if wl not in recruit.HEADLINE_COLOURS else ""),
                 color=t["muted"], fontsize=20, va="top")
        stats = [("fibre power", f"{p:.2f} mW"), ("warming at the hottest point", f"+{p * k:.2f} °C"),
                 ("neurons recruited", f"{n_full[i]:,}")]
        for j, (lab, val) in enumerate(stats):
            yy = (0.17 - 0.05 * j) if vertical else (0.62 - 0.14 * j)
            fig.text(x0, yy, val, color=col if j == 2 else t["fg"], fontsize=40 if vertical else 44, fontweight="bold")
            fig.text(x0, yy - (0.016 if vertical else 0.035), lab, color=t["muted"], fontsize=17)
        sep = "\n" if vertical else "; "
        fig.text(x0, 0.015 if vertical else 0.04, f"Educational demo, toy model. Not research. 1 in {THIN} neurons shown{sep}"
                 f"one threshold ({THRESHOLD:g} mW/mm²), lognormal expression (spread {sigma:g})",
                 color=t["muted"], fontsize=12.5 if vertical else 14)
        path = out / f"frame_{i:04d}.png"
        fig.savefig(path, dpi=100, facecolor=t["bg"])
        plt.close(fig)
        paths.append(path)
    return paths


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--vertical", action="store_true", help="1080x1920 instead of 1920x1080")
    ap.add_argument("--colour", type=int, default=470, choices=(470, 590, 635))
    ap.add_argument("--limit", type=float, default=DEFAULT_LIMIT_C)
    ap.add_argument("--frames", type=int, default=60)
    a = ap.parse_args()
    print(len(render(a.colour, a.limit, a.frames, a.vertical)), "frames written")
