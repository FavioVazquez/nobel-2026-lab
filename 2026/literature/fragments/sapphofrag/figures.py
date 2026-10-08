"""Figures, light and dark, PNG + SVG. Palette shared by the Literature lanes: warm paper, iron-gall ink, faded pencil,
one accent (the editors' hand). Colour is never the only cue: restorations also sit in a pale hole with brackets,
lost letters are dots, uncertain words keep Wharton's brackets.

Educational demos made to show an open-source tool. Not research.
"""
from __future__ import annotations

import json
import random
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402,F401
from matplotlib import font_manager  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import Polygon, Rectangle  # noqa: E402
from matplotlib.textpath import TextToPath  # noqa: E402

from .paths import FONTS, RESULTS  # noqa: E402

LABEL = "Educational demos made to show an open-source tool. Not research."
THEMES = {
    "light": dict(bg="#f3ece0", papyrus="#e3d3b4", fibre="#d4c19c", ink="#2b2118", pencil="#9c8f7a",
                  accent="#a8432a", wash="#efd9cc", second="#3f6e8c", sub="#5b4e40"),
    "dark": dict(bg="#1b1712", papyrus="#3a3024", fibre="#463a2b", ink="#efe6d6", pencil="#a39783",
                 accent="#e0876c", wash="#4a2f26", second="#7fb0d0", sub="#c9bba5"),
}
plt.rcParams["svg.hashsalt"] = "sapphofrag"  # stable ids: rebuilding gives the same SVG bytes
for f in FONTS.glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))
GREEK = FontProperties(family=["GFS Didot", "EB Garamond"])  # EB Garamond supplies ⟨ ⟩, missing from GFS Didot
BODY = FontProperties(family=["Literata", "EB Garamond"])
HAND = FontProperties(fname=str(FONTS / "Caveat[wght].ttf"))
_T2P = TextToPath()


def width(s: str, prop: FontProperties, size: float) -> float:
    """Advance width in points of s at the given size (spaces included)."""
    p = prop.copy()
    p.set_size(size)
    w, _, _ = _T2P.get_text_width_height_descent(s, p, ismath=False)
    return w


def page(w_pt: float, h_pt: float, t: dict):
    fig = plt.figure(figsize=(w_pt / 72, h_pt / 72))
    fig.patch.set_facecolor(t["bg"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_pt)
    ax.set_ylim(0, h_pt)
    ax.axis("off")
    ax.set_facecolor(t["bg"])
    return fig, ax


def ragged(x0, y0, x1, y1, rng, amp=3.0, step=9.0, sides="lrtb"):
    """A rectangle with torn edges on the named sides."""
    pts = []
    x = x0
    while x < x1:
        pts.append((x, y1 + (rng.uniform(-amp, amp) if "t" in sides else 0)))
        x += step * rng.uniform(0.6, 1.4)
    pts.append((x1, y1))
    y = y1
    while y > y0:
        pts.append((x1 + (rng.uniform(-amp, amp) if "r" in sides else 0), y))
        y -= step * rng.uniform(0.6, 1.4)
    pts.append((x1, y0))
    x = x1
    while x > x0:
        pts.append((x, y0 + (rng.uniform(-amp, amp) if "b" in sides else 0)))
        x -= step * rng.uniform(0.6, 1.4)
    pts.append((x0, y0))
    y = y0
    while y < y1:
        pts.append((x0 + (rng.uniform(-amp, amp) if "l" in sides else 0), y))
        y += step * rng.uniform(0.6, 1.4)
    return pts


def footer(ax, t, w, source, y=18):
    src = [source] if isinstance(source, str) else list(source)
    for k, line in enumerate(reversed(src)):
        ax.text(w / 2, y + 14 * (k + 1), line, ha="center", va="bottom", fontproperties=BODY, fontsize=9.5,
                color=t["sub"])
    ax.text(w / 2, y, LABEL, ha="center", va="bottom", fontproperties=BODY, fontsize=9.5, color=t["sub"],
            style="italic")


def save(fig, name, theme, title, desc):
    """PNG + SVG. The SVG gets role="img", a <title> and a <desc> for screen readers (and the lab label)."""
    fig.savefig(RESULTS / f"{name}_{theme}.png", dpi=150, facecolor=fig.get_facecolor())
    svg = RESULTS / f"{name}_{theme}.svg"
    fig.savefig(svg, facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    label_svg(svg, title, desc + " " + LABEL)


def label_svg(path, title: str, desc: str) -> None:
    from xml.sax.saxutils import escape
    text = path.read_text(encoding="utf-8")
    m = re.search(r"<svg\b[^>]*>", text)
    tag = m.group(0)
    new_tag = tag if 'role="img"' in tag else tag[:-1] + ' role="img">'
    meta = f"\n <title>{escape(title)}</title>\n <desc>{escape(desc.strip())}</desc>"
    path.write_text(text[:m.start()] + new_tag + meta + text[m.end():], encoding="utf-8")


# ---------------------------------------------------------------------------------------------------------------
def fig_papyrus(data: dict, theme: str):
    t = THEMES[theme]
    pap = data["papyrus"]
    lines = pap["lines"]
    fs, lead = 17.0, 27.0
    W = 640.0
    top_block, bottom_block = 118.0, 178.0
    H = top_block + lead * len(lines) + 40 + bottom_block
    fig, ax = page(W, H, t)
    rng = random.Random(1231)

    x_text = 92.0
    widths = [width(l["text"], GREEK, fs) for l in lines]
    x_right = x_text + max(widths) + 26
    y_top = H - top_block
    y_bot = y_top - lead * len(lines) - 14
    # the papyrus sheet (redrawn, not a photograph), torn on all sides
    ax.add_patch(Polygon(ragged(x_text - 26, y_bot, x_right, y_top + 6, rng, amp=5, step=14), closed=True,
                         facecolor=t["papyrus"], edgecolor=t["pencil"], linewidth=0.8, zorder=1))
    for k in range(int((y_top - y_bot) / 6)):  # horizontal fibres
        yy = y_bot + 3 + 6 * k + rng.uniform(-1, 1)
        ax.plot([x_text - 20, x_right - 6], [yy, yy + rng.uniform(-0.6, 0.6)], color=t["fibre"], lw=0.6,
                alpha=0.55, zorder=1.1)

    for i, l in enumerate(lines):
        y = y_top - lead * (i + 0.85)
        ax.text(x_text - 36, y, str(l["line"]), ha="right", va="baseline", fontproperties=BODY, fontsize=9,
                color=t["pencil"])
        x = x_text
        for s in l["spans"]:
            w = width(s["text"], GREEK, fs)
            if s["kind"] == "restored" and s["mark"] == "⟨⟩":
                ax.add_patch(Rectangle((x, y - 6), w, 22, facecolor=t["wash"], edgecolor="none", zorder=2))
            elif s["kind"] != "read":
                open_end = s["mark"].startswith("[ (open")
                x1 = (x_right + 4) if open_end else x + w
                hole = ragged(x - 1.5, y - 7.5, x1 + 1.5, y + 17, rng, amp=2.2, step=6,
                              sides="lrtb" if not open_end else "ltb")
                ax.add_patch(Polygon(hole, closed=True, facecolor=t["bg"] if s["kind"] == "lost" else t["wash"],
                                     edgecolor=t["pencil"], linewidth=0.6, linestyle=(0, (2, 2)), zorder=2))
            colour = {"read": t["ink"], "restored": t["accent"], "lost": t["pencil"]}[s["kind"]]
            ax.text(x, y, s["text"], ha="left", va="baseline", fontproperties=GREEK, fontsize=fs, color=colour,
                    zorder=3)
            x += w

    # header
    ax.text(28, H - 48, "Torn papyrus", fontproperties=HAND, fontsize=34, color=t["ink"], va="baseline")
    ax.text(28, H - 72, "Sappho fr. 16 (Voigt), as Grenfell and Hunt printed it in 1914:", fontproperties=BODY,
            fontsize=11.5, color=t["ink"])
    ax.text(28, H - 88, "P.Oxy. 1231 fragment 1, column i, lines 13-34 (redrawn, not a photograph)",
            fontproperties=BODY, fontsize=11.5, color=t["sub"])

    # legend
    ly = y_bot - 34
    ax.add_patch(Rectangle((28, ly - 4), 26, 18, facecolor=t["papyrus"], edgecolor="none"))
    ax.text(32, ly, "αβ", fontproperties=GREEK, fontsize=14, color=t["ink"])
    ax.text(62, ly, "ink: read on the papyrus by the 1914 editors", fontproperties=BODY, fontsize=10.5,
            color=t["ink"], va="baseline")
    ly -= 24
    ax.add_patch(Rectangle((28, ly - 4), 26, 18, facecolor=t["wash"], edgecolor=t["pencil"], linestyle=(0, (2, 2)),
                           linewidth=0.6))
    ax.text(30, ly, "[αβ]", fontproperties=GREEK, fontsize=12, color=t["accent"])
    ax.text(62, ly, "hole, filled by the editors: a guess, never Sappho's words",
            fontproperties=BODY, fontsize=10.5, color=t["ink"], va="baseline")
    ly -= 24
    ax.add_patch(Rectangle((28, ly - 4), 26, 18, facecolor=t["wash"], edgecolor="none"))
    ax.text(31, ly, "⟨α⟩", fontproperties=GREEK, fontsize=12, color=t["accent"])
    ax.text(62, ly, "a letter the scribe left out, added by the editors (not a hole)", fontproperties=BODY,
            fontsize=10.5, color=t["ink"], va="baseline")
    ly -= 24
    ax.add_patch(Rectangle((28, ly - 4), 26, 18, facecolor=t["bg"], edgecolor=t["pencil"], linestyle=(0, (2, 2)),
                           linewidth=0.6))
    ax.text(31, ly, ". . .", fontproperties=GREEK, fontsize=12, color=t["pencil"])
    ax.text(62, ly, "lost: one dot is about one letter; dots outside brackets are traces nobody could read",
            fontproperties=BODY, fontsize=10.5, color=t["ink"], va="baseline")
    L = pap["letters"]
    ax.text(28, ly - 26, "Letters in the 1914 text: %d read, %d restored in brackets, %d added, %d marked lost (dots)."
            % (L["read"], L["restored"], L["added"], L["lost_dots"]), fontproperties=BODY, fontsize=10.5, color=t["sub"])
    footer(ax, t, W, ["Greek: Grenfell & Hunt, The Oxyrhynchus Papyri X (1914), pp. 23, 25 (public domain);",
                      "modern editions read some lines differently."])
    save(fig, "papyrus", theme, "Torn papyrus: Sappho fr. 16 (Voigt) on P.Oxy. 1231",
         "Twenty-two lines of Greek from P.Oxy. 1231 fragment 1, column i, lines 13-34, redrawn as Grenfell and "
         "Hunt printed them in 1914. Letters read on the papyrus are in ink; letters the editors restored in "
         "square brackets sit in pale torn holes in red; letters the scribe left out are marked with angle "
         "brackets; lost letters are dots. Counts: %d read, %d restored, %d added, %d marked lost."
         % (L["read"], L["restored"], L["added"], L["lost_dots"]))


# ---------------------------------------------------------------------------------------------------------------
def _bracket_spans(text: str):
    """Split a Wharton line into (piece, uncertain?) by his square brackets."""
    out, buf, inside = [], "", False
    for ch in text:
        if ch == "[":
            if buf:
                out.append((buf, inside))
            buf, inside = "[", True
        elif ch == "]" and inside:
            out.append((buf + "]", True))
            buf, inside = "", False
        else:
            buf += ch
    if buf:
        out.append((buf, inside))
    return out


def fig_sappho31(data: dict, theme: str):
    t = THEMES[theme]
    s31 = data["sappho31"]
    lines = [g["text"] for g in s31["greek_lines"]]
    fs, lead, gap = 16.5, 24.0, 12.0
    W = 640.0
    H = 118 + lead * 20 + gap * 4 + 150
    fig, ax = page(W, H, t)
    x0 = 70.0
    y = H - 128
    pos = {}
    for st_i, stanza in enumerate(s31["stanzas"] + [[18, 19, 20]]):
        for n in stanza:
            indent = 34 if (n % 4 == 0) else 0
            pos[n] = (x0 + indent, y)
            y -= lead
        y -= gap
    for n, text in enumerate(lines, start=1):
        x, yy = pos[n]
        ax.text(x0 - 30, yy, str(n), ha="right", fontproperties=BODY, fontsize=9, color=t["pencil"])
        for piece, unc in _bracket_spans(text):
            ax.text(x, yy, piece, fontproperties=GREEK, fontsize=fs, color=t["accent"] if unc else t["ink"])
            x += width(piece, GREEK, fs)
        if n == 17:
            end_x = x
    # the pen stops: a blot, then the rest of stanza 5 as empty pencil rules
    _, y17 = pos[17]
    ax.plot([end_x + 6], [y17 + 5], marker="o", markersize=5.5, color=t["ink"])
    ax.annotate("the quotation in\nOn the Sublime ends here", xy=(end_x + 9, y17 + 5),
                xytext=(end_x + 24, y17 + 30), va="bottom", fontproperties=HAND, fontsize=19, color=t["second"],
                arrowprops=dict(arrowstyle="-", color=t["second"], lw=1.0, connectionstyle="arc3,rad=0.25"))
    for n in (18, 19, 20):
        x, yy = pos[n]
        wl = 300 if n < 20 else 90
        ax.plot([x, x + wl], [yy + 3, yy + 3], color=t["pencil"], lw=0.9, linestyle=(0, (1.5, 3)))
    _, y20 = pos[20]
    ax.text(x0, y20 - 26, "the rest of stanza 5, and anything after it: lost", fontproperties=BODY, fontsize=10.5,
            color=t["pencil"], style="italic")

    ax.text(28, H - 48, "A quotation that stops", fontproperties=HAND, fontsize=34, color=t["ink"])
    ax.text(28, H - 72, "Sappho 31 (Voigt) = Wharton 2, known only because the critic called 'Longinus'",
            fontproperties=BODY, fontsize=11.5, color=t["ink"])
    ax.text(28, H - 88, "quoted it in On the Sublime, chapter 10. Four stanzas and one line survive.",
            fontproperties=BODY, fontsize=11.5, color=t["ink"])
    ly = y20 - 58
    ax.text(28, ly, "[ ]", fontproperties=GREEK, fontsize=12, color=t["accent"])
    ax.text(52, ly, "Wharton's brackets: uncertain words; Bergk thought 'ἐπεὶ καὶ πένητα' may be the critic's own",
            fontproperties=BODY, fontsize=10, color=t["ink"])
    ax.text(52, ly - 15, "(Rhys Roberts 1899, Appendix A, pp. 172-173). Where the quotation stops: Rhys Roberts 1899, p. 70.",
            fontproperties=BODY, fontsize=10, color=t["ink"])
    footer(ax, t, W, ["Greek: H. T. Wharton, Sappho (1908), fr. 2, Project Gutenberg #57390 (public domain):",
                      "a 19th-century text after Bergk; modern editions differ in places."])
    save(fig, "stopped_quotation", theme, "A quotation that stops: Sappho 31 in On the Sublime",
         "The Greek of Sappho 31 (Wharton fr. 2) in four stanzas and one more line, as the critic called "
         "Longinus quoted it in On the Sublime, chapter 10. An ink blot marks where the quotation ends, after "
         "line 17; the rest of stanza 5 is drawn as empty dotted rules. Words Wharton put in square brackets "
         "are in red. Text: Wharton, Sappho (1908); cut point: Rhys Roberts (1899), p. 70.")


# ---------------------------------------------------------------------------------------------------------------
def fig_histogram(data: dict, theme: str):
    t = THEMES[theme]
    st = data["stats"]
    hist = {int(k): v for k, v in st["histogram"].items()}
    cap = 30
    xs = list(range(1, cap + 1))
    ys = [hist.get(x, 0) for x in xs]
    over = {k: v for k, v in hist.items() if k > cap}
    plt.rcParams.update({"font.family": BODY.get_name()})
    fig = plt.figure(figsize=(8.6, 6.4))
    fig.patch.set_facecolor(t["bg"])
    ax = fig.add_axes([0.1, 0.22, 0.86, 0.58])
    ax.set_facecolor(t["bg"])
    for x, y in zip(xs, ys):
        ax.bar(x, y, 0.8, color=t["accent"] if x <= 5 else t["pencil"],
               hatch=None if x <= 5 else "", edgecolor="none")
    xo = cap + 3
    ax.bar(xo, sum(over.values()), 1.6, color=t["ink"])
    ax.text(xo, sum(over.values()) + 0.4, "\n".join("fr. %s: %d" % (
        ", ".join(str(r["wharton_no"]) for r in data["wharton_fragments"]
                  if r["words"] == k and not (r["shares_entry_with"] and r["shares_entry_with"] < r["wharton_no"])),
        k) for k in sorted(over)), ha="center", va="bottom", fontsize=8.5, color=t["ink"], fontproperties=BODY)
    ax.axvline(st["median_words"], color=t["second"], lw=1.4, linestyle=(0, (4, 3)))
    ax.text(st["median_words"] + 0.4, max(ys) * 0.97, "median %g words" % st["median_words"], color=t["second"],
            fontproperties=BODY, fontsize=11, va="top")
    ax.set_xticks([1, 5, 10, 15, 20, 25, 30, xo])
    ax.set_xticklabels(["1", "5", "10", "15", "20", "25", "30", "> 30"])
    ax.set_xlabel("Greek words in the fragment (our count)", fontproperties=BODY, fontsize=12, color=t["ink"])
    ax.set_ylabel("fragments", fontproperties=BODY, fontsize=12, color=t["ink"])
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(t["pencil"])
    ax.tick_params(colors=t["ink"], labelsize=10.5)
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    fig.text(0.04, 0.93, "Fragments of a few words", fontproperties=HAND, fontsize=30, color=t["ink"])
    fig.text(0.04, 0.865, "%d of the %d fragments Wharton prints as Greek verse have 5 words or fewer (%.0f%%)."
             % (st["count_le_5"], st["n_entries_verse"], 100 * st["share_le_5"]), fontproperties=BODY,
             fontsize=11.5, color=t["ink"])
    fig.text(0.04, 0.83, "Red: 5 words or fewer. Only three pass 30: fr. 1 (Ode to Aphrodite), fr. 2 (Sappho 31), fr. 118 (an epigram).",
             fontproperties=BODY, fontsize=10.5, color=t["sub"])
    fig.text(0.5, 0.1, "Counted from H. T. Wharton, Sappho (1908), Project Gutenberg #57390 (fragment numbers after Bergk).",
             ha="center", fontproperties=BODY, fontsize=9, color=t["sub"])
    fig.text(0.5, 0.07, "Left out: %d numbers Wharton gives only as words inside another writer's prose, or with no Greek."
             % st["n_entries_inline_or_none"], ha="center", fontproperties=BODY, fontsize=9, color=t["sub"])
    fig.text(0.5, 0.035, LABEL, ha="center", fontproperties=BODY, fontsize=9, color=t["sub"], style="italic")
    save(fig, "fragment_lengths", theme, "Fragments of a few words: lengths of Sappho's fragments",
         "A histogram of the number of Greek words in each of the %d fragments Wharton (1908) prints as Greek "
         "verse. %d of them (%.0f%%) have 5 words or fewer, shown in red; the median is %g words. Only three "
         "have more than 30 words: fr. 1, fr. 2 and fr. 118."
         % (st["n_entries_verse"], st["count_le_5"], 100 * st["share_le_5"], st["median_words"]))


# ---------------------------------------------------------------------------------------------------------------
KIND_STYLE = {
    "metrician": ("accent", "o"),
    "grammarian or lexicon": ("second", "s"),
    "anthology or miscellany": ("ink", "D"),
    "critic or rhetorician": ("pencil", "^"),
    "scholiast or commentator": ("sub", "v"),
    "philosopher": ("sub", "h"),
    "other": ("pencil", "*"),
}


def fig_quoters(data: dict, theme: str, top: int = 12):
    t = THEMES[theme]
    net = data["quoters_network"]
    nodes = net["nodes_authors"][:top]
    rest = net["nodes_authors"][top:]
    fig = plt.figure(figsize=(8.6, 8.4))
    fig.patch.set_facecolor(t["bg"])
    ax = fig.add_axes([0.03, 0.1, 0.94, 0.74])
    ax.set_facecolor(t["bg"])
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(-1, top + 1.2)
    # fragment axis on the right: Wharton numbers 1..170, bottom to top
    fx = 8.6

    def fy(n):
        return (top + 0.5) - (n - 1) / 169 * (top + 0.2)

    ax.plot([fx, fx], [fy(1), fy(170)], color=t["pencil"], lw=1)
    for n in (1, 50, 100, 150, 170):
        ax.text(fx + 0.15, fy(n), "fr. %d" % n, va="center", fontproperties=BODY, fontsize=9, color=t["sub"])
    for i, nd in enumerate(nodes):
        y = top - i
        colour = t[KIND_STYLE[nd["kind"]][0]]
        marker = KIND_STYLE[nd["kind"]][1]
        ax.scatter([3.4], [y], s=30 + 9 * nd["n_fragments"], color=colour, marker=marker, zorder=3)
        ax.text(3.0, y, "%s  %d" % (nd["author"], nd["n_fragments"]), ha="right", va="center",
                fontproperties=BODY, fontsize=10.5, color=t["ink"])
        for n in nd["fragments"]:
            ax.plot([3.55, fx], [y, fy(n)], color=colour, lw=0.6, alpha=0.55, zorder=2)
    y = top - len(nodes)
    others = sum(n["n_fragments"] for n in rest)
    ax.text(3.0, y, "%d other writers  %d" % (len(rest), others), ha="right", va="center", fontproperties=BODY,
            fontsize=10.5, color=t["sub"])
    for nd in rest:
        for n in nd["fragments"]:
            ax.plot([3.55, fx], [y, fy(n)], color=t["pencil"], lw=0.4, alpha=0.35)
    # legend of kinds
    lx, ly = 0.2, -0.6
    for k, (c, m) in KIND_STYLE.items():
        ax.scatter([lx], [ly], s=35, color=t[c], marker=m)
        ax.text(lx + 0.15, ly, k, va="center", fontproperties=BODY, fontsize=8.5, color=t["ink"])
        lx += 1.45 if len(k) < 16 else 2.1
        if lx > 9:
            lx, ly = 0.2, ly - 0.45
    fig.text(0.04, 0.93, "Who saved Sappho", fontproperties=HAND, fontsize=30, color=t["ink"])
    fig.text(0.04, 0.885, "Later writers who quoted each fragment, as printed by Wharton, 1908 (first-named and others).",
             fontproperties=BODY, fontsize=10.5, color=t["ink"])
    fig.text(0.04, 0.86, "Not the modern count: modern editions add many papyrus fragments Wharton never saw.",
             fontproperties=BODY, fontsize=10, color=t["sub"])
    fig.text(0.5, 0.045, "Source notes: H. T. Wharton, Sappho (1908), Project Gutenberg #57390. Kinds are our rough grouping.",
             ha="center", fontproperties=BODY, fontsize=9, color=t["sub"])
    fig.text(0.5, 0.018, LABEL, ha="center", fontproperties=BODY, fontsize=9, color=t["sub"], style="italic")
    save(fig, "quoters", theme, "Who saved Sappho: the writers who quoted her",
         "Lines join each later Greek writer to the Sappho fragments he quotes, as printed by Wharton (1908), "
         "with the %d writers who quote most listed by name and count (%s) and %d other writers grouped. "
         "Marker shapes give the kind of writer: metrician, grammarian or lexicon, anthology, critic, "
         "scholiast, philosopher, other."
         % (len(nodes), ", ".join("%s %d" % (n["author"], n["n_fragments"]) for n in nodes[:3]) + ", ...",
            len(rest)))


def main():
    data = json.loads((RESULTS / "fragments.json").read_text(encoding="utf-8"))
    for theme in ("light", "dark"):
        fig_papyrus(data, theme)
        fig_sappho31(data, theme)
        fig_histogram(data, theme)
        fig_quoters(data, theme)


if __name__ == "__main__":
    main()
