"""Run everything and write results/: summary JSON, animation JSON, figures.

    python -m mirrorrace.run_all            # full run (about 2-4 minutes on a laptop, 4 processes)
    python -m mirrorrace.run_all --quick    # smaller seeded sweep, no N = 100,000 (under a minute)

Educational demo made to show an open-source tool. Toy model, not research. Dimensionless units.
"""
import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from . import analysis as an
from . import constants as C
from . import domains
from .sim import run

HERE = Path(__file__).resolve().parent.parent
RESULTS = HERE / "results"
STATUS = "final"


def _rng(*key):
    return np.random.default_rng([C.MASTER_SEED, *key])


def _ensemble(task):
    """One condition: returns the ee of every run at every checkpoint (runs x checkpoints)."""
    name, N, runs, k0, k2, progress, seed_one, key = task
    t = time.time()
    e = run(N, runs, k0, C.K1, k2, _rng(*key), progress=progress, seed_one=seed_one)
    ee = np.stack([e.ee(k) for k in range(len(progress))], axis=1)
    made = e.one[:, -1] + e.mirror[:, -1] + 2 * e.pairs[:, -1]
    return name, {"ee": ee, "progress": np.asarray(progress), "conserved": bool(np.all(made == N + e.seed_one)),
                  "seconds": time.time() - t}


def tasks(quick):
    P = C.PROGRESS_SWEEP
    out = [("copy_only", C.N_MAIN, C.RUNS, C.K0, 0.0, P, 0, (1,)),
           ("copy_only_a10", C.N_MAIN, C.RUNS, C.K0_STD_CHECK, 0.0, (1.0,), 0, (2,)),
           ("with_antagonism", C.N_MAIN, C.RUNS, C.K0, C.K2_STRONG, P, 0, (3,)),
           ("weak_antagonism", C.N_MAIN, C.RUNS, C.K0, C.K2_WEAK, (1.0,), 0, (4,))]
    for N in C.N_SWEEP:
        if N == C.N_MAIN or (quick and N > C.N_MAIN):
            continue
        out += [(f"copy_only_N{N}", N, C.RUNS, C.K0, 0.0, (1.0,), 0, (5, N)),
                (f"with_antagonism_N{N}", N, C.RUNS, C.K0, C.K2_STRONG, (1.0,), 0, (6, N))]
    runs = 400 if quick else C.SEED_RUNS
    deltas = np.repeat(np.asarray(C.SEED_DELTAS), runs)
    for N in C.N_SWEEP:
        if quick and N > C.N_MAIN:
            continue
        out.append((f"seeded_fixedrates_N{N}", N, deltas.size, C.K0, C.K2_STRONG, (1.0,), deltas, (7, N)))
        out.append((f"seeded_fixedconc_N{N}", N, deltas.size, C.K0 * N / C.N_REF, C.K2_STRONG, (1.0,), deltas, (8, N)))
    return out, runs


def race_progress(N=C.N_MAIN):
    """About 200 samples: evenly spaced, plus log-spaced ones so the first few molecules (where the race is decided) show."""
    used = np.unique(np.round(np.r_[np.geomspace(1, N, 150), np.linspace(0, N, 61)]).astype(int))
    return used / N, used


def race_runs(n_runs=8):
    """Time-resolved runs for the animation. The seed is the first one where both hands win at least 3 of 8."""
    prog, used = race_progress()
    out = {"progress": np.round(prog, 6).tolist(), "molecules_used": used.tolist(), "N": C.N_MAIN, "label": C.LABEL,
           "note": "counts of free one-hand, free mirror-hand molecules and inactive mixed pairs vs molecules of A used up "
                   "(samples are denser at the start, where the race is decided); 'time' is Gillespie model time "
                   "(dimensionless, 1/k1 units, per-molecule rates); seed picked so both hands win some runs "
                   "(each run's winner is still chance)"}
    for cond, k2, key in (("copy_only", 0.0, 9), ("with_antagonism", C.K2_STRONG, 10)):
        for s in range(200):
            e = run(C.N_MAIN, n_runs, C.K0, C.K1, k2, _rng(key, s), progress=prog, track_time=True)
            w = np.sign(e.ee(-1))
            if 3 <= np.sum(w > 0) <= 5 and np.sum(w < 0) >= 3:
                break
        out[cond] = {"seed": [C.MASTER_SEED, key, s], "k0": C.K0, "k1": C.K1, "k2": k2,
                     "runs": [{"one": e.one[i].tolist(), "mirror": e.mirror[i].tolist(), "pairs": e.pairs[i].tolist(),
                               "time": [float(f"{x:.4g}") for x in e.time[i]],
                               "final_ee": round(float(e.ee(-1)[i]), 4)} for i in range(n_runs)]}
    return out


def _stats_final(ee):
    one, mir, tie = an.wins(ee)
    return {"one_hand_wins": one, "mirror_hand_wins": mir, "ties": tie, "binomial_p": an.coin(one, mir),
            "p_one_hand_wins": round(one / (one + mir), 4), "mean_ee": round(float(ee.mean()), 4),
            "std_ee": round(float(ee.std()), 4), "median_abs_ee": round(float(np.median(np.abs(ee))), 4),
            "frac_abs_ee_above_90": round(float(np.mean(np.abs(ee) > 0.9)), 4)}


def summarise(res, seed_runs, race):
    s = {"status": STATUS, "label": C.LABEL, "disclaimer": C.DISCLAIMER, "units": "dimensionless model units",
         "N": C.N_MAIN, "runs": C.RUNS,
         "model": {"k0": C.K0, "k1": C.K1, "k2_strong": C.K2_STRONG, "k2_weak": C.K2_WEAK,
                   "ee_definition": "(one - mirror) / all product made, mixed pairs count one of each hand; fixed once A is used up",
                   "start": "N molecules of achiral A, zero of each hand (exactly racemic)"}}
    N, a = C.N_MAIN, C.K0 / C.K1
    ee = res["copy_only"]["ee"][:, -1]
    chi2, p, _, _ = an.flatness_test(ee, N, a)
    ee10 = res["copy_only_a10"]["ee"][:, -1]
    st = _stats_final(ee)
    s["copy_only"] = {"k0_over_k1": a, "std_ee": st["std_ee"], "std_predicted": round(an.polya_std_exact(N, a), 4),
                      "flatness_chi2_41bins": round(chi2, 2), "flatness_p": round(p, 4),
                      "p_one_hand_wins": st["p_one_hand_wins"], "one_hand_wins": st["one_hand_wins"],
                      "mirror_hand_wins": st["mirror_hand_wins"], "ties": st["ties"], "binomial_p": round(st["binomial_p"], 4),
                      "mean_ee": st["mean_ee"], "frac_abs_ee_above_90": st["frac_abs_ee_above_90"],
                      "exact_answer": "Beta-binomial(N, 1, 1): every final count equally likely (flat)",
                      "std_check_k0_over_k1_10": {"std_ee": round(float(ee10.std()), 4),
                                                  "std_predicted_exact_N": round(an.polya_std_exact(N, 10.0), 4),
                                                  "std_predicted_beta_10_10": round(an.polya_std_large_n(10.0), 4),
                                                  "flatness_p": round(an.flatness_test(ee10, N, 10.0)[1], 4)}}
    ea = res["with_antagonism"]["ee"]
    st = _stats_final(ea[:, -1])
    s["with_antagonism"] = {"k2_over_k1": C.K2_STRONG / C.K1, **{k: (round(v, 4) if isinstance(v, float) else v)
                                                                   for k, v in st.items()}}
    k = list(C.PROGRESS_SWEEP).index(C.STOP_FRACTION)
    es = np.abs(ea[:, k])
    s["stopped_early"] = {"read_after_fraction_of_A_used": C.STOP_FRACTION, "k2_over_k1": C.K2_STRONG / C.K1,
                          "median_abs_ee": round(float(np.median(es)), 4),
                          "range_abs_ee": [round(float(es.min()), 4), round(float(es.max()), 4)],
                          "q05_q95_abs_ee": [round(float(q), 4) for q in np.quantile(es, [0.05, 0.95])],
                          "frac_abs_ee_above_90": round(float(np.mean(es > 0.9)), 4),
                          **{kk: v for kk, v in _stats_final(ea[:, k]).items() if kk in ("one_hand_wins", "mirror_hand_wins", "ties", "binomial_p")},
                          "note": "the same toy runs as with_antagonism, read early (our choice of when to stop); not fitted to any experiment"}
    s["along_the_way"] = {"fraction_of_A_used": list(C.PROGRESS_SWEEP),
                          "with_antagonism_median_abs_ee": [round(float(np.median(np.abs(ea[:, j]))), 4) for j in range(len(C.PROGRESS_SWEEP))],
                          "with_antagonism_frac_abs_ee_above_90": [round(float(np.mean(np.abs(ea[:, j]) > 0.9)), 4) for j in range(len(C.PROGRESS_SWEEP))],
                          "copy_only_std_ee": [round(float(res["copy_only"]["ee"][:, j].std()), 4) for j in range(len(C.PROGRESS_SWEEP))]}
    s["weak_antagonism"] = {"k2_over_k1": C.K2_WEAK / C.K1, **{k: (round(v, 4) if isinstance(v, float) else v)
                                                                for k, v in _stats_final(res["weak_antagonism"]["ee"][:, -1]).items()}}
    s["other_N"] = {}
    for n in C.N_SWEEP:
        row = {}
        if n == C.N_MAIN:
            continue
        if f"copy_only_N{n}" in res:
            e = res[f"copy_only_N{n}"]["ee"][:, -1]
            row["copy_only"] = {"std_ee": round(float(e.std()), 4), "std_predicted": round(an.polya_std_exact(n, a), 4),
                                "flatness_p": round(an.flatness_test(e, n, a)[1], 4), **{k: v for k, v in _stats_final(e).items() if k in ("p_one_hand_wins", "binomial_p")}}
            e = res[f"with_antagonism_N{n}"]["ee"][:, -1]
            row["with_antagonism"] = {k: v for k, v in _stats_final(e).items() if k in ("frac_abs_ee_above_90", "median_abs_ee", "one_hand_wins", "mirror_hand_wins", "binomial_p")}
            s["other_N"][str(n)] = row
    s["real"] = {"soai_2003": {**{k: v for k, v in C.SOAI_2003.items()}, "binomial_p": round(an.coin(19, 18), 4)},
                 "singleton_vo_2003": {**C.SINGLETON_VO_2003, "binomial_p": round(an.coin(27, 27), 4)},
                 "note": "real runs ended at partial ee (15-91% in Soai's 37); the toy's spikes are not what a flask does"}
    s["seeded"] = seeded_summary(res, seed_runs)
    s["race_runs_seeds"] = {c: race[c]["seed"] for c in ("copy_only", "with_antagonism")}
    s["conservation_ok"] = all(v["conserved"] for v in res.values())
    s["seconds"] = {k: round(v["seconds"], 1) for k, v in res.items()}
    s["sources"] = C.SOURCES
    return s


def seeded_summary(res, runs):
    D = np.asarray(C.SEED_DELTAS)
    out = {"deltas": D.tolist(), "runs_per_point": runs, "k2_over_k1": C.K2_STRONG / C.K1,
           "scalings": {"fixed_rates": "k0/k1 = 1 for every N (the background is equally slow per molecule)",
                        "fixed_conc": f"k0/k1 = N / {C.N_REF} (same rate constants in concentration units: bigger flask, more background events before copying takes over)"},
           "curves": {}, "copy_only_exact": {}}
    for sc in ("fixedrates", "fixedconc"):
        for N in C.N_SWEEP:
            key = f"seeded_{sc}_N{N}"
            if key not in res:
                continue
            ee = res[key]["ee"][:, -1].reshape(len(D), runs)
            k = (ee > 0).sum(axis=1)
            pw = k / runs
            ci = [an.wilson(int(x), runs) for x in k]
            d75, d90 = an.crossing(D, pw, 0.75), an.crossing(D, pw, 0.9)
            out["curves"][f"{sc}_N{N}"] = {"N": N, "k0_over_k1": C.K0 * (N / C.N_REF if sc == "fixedconc" else 1),
                                         "p_seeded_wins": np.round(pw, 4).tolist(),
                                         "ci95": [[round(a, 4), round(b, 4)] for a, b in ci],
                                         "delta_at_p75": d75, "delta_at_p90": d90,
                                         "delta_at_p90_over_sqrtN": None if d90 is None else round(d90 / np.sqrt(N), 4)}
            a = C.K0 * (N / C.N_REF if sc == "fixedconc" else 1)
            out["copy_only_exact"][f"{sc}_N{N}"] = [round(an.seeded_copy_only_exact(N, a, int(d)), 4) for d in D]
    for sc in ("fixedrates", "fixedconc"):
        d90 = [(c["N"], c["delta_at_p90"]) for k, c in out["curves"].items() if k.startswith(sc) and c["delta_at_p90"]]
        if len(d90) > 1:
            raw = [d for _, d in d90]
            sq = [d / np.sqrt(n) for n, d in d90]
            out[f"{sc}_collapse"] = {"delta_at_p90_by_N": {str(n): round(d, 2) for n, d in d90},
                                     "spread_of_delta (max/min)": round(max(raw) / min(raw), 2),
                                     "spread_of_delta_over_sqrtN (max/min)": round(max(sq) / min(sq), 2)}
    return out


def domains_summary(times, shots, total):
    tot = float(total)
    return {"label": "toy: what Frank's equations do when the flask isn't stirred; " + C.LABEL,
            "grid": int(shots.shape[-1]), "molecules_of_A_per_cell": domains.OMEGA,
            "params": {"k0": domains.K0, "k1": domains.K1, "k2": domains.K2, "D": domains.D, "dt": domains.DT,
                       "note": "tuned for a clear picture; tau-leaping on whole molecules, periodic edges, closed flask"},
            "frames": len(times), "strip": "domains_strip_{light,dark}.png: frames left to right, 10 per row, 128 px each, 2 px gaps",
            "time": [round(float(x), 2) for x in times],
            "frac_A_left": [round(float(s[3].sum()) / tot, 4) for s in shots],
            "frac_one_hand_free": [round(float(s[0].sum()) / tot, 4) for s in shots],
            "frac_mirror_hand_free": [round(float(s[1].sum()) / tot, 4) for s in shots],
            "frac_in_mixed_pairs": [round(2 * float(s[2].sum()) / tot, 4) for s in shots]}


def histograms(res):
    out = {"edges": np.round(an.EDGES41, 4).tolist(), "label": C.LABEL, "N": C.N_MAIN, "runs": C.RUNS,
           "stopped_early_fraction_of_A_used": C.STOP_FRACTION, "counts": {}, "first_400_ee": {}, "first_400_bin": {}}
    k = list(C.PROGRESS_SWEEP).index(C.STOP_FRACTION)
    series = {"copy_only": res["copy_only"]["ee"][:, -1], "with_antagonism": res["with_antagonism"]["ee"][:, -1],
              "stopped_early": res["with_antagonism"]["ee"][:, k]}
    for name, ee in series.items():
        out["counts"][name] = np.histogram(ee, bins=an.EDGES41)[0].tolist()
        out["first_400_ee"][name] = np.round(ee[:400], 3).tolist()
        out["first_400_bin"][name] = np.clip(np.searchsorted(an.EDGES41, ee[:400], side="right") - 1, 0, 40).tolist()
    out["copy_only_exact_expected"] = np.round(an.polya_binned(C.N_MAIN, C.K0 / C.K1) * C.RUNS, 2).tolist()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    ap.add_argument("--no-figures", action="store_true")
    ap.add_argument("--no-domains", action="store_true", help="skip the unstirred 2D bonus (about 25 s)")
    args = ap.parse_args()
    RESULTS.mkdir(exist_ok=True)
    t0 = time.time()
    tl, seed_runs = tasks(args.quick)
    tl.sort(key=lambda t: -t[1] * t[2])
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        dom = None if args.no_domains else ex.submit(domains.simulate)
        res = dict(ex.map(_ensemble, tl))
        dom = None if dom is None else dom.result()
    race = race_runs()
    summary = summarise(res, seed_runs, race)
    summary["quick"] = args.quick
    hist = histograms(res)
    for name, obj in (("mirror_summary.json", summary), ("race_runs.json", race), ("histograms.json", hist)):
        (RESULTS / name).write_text(json.dumps(obj, indent=None if name != "mirror_summary.json" else 1,
                                               separators=None if name == "mirror_summary.json" else (",", ":")))
    np.savez_compressed(RESULTS / "final_ee.npz", **{k: res[k]["ee"][:, -1].astype(np.float32) for k in
                                                          ("copy_only", "copy_only_a10", "with_antagonism", "weak_antagonism")})
    if dom is not None:
        summary["domains"] = domains_summary(*dom)
        (RESULTS / "domains_frames.json").write_text(json.dumps(summary["domains"], separators=(",", ":")))
        (RESULTS / "mirror_summary.json").write_text(json.dumps(summary, indent=1))
    if not args.no_figures:
        from . import figures
        figures.make_all(summary, race, hist, RESULTS)
        if dom is not None:
            for theme in figures.THEMES:
                figures.domains(*dom, RESULTS, theme)
    print(json.dumps({k: summary[k] for k in ("copy_only", "with_antagonism", "stopped_early")}, indent=1))
    print(f"done in {time.time() - t0:.0f} s -> {RESULTS}")


if __name__ == "__main__":
    main()
