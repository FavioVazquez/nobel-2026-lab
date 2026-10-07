"""Run everything: python -m kagan.run_all (from 2026/chemistry/kagan-curve/). Writes results/."""
import argparse
import json

import numpy as np

from . import constants as C
from . import figures as F
from . import model as M


def summary(status="final"):
    e = np.linspace(0, 1, C.CURVE_N_POINTS)
    p = M.pie(C.PIE_LIGAND_ONE_HAND_PCT, C.K_STATISTICAL, 0.0)
    r = lambda v, n=6: [round(float(a), n) for a in v]  # noqa: E731
    k_values = (1.0, 4.0, 25.0, 100.0, 1000.0)
    return {
        "status": status,
        "label": C.LABEL,
        "units": "dimensionless; ee values in per cent unless the key says otherwise; our toy model, trend only",
        "model": "Kagan ML2: x + y + z = 1, x - y = ee_L, K = z^2/(x y); ee_prod = ee_max ee_L (1 + beta)/(1 + g beta),"
                 " beta = z/(1 - z) (SCI eqs. 2-3, p. 7; Buhse 2005 eqs. 3-7)",
        "pie_check": {
            "ligand": r(p["ligand"]),
            "catalysts_pct": r(p["catalysts_pct"]),
            "catalysts_order": ["one-hand pair", "mixed pair", "mirror-hand pair"],
            "effective": r(p["effective"]),
            "ee_prod_pct": round(p["ee_prod_pct"], 6),
            "K": C.K_STATISTICAL, "g": 0.0,
            "source": "Nobel popular information, figure 4 (numbers only; our own drawing)",
        },
        "curves": {
            "K": C.K_STATISTICAL,
            "ee_max": C.EE_MAX,
            "g_values": list(C.G_VALUES),
            "ee_L": r(100 * e, 4),
            "ee_prod": {f"{g:g}": r(100 * M.ee_prod(e, C.K_STATISTICAL, g, C.EE_MAX), 4) for g in C.G_VALUES},
        },
        "curves_g0_by_K": {
            "g": 0.0,
            "ee_L": r(100 * e, 4),
            "ee_prod": {f"{K:g}": r(100 * M.ee_prod(e, K, 0.0), 4) for K in k_values},
            "note": "K = 1: mixed pairs disfavoured; K = 4: random pairing; larger K: mixed pairs favoured",
        },
        "erosion": r([100 * v for v in M.erosion(C.EROSION_EE_MAX, C.EROSION_ROUNDS)], 4),
        "erosion_note": "plain copying, no non-linear effect, ee_max = 90 %: 100 -> 90 -> 81 -> ... (SCI p. 10)",
        "js": "kagan.js gives the same numbers to 1e-9 (tests/test_kagan_js.py)",
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="final")
    ap.add_argument("--no-figures", action="store_true")
    a = ap.parse_args(argv)
    F.RESULTS.mkdir(parents=True, exist_ok=True)
    s = summary(a.status)
    (F.RESULTS / "kagan_summary.json").write_text(json.dumps(s, indent=2) + "\n")
    print("pie:", s["pie_check"])
    print("erosion:", s["erosion"])
    if not a.no_figures:
        for p in F.all_figures():
            print("wrote", p.name)


if __name__ == "__main__":
    main()
