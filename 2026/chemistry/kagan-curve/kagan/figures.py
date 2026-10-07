"""Figures, each in a light and a dark version. Educational demo made to show an open-source tool."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Wedge  # noqa: E402

from . import constants as C  # noqa: E402
from . import model as M  # noqa: E402

RESULTS = Path(__file__).resolve().parent.parent / "results"
SUBTITLE = "our toy model: simplified, trend only (dimensionless units)"
ONE, MIRROR = "#c4622d", "#2b8a8f"
THEMES = {
    "light": {"bg": "#ffffff", "fg": "#1b1f24", "grid": "#d0d7de", "muted": "#57606a", "mixed": "#9aa0a6",
              "pos": "#0072b2", "neg": "#a2457f"},
    "dark": {"bg": "#0d1117", "fg": "#e6edf3", "grid": "#30363d", "muted": "#8b949e", "mixed": "#8b949e",
             "pos": "#56b4e9", "neg": "#e48cc2"},
}


def _theme(fig, axes, t, grid=True):
    fig.patch.set_facecolor(t["bg"])
    for ax in axes:
        ax.set_facecolor(t["bg"])
        for s in ax.spines.values():
            s.set_color(t["muted"])
        ax.tick_params(colors=t["fg"], labelsize=13, which="both")
        ax.xaxis.label.set_color(t["fg"])
        ax.yaxis.label.set_color(t["fg"])
        if grid:
            ax.grid(True, color=t["grid"], lw=0.7, alpha=0.8)


def _titles(fig, t, title, extra=""):
    h = fig.get_figheight()
    fig.suptitle(title, fontsize=18, fontweight="bold", color=t["fg"], x=0.02, y=1 - 0.12 / h, ha="left", va="top")
    fig.text(0.02, 1 - 0.5 / h, SUBTITLE, color=t["muted"], fontsize=12, ha="left", va="top")
    if extra:
        fig.text(0.02, 1 - 0.78 / h, extra, color=t["muted"], fontsize=12, ha="left", va="top")
    fig.text(0.02, 0.012, C.LABEL, color=t["muted"], fontsize=10, ha="left")


def _save(make, stem):
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = []
    for name, t in THEMES.items():
        fig = make(t)
        p = RESULTS / f"{stem}_{name}.png"
        fig.savefig(p, dpi=170, facecolor=fig.get_facecolor())
        plt.close(fig)
        out.append(p)
    return out


def fig_curves(K=C.K_STATISTICAL):
    e = np.linspace(0, 1, 201)
    styles = [(0.0, "pos", "-", 3.0, "g = 0: mixed pair inactive (bulge)"),
              (0.1, "pos", "-", 1.8, "g = 0.1 (bulge)"),
              (1.0, "fg", "-", 2.4, "g = 1: straight line"),
              (2.0, "neg", "--", 1.8, "g = 2 (sag)"),
              (10.0, "neg", "--", 3.0, "g = 10: mixed pair fast (sag)")]

    def make(t):
        fig, ax = plt.subplots(figsize=(8, 7))
        fig.subplots_adjust(left=0.14, right=0.97, top=0.83, bottom=0.17)
        _theme(fig, [ax], t)
        for g, col, ls, lw, lab in styles:
            ax.plot(100 * e, 100 * M.ee_prod(e, K, g), color=t[col], ls=ls, lw=lw, label=lab)
        ax.plot([50], [80], "o", ms=10, color=ONE, zorder=5)
        ax.annotate("75:25 ligand -> 80 % ee\n(the pie example)", (50, 80), (3, 88), color=t["fg"], fontsize=12,
                    arrowprops=dict(arrowstyle="->", color=t["muted"]))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_xlabel("ligand ee (%)", fontsize=14)
        ax.set_ylabel("product ee (%)", fontsize=14)
        leg = ax.legend(loc="lower right", fontsize=11.5, frameon=True, facecolor=t["bg"], edgecolor=t["grid"],
                        framealpha=0.95)
        for txt in leg.get_texts():
            txt.set_color(t["fg"])
        _titles(fig, t, "Kagan's curve: one ligand pair, three shapes",
                f"K = {K:g}, ee_max = 100 %, g = mixed / same-hand rate")
        return fig

    return _save(make, "kagan_curves")


def _pie(ax, fracs, colours, hatches, t, labels):
    start = 90.0
    for f, c, h, lab in zip(fracs, colours, hatches, labels):
        if f <= 0:
            continue
        ang = 360.0 * f
        ax.add_patch(Wedge((0, 0), 1, start - ang, start, facecolor=c, edgecolor=t["bg"], lw=2))
        if h:
            ax.add_patch(Wedge((0, 0), 1, start - ang, start, fill=False, edgecolor="white", lw=0, hatch=h))
        mid = np.deg2rad(start - ang / 2)
        r = 0.6 if f > 0.12 else 1.28
        ax.text(r * np.cos(mid), r * np.sin(mid), lab, ha="center", va="center", fontsize=14, fontweight="bold",
                color="white" if f > 0.12 else t["fg"])
        start -= ang
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")
    ax.axis("off")


def fig_pie():
    p = M.pie(C.PIE_LIGAND_ONE_HAND_PCT, C.K_STATISTICAL, 0.0)
    lig, cat, eff = p["ligand"], p["catalysts_pct"], p["effective"]

    def make(t):
        fig, axes = plt.subplots(1, 3, figsize=(12, 5.6))
        fig.subplots_adjust(left=0.02, right=0.98, top=0.74, bottom=0.2, wspace=0.25)
        _theme(fig, axes, t, grid=False)
        _pie(axes[0], [lig[0] / 100, lig[1] / 100], [ONE, MIRROR], ["", "//"], t,
             [f"{lig[0]:g} %", f"{lig[1]:g} %"])
        _pie(axes[1], [cat[0] / 100, cat[1] / 100, cat[2] / 100], [ONE, t["mixed"], MIRROR], ["", "", "//"], t,
             [f"{cat[0]:g} %", f"{cat[1]:g} %", f"{cat[2]:g} %"])
        _pie(axes[2], [eff[0] / 100, eff[1] / 100], [ONE, MIRROR], ["", "//"], t,
             [f"{eff[0]:.0f} %", f"{eff[1]:.0f} %"])
        heads = ["1. ligand: 75 : 25", "2. pairs on the metal", "3. pairs that work (g = 0)"]
        subs = ["one hand / mirror hand", "one-hand pair / mixed pair /\nmirror-hand pair", "product ee = 90 - 10 = 80 %"]
        for ax, h, s in zip(axes, heads, subs):
            ax.set_title(h, color=t["fg"], fontsize=15, fontweight="bold", pad=4)
            ax.text(0, -1.62, s, ha="center", va="top", color=t["muted"], fontsize=12)
        for x0 in (0.335, 0.665):
            fig.patches.append(FancyArrowPatch((x0 - 0.02, 0.5), (x0 + 0.02, 0.5), transform=fig.transFigure,
                                               arrowstyle="-|>", mutation_scale=22, color=t["muted"]))
        _titles(fig, t, "Kagan's pie: the mixed pairs soak up the mirror hand",
                "K = 4 (pairs form at random), mixed pair inactive, ee_max = 100 %; grey = mixed pair")
        return fig

    return _save(make, "kagan_pie")


def all_figures():
    return fig_curves() + fig_pie()
