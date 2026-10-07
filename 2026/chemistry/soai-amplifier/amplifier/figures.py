"""Figures, each in a light and a dark version. Educational demo made to show an open-source tool."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from . import constants as C  # noqa: E402
from . import model as M  # noqa: E402

RESULTS = Path(__file__).resolve().parent.parent / "results"
SUBTITLE = "our toy model: simplified, trend only (dimensionless units)"
ONE, MIRROR = "#c4622d", "#2b8a8f"
THEMES = {
    "light": {"bg": "#ffffff", "fg": "#1b1f24", "grid": "#d0d7de", "muted": "#57606a", "mixed": "#9aa0a6",
              "alt": "#0072b2", "alt2": "#a2457f"},
    "dark": {"bg": "#0d1117", "fg": "#e6edf3", "grid": "#30363d", "muted": "#8b949e", "mixed": "#8b949e",
             "alt": "#56b4e9", "alt2": "#e48cc2"},
}


def _theme(fig, axes, t):
    fig.patch.set_facecolor(t["bg"])
    for ax in axes:
        ax.set_facecolor(t["bg"])
        for s in ax.spines.values():
            s.set_color(t["muted"])
        ax.tick_params(colors=t["fg"], labelsize=13, which="both")
        ax.xaxis.label.set_color(t["fg"])
        ax.yaxis.label.set_color(t["fg"])
        ax.title.set_color(t["fg"])
        ax.grid(True, color=t["grid"], lw=0.7, alpha=0.8)


def _titles(fig, t, title, extra=""):
    h = fig.get_figheight()
    fig.suptitle(title, fontsize=18, fontweight="bold", color=t["fg"], x=0.02, y=1 - 0.12 / h, ha="left", va="top")
    fig.text(0.02, 1 - 0.5 / h, SUBTITLE, color=t["muted"], fontsize=12, ha="left", va="top")
    if extra:
        fig.text(0.02, 1 - 0.78 / h, extra, color=t["muted"], fontsize=12, ha="left", va="top")
    fig.text(0.02, 0.012, C.LABEL, color=t["muted"], fontsize=10, ha="left")


def _legend(ax, t, **kw):
    leg = ax.legend(fontsize=11.5, frameon=True, facecolor=t["bg"], edgecolor=t["grid"], framealpha=0.95, **kw)
    for txt in leg.get_texts():
        txt.set_color(t["fg"])


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


def fig_staircase(s):
    soai = np.array(C.SOAI_2003_PCT)
    tr = s["toy_rounds"]
    K, N = tr["K"], tr["turnovers_per_round"]
    toy = np.array([soai[0]] + tr["ee_pct"])
    k4 = np.array([soai[0]] + list(s["k4_fails"]["three_rounds"].values())[-1])
    x = np.arange(4)
    xs = np.append(x, 3.4)
    ext = lambda v: np.append(v, v[-1])  # noqa: E731

    def make(t):
        fig, axes = plt.subplots(1, 2, figsize=(12, 7.2))
        fig.subplots_adjust(left=0.08, right=0.98, top=0.8, bottom=0.3, wspace=0.28)
        _theme(fig, axes, t)
        ax = axes[0]
        ax.step(xs, ext(toy), where="post", color=ONE, lw=3, label=f"our toy: K = {K:.0f}, {N:.0f} turnovers/round")
        ax.step(xs, ext(k4), where="post", color=t["mixed"], lw=2.4, ls="--", label="random pairing K = 4, same turnovers")
        ax.plot(x[:3], soai[:3], "D", ms=10, color=t["fg"], label="Soai 2003 (measured; triangle = lower bound)", zorder=5)
        ax.plot(x[3], soai[3], marker="^", ms=12, color=t["fg"], zorder=5)
        ax.set_yscale("log")
        ax.set_ylim(1e-5, 300)
        ax.set_yticks([1e-4, 1e-2, 1, 100], ["0.0001 %", "0.01 %", "1 %", "100 %"])
        ax.set_ylabel("ee of the product (log scale)", fontsize=13)
        ax.set_title("ee after each round", fontsize=14, fontweight="bold")
        ax.annotate("0.00005 %:\nthe prepared\nhead start", (0, soai[0]), (0.25, 3e-4), color=t["fg"], fontsize=11,
                    arrowprops=dict(arrowstyle="->", color=t["muted"]))
        _legend(ax, t, loc="upper left", bbox_to_anchor=(0.0, -0.12))
        ax2 = axes[1]
        share = lambda e: (100 - np.asarray(e)) / 2  # noqa: E731
        ax2.step(xs, ext(share(toy)), where="post", color=MIRROR, lw=3, ls="-", label="our toy (fitted K)")
        ax2.step(xs, ext(share(k4)), where="post", color=t["mixed"], lw=2.4, ls="--", label="K = 4")
        ax2.plot(x[:3], share(soai[:3]), "D", ms=10, color=t["fg"], label="Soai 2003 (triangle = upper bound)", zorder=5)
        ax2.plot(x[3], share(soai[3]), marker="v", ms=12, color=t["fg"], zorder=5)
        ax2.annotate("< 0.25 %", (3, share(soai[3])), (2.2, 0.05), color=t["fg"], fontsize=11,
                     arrowprops=dict(arrowstyle="->", color=t["muted"]))
        ax2.set_yscale("log")
        ax2.set_ylim(0.005, 80)
        ax2.set_yticks([0.01, 0.1, 1, 10, 50], ["0.01 %", "0.1 %", "1 %", "10 %", "50 %"])
        ax2.set_ylabel("mirror-hand share of the product", fontsize=13)
        ax2.set_title("how much mirror hand is left", fontsize=14, fontweight="bold")
        _legend(ax2, t, loc="upper left", bbox_to_anchor=(0.0, -0.12))
        for a_ in axes:
            a_.set_xticks(x, ["start", "round 1", "round 2", "round 3"])
            a_.set_xlim(-0.2, 3.4)
        _titles(fig, t, "Three rounds: our toy against Soai's 2003 numbers",
                "our toy, built on one published model of several; K and turnovers are fitted toy numbers (to rounds 1 and 2)")
        return fig

    return _save(make, "rounds_staircase")


def fig_fan(s):
    l1 = s["layer1"]
    ton = np.array(l1["fan"]["turnovers"])
    K = s["toy_rounds"]["K"]
    styles = {"0.00005": ("-", 3.0), "0.01": ("-", 2.2), "0.5": ("-", 1.6), "5": ("-", 1.2)}

    def make(t):
        fig, ax = plt.subplots(figsize=(9, 7.6))
        fig.subplots_adjust(left=0.12, right=0.97, top=0.82, bottom=0.27)
        _theme(fig, [ax], t)
        for key, ys in l1["fan"]["ee_pct_by_ee0_pct"].items():
            ls, lw = styles[key]
            ax.plot(ton, ys, color=t["fg"], ls=ls, lw=lw, alpha=0.35 + 0.65 * lw / 3)
            j = np.searchsorted(np.array(ys), 50)
            if j < len(ton):
                ax.text(ton[j] * 1.15, 50, f"start {key} %", color=t["fg"], fontsize=11, rotation=72,
                        ha="left", va="center")
        fitted = 100 * M.toy_ee(C.SOAI_2003_PCT[0] / 100, 1 + ton, K)
        ax.plot(ton, fitted, color=t["alt2"], lw=3, ls="--", label=f"our fitted toy K = {K:.0f}, start 0.00005 %")
        for st, xy in zip(l1["statements"], [(3e4, 48), (1.5e5, 80)]):
            ax.plot(st["turnovers"], st["ee_pct"], "o", ms=10, color=t["alt"], zorder=5)
            ax.annotate(f"{st['ee0_pct']:g} % -> {st['ee_pct']:.1f} %", (st["turnovers"], st["ee_pct"]),
                        xy, color=t["fg"], fontsize=11,
                        arrowprops=dict(arrowstyle="->", color=t["muted"]))
        ax.plot([], [], "o", color=t["alt"], label="Blackmond's two statements (exact here)")
        ax.plot([], [], color=t["fg"], lw=2, label="random pairing K = 4 (Blackmond-Brown)")
        ax.set_xscale("log")
        ax.set_xlim(1, 1e8)
        ax.set_ylim(0, 102)
        ax.set_xlabel("turnovers (new product per seed molecule)", fontsize=13)
        ax.set_ylabel("ee of the whole product (%)", fontsize=13)
        _legend(ax, t, loc="upper left", bbox_to_anchor=(-0.02, -0.13))
        _titles(fig, t, "How many turnovers to amplify?", "mixed pairs inactive; each curve starts at a different ee")
        return fig

    return _save(make, "ee_vs_turnover_fan")


def fig_bifurcation(s):
    b = s["layer3"]["k2_bifurcation"]
    k2 = np.array(b["k2"])
    chk = s["layer3"]["fig1_check"]

    def make(t):
        fig, ax = plt.subplots(figsize=(9, 6.4))
        fig.subplots_adjust(left=0.12, right=0.97, top=0.8, bottom=0.15)
        _theme(fig, [ax], t)
        cols = [t["alt2"], t["alt"]]
        for (key, ys), c, ls in zip(b["ee_final_pct_by_ee0_pct"].items(), cols, ["-", "--"]):
            ax.plot(k2, ys, color=c, lw=3, ls=ls, marker="o", ms=5, label=f"start ee {key} %")
        ax.plot([1e5], [chk["ee_final_pct"]], "D", ms=11, color=t["fg"], zorder=5,
                label=f"Buhse Fig. 1 set: {chk['ee_final_pct']:.1f} % (published: about 85 %)")
        ax.set_xscale("log")
        ax.set_ylim(-2, 102)
        ax.set_xlabel("k2: how fast mixed pairs form (model units)", fontsize=13)
        ax.set_ylabel("final ee (%)", fontsize=13)
        _legend(ax, t, loc="upper left")
        _titles(fig, t, "A second published toy: amplification switches on",
                "Buhse-Micheau monomer-active model; one published toy model of several")
        return fig

    return _save(make, "layer3_bifurcation")


def fig_erosion(s):
    ero = np.array(s["erosion_pct"])
    amp = np.array([C.SOAI_2003_PCT[0]] + s["toy_rounds"]["ee_pct_more_rounds"])
    x = np.arange(len(ero))

    def make(t):
        fig, ax = plt.subplots(figsize=(9, 6.2))
        fig.subplots_adjust(left=0.12, right=0.97, top=0.8, bottom=0.15)
        _theme(fig, [ax], t)
        ax.step(x, ero, where="post", color=t["mixed"], lw=3, ls="--",
                label="plain copying, 90 % selective: 100 -> 90 -> 81 ...")
        ax.step(x, amp, where="post", color=ONE, lw=3, label="copying + mixed pairs inactive (our toy)")
        sel = np.array([C.SOAI_2003_PCT[0]] + s["toy_rounds"]["selectivity_check"]["ee_pct_more_rounds"])
        ax.step(x, sel, where="post", color=ONE, lw=2, ls=":",
                label="our toy with 90 % selective pairs: levels off near 90")
        for xi, v in zip(x, ero):
            ax.text(xi + 0.5, v + 2.5, f"{v:.0f}", color=t["muted"], ha="center", fontsize=11)
        for xi, txt, v in zip(x[:4], ["0.00005", f"{amp[1]:.0f}", f"{amp[2]:.0f}", f"{amp[3]:.2f}"], amp[:4]):
            ax.text(xi + 0.5, max(v, 0) - 6.5 if v > 1 else 3, txt, color=ONE, ha="center", fontsize=11)
        ax.set_xticks(x, ["start"] + [f"{k}" for k in x[1:]])
        ax.set_xlabel("round (each round's product is the next round's catalyst)", fontsize=13)
        ax.set_ylabel("ee of the product (%)", fontsize=13)
        ax.set_ylim(-3, 108)
        ax.set_xlim(0, len(x) - 0.01)
        _legend(ax, t, loc="lower right")
        _titles(fig, t, "Copying alone erodes; copying plus Kagan's effect climbs",
                "erosion: SCI p. 10 (90 % selective); climb: our fitted toy from 0.00005 % (perfectly selective pairs)")
        return fig

    return _save(make, "erosion_vs_amplification")


def fig_populations(rj):
    rows = rj["rounds"][:4]
    x = np.array([r["round"] for r in rows])
    one = np.array([r["one_hand_amount"] for r in rows])
    mir = np.array([r["mirror_hand_amount"] for r in rows])

    def make(t):
        fig, ax = plt.subplots(figsize=(9, 6.2))
        fig.subplots_adjust(left=0.12, right=0.97, top=0.8, bottom=0.15)
        _theme(fig, [ax], t)
        ax.plot(x, one, color=ONE, lw=3.2, marker="o", ms=9, label="one hand")
        ax.plot(x, mir, color=MIRROR, lw=3.2, ls="--", marker="s", ms=9, label="mirror hand")
        for xi, a, b in zip(x, one, mir):
            ax.text(xi, a * 2.2, f"{float(f'{a:.3g}'):,g}", color=ONE, ha="center", fontsize=12)
            ax.text(xi, b / 3.2, f"{float(f'{b:.3g}'):,g}", color=MIRROR, ha="center", fontsize=12)
        ax.set_yscale("log")
        ax.set_ylim(0.05, one.max() * 30)
        ax.set_xticks(x, ["start", "round 1", "round 2", "round 3"])
        ax.set_ylabel("amount (start = 1 in total, log scale)", fontsize=13)
        _legend(ax, t, loc="upper left")
        _titles(fig, t, "One hand multiplies, the mirror hand stalls",
                f"our fitted toy (K = {rj['K']:.0f}, {rj['turnovers_per_round']:.0f} turnovers/round); not Soai's amounts")
        return fig

    return _save(make, "two_populations")


def all_figures(summary, rj):
    return (fig_staircase(summary) + fig_fan(summary) + fig_bifurcation(summary) + fig_erosion(summary)
            + fig_populations(rj))
