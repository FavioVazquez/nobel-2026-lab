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
    ),
    "light": dict(
        bg="#F4F7FC", bg2="#E6EEFA", panel="#FFFFFF", border="#C6D3EA", text="#14213D",
        muted="#44557A", blue="#1A62D3", violet="#5A45C4", amber="#A85900", teal="#07785F",
        coral="#C23A22", rail="#C1CEE6", membrane="#DCE5F5", membrane_edge="#98ACD4",
        protein="#7A66E0", tissue1="#E3ECFA", tissue2="#D1DEF4", dots="#7C90B8",
        fibre="#7186AD", pill="#DCE8FB", pill_text="#17356E", cone="#2A74E8",
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
def hero(name: str, T: dict) -> str:
    W, H = 1600, 560
    alt = ("nobel-2026-lab. Educational demos of this year's Nobel Prizes. A fibre tip shines blue light "
           "into a block of tissue, the light fades with depth, a warm halo of heat sits at the tip, "
           "and a trace of nerve spikes runs below. Toy models, not research.")
    s = svg_open(W, H, "nobel-2026-lab: hands-on demos of the 2026 Nobel Prizes", alt, T, extra_style=(
        ".pulse{animation:pulse 5s ease-in-out infinite}"
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.72}}"
        ".warm{animation:warm 6s ease-in-out infinite}"
        "@keyframes warm{0%,100%{opacity:.9}50%{opacity:.55}}"
        ".spk{stroke-dasharray:220 1180;stroke-dashoffset:220;animation:draw 7s linear infinite}"
        "@keyframes draw{0%{stroke-dashoffset:220}100%{stroke-dashoffset:-1180}}"
    ))
    s += (
        f'<defs>'
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T["bg"]}"/>'
        f'<stop offset="1" stop-color="{T["bg2"]}"/></linearGradient>'
        f'<pattern id="dots" width="32" height="32" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1.6" fill="{T["dots"]}" fill-opacity=".28"/></pattern>'
        f'<linearGradient id="tis" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T["tissue1"]}"/>'
        f'<stop offset="1" stop-color="{T["tissue2"]}"/></linearGradient>'
        f'<linearGradient id="cone" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{T["cone"]}" stop-opacity=".85"/>'
        f'<stop offset="1" stop-color="{T["cone"]}" stop-opacity="0"/></linearGradient>'
        f'<radialGradient id="glow" cx="0.5" cy="0" r="1"><stop offset="0" stop-color="{T["cone"]}" stop-opacity=".75"/>'
        f'<stop offset=".45" stop-color="{T["cone"]}" stop-opacity=".22"/>'
        f'<stop offset="1" stop-color="{T["cone"]}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="heat" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{T["amber"]}" stop-opacity=".8"/>'
        f'<stop offset="1" stop-color="{T["amber"]}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="tclip"><rect x="900" y="190" width="600" height="300" rx="26"/></clipPath>'
        f'</defs>'
    )
    s += f'<rect width="{W}" height="{H}" rx="30" fill="url(#bg)"/><rect width="{W}" height="{H}" rx="30" fill="url(#dots)"/>'
    s += (f'<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="29" fill="none" stroke="{T["border"]}" stroke-width="3"/>')

    # left text block
    s += text(96, 150, "EDUCATIONAL DEMOS", 26, T["blue"], 700, extra='letter-spacing="5"', fit=362)
    s += text(92, 262, "Nobel 2026 Lab", 104, T["text"], 800, extra='letter-spacing="-2"', fit=742)
    s += text(96, 330, "Hands-on demos of this year\u2019s Nobel Prizes.", 38, T["text"], 500, fit=732)
    s += text(96, 384, "Medicine: a light switch for nerve cells.", 30, T["muted"], 400, fit=492)
    pill = "Toy models \u00b7 not research \u00b7 not for lab or clinical use"
    s += (f'<rect x="96" y="426" width="636" height="58" rx="29" fill="{T["pill"]}" stroke="{T["border"]}" stroke-width="2"/>'
          + text(96 + 30, 463, pill, 25, T["pill_text"], 600, fit=576))

    # tissue block with light, fading glow, heat halo, spikes
    s += (f'<rect x="900" y="190" width="600" height="300" rx="26" fill="url(#tis)" stroke="{T["border"]}" stroke-width="3"/>')
    s += '<g clip-path="url(#tclip)">'
    s += f'<ellipse cx="1200" cy="190" rx="330" ry="285" fill="url(#glow)" class="pulse"/>'
    s += (f'<polygon points="1200,194 1050,480 1350,480" fill="url(#cone)" class="pulse"/>')
    for r, op in ((95, .55), (170, .4), (250, .28)):
        s += (f'<path d="M{1200-r} 190 A{r} {r*0.95:.0f} 0 0 0 {1200+r} 190" fill="none" stroke="{T["cone"]}" '
              f'stroke-opacity="{op}" stroke-width="3" stroke-dasharray="3 9" stroke-linecap="round"/>')
    s += f'<ellipse cx="1200" cy="196" rx="120" ry="80" fill="url(#heat)" class="warm"/>'
    # spike trace along the bottom
    path = ("M915 452 H1010 L1022 452 L1034 372 L1046 470 L1058 452 H1150 L1162 452 L1174 372 L1186 470 L1198 452 "
            "H1290 L1302 452 L1314 372 L1326 470 L1338 452 H1480")
    s += (f'<path d="{path}" fill="none" stroke="{T["coral"]}" stroke-opacity=".55" stroke-width="5" '
          f'stroke-linejoin="round" stroke-linecap="round"/>')
    s += (f'<path d="{path}" fill="none" stroke="{T["coral"]}" stroke-width="6" stroke-linejoin="round" '
          f'stroke-linecap="round" class="spk"/>')
    s += '</g>'
    # fibre
    s += (f'<rect x="1190" y="64" width="20" height="130" rx="6" fill="{T["fibre"]}"/>'
          f'<path d="M1190 194 H1210 L1200 206 Z" fill="{T["fibre"]}"/>')
    # labels
    s += text(1226, 112, "optical fibre", 24, T["muted"], 500)
    s += text(1260, 300, "light", 28, T["blue"], 700)
    s += text(1262, 236, "warmth", 26, T["amber"], 700)
    s += text(1420, 438, "spikes", 26, T["coral"], 700, "middle")
    s += text(1476, 226, "tissue", 22, T["muted"], 500, "end")
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
    return out


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "icons").mkdir(exist_ok=True)
    made = []
    for variant, T in THEMES.items():
        for stem, fn in (("hero", hero), ("diagram-timeline", timeline),
                         ("diagram-light-gated-channel", channel), ("diagram-credit-map", credit)):
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
    main()
