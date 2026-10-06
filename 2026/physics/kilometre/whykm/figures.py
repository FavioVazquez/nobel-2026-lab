"""Figures, each in a light and a dark version. Educational demo made to show an open-source tool."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402

from . import constants as C  # noqa: E402
from . import physics as P  # noqa: E402

RESULTS = Path(__file__).resolve().parent.parent / "results"
LABEL = "Educational demo made to show an open-source tool. Toy model, not research."
SUBTITLE = "our toy model: simplified, trend only"
THEMES = {
    "light": {"bg": "#ffffff", "fg": "#1b1f24", "grid": "#d0d7de", "muted": "#57606a", "a": "#2f6fdf", "b": "#e5484d",
              "c": "#14a37f", "d": "#8e6cff", "cmap": "viridis"},
    "dark": {"bg": "#0d1117", "fg": "#e6edf3", "grid": "#30363d", "muted": "#8b949e", "a": "#58a6ff", "b": "#ff7b72",
             "c": "#3fd3a8", "d": "#b69cff", "cmap": "viridis"},
}
TEV = 1e3


def _theme(fig, axes, t):
    fig.patch.set_facecolor(t["bg"])
    for ax in axes:
        ax.set_facecolor(t["bg"])
        for s in ax.spines.values():
            s.set_color(t["muted"])
        ax.tick_params(colors=t["fg"], labelsize=12, which="both")
        ax.xaxis.label.set_color(t["fg"])
        ax.yaxis.label.set_color(t["fg"])
        ax.grid(True, color=t["grid"], lw=0.7, alpha=0.8, which="major")


def _titles(fig, t, title, extra=""):
    fig.suptitle(title, fontsize=17, fontweight="bold", color=t["fg"], x=0.02, y=0.985, ha="left")
    fig.text(0.02, 0.925, SUBTITLE + (f" · {extra}" if extra else ""), color=t["muted"], fontsize=11.5, ha="left")
    fig.text(0.02, 0.012, LABEL, color=t["muted"], fontsize=9.5, ha="left")


def _save(make, stem):
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = []
    for theme in ("light", "dark"):
        fig = make(THEMES[theme])
        p = RESULTS / f"{stem}_{theme}.png"
        fig.savefig(p, dpi=200, facecolor=fig.get_facecolor())
        plt.close(fig)
        out.append(p)
    return out


def _energy_axis(ax):
    ax.set_xscale("log")
    ax.set_xlim(C.E_MIN_PLOT_GEV, C.E_MAX_PLOT_GEV)
    ticks = [1e3, 1e4, 1e5, 1e6, 1e7]
    ax.set_xticks(ticks, ["1 TeV", "10 TeV", "100 TeV", "1 PeV", "10 PeV"])
    ax.set_xlabel("neutrino energy")


def _one_in(p):
    n = float(f"{1 / p:.2g}")
    return f"about 1 in {n:,.0f}"


def fig_interaction_chance(summary):
    E = np.logspace(3, 7, 300)
    p_nu, p_nub = P.p_interact(E, 1000, "numu"), P.p_interact(E, 1000, "numubar")
    p_avg = 0.5 * (p_nu + p_nub)

    def make(t):
        fig, ax = plt.subplots(figsize=(8, 5.4))
        fig.subplots_adjust(left=0.13, right=0.97, top=0.83, bottom=0.17)
        _theme(fig, [ax], t)
        ax.plot(E, p_nu, color=t["a"], lw=1.4, ls="--", label="muon neutrino")
        ax.plot(E, p_nub, color=t["b"], lw=1.4, ls="--", label="muon antineutrino")
        ax.plot(E, p_avg, color=t["fg"], lw=2.6, label="average of the two")
        for key, e in (("100TeV", 1e5), ("1PeV", 1e6)):
            v = summary["p_interact_1km"][key]
            ax.plot([e], [v], "o", ms=9, color=t["c"], zorder=5)
            ax.annotate(f"{_one_in(v)}\n({v:.1e})", (e, v), xytext=(-12, 22), textcoords="offset points",
                        color=t["fg"], fontsize=12, ha="right")
        _energy_axis(ax)
        ax.set_yscale("log")
        ax.set_ylabel("chance to interact in 1 km of ice")
        leg = ax.legend(loc="lower right", fontsize=11, frameon=False)
        [x.set_color(t["fg"]) for x in leg.get_texts()]
        _titles(fig, t, "1 km of ice stops almost no neutrinos",
                "nuFATE cross sections (CC + NC), ice 0.917 g/cm³")
        return fig

    return _save(make, "interaction_chance")


def fig_earth_transmission(summary):
    E = np.logspace(3, 7, 161)
    zen = np.linspace(90.0, 180.0, 181)
    X = P.column_depth(np.cos(np.radians(zen)))
    T = P.transmission_flavour(E, None, "mu", X=X)  # (E, zenith)

    def make(t):
        fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 5.4), gridspec_kw={"width_ratios": [1.25, 1]})
        fig.subplots_adjust(left=0.13, right=0.98, top=0.83, bottom=0.17, wspace=0.32)
        _theme(fig, [ax, ax2], t)
        im = ax.pcolormesh(E, zen, np.clip(T.T, 1e-4, 1), norm=LogNorm(1e-4, 1), cmap=t["cmap"], shading="auto")
        cs = ax.contour(E, zen, T.T, levels=[0.01, 0.1, 0.5, 0.9], colors=[t["bg"]], linewidths=1.0)
        ax.clabel(cs, fmt={0.01: "1%", 0.1: "10%", 0.5: "50%", 0.9: "90%"}, fontsize=10)
        cb = fig.colorbar(im, ax=ax, pad=0.02)
        cb.set_label("fraction that gets through", color=t["fg"])
        cb.ax.tick_params(colors=t["fg"])
        _energy_axis(ax)
        ax.set_ylabel("degrees from overhead\n(90 = horizon, 180 = straight up)")
        ax.set_yticks([90, 120, 150, 180])
        for z, col in ((180, t["fg"]), (150, t["a"]), (120, t["c"]), (100, t["d"])):
            Tz = P.transmission_flavour(E, np.cos(np.radians(z)), "mu")
            ax2.plot(E, Tz, color=col, lw=2.2, label=f"{z} deg" + (" (through the core)" if z == 180 else ""))
        v = summary["earth_survival_vertical"]["1PeV"]
        ax2.plot([1e6], [v], "o", ms=8, color=t["b"], zorder=5)
        ax2.annotate(f"straight up at 1 PeV:\n{v:.2g} survive", (1e6, v), xytext=(-150, -6), textcoords="offset points",
                     color=t["fg"], fontsize=11)
        _energy_axis(ax2)
        ax2.set_yscale("log")
        ax2.set_ylim(1e-5, 1.5)
        ax2.set_ylabel("fraction that gets through")
        leg = ax2.legend(loc="lower left", fontsize=10.5, frameon=False)
        [x.set_color(t["fg"]) for x in leg.get_texts()]
        _titles(fig, t, "Through the Earth: above ~100 TeV the planet gets in the way",
                "muon neutrinos, mean of nu and anti-nu; no regeneration, NC = loss")
        return fig

    return _save(make, "earth_transmission")


def fig_events_vs_size(summary):
    L = np.logspace(1, np.log10(2000), 200)
    per_nucleon = summary["details"]["events_per_year_per_nucleon"]
    N = P.nucleons_in_cube(L) * per_nucleon

    def make(t):
        fig, ax = plt.subplots(figsize=(8, 5.6))
        fig.subplots_adjust(left=0.13, right=0.97, top=0.83, bottom=0.17)
        _theme(fig, [ax], t)
        ax.plot(L, N, color=t["a"], lw=2.8)
        ax.axhline(1, color=t["muted"], lw=1, ls=":")
        ax.text(12, 1.25, "one event per year", color=t["muted"], fontsize=10.5)
        names = {"10m": (10, "10 m cube"), "100m": (100, "100 m cube"), "1km": (1000, "1 km cube (IceCube's scale)")}
        for key, (side, txt) in names.items():
            n = summary["events_per_year"][key]
            every = (f"about {n:.2g} interactions per year\n(before any detector cuts)" if n >= 1
                     else f"about one every {float(f'{1 / n:.2g}'):,.0f} years")
            ax.plot([side], [n], "o", ms=10, color=t["b"], zorder=5)
            off = {"10m": (14, -14), "100m": (14, -30), "1km": (-14, 18)}[key]
            ax.annotate(f"{txt}\n{every}", (side, n), xytext=off, textcoords="offset points", color=t["fg"],
                        fontsize=11, ha="right" if key == "1km" else "left", va="bottom" if key == "1km" else "top")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(8, 2500)
        ax.set_ylim(1e-6, 3e3)
        ax.set_xticks([10, 100, 1000, 2000], ["10 m", "100 m", "1 km", "2 km"])
        ax.set_xlabel("side of a cube of ice")
        ax.set_ylabel("neutrino interactions per year (above 60 TeV)")
        _titles(fig, t, "Why a cubic kilometre: 10x wider, 1,000x more events",
                "HESE 7.5-yr flux, all flavours, Earth included")
        return fig

    return _save(make, "events_vs_size")


def fig_hese_check(summary, hese):
    if hese is None:
        return []
    edges = np.array(hese["bins_GeV"])
    toy = np.array(hese["toy_1km3_per_bin"])
    sel = np.array(hese["hese_mc_selected_per_bin"])
    gr = np.array(hese["hese_mc_selected_glashow_per_bin"])
    ctr = np.sqrt(edges[:-1] * edges[1:])
    obs = summary["hese_check"]["observed_per_year_above_60TeV"]

    def make(t):
        fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 5.4), gridspec_kw={"width_ratios": [1.3, 1]})
        fig.subplots_adjust(left=0.08, right=0.98, top=0.83, bottom=0.17, wspace=0.3)
        _theme(fig, [ax, ax2], t)
        ax.stairs(toy, edges, color=t["a"], lw=2.4, label=f"our toy, every interaction in 1 km³ ({toy.sum():.0f}/yr)")
        ax.stairs(sel, edges, color=t["b"], lw=2.4,
                  label=f"IceCube's public HESE simulation, same flux ({sel.sum():.1f}/yr here)")
        ax.stairs(gr, edges, color=t["d"], lw=1.6, ls="--", label="of which Glashow resonance (not in our toy)")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(6e4, 1e7)
        ax.set_ylim(1e-3, 1e3)
        ax.set_xticks([1e5, 1e6, 1e7], ["100 TeV", "1 PeV", "10 PeV"])
        ax.set_xlabel("neutrino energy (true)")
        ax.set_ylabel("events per year in each bin")
        leg = ax.legend(loc="upper right", fontsize=9.5, frameon=False)
        [x.set_color(t["fg"]) for x in leg.get_texts()]
        ratio = (sel - gr) / toy
        ax2.plot(ctr, ratio, "o-", color=t["c"], lw=2)
        ax2.set_xscale("log")
        ax2.set_xlim(6e4, 1e7)
        ax2.set_ylim(0, 0.6)
        ax2.set_xticks([1e5, 1e6, 1e7], ["100 TeV", "1 PeV", "10 PeV"])
        ax2.set_xlabel("neutrino energy (true)")
        ax2.set_ylabel("kept by HESE (no Glashow)\n÷ all interactions in 1 km³")
        ax2.text(7e4, 0.53, "low end: part of the energy leaves\n(muons, neutral currents), so it\nfalls under 60 TeV deposited",
                 color=t["fg"], fontsize=9.5, va="top")
        ax2.text(3e5, 0.12, "plateau below 1: the outer\nlayers are the veto, not the\ncounting volume", color=t["fg"],
                 fontsize=9.5)
        _titles(fig, t, f"Cross-check: toy {toy.sum():.0f}/yr in 1 km³, IceCube HESE observed {obs:.1f}/yr",
                "the gap: veto layer + deposited-energy cut; the observed count also has backgrounds")
        return fig

    return _save(make, "hese_check")


def fig_earth_shadow(shape):
    if not shape:
        return []

    def make(t):
        fig, ax = plt.subplots(figsize=(8, 5.4))
        fig.subplots_adjust(left=0.13, right=0.97, top=0.83, bottom=0.17)
        _theme(fig, [ax], t)
        first = next(iter(shape.values()))
        E = np.array(first["E_GeV"])
        ax.plot(E, first["toy_ratio"], color=t["a"], lw=2.8, label="our toy (Earth transmission only)")
        styles = {"dr1_IC86_II_effectiveArea.csv": ("s", t["b"], "IceCube tracks DR1 (IC86-II), public table"),
                  "dr2_IC86_effectiveArea.csv": ("o", t["c"], "IceCube tracks DR2 (IC86), public table")}
        for name, v in shape.items():
            m, col, lab = styles[name]
            ax.plot(v["E_GeV"], v["public_ratio"], m, color=col, ms=6, label=lab)
        _energy_axis(ax)
        ax.set_yscale("log")
        ax.set_ylim(1e-3, 2)
        b_up, b_ref = first["dec_band_up"], first["dec_band_ref"]
        ax.set_ylabel("effective area ~60 deg below the horizon\n÷ effective area at the horizon")
        leg = ax.legend(loc="lower left", fontsize=10, frameon=False)
        [x.set_color(t["fg"]) for x in leg.get_texts()]
        _titles(fig, t, "Shape check: the Earth's shadow in public effective areas",
                f"declination {b_up[0]:.0f}-{b_up[1]:.0f} deg vs {b_ref[0]:.0f}-{b_ref[1]:.0f} deg; shape only")
        return fig

    return _save(make, "earth_shadow_check")
