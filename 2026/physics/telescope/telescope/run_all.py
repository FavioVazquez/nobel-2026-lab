"""One command: sweep every geometry, pick the example event, write the JSON files and the figures.

    python -m telescope.run_all                       # 4,000-track run, labelled "preliminary"
    python -m telescope.run_all --events 10000 --photons 300000 --workers 60 --status final   # the published run
    python -m telescope.run_all --quick               # small smoke run, a minute or two on a laptop
    python -m telescope.run_all --figures-only        # redraw figures from results/*.json

Educational demo made to show an open-source tool. Toy model, not research.
"""
import argparse
import csv
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from . import constants as K
from . import photon_check
from .geometry import hex_grid, icecube
from .light import AMPLITUDE, DIFF_LEN, THETA_C
from .sweep import FIELDS, run_event, run_geometry, tracks_for

RESULTS = Path(__file__).resolve().parent.parent / "results"
SPACINGS_M = [50, 80, 125, 160, 200, 250, 300]
LABEL = "our toy model, tuned constants, trend only"
DEMO = "Educational demo made to show an open-source tool. Toy model, not research."


def stats(R, rng):
    m = R["triggered"] == 1
    out = dict(tracks=int(len(m)), fitted_events=int(m.sum()), trigger_fraction=round(float(m.mean()), 4),
               median_hits=float(np.median(R["n_hits"][m])) if m.any() else None,
               median_hits_all_tracks=float(np.median(R["n_hits"])))
    for fit in ("line", "pandel"):
        e = R[f"err_{fit}_deg"][m]
        boot = np.median(rng.choice(e, (400, len(e))), axis=1)
        out[fit] = dict(median=float(np.median(e)), p68=float(np.quantile(e, 0.68)),
                        p16=float(np.quantile(e, 0.16)), p84=float(np.quantile(e, 0.84)),
                        median_ci68=[float(np.quantile(boot, 0.16)), float(np.quantile(boot, 0.84))])
    return out


def pick_example(R):
    """A typical event, not the best: among fitted events, the one whose Pandel error AND hit count are both
    closest to their medians (smallest sum of distances in rank, each rank scaled to 0..1)."""
    m = np.flatnonzero(R["triggered"] == 1)
    rank = lambda a: np.argsort(np.argsort(a)) / max(len(a) - 1, 1)
    score = np.abs(rank(R["err_pandel_deg"][m]) - 0.5) + np.abs(rank(R["n_hits"][m]) - 0.5)
    return int(R["event"][m[np.argmin(score)]])


def r3(v, nd=3):
    return [round(float(x), nd) for x in v]


def example_json(tracks, i, seed):
    ev = run_event("icecube", tracks[i], i, seed, keep_hits=True)
    idx, t, q = ev["hits"]
    order = np.argsort(t)
    return dict(
        label=LABEL, demo=DEMO, geometry="data/icecube86_geometry.csv (row order = sensor_index)",
        event=i, seed=seed, how_chosen="typical event: Pandel error and hit count both closest to their medians",
        track=dict(point=r3(ev["track"].point, 2), dir=r3(ev["track"].dir, 5)),
        time_zero="the true muon passes track.point at t = 0 ns",
        hits=[[int(idx[k]), round(float(t[k]), 1), int(q[k])] for k in order],
        hits_columns=["sensor_index", "t_ns (first photon)", "charge (photoelectrons)"],
        line_fit_dir=r3(ev["line"][0], 5), line_fit_point=r3(ev["line"][1], 2),
        pandel_fit_dir=r3(ev["pandel"][0], 5), pandel_fit_point=r3(ev["pandel"][1], 2),
        error_deg=dict(line=round(ev["err_line_deg"], 3), pandel=round(ev["err_pandel_deg"], 3)),
        n_hits=ev["n_hits"], n_strings_hit=ev["n_strings_hit"])


def write_events_csv(all_R):
    with open(RESULTS / "per_event.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(("geometry",) + FIELDS)
        for key, R in all_R.items():
            for j in range(len(R["event"])):
                w.writerow([key] + [("" if isinstance(R[k][j], float) and np.isnan(R[k][j]) else
                                     (round(float(R[k][j]), 4) if R[k].dtype.kind == "f" else int(R[k][j])))
                                    for k in FIELDS])


def sweep_all(n, seed, workers):
    t = time.time()
    tracks = tracks_for(n, seed)
    timings = {"generate_tracks_s": round(time.time() - t, 2)}
    all_R, per = {}, {}
    rng = np.random.default_rng(seed)
    for key in [str(s) for s in SPACINGS_M] + ["icecube"]:
        t = time.time()
        all_R[key] = run_geometry(key, tracks, seed, workers)
        timings[f"sweep_{key}_s"] = round(time.time() - t, 2)
        per[key] = stats(all_R[key], rng)
        print(f"{key:>8}: {per[key]['fitted_events']} fitted, hits {per[key]['median_hits']}, "
              f"line {per[key]['line']['median']:.2f} deg, pandel {per[key]['pandel']['median']:.2f} deg "
              f"[{timings[f'sweep_{key}_s']} s]", flush=True)
    return tracks, all_R, per, timings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--events", type=int, default=4000, help="tracks generated per geometry (default 4000)")
    ap.add_argument("--workers", type=int, default=None, help="processes (default: all cores)")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--status", default="preliminary", choices=["preliminary", "final"])
    ap.add_argument("--quick", action="store_true", help="60 tracks per geometry, smoke test only")
    ap.add_argument("--figures-only", action="store_true")
    ap.add_argument("--photons", type=int, default=200_000, help="photons for the tier-B photon-walk check")
    ap.add_argument("--sensitivity-out", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    RESULTS.mkdir(exist_ok=True)
    n = 60 if a.quick else a.events
    if a.sensitivity_out:          # internal: sweep only, with the Pandel override already in the environment
        _, _, per, timings = sweep_all(n, a.seed, a.workers)
        Path(a.sensitivity_out).write_text(json.dumps(dict(per=per, timings_s=timings,
                                                           pandel=os.environ.get("TELESCOPE_PANDEL"))))
        return
    if not a.figures_only:
        t_all = time.time()
        t = time.time()
        pc = photon_check.run(20_000 if a.quick else a.photons)
        (RESULTS / "photon_check.json").write_text(json.dumps(pc))
        tpc = round(time.time() - t, 1)
        tracks, all_R, per, timings = sweep_all(n, a.seed, a.workers)
        timings["photon_check_s"] = tpc
        t = time.time()
        fp = pc["pandel_fitted_to_walk"]
        env = dict(os.environ, TELESCOPE_PANDEL=f"{fp['lambda_m']},{fp['tau_ns']},{fp['lambda_a_m']}")
        sens_path = RESULTS / "sensitivity_walk_delays.json"
        cmd = [sys.executable, "-m", "telescope.run_all", "--events", str(n), "--seed", str(a.seed),
               "--sensitivity-out", str(sens_path)] + (["--workers", str(a.workers)] if a.workers else [])
        subprocess.run(cmd, env=env, check=True, cwd=RESULTS.parent)
        sens = json.loads(sens_path.read_text())
        timings["sensitivity_sweep_s"] = round(time.time() - t, 1)
        write_events_csv(all_R)
        ex_i = pick_example(all_R["icecube"])
        (RESULTS / "example_event.json").write_text(json.dumps(example_json(tracks, ex_i, a.seed)))
        hx = [per[str(s)] for s in SPACINGS_M]
        ic = per["icecube"]
        summary = dict(
            status=a.status if not a.quick else "smoke-test", label=LABEL, demo=DEMO,
            spacings_m=SPACINGS_M,
            median_error_deg={f: [round(p[f]["median"], 3) for p in hx] for f in ("line", "pandel")},
            p68_error_deg={f: [round(p[f]["p68"], 3) for p in hx] for f in ("line", "pandel")},
            p16_error_deg={f: [round(p[f]["p16"], 3) for p in hx] for f in ("line", "pandel")},
            p84_error_deg={f: [round(p[f]["p84"], 3) for p in hx] for f in ("line", "pandel")},
            median_error_ci68_deg={f: [r3(p[f]["median_ci68"]) for p in hx] for f in ("line", "pandel")},
            median_hits=[p["median_hits"] for p in hx],
            trigger_fraction=[p["trigger_fraction"] for p in hx],
            fitted_events=[p["fitted_events"] for p in hx],
            n_strings=[hex_grid(s).n_strings for s in SPACINGS_M],
            icecube_real=dict(
                median_error_deg={f: round(ic[f]["median"], 3) for f in ("line", "pandel")},
                p68_error_deg={f: round(ic[f]["p68"], 3) for f in ("line", "pandel")},
                p16_error_deg={f: round(ic[f]["p16"], 3) for f in ("line", "pandel")},
                p84_error_deg={f: round(ic[f]["p84"], 3) for f in ("line", "pandel")},
                median_error_ci68_deg={f: r3(ic[f]["median_ci68"]) for f in ("line", "pandel")},
                median_hits=ic["median_hits"], trigger_fraction=ic["trigger_fraction"],
                fitted_events=ic["fitted_events"], n_strings=icecube().n_strings),
            events_per_point=int(min([p["fitted_events"] for p in hx] + [ic["fitted_events"]])),
            events_per_point_note="smallest number of fitted (triggered) events at any point; "
                                  "tracks_generated_per_point tracks were simulated at every point",
            tracks_generated_per_point=n,
            definitions=dict(
                median="median angular error between the true and the fitted direction, over fitted events",
                p68="68% of fitted events have a smaller error (68% containment)",
                p16_p84="the middle 68% of fitted events lies between these errors (the band in the figure)",
                median_ci68="bootstrap 68% interval of the median itself (statistical precision)",
                median_hits="median number of hit sensors over fitted events",
                trigger=f"at least {K.TRIGGER_MIN_HITS} hit sensors"),
            model=dict(muon_energy_gev=K.MUON_ENERGY_GEV, cherenkov_angle_deg=round(float(np.degrees(THETA_C)), 2),
                       photons_per_m=round(K.muon_photons_per_m()), mean_pe_amplitude=round(float(AMPLITUDE), 3),
                       diffusion_length_m=round(float(DIFF_LEN), 2), time_jitter_ns=K.TIME_JITTER_NS),
            sensitivity_walk_delays=dict(
                what="same sweep, but simulation AND fit use Pandel delays fitted to our photon random walk "
                     "(results/photon_check.json) instead of AMANDA's published values",
                pandel=fp,
                median_error_deg={f: [round(sens["per"][str(s)][f]["median"], 3) for s in SPACINGS_M]
                                  for f in ("line", "pandel")},
                median_hits=[sens["per"][str(s)]["median_hits"] for s in SPACINGS_M],
                icecube_real=dict(median_error_deg={f: round(sens["per"]["icecube"][f]["median"], 3)
                                                    for f in ("line", "pandel")},
                                  median_hits=sens["per"]["icecube"]["median_hits"])),
            photon_check=dict(file="results/photon_check.json", summary=pc["summary"],
                              pandel_fitted_to_walk=fp, n_photons=pc["n_photons"]),
            seed=a.seed, timings_s=dict(timings, total_s=round(time.time() - t_all, 1)),
            machine=dict(system=platform.system(), cpus=os.cpu_count(), workers=a.workers or os.cpu_count(),
                         python=platform.python_version(), numpy=np.__version__))
        (RESULTS / "telescope_summary.json").write_text(json.dumps(summary, indent=1))
    from .figures import make_all
    make_all(RESULTS)


if __name__ == "__main__":
    main()
