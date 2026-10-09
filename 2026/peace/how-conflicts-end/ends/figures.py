"""Figures, each in a light and a dark version. Educational demo made to show an open-source tool."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from . import constants as C  # noqa: E402

RESULTS = Path(__file__).resolve().parent.parent / "results"
SUBTITLE = "UCDP Conflict Termination Dataset v.4 2024, all conflicts worldwide, by the year the episode ended"
THEMES = {
    "light": {"bg": "#ffffff", "fg": "#1b1f24", "grid": "#d0d7de", "muted": "#57606a"},
    "dark": {"bg": "#0d1117", "fg": "#e6edf3", "grid": "#30363d", "muted": "#8b949e"},
}
# Okabe-Ito colours, one per codebook outcome, in codebook order.
COLOURS = ["#0072b2", "#56b4e9", "#d55e00", "#e69f00", "#999999", "#cc79a7"]


def _theme(fig, ax, t):
    fig.patch.set_facecolor(t["bg"])
    ax.set_facecolor(t["bg"])
    for s in ax.spines.values():
        s.set_color(t["muted"])
    ax.tick_params(colors=t["fg"], labelsize=12)
    ax.xaxis.label.set_color(t["fg"])
    ax.yaxis.label.set_color(t["fg"])
    ax.grid(True, axis="y", color=t["grid"], lw=0.7, alpha=0.8)


def _titles(fig, t, title):
    h = fig.get_figheight()
    fig.suptitle(title, fontsize=17, fontweight="bold", color=t["fg"], x=0.02, y=1 - 0.12 / h, ha="left", va="top")
    fig.text(0.02, 1 - 0.5 / h, SUBTITLE, color=t["muted"], fontsize=11, ha="left", va="top")
    fig.text(0.02, 0.012, C.LABEL + "  Data: UCDP, CC BY 4.0 (Kreutz 2010).", color=t["muted"], fontsize=9.5,
             ha="left")


def _save(make, stem):
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = []
    for name, t in THEMES.items():
        fig = make(t)
        p = RESULTS / f"{stem}_{name}.png"
        fig.savefig(p, dpi=150, facecolor=fig.get_facecolor())
        plt.close(fig)
        out.append(p)
    return out


def fig_shares(s):
    per = s["by_decade"]
    names = list(C.OUTCOMES.values())
    x = np.arange(len(per))

    def make(t):
        fig, ax = plt.subplots(figsize=(12.5, 7))
        fig.subplots_adjust(left=0.07, right=0.64, top=0.84, bottom=0.14)
        _theme(fig, ax, t)
        bottom = np.zeros(len(per))
        for name, col in zip(names, COLOURS):
            v = np.array([p["shares_pct"][name] for p in per])
            ax.bar(x, v, bottom=bottom, color=col, width=0.75, label=name, edgecolor=t["bg"], lw=0.6)
            bottom += v
        for i, p in enumerate(per):
            ax.text(i, 101.5, "n = %d" % p["episodes_ended"], ha="center", color=t["fg"], fontsize=10.5)
        ax.set_xticks(x, [p["decade"] + ("*" if p["n_years"] < 10 else "") for p in per])
        ax.set_ylim(0, 106)
        ax.set_ylabel("share of episodes that ended (%)", fontsize=13)
        ax.set_xlabel("* 1940s = 1946-1949; 2020s = 2020-2023 only", fontsize=11)
        leg = ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=11, frameon=False,
                        title="how the episode ended (codebook)", title_fontsize=11)
        for tx in leg.get_texts() + [leg.get_title()]:
            tx.set_color(t["fg"])
        _titles(fig, t, "How conflict episodes ended, by decade")
        return fig

    return _save(make, "ends_by_decade")


def fig_agreement(s):
    """Two views: (A) shares of all endings, agreement-or-ceasefire and low activity; (B) the agreement-or-ceasefire
    share among endings with a clear outcome (agreement, ceasefire or victory)."""
    per = s["by_decade"]
    x = np.arange(len(per))
    labels = [p["decade"] + ("*" if p["n_years"] < 10 else "") for p in per]

    def col(key, i=None):
        return np.array([p[key] if i is None else p[key][i] for p in per])

    def slope_text(tr):
        p = "p < %g" % s["trends"]["p_floor"] if tr["p"] < s["trends"]["p_floor"] else "p = %.2f" % tr["p"]
        return "trend: %+.3f log-odds per decade (95 %%: %.3f to %.3f), %s" % (
            tr["slope_log_odds_per_decade"], tr["slope_ci95"][0], tr["slope_ci95"][1], p)

    def make(t):
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 7), sharey=True)
        fig.subplots_adjust(left=0.06, right=0.98, top=0.80, bottom=0.15, wspace=0.06)
        line = COLOURS[0] if t["bg"] == "#ffffff" else COLOURS[1]
        for ax in (a1, a2):
            _theme(fig, ax, t)
            ax.set_xticks(x, labels)
            ax.tick_params(axis="x", labelsize=10.5)
            ax.set_ylim(0, 100)
        a1.fill_between(x, col("agreement_or_ceasefire_ci95_pct", 0), col("agreement_or_ceasefire_ci95_pct", 1),
                        color=COLOURS[0], alpha=0.25, lw=0)
        a1.plot(x, col("agreement_or_ceasefire_pct"), "o-", color=line, lw=2.5, ms=7,
                label="peace agreement or ceasefire (95 % Wilson band)")
        a1.plot(x, col("low_activity_pct"), "s--", color=COLOURS[4], lw=2, ms=6, label="low activity (faded out)")
        a1.set_ylabel("share of episodes that ended (%)", fontsize=13)
        a1.set_title("A. Share of all endings", color=t["fg"], fontsize=13, loc="left")
        a1.text(0.02, 0.97, slope_text(s["trends"]["agreement_or_ceasefire_all_endings"]), transform=a1.transAxes,
                color=t["muted"], fontsize=9.5, va="top")
        a2.fill_between(x, col("agreement_or_ceasefire_among_clear_ci95_pct", 0),
                        col("agreement_or_ceasefire_among_clear_ci95_pct", 1), color=COLOURS[0], alpha=0.25, lw=0)
        a2.plot(x, col("agreement_or_ceasefire_among_clear_pct"), "o-", color=line, lw=2.5, ms=7,
                label="peace agreement or ceasefire (95 % Wilson band)")
        for i, p in enumerate(per):
            a2.text(i, 3, "%d of %d" % (p["agreement_or_ceasefire"], p["clear_outcome_endings"]), ha="center",
                    color=t["muted"], fontsize=9)
        a2.set_title("B. Share of endings with a clear outcome (agreement, ceasefire or victory)", color=t["fg"],
                     fontsize=13, loc="left")
        a2.text(0.02, 0.97, slope_text(s["trends"]["agreement_or_ceasefire_among_clear_outcomes"]),
                transform=a2.transAxes, color=t["muted"], fontsize=9.5, va="top")
        for ax in (a1, a2):
            leg = ax.legend(loc="upper left", bbox_to_anchor=(0, 0.92), fontsize=10.5, frameon=False)
            for tx in leg.get_texts():
                tx.set_color(t["fg"])
        fig.text(0.06, 0.055, "* 1940s = 1946-1949; 2020s = 2020-2023 only (conflicts still active in 2024 not "
                 "counted)", color=t["fg"], fontsize=10.5)
        _titles(fig, t, "Two views of how conflict episodes ended")
        return fig

    return _save(make, "agreement_share")
