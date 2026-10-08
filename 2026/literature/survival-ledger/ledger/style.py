"""Shared look for the Literature figures: warm paper, iron-gall ink, one accent.

Palette (shared by every Literature lane): paper #f3ece0, ink #2b2118, faded pencil #b9ad9a,
accent (editor's hand / survivors) #a8432a, second accent #3f6e8c. The dark theme swaps paper and ink and
lightens the accents so they keep their contrast. Ink vs pencil vs accent differ in lightness as well as hue,
and every encoding also uses shape (filled vs open), so the figures read without colour.
"""
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

LABEL = "Educational demos made to show an open-source tool. Not research."

THEMES = {
    "light": {"paper": "#f3ece0", "ink": "#2b2118", "pencil": "#b9ad9a", "accent": "#a8432a", "accent2": "#3f6e8c",
              "muted": "#6b5e4e"},
    "dark": {"paper": "#1e1914", "ink": "#efe6d6", "pencil": "#6e6354", "accent": "#e07a5c", "accent2": "#86b3d1",
             "muted": "#b3a690"},
}

# Fonts (SIL OFL 1.1) live in ../fonts/ (Literata, EB Garamond, Caveat); if missing, the figures fall back to a serif.
FONT_DIRS = [Path(__file__).resolve().parents[1] / "fonts"]
_loaded = False


def setup_fonts():
    global _loaded
    if _loaded:
        return
    for d in FONT_DIRS:
        if d.is_dir():
            for f in sorted(d.glob("*.ttf")):
                font_manager.fontManager.addfont(str(f))
    _loaded = True


def body_font():
    setup_fonts()
    names = {f.name for f in font_manager.fontManager.ttflist}
    return "Literata" if "Literata" in names else "serif"


def hand_font():
    setup_fonts()
    names = {f.name for f in font_manager.fontManager.ttflist}
    return "Caveat" if "Caveat" in names else body_font()


def apply(theme):
    t = THEMES[theme]
    plt.rcParams.update({
        "font.family": body_font(),
        "font.size": 13,
        "figure.facecolor": t["paper"],
        "axes.facecolor": t["paper"],
        "savefig.facecolor": t["paper"],
        "text.color": t["ink"],
        "axes.labelcolor": t["ink"],
        "axes.edgecolor": t["ink"],
        "xtick.color": t["ink"],
        "ytick.color": t["ink"],
        "svg.fonttype": "path",
        "svg.hashsalt": "nobel-2026-literature",
    })
    return t


def footer(fig, t, extra=""):
    text = LABEL + ("  " + extra if extra else "")
    fig.text(0.01, 0.012, text, fontsize=9.5, color=t["muted"], ha="left", va="bottom")


def save(fig, outdir, stem, theme, svg=True, title=None, desc=None):
    """Write PNG (+ SVG). The SVG gets role="img", a <title> and a <desc> for screen readers."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    paths = [outdir / f"{stem}_{theme}.png"]
    fig.savefig(paths[0], dpi=150, metadata={"Software": None})
    if svg:
        p = outdir / f"{stem}_{theme}.svg"
        fig.savefig(p, metadata={"Date": None, "Creator": None})
        _label_svg(p, title or stem.replace("_", " "), (desc or "") + " " + LABEL)
        paths.append(p)
    plt.close(fig)
    return paths


def _label_svg(path, title, desc):
    from xml.sax.saxutils import escape
    text = path.read_text(encoding="utf-8")
    m = re.search(r"<svg\b[^>]*>", text)
    tag = m.group(0)
    new_tag = tag if 'role="img"' in tag else tag[:-1] + ' role="img">'
    meta = f"\n <title>{escape(title)}</title>\n <desc>{escape(desc.strip())}</desc>"
    text = text[:m.start()] + new_tag + meta + text[m.end():]
    path.write_text(text, encoding="utf-8")
