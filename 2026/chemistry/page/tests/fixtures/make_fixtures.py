"""Write PLACEHOLDER inputs for the Chemistry page, in the layout the three experiments promise
(mirror-race, kagan-curve, soai-amplifier). Educational demo, toy models; not research.

These are rough stand-ins so the page can be built and tested before the experiments land. They are not
results: every file says "status": "fixture" and the page labels each number from them "placeholder".
All quantities are dimensionless model units.

    python3 tests/fixtures/make_fixtures.py        (from 2026/chemistry/page/; needs NumPy)
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LABEL = "placeholder for tests, not a result"
rng = np.random.default_rng(7)


def dump(rel, obj):
    p = HERE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1) + "\n")
    print("wrote", p.relative_to(HERE))


def race(n, k0, k1, k2, seed, samples=200):
    """Jump-chain Frank network (one hand X, mirror hand Y, inactive pair P) from a racemic start."""
    r = np.random.default_rng(seed)
    a, x, y, p = n, 0, 0, 0
    one, mir, prog = [0], [0], [0.0]
    marks = set(np.linspace(0, n, samples).astype(int))
    while True:
        w = np.array([k0 * a + k1 * a * x / n, k0 * a + k1 * a * y / n, k2 * x * y / n])
        if w.sum() <= 0:
            break
        e = r.choice(3, p=w / w.sum())
        if e == 0: a -= 1; x += 1
        elif e == 1: a -= 1; y += 1
        else: x -= 1; y -= 1; p += 1
        if (n - a) in marks and e < 2:
            one.append(x); mir.append(y); prog.append((n - a) / n)
    return {"seed": seed, "progress": prog, "one_hand": one, "mirror_hand": mir}


def main():
    edges = np.linspace(-1, 1, 42)
    flat = rng.uniform(-1, 1, 10000)
    spikes = np.sign(rng.uniform(-1, 1, 10000)) * (1 - np.abs(rng.normal(0, 0.03, 10000)))
    early = np.sign(rng.uniform(-1, 1, 10000)) * np.clip(rng.beta(2.2, 1.6, 10000), 0.05, 1)
    h = lambda v: np.histogram(v, edges)[0].tolist()
    dump("mirror-race/results/mirror_summary.json", {
        "status": "fixture", "N": 10000, "runs": 10000,
        "model": {"k0": 1.0, "k1": 1.0, "k2_strong": 100.0, "ee_definition": "(one - mirror) / all product made, mixed pairs count one of each hand"},
        "copy_only": {"std_ee": 0.577, "std_predicted": 0.5774, "flatness_p": 0.5, "p_one_hand_wins": 0.501},
        "with_antagonism": {"frac_abs_ee_above_90": 0.97, "one_hand_wins": 5012, "mirror_hand_wins": 4988, "binomial_p": 0.81},
        "stopped_early": {"read_after_fraction_of_A_used": 0.05, "median_abs_ee": 0.55, "range_abs_ee": [0.05, 0.99], "q05_q95_abs_ee": [0.1, 0.98]},
        "real": {"soai_2003": {"runs": 37, "one": 19, "mirror": 18, "ee_range_pct": [15, 91], "binomial_p": 1.0},
                 "singleton_vo_2003": {"runs": 54, "one": 27, "mirror": 27, "binomial_p": 1.0}},
        "seeded": {}, "sources": {}, "label": LABEL})
    dump("mirror-race/results/histograms.json", {
        "status": "fixture", "edges": edges.round(6).tolist(), "stopped_early_fraction_of_A_used": 0.05,
        "counts": {"copy_only": h(flat), "with_antagonism": h(spikes), "stopped_early": h(early)},
        "first_400_ee": {"copy_only": flat[:400].round(4).tolist(), "with_antagonism": spikes[:400].round(4).tolist()},
        "label": LABEL})
    dump("mirror-race/results/race_runs.json", {
        "status": "fixture", "N": 2000, "label": LABEL,
        "copy_only": {"runs": [race(2000, 1, 1, 0, s, 120) for s in range(4)]},
        "with_antagonism": {"runs": [race(2000, 1, 1, 100, s, 120) for s in range(4)]}})

    def ee_prod(eel, K, g):
        z = (1 - eel ** 2) / 2 if abs(K - 4) < 1e-12 else (-K + np.sqrt(K * (4 * (1 - eel ** 2) + K * eel ** 2))) / (4 - K)
        b = z / (1 - z)
        return eel * (1 + b) / (1 + g * b)
    eel = np.linspace(0, 1, 21)
    dump("kagan-curve/results/kagan_summary.json", {
        "status": "fixture",
        "pie_check": {"ligand": [75, 25], "catalysts_pct": [56.25, 37.5, 6.25], "effective": [90, 10], "ee_prod_pct": 80},
        "curves": {"K": 4, "g_values": [0, 0.5, 1, 2], "ee_L": eel.round(4).tolist(),
                   "ee_prod": {str(g): ee_prod(eel, 4, g).round(6).tolist() for g in (0, 0.5, 1, 2)}},
        "erosion": [100, 90, 81, 72.9, 65.61], "label": LABEL})
    dump("soai-amplifier/results/amplifier_summary.json", {
        "status": "fixture", "soai_2003_pct": [0.00005, 57, 99, 99.5],
        "layer1": {"ee0_0p01_ton1e4_pct": 61.8, "ee0_0p5_pct": 99.0},
        "toy_rounds": {"K": 1000, "turnovers_per_round": 5, "ee_pct": [66, 94, 99]},
        "k4_fails": {"turnovers_needed_to_57": 1.7e6}, "layer3": {},
        "notes": "one published toy model of several; the real mechanism is still debated", "label": LABEL})
    dump("soai-amplifier/results/rounds.json", {
        "status": "fixture", "label": LABEL,
        "rounds": [{"round": i, "ee_pct": e} for i, e in enumerate([0.00005, 66, 94, 99])]})


if __name__ == "__main__":
    main()
