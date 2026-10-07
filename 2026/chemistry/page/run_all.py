"""One command: rebuild data.js, then check the page in headless Chromium and refresh the screenshots and og.jpg.
Educational demo, toy models; not research.

    python3 -m page.run_all                     # from 2026/chemistry/: ../mirror-race, ../kagan-curve, ../soai-amplifier
    python3 -m page.run_all --from MIRROR_RESULTS KAGAN_DIR AMP_RESULTS
    python3 -m page.run_all --fixtures          # placeholder inputs
    python3 -m page.run_all --no-browser        # only rebuild data.js
"""
import os
import subprocess
import sys
from pathlib import Path

from . import build_data

HERE = Path(__file__).resolve().parent


def main():
    argv = sys.argv[1:]
    browser = "--no-browser" not in argv
    build_data.main([a for a in argv if a != "--no-browser"])
    if browser:
        env = {**os.environ, "PYTHON": sys.executable}
        env.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(Path.home() / ".showtime/browsers"))
        sys.exit(subprocess.run(["node", "tests/test_page.mjs", "--shots", "--og"], cwd=HERE, env=env).returncode)


if __name__ == "__main__":
    main()
