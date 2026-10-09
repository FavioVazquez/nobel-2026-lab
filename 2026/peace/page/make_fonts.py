"""Subset the page's two OFL font families to the characters the page uses and write them to fonts/ as WOFF2.

Educational demos made to show an open-source tool. Not research.

    python3 make_fonts.py --src DIR [DIR ...]      # folders holding the source fonts (see README.md)

Source fonts (both SIL Open Font License 1.1, from github.com/google/fonts, ofl/ibmplexsans and ofl/sourceserif4;
nothing here fetches anything):
  sans, sans-bold  IBMPlexSans[wdth,wght].ttf: body text and numbers (weights 400 and 600)
  serif            SourceSerif4[opsz,wght].ttf: headings and the big numbers (optical size 36, weight 600)
  italic           SourceSerif4-Italic[opsz,wght].ttf: the quoted sentences

Every subset gets a new family name ("Peace Page ..."), because the OFL asks modified fonts not to use a Reserved Font
Name (IBM Plex has one). fonts/OFL.txt holds the licence and each source font's copyright line.
Needs fontTools >= 4.40 (older ones fail on these variable fonts) and brotli for WOFF2. With a fontTools that has no
brotli, the fonts are written as TTF; then run `python3 make_fonts.py --compress` with a Python that has brotli.
"""
import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "fonts"
# key: (source file names in order of preference, new family name, axis values to pin; variable fonts become static)
FACES = {
    "sans": (["IBMPlexSans[wdth,wght].ttf"], "Peace Page Sans", {"wdth": 100, "wght": 400}),
    "sans-bold": (["IBMPlexSans[wdth,wght].ttf"], "Peace Page Sans Bold", {"wdth": 100, "wght": 600}),
    "serif": (["SourceSerif4[opsz,wght].ttf"], "Peace Page Serif", {"opsz": 36, "wght": 600}),
    "italic": (["SourceSerif4-Italic[opsz,wght].ttf"], "Peace Page Serif Italic", {"opsz": 20, "wght": 400}),
}
# always keep these, so text added later in plain ASCII still renders in the right face
BASE = "".join(chr(c) for c in range(0x20, 0x7F)) + " –—‘’“”…·×÷±°§¶•→←↔≈½¼¾¹²³⁰⁴⁵⁶⁷⁸⁹₀₁₂ʼ′″"


def used_chars():
    text = ""
    for f in ("index.html", "data.js"):
        p = HERE / f
        if p.exists():
            text += p.read_text(encoding="utf-8")
    text = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), text)
    return set(text) | set(BASE)


def find(srcs, names):
    for n in names:
        for s in srcs:
            p = Path(s) / n
            if p.exists():
                return p
    return None


def rename(font, family):
    name = font["name"]
    for rec in list(name.names):
        if rec.nameID in (1, 3, 4, 6, 16, 17, 21, 22):
            name.removeNames(nameID=rec.nameID)
    style = "Italic" if "Italic" in family else "Regular"
    ps = family.replace(" ", "") + "-" + style
    for nid, val in ((1, family), (2, style), (3, ps + "-subset"), (4, family + " " + style), (6, ps)):
        name.setName(val, nid, 3, 1, 0x409)


def subset(path, family, chars, out, pin=None):
    from fontTools import subset as fts
    from fontTools.ttLib import TTFont
    font = TTFont(str(path))
    copyright_line = font["name"].getDebugName(0) or ""
    if pin and "fvar" in font:
        from fontTools.varLib import instancer
        axes = {a.axisTag for a in font["fvar"].axes}
        font = instancer.instantiateVariableFont(font, {k: v for k, v in pin.items() if k in axes})
    cmap = font.getBestCmap()
    keep = sorted(ord(c) for c in chars if ord(c) in cmap)
    opts = fts.Options()
    opts.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk", "onum", "lnum", "pnum", "tnum", "frac", "smcp", "c2sc"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    opts.hinting = False
    sub = fts.Subsetter(options=opts)
    sub.populate(unicodes=keep)
    sub.subset(font)
    rename(font, family)
    try:
        import brotli  # noqa: F401
        font.flavor = "woff2"
        font.save(str(out))
    except ImportError:  # this Python has no brotli: write TTF, then run --compress with one that has it
        font.flavor = None
        font.save(str(out.with_suffix(".ttf")))
    return copyright_line, len(keep)


def compress():
    from fontTools.ttLib import woff2
    for p in sorted(OUT.glob("*.ttf")):
        woff2.compress(str(p), str(p.with_suffix(".woff2")))
        p.unlink()
        print(f"  compressed fonts/{p.with_suffix('.woff2').name} ({p.with_suffix('.woff2').stat().st_size / 1024:.1f} KB)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", nargs="+")
    ap.add_argument("--compress", action="store_true", help="only turn fonts/*.ttf into WOFF2 (needs brotli)")
    a = ap.parse_args(argv)
    if a.compress:
        return compress()
    if not a.src:
        ap.error("--src is required")
    chars = used_chars()
    OUT.mkdir(exist_ok=True)
    lines = []
    for key, (names, family, pin) in FACES.items():
        p = find(a.src, names)
        if p is None:
            sys.exit(f"missing source font for {key}: one of {names} in {a.src}")
        cr, n = subset(p, family, chars, OUT / f"{key}.woff2", pin)
        outp = OUT / f"{key}.woff2" if (OUT / f"{key}.woff2").exists() and not (OUT / f"{key}.ttf").exists() else OUT / f"{key}.ttf"
        size = outp.stat().st_size
        print(f"  {key:7s} {p.name:36s} -> fonts/{outp.name} ({n} characters, {size / 1024:.1f} KB)")
        lines.append(f"fonts/{key}.woff2: a subset of {p.name.split('[')[0].split('-latin')[0].replace('-Regular.ttf', '')} "
                     f"renamed \"{family}\". {cr}")
    ofl = (HERE / "fonts" / "OFL-1.1.txt").read_text(encoding="utf-8") if (HERE / "fonts" / "OFL-1.1.txt").exists() else ""
    (OUT / "OFL.txt").write_text(
        "The font files in this folder are subsets of fonts released under the SIL Open Font License, Version 1.1.\n"
        "Each subset has a new family name, as the licence asks of modified fonts.\n\n" + "\n".join(lines) + "\n\n" + ofl,
        encoding="utf-8")
    # which face does the body text use? the page reads this to name it in the footer
    (OUT / "faces.txt").write_text("\n".join(f"{k}: {find(a.src, v[0]).name} {v[2] or ''}" for k, v in FACES.items()) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
