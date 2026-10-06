"""Figures (light and dark themes, 1600 px wide) from results/*.json. Toy model, not research."""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .geometry import icecube  # noqa: E402

SUBTITLE = "our toy model: tuned constants, trend only, not IceCube's performance"
FOOTER = "Educational demo made to show an open-source tool. Toy model, not research."
THEMES = {
    "light": dict(bg="white", fg="#1f2328", grid="#d0d7de", dim="#8c959f", line="#d1495b", pandel="#2e86de",
                  real="#1b998b", track="#1f2328", sensors="#c9d1d9", cmap="viridis"),
    "dark": dict(bg="#0d1117", fg="#e6edf3", grid="#30363d", dim="#8b949e", line="#ff7b72", pandel="#58a6ff",
                 real="#3fb950", track="#f0f6fc", sensors="#484f58", cmap="plasma"),
}


def _style(fig, axes, th):
    fig.patch.set_facecolor(th["bg"])
    for ax in axes:
        ax.set_facecolor(th["bg"])
        ax.tick_params(colors=th["fg"])
        for s in ax.spines.values():
            s.set_color(th["dim"])
        ax.xaxis.label.set_color(th["fg"])
        ax.yaxis.label.set_color(th["fg"])
        ax.title.set_color(th["fg"])


def _titles(fig, title, th, size=15):
    fig.text(0.01, 0.975, title, fontsize=size, weight="bold", color=th["fg"], va="top")
    fig.text(0.01, 0.925, SUBTITLE, fontsize=10.5, color=th["dim"], va="top", style="italic")
    fig.text(0.01, 0.012, FOOTER, fontsize=8.5, color=th["dim"], va="bottom")


def error_vs_spacing(S, theme):
    th = THEMES[theme]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(8, 4.5), dpi=200, gridspec_kw=dict(width_ratios=[1.6, 1]))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.82, bottom=0.23, wspace=0.28)
    _style(fig, (ax, bx), th)
    x = np.array(S["spacings_m"])
    ic = S["icecube_real"]
    for fit, name, col, dx in (("line", "line fit", th["line"], -3), ("pandel", "Pandel likelihood fit", th["pandel"], 3)):
        med = np.array(S["median_error_deg"][fit])
        ax.fill_between(x, S["p16_error_deg"][fit], S["p84_error_deg"][fit], color=col, alpha=0.15, lw=0)
        ax.plot(x, med, "-o", color=col, ms=4, lw=1.8, label=f"{name}: median, middle 68% shaded")
        ax.errorbar([125 + dx], [ic["median_error_deg"][fit]],
                    yerr=[[ic["median_error_deg"][fit] - ic["p16_error_deg"][fit]],
                          [ic["p84_error_deg"][fit] - ic["median_error_deg"][fit]]],
                    fmt="D", color=th["real"], mec=col, mew=1.5, ms=6, capsize=2, lw=1, zorder=5)
    ax.plot([], [], "D", color=th["real"], ms=6,
            label="real IceCube layout, same toy\n(IceCube's real aim: about 0.3° at 100 TeV)")
    ax.axvline(125, color=th["dim"], ls=":", lw=1)
    ax.text(128, 0.03, "IceCube's 125 m", transform=ax.get_xaxis_transform(), color=th["dim"], fontsize=8, va="bottom")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{s}\n{n} str." + (f"\n{f:.0%} fitted" if f < 0.99 else "")
                        for s, n, f in zip(x, S["n_strings"], S["trigger_fraction"])], fontsize=7, va="top")
    ax.set_xlabel("distance between strings (m), same 1 km² patch: wider = fewer strings\n"
                  "\"fitted\" = share of muons with 8+ hits", fontsize=8)
    ax.set_ylabel("angular error (degrees, log scale)")
    ax.grid(True, which="both", color=th["grid"], lw=0.5)
    leg = ax.legend(fontsize=7.5, loc="upper left", frameon=False, borderaxespad=0.2)
    for t in leg.get_texts():
        t.set_color(th["fg"])
    bx.plot(x, S["median_hits"], "-o", color=th["fg"], ms=4, lw=1.5)
    bx.plot([125], [ic["median_hits"]], "D", color=th["real"], ms=6)
    bx.axvline(125, color=th["dim"], ls=":", lw=1)
    bx.set_yscale("log")
    bx.set_yticks([10, 20, 50, 100, 200, 500])
    bx.set_yticklabels(["10", "20", "50", "100", "200", "500"])
    bx.set_xlabel("distance between strings (m)")
    bx.set_ylabel("median number of sensors hit")
    bx.grid(True, which="both", color=th["grid"], lw=0.5)
    _titles(fig, "Closer strings, sharper aim: 1 TeV muons in a toy ice telescope", th)
    return fig


def _clip_line(p, u, lo, hi):
    """Segment of the line p + s u inside the box [lo, hi]^3."""
    s0, s1 = -1e9, 1e9
    for k in range(3):
        if abs(u[k]) > 1e-9:
            a, b = sorted(((lo[k] - p[k]) / u[k], (hi[k] - p[k]) / u[k]))
            s0, s1 = max(s0, a), min(s1, b)
    return np.array([p + s0 * u, p + s1 * u])


def example_event(E, theme):
    th = THEMES[theme]
    det = icecube()
    xyz = det.xyz
    idx = np.array([h[0] for h in E["hits"]])
    t = np.array([h[1] for h in E["hits"]])
    t = t - t.min()
    q = np.array([h[2] for h in E["hits"]])
    fig, axes = plt.subplots(1, 2, figsize=(8, 4.6), dpi=200)
    fig.subplots_adjust(left=0.09, right=0.86, top=0.8, bottom=0.14, wspace=0.3)
    _style(fig, axes, th)
    lo, hi = xyz.min(0) - 60, xyz.max(0) + 60
    tr = (np.array(E["track"]["point"]), np.array(E["track"]["dir"]))
    lines = [(tr, th["track"], "--", "true track"),
             ((np.array(E["line_fit_point"]), np.array(E["line_fit_dir"])), th["line"], "-",
              f"line fit ({E['error_deg']['line']:.1f} deg off)"),
             ((np.array(E["pandel_fit_point"]), np.array(E["pandel_fit_dir"])), th["pandel"], "-",
              f"Pandel fit ({E['error_deg']['pandel']:.1f} deg off)")]
    sc = None
    for ax, (i, j), name in ((axes[0], (0, 1), "top view"), (axes[1], (0, 2), "side view")):
        ax.scatter(xyz[:, i], xyz[:, j], s=0.6 if j == 2 else 2, color=th["sensors"], lw=0)
        sc = ax.scatter(xyz[idx, i], xyz[idx, j], c=t, cmap=th["cmap"], s=6 + 10 * np.log1p(q),
                        edgecolors="none", zorder=3)
        for (p, u), col, ls, lab in lines:
            seg = _clip_line(p, u, lo, hi)
            ax.plot(seg[:, i], seg[:, j], ls, color=col, lw=1.4, label=lab, zorder=4)
        a = _clip_line(*tr, lo, hi)[-1]
        ax.annotate("", xy=(a[i], a[j]), xytext=(a[i] - 60 * tr[1][i], a[j] - 60 * tr[1][j]),
                    arrowprops=dict(arrowstyle="->", color=th["track"], lw=1.2), zorder=5)
        ax.set_xlim(lo[i], hi[i])
        ax.set_ylim(lo[j], hi[j])
        ax.set_aspect("equal")
        ax.set_title(name, fontsize=10)
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)" if j == 1 else "z (m)", labelpad=1)
    leg = axes[0].legend(fontsize=7, loc="upper right", frameon=False)
    for tt in leg.get_texts():
        tt.set_color(th["fg"])
    cax = fig.add_axes([0.88, 0.18, 0.015, 0.58])
    cb = fig.colorbar(sc, cax=cax)
    cb.set_label("time after the first hit (ns)", color=th["fg"])
    cb.ax.tick_params(colors=th["fg"])
    _titles(fig, f"A typical simulated 1 TeV muon, real IceCube layout: {E['n_hits']} sensors hit", th, size=13.5)
    return fig


def photon_check_fig(args, theme):
    S, P = args
    th = THEMES[theme]
    from scipy.stats import gamma
    from .light import SIN_C
    from . import constants as K
    fig, axes = plt.subplots(1, 3, figsize=(8, 3.9), dpi=200)
    fig.subplots_adjust(left=0.095, right=0.985, top=0.76, bottom=0.17, wspace=0.4)
    _style(fig, axes, th)
    ax, bx, cx = axes
    r = np.array(P["rho_m"])
    ax.plot(r, P["fluence_walk"], "o", ms=2.5, color=th["fg"], label="photon random walk")
    ax.plot(r, P["fluence_diffusion"], "-", color=th["pandel"], lw=1.5, label="diffusion formula (used)")
    ax.set_yscale("log")
    ax.set_xlabel("distance from the muon (m)")
    ax.set_ylabel("light at that distance (1/m^2)", fontsize=8)
    ax.set_title("how much light", fontsize=9.5)
    t = np.array(P["delay_ns"])
    fp, pl = P["pandel_fitted_to_walk"], P["pandel_literature"]
    cols = [th["real"], th["pandel"], th["line"]]
    for k, col in zip(P["delay_pdf_walk"], cols):
        rc = P["summary"][k]["rho_bin_centre_m"]
        bx.plot(t, P["delay_pdf_walk"][k], "-", color=col, lw=1.4, label=f"{rc:.0f} m")
        bx.plot(t, P["delay_pdf_pandel"][k], "--", color=col, lw=1)
        rate = 1 / fp["tau_ns"] + (K.C_VAC / K.N_ICE) / fp["lambda_a_m"]
        bx.plot(t, gamma.pdf(t, rc / SIN_C / fp["lambda_m"], scale=1 / rate), ":", color=col, lw=1)
    bx.plot([], [], "-", color=th["dim"], label="walk")
    bx.plot([], [], "--", color=th["dim"], label="Pandel, AMANDA values (used)")
    bx.plot([], [], ":", color=th["dim"], label="Pandel fitted to walk")
    bx.set_yscale("log")
    bx.set_ylim(1e-6, 3e-2)
    bx.set_xlabel("delay after direct light (ns)")
    bx.set_ylabel("probability per ns", fontsize=8)
    bx.set_title("how late it arrives", fontsize=9.5)
    x = S["spacings_m"]
    cx.plot(x, S["median_error_deg"]["pandel"], "-o", ms=3, color=th["pandel"], label="AMANDA delays (main)")
    cx.plot(x, S["sensitivity_walk_delays"]["median_error_deg"]["pandel"], ":s", ms=3, color=th["pandel"],
            label="walk-fitted delays")
    cx.set_yscale("log")
    cx.set_xlabel("distance between strings (m)")
    cx.set_ylabel("Pandel fit median error (deg)", fontsize=8)
    cx.set_title("does it change the trend?", fontsize=9.5)
    for a_ in axes:
        a_.grid(True, which="major", color=th["grid"], lw=0.5)
        leg = a_.legend(fontsize=6, frameon=False, loc="best")
        for tt in leg.get_texts():
            tt.set_color(th["fg"])
    _titles(fig, "Checking our light shortcut against a photon random walk (same toy ice)", th, size=12.5)
    return fig


def make_all(results):
    results = Path(results)
    S = json.loads((results / "telescope_summary.json").read_text())
    E = json.loads((results / "example_event.json").read_text())
    jobs = [("error_vs_spacing", error_vs_spacing, S), ("example_event", example_event, E)]
    if (results / "photon_check.json").exists() and "sensitivity_walk_delays" in S:
        P = json.loads((results / "photon_check.json").read_text())
        jobs.append(("photon_check", photon_check_fig, (S, P)))
    for stem, fn, arg in jobs:
        for theme in THEMES:
            fig = fn(arg, theme)
            fig.savefig(results / f"{stem}_{theme}.png", facecolor=fig.get_facecolor())
            plt.close(fig)
