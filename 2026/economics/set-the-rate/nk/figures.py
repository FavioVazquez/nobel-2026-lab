"""Figures, each in a light and a dark version, PNG and SVG (with <title> and <desc>).
Educational demo made to show an open-source tool."""
from html import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

from . import constants as C  # noqa: E402

plt.rcParams["svg.fonttype"] = "none"  # keep text as text in the SVG (searchable, and the label stays readable)
plt.rcParams["svg.hashsalt"] = "nobel-2026-economics-set-the-rate"
SUBTITLE = "Three-equation New Keynesian model, quarterly, calibration as in Galí (2015), ch. 3. Pure simulation, no data."
THEMES = {
    "light": {"bg": "#ffffff", "fg": "#1b1f24", "grid": "#d0d7de", "muted": "#57606a"},
    "dark": {"bg": "#0d1117", "fg": "#e6edf3", "grid": "#30363d", "muted": "#8b949e"},
}
# Okabe-Ito colours.
BLUE, SKY, VERMILION, ORANGE, GREY = "#0072b2", "#56b4e9", "#d55e00", "#e69f00", "#999999"


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


def _titles(fig, t, title):
    h = fig.get_figheight()
    fig.suptitle(title, fontsize=17, fontweight="bold", color=t["fg"], x=0.02, y=1 - 0.12 / h, ha="left", va="top")
    fig.text(0.02, 1 - 0.5 / h, SUBTITLE, color=t["muted"], fontsize=11, ha="left", va="top")
    fig.text(0.02, 0.012, C.LABEL + "  Woodford (2003); Clarida, Galí and Gertler (1999); Galí (2015).", color=t["muted"], fontsize=9.5, ha="left")


def _legend(ax, t, **kw):
    leg = ax.legend(frameon=False, fontsize=10.5, **kw)
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


PANELS = (("output_gap", "output gap (%)"), ("inflation", "inflation (pp a year)"),
          ("policy_rate", "policy rate (pp a year)"))


def _three(t, title, lines, q, subtitle_note):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.6))
    fig.subplots_adjust(left=0.05, right=0.98, top=0.76, bottom=0.17, wspace=0.22)
    for ax, (key, name) in zip(axes, PANELS):
        _theme(fig, ax, t)
        ax.axhline(0, color=t["muted"], lw=0.8)
        for label, paths, col, style in lines:
            ax.plot(q, paths[key][:len(q)], style, color=col, lw=2.4, ms=4, label=label)
        ax.set_title(name, fontsize=12.5, loc="left", color=t["fg"])
        ax.set_xlabel("quarters after the shock", fontsize=11)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if len(lines) > 1:
        _legend(axes[0], t, loc="lower right")
    _titles(fig, t, title)
    fig.text(0.02, 0.06, subtitle_note, color=t["muted"], fontsize=10, ha="left")
    return fig


def fig_demand(s):
    b = s["demand_shock"]
    q = np.arange(s["calibration"]["horizon_quarters"] + 1)
    title = "A spending shock (households less patient) under the rule"
    desc = ("Three panels over %d quarters: output gap, inflation and policy rate after households become less "
            "patient and the natural rate of interest rises by 1 percentage point a year. On impact the gap is %s %%, inflation %s and the rate %s percentage "
            "points a year; all three return to zero." % (q[-1], b["impact"]["output_gap"],
                                                         b["impact"]["inflation"], b["impact"]["policy_rate"]))

    def make(t):
        return _three(t, title, [("phi_pi = %g" % b["phi_pi"], b["paths"], BLUE if t["bg"] == "#ffffff" else SKY,
                                  "o-")], q, "Rule: i = %g pi + %g x. Shock persistence %g." % (
            b["phi_pi"], s["calibration"]["phi_y"], s["calibration"]["rho_demand"]))

    return _save(make, "demand_shock", title, desc)


def fig_cost_push(s):
    c = s["cost_push_shock"]
    q = np.arange(s["calibration"]["horizon_quarters"] + 1)
    title = "A cost-push (supply) shock: inflation up, output gap down"
    desc = ("Three panels over %d quarters after a cost-push shock that adds 1 percentage point a year to the Phillips curve, "
            "for the rule with phi_pi = %g and with phi_pi = %g. On impact inflation is %s vs %s and the gap %s vs %s."
            % (q[-1], c["baseline"]["phi_pi"], c["strong"]["phi_pi"], c["baseline"]["impact"]["inflation"],
               c["strong"]["impact"]["inflation"], c["baseline"]["impact"]["output_gap"],
               c["strong"]["impact"]["output_gap"]))

    def make(t):
        return _three(t, title, [
            ("phi_pi = %g" % c["baseline"]["phi_pi"], c["baseline"]["paths"], BLUE if t["bg"] == "#ffffff" else SKY,
             "o-"),
            ("phi_pi = %g (stronger)" % c["strong"]["phi_pi"], c["strong"]["paths"], VERMILION, "s--")], q,
            "Same shock, two rules. Shock persistence %g." % s["calibration"]["rho_cost_push"])

    return _save(make, "cost_push_shock", title, desc)


def fig_taylor(s):
    tp = s["taylor_principle"]
    title = "The Taylor principle: count the eigenvalues"
    desc = ("Eigenvalue moduli of the model with the rule, against the unit circle. With phi_pi = %g, %d of %d are "
            "outside (a unique bounded solution); with phi_pi = %g, %d of %d (many bounded solutions)." % (
                tp["active"]["phi_pi"], tp["active"]["outside_unit_circle"], tp["active"]["forward_looking_variables"],
                tp["passive"]["phi_pi"], tp["passive"]["outside_unit_circle"],
                tp["passive"]["forward_looking_variables"]))

    def make(t):
        fig, ax = plt.subplots(figsize=(11, 6))
        fig.subplots_adjust(left=0.08, right=0.97, top=0.80, bottom=0.17)
        _theme(fig, ax, t)
        ax.axhline(1, color=t["muted"], lw=1.4, ls="--")
        ax.text(0.5, 0.98, "unit circle\n(modulus 1)", color=t["muted"], fontsize=10, va="top", ha="center")
        for k, (key, col) in enumerate((("active", BLUE if t["bg"] == "#ffffff" else SKY), ("passive", VERMILION))):
            b = tp[key]
            mods = b["eigenvalue_moduli"]
            ax.bar([k - 0.17, k + 0.17], mods, width=0.3, color=col)
            for dx, m in zip((-0.17, 0.17), mods):
                ax.text(k + dx, m + 0.02, "%g" % m, ha="center", color=t["fg"], fontsize=11)
            verdict = "unique bounded solution" if b["unique_bounded_solution"] else "many bounded solutions"
            ax.text(k, -0.2, "%d of %d outside: %s" % (b["outside_unit_circle"], b["forward_looking_variables"],
                                                       verdict), ha="center", color=t["fg"], fontsize=11)
        ax.set_xticks([0, 1], ["phi_pi = %g" % tp["active"]["phi_pi"], "phi_pi = %g" % tp["passive"]["phi_pi"]])
        ax.set_xlim(-0.6, 1.6)
        ax.set_ylim(0, 1.6)
        ax.set_ylabel("eigenvalue modulus", fontsize=12)
        _titles(fig, t, title)
        return fig

    return _save(make, "taylor_principle", title, desc)


def fig_forward_guidance(s):
    fg = s["forward_guidance"]
    on, peg = fg["rule_on"], fg["pegged_puzzle"]
    q = np.arange(len(on["paths"]["output_gap"]))
    h = on["by_horizon"]
    title = "Forward guidance: a promised shift of the rule in quarter %d moves today" % fg["quarter"]
    desc = ("A: the rule stays on and its intercept is 1 percentage point a year lower in quarter %d only; today the "
            "output gap is %s %% and inflation %s. B: today's response for the same shift promised 0 to %d quarters "
            "ahead; inflation today peaks for quarter %d. C, the forward guidance puzzle: with the nominal rate held still "
            "until the promised quarter, today's response relative to a cut made today grows with the horizon." % (
                fg["quarter"], on["today"]["output_gap"], on["today"]["inflation"], h["quarters"][-1],
                on["inflation_peak"]["quarter"]))

    def make(t):
        fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(17, 6.2))
        fig.subplots_adjust(left=0.045, right=0.985, top=0.77, bottom=0.17, wspace=0.2)
        line = BLUE if t["bg"] == "#ffffff" else SKY
        for ax in (a1, a2, a3):
            _theme(fig, ax, t)
        for ax in (a1, a2):
            ax.axhline(0, color=t["muted"], lw=0.8)
        a1.step(q, on["paths"]["intercept_shift"], where="mid", color=GREY, lw=2.2, label="announced intercept shift")
        a1.plot(q, on["paths"]["policy_rate"], "^:", color=ORANGE, lw=2, ms=4, label="policy rate (pp a year)")
        a1.plot(q, on["paths"]["output_gap"], "o-", color=line, lw=2.4, ms=4, label="output gap (%)")
        a1.plot(q, on["paths"]["inflation"], "s--", color=VERMILION, lw=2.4, ms=4, label="inflation (pp a year)")
        a1.set_xlabel("quarter (today = 0)", fontsize=11)
        a1.set_title("A. Rule on, shift in quarter %d" % fg["quarter"], fontsize=12.5, loc="left", color=t["fg"])
        _legend(a1, t, loc="upper right")
        a2.plot(h["quarters"], h["output_gap_today"], "o-", color=line, lw=2.4, ms=5, label="output gap today (%)")
        a2.plot(h["quarters"], h["inflation_today"], "s--", color=VERMILION, lw=2.4, ms=5,
                label="inflation today (pp a year)")
        a2.set_xlabel("quarter of the promised shift", fontsize=11)
        a2.set_title("B. Rule on: today's response by horizon", fontsize=12.5, loc="left", color=t["fg"])
        _legend(a2, t, loc="upper right")
        ph = peg["by_horizon"]
        a3.plot(ph["quarters"], ph["output_gap_ratio"], "o-", color=line, lw=2.4, ms=5, label="output gap today")
        a3.plot(ph["quarters"], ph["inflation_ratio"], "s--", color=VERMILION, lw=2.4, ms=5, label="inflation today")
        a3.set_yscale("log")
        a3.set_ylabel("x the effect of the same cut made today", fontsize=11)
        a3.set_xlabel("quarter of the promised cut", fontsize=11)
        a3.set_title("C. The puzzle: nominal rate held still until then", fontsize=12.5, loc="left", color=t["fg"])
        _legend(a3, t, loc="upper left")
        _titles(fig, t, title)
        fig.text(0.02, 0.06, "Full rational expectations, perfect foresight after the announcement. C is relative "
                 "to quarter 0 (ratios, log scale), not a level.", color=t["muted"], fontsize=10, ha="left")
        return fig

    return _save(make, "forward_guidance", title, desc)


def all_figures(s):
    return fig_demand(s) + fig_cost_push(s) + fig_taylor(s) + fig_forward_guidance(s)
