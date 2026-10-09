"""Kaplan-Meier figure in a light and a dark version. Educational demo made to show an open-source tool."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from . import constants as C  # noqa: E402

RESULTS = Path(__file__).resolve().parent.parent / "results"
SUBTITLE = "UCDP Peace Agreement Dataset 22.2 and UCDP conflict-years to 2024, all agreements worldwide"
THEMES = {
    "light": {"bg": "#ffffff", "fg": "#1b1f24", "grid": "#d0d7de", "muted": "#57606a"},
    "dark": {"bg": "#0d1117", "fg": "#e6edf3", "grid": "#30363d", "muted": "#8b949e"},
}
COLOURS = {"Full": "#0072b2", "Partial": "#e69f00", "Peace process": "#cc79a7"}
COLOURS_DARK = {"Full": "#56b4e9", "Partial": "#e69f00", "Peace process": "#e48cc2"}


def _save(make, stem):
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = []
    for name, t in THEMES.items():
        fig = make(t, COLOURS if name == "light" else COLOURS_DARK)
        p = RESULTS / f"{stem}_{name}.png"
        fig.savefig(p, dpi=150, facecolor=fig.get_facecolor())
        plt.close(fig)
        out.append(p)
    return out


def _step(curve, xmax):
    xs, ys, lo, hi = [], [], [], []
    for i, c in enumerate(curve):
        end = curve[i + 1]["t"] if i + 1 < len(curve) else xmax
        xs += [c["t"], end]
        ys += [c["S"] * 100] * 2
        lo += [c["lo"] * 100] * 2
        hi += [c["hi"] * 100] * 2
    return xs, ys, lo, hi


def fig_km(s, xmax=C.FIGURE_YEARS):
    def make(t, cols):
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 7), sharey=True)
        fig.subplots_adjust(left=0.07, right=0.98, top=0.78, bottom=0.16, wspace=0.06)
        fig.patch.set_facecolor(t["bg"])
        for ax in (a1, a2):
            ax.set_facecolor(t["bg"])
            for sp in ax.spines.values():
                sp.set_color(t["muted"])
            ax.tick_params(colors=t["fg"], labelsize=12)
            ax.grid(True, color=t["grid"], lw=0.7, alpha=0.8)
            for h in C.HORIZONS:
                ax.axvline(h, color=t["muted"], lw=0.9, ls=":")
            ax.set_xlim(0, xmax)
            ax.set_xticks(range(0, xmax + 1, 5))
            ax.set_ylim(0, 100)
        main = s["main"]["groups"]
        for name, col in cols.items():
            xs, ys, lo, hi = _step(main[name]["curve"], xmax)
            a1.fill_between(xs, lo, hi, color=col, alpha=0.12, lw=0)
            a1.plot(xs, ys, color=col, lw=2.6, label="%s (n = %d)" % (name, main[name]["agreements"]))
        xs, ys, _, _ = _step(main["All"]["curve"], xmax)
        a1.plot(xs, ys, color=t["fg"], lw=1.4, ls="--", label="all (n = %d)" % main["All"]["agreements"])
        a1.set_title("A. Main clock, by agreement type", color=t["fg"], fontsize=13, loc="left")
        a1.set_xlabel("years from the year before the first quiet year", fontsize=12, color=t["fg"])
        a1.set_ylabel("agreements with no fighting yet in the same conflict (%)", fontsize=12, color=t["fg"])
        views = [("main clock (n = %d)", main["All"], "-", 2.6),
                 ("main clock, without settled late (n = %d)", s["main"]["without_settled_late"]["All"], "-.", 2.0),
                 ("strict clock, from the signing year (n = %d)", s["strict"]["groups"]["All"], ":", 2.4)]
        for label, g, ls, lw in views:
            xs, ys, _, _ = _step(g["curve"], xmax)
            a2.plot(xs, ys, color=t["fg"] if ls == "-" else t["muted"], lw=lw, ls=ls, label=label % g["agreements"])
        a2.set_title("B. All agreements, three ways of counting", color=t["fg"], fontsize=13, loc="left")
        a2.set_xlabel("years on that clock", fontsize=12, color=t["fg"])
        for ax, title in ((a1, "UCDP agreement type (shaded: Greenwood 95 %)"), (a2, None)):
            leg = ax.legend(loc="upper right", fontsize=10.5, frameon=False, title=title, title_fontsize=10.5)
            for tx in leg.get_texts() + ([leg.get_title()] if title else []):
                tx.set_color(t["fg"])
        h = fig.get_figheight()
        fig.suptitle("How long the quiet lasted after a peace agreement", fontsize=17, fontweight="bold",
                     color=t["fg"], x=0.02, y=1 - 0.12 / h, ha="left", va="top")
        fig.text(0.02, 1 - 0.5 / h, SUBTITLE, color=t["muted"], fontsize=11, ha="left", va="top")
        fig.text(0.02, 1 - 0.78 / h, "Kaplan-Meier; quiet = fewer than 25 battle-related deaths in a calendar year; "
                 "agreements in linked conflicts are not independent; correlation, not cause", color=t["muted"],
                 fontsize=11, ha="left", va="top")
        fig.text(0.02, 0.012, C.LABEL + "  Data: UCDP, CC BY 4.0 (Pettersson et al. 2019; Kreutz 2010).",
                 color=t["muted"], fontsize=9.5, ha="left")
        return fig

    return _save(make, "km_by_type")
