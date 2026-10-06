"""Runs the headless-Chrome page check (tests/test_page.cjs) under pytest. Educational demo, toy model.

Needs Node and Playwright (point NODE_PATH at a node_modules folder that holds playwright). Uses the
installed Google Chrome when CHROME is not set and Chrome is in its default macOS place.
    NODE_PATH=/path/to/node_modules python -m pytest -q tests      (from 2026/medicine/page/)
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PAGE = Path(__file__).resolve().parents[1]
MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def _has_playwright():
    return bool(shutil.which("node")) and subprocess.run(
        ["node", "-e", "require('playwright')"], capture_output=True).returncode == 0


@pytest.mark.skipif(not _has_playwright(), reason="needs Node and Playwright (set NODE_PATH)")
def test_page_in_headless_chrome():
    env = {**os.environ, "PYTHON": os.environ.get("PYTHON", sys.executable)}
    if "CHROME" not in env and Path(MAC_CHROME).exists():
        env["CHROME"] = MAC_CHROME
    r = subprocess.run(["node", "tests/test_page.cjs"], cwd=PAGE, env=env, capture_output=True, text=True, timeout=900)
    print(r.stdout)
    assert r.returncode == 0, r.stdout + r.stderr
