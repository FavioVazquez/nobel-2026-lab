"""Run everything: python -m amplifier.run_all (from 2026/chemistry/soai-amplifier/). Writes results/."""
import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from . import constants as C
from . import model as M


def _r(v, n=6):
    return float(f"{float(v):.{n}g}")


def _key(pct):
    return np.format_float_positional(float(f"{pct:.6g}"), trim="-")


def _k2_point(args):
    k2, ee0 = args
    out = M.buhse_run(ee0, cat0=C.BUHSE_CAT0, t_end=C.BUHSE_T_END, k2=k2)
    return out["ee_final"], out["A_final"]


def layer1():
    rows = []
    for ee0_pct, ton in C.L1_STATEMENTS:
        rows.append({"ee0_pct": ee0_pct, "turnovers": ton,
                     "ee_pct": _r(100 * M.layer1_ee(ee0_pct / 100, 1 + ton), 5)})
    ton = np.logspace(0, 8, 81)
    fan = {_key(e): [_r(100 * v, 6) for v in M.layer1_ee(e / 100, 1 + ton)] for e in (0.00005, 0.01, 0.5, 5.0)}
    return {"model": "Blackmond-Brown dimer model, K = 4, mixed pair inactive; exact: 1/S - 1/R is conserved",
            "statements": rows,
            "source": "Blackmond review arXiv:1909.13015 (scheme 8, fig. 3): 0.01 % with 1e4 turnovers -> just over"
                      " 60 %; 0.5 % -> approaches homochirality",
            "fan": {"turnovers": [_r(t) for t in ton], "ee_pct_by_ee0_pct": fan}}


def toy(ee0):
    K, N = M.fit_two_rounds(ee0, C.FIT_TARGET_ROUNDS[0] / 100, C.FIT_TARGET_ROUNDS[1] / 100)
    ee = M.toy_rounds(ee0, K, N, C.ROUNDS_SHOWN)
    scan = []
    for k in C.K_SCAN:
        n = M.turnovers_for_round1(ee0, C.FIT_TARGET_ROUNDS[0] / 100, k)
        scan.append({"K": k, "turnovers_per_round_for_57": _r(n, 4),
                     "ee_pct": [_r(100 * v, 5) for v in M.toy_rounds(ee0, k, n, 3)]})
    return K, N, ee, scan


def rounds_json(ee0, K, N, ee):
    rows = []
    for k in range(len(ee) + 1):
        e = ee0 if k == 0 else float(ee[k - 1])
        total = (1 + N) ** k
        one, mir = M.hand_amounts(e, total)
        rows.append({"round": k, "ee_pct": _r(100 * e, 6), "mirror_hand_share_pct": _r(100 * (1 - e) / 2, 6),
                     "one_hand_amount": _r(one), "mirror_hand_amount": _r(mir),
                     "log10_one_hand": _r(np.log10(one), 5), "log10_mirror_hand": _r(np.log10(mir), 5),
                     "soai_2003_pct": C.SOAI_2003_PCT[k] if k < len(C.SOAI_2003_PCT) else None})
    return {"status": None, "label": C.LABEL, "notes": C.NOTES,
            "what": "our toy model (layer 2), trend only: each round's whole product seeds the next; amounts are"
                    " relative to the round-0 seed (= 1), dimensionless",
            "K": _r(K), "turnovers_per_round": _r(N),
            "fitted": "K and turnovers_per_round are fitted toy numbers (to 57 % and 99 %); not Soai's values",
            "soai_2003_note": "Soai 2003 (S03a): 0.00005 -> 57 -> 99 -> >99.5 % ee; the last is a lower bound",
            "rounds": rows}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="final")
    ap.add_argument("--no-figures", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    from . import figures as F
    F.RESULTS.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    ee0 = C.SOAI_2003_PCT[0] / 100
    l1 = layer1()
    K, N, ee, scan = toy(ee0)
    rj = rounds_json(ee0, K, N, ee)
    rj["status"] = a.status
    k4 = {"turnovers_needed_to_57": _r(M.layer1_factor_needed(ee0, 0.57) - 1, 4),
          "note": "exact, from 1/S - 1/R conserved: K = 4 needs ~1.7 million turnovers to go from 0.00005 % to 57 %",
          "three_rounds": {_key(n): [_r(100 * v, 4) for v in M.toy_rounds(ee0, 4.0, n, 3)]
                           for n in (*C.K4_DEMO_TURNOVERS, N)}}

    fig1 = M.buhse_run(C.BUHSE_EE0, cat0=C.BUHSE_CAT0, t_end=C.BUHSE_T_END)
    k2s = np.logspace(*C.K2_LOG10_SCAN)
    jobs = [(k2, e) for e in C.K2_EE0S for k2 in k2s]
    with ProcessPoolExecutor(max_workers=max(1, min(4, a.workers))) as ex:
        res = list(ex.map(_k2_point, jobs))
    bif = {_key(100 * e): [_r(100 * res[i * len(k2s) + j][0], 5) for j in range(len(k2s))]
           for i, e in enumerate(C.K2_EE0S)}
    racemic = M.buhse_run(0.0, cat0=C.BUHSE_CAT0, t_end=C.BUHSE_T_END)["ee_final"]
    naive = M.buhse_naive_racemic(C.BUHSE_CAT0, C.BUHSE_T_END)
    naive_scan = [{"rtol": rt, "atol": at, "ee_final": _r(M.buhse_naive_racemic(C.BUHSE_CAT0, C.BUHSE_T_END, rtol=rt, atol=at), 3)}
                  for rt, at in C.NAIVE_TOLERANCES]
    l3 = {"model": "Buhse-Micheau monomer-active model, reactions [1']-[10'] of Buhse 2005 (J. Mex. Chem. Soc. 49, 328)",
          "params": {**M.BUHSE_FIG1, "A0": 1.0, "Z0": 1.0, "seed": C.BUHSE_CAT0},
          "fig1_check": {"ee0_pct": _r(100 * C.BUHSE_EE0), "ee_final_pct": _r(100 * fig1["ee_final"], 4),
                         "published": "about 85 % (Buhse 2005 Fig. 1)", "A_left": _r(fig1["A_final"], 3)},
          "k2_bifurcation": {"k2": [_r(k) for k in k2s], "ee_final_pct_by_ee0_pct": bif,
                             "published": "amplification needs strong mixed-pair formation; Buhse 2005 Fig. 2 puts"
                                          " the threshold near k2 = 6e3 for an achiral start"},
          "racemic_stays_racemic": {"ee_final": racemic,
                                    "naive_hand_by_hand_LSODA_ee_final": _r(naive, 4),
                                    "naive_tolerance_scan": naive_scan,
                                    "note": "our sum/difference form keeps an exact racemic start at exactly 0; the"
                                            " same model written hand by hand with LSODA (finite-difference Jacobian)"
                                            " drifts to this ee from numerical error alone (value depends on solver"
                                            " tolerances: rtol 1e-10 / atol 1e-22 here; see naive_tolerance_scan)"}}
    summary = {
        "status": a.status, "label": C.LABEL, "notes": C.NOTES,
        "units": "dimensionless model units; ee in per cent; our toy model, trend only",
        "soai_2003_pct": list(C.SOAI_2003_PCT),
        "soai_2003_note": "S03a: a prepared 0.00005 % ee head start (five parts in ten million), then 57, 99, >99.5 %",
        "layer1": l1,
        "toy_rounds": {"K": _r(K), "turnovers_per_round": _r(N), "ee_pct": [_r(100 * v, 6) for v in ee[:3]],
                       "ee_pct_more_rounds": [_r(100 * v, 6) for v in ee],
                       "fitted": "K and turnovers_per_round are fitted toy numbers (round 1 = 57 %, round 2 = 99 %);"
                                 " round 3 is the model's prediction against >99.5 %. Turnovers per round is a model"
                                 " parameter, not Soai's experimental ratio",
                       "K_scan_matched_to_round1": scan,
                       "selectivity_check": {
                           "ee_max": C.EROSION_EE_MAX,
                           "ee_pct_more_rounds": [_r(100 * v, 6) for v in M.toy_rounds(ee0, K, N, C.ROUNDS_SHOWN,
                                                                                         C.EROSION_EE_MAX)],
                           "note": "the same fitted K and turnovers, but same-hand pairs only 90 % selective (as in the"
                                   " erosion example): still climbs from 0.00005 %, then levels off near 90 %; the"
                                   " climb to 99.98 % comes from our choice of perfectly selective pairs (ee_max = 100 %)"}},
        "k4_fails": k4,
        "layer3": l3,
        "erosion_pct": [_r(100 * C.EROSION_EE_MAX ** k) for k in range(C.ROUNDS_SHOWN + 1)],
        "runtime_s": round(time.time() - t0, 1),
    }
    (F.RESULTS / "amplifier_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (F.RESULTS / "rounds.json").write_text(json.dumps(rj, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("toy_rounds", "k4_fails")}, indent=1)[:1500])
    print("layer1", l1["statements"], "layer3", l3["fig1_check"], l3["racemic_stays_racemic"])
    if not a.no_figures:
        for p in F.all_figures(summary, rj):
            print("wrote", p.name)


if __name__ == "__main__":
    main()
