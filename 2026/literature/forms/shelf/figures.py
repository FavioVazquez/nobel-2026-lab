"""Figures for the forms shelf, the 22! card and the prize history, light and dark, PNG + SVG."""
import random

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

from . import style
from . import works as W

SEL = "Committee bibliography, 'a selection' (nobelprize.org, 2026-10-08)."


def forms_count(rows, summary, outdir, theme):
    t = style.apply(theme)
    tags = sorted(W.TAG_ORDER, key=lambda k: summary["works_per_tag"][k])
    fig, ax = plt.subplots(figsize=(10, 7.2))
    fig.subplots_adjust(left=0.36, right=0.95, top=0.80, bottom=0.12)
    for i, tag in enumerate(tags):
        n_line = sum(1 for r in rows if tag in r["tags"]
                     and any(e["tag"] == tag and e["basis"] == "line" for e in r["evidence"]))
        n_all = summary["works_per_tag"][tag]
        ax.barh(i, n_line, color=t["ink"], height=0.62)
        ax.barh(i, n_all - n_line, left=n_line, color=t["paper"], edgecolor=t["accent"], hatch="///",
                linewidth=1.4, height=0.62)
        ax.text(n_all + 0.3, i, str(n_all), va="center", fontsize=16, color=t["ink"])
    ax.set_yticks(range(len(tags)), [W.TAGS[k] for k in tags], fontsize=15)
    ax.set_xlim(0, max(summary["works_per_tag"].values()) + 2.5)
    ax.xaxis.set_major_locator(plt.MultipleLocator(2))
    ax.tick_params(axis="x", labelsize=13)
    ax.set_xlabel("entries in the Committee's list that carry this form", fontsize=14)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.02, 0.95, "Her books by the forms named on them", fontsize=21, weight="bold")
    fig.text(0.02, 0.895, f"{summary['entries']} entries (1981–2025) in the Nobel Committee's bibliography, 'a selection'. "
             f"{summary['entries_with_no_tag']} name no form.", fontsize=13, color=t["muted"])
    fig.text(0.02, 0.855, "solid = named on the book's own line (title, subtitle, note)   "
             "hatched = named only in the Committee's essay", fontsize=12.5, color=t["muted"])
    style.footer(fig, t, "One book can carry several forms.")
    return style.save(fig, outdir, "forms_count", theme, title="Her books by the forms named on them",
                      desc=f"Bar chart: the {summary['entries']} entries of the Nobel Committee's bibliography (a selection) "
                           "by the form their own line or the Committee's essay names, from the classical-dialogue tag "
                           f"({summary['works_per_tag']['classical']}) to scholarly thesis (1); solid parts named on the line, "
                           f"hatched parts only in the Committee's essay; {summary['entries_with_no_tag']} entries name no form.")


def forms_matrix(rows, outdir, theme):
    t = style.apply(theme)
    rs = sorted(rows, key=lambda r: (r["year"], r["n"]))
    tags = W.TAG_ORDER
    fig, ax = plt.subplots(figsize=(13, 7.6))
    fig.subplots_adjust(left=0.25, right=0.985, top=0.83, bottom=0.14)
    for x, r in enumerate(rs):
        ax.plot([x, x], [-0.6, len(tags) - 0.4], color=t["pencil"], lw=0.8, zorder=0)
        for tag in r["tags"]:
            y = len(tags) - 1 - tags.index(tag)
            by_line = any(e["tag"] == tag and e["basis"] == "line" for e in r["evidence"])
            if by_line:
                ax.scatter(x, y, s=95, marker="s", color=t["ink"], zorder=3)
            else:
                ax.scatter(x, y, s=110, marker="o", facecolor=t["paper"], edgecolor=t["accent"], linewidth=2.2, zorder=3)
    ax.set_yticks(range(len(tags)), [W.TAGS[k] for k in reversed(tags)], fontsize=13)
    years = [r["year"] for r in rs]
    ticks, labels, seen = [], [], set()
    for x, y in enumerate(years):
        dec = y // 10 * 10
        if dec not in seen:
            seen.add(dec)
            ticks.append(x)
            labels.append(str(y))
    ax.set_xticks(ticks, labels, fontsize=12)
    ax.set_xlim(-1, len(rs))
    ax.set_xlabel("each pencil line is one entry, in order of year", fontsize=13)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.02, 0.95, "Forms, entry by entry", fontsize=21, weight="bold")
    fig.text(0.02, 0.895, "ink square: named on the book's own line      red ring: named only in the Committee's essay",
             fontsize=13, color=t["muted"])
    fig.text(0.02, 0.86, SEL + " Our tags, each resting on a quoted subtitle or Committee phrase.", fontsize=12,
             color=t["muted"])
    style.footer(fig, t)
    return style.save(fig, outdir, "forms_matrix", theme, title="Forms, entry by entry",
                      desc="Dot matrix of the Committee's bibliography entries in order of year (1981-2025) against eleven "
                           "form tags: ink squares where the book's own line names the form, red rings where only the "
                           "Committee's essay does.")


def float_card(card, outdir, theme):
    t = style.apply(theme)
    fig = plt.figure(figsize=(10, 6.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 64)
    ax.axis("off")
    ax.text(4, 58.5, "22 chapbooks, any order", fontsize=24, weight="bold")
    ax.text(4, 54, "Float (2016): the Committee says its 22 chapbooks can be read in any order.",
            fontsize=13.5, color=t["muted"])

    def row(order, y, color, fill):
        w, gap, x0 = 3.6, 0.55, 4
        for i, k in enumerate(order):
            x = x0 + i * (w + gap)
            ax.add_patch(FancyBboxPatch((x, y), w, 7.5, boxstyle="round,pad=0.02,rounding_size=0.3",
                                        facecolor=fill, edgecolor=color, linewidth=1.6))
            ax.text(x + w / 2, y + 3.7, str(k), ha="center", va="center", fontsize=11.5, color=color)

    row(range(1, 23), 41, t["ink"], t["paper"])
    order = list(range(1, 23))
    random.Random(2026).shuffle(order)
    row(order, 29, t["accent"], t["paper"])
    ax.text(4, 50.0, "one order", fontsize=13, color=t["ink"])
    ax.text(4, 38.0, "another (one of the rest, shuffled with a fixed seed)", fontsize=13, color=t["accent"])
    ax.text(4, 22.0, "22! =", fontsize=22, color=t["ink"])
    ax.text(14.5, 22.0, card["orderings_grouped"], fontsize=24, weight="bold", color=t["accent"])
    mant, ex = card["orderings_scientific"].split(" × 10^")
    ax.text(4, 15.5, f"about {mant} × $10^{{{ex}}}$ ways to order them (22 × 21 × 20 × … × 2 × 1)", fontsize=14)
    ym, ye = f"{card['years_at_one_ordering_per_second']:.1e}".split("e")
    ax.text(4, 10.0, f"At one order per second: about {ym} × $10^{{{int(ye)}}}$ years, "
            f"some {card['times_age_of_universe']:,} times the age of the universe.", fontsize=13.5, color=t["muted"])
    ax.text(4, 3.0, style.LABEL + "  Arithmetic only: it says nothing about how the book is read.",
            fontsize=9.5, color=t["muted"])
    return style.save(fig, outdir, "float_22", theme, title="22 chapbooks, any order",
                      desc="Twenty-two chapbook outlines in order and shuffled; 22! = 1,124,000,727,777,607,680,000 "
                           "orders, about 1.1 x 10^21. Arithmetic only.")


def prize_by_decade(hist, outdir, theme):
    t = style.apply(theme)
    dec = hist["by_decade"]
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.78, bottom=0.17)
    for i, d in enumerate(dec):
        ax.bar(i, d["laureates"], color=t["paper"], edgecolor=t["ink"], linewidth=1.6, width=0.72)
        ax.bar(i, d["women"], color=t["accent"], width=0.72)
        ax.text(i, d["laureates"] + 0.25, f'{d["women"]}/{d["laureates"]}', ha="center", fontsize=12.5)
    labels = ["1900s"] + ["'" + d["decade"][2:] for d in dec[1:-1]] + ["2020s\n(7 yrs)"]
    ax.set_xticks(range(len(dec)), labels, fontsize=12.5)
    ax.set_ylabel("Literature laureates", fontsize=14)
    ax.set_ylim(0, 13)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    tot = hist["totals"]
    fig.text(0.02, 0.94, f"{tot['women']} women among {tot['laureates']} Literature laureates", fontsize=21,
             weight="bold")
    fig.text(0.02, 0.885, "Red: women (Nobel API 'gender' field). Outline: all laureates. Labels: women/all.",
             fontsize=13, color=t["muted"])
    fig.text(0.02, 0.845, "1901–2026. No award in 1914, 1918, 1935, 1940–43; shared in 1904, 1917, 1966, 1974.",
             fontsize=12.5, color=t["muted"])
    style.footer(fig, t, "Source: Nobel Prize API v2.1 (CC0), 2026-10-08.")
    return style.save(fig, outdir, "prize_by_decade", theme, title="Women among Literature laureates, by decade",
                      desc="Bar chart of the 123 Literature laureates 1901-2026 by decade, with the 19 women filled in "
                           "red; the 2020s have 4 of 7. Source: Nobel Prize API (CC0).")


def prize_timeline(hist, api, outdir, theme):
    t = style.apply(theme)
    laur = api["laureates"]
    fig, ax = plt.subplots(figsize=(12, 4.6))
    fig.subplots_adjust(left=0.03, right=0.98, top=0.70, bottom=0.2)
    canada = {r["id"] for r in laur if r["birth.place.country.en"] == "Canada"}
    seen = {}
    for r in laur:
        y = int(r["nobelPrizes.awardYear"])
        k = seen.get(y, 0)
        seen[y] = k + 1
        x = y + 0.45 * k
        woman = r["gender"] == "female"
        ax.add_patch(Rectangle((x - 0.32, 0), 0.64, 1.0 if woman else 0.62,
                               facecolor=t["accent"] if woman else t["paper"],
                               edgecolor=t["accent"] if woman else t["ink"], linewidth=0.9))
        if r["id"] in canada:
            name = r["knownName.en"]
            note = {"Saul Bellow": "Saul Bellow 1976\nborn in Canada,\ncounted as American",
                    "Alice Munro": "Alice Munro 2013\n'Canadian author'",
                    "Anne Carson": "Anne Carson 2026\n'Canadian author'"}[name]
            ax.annotate(note, (x, 1.05 if woman else 0.67), xytext=(x - {"Saul Bellow": 4, "Alice Munro": 24, "Anne Carson": 6}[name], 1.55),
                        fontsize=11, ha="center", color=t["ink"],
                        arrowprops=dict(arrowstyle="-", color=t["accent2"], lw=1.4))
    ax.set_xlim(1899, 2028)
    ax.set_ylim(0, 2.3)
    ax.set_yticks([])
    yrs = [1901, 1925, 1950, 1975, 2000, 2026]
    ax.set_xticks(yrs, [str(y) for y in yrs], fontsize=12.5)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.text(0.02, 0.92, "123 laureates, one book each", fontsize=20, weight="bold")
    fig.text(0.02, 0.84, "tall red: women (19)   short outline: men (104)   blue lines: born in Canada (API birth country)",
             fontsize=12.5, color=t["muted"])
    style.footer(fig, t, "Source: Nobel Prize API v2.1 (CC0), 2026-10-08; press releases 1976, 2013, 2026.")
    return style.save(fig, outdir, "prize_timeline", theme, title="123 laureates, one book each",
                      desc="The 123 Literature laureates as small books along the years 1901-2026, women tall and red; "
                           "Saul Bellow (1976), Alice Munro (2013) and Anne Carson (2026), born in Canada, marked with "
                           "the field each counts under.")
