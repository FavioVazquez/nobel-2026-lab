"""Shared helpers: paths, CSV inputs, figure themes. Educational demo, toy model."""
import csv
import io
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs"
RESULTS = HERE.parent / "results"

WAVELENGTH_COLOURS = {445: "#5b6cff", 470: "#2f8cff", 532: "#2fbf71", 590: "#f5a524", 635: "#e5484d"}
SWITCH_COLOURS = ["#2f8cff", "#8e6cff", "#14b8a6", "#f5a524", "#e5484d"]
DEMO_TAG = "Educational demo, toy model"

THEMES = {
    "light": {"bg": "#ffffff", "fg": "#1b1f24", "grid": "#d0d7de", "muted": "#57606a"},
    "dark": {"bg": "#0d1117", "fg": "#e6edf3", "grid": "#30363d", "muted": "#8b949e"},
}


def read_csv(name):
    """Read a CSV from inputs/, skipping '#' comment lines."""
    text = "".join(l for l in (INPUTS / name).read_text().splitlines(True) if not l.startswith("#"))
    return list(csv.DictReader(io.StringIO(text)))


def apply_theme(fig, axes, theme):
    t = THEMES[theme]
    fig.patch.set_facecolor(t["bg"])
    for ax in axes:
        ax.set_facecolor(t["bg"])
        for s in ax.spines.values():
            s.set_color(t["muted"])
        ax.tick_params(colors=t["fg"], labelsize=15)
        ax.xaxis.label.set_color(t["fg"])
        ax.yaxis.label.set_color(t["fg"])
        ax.title.set_color(t["fg"])
        ax.grid(True, color=t["grid"], lw=0.8, alpha=0.8)
    return t


def titles(fig, ax_top, t, title, subtitle):
    """Plain-language title on top, the demo tag and conditions in a muted line under it."""
    fig.suptitle(title, fontsize=20, fontweight="bold", color=t["fg"], x=0.02, ha="left")
    ax_top.set_title(f"{DEMO_TAG} · {subtitle}", loc="left", color=t["muted"], fontsize=12.5, pad=10)


def save_themed(make_fig, stem):
    """make_fig(theme) -> matplotlib Figure sized 8 in wide; saved at 200 dpi = 1600 px wide."""
    import matplotlib.pyplot as plt

    RESULTS.mkdir(parents=True, exist_ok=True)
    paths = []
    for theme in ("light", "dark"):
        fig = make_fig(theme)
        p = RESULTS / f"{stem}_{theme}.png"
        fig.savefig(p, dpi=200, facecolor=fig.get_facecolor())
        plt.close(fig)
        paths.append(p)
    return paths
