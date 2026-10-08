"""Figures: warm paper, iron-gall ink, one accent (palette shared by every Literature lane).

Encodings never rely on colour alone: a carried word is a filled dot (close) or an open dot with a dashed thread
(loose); a dropped word is a short pencil gap in its thread; added words are listed in the accent colour after a "+".
Every figure carries the lab label and its sources. Greek is set in GFS Didot, English and Latin in Literata
(both SIL OFL 1.1, in data/fonts/).
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
RES = HERE / "results"
FONTS = HERE / "data" / "fonts"
LABEL = "Educational demos made to show an open-source tool. Not research."
COUNT_LABEL = "our rough count, not a quality score"

THEMES = {
    "light": {"paper": "#f3ece0", "ink": "#2b2118", "pencil": "#b9ad9a", "accent": "#a8432a", "accent2": "#3f6e8c",
              "muted": "#6b5e4e"},
    "dark": {"paper": "#1e1914", "ink": "#efe6d6", "pencil": "#6e6354", "accent": "#e07a5c", "accent2": "#86b3d1",
             "muted": "#b3a690"},
}
SHORT = {"catullus": "Catullus", "philips": "Philips", "smollett": "Smollett", "merivale": "Merivale",
         "symonds": "Symonds", "wharton": "Wharton"}
DATE = {"catullus": "1st c. BC", "philips": "1711", "smollett": "1748", "merivale": "1833", "symonds": "1883",
        "wharton": "1885/1908"}
LANG = {"catullus": "Latin verse", "philips": "English verse", "smollett": "English verse", "merivale": "English verse",
        "symonds": "English verse", "wharton": "English prose"}

_fonts = False


def _setup():
    global _fonts
    if not _fonts:
        for f in sorted(FONTS.glob("*.ttf")):
            font_manager.fontManager.addfont(str(f))
        _fonts = True


def GREEK():
    _setup()
    return {"family": "GFS Didot"}


def BODY():
    _setup()
    return {"family": "Literata"}


def _fig(w_px, h_px, theme):
    t = THEMES[theme]
    fig = plt.figure(figsize=(w_px / 100, h_px / 100), dpi=100)
    fig.patch.set_facecolor(t["paper"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_px)
    ax.set_ylim(h_px, 0)
    ax.axis("off")
    ax.set_facecolor(t["paper"])
    return fig, ax


def _save(fig, name, theme, title, desc, svg=True):
    """PNG (+ SVG). The SVG gets role="img", a <title> and a <desc> for screen readers (and the lab label)."""
    RES.mkdir(exist_ok=True)
    fig.savefig(RES / f"{name}_{theme}.png", dpi=100, facecolor=fig.get_facecolor())
    if svg:
        plt.rcParams["svg.hashsalt"] = "translators"  # stable ids: the SVGs rebuild byte-identical
        p = RES / f"{name}_{theme}.svg"
        fig.savefig(p, facecolor=fig.get_facecolor(), metadata={"Date": None})
        _label_svg(p, title, desc + " " + LABEL)
    plt.close(fig)


def _label_svg(path, title, desc):
    import re
    from xml.sax.saxutils import escape
    text = path.read_text(encoding="utf-8")
    m = re.search(r"<svg\b[^>]*>", text)
    tag = m.group(0)
    new_tag = tag if 'role="img"' in tag else tag[:-1] + ' role="img">'
    meta = f"\n <title>{escape(title)}</title>\n <desc>{escape(desc.strip())}</desc>"
    path.write_text(text[:m.start()] + new_tag + meta + text[m.end():], encoding="utf-8")


def _words(version, ids):
    by = {t["id"]: t for t in version["tokens"]}
    order = {t["id"]: i for i, t in enumerate(version["tokens"])}
    return " ".join(by[i]["word"] for i in sorted(ids, key=order.get))


# --------------------------------------------------------------------------------------------------------------
# 1. Threads: each Greek word's thread runs down a timeline of versions
# --------------------------------------------------------------------------------------------------------------
def threads(V, A, C, theme, greek_lines, name, w, h, fs):
    t = THEMES[theme]
    fig, ax = _fig(w, h, theme)
    gtoks = [g for g in V["greek"]["tokens"] if g["line"] in greek_lines]
    gloss = {g["id"]: g.get("gloss", {}) for g in A["greek_tokens"]}
    vers = V["versions"]
    stanza_of_scope = sorted({g["stanza"] for g in gtoks})
    left, right = fs["left"], w - fs["right"]
    colw = (right - left) / len(gtoks)
    top = fs["top"]
    row0 = top + fs["head"]
    rowh = (h - row0 - fs["foot"]) / len(vers)

    ax.text(fs["pad"], fs["pad"], fs["title"], fontsize=fs["t"], color=t["ink"], va="top", **BODY())
    ax.text(fs["pad"], fs["pad"] + fs["t"] * 1.9, fs["subtitle"], fontsize=fs["s"], color=t["muted"], va="top", **BODY())

    # Greek words and their LSJ gloss
    xs = {}
    for i, g in enumerate(gtoks):
        x = left + colw * (i + 0.5)
        xs[g["id"]] = x
        dy = fs["stagger"] * (i % 2)
        ax.text(x, top + dy, g["word"], ha="center", va="center", fontsize=fs["g"], color=t["ink"], **GREEK())
        gl = gloss[g["id"]].get("gloss", "")
        ax.text(x, top + dy + fs["g"] * 0.9, "\n".join(textwrap.wrap(gl, fs["wrap"])[:2]), ha="center", va="top",
                fontsize=fs["gl"], color=t["muted"], style="italic", **BODY())

    # timeline rule on the left with a break between Catullus and Philips
    xr = fs["rule_x"]
    ys = [row0 + rowh * (k + 0.5) for k in range(len(vers))]
    ax.plot([xr, xr], [ys[0], ys[0] + rowh * 0.42], color=t["ink"], lw=1.6)
    ax.plot([xr, xr], [ys[1] - rowh * 0.42, ys[-1]], color=t["ink"], lw=1.6)
    yb = (ys[0] + ys[1]) / 2
    for d in (-6, 6):
        ax.plot([xr - 9, xr + 9], [yb + d - 4, yb + d + 4], color=t["ink"], lw=1.4)
    ax.text(xr + 14, yb, "about 1,750 years (rows not to scale)", fontsize=fs["gl"], color=t["muted"], va="center",
            style="italic", **BODY())

    for k, v in enumerate(vers):
        y = ys[k]
        ax.plot([xr - 7, xr + 7], [y, y], color=t["ink"], lw=1.6)
        ax.text(xr - 14, y - fs["lab"] * 0.7, SHORT[v["id"]], ha="right", va="center", fontsize=fs["lab"], color=t["ink"], **BODY())
        ax.text(xr - 14, y + fs["lab"] * 0.75, DATE[v["id"]], ha="right", va="center", fontsize=fs["lab"] * 0.85,
                color=t["muted"], **BODY())
        ax.text(xr - 14, y + fs["lab"] * 1.9, LANG[v["id"]], ha="right", va="center", fontsize=fs["gl"],
                color=t["muted"], style="italic", **BODY())
        L = A["links"][v["id"]]
        present = {ln["stanza"] for ln in v["lines"] if ln.get("text")}
        carried = 0
        for gi, g in enumerate(gtoks):
            x = xs[g["id"]]
            if g["stanza"] not in present:
                continue
            link = L.get(g["id"])
            if link:
                carried += 1
                close = link["strength"] == "close"
                col = t["ink"] if close else t["accent2"]
                ax.plot([x], [y], marker="o", ms=fs["dot"], mfc=col if close else t["paper"], mec=col, mew=1.8, zorder=3)
                txt = _words(v, link["to"])
                ax.text(x, y + fs["dot"] * 0.9 + fs["wstagger"] * (gi % 2), "\n".join(textwrap.wrap(txt, fs["wrap"])[:3]), ha="center", va="top",
                        fontsize=fs["w"], color=col, style="normal" if close else "italic", **BODY())
            else:
                ax.plot([x - 6, x + 6], [y, y], color=t["pencil"], lw=1.4)
        # added words in this version's lines for the stanzas shown
        lines_here = {ln["n"] for ln in v["lines"] if ln.get("stanza") in stanza_of_scope and ln.get("text")}
        linked = {tid for lk in L.values() for tid in lk["to"]}
        added = [tk["word"] for tk in v["tokens"] if tk["line"] in lines_here and tk["id"] not in linked]
        n_scope = sum(1 for g in gtoks if g["stanza"] in present)
        if fs.get("nocounts"):
            continue
        ax.text(right + 16, y - fs["w"] * 0.9, f"carried {carried}/{n_scope}", fontsize=fs["w"], color=t["ink"], va="center", **BODY())
        add_txt = "+ " + " ".join(added) if added else "+ none"
        ax.text(right + 16, y + fs["w"] * 0.5, "\n".join(textwrap.wrap(add_txt, fs["addwrap"])[:fs["addlines"]])
                + ("…" if len(textwrap.wrap(add_txt, fs["addwrap"])) > fs["addlines"] else ""),
                fontsize=fs["w"] * 0.92, color=t["accent"], va="top", **BODY())
        ax.text(right + 16, y + fs["w"] * 0.5 + fs["w"] * 1.45 * min(fs["addlines"], len(textwrap.wrap(add_txt, fs["addwrap"]))) + 4,
                f"added {len(added)}", fontsize=fs["w"] * 0.85, color=t["accent"], va="top", style="italic", **BODY())

    # threads: faint vertical pencil line per Greek word, inked between consecutive rows that both carry it
    for g in gtoks:
        x = xs[g["id"]]
        ax.plot([x, x], [top + fs["stagger"] + fs["g"] * 0.9 + fs["gl"] * 2.8, ys[-1]], color=t["pencil"], lw=0.8, zorder=1, alpha=0.7)

    # legend + footer
    yl = h - fs["foot"] + 18
    ax.plot([fs["pad"] + 8], [yl], marker="o", ms=fs["dot"], mfc=t["ink"], mec=t["ink"])
    ax.text(fs["pad"] + 24, yl, "carried, close sense", fontsize=fs["gl"] * 1.1, color=t["ink"], va="center", **BODY())
    x2 = fs["pad"] + fs["leg2"]
    ax.plot([x2], [yl], marker="o", ms=fs["dot"], mfc=t["paper"], mec=t["accent2"], mew=1.8)
    ax.text(x2 + 16, yl, "carried, loose (sense shifted)", fontsize=fs["gl"] * 1.1, color=t["accent2"], va="center", style="italic", **BODY())
    x3 = x2 + fs["leg3"]
    if x3 > w:
        x3, yl = fs["pad"] + 8, yl + 34
    ax.plot([x3 - 6, x3 + 6], [yl, yl], color=t["pencil"], lw=1.4)
    ax.text(x3 + 16, yl, "no counterpart (dropped)", fontsize=fs["gl"] * 1.1, color=t["muted"], va="center", **BODY())
    x4 = x3 + fs["leg4"]
    if not fs.get("nocounts"):
        ax.text(x4, yl, "+ words with no Greek counterpart (added)", fontsize=fs["gl"] * 1.1, color=t["accent"], va="center", **BODY())
    for i, line in enumerate(fs["footer"]):
        ax.text(fs["pad"], yl + 30 + i * fs["gl"] * 1.6, line, fontsize=fs["gl"], color=t["muted"], va="top", **BODY())
    _save(fig, name, theme, fs["title"], fs["desc"])


FOOT_SRC = ("Greek: Sappho fr. 2 (Voigt 31) as printed by H. T. Wharton, Sappho, 5th ed. 1908 (Project Gutenberg #57390), "
            "Bergk's text. Versions: as printed in the same book. Glosses: LSJ, Perseus Digital Library, CC BY-SA 4.0.")


def make_threads(V, A, C, theme):
    threads(V, A, C, theme, range(1, 5), "threads_stanza1", 1920, 1240, {
        "title": "One stanza, six versions: where each Greek word went",
        "desc": "The 16 Greek words of the first stanza of Sappho 31 (Wharton fr. 2) across the top; below them one "
                "row per version, oldest first: Catullus (Latin, 1st century BC), Ambrose Philips 1711, Tobias "
                "Smollett 1748, J. H. Merivale 1833, J. A. Symonds 1883 and H. T. Wharton's prose 1885. A thread "
                "runs down from each Greek word; a filled dot marks a close counterpart, an open dot with a dashed "
                "thread a loose one, a gap a dropped word; words with no Greek counterpart are listed after a plus "
                f"sign. Counts are {COUNT_LABEL}.",
        "subtitle": "Sappho's first stanza (Greek, top) and its counterpart words in each version, oldest first. "
                    f"Counts are {COUNT_LABEL}.",
        "left": 215, "right": 300, "top": 150, "head": 122, "foot": 120, "pad": 30, "t": 30, "s": 15, "g": 23,
        "gl": 11, "w": 13, "lab": 17, "dot": 9, "wrap": 13, "addwrap": 32, "addlines": 3, "rule_x": 190,
        "stagger": 68, "wstagger": 22,
        "leg2": 230, "leg3": 330, "leg4": 270,
        "footer": [LABEL + "  The Greek is Wharton's 19th-century text. 'Carried' means our hand alignment found a counterpart; "
                   "it says nothing about which version is better.", FOOT_SRC],
    })
    threads(V, A, C, theme, range(1, 2), "threads_line1", 1080, 1500, {
        "title": "The first line, six ways",
        "desc": "The Greek words of the first line of Sappho 31 (Wharton fr. 2) and their counterparts in six "
                "versions, oldest first (Catullus, Philips 1711, Smollett 1748, Merivale 1833, Symonds 1883, "
                "Wharton 1885), showing who kept 'seems' and 'to me'. Filled dots are close counterparts, open "
                "dots loose ones, gaps dropped words.",
        "subtitle": f"Who kept 'seems' and 'to me'?  ({COUNT_LABEL})",
        "left": 250, "right": 30, "top": 190, "head": 90, "foot": 230, "pad": 36, "t": 38, "s": 21, "g": 34,
        "gl": 15, "w": 19, "lab": 22, "dot": 12, "wrap": 12, "addwrap": 30, "addlines": 0, "rule_x": 220,
        "stagger": 0, "wstagger": 0,
        "leg2": 300, "leg3": 10_000, "leg4": 10_000, "nocounts": True,
        "footer": [LABEL, "Greek: Wharton, Sappho (1908), Project Gutenberg #57390.",
                   "Versions as printed by Wharton. Glosses: LSJ via Perseus, CC BY-SA 4.0."],
    })


# --------------------------------------------------------------------------------------------------------------
# 2. Counts (whole poem, lines 1-16)
# --------------------------------------------------------------------------------------------------------------
def make_counts(V, C, theme):
    t = THEMES[theme]
    plt.rcParams.update({"font.family": BODY()["family"], "font.size": 15})
    fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
    fig.patch.set_facecolor(t["paper"])
    order = [v["id"] for v in V["versions"]]
    rows = [C["versions"][i] for i in order]
    ax1 = fig.add_axes([0.25, 0.47, 0.68, 0.36])
    ax2 = fig.add_axes([0.25, 0.12, 0.68, 0.26])
    for ax in (ax1, ax2):
        ax.set_facecolor(t["paper"])
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(t["pencil"])
        ax.tick_params(colors=t["muted"], labelsize=14)
        ax.invert_yaxis()
    labels = [f"{SHORT[i]}  {DATE[i]}" for i in order]
    y = range(len(rows))
    cl = [r["carried_close"] for r in rows]
    lo = [r["carried_loose"] for r in rows]
    dr = [r["greek_words_dropped"] for r in rows]
    ax1.barh(y, cl, color=t["ink"], height=0.62, edgecolor=t["paper"], linewidth=2)
    ax1.barh(y, lo, left=cl, color=t["accent2"], height=0.62, edgecolor=t["paper"], linewidth=2, hatch="//")
    ax1.barh(y, dr, left=[a + b for a, b in zip(cl, lo)], color=t["paper"], height=0.62, edgecolor=t["pencil"], linewidth=1.5)
    for k, r in enumerate(rows):
        ax1.text(r["greek_words_in_scope"] + 1, k, f"{r['greek_words_carried']} of {r['greek_words_in_scope']} carried",
                 va="center", fontsize=13, color=t["ink"])
    ax1.set_yticks(list(y), labels, fontsize=15, color=t["ink"])
    ax1.set_xlim(0, 95)
    ax1.set_xlabel("Greek words (lines 1-16; Catullus as quoted by Wharton: lines 1-12)", color=t["muted"], fontsize=13)
    ax1.set_title("Greek words with a counterpart", loc="left", color=t["ink"], fontsize=18, pad=12)
    ax2.barh(y, [r["words_added"] for r in rows], color=t["accent"], height=0.62)
    for k, r in enumerate(rows):
        ax2.text(r["words_added"] + 1, k, f"{r['words_added']} of {r['version_words']} words", va="center", fontsize=13, color=t["ink"])
    ax2.set_yticks(list(y), labels, fontsize=15, color=t["ink"])
    ax2.set_xlim(0, 110)
    ax2.set_xlabel("words in the version with no Greek counterpart", color=t["muted"], fontsize=13)
    ax2.set_title("Words added", loc="left", color=t["ink"], fontsize=18, pad=12)
    fig.text(0.04, 0.965, "Sappho 31 in six versions: our rough count", fontsize=26, color=t["ink"], va="top")
    fig.text(0.04, 0.925, f"{COUNT_LABEL.capitalize()}. Solid = close sense, hatched = loose, open = dropped.",
             fontsize=14, color=t["muted"], va="top")
    fig.text(0.04, 0.9, "Prose, rhyme and metre need different numbers of words; no ranking is implied.",
             fontsize=14, color=t["muted"], va="top")
    fig.text(0.04, 0.05, LABEL, fontsize=12, color=t["muted"])
    fig.text(0.04, 0.03, "Texts: Wharton, Sappho (1908), Project Gutenberg #57390. Alignment and counts: ours, by hand (README).",
             fontsize=12, color=t["muted"])
    _save(fig, "counts", theme, "Sappho 31 in six versions: our rough count",
          "Two bar charts over the six versions, oldest first. Top: of the Greek words of lines 1-16, how many "
          "have a close counterpart, a loose one, or none (" + "; ".join(
              f"{SHORT[i]} {C['versions'][i]['greek_words_carried']} of {C['versions'][i]['greek_words_in_scope']}"
              for i in order) + "). Bottom: words in each version with no Greek counterpart (" + "; ".join(
              f"{SHORT[i]} {C['versions'][i]['words_added']} of {C['versions'][i]['version_words']}" for i in order)
          + f"). {COUNT_LABEL.capitalize()}; prose, rhyme and metre need different numbers of words.")


# --------------------------------------------------------------------------------------------------------------
# 3. γλυκύπικρον split
# --------------------------------------------------------------------------------------------------------------
def make_glukupikron(V, theme, glossdata):
    t = THEMES[theme]
    w, h = 1080, 1350
    fig, ax = _fig(w, h, theme)
    fr = V["fr40"]
    word = "γλυκύπικρον"
    line2 = fr["greek_lines"][1]["text"]
    assert word in line2
    a, b = word[:5], word[5:]   # γλυκύ | πικρον
    ax.text(w / 2, 90, "One word, two tastes", ha="center", fontsize=40, color=t["ink"], **BODY())
    ax.text(w / 2, 145, "Sappho, Wharton fr. 40 (Voigt 130), line 2:", ha="center", fontsize=18, color=t["muted"], **BODY())
    ax.text(w / 2, 190, line2, ha="center", fontsize=26, color=t["muted"], **GREEK())
    ax.text(w / 2 - 6, 300, a, ha="right", fontsize=64, color=t["ink"], **GREEK())
    ax.text(w / 2 + 6, 300, b, ha="left", fontsize=64, color=t["accent"], **GREEK())
    ax.plot([w / 2, w / 2], [230, 320], color=t["pencil"], lw=1.2, ls=(0, (4, 4)))
    xa, xb = 300, 780
    ax.text(xa, 400, glossdata["sweet"]["lemma"], ha="center", fontsize=34, color=t["ink"], **GREEK())
    ax.text(xa, 445, f"“{glossdata['sweet']['gloss']}”", ha="center", fontsize=19, color=t["ink"], style="italic", **BODY())
    ax.text(xb, 400, glossdata["bitter"]["lemma"], ha="center", fontsize=34, color=t["accent"], **GREEK())
    ax.text(xb, 445, f"“{glossdata['bitter']['gloss']}”", ha="center", fontsize=19, color=t["accent"], style="italic", **BODY())
    ax.plot([w / 2 - 120, xa], [320, 370], color=t["ink"], lw=1.4)
    ax.plot([w / 2 + 120, xb], [320, 370], color=t["accent"], lw=1.4)
    ax.text(w / 2, 478, "LSJ (Perseus, CC BY-SA 4.0): headwords and glosses", ha="center", fontsize=13, color=t["muted"], **BODY())

    # each rendering: the 'sweet' half in ink, the 'bitter' half in the accent, with the Greek half named under it
    rows = [
        ("Symonds, 1883", ("bitter-", "sweet"), "bitter first: order reversed", fr["symonds"]["lines"][1]["text"]),
        ("Wharton, 1885/1908", ("bitter-", "sweet"), "bitter first: order reversed", fr["wharton_prose"]["text"]),
        ("LSJ, 1940", ("sweetly", "bitter"), "sweet first, as in the Greek", None),
    ]
    y = 580
    cx = w / 2 + 60
    for who, (left_w, right_w), how, ctx in rows:
        bitter_first = left_w.startswith("bitter")
        ax.text(70, y, who, fontsize=20, color=t["muted"], va="center", **BODY())
        ax.text(cx, y, left_w, ha="right", fontsize=40, va="center", color=t["accent"] if bitter_first else t["ink"], **BODY())
        ax.text(cx + (0 if bitter_first else 14), y, right_w, ha="left", fontsize=40, va="center",
                color=t["ink"] if bitter_first else t["accent"], **BODY())
        ax.text(cx - 70, y + 36, b if bitter_first else a, ha="center", fontsize=17, va="top",
                color=t["accent"] if bitter_first else t["ink"], **GREEK())
        ax.text(cx + 75, y + 36, a if bitter_first else b, ha="center", fontsize=17, va="top",
                color=t["ink"] if bitter_first else t["accent"], **GREEK())
        ax.text(70, y + 30, how, fontsize=14, color=t["muted"], va="top", style="italic", **BODY())
        if ctx:
            ax.text(cx, y + 72, "\u201c" + ctx + "\u201d", ha="center", fontsize=15, color=t["muted"], va="top", style="italic", **BODY())
        y += 170
    ax.text(w / 2, y + 10, "Wharton and Symonds both write \u201cbitter-sweet\u201d: the same two halves, order reversed.",
            ha="center", fontsize=18, color=t["ink"], **BODY())
    ax.text(w / 2, y + 80, "Nobel Committee for Literature, 2026, on her essay Eros the Bittersweet (1986):",
            ha="center", fontsize=17, color=t["ink"], **BODY())
    ax.text(w / 2, y + 115, "the book \u201cdraws heavily on a compound adjective from Sappho\u201d", ha="center", fontsize=19,
            color=t["accent"], style="italic", **BODY())
    ax.text(w / 2, y + 147, "(the Committee does not name the word)", ha="center", fontsize=14, color=t["muted"], **BODY())
    ax.text(40, h - 70, LABEL, fontsize=13, color=t["muted"], **BODY())
    ax.text(40, h - 45, "Greek and English: Wharton, Sappho, 5th ed. 1908 (Project Gutenberg #57390), p. 96. "
            "Committee: nobelprize.org bio-bibliography.", fontsize=11, color=t["muted"], **BODY())
    _save(fig, "glukupikron", theme, "One word, two tastes: the Greek compound for bitter-sweet",
          f"Sappho's compound adjective {word} (Wharton fr. 40, Voigt 130) split into its two halves, "
          f"{glossdata['sweet']['lemma']} 'sweet' and {glossdata['bitter']['lemma']} "
          f"'{glossdata['bitter']['gloss']}' (LSJ). Below, Wharton's prose and Symonds' verse both write "
          "'bitter-sweet', the halves in reverse order, and the Nobel Committee's sentence that her essay Eros "
          "the Bittersweet draws on a compound adjective from Sappho (the Committee does not name the word).")


def make_all(V, A, C):
    import json
    from . import lsj
    from .lsj import beta_to_unicode
    G = json.loads((HERE / "data" / "glosses.json").read_text(encoding="utf-8"))["glosses"]
    gd = {"sweet": {"lemma": beta_to_unicode("gluku/s"), "gloss": "sweet"},
          "bitter": {"lemma": beta_to_unicode("pikro/s"), "gloss": G["pikro/s"]["gloss"]},
          "compound": {"lemma": beta_to_unicode("gluku/pikros"), "gloss": G["gluku/pikros"]["gloss"]}}
    st = lsj.load()["entries"]
    assert lsj.has_phrase(st["gluku/s"], "sweet") and lsj.has_phrase(st["pikro/s"], gd["bitter"]["gloss"])
    for theme in ("light", "dark"):
        make_threads(V, A, C, theme)
        make_counts(V, C, theme)
        make_glukupikron(V, theme, gd)
