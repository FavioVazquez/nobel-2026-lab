"""Figures, light and dark. Colour-blind safe: one hand = burnt orange (solid), mirror hand = teal
(dashed / hatched), mixed or racemic = grey.

Educational demo made to show an open-source tool. Toy model, not research.
"""
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from . import constants as C  # noqa: E402

ONE, MIRROR, GREY = "#c4622d", "#2b8a8f", "#8c8c8c"
THEMES = {
    "light": dict(bg="white", fg="#1d1d1d", sub="#555555", grid="#dddddd", ref="#1d1d1d"),
    "dark": dict(bg="#121417", fg="#ececec", sub="#b0b0b0", grid="#33373d", ref="#ececec"),
}
N_SHADES = {"light": ("#9a9a9a", "#555555", "#111111"), "dark": ("#7a7a7a", "#b5b5b5", "#ffffff")}


def _setup(theme):
    t = THEMES[theme]
    plt.rcParams.update({"figure.facecolor": t["bg"], "axes.facecolor": t["bg"], "savefig.facecolor": t["bg"],
                         "text.color": t["fg"], "axes.labelcolor": t["fg"], "axes.edgecolor": t["sub"],
                         "xtick.color": t["fg"], "ytick.color": t["fg"], "axes.grid": True, "grid.color": t["grid"],
                         "font.size": 15, "axes.titlesize": 16, "axes.labelsize": 15, "legend.fontsize": 13,
                         "hatch.color": MIRROR, "hatch.linewidth": 1.2, "axes.spines.top": False,
                         "axes.spines.right": False, "legend.frameon": False})
    return t


def _frame(fig, t, title, top=0.86, bottom=0.11):
    fig.suptitle(title, fontsize=20, fontweight="bold", y=0.985)
    fig.text(0.5, 1 - 0.52 / fig.get_figheight(), C.SUBTITLE, ha="center", fontsize=14, color=t["sub"], style="italic")
    fig.text(0.5, 0.012, C.DISCLAIMER, ha="center", fontsize=11, color=t["sub"])
    fig.subplots_adjust(top=top, bottom=bottom)


def _save(fig, out, name, theme):
    fig.savefig(out / f"{name}_{theme}.png", dpi=110)
    plt.close(fig)


def ee_label(ee):
    """One decimal; never round a run that made some mirror hand up to "100.0%" (two decimals near the ends)."""
    s = f"{ee:+.1%}"
    return f"{ee:+.2%}" if abs(ee) < 1 and s.lstrip("+-") == "100.0%" else s


def _hist_bars(ax, edges, counts, t):
    c = 0.5 * (edges[1:] + edges[:-1])
    w = np.diff(edges)
    for x, wi, n in zip(c, w, counts):
        if abs(x) < 1e-9:
            ax.bar(x, n, wi * 0.92, color=GREY)
        elif x > 0:
            ax.bar(x, n, wi * 0.92, color=ONE)
        else:
            ax.bar(x, n, wi * 0.92, facecolor="none", edgecolor=MIRROR, hatch="///", linewidth=1.2)
    ax.set_xlim(-1.05, 1.05)
    ax.set_xticks([-1, -0.5, 0, 0.5, 1])
    ax.set_xticklabels(["all\nmirror", "", "50:50", "", "all\none"])


def race(race_data, out, theme):
    t = _setup(theme)
    used = np.asarray(race_data["molecules_used"])
    m = used > 0
    for cond, title in (("with_antagonism", "The mirror race: 8 runs, each from exactly 50:50"),
                        ("copy_only", "Copying only, no antagonism: 8 runs")):
        fig, axes = plt.subplots(2, 4, figsize=(13, 7.6), sharex=True, sharey=True)
        for ax, r in zip(axes.flat, race_data[cond]["runs"]):
            ax.plot(used[m], np.asarray(r["one"])[m], color=ONE, lw=3, label="one hand")
            ax.plot(used[m], np.asarray(r["mirror"])[m], color=MIRROR, lw=3, ls="--", label="mirror hand")
            if cond == "with_antagonism":
                ax.plot(used[m], np.asarray(r["pairs"])[m], color=GREY, lw=1.6, ls=":", label="mixed pairs (inactive)")
            ee = r["final_ee"]
            win = "one hand" if ee > 0 else "mirror hand"
            ax.set_title(f"{win}: ee {ee_label(ee)}", fontsize=13, color=ONE if ee > 0 else MIRROR)
            ax.set_xscale("log")
            ax.set_yscale("symlog", linthresh=1)
            ax.set_xticks([1, 100, 10_000])
            ax.set_xticklabels(["1", "100", "10k"])
            ax.set_yticks([0, 1, 100, 10_000])
            ax.set_yticklabels(["0", "1", "100", "10k"])
            ax.set_ylim(-0.2, race_data["N"] * 1.5)
        for ax in axes[1]:
            ax.set_xlabel("molecules of A used")
        for ax in axes[:, 0]:
            ax.set_ylabel("molecules")
        h, l = axes.flat[0].get_legend_handles_labels()
        fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.035))
        _frame(fig, t, title, top=0.83, bottom=0.2)
        fig.text(0.5, 0.875, f"N = {race_data['N']:,} molecules of A; which hand wins is chance", ha="center", fontsize=13,
                 color=t["sub"])
        _save(fig, out, f"race_{cond}", theme)


def histograms(hist, summary, out, theme):
    t = _setup(theme)
    e = np.asarray(hist["edges"])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 6.6), sharey=False)
    _hist_bars(a1, e, hist["counts"]["copy_only"], t)
    exp = np.asarray(hist["copy_only_exact_expected"])
    a1.step(np.r_[e[:-1], e[-1]], np.r_[exp, exp[-1]], where="post", color=t["ref"], lw=2, ls="-.",
            label="exact answer (Polya urn)")
    a1.set_ylim(0, max(hist["counts"]["copy_only"]) * 1.6)
    a1.legend(loc="upper center")
    co = summary["copy_only"]
    a1.set_title(f"copying only (k0 = k1): flat\n(spread {co['std_ee']:.3f}, exact {co['std_predicted']:.3f})")
    a1.set_ylabel(f"runs out of {hist['runs']:,}")
    a1.set_xlabel("final ee")
    _hist_bars(a2, e, hist["counts"]["with_antagonism"], t)
    wa = summary["with_antagonism"]
    a2.set_title(f"copying + mutual antagonism (k2 = 100 k1): two spikes\n({wa['frac_abs_ee_above_90']:.1%} of runs beyond 90% ee)")
    a2.set_xlabel("final ee")
    a2.text(0.62, max(hist["counts"]["with_antagonism"]) * 0.55, f"one hand\n{wa['one_hand_wins']:,}", color=ONE,
            ha="center", fontsize=14, fontweight="bold")
    a2.text(-0.62, max(hist["counts"]["with_antagonism"]) * 0.55, f"mirror hand\n{wa['mirror_hand_wins']:,}",
            color=MIRROR, ha="center", fontsize=14, fontweight="bold")
    _frame(fig, t, f"{hist['runs']:,} runs from exactly 50:50, N = {hist['N']:,}", top=0.8, bottom=0.17)
    _save(fig, out, "histograms", theme)


def stopped_vs_real(hist, summary, out, theme):
    t = _setup(theme)
    e = np.asarray(hist["edges"])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 7.2), gridspec_kw={"width_ratios": [1.2, 1], "wspace": 0.42})
    _hist_bars(a1, e, hist["counts"]["stopped_early"], t)
    se = summary["stopped_early"]
    a1.set_title(f"toy runs read early ({se['read_after_fraction_of_A_used']:.0%} of A used, our choice):\n"
                 f"partial ee, median |ee| {se['median_abs_ee']:.0%}")
    a1.set_xlabel("ee at that moment")
    a1.set_ylabel(f"runs out of {hist['runs']:,}")
    top = max(hist["counts"]["stopped_early"])
    for sgn in (1, -1):
        a1.axvspan(sgn * 0.15, sgn * 0.91, ymin=0.9, ymax=0.94, color=t["sub"], alpha=0.6, lw=0)
    a1.set_ylim(0, top / 0.86)
    a1.text(0, top / 0.86 * 0.955, "Soai's 37 real runs: 15-91% ee (for scale; toy not fitted)", ha="center", fontsize=11,
            color=t["sub"])
    rows = [("our toy\n(10,000 runs)", summary["with_antagonism"]["one_hand_wins"],
             summary["with_antagonism"]["mirror_hand_wins"], summary["with_antagonism"]["binomial_p"]),
            ("Soai 2003\n(37 runs)", 19, 18, summary["real"]["soai_2003"]["binomial_p"]),
            ("Singleton & Vo\n2003 (54 runs)", 27, 27, summary["real"]["singleton_vo_2003"]["binomial_p"])]
    y = np.arange(len(rows))[::-1]
    for yi, (lab, o, m, p) in zip(y, rows):
        f = o / (o + m)
        a2.barh(yi, f, color=ONE, height=0.55)
        a2.barh(yi, 1 - f, left=f, facecolor="none", edgecolor=MIRROR, hatch="///", height=0.55)
        a2.text(0.02, yi + 0.36, f"{o:,} one hand", color=ONE, fontsize=12, fontweight="bold")
        a2.text(0.98, yi + 0.36, f"{m:,} mirror hand", color=MIRROR, fontsize=12, fontweight="bold", ha="right")
        a2.text(0.5, yi - 0.48, f"coin-fairness test p = {p:.2f}", ha="center", fontsize=12, color=t["sub"])
    a2.axvline(0.5, color=t["ref"], lw=1.5, ls=":")
    a2.set_yticks(y)
    a2.set_yticklabels([r[0] for r in rows], fontsize=13)
    a2.set_xlim(0, 1)
    a2.set_ylim(-0.8, len(rows) - 0.3)
    a2.set_xticks([0, 0.5, 1])
    a2.set_xticklabels(["0%", "50%", "100%"])
    a2.grid(False)
    a2.set_title("is the coin fair? which hand won")
    _frame(fig, t, "Toy runs stopped early, and the real coin tosses", top=0.8, bottom=0.2)
    fig.text(0.5, 0.045, "Real hands: Soai 19 (S), 18 (R); Singleton & Vo 27 (R), 27 (S). p near 1 = consistent with 50:50.",
             ha="center", fontsize=11, color=t["sub"])
    _save(fig, out, "stopped_early_vs_real", theme)


def seeded(summary, out, theme):
    t = _setup(theme)
    sd = summary["seeded"]
    D = np.asarray(sd["deltas"], float)
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.6), sharey=True)
    markers = ("o", "s", "^")
    for ax, sc, xl in ((axes[0], "fixedrates", "head start (extra one-hand molecules)"),
                       (axes[1], "fixedconc", "head start / sqrt(N)")):
        for i, N in enumerate(C.N_SWEEP):
            c = sd["curves"].get(f"{sc}_N{N}")
            if c is None:
                continue
            x = D if sc == "fixedrates" else D / np.sqrt(N)
            m = D > 0
            ax.plot(x[m], np.asarray(c["p_seeded_wins"])[m], marker=markers[i], color=N_SHADES[theme][i], lw=2.2,
                    ms=7, label=f"N = {N:,}")
            ex = np.asarray(sd["copy_only_exact"][f"{sc}_N{N}"])
            ax.plot(x[m], ex[m], color=N_SHADES[theme][i], lw=1.2, ls=":")
        ax.set_xscale("log")
        ax.axhline(0.5, color=GREY, lw=1, ls="--")
        ax.set_xlabel(xl)
        ax.set_ylim(0.45, 1.01)
    axes[0].set_ylabel("chance the head-start hand wins")
    axes[0].set_title("same rates per molecule for every N")
    axes[1].set_title("same rates per concentration\n(bigger N = more background)")
    axes[0].legend(loc="lower right")
    axes[0].set_xlim(0.8, 70)
    axes[1].set_xlim(2e-3, 0.7)
    axes[1].text(0.98, 0.04, "dotted: copying only, exact answer", transform=axes[1].transAxes, ha="right",
                 fontsize=12, color=t["sub"])
    _frame(fig, t, "How big a head start picks the winner?", top=0.8, bottom=0.15)
    _save(fig, out, "seeded_bias", theme)


def make_all(summary, race_data, hist, out):
    for theme in THEMES:
        race(race_data, out, theme)
        histograms(hist, summary, out, theme)
        stopped_vs_real(hist, summary, out, theme)
        seeded(summary, out, theme)


def domains(times, shots, total, out, theme):
    """Bonus: 6 frames of the unstirred toy, plus a strip of every frame (10 per row) for the video and the page."""
    from . import domains as dm
    t = _setup(theme)
    bg = matplotlib.colors.to_rgb(t["bg"])
    n = len(times)
    pick = [int(round(f * (n - 1))) for f in (0.15, 0.3, 0.45, 0.6, 0.8, 1.0)]
    fig, axes = plt.subplots(1, 6, figsize=(16, 5.0))
    for ax, i in zip(axes, pick):
        ax.imshow(dm.colour(shots[i], bg), interpolation="nearest")
        ax.set_title(f"time {times[i]:.0f}\nA left {shots[i][3].sum() / total:.0%}", fontsize=13)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        for sp in ax.spines.values():
            sp.set_visible(False)
    fig.text(0.5, 0.08, "burnt orange = one hand   teal = mirror hand   grey = inactive mixed pairs   background = A not yet used",
             ha="center", fontsize=12, color=t["sub"])
    _frame(fig, t, "Toy: what Frank's equations do when the flask isn't stirred", top=0.76, bottom=0.12)
    _save(fig, out, "domains", theme)
    gap, size, cols = 2, shots.shape[-1], 10
    rows = int(np.ceil(n / cols))
    strip = np.ones((rows * (size + gap) - gap, cols * (size + gap) - gap, 3)) * np.asarray(bg)
    for k in range(n):
        r, c = divmod(k, cols)
        strip[r * (size + gap):r * (size + gap) + size, c * (size + gap):c * (size + gap) + size] = dm.colour(shots[k], bg)
    from PIL import Image  # Pillow ships with Matplotlib
    img = Image.fromarray((np.clip(strip, 0, 1) * 255).astype(np.uint8))
    img.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(out / f"domains_strip_{theme}.png", optimize=True)
