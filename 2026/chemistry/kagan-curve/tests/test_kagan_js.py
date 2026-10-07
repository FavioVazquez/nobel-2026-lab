"""kagan.js must give the same numbers as kagan/model.py to 1e-9. Runs node if it can find it."""
import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from kagan import model as M

HERE = Path(__file__).resolve().parent.parent
NODE = shutil.which("node") or next(
    (p for p in [os.path.expanduser("~/.showtime/node/bin/node")] if os.path.exists(p)), None)

SCRIPT = r"""
const K = require(process.argv[1]);
const ks = [0.5, 4, 25, 1000, Infinity], gs = [0, 0.1, 1, 2, 10], out = {ee: [], pie: K.pie(75, 4, 0),
  erosion: K.erosion(0.9, 6), z: []};
for (const k of ks) for (const g of gs) for (let i = 0; i <= 50; i++) {
  const e = -1 + i / 25;
  out.ee.push([k === Infinity ? "inf" : k, g, e, K.eeProd(e, k, g, 0.9)]);
}
for (const k of ks) for (let i = 0; i <= 20; i++) out.z.push([k === Infinity ? "inf" : k, i / 20, K.mixedFraction(i / 20, k)]);
console.log(JSON.stringify(out));
"""


@pytest.mark.skipif(NODE is None, reason="node not found")
def test_js_matches_python():
    res = subprocess.run([NODE, "-e", SCRIPT, str(HERE / "kagan.js")], capture_output=True, text=True, check=True,
                         timeout=30)
    out = json.loads(res.stdout)
    worst = 0.0
    for k, g, e, v in out["ee"]:
        k = float(k)
        worst = max(worst, abs(v - float(M.ee_prod(e, k, g, 0.9))))
    for k, e, v in out["z"]:
        worst = max(worst, abs(v - float(M.mixed_fraction(e, float(k)))))
    assert worst < 1e-9
    p = M.pie(75.0, 4.0, 0.0)
    assert np.allclose(out["pie"]["catalystsPct"], p["catalysts_pct"], atol=1e-9)
    assert np.allclose(out["pie"]["effective"], p["effective"], atol=1e-9)
    assert out["pie"]["eeProdPct"] == pytest.approx(80.0, abs=1e-9)
    assert np.allclose(out["erosion"], [100 * v for v in M.erosion(0.9, 6)], atol=1e-9)
