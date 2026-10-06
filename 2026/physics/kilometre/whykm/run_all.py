"""One command: every number, table and figure.   python -m whykm.run_all [--status final] [--fetch]

Educational demo made to show an open-source tool. Toy model, not research.
Writes results/kilometre_summary.json, results/*.csv and results/*_{light,dark}.png.
The cross-checks run only if the public IceCube files are in data_cache/ (python -m whykm.fetch).
"""
import argparse
import csv
import json
import platform
import time

import numpy as np

from . import constants as C
from . import crosscheck as X
from . import figures as F
from . import physics as P
from .fetch import fetch

TOY = "our toy model, trend only"


def sig(x, n=3):
    return float(f"{x:.{n}g}")


def write_csv(name, header, rows, note=""):
    F.RESULTS.mkdir(parents=True, exist_ok=True)
    with open(F.RESULTS / name, "w", newline="") as f:
        f.write(f"# {F.LABEL} Values: {TOY}.{' ' + note if note else ''}\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def core_numbers():
    p100, p1 = (float(P.p_interact_flavour(e)) for e in (1e5, 1e6))
    Xv = P.column_depth(-1.0)
    T100, T1 = (float(P.transmission_flavour(e, None, "mu", X=Xv)) for e in (1e5, 1e6))
    per_nucleon = P.events_per_year_per_nucleon()
    ev = {k: float(P.nucleons_in_cube(s) * per_nucleon) for k, s in (("10m", 10), ("100m", 100), ("1km", 1000))}
    lo = P.events_per_year(1000, phi=C.HESE_PHI_ASTRO - C.HESE_PHI_ASTRO_ERR[0])
    hi = P.events_per_year(1000, phi=C.HESE_PHI_ASTRO + C.HESE_PHI_ASTRO_ERR[1])
    g_soft = P.events_per_year(1000, gamma=C.HESE_GAMMA + C.HESE_GAMMA_ERR[1])
    g_hard = P.events_per_year(1000, gamma=C.HESE_GAMMA - C.HESE_GAMMA_ERR[0])
    details = {
        "p_interact_1km_per_species": {s: {k: float(P.p_interact(e, 1000, s)) for k, e in (("100TeV", 1e5), ("1PeV", 1e6))}
                                       for s in P.SPECIES},
        "earth_survival_vertical_per_species": {
            s: {k: float(P.transmission(e, None, s, X=Xv)) for k, e in (("100TeV", 1e5), ("1PeV", 1e6), ("10TeV", 1e4))}
            for s in ("numu", "numubar")},
        "vertical_column_depth_g_cm2": float(Xv),
        "events_per_year_per_nucleon": float(per_nucleon),
        "events_per_year_2km": float(P.nucleons_in_cube(2000) * per_nucleon),
        "events_1km_split": {
            "upgoing_through_earth": float(P.events_per_year(1000, hemisphere="up")),
            "downgoing": float(P.events_per_year(1000, hemisphere="down")),
            "if_earth_were_transparent": float(P.events_per_year(1000, earth=False)),
            "charged_current_only": float(P.events_per_year(1000, kind="CC")),
            "neutral_current_only": float(P.events_per_year(1000, kind="NC")),
            "threshold_100TeV": float(P.events_per_year(1000, e_min=1e5)),
            "integrate_to_100PeV_instead_of_10PeV": float(P.events_per_year(1000, e_max=1e8)),
        },
        "events_1km_flux_band": {
            "normalisation_minus_1sigma": float(lo), "normalisation_plus_1sigma": float(hi),
            "gamma_plus_1sigma_softer": float(g_soft), "gamma_minus_1sigma_harder": float(g_hard),
            "note": "one parameter moved at a time; the real fit has correlated errors, so this is not a confidence band",
        },
        "thin_target_relative_error_2km_10PeV": P.thin_target_error(),
    }
    return {"p_interact_1km": {"100TeV": p100, "1PeV": p1}, "one_in_N_100TeV": 1.0 / p100,
            "earth_survival_vertical": {"100TeV": T100, "1PeV": T1}, "events_per_year": ev, "details": details}


def tables():
    E = np.logspace(3, 7, 41)
    write_csv("interaction_chance_1km.csv", ["E_GeV", "p_numu", "p_numubar", "p_mean"],
              [[f"{e:.4g}", f"{a:.4e}", f"{b:.4e}", f"{0.5 * (a + b):.4e}"]
               for e, a, b in zip(E, P.p_interact(E, 1000, "numu"), P.p_interact(E, 1000, "numubar"))])
    zen = np.array([90, 95, 100, 110, 120, 130, 140, 150, 160, 170, 180], dtype=float)
    X = P.column_depth(np.cos(np.radians(zen)))
    T = P.transmission_flavour(E, None, "mu", X=X)
    write_csv("earth_transmission_numu.csv", ["E_GeV"] + [f"zenith_{z:.0f}deg" for z in zen],
              [[f"{e:.4g}"] + [f"{v:.4e}" for v in row] for e, row in zip(E, T)],
              note="Fraction surviving the Earth, mean of nu_mu and nu_mu-bar (not nu_mu alone).")
    L = np.array([10, 20, 50, 100, 200, 500, 1000, 2000], dtype=float)
    write_csv("events_vs_size.csv", ["cube_side_m", "events_per_year"],
              [[f"{l:.0f}", f"{v:.4e}"] for l, v in zip(L, P.events_per_year(L))])


def keep_previous_crosschecks(summary):
    """Fresh clone without data_cache/: keep the cross-check fields of the committed summary, if it has them and
    its toy 1 km^3 count is the same as now, instead of overwriting them with nulls. Returns the kept figure names."""
    p = F.RESULTS / "kilometre_summary.json"
    old = json.loads(p.read_text()) if p.exists() else {}
    oh = old.get("hese_check", {})
    if oh.get("hese_public_simulation_same_flux_per_year") is None or \
            oh.get("ours_1km3_per_year") != summary["hese_check"]["ours_1km3_per_year"]:
        return []
    summary["hese_check"] = oh
    for k in ("hese_simulation", "earth_shadow_shape"):
        summary["details"][k] = old["details"][k]
    summary["hese_check"]["kept_from_previous_run"] = "cross-check files not in data_cache/; kept from the committed run"
    print("cross-check files missing: kept the committed cross-check numbers and figures")
    return [n for n in old.get("run", {}).get("figures", []) if n.startswith(("hese_check", "earth_shadow"))]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="final", choices=["preliminary", "final"])
    ap.add_argument("--fetch", action="store_true", help="download the cross-check files first")
    ap.add_argument("--no-figures", action="store_true")
    a = ap.parse_args(argv)
    t0 = time.time()
    if a.fetch:
        fetch()
    s = core_numbers()
    obs = X.hese_observed()
    hese = X.hese_mc_check()
    shape = X.earth_shadow_shape()
    ours = s["events_per_year"]["1km"]
    if hese:
        plateau = np.array(hese["ratio_selected_no_glashow_over_toy_per_bin"])
        note = (f"Not a match, and not expected to be one. Our toy counts every interaction above 60 TeV of neutrino energy "
                f"in a full 1 km^3 ({ours:.0f}/yr). IceCube's own public HESE simulation, for the same flux, keeps "
                f"{hese['per_year_selected_all_Enu']:.1f}/yr astrophysical events (about 1 in {ours / hese['per_year_selected_all_Enu']:.0f}). "
                f"Per energy bin it keeps {plateau[0]:.2f} of our count at 60-110 TeV, rising to about {plateau[-3:].mean():.2f} "
                f"above 1 PeV: the outer layers are the veto, not the counting volume, and below a few hundred TeV much "
                f"of the energy leaves (muon tracks, neutral currents) so the deposited energy falls under the 60 TeV cut. "
                f"The observed {obs['observed_per_year_above_60TeV']:.1f}/yr also contains atmospheric neutrinos and muons.")
    else:
        note = ("Cross-check files not fetched (python -m whykm.fetch); only the observed count is compared. Our toy counts "
                "every interaction in a full 1 km^3 with no veto and no deposited-energy cut, so it must exceed the observed rate.")
    summary = {
        "status": a.status,
        "p_interact_1km": {k: sig(v) for k, v in s["p_interact_1km"].items()},
        "one_in_N_100TeV": round(s["one_in_N_100TeV"], -2),
        "earth_survival_vertical": {k: sig(v, 4) for k, v in s["earth_survival_vertical"].items()},
        "events_per_year": {k: sig(v) for k, v in s["events_per_year"].items()},
        "hese_check": {
            "observed_per_year_above_60TeV": sig(obs["observed_per_year_above_60TeV"]),
            "ours_1km3_per_year": sig(ours),
            "hese_public_simulation_same_flux_per_year": sig(hese["per_year_selected_all_Enu"]) if hese else None,
            "note": note,
        },
        "sources": {
            "cross_sections": "totals: nuFATE isoscalar table NuFATECrossSections.h5 (CT10nlo, per nucleon 0.5(p+n)), exported to inputs/nufate/nufate_isoscalar_total_xs.csv; CC/NC split only: nuFATE text tables nusigma_sigma_CC/NC.dat (not isoscalar below ~1 PeV); MIT; github.com/aaronvincent/nuFATE commit 86813eb, arXiv:1706.09895",
            "earth_density": "nuFATE earth.py polynomial fit to STW105 (MIT)",
            "flux": "IceCube HESE 7.5 yr single power law: Phi_6nu = 6.37 (+1.47 -1.62) x 1e-18 GeV^-1 cm^-2 s^-1 sr^-1 at 100 TeV, gamma = 2.87 (+0.20 -0.19); arXiv:2011.03545 eq. VI.1 and Fig. VI.2",
            "hese_observed": "IceCube HESE 7.5-year data release, doi:10.21234/4EQJ-BB17 (HESE_data.json, 102 events, 60 at >= 60 TeV deposited; livetime 227,708,167.68 s from the release's HESE_fit.py)",
            "hese_simulation": "same release, HESE_mc_truth.json + HESE_mc_observable.json, weights x flux (release recipe weighter.py)",
            "effective_areas": "IceTracks-DR1 IC86-II (doi:10.7910/DVN/VKL316, CC0) and IceTracks-DR2 IC86 (doi:10.7910/DVN/MMIIZA, CC0)",
            "ice_density": "0.917 g/cm^3, textbook ice Ih",
            "detector_depth": "1.95 km, middle of the 1450-2450 m sensor depths (arXiv:1301.5361)",
        },
        "label": TOY,
        "disclaimer": F.LABEL,
        "details": {**s["details"], "hese_observed": obs, "hese_simulation": hese, "earth_shadow_shape": shape},
        "units": {"p_interact_1km": "probability", "earth_survival_vertical": "fraction, muon neutrinos, mean of nu and nubar",
                  "events_per_year": "interactions per year above 60 TeV neutrino energy inside a cube of ice, all flavours"},
    }
    kept = keep_previous_crosschecks(summary) if not hese else []
    tables()
    figs = [] if a.no_figures else (F.fig_interaction_chance(summary) + F.fig_earth_transmission(summary)
                                    + F.fig_events_vs_size(summary)
                                    + ([] if kept else F.fig_hese_check(summary, hese) + F.fig_earth_shadow(shape)))
    summary["run"] = {"seconds": round(time.time() - t0, 1), "python": platform.python_version(),
                      "numpy": np.__version__, "figures": [p.name for p in figs] + kept}
    (F.RESULTS / "kilometre_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("status", "p_interact_1km", "one_in_N_100TeV", "earth_survival_vertical",
                                                 "events_per_year", "hese_check")}, indent=2))
    print(f"done in {summary['run']['seconds']} s, {len(figs)} figures in {F.RESULTS}")


if __name__ == "__main__":
    main()
