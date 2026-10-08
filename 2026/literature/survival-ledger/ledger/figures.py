"""The ink bookshelf and the Sappho dot grid, light and dark, PNG + SVG."""
import random

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from . import style


def _spine(ax, x, y, w, h, kind, t):
    """kind: 'inked' (survives), 'half' (survives, authorship disputed), 'lost' (pencil), 'maybe' (only in the
    high end of the range: dashed pencil), 'scrap' (lost, fragments survive)."""
    if kind == "inked":
        ax.add_patch(Rectangle((x, y), w, h, facecolor=t["ink"], edgecolor=t["ink"], lw=0.8))
    elif kind == "half":
        ax.add_patch(Rectangle((x, y), w, h, facecolor=t["paper"], edgecolor=t["ink"], lw=1.0, hatch="////"))
    elif kind == "lost":
        ax.add_patch(Rectangle((x, y), w, h, facecolor="none", edgecolor=t["pencil"], lw=0.9))
    elif kind == "maybe":
        ax.add_patch(Rectangle((x, y), w, h, facecolor="none", edgecolor=t["pencil"], lw=0.9, ls=(0, (2, 2))))
    elif kind == "scrap":
        ax.add_patch(Rectangle((x, y), w, h, facecolor="none", edgecolor=t["pencil"], lw=0.9))
        ax.add_patch(Rectangle((x + w * 0.2, y + h * 0.15), w * 0.6, h * 0.12, facecolor=t["ink"], lw=0))


def shelf(rows, outdir, theme):
    t = style.apply(theme)
    shelf_rows = [r for r in rows if r.get("shelf")]
    n = len(shelf_rows)
    row_h = 1.0
    H0 = 1.45 * n + 3.2
    fig = plt.figure(figsize=(12, H0))
    ax = fig.add_axes([0.02, 0.6 / H0, 0.96, 1 - 0.6 / H0 - 1.75 / H0])
    max_items = max(s["shelf"]["total"][1] for s in shelf_rows)
    per_line = 66
    w_unit = 1.0
    ax.set_xlim(-1, per_line * w_unit + 1)
    y = 0
    for r in shelf_rows:
        s = r["shelf"]
        lo, hi = s["total"]
        slo, shi = s["survive"]
        kinds = []
        for i in range(hi):
            if i < slo:
                kinds.append("inked")
            elif i < shi:
                kinds.append("half")
            elif i < lo:
                kinds.append("scrap" if s.get("fragments") else "lost")
            else:
                kinds.append("maybe")
        lines = (hi + per_line - 1) // per_line
        top = y
        ax.text(0, -(top + 0.05), r["author"], fontsize=17, weight="bold", va="center")
        ax.text(per_line * w_unit, -(top + 0.05), s["label"], fontsize=13, va="center", ha="right", color=t["muted"])
        for i, k in enumerate(kinds):
            line, col = divmod(i, per_line)
            _spine(ax, col * w_unit + 0.12, -(top + 0.95 + line * 0.62), w_unit * 0.76, 0.55, k, t)
        y = top + 0.95 + (lines - 1) * 0.62 + 0.55 + 0.45
    ax.set_ylim(-(y + 0.1), 0.6)
    ax.axis("off")
    H = fig.get_figheight()
    fig.text(0.02, 1 - 0.55 / H, "What survives of the ancient authors the Nobel Committee names", fontsize=20,
             weight="bold")
    fig.text(0.02, 1 - 0.95 / H, "One mark per play or book (modern estimates; ancient counts in the ledger). "
             "Solid ink: survives.  Hatched: survives, authorship disputed.", fontsize=12.5, color=t["muted"])
    fig.text(0.02, 1 - 1.27 / H, "Pencil outline: lost.  Dashed: only in the high end of the range (Sophocles: more than 120, open-ended).  "
             "Small ink bar: lost, fragments survive.", fontsize=12.5, color=t["muted"])
    style.footer(fig, t, "Counts are estimates with ranges; every source is in results/ledger.json.")
    del max_items
    return style.save(fig, outdir, "bookshelf", theme,
                      title="What survives of the ancient authors the Nobel Committee names",
                      desc="An ink bookshelf, one mark per play or book at the modern estimate: Sophocles 7 of more "
                           "than 120, Euripides 18 or 19 of about 90, Aeschylus 7 (one disputed) of 70 to 90, "
                           "Stesichoros 26 books in fragments, Sappho 8 or 9 books in fragments, Catullus one book "
                           "through one lost manuscript, Thucydides all 8 books but unfinished.")


def sappho_grid(row, outdir, theme, seed=2026):
    t = style.apply(theme)
    g = row["grid"]
    total, inked, book1 = g["total"], g["inked"], g["book1"]
    side = 100
    assert side * side == total
    fig = plt.figure(figsize=(8.6, 10.6))
    ax = fig.add_axes([0.06, 0.135, 0.88, 0.75])
    idx = list(range(total))
    random.Random(seed).shuffle(idx)
    inked_set = set(idx[:inked])
    xs_p, ys_p, xs_i, ys_i = [], [], [], []
    for k in range(total):
        r, c = divmod(k, side)
        (xs_i if k in inked_set else xs_p).append(c)
        (ys_i if k in inked_set else ys_p).append(-r)
    ax.scatter(xs_p, ys_p, s=2.2, color=t["pencil"], linewidths=0)
    ax.scatter(xs_i, ys_i, s=9, color=t["ink"], linewidths=0)
    # Book I: 1,320 verses = 13 full rows + 20 dots
    full, rest = divmod(book1, side)
    bx = [-0.8, side - 0.2, side - 0.2, rest - 0.2, rest - 0.2, -0.8, -0.8]
    by = [0.8, 0.8, -(full - 0.5), -(full - 0.5), -(full + 0.5), -(full + 0.5), 0.8]
    ax.plot(bx, by, color=t["accent"], lw=1.6)
    ax.set_xlim(-2, side + 1)
    ax.set_ylim(-(side + 1), 2)
    ax.set_aspect("equal")
    ax.axis("off")
    alt = g["alt_total"]
    ra = alt // side
    ax.plot([-0.8, side - 0.2], [-(ra - 0.5), -(ra - 0.5)], color=t["accent2"], lw=1.6, ls=(0, (4, 2)))
    fig.text(0.06, 0.965, "Sappho: about 650 of some 10,000 lines", fontsize=21, weight="bold")
    fig.text(0.06, 0.937, "ESTIMATE", fontsize=14, color=t["accent"], weight="bold")
    fig.text(0.06, 0.915, f"{total:,} dots = a modern estimate of all she wrote; {inked} inked = the lines that survive.",
             fontsize=12, color=t["muted"])
    fig.text(0.06, 0.895, "The inked dots are scattered at random: where they sit means nothing.", fontsize=12,
             color=t["muted"])
    fig.text(0.06, 0.112, f"Red outline: Book I alone, {book1:,} verses: the number on the papyrus roll's own",
             fontsize=11.5, color=t["accent"])
    fig.text(0.06, 0.092, "end-title (P.Oxy. 1231 fr. 56; Grenfell & Hunt 1914, p. 20).", fontsize=11.5, color=t["accent"])
    fig.text(0.06, 0.068, f"Blue dashes: the older estimate, about {alt:,} verses in all (Grenfell & Hunt 1914).",
             fontsize=11.5, color=t["accent2"])
    fig.text(0.06, 0.044, "Survives: about 650 lines. Only fragment 1 (the Ode to Aphrodite) is certainly complete.",
             fontsize=11.5, color=t["muted"])
    style.footer(fig, t)
    return style.save(fig, outdir, "sappho_grid", theme, title="Sappho: about 650 of some 10,000 lines (estimate)",
                      desc="A 100 by 100 grid of 10,000 dots, a modern estimate of all the lines Sappho wrote, with "
                           "650 dots inked at random positions for the lines that survive; Book I (1,320 verses, from "
                           "the papyrus end-title) outlined in red; the older 9,000 estimate marked with a dashed line.")
