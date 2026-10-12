"""Subset the page's three OFL font families to the characters the page uses and write them to fonts/ as WOFF2.

Educational demos made to show an open-source tool. Not research.

    python3 make_fonts.py --src DIR [DIR ...]      # folders holding the source fonts (see README.md)

Source fonts (all SIL Open Font License 1.1; the Latin variable files of the @fontsource-variable packages fraunces,
inter and jetbrains-mono, the same faces the film uses; nothing here fetches anything):
  sans, sans-bold  inter-latin-wght-normal.woff2: body text (weights 400 and 600)
  serif            fraunces-latin-full-normal.woff2: headings and the big numbers (optical size 48, weight 500)
  italic           fraunces-latin-full-italic.woff2: the accent words of the headings and the quoted sentences
  mono             jetbrains-mono-latin-wght-normal.woff2: kickers, labels and the numbers in the charts (weight 500)

Every subset gets a new family name ("Econ Page ..."), because the OFL asks modified fonts not to use a Reserved Font
Name. fonts/OFL.txt holds the licence and each source font's copyright line.
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
    "sans": (["inter-latin-wght-normal.woff2"], "Econ Page Sans", {"wght": 400}),
    "sans-bold": (["inter-latin-wght-normal.woff2"], "Econ Page Sans Bold", {"wght": 600}),
    "serif": (["fraunces-latin-full-normal.woff2"], "Econ Page Serif", {"opsz": 48, "wght": 500, "SOFT": 0, "WONK": 0}),
    "italic": (["fraunces-latin-full-italic.woff2"], "Econ Page Serif Italic", {"opsz": 48, "wght": 500, "SOFT": 0, "WONK": 0}),
    "mono": (["jetbrains-mono-latin-wght-normal.woff2"], "Econ Page Mono", {"wght": 500}),
}
# always keep these, so text added later in plain ASCII still renders in the right face
BASE = "".join(chr(c) for c in range(0x20, 0x7F)) + " –—‘’“”…·×÷±°§¶•¹²³⁰⁴⁵⁶⁷⁸⁹ʼ′″−"


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
            for p in (Path(s) / n, Path(s) / "files" / n):
                if p.exists():
                    return p
    return None


def rename(font, family):
    name = font["name"]
    for rec in list(name.names):
        if rec.nameID in (1, 3, 4, 6, 16, 17, 21, 22, 25):
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
    opts.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk", "onum", "lnum", "pnum", "tnum", "frac"]
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
        print(f"  {key:9s} {p.name:40s} -> fonts/{outp.name} ({n} characters, {outp.stat().st_size / 1024:.1f} KB)")
        src = re.sub(r"-latin.*$", "", p.stem)
        lines.append(f"fonts/{key}.woff2: a subset of {src} renamed \"{family}\". {cr}")
    ofl = (OUT / "OFL-1.1.txt").read_text(encoding="utf-8") if (OUT / "OFL-1.1.txt").exists() else ""
    (OUT / "OFL.txt").write_text(
        "The font files in this folder are subsets of fonts released under the SIL Open Font License, Version 1.1.\n"
        "Each subset has a new family name, as the licence asks of modified fonts.\n\n" + "\n".join(lines) + "\n\n" + ofl,
        encoding="utf-8")
    (OUT / "faces.txt").write_text("\n".join(f"{k}: {find(a.src, v[0]).name} {v[2] or ''}" for k, v in FACES.items()) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
