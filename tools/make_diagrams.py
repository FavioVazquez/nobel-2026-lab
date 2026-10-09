#!/usr/bin/env python3
"""Generate the README art and diagrams for nobel-2026-lab (dark and light variants).

Run from anywhere:  python3 tools/make_diagrams.py
Writes SVG files into assets/ (stdlib only, no network). Every picture has a <title>
and <desc> (alt text), opaque panels so it reads on any page background, and a
prefers-reduced-motion guard for the few animated parts.
"""
from __future__ import annotations

import html
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

FONT = 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'

THEMES = {
    "dark": dict(
        bg="#0B1220", bg2="#111C36", panel="#121C32", border="#2A3B61", text="#EAF0FA",
        muted="#A3B4D2", blue="#58A9FF", violet="#B2A5FF", amber="#FFB84D", teal="#45DDB7",
        coral="#FF8F7A", rail="#2D3F66", membrane="#2B3B5F", membrane_edge="#5873AC",
        protein="#9482F2", tissue1="#16253F", tissue2="#0E1830", dots="#7F95C4",
        fibre="#8FA2C6", pill="#1A2A4D", pill_text="#CFE0FF", cone="#58A9FF",
        ice1="#162B4A", ice2="#0F1E38", ice_top="#24406A", ice_edge="#5677B0",
        earth="#3A3328", earth_edge="#9C8662", sensor_off="#6F84AE",
    ),
    "light": dict(
        bg="#F4F7FC", bg2="#E6EEFA", panel="#FFFFFF", border="#C6D3EA", text="#14213D",
        muted="#44557A", blue="#1A62D3", violet="#5A45C4", amber="#A85900", teal="#07785F",
        coral="#C23A22", rail="#C1CEE6", membrane="#DCE5F5", membrane_edge="#98ACD4",
        protein="#7A66E0", tissue1="#E3ECFA", tissue2="#D1DEF4", dots="#7C90B8",
        fibre="#7186AD", pill="#DCE8FB", pill_text="#17356E", cone="#2A74E8",
        ice1="#E9F2FD", ice2="#D2E2F6", ice_top="#F8FBFF", ice_edge="#93AFD8",
        earth="#EDE3D2", earth_edge="#A88D60", sensor_off="#8597BC",
    ),
}


def esc(s: str) -> str:
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- text helpers
def tw(s: str, size: float, bold: bool = False) -> float:
    """Rough text width for a Helvetica/Arial-like font, padded for wider UI fonts."""
    w = 0.0
    for ch in s:
        if ch in "il.,;:'|!":
            w += 0.26
        elif ch in "jtfr()[]-/":
            w += 0.34
        elif ch == " ":
            w += 0.29
        elif ch in "mwMW":
            w += 0.84
        elif ch.isupper():
            w += 0.69
        elif ch.isdigit():
            w += 0.57
        else:
            w += 0.55
    return w * size * (1.08 if bold else 1.0) * 1.10


def wrap(s: str, size: float, maxw: float, bold: bool = False) -> list[str]:
    out, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if tw(trial, size, bold) <= maxw or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def text(x, y, s, size, fill, weight=400, anchor="start", extra="", fit=None):
    """fit: exact rendered width in px; keeps the layout identical whatever font the viewer has."""
    if fit:
        extra += f' textLength="{fit:g}" lengthAdjust="spacingAndGlyphs"'
    return (f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" {extra}>{esc(s)}</text>')


def para(x, y, lines, size, fill, lh, weight=400):
    return "\n".join(text(x, y + i * lh, ln, size, fill, weight) for i, ln in enumerate(lines))


def svg_open(w, h, title, desc, T, extra_style=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="t d">\n'
        f'<title id="t">{esc(title)}</title>\n<desc id="d">{esc(desc)}</desc>\n'
        f'<style>{extra_style}@media (prefers-reduced-motion: reduce){{*{{animation:none!important;'
        f'transition:none!important}}}}</style>\n'
        f'<g font-family=\'{FONT}\'>\n'
    )


SVG_CLOSE = "</g>\n</svg>\n"


def bg_rect(w, h, T, r=28):
    return (f'<rect width="{w}" height="{h}" rx="{r}" fill="{T["bg"]}"/>'
            f'<rect x="1.5" y="1.5" width="{w-3}" height="{h-3}" rx="{r-1}" fill="none" '
            f'stroke="{T["border"]}" stroke-width="3"/>')


# ---------------------------------------------------------------- hero
# One card per prize, side by side, and a quiet dashed slot for the prize still to come.
# Colours only the banner uses live here, so the shared THEMES table stays as the diagrams use it.
HERO_EXTRA = {
    "dark": dict(ice1="#13284A", ice2="#091629", ice_top="#26446F", sensor_off="#5D7299",
                 neuron="#B9AEFF", next_fill="#0F1A30"),
    "light": dict(ice1="#E4EEFB", ice2="#C9DAF1", ice_top="#F8FBFF", sensor_off="#8293B6",
                  neuron="#5A45C4", next_fill="#FFFFFF"),
}
CARD_W, CARD_H, WIN_H, NEXT_W, CARD_GAP = 290, 432, 308, 160, 20


def _hero_defs(T: dict, X: dict) -> str:
    return (
        f'<defs>'
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T["bg"]}"/>'
        f'<stop offset="1" stop-color="{T["bg2"]}"/></linearGradient>'
        f'<pattern id="dots" width="32" height="32" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1.6" fill="{T["dots"]}" fill-opacity=".28"/></pattern>'
        f'<linearGradient id="tis" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T["tissue1"]}"/>'
        f'<stop offset="1" stop-color="{T["tissue2"]}"/></linearGradient>'
        f'<linearGradient id="ice" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{X["ice1"]}"/>'
        f'<stop offset="1" stop-color="{X["ice2"]}"/></linearGradient>'
        f'<linearGradient id="cone" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{T["cone"]}" stop-opacity=".8"/>'
        f'<stop offset="1" stop-color="{T["cone"]}" stop-opacity="0"/></linearGradient>'
        f'<radialGradient id="glow" cx="0.5" cy="0" r="1"><stop offset="0" stop-color="{T["cone"]}" stop-opacity=".6"/>'
        f'<stop offset=".45" stop-color="{T["cone"]}" stop-opacity=".16"/>'
        f'<stop offset="1" stop-color="{T["cone"]}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{T["cone"]}" stop-opacity=".75"/>'
        f'<stop offset="1" stop-color="{T["cone"]}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="spark" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".9"/>'
        f'<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="cardclip"><rect width="{CARD_W}" height="{CARD_H}" rx="22"/></clipPath>'
        f'</defs>'
    )


def _hero_caption(T: dict, kicker: str, col: str, lines: tuple[str, str]) -> str:
    s = (f'<rect y="{WIN_H}" width="{CARD_W}" height="{CARD_H - WIN_H}" fill="{T["panel"]}" clip-path="url(#cardclip)"/>'
         f'<line x1="0" y1="{WIN_H}" x2="{CARD_W}" y2="{WIN_H}" stroke="{T["border"]}" stroke-width="2"/>')
    s += text(26, WIN_H + 42, kicker, 19, col, 800, extra='letter-spacing="3"')
    s += text(26, WIN_H + 76, lines[0], 25, T["text"], 700)
    s += text(26, WIN_H + 107, lines[1], 25, T["text"], 700)
    s += (f'<rect x="1.25" y="1.25" width="{CARD_W - 2.5}" height="{CARD_H - 2.5}" rx="21" fill="none" '
          f'stroke="{T["border"]}" stroke-width="2.5"/>')
    return s


def _card_medicine(T: dict, X: dict) -> str:
    """A nerve cell lit by a pulse of blue light from the tip of an optical fibre."""
    cx = CARD_W / 2
    s = '<g clip-path="url(#cardclip)">'
    s += f'<rect width="{CARD_W}" height="{WIN_H}" fill="url(#tis)"/>'
    s += f'<ellipse cx="{cx:g}" cy="78" rx="190" ry="250" fill="url(#glow)" class="pulse"/>'
    s += f'<polygon points="{cx-9:g},80 {cx+9:g},80 {cx+128:g},{WIN_H} {cx-128:g},{WIN_H}" fill="url(#cone)" class="pulse"/>'
    # the nerve cell: soma, dendrites, an axon running down out of the window
    sx, sy = cx + 6, 178
    n = X["neuron"]
    trunks = [
        f"M{sx-12} {sy-14} C{sx-34} {sy-38} {sx-58} {sy-46} {sx-96} {sy-70}",
        f"M{sx+12} {sy-14} C{sx+34} {sy-40} {sx+66} {sy-46} {sx+104} {sy-80}",
        f"M{sx-18} {sy+4} C{sx-48} {sy+8} {sx-80} {sy} {sx-116} {sy+22}",
        f"M{sx+18} {sy+4} C{sx+50} {sy+10} {sx+82} {sy+2} {sx+118} {sy+24}",
    ]
    twigs = [
        f"M{sx-58} {sy-46} Q{sx-66} {sy-74} {sx-62} {sy-104}",
        f"M{sx+62} {sy-45} Q{sx+86} {sy-40} {sx+112} {sy-30}",
        f"M{sx-80} {sy+1} Q{sx-90} {sy+26} {sx-98} {sy+54}",
        f"M{sx+86} {sy+3} Q{sx+98} {sy+28} {sx+102} {sy+60}",
        f"M{sx-30} {sy-34} Q{sx-26} {sy-60} {sx-14} {sy-84}",
    ]
    axon = f"M{sx+2} {sy+18} C{sx+6} {sy+56} {sx-22} {sy+82} {sx-14} {sy+118} S{sx-6} {sy+150} {sx-4} {WIN_H+4}"
    axon_twigs = [f"M{sx-12} {sy+112} Q{sx-38} {sy+120} {sx-58} {WIN_H+4}",
                  f"M{sx-12} {sy+108} Q{sx+20} {sy+116} {sx+44} {WIN_H+4}"]
    s += f'<circle cx="{sx:g}" cy="{sy}" r="70" fill="url(#halo)" class="pulse"/>'
    s += (f'<g fill="none" stroke="{n}" stroke-linecap="round" stroke-linejoin="round">'
          + "".join(f'<path d="{d}" stroke-width="5"/>' for d in trunks)
          + "".join(f'<path d="{d}" stroke-width="3.5"/>' for d in twigs + axon_twigs)
          + f'<path d="{axon}" stroke-width="5"/></g>')
    # the spike: a bright dash running down the axon
    s += (f'<path d="{axon}" fill="none" stroke="{T["coral"]}" stroke-width="7" stroke-linecap="round" '
          f'class="spk" pathLength="100"/>')
    s += f'<circle cx="{sx:g}" cy="{sy}" r="21" fill="{n}"/>'
    s += f'<circle cx="{sx:g}" cy="{sy}" r="21" fill="{T["cone"]}" class="lit"/>'
    s += f'<circle cx="{sx-6:g}" cy="{sy-6}" r="12" fill="url(#spark)" class="lit"/>'
    s += '</g>'
    # the optical fibre comes in from above the card
    s += (f'<rect x="{cx-9:g}" y="-40" width="18" height="110" rx="5" fill="{T["fibre"]}"/>'
          f'<path d="M{cx-9:g} 70 H{cx+9:g} L{cx:g} 82 Z" fill="{T["fibre"]}"/>')
    s += _hero_caption(T, "MEDICINE", T["violet"], ("A light switch", "for nerve cells"))
    return s


def _card_physics(T: dict, X: dict) -> str:
    """Strings of light sensors in dark ice, a particle track, its blue Cherenkov cone and a few lit sensors."""
    import math
    s = '<g clip-path="url(#cardclip)">'
    s += f'<rect width="{CARD_W}" height="{WIN_H}" fill="url(#ice)"/>'
    s += f'<rect width="{CARD_W}" height="22" fill="{X["ice_top"]}"/>'
    s += f'<line x1="0" y1="22" x2="{CARD_W}" y2="22" stroke="{T["border"]}" stroke-width="2"/>'
    front = [45, 95, 145, 195, 245]
    back = [70, 120, 170, 220]
    depths = [46 + 22 * k for k in range(12)]
    p0, p1 = (16.0, 34.0), (276.0, 300.0)
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    head_t = 0.74 * L
    hx, hy = p0[0] + ux * head_t, p0[1] + uy * head_t
    # strings (the back row fainter, for depth)
    for xs, op, off in ((back, .45, 11), (front, 1, 0)):
        s += f'<g stroke="{X["sensor_off"]}" stroke-opacity="{op}" stroke-width="2">'
        s += "".join(f'<line x1="{x}" y1="22" x2="{x}" y2="{WIN_H}"/>' for x in xs) + '</g>'
    # the Cherenkov cone: apex at the particle, opening backwards
    ang, cl = math.radians(41), 200
    bx, by = -ux, -uy
    e = []
    for sgn in (1, -1):
        c, sn = math.cos(sgn * ang), math.sin(sgn * ang)
        e.append((hx + cl * (bx * c - by * sn), hy + cl * (bx * sn + by * c)))
    s += (f'<linearGradient id="ckv" gradientUnits="userSpaceOnUse" x1="{hx:.1f}" y1="{hy:.1f}" '
          f'x2="{hx + bx * cl * .8:.1f}" y2="{hy + by * cl * .8:.1f}">'
          f'<stop offset="0" stop-color="{T["cone"]}" stop-opacity=".62"/>'
          f'<stop offset="1" stop-color="{T["cone"]}" stop-opacity="0"/></linearGradient>')
    s += (f'<polygon points="{hx:.1f},{hy:.1f} {e[0][0]:.1f},{e[0][1]:.1f} {e[1][0]:.1f},{e[1][1]:.1f}" '
          f'fill="url(#ckv)" class="pulse"/>')
    for ex, ey in e:
        s += (f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{hx + (ex - hx) * .55:.1f}" y2="{hy + (ey - hy) * .55:.1f}" '
              f'stroke="{T["cone"]}" stroke-width="2.5" stroke-opacity=".8" stroke-linecap="round"/>')
    # sensors: lit when the light from the track behind the particle reaches them; colour = arrival order
    times = [T["coral"], T["amber"], T["teal"]]
    unlit, lit = [], []
    for xs, off, scale in ((back, 11, .75), (front, 0, 1.0)):
        for x in xs:
            for d in depths:
                y = d + off
                wx, wy = x - p0[0], y - p0[1]
                proj = wx * ux + wy * uy
                perp = abs(wx * uy - wy * ux)
                if scale == 1 and perp < 24 and 30 < proj < head_t + 8:
                    r = 5.5 + 6 * (1 - perp / 24)
                    k = min(2, int(3 * proj / (head_t + 8)))
                    lit.append((x, y, r, times[k], proj))
                else:
                    unlit.append(f'<circle cx="{x}" cy="{y}" r="{3.6 * scale:.1f}" fill="{X["sensor_off"]}" '
                                 f'fill-opacity="{.9 if scale == 1 else .5}"/>')
    s += "".join(unlit)
    for x, y, r, col, proj in lit:
        delay = -4.0 * proj / head_t
        s += (f'<g class="tw" style="animation-delay:{delay:.2f}s">'
              f'<circle cx="{x}" cy="{y}" r="{r * 2.1:.1f}" fill="{col}" fill-opacity=".28"/>'
              f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="{col}"/></g>')
    # the track and the particle
    s += (f'<line x1="{p0[0]:g}" y1="{p0[1]:g}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="{T["text"]}" stroke-width="3.5" '
          f'stroke-linecap="round" stroke-opacity=".85"/>')
    s += _hero_arrow(hx + ux * 14, hy + uy * 14, ux, uy, 16, T["text"])
    s += '</g>'
    s += _hero_caption(T, "PHYSICS", T["teal"], ("A telescope", "made of ice"))
    return s


def _hero_arrow(x: float, y: float, ux: float, uy: float, size: float, col: str) -> str:
    bx, by = x - ux * size, y - uy * size
    w = size * 0.6
    return (f'<polygon points="{x:.1f},{y:.1f} {bx + uy * w:.1f},{by - ux * w:.1f} '
            f'{bx - uy * w:.1f},{by + ux * w:.1f}" fill="{col}"/>')


def _card_chemistry(T: dict, X: dict) -> str:
    """A left hand and its mirror image across a dashed mirror; above them, three molecules of one hand, one of the other."""
    C = chem_theme(T)
    cx = CARD_W / 2
    s = '<g clip-path="url(#cardclip)">'
    s += f'<rect width="{CARD_W}" height="{WIN_H}" fill="{C["bg"]}"/><rect width="{CARD_W}" height="{WIN_H}" fill="url(#ruled)"/>'
    s += f'<line x1="22" y1="0" x2="22" y2="{WIN_H}" stroke="{ONE}" stroke-opacity=".28" stroke-width="2"/>'
    # the mirror
    s += f'<rect x="{cx - 4:g}" y="52" width="8" height="{WIN_H - 52}" fill="{C["mixed_soft"]}"/>'
    s += (f'<line x1="{cx:g}" y1="52" x2="{cx:g}" y2="{WIN_H}" stroke="{C["muted"]}" stroke-width="3" '
          f'stroke-dasharray="9 7"/>')
    s += text(cx, 36, "mirror", 18, C["muted"], 700, "middle", 'letter-spacing="1"')
    # one hand wins: many copies of it, one of its mirror image
    hs, hx, hy = .74, 76, 286
    s += "".join(token(cx - hx + dx, 94, 13, "one", C) for dx in (-34, 0, 34))
    s += token(cx + hx, 94, 13, "mirror", C)
    # the hands (the mirror one flipped, so its thumb points back at the mirror too)
    s += f'<g transform="translate({cx - hx:g},{hy}) scale({hs:g})">' + _hand(C, "one") + '</g>'
    s += f'<g transform="translate({cx + hx:g},{hy}) scale({-hs:g} {hs:g})">' + _hand(C, "mirror") + '</g>'
    s += '</g>'
    s += _hero_caption(T, "CHEMISTRY", C["one_text"], ("One hand wins:", "mirror molecules"))
    return s


# Literature: the colours of the Literature page (2026/literature/page), ink on paper and a papyrus sheet.
LIT = {
    "light": dict(paper="#F3ECE0", papyrus="#E2CD9F", fibre="#785828", fibre_op=".16", hole="#F3ECE0",
                  hole_edge="#50371A", hole_op=".38", ink="#2B2118", accent="#A8432A", shadow="#3C230A", kicker="#3F6E8C"),
    "dark": dict(paper="#1B1510", papyrus="#4A3920", fibre="#FFDCA0", fibre_op=".08", hole="#1B1510",
                 hole_edge="#000000", hole_op=".55", ink="#EEE2C8", accent="#E48A66", shadow="#000000", kicker="#8DBAD8"),
}
GREEK_FONT = 'Georgia, "Times New Roman", "DejaVu Serif", serif'


def lit_theme(T: dict) -> dict:
    return LIT["dark" if T is THEMES["dark"] else "light"]


def lit_defs(L: dict) -> str:
    """The papyrus fibres: close horizontal strands, unevenly spaced, over a few faint vertical ones."""
    f, op = L["fibre"], L["fibre_op"]
    return (f'<defs><pattern id="pfibre" width="47" height="11" patternUnits="userSpaceOnUse">'
            f'<g stroke="{f}" stroke-opacity="{op}"><line x1="0" y1="1.5" x2="47" y2="1.5" stroke-width="1"/>'
            f'<line x1="0" y1="5" x2="47" y2="5" stroke-width="1.6"/><line x1="0" y1="8.5" x2="47" y2="8.5" stroke-width=".8"/></g>'
            f'<g stroke="{f}" stroke-opacity=".05" stroke-width="2"><line x1="9" y1="0" x2="9" y2="11"/>'
            f'<line x1="31" y1="0" x2="31" y2="11"/></g>'
            f'</pattern></defs>')


def _greek(x: float, y: float, s: str, L: dict, size: float = 24) -> tuple[str, float]:
    """A run of Greek capitals; square brackets in the editors' red. Widths are fixed, so any serif lays out alike."""
    w = sum(.32 if ch in "[]" else .7 for ch in s) * size
    tspans = "".join(f'<tspan fill="{L["accent"]}">{ch}</tspan>' if ch in "[]" else esc(ch) for ch in s)
    return (f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" font-family=\'{GREEK_FONT}\' fill="{L["ink"]}" '
            f'textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs">{tspans}</text>'), w


def _card_literature(T: dict, X: dict) -> str:
    """A torn scrap of papyrus with a few lines of Greek capitals, holes in it, and square brackets where letters are lost.

    The letters are decorative, not a line of any poem: the card shows what a papyrus fragment looks like."""
    L = lit_theme(T)
    torn = ("38,50 60,44 74,49 92,42 118,46 140,40 158,45 176,41 198,47 214,42 236,46 252,40 "
            "258,58 250,74 262,92 254,110 248,124 260,140 252,160 264,178 250,196 256,214 246,232 258,250 250,268 "
            "236,276 214,270 196,282 172,274 150,280 128,272 104,282 84,274 62,280 44,272 "
            "36,256 44,238 32,220 40,200 30,182 42,162 34,144 44,126 32,106 40,88 30,70")
    holes = ("M134 112 L150 108 L168 113 L178 110 L182 124 L176 140 L160 144 L146 140 L132 142 L128 126 Z",
             "M150 190 L168 186 L182 192 L204 188 L214 200 L208 216 L190 222 L172 218 L154 222 L146 206 Z")
    s = '<g clip-path="url(#cardclip)">'
    s += f'<rect width="{CARD_W}" height="{WIN_H}" fill="{L["paper"]}"/>'
    s += '<g transform="rotate(-3 147 160)">'
    s += f'<polygon points="{torn}" fill="{L["shadow"]}" fill-opacity=".18" transform="translate(4 7)"/>'
    s += f'<polygon points="{torn}" fill="{L["papyrus"]}"/><polygon points="{torn}" fill="url(#pfibre)"/>'
    for d in holes:
        s += (f'<path d="{d}" fill="{L["hole"]}"/>'
              f'<path d="{d}" fill="none" stroke="{L["hole_edge"]}" stroke-opacity="{L["hole_op"]}" stroke-width="2" '
              f'stroke-linejoin="round"/>')
    s += f'<polygon points="{torn}" fill="none" stroke="{L["hole_edge"]}" stroke-opacity="{L["hole_op"]}" stroke-width="2" stroke-linejoin="round"/>'
    # five lines: torn off at both edges, and broken around the two holes
    x0 = 52
    for y, parts in ((92, (("]ΤΑΝΑΙΣΤΑ[", x0),)),
                     (134, (("]ΚΑΡ[", x0), ("]ΝΟΣ", 184))),
                     (174, (("]ΜΕΛΙΧΡΟΝ[", x0),)),
                     (214, (("]ΑΛΛΑ[", x0), ("]Ε[", 216))),
                     (254, (("]ΤΟΙ[", x0 + 24),))):
        for run, x in parts:
            s += _greek(x, y, run, L)[0]
    s += '</g></g>'
    s += _hero_caption(T, "LITERATURE", L["kicker"], ("What survives:", "a torn papyrus"))
    return s


# Peace: the colours of the Peace page (2026/peace/page), a warm room and a cool room side by side, as in the film.
PEACE = {
    "light": dict(warm_bg="#EFE7DB", cool_bg="#E3E6EA", pool_warm="#E8A25A", pool_cool="#8E959D", wall="#6A7079",
                  wood="#A3560F", wood_dark="#6B3A0E", steel="#4F565E", paper="#FBFAF7", kicker="#A3560F"),
    "dark": dict(warm_bg="#25211C", cool_bg="#1D2024", pool_warm="#E8A25A", pool_cool="#8E959D", wall="#5D636B",
                 wood="#E8A25A", wood_dark="#B9763A", steel="#A9B0B8", paper="#ECE8E1", kicker="#E8A25A"),
}


def peace_theme(T: dict) -> dict:
    return PEACE["dark" if T is THEMES["dark"] else "light"]


def _card_peace(T: dict, X: dict) -> str:
    """Two rooms side by side: on the left a judge's gavel on its block in warm light; on the right a table with a
    signed sheet on it and two empty chairs facing each other in cool light. Symbolic: no person is drawn."""
    P = peace_theme(T)
    mid = CARD_W / 2
    s = '<g clip-path="url(#cardclip)">'
    s += (f'<radialGradient id="pwarm" cx="0.5" cy="0" r="0.95"><stop offset="0" stop-color="{P["pool_warm"]}" stop-opacity=".42"/>'
          f'<stop offset="1" stop-color="{P["pool_warm"]}" stop-opacity="0"/></radialGradient>'
          f'<radialGradient id="pcool" cx="0.5" cy="0" r="0.95"><stop offset="0" stop-color="{P["pool_cool"]}" stop-opacity=".42"/>'
          f'<stop offset="1" stop-color="{P["pool_cool"]}" stop-opacity="0"/></radialGradient>')
    s += f'<rect width="{mid:g}" height="{WIN_H}" fill="{P["warm_bg"]}"/><rect width="{mid:g}" height="{WIN_H}" fill="url(#pwarm)"/>'
    s += f'<rect x="{mid:g}" width="{mid:g}" height="{WIN_H}" fill="{P["cool_bg"]}"/><rect x="{mid:g}" width="{mid:g}" height="{WIN_H}" fill="url(#pcool)"/>'
    floor = 262
    s += (f'<line x1="0" y1="{floor}" x2="{CARD_W}" y2="{floor}" stroke="{P["wall"]}" stroke-opacity=".55" stroke-width="2"/>')
    # left room: the sound block and a gavel resting at an angle
    s += (f'<rect x="22" y="{floor - 20}" width="78" height="20" rx="6" fill="{P["wood_dark"]}"/>'
          f'<rect x="30" y="{floor - 28}" width="62" height="10" rx="4" fill="{P["wood"]}"/>')
    s += (f'<g transform="rotate(-45 58 150)">'
          f'<rect x="53.5" y="150" width="9" height="98" rx="4.5" fill="{P["wood_dark"]}"/>'
          f'<rect x="21" y="134" width="74" height="32" rx="9" fill="{P["wood"]}"/>'
          f'<rect x="31" y="134" width="6" height="32" fill="{P["wood_dark"]}" fill-opacity=".55"/>'
          f'<rect x="79" y="134" width="6" height="32" fill="{P["wood_dark"]}" fill-opacity=".55"/></g>')
    # right room: a table with a signed sheet, two empty chairs facing each other
    tx0, tx1, ty = 186, 250, 214
    s += (f'<rect x="{tx0 - 6}" y="{ty}" width="{tx1 - tx0 + 12}" height="7" rx="3" fill="{P["steel"]}"/>'
          f'<g stroke="{P["steel"]}" stroke-width="5" stroke-linecap="round">'
          f'<line x1="{tx0 + 2}" y1="{ty + 7}" x2="{tx0 + 2}" y2="{floor}"/><line x1="{tx1 - 2}" y1="{ty + 7}" x2="{tx1 - 2}" y2="{floor}"/></g>')
    s += (f'<polygon points="{tx0 + 8},{ty - 1} {tx1 - 4},{ty - 1} {tx1 - 12},{ty - 9} {tx0 + 16},{ty - 9}" fill="{P["paper"]}"/>'
          f'<path d="M{tx0 + 24} {ty - 4} q5 -5 9 0 t9 0" fill="none" stroke="{P["wood"]}" stroke-width="2" stroke-linecap="round"/>')

    def chair(x_back: float, x_front: float) -> str:
        seat = ty + 8
        return (f'<g stroke="{P["steel"]}" stroke-width="5" stroke-linecap="round" fill="none">'
                f'<line x1="{x_back}" y1="{seat - 46}" x2="{x_back}" y2="{floor}"/>'
                f'<line x1="{x_back}" y1="{seat}" x2="{x_front}" y2="{seat}"/>'
                f'<line x1="{x_front}" y1="{seat}" x2="{x_front}" y2="{floor}"/></g>')
    s += chair(mid + 16, mid + 34) + chair(CARD_W - 16, CARD_W - 34)
    # the wall between the rooms
    s += f'<line x1="{mid:g}" y1="0" x2="{mid:g}" y2="{WIN_H}" stroke="{P["wall"]}" stroke-width="3"/>'
    s += '</g>'
    s += _hero_caption(T, "PEACE", P["kicker"], ("Two rooms: courts", "and agreements"))
    return s


def _card_next(T: dict, X: dict) -> str:
    """A dashed slot: the prize still to be announced joins here."""
    cx = NEXT_W / 2
    s = (f'<rect x="1.25" y="1.25" width="{NEXT_W - 2.5}" height="{CARD_H - 2.5}" rx="21" fill="{X["next_fill"]}" '
         f'fill-opacity=".55" stroke="{T["dots"]}" stroke-opacity=".75" stroke-width="2.5" stroke-dasharray="10 9"/>')
    s += (f'<circle cx="{cx:g}" cy="138" r="28" fill="none" stroke="{T["muted"]}" stroke-width="3"/>'
          f'<path d="M{cx-12:g} 138 H{cx+12:g} M{cx:g} 126 V150" stroke="{T["muted"]}" stroke-width="3.5" stroke-linecap="round"/>')
    s += text(cx, 212, "NEXT", 18, T["muted"], 800, "middle", 'letter-spacing="3"')
    s += f'<line x1="{cx-30:g}" y1="236" x2="{cx+30:g}" y2="236" stroke="{T["border"]}" stroke-width="2"/>'
    s += text(cx, 280, "Economics", 23, T["text"], 700, "middle")
    s += text(cx, 312, "12 Oct", 21, T["muted"], 500, "middle")
    return s


def _hero_words(T: dict) -> str:
    """The text block, in its own coordinates: 600 wide, from y = 100 to 470."""
    return _hero_head(T) + _hero_foot(T)


def _hero_head(T: dict) -> str:
    """Kicker, name and one line: y = 100 to 285 of the text block."""
    s = text(4, 124, "EDUCATIONAL DEMOS", 24, T["blue"], 700, extra='letter-spacing="5"', fit=334)
    s += text(0, 220, "Nobel 2026 Lab", 84, T["text"], 800, extra='letter-spacing="-2"', fit=599)
    s += text(4, 276, "Hands-on demos of this year’s Nobel Prizes.", 31, T["text"], 500, fit=596)
    return s


def _hero_foot(T: dict) -> str:
    """The toy-models pill and the showtime credit: y = 314 to 470 of the text block, 563 wide."""
    pill = "Toy models · not research · not for lab or clinical use"
    s = (f'<rect x="4" y="314" width="559" height="54" rx="27" fill="{T["pill"]}" stroke="{T["border"]}" stroke-width="2"/>'
         + text(4 + 26, 349, pill, 22, T["pill_text"], 600, fit=507))
    # credit for the tool that makes every video here
    s += (f'<rect x="4" y="408" width="40" height="30" rx="8" fill="none" stroke="{T["muted"]}" stroke-width="3"/>'
          f'<polygon points="19,415 19,431 32,423" fill="{T["coral"]}"/>')
    s += (f'<text x="58" y="432" font-size="25" fill="{T["muted"]}" font-weight="500">Videos made with '
          f'<tspan fill="{T["text"]}" font-weight="800">showtime</tspan></text>')
    s += text(58, 464, "an open-source video studio for coding agents", 20, T["muted"], 500)
    return s


def hero(name: str, T: dict, og: bool = False) -> str:
    X = HERO_EXTRA["dark" if T is THEMES["dark"] else "light"]
    prizes = (_card_medicine, _card_physics, _card_chemistry, _card_literature, _card_peace)
    row_w = len(prizes) * (CARD_W + CARD_GAP) + NEXT_W   # the row of cards, then the slot for the prize to come
    if og:   # the 1200 x 630 share image: full bleed, everything clear of the outer 40 px
        # Five cards do not fit beside the text at a readable size, so the share image has two rows:
        # the name on the left and the pill and credit on the right, then the cards across the full width.
        W, H, rx = 1200, 630, 0
        ws, gap = .64, 50                      # gap: room for the Medicine card's fibre above its card
        cs = (1200 - 2 * 48) / row_w
        top = (630 - (185 * ws + gap + CARD_H * cs)) / 2
        words = ((_hero_head, 48, top - 100 * ws, ws),
                 (_hero_foot, 1200 - 48 - 567 * ws, top + 185 * ws - 470 * ws, ws))
        cards = (48, top + 185 * ws + gap, cs)
    else:
        W, H, rx = 736 + row_w + 64, 560, 30
        words = ((_hero_words, 88, -6, 1.0),)
        cards = (736, 64, 1.0)
    alt = ("Nobel 2026 Lab. Hands-on demos of this year’s Nobel Prizes, one card per prize. Medicine: a nerve cell "
           "lit by a pulse of blue light from the tip of an optical fibre, with a spike running down its axon. Physics: "
           "strings of light sensors hanging in dark ice, a particle track with a cone of blue Cherenkov light behind it, "
           "and the sensors near the track lit up. Chemistry: a left hand drawn solid orange and its mirror image, a right "
           "hand drawn hatched teal, on either side of a dashed mirror line, with three small orange molecules above "
           "the left hand and only one teal one above the right: one hand wins. Literature: a torn scrap of papyrus "
           "with a few lines of Greek capitals, broken off at its ragged edges and around two holes, with red square "
           "brackets where letters are lost: what survives. Peace: two rooms side by side, a judge's gavel on its block in "
           "warm light on the left, and on the right, in cool light, a table with a signed sheet and two empty chairs "
           "facing each other. A smaller dashed slot holds the prize still to come: Economics on 12 October. Toy models, not research, not for lab or clinical use. Videos made "
           "with showtime, an open-source video studio for coding agents.")
    s = svg_open(W, H, "Nobel 2026 Lab: hands-on demos of this year’s Nobel Prizes", alt, T, extra_style=(
        ".pulse{animation:pulse 5s ease-in-out infinite}"
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.7}}"
        ".lit{animation:lit 5s ease-in-out infinite}"
        "@keyframes lit{0%,100%{opacity:.85}50%{opacity:.35}}"
        ".tw{animation:tw 4s ease-in-out infinite}"
        "@keyframes tw{0%,100%{opacity:1}50%{opacity:.62}}"
        ".spk{stroke-dasharray:14 186;stroke-dashoffset:-40;animation:spk 5s linear infinite}"
        "@keyframes spk{0%{stroke-dashoffset:14}100%{stroke-dashoffset:-186}}"
    ))
    s += _hero_defs(T, X) + chem_defs(chem_theme(T)) + lit_defs(lit_theme(T))
    s += f'<rect width="{W}" height="{H}" rx="{rx}" fill="url(#bg)"/><rect width="{W}" height="{H}" rx="{rx}" fill="url(#dots)"/>'
    if not og:
        s += f'<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="{rx-1}" fill="none" stroke="{T["border"]}" stroke-width="3"/>'
    for fn, wx, wy, ws in words:
        s += f'<g transform="translate({wx:g},{wy:g}) scale({ws:g})">' + fn(T) + '</g>'
    cx0, cy0, cs = cards
    s += f'<g transform="translate({cx0:g},{cy0:g}) scale({cs:g})">'
    s += _card_medicine(T, X)
    for k, card in enumerate(prizes[1:] + (_card_next,), start=1):
        s += f'<g transform="translate({k * (CARD_W + CARD_GAP)},0)">' + card(T, X) + '</g>'
    s += '</g>'
    s += SVG_CLOSE
    return s


# ---------------------------------------------------------------- timeline
def timeline(name: str, T: dict) -> str:
    W = 800
    cats = {
        "teal": ("Discoveries and ideas", T["teal"]),
        "blue": ("The tool for neurons", T["blue"]),
        "amber": ("Prizes and medicine", T["amber"]),
    }
    items = [
        ("1971", "teal", "Dieter Oesterhelt and Walther Stoeckenius find bacteriorhodopsin, a light-driven protein, in a salt-loving microbe."),
        ("Early 1990s", "teal", "Peter Hegemann asks why an alga reacts to light so fast. He proposes that one protein both catches light and forms a channel. The idea meets scepticism."),
        ("1999", "teal", "Francis Crick writes that the ideal signal for switching neurons on and off would be light, and calls the idea “rather far-fetched”."),
        ("2002", "teal", "Georg Nagel, Hegemann, Ernst Bamberg and colleagues show in frog eggs that channelrhodopsin-1 is a light-gated channel."),
        ("2003", "teal", "Channelrhodopsin-2 opens directly in light and works in mammalian cells. The paper says it “should become a useful tool”."),
        ("2004 to 2005", "blue", "4 August 2004: the first neuron carrying the protein fires to blue light. In 2005 Boyden, Zhang, Bamberg, Nagel and Deisseroth report millisecond control of nerve cells."),
        ("2006 to 2007", "blue", "The word “optogenetics” is coined in a 2006 review. In 2007 Deisseroth’s lab uses an optical fibre to switch on nerve cells in living mice."),
        ("2010 to 2013", "amber", "Nature Methods names optogenetics its Method of the Year 2010. The 2013 Brain Prize goes to six pioneers."),
        ("2021", "amber", "One blind patient regains partial sight with optogenetic gene therapy and light-projecting goggles. The Lasker Award goes to Deisseroth, Hegemann and Oesterhelt."),
        ("2026", "amber", "9 September: the FDA accepts an optogenetic gene therapy for review; it is not yet approved. 5 October: the Nobel Prize goes to Deisseroth, Hegemann and Nagel."),
    ]
    rail_x, card_x = 46, 84
    card_w = W - card_x - 22
    text_x, text_w, size, lh = card_x + 24, card_w - 48, 24, 31
    y = 232
    cards, nodes = [], []
    for year, cat, body in items:
        ls = wrap(body, size, text_w)
        h = 24 + 36 + len(ls) * lh + 14
        col = cats[cat][1]
        cards.append(
            f'<rect x="{card_x}" y="{y}" width="{card_w}" height="{h}" rx="18" fill="{T["panel"]}" stroke="{T["border"]}" stroke-width="2"/>'
            f'<rect x="{card_x}" y="{y+18}" width="6" height="{h-36}" rx="3" fill="{col}"/>'
            + text(text_x, y + 46, year, 29, col, 800)
            + para(text_x, y + 46 + 36, ls, size, T["text"], lh))
        nodes.append((y + 30, col))
        y += h + 16
    H = y + 100
    desc = ("A vertical timeline in ten steps from 1971 to 2026: a light-driven protein in a microbe (1971), "
            "Hegemann's idea of a one-protein light-gated channel (early 1990s), Crick's remark that light would be the ideal signal (1999), "
            "channelrhodopsin-1 (2002) and channelrhodopsin-2 (2003), the first neurons fired with blue light (2004 to 2005), "
            "the word optogenetics and fibre optics in living mice (2006 to 2007), early prizes (2010 to 2013), partial sight "
            "recovery in one patient (2021), and the 2026 Nobel Prize.")
    s = svg_open(W, H, "From algae to a Nobel Prize: a timeline, 1971 to 2026", desc, T)
    s += bg_rect(W, H, T)
    s += text(40, 78, "From algae to a Nobel Prize", 38, T["text"], 800)
    s += text(40, 118, "Ten steps, 1971 to 2026", 26, T["muted"], 500)
    # legend (two rows to stay readable on a phone)
    lx, ly = 40, 164
    for key in ("teal", "blue", "amber"):
        label, col = cats[key]
        need = 26 + tw(label, 22)
        if lx + need > W - 40:
            lx, ly = 40, ly + 34
        s += f'<circle cx="{lx+9}" cy="{ly-8}" r="9" fill="{col}"/>' + text(lx + 26, ly, label, 22, T["muted"], 500)
        lx += need + 24
    s += f'<line x1="{rail_x}" y1="{nodes[0][0]}" x2="{rail_x}" y2="{nodes[-1][0]}" stroke="{T["rail"]}" stroke-width="5" stroke-linecap="round"/>'
    s += "\n".join(cards)
    for ny, col in nodes:
        s += f'<circle cx="{rail_x}" cy="{ny}" r="13" fill="{col}" stroke="{T["bg"]}" stroke-width="5"/>'
    s += para(40, H - 62, wrap("Every step is sourced in FACTS.md, section 3. Educational demo, not research.", 21, W - 80), 21, T["muted"], 28)
    s += SVG_CLOSE
    return s


# ---------------------------------------------------------------- light-gated channel
def channel(name: str, T: dict) -> str:
    W = 800
    pw, gutter, mx = 348, 56, 24
    steps = [
        ("1", "Light arrives", "Blue light, around 460 to 470 nanometres, reaches the protein in the cell’s outer membrane."),
        ("2", "Channel opens", "A light-catching molecule inside the protein, retinal, changes shape. The protein opens a pore through itself."),
        ("3", "Ions flow in", "Positive ions flow through the open pore, mostly into the cell."),
        ("4", "Neuron fires", "The inside of the cell becomes less negative and can fire a spike, within milliseconds."),
    ]
    cap_size, cap_lh = 23, 29
    cap_lines = [wrap(c, cap_size, pw - 48) for _, _, c in steps]
    row_lines = [max(len(cap_lines[0]), len(cap_lines[1])), max(len(cap_lines[2]), len(cap_lines[3]))]
    ill_h = 284
    top = 156
    heights = [84 + n * cap_lh + 14 + ill_h for n in row_lines]
    ys = [top, top + heights[0] + 30]
    H = ys[1] + heights[1] + 30 + 150
    desc = ("A four-step drawing of how a light-gated channel works. Step 1: blue light arrives at a protein sitting in the cell membrane, "
            "with the channel closed. Step 2: a light-catching molecule inside the protein changes shape and a pore opens. "
            "Step 3: positive ions flow through the open pore into the cell. Step 4: the inside of the cell becomes less negative "
            "and the neuron fires a spike. Simplified; shapes are not to scale.")
    s = svg_open(W, H, "How a light-gated channel works, in four steps", desc, T)
    s += bg_rect(W, H, T)
    s += text(40, 78, "How a light-gated channel works", 38, T["text"], 800)
    s += text(40, 118, "Light, a pore, ions, a spike", 26, T["muted"], 500)

    WALL, WH = 52, 96   # wall width and height of the protein halves

    def membrane(cx: float, my: float, open_: bool) -> str:
        gap = 22 if open_ else 0
        lx = cx - gap - WALL            # left wall x
        rx = cx + gap                   # right wall x
        mem = (f'<rect x="{mx}" y="{my}" width="{lx - mx:g}" height="52" fill="{T["membrane"]}" stroke="{T["membrane_edge"]}" stroke-width="2.5"/>'
               f'<rect x="{rx + WALL:g}" y="{my}" width="{pw - mx - rx - WALL:g}" height="52" fill="{T["membrane"]}" stroke="{T["membrane_edge"]}" stroke-width="2.5"/>')
        wall = (f'<rect x="{lx:g}" y="{my - 22}" width="{WALL}" height="{WH}" rx="16" fill="{T["protein"]}"/>'
                f'<rect x="{rx:g}" y="{my - 22}" width="{WALL}" height="{WH}" rx="16" fill="{T["protein"]}"/>')
        if not open_:
            wall += f'<line x1="{cx:g}" y1="{my - 18}" x2="{cx:g}" y2="{my + 70}" stroke="{T["panel"]}" stroke-width="3"/>'
        return mem + wall

    for i, (num, ttl, cap) in enumerate(steps):
        col, row = i % 2, i // 2
        x = mx + col * (pw + gutter)
        y = ys[row]
        ph = heights[row]
        g = f'<g transform="translate({x},{y})">'
        g += f'<rect width="{pw}" height="{ph}" rx="22" fill="{T["panel"]}" stroke="{T["border"]}" stroke-width="2"/>'
        g += f'<circle cx="42" cy="46" r="22" fill="{T["blue"]}"/>' + text(42, 55, num, 26, T["bg"], 800, "middle")
        g += text(78, 56, ttl, 28, T["text"], 800)
        g += para(24, 100, cap_lines[i], cap_size, T["muted"], cap_lh)
        oy = 84 + row_lines[row] * cap_lh + 14   # top of the illustration area
        cx, my = pw / 2, oy + 112                # channel centre x, membrane top y
        if i == 0:
            g += membrane(cx, my, False)
            g += f'<polygon points="{cx-54:g},{oy+4} {cx+54:g},{oy+4} {cx+24:g},{my-26} {cx-24:g},{my-26}" fill="{T["blue"]}" fill-opacity=".34"/>'
            for dx in (-24, 0, 24):
                g += f'<line x1="{cx+dx*1.5:g}" y1="{oy+12}" x2="{cx+dx*0.6:g}" y2="{my-32}" stroke="{T["blue"]}" stroke-width="5" stroke-linecap="round"/>'
            g += text(pw - 18, my - 40, "blue light", 22, T["blue"], 700, "end")
            rx_ = cx - 26   # retinal x, inside the left wall
            g += (f'<path d="M{rx_:g} {my-2} L{rx_:g} {my+46}" fill="none" stroke="{T["amber"]}" '
                  f'stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
            g += f'<line x1="{rx_:g}" y1="{my+56}" x2="{rx_:g}" y2="{my+92}" stroke="{T["amber"]}" stroke-width="2.5"/>'
            g += text(rx_, my + 116, "retinal", 21, T["amber"], 700, "middle")
            g += text(cx, my + 156, "channel closed", 22, T["muted"], 600, "middle")
        if i == 1:
            g += membrane(cx, my, True)
            g += f'<polygon points="{cx-54:g},{oy+4} {cx+54:g},{oy+4} {cx+24:g},{my-26} {cx-24:g},{my-26}" fill="{T["blue"]}" fill-opacity=".22"/>'
            rx_ = cx - 22 - WALL / 2   # inside the left wall
            g += f'<circle cx="{rx_:g}" cy="{my+22}" r="30" fill="{T["amber"]}" fill-opacity=".28"/>'
            g += (f'<path d="M{rx_:g} {my-2} L{rx_:g} {my+12} L{rx_+10:g} {my+24} L{rx_+10:g} {my+46}" fill="none" stroke="{T["amber"]}" '
                  f'stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
            g += f'<line x1="{rx_+10:g}" y1="{my+56}" x2="{rx_+10:g}" y2="{my+92}" stroke="{T["amber"]}" stroke-width="2.5"/>'
            g += text(rx_ + 10, my + 116, "retinal, new shape", 21, T["amber"], 700, "middle")
            g += text(cx, my + 156, "pore open", 22, T["muted"], 600, "middle")
        if i == 2:
            g += membrane(cx, my, True)
            g += text(mx, oy + 22, "outside", 21, T["muted"], 600)
            g += text(mx, my + 156, "inside", 21, T["muted"], 600)
            ions = [(cx - 72, oy + 56), (cx + 62, oy + 40), (cx + 100, oy + 96), (cx - 4, oy + 52),
                    (cx, my + 4), (cx, my + 44),
                    (cx - 78, my + 108), (cx + 14, my + 122), (cx + 82, my + 100)]
            for ix, iy in ions:
                g += f'<circle cx="{ix:g}" cy="{iy:g}" r="13" fill="{T["teal"]}"/>' + text(ix, iy + 7, "+", 20, T["bg"], 800, "middle")
            for ay in (oy + 84, my + 70):
                g += (f'<path d="M{cx-12:g} {ay} l12 11 l12 -11" fill="none" stroke="{T["teal"]}" stroke-width="4.5" '
                      f'stroke-linecap="round" stroke-linejoin="round"/>')
        if i == 3:
            base, peak = oy + 176, oy + 44
            g += f'<line x1="34" y1="{base}" x2="{pw-26}" y2="{base}" stroke="{T["membrane_edge"]}" stroke-width="3"/>'
            g += f'<line x1="34" y1="{base}" x2="34" y2="{oy+14}" stroke="{T["membrane_edge"]}" stroke-width="3"/>'
            x0 = 66
            g += (f'<path d="M34 {base-10} H{x0+34} L{x0+52} {base-18} L{x0+66} {peak} L{x0+88} {base+14} L{x0+108} {base-10} H{pw-30}" '
                  f'fill="none" stroke="{T["coral"]}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>')
            g += f'<rect x="{x0+8}" y="{base+34}" width="46" height="12" rx="6" fill="{T["blue"]}"/>'
            g += text(x0 + 31, base + 72, "light pulse", 21, T["blue"], 700, "middle")
            g += text(x0 + 66 + 16, peak + 8, "spike", 22, T["coral"], 700)
            g += text(44, oy + 26, "voltage", 21, T["muted"], 600)
            g += text(pw - 26, base + 72, "time: ms", 21, T["muted"], 600, "end")
        g += '</g>'
        s += g
        if i in (0, 2):
            s += (f'<path d="M{x + pw + 16} {y + 34} l22 12 l-22 12" fill="none" stroke="{T["muted"]}" stroke-width="5" '
                  f'stroke-linecap="round" stroke-linejoin="round"/>')
    fy = ys[1] + heights[1] + 62
    f1 = wrap("In frog eggs the channel opened within about 0.2 milliseconds. In neurons, blue light controls firing with millisecond precision.", 22, W - 80)
    f2 = wrap("Simplified drawing: shapes and sizes are not to scale. Sources: FACTS.md, section 4.", 20, W - 80)
    s += para(40, fy, f1, 22, T["text"], 29)
    s += para(40, fy + len(f1) * 29 + 14, f2, 20, T["muted"], 27)
    s += SVG_CLOSE
    return s


# ---------------------------------------------------------------- credit map
def credit(name: str, T: dict) -> str:
    W = 800
    mx = 24
    cw = W - 2 * mx
    pad = 26
    inner_w = cw - 2 * pad
    parts: list[str] = []
    y = 210

    def section(title, sub, col):
        nonlocal y
        out = f'<rect x="{mx}" y="{y}" width="8" height="40" rx="4" fill="{col}"/>' + text(mx + 22, y + 30, title, 29, T["text"], 800)
        y += 52
        sl = wrap(sub, 22, cw - 30)
        out += para(mx + 22, y + 6, sl, 22, T["muted"], 29)
        y += len(sl) * 29 + 24
        parts.append(out)

    def card(name_, where, body, col, big=True):
        nonlocal y
        nl = 28 if big else 26
        wl = wrap(where, 21, inner_w) if where else []
        bl = wrap(body, 23, inner_w)
        h = pad - 6 + nl + 8 + len(wl) * 27 + (6 if wl else 0) + len(bl) * 30 + pad - 6
        out = (f'<rect x="{mx}" y="{y}" width="{cw}" height="{h}" rx="18" fill="{T["panel"]}" stroke="{T["border"]}" stroke-width="2"/>'
               f'<rect x="{mx}" y="{y+16}" width="6" height="{h-32}" rx="3" fill="{col}"/>')
        yy = y + pad - 6 + nl
        out += text(mx + pad, yy, name_, nl, T["text"], 800)
        yy += 8
        if wl:
            yy += 22
            out += para(mx + pad, yy, wl, 21, col, 27, 600)
            yy += (len(wl) - 1) * 27 + 6
        yy += 28
        out += para(mx + pad, yy, bl, 23, T["text"], 30)
        parts.append(out)
        y += h + 14

    def link(label):
        nonlocal y
        out = (f'<path d="M{mx+44} {y-12} v22 m0 0 l-9 -9 m9 9 l9 -9" fill="none" stroke="{T["muted"]}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
        out += text(mx + 70, y + 6, label, 21, T["muted"], 500)
        parts.append(out)
        y += 32

    section("The prize: three people", "The Nobel committee’s citation: “for their discoveries concerning light-gated ion channels and optogenetics.”", T["amber"])
    card("Peter Hegemann", "Max Planck Institute for Biochemistry (prize work); Humboldt University of Berlin",
         "Asked why an alga reacts to light so fast. Proposed that one protein is both light sensor and channel. His group found the genes.", T["amber"])
    link("sent two algal genes to test")
    card("Georg Nagel", "Max Planck Institute for Biophysics (prize work); University of Würzburg",
         "Put the genes into frog eggs and showed the proteins are light-gated channels (2002, 2003). Provided the ChR2 clone used in neurons.", T["amber"])
    link("sent the ChR2 clone after an email request")
    card("Karl Deisseroth", "Stanford University; Howard Hughes Medical Institute",
         "His lab first showed ChR2 firing neurons with blue light (2005), and in 2007 used optical fibres in living mice.", T["amber"])
    y += 12
    section("Also named in the committee’s texts", "People the scientific background names. None of them is a laureate.", T["blue"])
    card("Ernst Bamberg", "Co-author of the 2002, 2003 and 2005 papers",
         "The committee names him as Nagel’s PhD supervisor and a collaborator on both channelrhodopsin papers.", T["blue"], False)
    card("Edward Boyden", "First author of the 2005 paper",
         "With Xue Han, led an independent 2007 study that used halorhodopsin to silence neurons.", T["blue"], False)
    card("Feng Zhang", "Co-author of the 2005 paper",
         "Led the 2007 halorhodopsin silencing paper in Deisseroth’s lab.", T["blue"], False)
    card("Gero Miesenböck", "Light-sensitive neurons with genes, 2002",
         "Co-author of the 2006 review that coined the word “optogenetics”.", T["blue"], False)
    card("Spudich and Takahashi groups", "Independent discovery",
         "Identified the same algal genes at about the same time.", T["blue"], False)
    card("Pan; Herlitze and Landmesser; Yawo", "Early independent studies, 2005 to 2006",
         "Zhuo-Hua Pan restored light responses in mouse retinas. The other groups used ChR2 in neurons.", T["blue"], False)
    y += 12
    section("Other prizes and the rule", "What the prize pages and news reports say.", T["teal"])
    card("2013 Brain Prize: six people", "",
         "Ernst Bamberg, Edward Boyden, Karl Deisseroth, Peter Hegemann, Gero Miesenböck and Georg Nagel.", T["teal"], False)
    card("2021 Lasker Basic Award: three people", "",
         "Karl Deisseroth, Peter Hegemann and Dieter Oesterhelt.", T["teal"], False)
    card("The Nobel rule", "",
         "A Nobel Prize is limited to no more than three people (STAT; Nature).", T["teal"], False)
    H = y + 110
    desc = ("A neutral map of the people the Nobel committee names for the 2026 Medicine prize. Three prize winners, Peter Hegemann, "
            "Georg Nagel and Karl Deisseroth, are shown with what the committee says they did and with arrows for who sent genes to whom. "
            "Below them are the other people the committee's texts name, such as Ernst Bamberg, Edward Boyden, Feng Zhang and Gero Miesenböck, "
            "then the 2013 Brain Prize and 2021 Lasker winners and the three-person rule. It lists what the sources say and does not rank anyone.")
    s = svg_open(W, H, "Where the credit sits: who the Nobel committee names", desc, T)
    s += bg_rect(W, H, T)
    s += text(40, 78, "Where the credit sits", 38, T["text"], 800)
    sub = wrap("A map of what the sources write about who did what. It does not rank anyone.", 24, W - 80)
    s += para(40, 118, sub, 24, T["muted"], 31)
    s += "\n".join(parts)
    s += para(40, H - 70, wrap("Sources: FACTS.md section 2, the committee’s scientific background, the Brain Prize and Lasker pages.", 20, W - 80), 20, T["muted"], 27)
    s += SVG_CLOSE
    return s


# ---------------------------------------------------------------- physics helpers
def arrowhead(x: float, y: float, ux: float, uy: float, size: float, col: str) -> str:
    """A filled arrowhead with its tip at (x, y), pointing along the unit vector (ux, uy)."""
    bx, by = x - ux * size, y - uy * size
    w = size * 0.62
    return (f'<polygon points="{x:.1f},{y:.1f} {bx + uy * w:.1f},{by - ux * w:.1f} '
            f'{bx - uy * w:.1f},{by + ux * w:.1f}" fill="{col}"/>')


def burst(x: float, y: float, r: float, col: str) -> str:
    """An eight-point star: where a neutrino hits a nucleus."""
    import math
    pts = []
    for k in range(16):
        a = math.pi * k / 8
        rr = r if k % 2 == 0 else r * 0.45
        pts.append(f"{x + rr * math.cos(a):.1f},{y + rr * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{col}"/>'


# ---------------------------------------------------------------- physics: how a neutrino telescope works
def telescope(name: str, T: dict) -> str:
    import math
    W = 800
    pw, gutter, mx = 348, 56, 24
    steps = [
        ("1", "Passes through", "A neutrino from space has no electric charge. Almost always, it crosses the whole Earth and the ice without touching anything."),
        ("2", "A rare hit", "Very rarely, one hits a nucleus in the ice. That makes a muon, which leaves a long track, or a shower, a ball of light."),
        ("3", "A cone of light", "The charged particles move faster than light travels in ice. They give off a cone of blue light, called Cherenkov light."),
        ("4", "Sensors see it", "Sensors on strings record when and how much light arrives. The pattern gives the direction and the energy."),
    ]
    cap_size, cap_lh = 23, 29
    cap_lines = [wrap(c, cap_size, pw - 48) for _, _, c in steps]
    row_lines = [max(len(cap_lines[0]), len(cap_lines[1])), max(len(cap_lines[2]), len(cap_lines[3]))]
    ill_h = 292
    top = 156
    heights = [84 + n * cap_lh + 14 + ill_h + 14 for n in row_lines]
    ys = [top, top + heights[0] + 30]
    H = ys[1] + heights[1] + 30 + 150
    desc = ("A four-panel drawing of how a neutrino telescope works. Panel 1: a neutrino from space crosses the Earth and the "
            "ice at the South Pole without touching anything, which is what almost always happens. Panel 2: very rarely it hits "
            "a nucleus in the ice and makes either a muon, which leaves a long track, or a shower, a ball of light. Panel 3: the "
            "charged particles move faster than light travels in ice and give off a cone of blue Cherenkov light. Panel 4: light "
            "sensors on vertical strings record when and how much light arrives, the first sensors in red and the last in blue, "
            "and the pattern gives the direction and the energy. A simplified drawing: shapes, sizes and angles are not to scale.")
    s = svg_open(W, H, "How a neutrino telescope works, in four steps", desc, T)
    s += (f'<defs>'
          f'<linearGradient id="iceg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T["ice1"]}"/>'
          f'<stop offset="1" stop-color="{T["ice2"]}"/></linearGradient>'
          f'<radialGradient id="ball" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{T["cone"]}" stop-opacity=".9"/>'
          f'<stop offset=".55" stop-color="{T["cone"]}" stop-opacity=".35"/>'
          f'<stop offset="1" stop-color="{T["cone"]}" stop-opacity="0"/></radialGradient>'
          f'<linearGradient id="ckv" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="{T["cone"]}" stop-opacity=".55"/>'
          f'<stop offset="1" stop-color="{T["cone"]}" stop-opacity="0"/></linearGradient>'
          f'</defs>')
    s += bg_rect(W, H, T)
    s += text(40, 78, "How a neutrino telescope works", 38, T["text"], 800)
    s += text(40, 118, "Through the Earth, a rare hit, a cone of light", 26, T["muted"], 500)

    nu, mu, lt = T["violet"], T["coral"], T["blue"]

    def ice_box(oy: float) -> str:
        return (f'<rect x="16" y="{oy:g}" width="{pw - 32}" height="{ill_h - 4}" rx="16" fill="url(#iceg)" '
                f'stroke="{T["ice_edge"]}" stroke-width="2"/>'
                + text(pw - 30, oy + 26, "ice", 20, T["muted"], 600, "end"))

    for i, (num, ttl, cap) in enumerate(steps):
        col, row = i % 2, i // 2
        x = mx + col * (pw + gutter)
        y = ys[row]
        ph = heights[row]
        g = f'<g transform="translate({x},{y})">'
        g += f'<rect width="{pw}" height="{ph}" rx="22" fill="{T["panel"]}" stroke="{T["border"]}" stroke-width="2"/>'
        g += f'<circle cx="42" cy="46" r="22" fill="{T["blue"]}"/>' + text(42, 55, num, 26, T["bg"], 800, "middle")
        g += text(78, 56, ttl, 28, T["text"], 800)
        g += para(24, 100, cap_lines[i], cap_size, T["muted"], cap_lh)
        oy = 84 + row_lines[row] * cap_lh + 14   # top of the illustration area
        cx = pw / 2
        if i == 0:
            ex, ey, er = cx, oy + 124, 96                   # the Earth
            cy_ = ey + 74                                   # chord of the polar ice cap
            hw = math.sqrt(er * er - 74 * 74)
            g += f'<circle cx="{ex:g}" cy="{ey:g}" r="{er}" fill="{T["earth"]}" stroke="{T["earth_edge"]}" stroke-width="2.5"/>'
            g += (f'<path d="M{ex - hw:.1f} {cy_:g} A{er} {er} 0 0 0 {ex + hw:.1f} {cy_:g} Z" fill="{T["ice_top"]}" '
                  f'stroke="{T["ice_edge"]}" stroke-width="2.5"/>')
            g += text(ex + 34, ey - 6, "Earth", 22, T["muted"], 700, "middle")
            x0, y0, x1, y1 = 36.0, oy + 8, ex + 6, ey + er
            yend = oy + ill_h - 14
            xend = x0 + (x1 - x0) * (yend - y0) / (y1 - y0)
            L = math.hypot(xend - x0, yend - y0)
            ux, uy = (xend - x0) / L, (yend - y0) / L
            g += (f'<line x1="{x0:g}" y1="{y0:g}" x2="{xend - ux * 10:.1f}" y2="{yend - uy * 10:.1f}" stroke="{nu}" '
                  f'stroke-width="4.5" stroke-dasharray="10 8" stroke-linecap="round"/>')
            g += arrowhead(xend, yend, ux, uy, 18, nu)
            g += text(60, oy + 24, "neutrino", 22, nu, 700)
            g += text(24, oy + ill_h - 22, "South Pole ice", 21, T["muted"], 700)
            g += (f'<line x1="96" y1="{oy + ill_h - 44:g}" x2="{ex - hw * 0.55:.1f}" y2="{cy_ + 10:g}" '
                  f'stroke="{T["muted"]}" stroke-width="2"/>')
        if i == 1:
            g += ice_box(oy)
            for k, (sx, hx) in enumerate(((40.0, 86.0), (196.0, 242.0))):
                sy, hy = oy + 16, oy + 104
                L = math.hypot(hx - sx, hy - sy)
                ux, uy = (hx - sx) / L, (hy - sy) / L
                g += (f'<line x1="{sx:g}" y1="{sy:g}" x2="{hx - ux * 12:.1f}" y2="{hy - uy * 12:.1f}" stroke="{nu}" '
                      f'stroke-width="4.5" stroke-dasharray="10 8" stroke-linecap="round"/>')
                if k == 0:
                    mx2, my2 = hx + ux * 118, hy + uy * 118
                    g += (f'<line x1="{hx:g}" y1="{hy:g}" x2="{mx2 - ux * 12:.1f}" y2="{my2 - uy * 12:.1f}" stroke="{mu}" '
                          f'stroke-width="6" stroke-linecap="round"/>')
                    g += arrowhead(mx2, my2, ux, uy, 20, mu)
                    g += burst(hx, hy, 15, T["amber"])
                    g += text(hx - 20, hy + 7, "hit", 21, T["amber"], 700, "end")
                    g += text(30, oy + 252, "muon:", 22, mu, 700)
                    g += text(30, oy + 276, "a long track", 21, T["text"], 500)
                else:
                    g += f'<circle cx="{hx + 6:g}" cy="{hy + 30:g}" r="58" fill="url(#ball)"/>'
                    g += burst(hx, hy, 15, T["amber"])
                    g += text(186, oy + 252, "shower:", 22, lt, 700)
                    g += text(186, oy + 276, "a ball of light", 21, T["text"], 500)
            g += f'<line x1="{cx:g}" y1="{oy + 40:g}" x2="{cx:g}" y2="{oy + 226:g}" stroke="{T["ice_edge"]}" stroke-width="2" stroke-dasharray="4 6"/>'
        if i == 2:
            g += ice_box(oy)
            ty = oy + 128
            ax, back, spread = 236.0, 108.0, 112.0
            g += (f'<polygon points="{ax:g},{ty:g} {ax - back:g},{ty - spread:g} {ax - back:g},{ty + spread:g}" '
                  f'fill="url(#ckv)"/>')
            for sgn in (-1, 1):
                g += (f'<line x1="{ax:g}" y1="{ty:g}" x2="{ax - back:g}" y2="{ty + sgn * spread:g}" stroke="{lt}" '
                      f'stroke-width="3.5" stroke-linecap="round"/>')
                el = math.hypot(back, spread)
                nx, ny = spread / el, sgn * back / el          # outward, forward normal to the light front
                for f in (0.38, 0.78):
                    px, py = ax - back * f, ty + sgn * spread * f
                    qx, qy = px + nx * 34, py + ny * 34
                    g += (f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{qx - nx * 8:.1f}" y2="{qy - ny * 8:.1f}" stroke="{lt}" '
                          f'stroke-width="3.5" stroke-linecap="round"/>')
                    g += arrowhead(qx, qy, nx, ny, 12, lt)
            g += f'<line x1="30" y1="{ty:g}" x2="{ax:g}" y2="{ty:g}" stroke="{mu}" stroke-width="6" stroke-linecap="round"/>'
            g += f'<circle cx="{ax:g}" cy="{ty:g}" r="9" fill="{mu}"/>'
            g += arrowhead(ax + 34, ty, 1, 0, 16, mu)
            g += text(30, ty - 16, "muon", 22, mu, 700)
            g += text(pw - 30, oy + ill_h - 18, "Cherenkov light", 22, lt, 700, "end")
        if i == 3:
            xs = [46 + j * 64 for j in range(5)]
            sens_y = [oy + 18 + k * 30 for k in range(7)]
            for sx in xs:
                g += f'<line x1="{sx}" y1="{oy + 4:g}" x2="{sx}" y2="{sens_y[-1] + 12:g}" stroke="{T["rail"]}" stroke-width="3"/>'
            t0x, t0y, t1x, t1y = 20.0, oy + 22, pw - 14, oy + 186
            L = math.hypot(t1x - t0x, t1y - t0y)
            ux, uy = (t1x - t0x) / L, (t1y - t0y) / L
            g += (f'<line x1="{t0x:g}" y1="{t0y:g}" x2="{t1x - ux * 12:.1f}" y2="{t1y - uy * 12:.1f}" stroke="{mu}" '
                  f'stroke-width="3" stroke-dasharray="8 7" stroke-opacity=".9"/>')
            g += arrowhead(t1x, t1y, ux, uy, 16, mu)
            order = [T["coral"], T["amber"], T["teal"], T["blue"]]
            lit, unlit = [], []
            for sx in xs:
                for sy in sens_y:
                    dx, dy = sx - t0x, sy - t0y
                    along = dx * ux + dy * uy
                    d = abs(dx * uy - dy * ux)
                    if d < 44:
                        r = 5 + 9 * (1 - d / 44)
                        c = order[min(3, int(4 * along / L))]
                        lit.append(f'<circle cx="{sx}" cy="{sy:g}" r="{r:.1f}" fill="{c}" stroke="{T["panel"]}" stroke-width="2"/>')
                    else:
                        unlit.append(f'<circle cx="{sx}" cy="{sy:g}" r="5" fill="{T["panel"]}" stroke="{T["sensor_off"]}" stroke-width="2.5"/>')
            g += "".join(unlit) + "".join(lit)
            g += text(pw - 18, sens_y[-1] + 34, "direction", 21, mu, 700, "end")
            ly = oy + ill_h - 36
            g += text(24, ly, "first", 21, T["muted"], 600)
            for k, c in enumerate(order):
                g += f'<circle cx="{86 + k * 22}" cy="{ly - 7:g}" r="8" fill="{c}"/>'
            g += text(86 + 3 * 22 + 16, ly, "last", 21, T["muted"], 600)
            g += text(24, ly + 28, "bigger dot: more light", 21, T["muted"], 600)
        g += '</g>'
        s += g
        if i in (0, 2):
            s += (f'<path d="M{x + pw + 16} {y + 34} l22 12 l-22 12" fill="none" stroke="{T["muted"]}" stroke-width="5" '
                  f'stroke-linecap="round" stroke-linejoin="round"/>')
    fy = ys[1] + heights[1] + 62
    f1 = wrap("IceCube watches a cubic kilometre of Antarctic ice this way, with 5,160 sensors on 86 strings.", 22, W - 80)
    f2 = wrap("Simplified drawing: shapes, sizes and angles are not to scale. Detector numbers: IceCube Collaboration, icecube.wisc.edu.", 20, W - 80)
    s += para(40, fy, f1, 22, T["text"], 29)
    s += para(40, fy + len(f1) * 29 + 14, f2, 20, T["muted"], 27)
    s += SVG_CLOSE
    return s


# ---------------------------------------------------------------- physics: IceCube to scale
def icecube_scale(name: str, T: dict) -> str:
    W = 800
    S = 0.26        # px per metre, for depth and for width (so those two are to scale)
    K = 0.28        # squash of the front-to-back direction: a view from slightly above
    Y0 = 262        # the ice surface, at the middle of the top face
    cx = 360
    VB = 640        # half the front-to-back size of the ice block drawn, in metres
    top_h = VB * S * K

    def Y(d: float) -> float:
        return Y0 + d * S

    def P(u: float, v: float, d: float) -> tuple[float, float]:
        return cx + u * S, Y(d) + v * S * K

    sp = 125.0
    pts = [(sp * (q + r / 2), sp * r * 3 ** 0.5 / 2)
           for q in range(-4, 5) for r in range(-4, 5) if abs(q + r) <= 4]
    pts.sort(key=lambda p: (p[1], p[0]))          # back to front
    hx = [(500, 0), (250, 433), (-250, 433), (-500, 0), (-250, -433), (250, -433)]
    d_top, d_bot = 1450, 2450
    block_l, block_r = 150, W - 24
    block_b = Y(d_bot) + top_h + 70
    H = int(block_b + 150)

    desc = ("A drawing of the IceCube Neutrino Observatory at the South Pole, seen from slightly above. A hexagon of vertical "
            "strings hangs in the ice below the surface. Light sensors sit on the strings between 1,450 metres and 2,450 metres "
            "deep, filling a hexagonal block about 1 kilometre across and 1 kilometre tall: a cubic kilometre of ice. In all "
            "there are 5,160 sensors on 86 strings, in holes drilled into the ice on a hexagonal grid 125 metres apart. On the "
            "surface, IceTop has 81 stations on top of the strings. Depth and width are drawn roughly to scale; only some "
            "strings and sensors are drawn, and the sensors are drawn far larger than they are. Numbers from the IceCube "
            "Collaboration, https://icecube.wisc.edu/science/icecube/ (checked 2026-10-06).")
    s = svg_open(W, H, "IceCube: a cubic kilometre of ice, roughly to scale", desc, T)
    s += (f'<defs><linearGradient id="iceb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T["ice1"]}"/>'
          f'<stop offset=".85" stop-color="{T["ice2"]}"/><stop offset="1" stop-color="{T["ice2"]}" stop-opacity="0"/>'
          f'</linearGradient></defs>')
    s += bg_rect(W, H, T)
    s += text(40, 78, "IceCube: a cubic kilometre of ice", 38, T["text"], 800)
    sub = wrap("5,160 light sensors on 86 strings, at the South Pole", 25, W - 80)
    s += para(40, 118, sub, 25, T["muted"], 32, 500)

    # the ice block: top face (the surface) and front face
    s += (f'<rect x="{block_l}" y="{Y0 + top_h:.1f}" width="{block_r - block_l}" height="{block_b - Y0 - top_h:.1f}" '
          f'fill="url(#iceb)"/>')
    s += (f'<rect x="{block_l}" y="{Y0 - top_h:.1f}" width="{block_r - block_l}" height="{2 * top_h:.1f}" rx="6" '
          f'fill="{T["ice_top"]}" stroke="{T["ice_edge"]}" stroke-width="2.5"/>')
    s += (f'<line x1="{block_l}" y1="{Y0 + top_h:.1f}" x2="{block_l}" y2="{block_b - 30:.1f}" stroke="{T["ice_edge"]}" stroke-width="2.5"/>'
          f'<line x1="{block_r}" y1="{Y0 + top_h:.1f}" x2="{block_r}" y2="{block_b - 30:.1f}" stroke="{T["ice_edge"]}" stroke-width="2.5"/>')

    def poly(points, **attrs) -> str:
        a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}" {a}/>'

    def seg(p, q, col, w, dash="", op=1.0) -> str:
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="{col}" '
                f'stroke-width="{w}" stroke-opacity="{op}" stroke-linecap="round"{d}/>')

    top_hex = [P(u, v, d_top) for u, v in hx]
    bot_hex = [P(u, v, d_bot) for u, v in hx]
    sil = [top_hex[3], top_hex[4], top_hex[5], top_hex[0], bot_hex[0], bot_hex[1], bot_hex[2], bot_hex[3]]
    s += poly(sil, fill=T["blue"], fill_opacity=".10")
    s += poly(top_hex, fill=T["blue"], fill_opacity=".10")
    # hidden edges first (back of the bottom hexagon, back vertical edges)
    for a, b in ((3, 4), (4, 5), (5, 0)):
        s += seg(bot_hex[a], bot_hex[b], T["blue"], 2, "6 6", .55)
    for k in (4, 5):
        s += seg(top_hex[k], bot_hex[k], T["blue"], 2, "6 6", .55)
    # surface hexagon (IceTop) outline
    surf_hex = [P(u, v, 0) for u, v in hx]
    s += poly(surf_hex, fill="none", stroke=T["amber"], stroke_width="2", stroke_dasharray="5 5", stroke_opacity=".8")
    # strings and sensors, back to front
    for u, v in pts:
        a, b = P(u, v, 0), P(u, v, d_bot)
        s += seg(a, b, T["fibre"], 1.3, "", .55)
        for d in range(d_top, d_bot + 1, 100):
            px, py = P(u, v, d)
            s += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.5" fill="{T["blue"]}"/>'
        s += f'<rect x="{a[0] - 3.5:.1f}" y="{a[1] - 2.5:.1f}" width="7" height="5" rx="1.5" fill="{T["amber"]}"/>'
    # visible edges of the instrumented volume
    for k in range(6):
        s += seg(top_hex[k], top_hex[(k + 1) % 6], T["blue"], 2.5, "", .9)
    for a, b in ((0, 1), (1, 2), (2, 3)):
        s += seg(bot_hex[a], bot_hex[b], T["blue"], 2.5, "", .9)
    for k in (0, 1, 2, 3):
        s += seg(top_hex[k], bot_hex[k], T["blue"], 2.5, "", .9)

    # depth axis on the left
    ax_x = 136
    s += seg((ax_x, Y0), (ax_x, Y(d_bot)), T["muted"], 2.5)
    for d, lab, sub_ in ((0, "0 m", "surface"), (d_top, "1,450 m", "top sensors"), (d_bot, "2,450 m", "deepest")):
        yy = Y(d)
        s += seg((ax_x - 8, yy), (ax_x, yy), T["muted"], 2.5)
        if d:
            s += seg((ax_x, yy), (cx - 500 * S - 6, yy), T["muted"], 1.6, "3 6", .9)
        s += text(ax_x - 14, yy + 2, lab, 22, T["text"], 800, "end")
        s += text(ax_x - 14, yy + 26, sub_, 19, T["muted"], 500, "end")
    # width bracket under the detector
    by = Y(d_bot) + top_h + 22
    xl, xr = cx - 500 * S, cx + 500 * S
    s += (f'<path d="M{xl:.1f} {by - 12:.1f} V{by:.1f} H{xr:.1f} V{by - 12:.1f}" fill="none" stroke="{T["text"]}" '
          f'stroke-width="2.5" stroke-linejoin="round"/>')
    s += text(cx, by + 30, "about 1 km", 22, T["text"], 800, "middle")

    # callouts on the right
    cx0 = 532

    def leader(y_text, tx, ty):
        return seg((cx0 - 8, y_text), (tx, ty), T["muted"], 1.8, "", .9)

    # IceTop, above the surface
    it = P(500, 0, 0)
    s += text(cx0, Y0 - top_h - 40, "IceTop: 81 stations", 22, T["amber"], 800)
    s += text(cx0, Y0 - top_h - 14, "on the surface", 20, T["muted"], 500)
    s += seg((cx0 - 8, Y0 - top_h - 24), (it[0] + 6, it[1] - 4), T["muted"], 1.8, "", .9)
    # holes and spacing, in the upper ice
    yh = Y(620)
    for k, ln in enumerate(("Strings hang in 86 holes", "drilled into the ice,", "125 m apart on a", "hexagonal grid.")):
        s += text(cx0, yh + k * 27, ln, 20, T["muted"], 500)
    # the cubic kilometre
    yk = Y(d_top) + 6
    s += text(cx0, yk, "A cubic kilometre", 24, T["blue"], 800)
    s += text(cx0, yk + 29, "of ice, watched from", 20, T["text"], 500)
    s += text(cx0, yk + 56, "1,450 m to 2,450 m deep", 20, T["text"], 500)
    s += leader(yk - 8, top_hex[0][0] + 6, top_hex[0][1])
    # the sensor count
    ys_ = Y(2010)
    s += text(cx0, ys_, "5,160 sensors", 28, T["blue"], 800)
    s += text(cx0, ys_ + 30, "on 86 strings", 22, T["text"], 600)
    s += leader(ys_ - 9, xr + 6, ys_ - 9)

    fy = block_b + 30
    f1 = wrap("Depth and width are roughly to scale. Only some strings and sensors are drawn, and the dots are far bigger than the real sensors.", 20, W - 80)
    f2 = wrap("Numbers: IceCube Collaboration, icecube.wisc.edu/science/icecube.", 20, W - 80)
    s += para(40, fy, f1, 20, T["text"], 27)
    s += para(40, fy + len(f1) * 27 + 10, f2, 20, T["muted"], 27)
    s += SVG_CLOSE
    return s


# ---------------------------------------------------------------- chemistry: its own look
# A warm paper notebook in light, a night notebook in dark. One hand is always burnt orange and solid;
# the mirror hand is always teal and hatched (so the two differ without colour too); mixed pairs are grey.
ONE, MIRROR = "#c4622d", "#2b8a8f"
CHEM = {
    "light": dict(bg="#F6EFE2", panel="#FFFAF0", border="#D8C9AE", text="#2B2118", muted="#66563F",
                  one_text="#A34B1C", mirror_text="#1B6A6E", mixed="#9B9283", mixed_soft="#ECE5D8",
                  rule="#E6D9C2", stick="#8A7B66", ball="#FFFDF8", hatch_line="#FFFAF0", chip="#F1E7D6"),
    "dark": dict(bg="#10141B", panel="#171D27", border="#323C4C", text="#EEE6D6", muted="#ABA394",
                 one_text="#EC8A5A", mirror_text="#5FC0C5", mixed="#8A867F", mixed_soft="#252C37",
                 rule="#1C2330", stick="#8C8577", ball="#F3ECDF", hatch_line="#10141B", chip="#202835"),
}


def chem_theme(T: dict) -> dict:
    return CHEM["dark" if T is THEMES["dark"] else "light"]


def chem_defs(C: dict) -> str:
    """The hatch for the mirror hand, and the notebook ruling behind the panels."""
    return (f'<defs>'
            f'<pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="9" height="9" fill="{MIRROR}"/>'
            f'<line x1="1.5" y1="0" x2="1.5" y2="9" stroke="{C["hatch_line"]}" stroke-width="2.6" stroke-opacity=".7"/></pattern>'
            f'<pattern id="ruled" width="32" height="32" patternUnits="userSpaceOnUse">'
            f'<line x1="0" y1="31" x2="32" y2="31" stroke="{C["rule"]}" stroke-width="1.5"/></pattern>'
            f'</defs>')


def chem_bg(w: float, h: float, C: dict, r: int = 28) -> str:
    return (f'<rect width="{w}" height="{h}" rx="{r}" fill="{C["bg"]}"/>'
            f'<rect x="8" y="8" width="{w-16}" height="{h-16}" rx="{r-6}" fill="url(#ruled)"/>'
            f'<line x1="22" y1="8" x2="22" y2="{h-8}" stroke="{ONE}" stroke-opacity=".28" stroke-width="2"/>'
            f'<rect x="1.5" y="1.5" width="{w-3}" height="{h-3}" rx="{r-1}" fill="none" stroke="{C["border"]}" stroke-width="3"/>')


def chem_panel(x: float, y: float, w: float, h: float, C: dict) -> str:
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="20" fill="{C["panel"]}" stroke="{C["border"]}" stroke-width="2"/>'


def hand_fill(hand: str) -> str:
    return ONE if hand == "one" else ("url(#hatch)" if hand == "mirror" else "")


def step_badge(x: float, y: float, num: str, C: dict) -> str:
    return (f'<circle cx="{x:g}" cy="{y:g}" r="21" fill="{C["text"]}"/>'
            + text(x, y + 8.5, num, 24, C["panel"], 800, "middle"))


def chem_title(W: float, title: str, sub: str, C: dict) -> tuple[str, float]:
    s = text(44, 78, title, 38, C["text"], 800)
    sl = wrap(sub, 25, W - 88)
    s += para(44, 118, sl, 25, C["muted"], 32, 500)
    return s, 118 + (len(sl) - 1) * 32


def chem_footer(W: float, y: float, lines: list[tuple[str, bool]], C: dict) -> tuple[str, float]:
    s = ""
    for body, strong in lines:
        size = 21 if strong else 19
        lh = 28 if strong else 26
        ls = wrap(body, size, W - 88)
        s += para(44, y, ls, size, C["text"] if strong else C["muted"], lh)
        y += len(ls) * lh + 10
    return s, y


def token(x: float, y: float, r: float, hand: str, C: dict, grey: bool = False) -> str:
    """A molecule with a hand: a ball with a knob on one side. Its mirror image has the knob on the other side."""
    import math
    ang = math.radians(-40 if hand == "one" else -140)
    kx, ky = x + r * 0.95 * math.cos(ang), y + r * 0.95 * math.sin(ang)
    fill = C["mixed"] if grey else hand_fill(hand)
    edge = C["panel"]
    return (f'<circle cx="{kx:.1f}" cy="{ky:.1f}" r="{r * .46:.1f}" fill="{fill}" stroke="{edge}" stroke-width="2"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{edge}" stroke-width="2"/>'
            f'<circle cx="{kx:.1f}" cy="{ky:.1f}" r="{r * .46 - 1:.1f}" fill="{fill}"/>')


def chem_arrow(x0: float, y0: float, x1: float, y1: float, col: str, w: float = 4) -> str:
    import math
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    return (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1 - ux * 10:.1f}" y2="{y1 - uy * 10:.1f}" stroke="{col}" '
            f'stroke-width="{w}" stroke-linecap="round"/>' + arrowhead(x1, y1, ux, uy, 14, col))


# ---------------------------------------------------------------- chemistry: mirror hands and alanine
def _hand(C: dict, hand: str) -> str:
    """A left hand seen from the back, fingers up, thumb on the right; origin at the wrist.

    Every part is drawn without its own transform, so the mirror hand's hatching runs the same way across it."""
    shapes = [
        '<rect x="-27" y="-28" width="54" height="40" rx="12"/>',                      # wrist
        '<rect x="-44" y="-110" width="88" height="96" rx="26"/>',                     # palm
    ]
    fingers = ((-32, -168), (-11, -192), (11, -200), (32, -184))                       # little to index finger
    for cx, top in fingers:
        shapes.append(f'<rect x="{cx - 10}" y="{top}" width="20" height="{-top - 80}" rx="10"/>')
    body = "".join(shapes)
    thumb = 'x1="30" y1="-34" x2="78" y2="-84"'
    out = (f'<g fill="none" stroke="{C["text"]}" stroke-width="7" stroke-linejoin="round">{body}</g>'
           f'<line {thumb} stroke="{C["text"]}" stroke-width="31" stroke-linecap="round"/>')
    out += f'<g fill="{hand_fill(hand)}">{body}</g>'
    out += f'<line {thumb} stroke="{hand_fill(hand)}" stroke-width="24" stroke-linecap="round"/>'
    # fingernails do not show from the back; knuckles do: small arcs at the base of each finger
    out += (f'<g stroke="{C["panel"]}" stroke-opacity=".7" stroke-width="3" stroke-linecap="round" fill="none">'
            + "".join(f'<path d="M{cx - 6} -86 q6 -5 12 0"/>' for cx, _ in fingers) + '</g>')
    return out


ALA_PRIORITY = {"NH₂": 1, "COOH": 2, "CH₃": 3, "H": 4}


def _alanine_vectors() -> dict[str, tuple[float, float, float]]:
    """Unit bond vectors of L-alanine, (S)-2-aminopropanoic acid: x right, y up, z toward the viewer.

    A regular tetrahedron with H up and leaning back, tilted so all four groups show; the three heavy
    groups are placed so that the centre is S (checked with the sign of a triple product)."""
    import math
    t = math.radians(-24)
    def tilt(v):
        x, y, z = v
        return (x, y * math.cos(t) - z * math.sin(t), y * math.sin(t) + z * math.cos(t))
    h = tilt((0.0, 1.0, 0.0))
    r = math.sqrt(8) / 3
    pos = [tilt((r * math.sin(math.radians(a)), -1 / 3, r * math.cos(math.radians(a)))) for a in (75, 195, 315)]
    # pos[0] right and to the front, pos[1] down and to the back, pos[2] left and to the front
    v = {"H": h, "NH₂": pos[0], "COOH": pos[2], "CH₃": pos[1]}
    def det(a, b, c):
        return (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0]))
    if det(v["NH₂"], v["COOH"], v["CH₃"]) < 0:        # R: swap two groups to make it S
        v["NH₂"], v["COOH"] = v["COOH"], v["NH₂"]
    assert det(v["NH₂"], v["COOH"], v["CH₃"]) > 0      # positive = S with these axes (checked on a Fischer projection)
    return v


def _molecule(cx: float, cy: float, C: dict, hand: str) -> str:
    """Ball-and-stick alanine. hand='one' draws L-alanine; 'mirror' draws its mirror image, D-alanine."""
    vec = _alanine_vectors()
    sgn = 1 if hand == "one" else -1
    Lb = 114
    items = []
    for name, (x, y, z) in vec.items():
        px, py = cx + sgn * x * Lb, cy - y * Lb
        base = 17 if name == "H" else 35
        items.append((z, name, px, py, base * (1 + 0.16 * z)))
    items.sort()
    s = ""
    def stick(px, py, front):
        import math
        L = math.hypot(px - cx, py - cy)
        x0, y0 = (cx + (px - cx) / L * 22, cy + (py - cy) / L * 22) if front else (cx, cy)   # front sticks leave the C ball's surface
        return (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{px:.1f}" y2="{py:.1f}" stroke="{C["text"]}" stroke-width="15" stroke-linecap="round"/>'
                f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{px:.1f}" y2="{py:.1f}" stroke="{C["stick"]}" stroke-width="9" stroke-linecap="round"/>')
    def ball(name, px, py, r, back=False):
        fill = C["mixed_soft"] if back else C["ball"]
        b = (f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="{fill}" stroke="{C["text"]}" stroke-width="3"/>')
        size = 16 if name == "COOH" else (18 if name != "H" else 17)
        return b + text(px, py + size * 0.36, name, size, C["text"] if back else "#2B2118", 800, "middle")
    for z, name, px, py, r in items:
        if z < 0:
            s += stick(px, py, False) + ball(name, px, py, r, back=True)
    s += (f'<circle cx="{cx:g}" cy="{cy:g}" r="27" fill="{hand_fill(hand)}" stroke="{C["text"]}" stroke-width="3"/>'
          + text(cx, cy + 8, "C", 23, "#FFFFFF", 800, "middle", f'stroke="{C["text"]}" stroke-width="3" paint-order="stroke"'))
    for z, name, px, py, r in items:
        if z >= 0:
            s += stick(px, py, True) + ball(name, px, py, r)
    return s


def mirror_hands(name: str, T: dict) -> str:
    C = chem_theme(T)
    W = 800
    mx = 400
    desc = ("Two hands and an amino acid, each next to its mirror image across a dashed mirror line. Top: a left hand, "
            "drawn solid orange, and its mirror image, a right hand, drawn hatched teal. Bottom: a ball-and-stick model of "
            "the amino acid alanine: a central carbon atom holding four different groups, a hydrogen atom (H), an amino "
            "group (NH2), a carboxylic acid group (COOH) and a methyl group (CH3), in a tetrahedral shape. On the left is "
            "L-alanine, the form found in the proteins of living things; on the right its mirror image, D-alanine. The two "
            "have the same atoms joined the same way, but they cannot be laid on top of each other, like a left and a right "
            "hand. Chemists call such molecules chiral, and the two forms enantiomers. Life uses one hand: the amino acids "
            "in our proteins are the L form. Our own drawing, not to scale.")
    s_title, ty = chem_title(W, "Mirror molecules", "Life uses one hand", C)
    top = ty + 34
    hand_y = top + 252
    mol_top = hand_y + 92
    mol_y = mol_top + 168
    lab_y = mol_y + 152
    foot_y = lab_y + 92
    foot, end = chem_footer(W, foot_y, [
        ("Same atoms, joined the same way, yet one cannot be laid on top of the other, like your two hands. "
         "Chemists call such molecules chiral, and the two forms enantiomers.", True),
        ("Like hands, amino acids come in two mirror forms, but only one is found in the proteins in your cells. "
         "Source: the Nobel Committee’s popular science background, 2026. Our own drawing, not to scale.", False),
    ], C)
    H = end + 34
    s = svg_open(W, H, "Mirror molecules: life uses one hand", desc, T)
    s += chem_defs(C) + chem_bg(W, H, C) + s_title
    s += chem_panel(36, top, W - 72, lab_y + 44 - top, C)
    # the mirror
    s += f'<rect x="{mx - 5}" y="{top + 54}" width="10" height="{lab_y - top - 60}" fill="{C["mixed_soft"]}"/>'
    s += (f'<line x1="{mx}" y1="{top + 54}" x2="{mx}" y2="{lab_y + 6}" stroke="{C["muted"]}" stroke-width="3" '
          f'stroke-dasharray="10 8"/>')
    s += text(mx, top + 38, "mirror", 21, C["muted"], 700, "middle", 'letter-spacing="1"')
    # hands
    s += f'<g transform="translate({mx - 175},{hand_y})">' + _hand(C, "one") + '</g>'
    s += f'<g transform="translate({mx + 175},{hand_y}) scale(-1 1)">' + _hand(C, "mirror") + '</g>'
    s += text(mx - 175, hand_y + 50, "a left hand", 22, C["one_text"], 800, "middle")
    s += text(mx + 175, hand_y + 50, "its mirror image: a right hand", 22, C["mirror_text"], 800, "middle")
    s += f'<line x1="60" y1="{mol_top - 10}" x2="{W - 60}" y2="{mol_top - 10}" stroke="{C["rule"]}" stroke-width="2"/>'
    # molecules
    s += _molecule(mx - 180, mol_y, C, "one")
    s += _molecule(mx + 180, mol_y, C, "mirror")
    s += text(mx - 180, lab_y, "L-alanine", 26, C["one_text"], 800, "middle")
    s += text(mx - 180, lab_y + 28, "the form in our proteins", 20, C["muted"], 600, "middle")
    s += text(mx + 180, lab_y, "D-alanine", 26, C["mirror_text"], 800, "middle")
    s += text(mx + 180, lab_y + 28, "its mirror image", 20, C["muted"], 600, "middle")
    s += foot
    s += SVG_CLOSE
    return s


# ---------------------------------------------------------------- chemistry: Kagan's bend
def _pair(x: float, y: float, a: str, b: str, C: dict, grey: bool = False, faded: bool = False) -> str:
    """A metal (M) holding two ligands, one on each side."""
    op = ' opacity=".45"' if faded else ""
    s = f'<g{op}>'
    for dx, hand in ((-24, a), (24, b)):
        fill = C["mixed"] if grey else hand_fill(hand)
        s += f'<circle cx="{x + dx:g}" cy="{y:g}" r="15" fill="{fill}" stroke="{C["text"]}" stroke-width="2.5"/>'
    s += f'<circle cx="{x:g}" cy="{y:g}" r="14" fill="{C["chip"]}" stroke="{C["text"]}" stroke-width="2.5"/>'
    s += text(x, y + 6, "M", 16, C["text"], 800, "middle")
    return s + '</g>'


def _bar(x: float, y: float, w: float, h: float, frac_one: float, C: dict) -> str:
    w1 = w * frac_one
    return (f'<rect x="{x:g}" y="{y:g}" width="{w1:g}" height="{h:g}" fill="{ONE}"/>'
            f'<rect x="{x + w1:g}" y="{y:g}" width="{w - w1:g}" height="{h:g}" fill="url(#hatch)"/>'
            f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="3" fill="none" stroke="{C["text"]}" stroke-width="2.5"/>')


def kagan_bend(name: str, T: dict) -> str:
    C = chem_theme(T)
    W = 800
    desc = ("Kagan's non-linear effect in three steps and a curve. Step 1: the chiral part of a catalyst, the ligand, is a "
            "mix of 75 per cent one hand and 25 per cent the mirror hand, an excess (ee) of 50 per cent. Step 2: each metal "
            "atom holds two ligands, which pair up by chance: 56 per cent one-hand pairs, 38 per cent mixed pairs and 6 per "
            "cent mirror pairs. Step 3: the mixed pairs barely work and sit out, so the reaction is driven by the other two "
            "in the ratio 56 to 6, which is 90 to 10: the product has an 80 per cent excess of one hand. A straight line "
            "would have given 50 per cent. Below, a sketch of the curve, shape only: the product's ee against the ligand's ee, "
            "with the straight line that chemists expected, the curve bulging above it (a positive non-linear effect, with "
            "the example at 50 per cent in and 80 per cent out) and a curve that sags below it when the mixed pair works "
            "faster (a negative effect). The numbers follow the worked example in the Nobel Committee's popular science "
            "background. Our own drawing.")
    s_title, ty = chem_title(W, "Kagan’s bend", "A catalyst made from a mix of both hands does not add up in a straight line", C)
    px, pw = 36, W - 72
    ill_w = 268                         # illustration column inside each step panel
    tx = px + ill_w + 30                # text column
    tw_ = px + pw - tx - 24
    steps = [
        ("1", "Mix the hands", "The chiral part of the catalyst, the ligand, is 75% one hand and 25% the mirror hand: an excess (ee) of 50%."),
        ("2", "They pair up", "Each metal atom (M) holds two ligands, chosen by chance: 56% one-hand pairs, 38% mixed pairs, 6% mirror pairs."),
        ("3", "Mixed pairs sit out", "The mixed pair barely works. The other two drive the reaction, 56 to 6, which is 90 to 10: an 80% excess of one hand."),
    ]
    y = ty + 36
    s_body = ""
    for i, (num, ttl, cap) in enumerate(steps):
        cl = wrap(cap, 20, tw_)
        h = max(176, 74 + len(cl) * 27 + 20)
        s_body += chem_panel(px, y, pw, h, C)
        s_body += step_badge(tx + 18, y + 40, num, C) + text(tx + 50, y + 49, ttl, 26, C["text"], 800)
        s_body += para(tx, y + 88, cl, 20, C["muted"], 27)
        cx, cy = px + 24 + ill_w / 2, y + h / 2
        if i == 0:
            k = 0
            for r_ in range(4):
                for c_ in range(5):
                    hand = "one" if k < 15 else "mirror"
                    s_body += (f'<circle cx="{cx - 88 + c_ * 44:g}" cy="{cy - 54 + r_ * 30:g}" r="12" fill="{hand_fill(hand)}" '
                               f'stroke="{C["text"]}" stroke-width="2"/>')
                    k += 1
            s_body += text(cx, cy + 82, "75 : 25", 22, C["text"], 800, "middle")
        if i == 1:
            for k, (a, b, pct, lab) in enumerate((("one", "one", "56%", ""), ("one", "mirror", "38%", "mixed"),
                                                   ("mirror", "mirror", "6%", ""))):
                gx = cx - 86 + k * 86
                s_body += _pair(gx, cy - 18, a, b, C)
                s_body += text(gx, cy + 30, pct, 23, C["text"], 800, "middle")
                if lab:
                    s_body += text(gx, cy + 56, lab, 18, C["muted"], 700, "middle")
        if i == 2:
            s_body += _pair(cx - 86, cy - 44, "one", "one", C)
            s_body += _pair(cx, cy - 44, "one", "mirror", C, grey=True, faded=True)
            s_body += f'<line x1="{cx - 40}" y1="{cy - 70}" x2="{cx + 40}" y2="{cy - 18}" stroke="{C["muted"]}" stroke-width="3.5" stroke-linecap="round"/>'
            s_body += _pair(cx + 86, cy - 44, "mirror", "mirror", C)
            s_body += _bar(cx - 112, cy + 2, 224, 26, 0.9, C)
            s_body += text(cx - 112, cy + 56, "90 : 10", 21, C["text"], 800)
            s_body += text(cx + 112, cy + 56, "ee 80%", 21, C["one_text"], 800, "end")
        y += h + 16
    # the curve
    ch_top = y
    plot_x, plot_w, plot_h = px + 92, 360, 300
    plot_y = ch_top + 70
    ch_h = plot_h + 70 + 92
    s_body += chem_panel(px, ch_top, pw, ch_h, C)
    s_body += text(px + 28, ch_top + 46, "The curve", 26, C["text"], 800)
    tagw = tw("shape only", 18, True) + 26
    s_body += (f'<rect x="{px + 168}" y="{ch_top + 22}" width="{tagw:.0f}" height="32" rx="16" fill="{C["chip"]}" stroke="{C["border"]}" stroke-width="2"/>'
               + text(px + 168 + tagw / 2, ch_top + 44, "shape only", 18, C["muted"], 800, "middle"))
    X = lambda v: plot_x + v * plot_w
    Y = lambda v: plot_y + plot_h - v * plot_h
    s_body += (f'<rect x="{plot_x}" y="{plot_y}" width="{plot_w}" height="{plot_h}" fill="{C["bg"]}" fill-opacity=".55"/>'
               f'<path d="M{plot_x} {plot_y} V{plot_y + plot_h} H{plot_x + plot_w}" fill="none" stroke="{C["text"]}" stroke-width="3"/>')
    for v, lab in ((0, "0%"), (0.5, "50%"), (1, "100%")):
        s_body += text(X(v), plot_y + plot_h + 28, lab, 18, C["muted"], 600, "middle")
        s_body += text(plot_x - 10, Y(v) + 6, lab, 18, C["muted"], 600, "end")
    s_body += text(X(0.5), plot_y + plot_h + 58, "lead of one hand in the ligand (ee)", 20, C["text"], 700, "middle")
    s_body += text(plot_x - 62, Y(0.5), "lead in the product (ee)", 20, C["text"], 700, "middle",
                   f'transform="rotate(-90 {plot_x - 62} {Y(0.5):g})"')
    def curve(f):
        pts = [(X(k / 60), Y(f(k / 60))) for k in range(61)]
        return "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in pts)
    # ML2 with chance pairing: beta = (1 - x^2) / (1 + x^2); ee = x (1 + beta) / (1 + g beta)
    def ml2(g):
        return lambda x: x * (1 + (1 - x * x) / (1 + x * x)) / (1 + g * (1 - x * x) / (1 + x * x))
    s_body += f'<path d="{curve(ml2(2.5))}" fill="none" stroke="{C["mixed"]}" stroke-width="3.5" stroke-dasharray="2 7" stroke-linecap="round"/>'
    s_body += f'<line x1="{X(0)}" y1="{Y(0)}" x2="{X(1)}" y2="{Y(1)}" stroke="{C["text"]}" stroke-width="3" stroke-dasharray="12 8"/>'
    s_body += f'<path d="{curve(ml2(0))}" fill="none" stroke="{ONE}" stroke-width="5.5" stroke-linecap="round"/>'
    s_body += f'<line x1="{X(.5)}" y1="{Y(.5)}" x2="{X(.5)}" y2="{Y(.8)}" stroke="{C["text"]}" stroke-width="2" stroke-dasharray="3 5"/>'
    s_body += f'<circle cx="{X(.5)}" cy="{Y(.5)}" r="7" fill="{C["panel"]}" stroke="{C["muted"]}" stroke-width="3"/>'
    s_body += f'<circle cx="{X(.5)}" cy="{Y(.8)}" r="9" fill="{ONE}" stroke="{C["panel"]}" stroke-width="3"/>'
    # labels to the right of the plot
    lx = plot_x + plot_w + 34
    lw = px + pw - 22 - lx
    def label(yy, col, title_, body):
        out = text(lx, yy, title_, 21, col, 800)
        bl = wrap(body, 18, lw)
        out += para(lx, yy + 25, bl, 18, C["muted"], 24)
        return out, yy + 25 + len(bl) * 24 + 16
    o, ny = label(plot_y + 12, C["one_text"], "Kagan’s bend", "The mixed pair is slow: the product beats the straight line. Our example: 50% in, 80% out.")
    s_body += o
    o, ny = label(ny, C["text"], "Straight line", "What chemists expected: 50% in, 50% out.")
    s_body += o
    o, ny = label(ny, C["muted"], "Bend below", "If the mixed pair is faster, the curve sags under the line.")
    s_body += o
    y = ch_top + ch_h + 40
    foot, end = chem_footer(W, y, [
        ("Kagan reported this non-linear effect in 1986. Before that, chemists assumed that a ligand with a 50% "
         "lead of one hand gives a product with a 50% lead.", True),
        ("Simplified: the numbers follow the worked example in the Nobel Committee’s popular science background, "
         "with the mixed pair doing nothing and the two same-hand pairs equally good. Our own drawing.", False),
    ], C)
    H = end + 34
    s = svg_open(W, H, "Kagan’s bend: a mixed-hand catalyst beats a straight line", desc, T)
    s += chem_defs(C) + chem_bg(W, H, C) + s_title + s_body + foot
    s += SVG_CLOSE
    return s


# ---------------------------------------------------------------- chemistry: Soai's copier
def soai_copier(name: str, T: dict) -> str:
    import random
    C = chem_theme(T)
    W = 800
    desc = ("How Soai's reaction copies one hand, and his group's 2003 numbers. Top, the copier: grey dots are a simple "
            "ingredient with no hand; a molecule with one hand, solid orange, turns an ingredient into a new molecule of "
            "its own hand, so 1 molecule becomes 2, and 2 become 4. Middle, a bar chart of the lead of one hand (ee) in "
            "three runs in a row, Soai's group, 2003: the start, 0.00005 per cent, too small to draw (one hand ahead by "
            "about one molecule in two million); after run 1, 57 per cent; after run 2, 99 per cent; after run 3, more "
            "than 99.5 per cent. Bottom: with no head start at all, 37 runs: 19 gave one hand and 18 the other, with a "
            "lead between 15 and 91 per cent, never one hand only; the hand was chosen at random. Why the reaction "
            "amplifies the lead is still debated. The tokens are symbols, not real molecules. Our own drawing.")
    s_title, ty = chem_title(W, "Soai’s copier", "A molecule that makes copies of its own hand", C)
    px, pw = 36, W - 72
    y = ty + 36
    s_body = ""
    # --- the copier: autocatalysis only (1 -> 2 -> 4); no claim about how the other hand is held back
    mh = 330
    s_body += chem_panel(px, y, pw, mh, C)
    s_body += text(px + 28, y + 46, "Each copy makes another copy", 26, C["text"], 800)
    s_body += para(px + 28, y + 76, wrap("A molecule of one hand turns a simple ingredient into a new molecule "
                                         "of the same hand.", 19, pw - 56), 19, C["muted"], 25, 600)
    def ingredient(x, yy):
        return f'<circle cx="{x:g}" cy="{yy:g}" r="9" fill="{C["mixed"]}" stroke="{C["panel"]}" stroke-width="2"/>'
    cy = y + 186
    r_ = 17
    # 1
    gx1 = px + 70
    s_body += token(gx1, cy, r_, "one", C)
    s_body += text(px + 118, cy + 10, "+", 30, C["text"], 800, "middle")
    s_body += ingredient(px + 148, cy)
    s_body += chem_arrow(px + 172, cy, px + 226, cy, C["muted"])
    # 2
    gx2 = px + 262
    s_body += token(gx2, cy - 22, r_, "one", C) + token(gx2, cy + 22, r_, "one", C)
    s_body += text(px + 310, cy + 10, "+", 30, C["text"], 800, "middle")
    s_body += ingredient(px + 340, cy - 16) + ingredient(px + 340, cy + 16)
    s_body += chem_arrow(px + 364, cy, px + 418, cy, C["muted"])
    # 4
    gx4 = px + 476
    for dx in (-22, 22):
        for dy in (-22, 22):
            s_body += token(gx4 + dx, cy + dy, r_, "one", C)
    s_body += chem_arrow(px + 530, cy, px + 584, cy, C["muted"])
    s_body += text(px + 600, cy + 9, "8, 16 …", 24, C["one_text"], 800)
    for gx, n in ((gx1, "1"), (gx2, "2"), (gx4, "4")):
        s_body += text(gx, cy + 70, n, 24, C["text"], 800, "middle")
    # legend
    ly = y + mh - 34
    s_body += ingredient(px + 40, ly - 6) + text(px + 58, ly, "simple ingredient, no hand", 18, C["muted"], 700)
    lx2 = px + 58 + tw("simple ingredient, no hand", 18, True) + 40
    s_body += token(lx2, ly - 6, 11, "one", C) + text(lx2 + 20, ly, "molecule of one hand", 18, C["muted"], 700)
    y += mh + 16
    # --- the 2003 bars
    bh_top = y
    plot_x, plot_w, plot_h = px + 112, 520, 250
    plot_y = bh_top + 136
    bh = plot_h + 136 + 128
    s_body += chem_panel(px, bh_top, pw, bh, C)
    s_body += text(px + 28, bh_top + 46, "Three runs in a row", 26, C["text"], 800)
    s_body += text(px + 28, bh_top + 74, "Soai’s group, 2003: the lead of one hand (ee) after each run", 19, C["muted"], 600)
    Y = lambda v: plot_y + plot_h - v / 100 * plot_h
    for v in (0, 50, 100):
        s_body += f'<line x1="{plot_x}" y1="{Y(v):.1f}" x2="{plot_x + plot_w}" y2="{Y(v):.1f}" stroke="{C["rule"]}" stroke-width="2"/>'
        s_body += text(plot_x - 12, Y(v) + 6, f"{v}%", 18, C["muted"], 600, "end")
    bars = (("start", 0.00005, "0.00005%"), ("run 1", 57, "57%"), ("run 2", 99, "99%"), ("run 3", 99.5, ">99.5%"))
    bw, gap = 66, (plot_w - 4 * 66) / 4
    for k, (lab, v, vl) in enumerate(bars):
        bx = plot_x + gap / 2 + k * (bw + gap)
        if k == 0:
            s_body += f'<rect x="{bx:.1f}" y="{Y(0) - 3:.1f}" width="{bw}" height="3" fill="{ONE}"/>'
        else:
            s_body += f'<rect x="{bx:.1f}" y="{Y(v):.1f}" width="{bw}" height="{Y(0) - Y(v):.1f}" rx="4" fill="{ONE}"/>'
            s_body += text(bx + bw / 2, Y(v) - 10, vl, 20, C["text"], 800, "middle")
        s_body += text(bx + bw / 2, Y(0) + 28, lab, 19, C["text"], 700, "middle")
    s_body += f'<line x1="{plot_x}" y1="{Y(0)}" x2="{plot_x + plot_w}" y2="{Y(0)}" stroke="{C["text"]}" stroke-width="3"/>'
    # the callout for the start bar, under the axis
    b0 = plot_x + gap / 2 + bw / 2
    cy_ = Y(0) + 70
    s_body += f'<path d="M{b0:.1f} {Y(0) + 38:.1f} V{cy_ - 6:.1f}" stroke="{C["muted"]}" stroke-width="2" stroke-dasharray="3 4"/>'
    s_body += f'<circle cx="{b0:.1f}" cy="{Y(0) - 3:.1f}" r="7" fill="none" stroke="{C["muted"]}" stroke-width="2"/>'
    s_body += (f'<text x="{b0 - 30:.1f}" y="{cy_ + 14:.1f}" font-size="19" fill="{C["muted"]}" font-weight="600">'
               f'<tspan fill="{C["one_text"]}" font-weight="800">Start, 0.00005%: too small to draw.</tspan></text>')
    s_body += text(b0 - 30, cy_ + 40, "One hand was ahead by about 1 molecule in 2 million.", 19, C["muted"], 600)
    y = bh_top + bh + 16
    # --- no head start
    nh_top = y
    nh = 222
    s_body += chem_panel(px, nh_top, pw, nh, C)
    s_body += text(px + 28, nh_top + 46, "No head start at all", 26, C["text"], 800)
    s_body += text(px + 28, nh_top + 74, "37 runs with nothing added to choose a hand", 19, C["muted"], 600)
    runs = ["one"] * 19 + ["mirror"] * 18
    random.Random(2003).shuffle(runs)
    for k, hnd in enumerate(runs):
        rx, ry = px + 46 + (k % 19) * 36.5, nh_top + 110 + (k // 19) * 40
        s_body += token(rx, ry + 4, 11, hnd, C)
    s_body += text(px + pw - 28, nh_top + 46, "19 one hand · 18 the other", 19, C["text"], 800, "end")
    s_body += text(px + 28, nh_top + 196, "Each run ended between 15% and 91% ee: a lead, never one hand only.", 19, C["muted"], 700)
    y = nh_top + nh + 40
    foot, end = chem_footer(W, y, [
        ("Each molecule makes more of its own hand. Copying alone does not explain why the lead grows; "
         "how the reaction amplifies it is still debated.", True),
        ("ee, the lead of one hand: % of one hand minus % of the other; 0% is an even mix, 100% is one hand only. "
         "Numbers: Soai and co-workers, 2003, as given in the Nobel Committee’s scientific background. "
         "The tokens are symbols, not real molecules. Our own drawing.", False),
    ], C)
    H = end + 34
    s = svg_open(W, H, "Soai’s copier: a molecule that makes copies of its own hand", desc, T)
    s += chem_defs(C) + chem_bg(W, H, C) + s_title + s_body + foot
    s += SVG_CLOSE
    return s


# ---------------------------------------------------------------- station icons (work on light and dark pages)
def icons() -> dict[str, str]:
    slate, blue, amber, teal, coral = "#64748B", "#3B82F6", "#F59E0B", "#14B8A6", "#F43F5E"
    def wrap_icon(title, body):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96" role="img" aria-labelledby="t">'
                f'<title id="t">{esc(title)}</title>{body}</svg>\n')
    out = {}
    out["station-switch"] = wrap_icon("Icon: a light switch turned on",
        f'<rect x="10" y="34" width="76" height="40" rx="20" fill="none" stroke="{slate}" stroke-width="5"/>'
        f'<circle cx="64" cy="54" r="14" fill="{blue}"/>'
        f'<g stroke="{blue}" stroke-width="5" stroke-linecap="round"><line x1="48" y1="8" x2="48" y2="20"/><line x1="26" y1="14" x2="32" y2="23"/><line x1="70" y1="14" x2="64" y2="23"/></g>')
    out["station-depth"] = wrap_icon("Icon: a beam of light fading as it goes deeper",
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{blue}" stop-opacity=".95"/><stop offset="1" stop-color="{blue}" stop-opacity=".05"/></linearGradient></defs>'
        f'<rect x="12" y="10" width="72" height="76" rx="12" fill="none" stroke="{slate}" stroke-width="5"/>'
        f'<polygon points="40,14 56,14 76,80 20,80" fill="url(#g)"/>'
        f'<g stroke="{slate}" stroke-width="4" stroke-linecap="round"><line x1="84" y1="30" x2="92" y2="30"/><line x1="84" y1="50" x2="92" y2="50"/><line x1="84" y1="70" x2="92" y2="70"/></g>')
    out["station-heat"] = wrap_icon("Icon: a thermometer",
        f'<rect x="38" y="8" width="20" height="56" rx="10" fill="none" stroke="{slate}" stroke-width="5"/>'
        f'<circle cx="48" cy="72" r="16" fill="{amber}" stroke="{slate}" stroke-width="5"/>'
        f'<rect x="44.5" y="30" width="7" height="42" rx="3.5" fill="{amber}"/>'
        f'<g stroke="{amber}" stroke-width="4.5" stroke-linecap="round"><line x1="70" y1="22" x2="82" y2="22"/><line x1="70" y1="36" x2="86" y2="36"/><line x1="70" y1="50" x2="82" y2="50"/></g>')
    out["station-page"] = wrap_icon("Icon: a web page with a slider",
        f'<rect x="8" y="14" width="80" height="68" rx="10" fill="none" stroke="{slate}" stroke-width="5"/>'
        f'<line x1="8" y1="32" x2="88" y2="32" stroke="{slate}" stroke-width="5"/>'
        f'<line x1="22" y1="58" x2="74" y2="58" stroke="{slate}" stroke-width="5" stroke-linecap="round"/>'
        f'<circle cx="52" cy="58" r="9" fill="{teal}"/>'
        f'<circle cx="19" cy="23" r="2.8" fill="{slate}"/><circle cx="29" cy="23" r="2.8" fill="{slate}"/>')
    out["station-video"] = wrap_icon("Icon: a video frame with a play button",
        f'<rect x="8" y="18" width="80" height="60" rx="12" fill="none" stroke="{slate}" stroke-width="5"/>'
        f'<polygon points="40,34 40,62 64,48" fill="{coral}"/>')
    # physics
    out["station-cone"] = wrap_icon("Icon: a cone of blue light behind a fast particle",
        f'<defs><linearGradient id="g" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="{blue}" stop-opacity=".7"/><stop offset="1" stop-color="{blue}" stop-opacity="0"/></linearGradient></defs>'
        f'<polygon points="70,48 26,10 26,86" fill="url(#g)"/>'
        f'<g stroke="{blue}" stroke-width="5" stroke-linecap="round"><line x1="70" y1="48" x2="28" y2="12"/><line x1="70" y1="48" x2="28" y2="84"/></g>'
        f'<line x1="8" y1="48" x2="68" y2="48" stroke="{coral}" stroke-width="5" stroke-linecap="round"/>'
        f'<circle cx="72" cy="48" r="7" fill="{coral}"/><polygon points="94,48 82,41 82,55" fill="{coral}"/>')
    # strings of sensors; the ones near the particle track are lit
    strings, sens = (22, 48, 74), (16, 36, 56, 76)
    t0, t1 = (8.0, 14.0), (88.0, 80.0)
    L = ((t1[0] - t0[0]) ** 2 + (t1[1] - t0[1]) ** 2) ** 0.5
    ux, uy = (t1[0] - t0[0]) / L, (t1[1] - t0[1]) / L
    body = f'<g stroke="{slate}" stroke-width="4" stroke-linecap="round">' + "".join(
        f'<line x1="{sx}" y1="6" x2="{sx}" y2="88"/>' for sx in strings) + '</g>'
    body += f'<line x1="{t0[0]:g}" y1="{t0[1]:g}" x2="{t1[0]:g}" y2="{t1[1]:g}" stroke="{coral}" stroke-width="4" stroke-linecap="round"/>'
    for sx in strings:
        for sy in sens:
            d = abs((sx - t0[0]) * uy - (sy - t0[1]) * ux)
            if d < 11:
                body += f'<circle cx="{sx}" cy="{sy}" r="7.5" fill="{blue}"/>'
            else:
                body += f'<circle cx="{sx}" cy="{sy}" r="5" fill="{slate}"/>'
    out["station-telescope"] = wrap_icon("Icon: strings of light sensors, the ones near a particle track lit up", body)
    out["station-kilometre"] = wrap_icon("Icon: a cube of ice dotted with sensors",
        f'<g fill="none" stroke="{slate}" stroke-width="5" stroke-linejoin="round">'
        f'<polygon points="10,34 58,34 58,84 10,84"/><polyline points="10,34 34,12 84,12 58,34"/><polyline points="84,12 84,62 58,84"/></g>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="{blue}"/>' for x in (22, 34, 46) for y in (47, 59, 71)))
    import math
    a0, a1, r = math.radians(-62), math.radians(-118), 38
    sx, sy = 48 + r * math.cos(a0), 48 + r * math.sin(a0)
    ex, ey = 48 + r * math.cos(a1), 48 + r * math.sin(a1)
    tx, ty = -math.sin(a1), math.cos(a1)          # direction of travel at the end (clockwise)
    tip = (ex + tx * 9, ey + ty * 9)
    head = (f'<polygon points="{tip[0]:.1f},{tip[1]:.1f} {ex - ty * 8:.1f},{ey + tx * 8:.1f} '
            f'{ex + ty * 8:.1f},{ey - tx * 8:.1f}" fill="{slate}"/>')
    out["station-replay"] = wrap_icon("Icon: a burst of coloured dots inside a replay arrow",
        f'<path d="M{sx:.1f} {sy:.1f} A{r} {r} 0 1 1 {ex:.1f} {ey:.1f}" fill="none" stroke="{slate}" stroke-width="5" stroke-linecap="round"/>'
        + head
        + "".join(f'<circle cx="{x}" cy="{y}" r="{rr}" fill="{c}"/>' for x, y, rr, c in (
            (27, 54, 3.5, blue), (69, 44, 3.5, blue), (51, 27, 3.5, blue), (44, 70, 3.5, blue),
            (62, 34, 4.5, teal), (34, 62, 4.5, teal), (33, 38, 6, amber), (62, 59, 6, amber), (48, 48, 9, coral))))
    # chemistry: one hand burnt orange and solid, the mirror hand teal and hatched
    hatch = (f'<defs><pattern id="h" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             f'<rect width="7" height="7" fill="{MIRROR}"/><line x1="1" y1="0" x2="1" y2="7" stroke="#FFFFFF" '
             f'stroke-width="2" stroke-opacity=".6"/></pattern></defs>')
    def blob(x, y, r, fill, side):
        kx = x + side * r * 0.75
        return (f'<circle cx="{kx:g}" cy="{y - r * 0.68:g}" r="{r * .5:g}" fill="{fill}"/>'
                f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{fill}"/>')
    out["station-mirror"] = wrap_icon("Icon: a molecule and its mirror image on either side of a dashed mirror line",
        hatch + f'<line x1="48" y1="6" x2="48" y2="90" stroke="{slate}" stroke-width="4" stroke-dasharray="7 6" stroke-linecap="round"/>'
        + f'<g stroke="{slate}" stroke-width="4" stroke-linecap="round"><line x1="26" y1="50" x2="12" y2="70"/><line x1="26" y1="50" x2="38" y2="68"/>'
          f'<line x1="70" y1="50" x2="84" y2="70"/><line x1="70" y1="50" x2="58" y2="68"/></g>'
        + blob(26, 46, 12, ONE, 1) + blob(70, 46, 12, "url(#h)", -1)
        + f'<circle cx="12" cy="72" r="6" fill="{slate}"/><circle cx="38" cy="70" r="6" fill="{slate}"/>'
          f'<circle cx="84" cy="72" r="6" fill="{slate}"/><circle cx="58" cy="70" r="6" fill="{slate}"/>')
    pts = []
    for k in range(25):
        xx = k / 24
        pts.append(f"{12 + xx * 72:.1f} {84 - 2 * xx / (1 + xx * xx) * 72:.1f}")
    out["station-kagan"] = wrap_icon("Icon: a curve bulging above a straight dashed line",
        f'<path d="M12 8 V84 H88" fill="none" stroke="{slate}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<line x1="12" y1="84" x2="84" y2="12" stroke="{slate}" stroke-width="4" stroke-dasharray="6 6"/>'
        f'<path d="M{" L".join(pts)}" fill="none" stroke="{ONE}" stroke-width="6" stroke-linecap="round"/>')
    out["station-soai"] = wrap_icon("Icon: an orange molecule making two copies of itself",
        blob(20, 52, 12, ONE, 1)
        + f'<line x1="36" y1="50" x2="50" y2="50" stroke="{slate}" stroke-width="5" stroke-linecap="round"/>'
          f'<polygon points="58,50 48,43 48,57" fill="{slate}"/>'
        + blob(74, 30, 11, ONE, 1) + blob(74, 74, 11, ONE, 1))
    out["station-race"] = wrap_icon("Icon: an orange dot and a hatched teal dot racing to a finish line, the orange one ahead",
        hatch + f'<line x1="88" y1="8" x2="88" y2="88" stroke="{slate}" stroke-width="4" stroke-dasharray="6 5" stroke-linecap="round"/>'
        + f'<g stroke="{slate}" stroke-width="4" stroke-linecap="round">'
          f'<line x1="8" y1="26" x2="36" y2="26"/><line x1="16" y1="38" x2="40" y2="38"/>'
          f'<line x1="8" y1="62" x2="20" y2="62"/><line x1="12" y1="74" x2="24" y2="74"/></g>'
        + f'<circle cx="62" cy="32" r="16" fill="{ONE}"/><circle cx="40" cy="68" r="14" fill="url(#h)"/>')
    # peace (the Peace page's amber)
    brass = "#D9883F"
    out["station-endings"] = wrap_icon("Icon: bars by decade with a dashed line rising above them",
        f'<path d="M10 8 V86 H90" fill="none" stroke="{slate}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
        + "".join(f'<rect x="{x}" y="{86 - h}" width="11" height="{h}" rx="2" fill="{brass}"/>'
                  for x, h in ((18, 22), (34, 26), (50, 34), (66, 30), (80, 18)))
        + f'<polyline points="23,66 39,62 55,46 71,24 85,22" fill="none" stroke="{slate}" stroke-width="4" '
          f'stroke-dasharray="6 5" stroke-linecap="round" stroke-linejoin="round"/>')
    out["station-hold"] = wrap_icon("Icon: a falling step curve with a dot marking one point on it",
        f'<path d="M10 8 V86 H90" fill="none" stroke="{slate}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M12 16 H26 V36 H38 V46 H50 V52 H66 V56 H88" fill="none" stroke="{brass}" stroke-width="5" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f'<line x1="44" y1="30" x2="44" y2="66" stroke="{slate}" stroke-width="4" stroke-linecap="round"/>'
        f'<circle cx="44" cy="46" r="7" fill="{brass}" stroke="{slate}" stroke-width="3"/>')
    return out


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "icons").mkdir(exist_ok=True)
    made = []
    for variant, T in THEMES.items():
        for stem, fn in (("hero", hero), ("diagram-timeline", timeline),
                         ("diagram-light-gated-channel", channel), ("diagram-credit-map", credit),
                         ("diagram-neutrino-telescope", telescope), ("diagram-icecube-scale", icecube_scale),
                         ("diagram-mirror-hands", mirror_hands), ("diagram-kagan-bend", kagan_bend),
                         ("diagram-soai-copier", soai_copier)):
            p = ASSETS / f"{stem}-{variant}.svg"
            p.write_text(fn(stem, T), encoding="utf-8")
            made.append(p)
    for stem, body in icons().items():
        p = ASSETS / "icons" / f"{stem}.svg"
        p.write_text(body, encoding="utf-8")
        made.append(p)
    for p in made:
        print("wrote", p.relative_to(ROOT))


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3 and sys.argv[1] == "--og":
        # The 1200 x 630 share image's source (dark). Render it to assets/og-lab.jpg with a headless browser.
        pathlib.Path(sys.argv[2]).write_text(hero("og", THEMES["dark"], og=True), encoding="utf-8")
    else:
        main()
