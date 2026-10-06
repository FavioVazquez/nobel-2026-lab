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
# One card per prize, side by side, and a quiet dashed slot for the prizes still to come.
# Colours only the banner uses live here, so the shared THEMES table stays as the diagrams use it.
HERO_EXTRA = {
    "dark": dict(ice1="#13284A", ice2="#091629", ice_top="#26446F", sensor_off="#5D7299",
                 neuron="#B9AEFF", next_fill="#0F1A30"),
    "light": dict(ice1="#E4EEFB", ice2="#C9DAF1", ice_top="#F8FBFF", sensor_off="#8293B6",
                  neuron="#5A45C4", next_fill="#FFFFFF"),
}
CARD_W, CARD_H, WIN_H, NEXT_W, CARD_GAP = 290, 432, 308, 180, 20


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


def _card_next(T: dict, X: dict) -> str:
    """A dashed slot: the prizes still to be announced join here."""
    cx = NEXT_W / 2
    s = (f'<rect x="1.25" y="1.25" width="{NEXT_W - 2.5}" height="{CARD_H - 2.5}" rx="21" fill="{X["next_fill"]}" '
         f'fill-opacity=".55" stroke="{T["dots"]}" stroke-opacity=".75" stroke-width="2.5" stroke-dasharray="10 9"/>')
    s += (f'<circle cx="{cx:g}" cy="104" r="28" fill="none" stroke="{T["muted"]}" stroke-width="3"/>'
          f'<path d="M{cx-12:g} 104 H{cx+12:g} M{cx:g} 92 V116" stroke="{T["muted"]}" stroke-width="3.5" stroke-linecap="round"/>')
    s += text(cx, 178, "NEXT", 18, T["muted"], 800, "middle", 'letter-spacing="3"')
    for y, prize, day in ((236, "Chemistry", "7 Oct"), (336, "Economics", "12 Oct")):
        s += text(cx, y, prize, 25, T["text"], 700, "middle")
        s += text(cx, y + 32, day, 21, T["muted"], 500, "middle")
    s += f'<line x1="{cx-34:g}" y1="292" x2="{cx+34:g}" y2="292" stroke="{T["border"]}" stroke-width="2"/>'
    return s


def _hero_words(T: dict) -> str:
    """The text block, in its own coordinates: 600 wide, from y = 100 to 470."""
    s = text(4, 124, "EDUCATIONAL DEMOS", 24, T["blue"], 700, extra='letter-spacing="5"', fit=334)
    s += text(0, 220, "Nobel 2026 Lab", 84, T["text"], 800, extra='letter-spacing="-2"', fit=599)
    s += text(4, 276, "Hands-on demos of this year’s Nobel Prizes.", 31, T["text"], 500, fit=596)
    pill = "Toy models · not research · not for lab or clinical use"
    s += (f'<rect x="4" y="314" width="559" height="54" rx="27" fill="{T["pill"]}" stroke="{T["border"]}" stroke-width="2"/>'
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
    if og:   # the 1200 x 630 share image: full bleed, everything clear of the outer 40 px
        W, H, rx = 1200, 630, 0
        words = (64, 93, .78)
        cards = (1200 - 64 - .68 * (2 * CARD_W + NEXT_W + 2 * CARD_GAP), (630 - .68 * CARD_H) / 2, .68)
    else:
        W, H, rx = 1600, 560, 30
        words = (88, -6, 1.0)
        cards = (736, 64, 1.0)
    alt = ("Nobel 2026 Lab. Hands-on demos of this year’s Nobel Prizes, one card per prize. Medicine: a nerve cell "
           "lit by a pulse of blue light from the tip of an optical fibre, with a spike running down its axon. Physics: "
           "strings of light sensors hanging in dark ice, a particle track with a cone of blue Cherenkov light behind it, "
           "and the sensors near the track lit up. A third, dashed slot holds the prizes still to come: Chemistry on "
           "7 October and Economics on 12 October. Toy models, not research, not for lab or clinical use. Videos made "
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
    s += _hero_defs(T, X)
    s += f'<rect width="{W}" height="{H}" rx="{rx}" fill="url(#bg)"/><rect width="{W}" height="{H}" rx="{rx}" fill="url(#dots)"/>'
    if not og:
        s += f'<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="{rx-1}" fill="none" stroke="{T["border"]}" stroke-width="3"/>'
    wx, wy, ws = words
    s += f'<g transform="translate({wx:g},{wy:g}) scale({ws:g})">' + _hero_words(T) + '</g>'
    cx0, cy0, cs = cards
    s += f'<g transform="translate({cx0:g},{cy0:g}) scale({cs:g})">'
    s += _card_medicine(T, X)
    s += f'<g transform="translate({CARD_W + CARD_GAP},0)">' + _card_physics(T, X) + '</g>'
    s += f'<g transform="translate({2 * (CARD_W + CARD_GAP)},0)">' + _card_next(T, X) + '</g>'
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
    return out


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "icons").mkdir(exist_ok=True)
    made = []
    for variant, T in THEMES.items():
        for stem, fn in (("hero", hero), ("diagram-timeline", timeline),
                         ("diagram-light-gated-channel", channel), ("diagram-credit-map", credit),
                         ("diagram-neutrino-telescope", telescope), ("diagram-icecube-scale", icecube_scale)):
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
