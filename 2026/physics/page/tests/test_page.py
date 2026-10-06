"""Runs the headless-Chromium page check (tests/test_page.mjs) under pytest. Educational demo, toy models; not research.

Needs Node and playwright-core with a Chromium build. Defaults to showtime's copies
(~/.showtime/node/node_modules/playwright-core and ~/.showtime/browsers); set PLAYWRIGHT_CORE and
PLAYWRIGHT_BROWSERS_PATH to use others.    python3 -m pytest -q tests      (from 2026/physics/page/)
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PAGE = Path(__file__).resolve().parents[1]
HOME = Path.home()
CORE = Path(os.environ.get("PLAYWRIGHT_CORE", HOME / ".showtime/node/node_modules/playwright-core/index.mjs"))
BROWSERS = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", str(HOME / ".showtime/browsers"))


@pytest.mark.skipif(not (shutil.which("node") and CORE.exists()), reason="needs Node and playwright-core (set PLAYWRIGHT_CORE)")
def test_page_in_headless_chromium():
    env = {**os.environ, "PLAYWRIGHT_BROWSERS_PATH": BROWSERS, "PLAYWRIGHT_CORE": str(CORE), "PYTHON": sys.executable}
    r = subprocess.run(["node", "tests/test_page.mjs"], cwd=PAGE, env=env, capture_output=True, text=True, timeout=300)
    print(r.stdout)
    assert r.returncode == 0, r.stdout + r.stderr
