"""One command: rebuild data.js, then check the page in headless Chromium and refresh the screenshots and og.jpg.
Educational demos made to show an open-source tool. Not research.

    python3 -m page.run_all --from SPEND_RESULTS RATE_RESULTS   # from 2026/economics/: the toys' results folders
    python3 -m page.run_all                      # after the merge: ../can-you-predict-spending, ../set-the-rate
    python3 -m page.run_all --fixtures           # the copies in tests/fixtures
    python3 -m page.run_all --no-browser         # only rebuild data.js

The fonts in fonts/ are subsets made by make_fonts.py; rerun it (see README.md) only if the page gains new characters.
"""
import os
import subprocess
import sys
from pathlib import Path

from . import build_data

HERE = Path(__file__).resolve().parent


def shrink():
    """The paper grain makes full-page PNGs large; with Pillow, store them with a 128-colour palette (no dithering)."""
    try:
        from PIL import Image
    except ImportError:
        return
    for p in sorted((HERE / "screenshots").glob("*.png")):
        im = Image.open(p).convert("RGB")
        kw = {"dither": Image.Dither.NONE} if hasattr(Image, "Dither") else {}
        im.quantize(colors=128, method=0, **kw).save(p, optimize=True)


def main():
    argv = sys.argv[1:]
    browser = "--no-browser" not in argv
    build_data.main([a for a in argv if a != "--no-browser"])
    if browser:
        env = {**os.environ, "PYTHON": sys.executable}
        env.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(Path.home() / ".showtime/browsers"))
        code = subprocess.run(["node", "tests/test_page.mjs", "--shots", "--og"], cwd=HERE, env=env).returncode
        shrink()
        sys.exit(code)


if __name__ == "__main__":
    main()
