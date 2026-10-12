"""Figures, each in a light and a dark version, PNG and SVG (with <title> and <desc>).
Educational demo made to show an open-source tool."""
from html import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from . import constants as C  # noqa: E402

plt.rcParams["svg.fonttype"] = "none"  # keep text as text in the SVG (searchable, and the label stays readable)
plt.rcParams["svg.hashsalt"] = "nobel-2026-economics-spending"
THEMES = {
    "light": {"bg": "#ffffff", "fg": "#1b1f24", "grid": "#d0d7de", "muted": "#57606a"},
    "dark": {"bg": "#0d1117", "fg": "#e6edf3", "grid": "#30363d", "muted": "#8b949e"},
}
# Okabe-Ito colours.
BLUE, SKY, VERMILION, ORANGE, GREEN, PURPLE, GREY = ("#0072b2", "#56b4e9", "#d55e00", "#e69f00", "#009e73",
                                                     "#cc79a7", "#999999")
DATA_NOTE = ("US quarterly data per person: real non-durables + services (Fisher-chained), real disposable income "
             "(BEA, release of 30 Sep 2026).")
SIM_NOTE = "Simulated households (seed %d, %d runs per case). No data." % (C.SIM["seed"], C.SIM["reps"])


def _years(q):
    return "%s-%s" % (q[0][:4], q[1][:4])


def _pct_label(v):
    """Bar labels: whole per cents, except that a value just under 100 is never written as 100."""
    return "%.1f" % v if 99.5 <= v < 100 else "%.0f" % v


def _theme(fig, ax, t):
    fig.patch.set_facecolor(t["bg"])
    ax.set_facecolor(t["bg"])
    for s in ax.spines.values():
        s.set_color(t["muted"])
    ax.tick_params(colors=t["fg"], labelsize=11)
    ax.xaxis.label.set_color(t["fg"])
    ax.yaxis.label.set_color(t["fg"])
    ax.title.set_color(t["fg"])
    ax.grid(True, axis="y", color=t["grid"], lw=0.7, alpha=0.8)


def _titles(fig, t, title, subtitle, credit):
    h = fig.get_figheight()
    fig.suptitle(title, fontsize=17, fontweight="bold", color=t["fg"], x=0.02, y=1 - 0.12 / h, ha="left", va="top")
    fig.text(0.02, 1 - 0.5 / h, subtitle, color=t["muted"], fontsize=11, ha="left", va="top")
    fig.text(0.02, 0.012, C.LABEL + "  " + credit, color=t["muted"], fontsize=9.5, ha="left")


def _legend(ax, t, **kw):
    leg = ax.legend(frameon=False, fontsize=10, **kw)
    for tx in leg.get_texts():
        tx.set_color(t["fg"])


def _svg_title_desc(path, title, desc):
    s = path.read_text()
    i = s.index(">", s.index("<svg")) + 1
    head = s[:i].replace("<svg ", '<svg role="img" aria-labelledby="fig-title fig-desc" ', 1)
    path.write_text(head + '\n <title id="fig-title">%s</title>\n <desc id="fig-desc">%s</desc>' % (
        escape(title), escape(desc)) + s[i:])


def _save(make, stem, title, desc):
    C.RESULTS.mkdir(parents=True, exist_ok=True)
    out = []
    for name, t in THEMES.items():
        fig = make(t)
        for ext in ("png", "svg"):
            p = C.RESULTS / f"{stem}_{name}.{ext}"
            if ext == "png":
                fig.savefig(p, dpi=150, facecolor=fig.get_facecolor())
            else:
                fig.savefig(p, facecolor=fig.get_facecolor(), metadata={"Date": None})
                _svg_title_desc(p, title, desc + " " + C.LABEL)
            out.append(p)
        plt.close(fig)
    return out


def _ptext(p):
    return "p < 0.001" if p < 0.001 else "p = %.3f" % p


def _qx(q):
    return int(q[:4]) + (int(q[-1]) - 1) / 4


def fig_hall(s):
    h = s["hall"]
    ser = h["series"]
    x = np.array([_qx(q) for q in ser["quarters"]])
    dc = np.array(ser["dc_pct"])
    fit = np.array(ser["fitted_lags_2_4_pre_2020_pct"])
    x_fit = x[:len(fit)]
    p24 = h["pre_2020"]
    rob = s["robustness_total_pce"]["hall"]
    names = [(k, _years(h[k]["quarters"])) for k in ("pre_2020", "full", "first_half", "second_half")]
    pre_y, full_y = names[0][1], names[1][1]
    title = "Can the past predict next quarter's spending?"
    desc = ("Left: quarterly growth of US real spending per person on non-durable goods and services, %s, and the "
            "regression's prediction from spending and income growth two to four quarters back, fitted on %s "
            "(in-sample R squared %.1f per cent). Right: R squared by sample, with lags two to four (the headline) "
            "and with lags one to four, where averaging within quarters adds predictability even under Hall's "
            "hypothesis; diamonds: lags two to four on total spending, durables included. Hall's 1978 benchmark "
            "for forward-looking households is zero." % (full_y.replace("-", " to "), pre_y.replace("-", " to "),
                                                       p24["lags_2_4"]["r2_pct"]))
    lim = 3.2

    def make(t):
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 6.8), gridspec_kw={"width_ratios": [1.7, 1]})
        fig.subplots_adjust(left=0.06, right=0.98, top=0.80, bottom=0.17, wspace=0.18)
        for ax in (a1, a2):
            _theme(fig, ax, t)
        hi = VERMILION if t["bg"] == "#ffffff" else ORANGE
        a1.axhline(0, color=t["muted"], lw=0.8)
        a1.axvspan(_qx("2020Q1"), x[-1] + 0.25, color=t["grid"], alpha=0.35, lw=0)
        a1.text(_qx("2020Q1") + 0.3, -lim + 0.15, "left out of\nthe headline", color=t["muted"], fontsize=9.5)
        a1.plot(x, np.clip(dc, -lim, lim), "-", color=GREY, lw=1.1, label="actual growth")
        a1.plot(x_fit, np.clip(fit, -lim, lim), "-", color=hi, lw=1.8,
                label="predicted from lags 2-4, fitted %s (R² %.1f %%)" % (pre_y, p24["lags_2_4"]["r2_pct"]))
        off = ["%s %+.1f" % (q, v["dc_pct"]) for q, v in s["pandemic"]["quarters"].items() if abs(v["dc_pct"]) > lim]
        a1.text(0.99, 0.97, "off the scale: " + ", ".join(off), transform=a1.transAxes, ha="right", va="top",
                color=t["muted"], fontsize=9.5)
        a1.set_ylim(-lim - 0.1, lim + 0.1)
        a1.set_ylabel("growth from the previous quarter (log points, about %)", fontsize=11.5)
        a1.set_title("A. Non-durables + services: growth per person and its prediction (clipped at ±%.1f)" % lim,
                     fontsize=12.5, loc="left", color=t["fg"])
        _legend(a1, t, loc="lower left", ncol=2)
        xb = np.arange(len(names))
        r24 = [h[k]["lags_2_4"]["r2_pct"] for k, _ in names]
        r14 = [h[k]["r2_pct"] for k, _ in names]
        rp = [rob[k]["lags_2_4"]["r2_pct"] for k, _ in names]
        a2.bar(xb - 0.2, r24, 0.4, color=BLUE if t["bg"] == "#ffffff" else SKY, label="lags 2-4 (headline)")
        a2.bar(xb + 0.2, r14, 0.4, color=GREY, label="lags 1-4 (includes the averaging effect)")
        a2.plot(xb - 0.2, rp, "D", color=t["fg"], mfc="none", ms=7, mew=1.4,
                label="lags 2-4, total PCE (durables in)")
        for i, (k, _) in enumerate(names):
            a2.text(i - 0.2, max(r24[i], rp[i]) + 0.9, "%.1f" % r24[i], ha="center", color=t["fg"], fontsize=10)
            a2.text(i + 0.2, r14[i] + 0.6, "%.1f" % r14[i], ha="center", color=t["fg"], fontsize=10)
            a2.text(i, -3.6, "lags 2-4\n" + _ptext(h[k]["lags_2_4"]["p"]), ha="center", color=t["muted"],
                    fontsize=9)
        a2.set_xticks(xb, [n for _, n in names])
        a2.set_ylim(-5.5, max(r14) + 8)
        a2.axhline(0, color=t["muted"], lw=0.8)
        a2.set_ylabel("share of the variance explained, R² (%)", fontsize=11.5)
        a2.set_title("B. How much the past predicts (in-sample)", fontsize=12.5, loc="left", color=t["fg"])
        _legend(a2, t, loc="upper left")
        _titles(fig, t, title, DATA_NOTE + " Hall's benchmark: zero.",
                "Hall (1978); Working (1960); HAC (Newey-West, %d lags) tests." % C.HAC_LAGS)
        return fig

    return _save(make, "hall_test", title, desc)


def fig_lambda(s):
    L = s["lambda"]
    pub = L["published"]["rows"]
    rng = L["published"]["iv_range"]
    R = s["robustness_total_pce"]["lambda"]
    rows = [("Campbell and Mankiw 1989, " + L["published"]["sample"], [
        ("income growth, lags 2-4 (their row 2)", pub["2"]["lambda"], pub["2"]["ci95"], None, None),
        ("consumption growth, lags 2-4 (row 4)", pub["4"]["lambda"], pub["4"]["ci95"], None, None),
        ("both, plus log(c / y) (row 8)", pub["8"]["lambda"], pub["8"]["ci95"], None, None)])]
    sets = {"cm_window": (("income", "income growth, lags 2-4 (row 2)"), ("consumption", "consumption growth (row 4)"),
                          ("row8", "both, plus log(c / y) (row 8)"), ("both", "both")),
            "pre_2020": (("income", "income growth, lags 2-4"), ("consumption", "consumption growth"),
                         ("both", "both")),
            "full": (("income", "income growth, lags 2-4"), ("consumption", "consumption growth"), ("both", "both"))}
    for key, items in sets.items():
        q = L[key]["quarters"]
        rows.append(("ours, %s to %s (non-durables + services)" % (q[0], q[1]), [
            (lab, L[key][z]["lambda"], L[key][z]["ci95"], L[key][z]["effective_F"], L[key][z]["anderson_rubin"])
            for z, lab in items]))
    q = R["pre_2020"]["quarters"]
    rows.append(("robustness: total PCE (durables in), %s to %s" % (q[0], q[1]), [
        ("both", R["pre_2020"]["both"]["lambda"], R["pre_2020"]["both"]["ci95"], R["pre_2020"]["both"]["effective_F"],
         R["pre_2020"]["both"]["anderson_rubin"])]))
    title = "What share of income goes to households who spend as they earn?"
    desc = ("Instrumental-variables estimates of lambda, the share of income going to hand-to-mouth households: "
            "Campbell and Mankiw's published values for 1953 to 1986 with 95 per cent intervals (the shaded band is "
            "the range of their Table 1 estimates, %.3f to %.3f), and ours on US non-durables and services for "
            "their window, 1953 to 1986, for 1953 to 2019 and for 1953 to 2026, plus total spending for 1953 to "
            "2019, each with its 95 per cent interval (solid) and its weak-instrument-robust Anderson-Rubin set "
            "(dashed, below). Open markers: effective F (Montiel Olea and Pflueger) of %d or less." % (
                rng[0], rng[1], C.WEAK_F))
    colours = [GREY, GREEN, BLUE, PURPLE, ORANGE]
    lo_x, hi_x = -1.0, 2.6

    def make(t):
        fig, ax = plt.subplots(figsize=(15, 11))
        fig.subplots_adjust(left=0.30, right=0.86, top=0.89, bottom=0.10)
        _theme(fig, ax, t)
        ax.grid(True, axis="x", color=t["grid"], lw=0.7, alpha=0.8)
        ax.grid(False, axis="y")
        ax.axvspan(rng[0], rng[1], color=GREY, alpha=0.18, lw=0)
        y, ticks, labels = 0, [], []
        ax.text((rng[0] + rng[1]) / 2, -len(rows[0][1]) - 0.62, "their Table 1 range", color=t["muted"], fontsize=9,
                ha="center", va="center")
        for gi, (group, items) in enumerate(rows):
            col = colours[gi] if not (t["bg"] != "#ffffff" and colours[gi] == BLUE) else SKY
            ax.text(lo_x + 0.02, y - 0.35, group, color=t["fg"], fontsize=11, fontweight="bold", va="center")
            for lab, lam, ci, f, ar in items:
                y -= 1
                weak = f is not None and not f > C.WEAK_F
                ax.plot(ci, [y, y], "-", color=col, lw=2.2)
                ax.plot([lam], [y], "o", ms=9, color=col, mfc=t["bg"] if weak else col, mew=2)
                ticks.append(y)
                labels.append(lab)
                if f is not None:
                    ax.text(hi_x + 0.04, y, "eff. F = %.2f" % f, color=t["muted"], fontsize=9.5, va="center")
                if ar is not None:
                    ya = y - 0.32
                    if ar["empty"]:
                        ax.text(lo_x + 0.04, ya, "AR set empty", color=col, fontsize=8.5, va="center")
                    for a0, a1 in ar["set95"]:
                        ax.plot([max(a0, lo_x), min(a1, hi_x)], [ya, ya], "--", color=col, lw=1.4)
                        if a0 < lo_x:
                            ax.plot([lo_x + 0.02], [ya], "<", color=col, ms=6)
                        if a1 > hi_x:
                            ax.plot([hi_x - 0.02], [ya], ">", color=col, ms=6)
            y -= 1.0
        for v, txt in ((0, "0: all forward-looking (Hall)"), (1, "1: all hand-to-mouth")):
            ax.axvline(v, color=t["muted"], lw=1, ls=":")
            ax.text(v + 0.02, 0.75, txt, color=t["muted"], fontsize=9.5, va="center")
        ax.set_yticks(ticks, labels)
        ax.tick_params(axis="y", labelsize=10)
        ax.set_xlim(lo_x, hi_x)
        ax.set_ylim(y + 0.5, 1.2)
        ax.set_xlabel("lambda: 95 %% interval (solid), Anderson-Rubin set (dashed; arrow = goes on), open marker: "
                      "effective F %d or less" % C.WEAK_F, fontsize=11)
        _titles(fig, t, title, DATA_NOTE + " Theirs: the same concept, 1982 dollars.",
                "Campbell and Mankiw (1989), Table 1, p. 192; ours: HAC (Newey-West, %d lags); Anderson and Rubin "
                "(1949); Montiel Olea and Pflueger (2013)." % C.HAC_LAGS)
        return fig

    return _save(make, "lambda", title, desc)


def fig_control(s):
    c = s["control"]
    bins = np.array(c["hist_bins"])
    mid = (bins[:-1] + bins[1:]) / 2
    cs = c["cases"]
    title = "A control: simulated households with a known share"
    desc = ("Simulated mix of forward-looking households (consumption a random walk) and hand-to-mouth households "
            "with a share of %g of income, %d quarters, %d runs per case. Left: estimates of the share when past "
            "income predicts income growth (persistence %g); middle: when it barely does (persistence %g); right: "
            "how often Hall's test rejects at the 5 per cent level, how often the 95 per cent interval holds the "
            "true share, and how often the Anderson-Rubin set does." % (C.SIM["lambda"], c["n_regression"], C.SIM["reps"], C.SIM["rho"], C.SIM["rho_weak"]))

    def make(t):
        fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(16, 7.4), gridspec_kw={"width_ratios": [1, 1, 1.1]})
        fig.subplots_adjust(left=0.05, right=0.98, top=0.82, bottom=0.27, wspace=0.22)
        hm = BLUE if t["bg"] == "#ffffff" else SKY
        for ax, (k_h, k_r), lab in ((a1, ("hand_to_mouth", "random_walk"), "A. Past income predicts income"),
                                    (a2, ("hand_to_mouth_weak", "random_walk_weak"),
                                     "B. Past income barely predicts income")):
            _theme(fig, ax, t)
            for k, col, name in ((k_r, GREY, "true share 0 (random walk)"),
                                 (k_h, hm, "true share %g" % C.SIM["lambda"])):
                ax.bar(mid, cs[k]["lambda_hist"], width=0.05, color=col, alpha=0.75, label=name)
                ax.axvline(cs[k]["lambda_true"], color=col, lw=2, ls="--")
            ax.set_xlim(-0.6, 1.6)
            ax.set_xlabel("estimated share (lambda), lags 2-4 as instruments", fontsize=11)
            ax.set_ylabel("runs (of %d)" % C.SIM["reps"], fontsize=11)
            ax.set_title("%s (median F = %.1f)" % (lab, cs[k_h]["median_first_stage_F"]), fontsize=12, loc="left", color=t["fg"])
            _legend(ax, t, loc="upper left" if ax is a2 else "center right")
        _theme(fig, a3, t)
        order = [("random_walk", "share 0\nstrong"), ("hand_to_mouth", "share %g\nstrong" % C.SIM["lambda"]),
                 ("random_walk_weak", "share 0\nweak"), ("hand_to_mouth_weak", "share %g\nweak" % C.SIM["lambda"])]
        xb = np.arange(len(order))
        bars = [("hall_reject_pct", VERMILION, "Hall's test rejects (5 % level)"),
                ("ci95_coverage_pct", GREEN, "95 % interval holds the true share"),
                ("ar_coverage_pct", PURPLE, "Anderson-Rubin set holds it")]
        for j, (key, col, name) in enumerate(bars):
            v = [cs[k][key] for k, _ in order]
            off = (j - 1) * 0.27
            a3.bar(xb + off, v, 0.27, color=col, label=name)
            for i in range(len(order)):
                a3.text(xb[i] + off, v[i] + 1.5, _pct_label(v[i]), ha="center", color=t["fg"], fontsize=8.5)
        a3.axhline(c["test_level_pct"], color=t["muted"], lw=1, ls=":")
        a3.set_xticks(xb, [n for _, n in order])
        a3.set_ylim(0, 106)
        a3.set_ylabel("share of runs (%)", fontsize=11)
        a3.set_title("C. What the tests catch", fontsize=12, loc="left", color=t["fg"])
        _legend(a3, t, loc="upper center", ncol=1, bbox_to_anchor=(0.5, -0.12), handlelength=1.2)
        _titles(fig, t, title, SIM_NOTE + " Same number of quarters as the US data.",
                "Campbell and Mankiw (1989) model; toy values.")
        return fig

    return _save(make, "control", title, desc)
