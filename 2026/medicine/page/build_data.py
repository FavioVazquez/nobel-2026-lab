"""Build page/data.js from the simulator's precomputed results (educational demo, toy model).

Reads 2026/medicine/results/{run_summary.json, tradeoff.csv, light_fibre200um_<nm>nm.npz} and, with
--recruitment, the heat budget's heat-budget/results/recruitment.json. Writes page/data.js, a plain script
that sets window.NOBEL_MED_DATA, so index.html works from file:// with no server and no network.
Every number the page's text states comes from here (nothing is hard-coded in index.html).

    python3 build_data.py --recruitment            # from 2026/medicine/page/: with the bonus panel
    python3 build_data.py                          # without the bonus panel
    python3 build_data.py --recruitment other.json --out /tmp/data.js   # try a different recruitment file
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
RECRUITMENT = HERE.parent / "heat-budget" / "results" / "recruitment.json"
HEADLINE_COLOURS = ("470", "590")  # the red (635 nm) recruitment result is shown only as a labelled toy upper bound
COLOURS = ("470", "590", "635")
SWITCHES = ("ChR2 (Williams 2013)", "Chronos (simplified)", "ChrimsonR (simplified)")
POWER_MW = 10.0  # the depth chart shows light at 10 mW out of the fibre, like the simulator's figure


def sig(x, n=4):
    return float(f"{x:.{n}g}")


def depth_profile(npz):
    """Same definition as simulator.light.depth_profile: fluence averaged over the innermost 100 um."""
    r, z, phi = npz["r_edges"], npz["z_edges"], npz["fluence_per_W"].astype(float)
    k = max(1, int(round(0.1 / (r[1] - r[0]))))
    area = np.pi * (r[1:k + 1] ** 2 - r[:k] ** 2)
    prof = (phi[:k] * area[:, None]).sum(0) / area.sum()
    return 0.5 * (z[1:] + z[:-1]), prof


def first_depth_below(z, mw_mm2, level):
    """Depth (mm) where the profile first drops below `level`, past the tip."""
    m = z > 0
    zz, vv = z[m], mw_mm2[m]
    idx = np.nonzero(vv < level)[0]
    return None if idx.size == 0 else sig(zz[idx[0]], 3)


def light_block(summary):
    out = {"power_mW": POWER_MW, "depth_mm": None, "profiles": {}, "reach_mm": {}, "mu_eff_per_mm": {}}
    for c in COLOURS:
        z, prof = depth_profile(np.load(RESULTS / f"light_fibre200um_{c}nm.npz"))
        mw = prof * POWER_MW  # W/mm^2 per W  x  mW  ->  mW/mm^2
        m = (z > 0) & (z <= 4.0)
        zz, vv = z[m][1::2], mw[m][1::2]  # every 50 um is plenty for a chart
        out["depth_mm"] = [sig(v, 3) for v in zz]
        out["profiles"][c] = [sig(max(v, 1e-6)) for v in vv]
        out["reach_mm"][c] = {"3": first_depth_below(z, mw, 3.0), "1": first_depth_below(z, mw, 1.0)}
        out["mu_eff_per_mm"][c] = sig(summary["light"][c]["mu_eff_fit_per_mm"])
    return out


def hotter_than_stujenske(summary):
    """Range of (this model / Stujenske 2015) over the verified heating comparisons in run_summary.json."""
    h, pt = summary["heat_comparison"], summary["heat_pulse_trains_470nm_10mW"]
    a, b = h["case_532nm_62um_10mW"], h["case_445nm_200um"]
    r = [a["slice_plateau_C"] / a["published_slice_plateau_C"], a["max_voxel_C"] / a["published_max_voxel_C"],
         b["peak_C_per_mW"] / b["published_model_C_per_mW"],
         pt["50 % duty (25 ms on, 20 Hz)"] / max(pt["published_band_C (5-10 mW, <=50 % duty)"])]
    return [round(min(r), 1), round(max(r), 1)]


def heat_block(summary):
    pt = summary["heat_pulse_trains_470nm_10mW"]
    return {
        "colour": "470",
        "sim_power_mW": 10.0,
        "duration_s": 10.0,
        "duty_points": [
            {"duty": 0.10, "C": sig(pt["10 % duty (10 ms on, 10 Hz)"]), "pattern": "10 ms on, 10 pulses per second"},
            {"duty": 0.50, "C": sig(pt["50 % duty (25 ms on, 20 Hz)"]), "pattern": "25 ms on, 20 pulses per second"},
            {"duty": 1.00, "C": sig(pt["continuous"]), "pattern": "light always on"},
        ],
        "steady_C_per_mW": {c: sig(summary["heat_per_wavelength"][c]["peak_per_mW"]) for c in COLOURS},
        "published_band_C": pt["published_band_C (5-10 mW, <=50 % duty)"],
        "stujenske_compare": summary["heat_comparison"],
        "hotter_than_stujenske": hotter_than_stujenske(summary),
    }


# Klapoetke et al. 2014 (PMC3943671), wording checked in the full text; the same text as on the trade-off figure
CHRIMSONR_QUOTE = ("fast, reliable red-light driven spiking at frequencies of at least 20 Hz ... comparable to the "
                   "blue-light spiking performance of the commonly used ChR2 (H134R)")
CHRIMSONR_CONDITIONS = "cultured neurons and slice, 40-pulse trains, 2 ms pulses, 5 mW/mm\u00b2, red light"


def speed_block(summary):
    out = {"switches": {}, "rule": summary.get("following_rule", ""),
           "resonance_window_Hz": summary.get("following_resonance_window_Hz"),
           "dt_check": summary.get("following_dt_check"),
           "chrimsonr_quote": CHRIMSONR_QUOTE, "chrimsonr_conditions": CHRIMSONR_CONDITIONS}
    for name in SWITCHES + ("ChR2 (PyRhO fit)",):
        s = summary["switches"][name]
        fr = sorted((float(k), v) for k, v in s["fraction_by_rate"].items())
        out["switches"][name] = {
            "status": s["status"], "wavelength": s["wavelength"], "tau_off_ms": sig(s["tau_off_ms"], 3),
            "max_following_rate_Hz": s["max_following_rate_Hz"], "first_failure_Hz": s.get("first_failure_Hz"),
            "follows_again_Hz": s.get("follows_again_Hz", []),
            "rates_Hz": [r for r, _ in fr], "fraction": [sig(v, 3) for _, v in fr],
        }
    return out


def tradeoff_block():
    lines = [l for l in (RESULTS / "tradeoff.csv").read_text().splitlines() if l and not l.startswith("#")]
    rows = list(csv.DictReader(lines))
    return {"colours": [{k: r[k] for k in ("name", "wavelength_nm", "volume_mm3_per_mW_at_3mWmm2", "peak_warming_C_per_mW")}
                        for r in rows if r["row"] == "colour"],
            "switches": [{k: r[k] for k in ("name", "wavelength_nm", "status", "max_following_rate_Hz", "follows_again_Hz")}
                         for r in rows if r["row"] == "switch"]}


def recruitment_block(path, n_points=13):
    """Heat-budget result (heat-budget/results/recruitment.json, default expression spread). Returns per-colour
    power, warming and recruited counts, decimated to n_points, plus the count at 1 C. The 635 nm row is kept
    apart as a labelled toy upper bound. Returns None if the file is missing or malformed."""
    if path is None or not path.exists():
        return None
    try:
        d = json.loads(path.read_text())
        sigma = f"{d['assumptions']['default_sigma']:g}"
        cols, block = {}, {}
        for c, e in d["colours"].items():
            n = len(e["power_mW"])
            idx = np.unique(np.linspace(0, n - 1, n_points).round().astype(int))
            by = e["by_sigma"][sigma]
            cols[c] = {"power_mW": [sig(e["power_mW"][i]) for i in idx], "warming_C": [sig(e["warming_C"][i]) for i in idx],
                       "neurons_recruited": [int(by["recruited"][i]) for i in idx],
                       "at_1C": int(by["at_limit"]["1"]["recruited"]), "C_per_mW": sig(e["C_per_mW"]),
                       "power_for_1C_mW": sig(e["power_at_limit_mW"]["1"])}
        block = {"colours": [c for c in HEADLINE_COLOURS if c in cols], "data": cols,
                 "upper_bound": {c: cols[c] for c in cols if c not in HEADLINE_COLOURS},
                 "density_per_mm3": d["assumptions"]["density_per_mm3"], "threshold_mW_mm2": d["assumptions"]["threshold_mW_mm2"],
                 "sigma": float(sigma), "source": "heat-budget/results/" + path.name}
        ok = len(block["colours"]) > 0
    except (KeyError, TypeError, ValueError):
        ok = False
    if not ok:
        print(f"warning: {path} does not match the heat budget's recruitment.json schema; panel left out")
        return None
    return block


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--recruitment", type=Path, nargs="?", const=RECRUITMENT, default=None,
                    help=f"include the bonus panel from this file (default {RECRUITMENT.relative_to(HERE.parent)})")
    ap.add_argument("--out", type=Path, default=HERE / "data.js")
    a = ap.parse_args()
    summary = json.loads((RESULTS / "run_summary.json").read_text())
    data = {
        "tag": "Educational demo, toy model. Not research, not for lab or clinical use.",
        "light": light_block(summary),
        "heat": heat_block(summary),
        "speed": speed_block(summary),
        "tradeoff": tradeoff_block(),
        "model": {"heat_box_edge_mm": sig(float(np.load(RESULTS / "light_fibre200um_470nm.npz")["r_edges"][-1]), 3),
                  "neuron_dt_ms": summary.get("following_dt_check", {}).get("dt_ms")},
        "recruitment": recruitment_block(a.recruitment),
    }
    js = ("// Generated by build_data.py from ../results. Do not edit by hand.\n"
          "// Educational demo, toy model. Not research, not for lab or clinical use.\n"
          f"window.NOBEL_MED_DATA = {json.dumps(data, separators=(',', ':'))};\n")
    a.out.write_text(js)
    print(f"wrote {a.out} ({len(js.encode()) / 1024:.1f} KB); recruitment panel: "
          f"{'yes' if data['recruitment'] else 'no'}")


if __name__ == "__main__":
    main()
