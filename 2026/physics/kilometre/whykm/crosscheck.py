"""Honest cross-checks of the toy against IceCube's public files (see fetch.py for where they come from).

Educational demo made to show an open-source tool. Toy model, not research.

A. HESE 7.5 years (doi:10.21234/4EQJ-BB17): what was observed, and what the collaboration's OWN public
   simulation expects for the same flux. Splitting the toy-to-observed gap into steps shows where events
   are lost (fiducial volume and veto, deposited energy below 60 TeV, ...).
B. Track effective areas (DR1 IC86-II, DR2 IC86; CC0): only the SHAPE of the Earth shadow is compared,
   because those samples catch muons made far outside the detector, which a "contained" toy does not.
"""
import json

import numpy as np

from . import constants as C
from . import physics as P
from .fetch import CACHE, HESE_FILES, have

HESE_BINS_GEV = np.logspace(np.log10(6e4), 7, 9)  # 60 TeV .. 10 PeV, 8 log bins (choice)


# ---------------------------------------------------------------------------------- A. HESE ------
def hese_observed():
    """Counts from the public data file if present, else the counts written in constants.py."""
    if have("HESE_data.json"):
        d = json.loads((CACHE / "HESE_data.json").read_text())
        e = np.asarray(d["recoDepositedEnergy"], dtype=float)
        n, n60, src = int(e.size), int((e >= C.HESE_E_CUT_GEV).sum()), "HESE_data.json"
    else:
        n, n60, src = C.HESE_N_EVENTS, C.HESE_N_ABOVE_60TEV, "constants.py (file not fetched)"
    years = C.HESE_LIVETIME_S / C.SECONDS_PER_YEAR
    return {"n_events": n, "n_above_60TeV": n60, "livetime_years": years,
            "observed_per_year_above_60TeV": n60 / years, "counted_from": src}


def _load_hese_mc():
    mc = {}
    for f in ("HESE_mc_truth.json", "HESE_mc_observable.json"):
        mc.update(json.loads((CACHE / f).read_text()))
    keys = ("primaryEnergy", "weightOverFluxOverLivetime", "recoDepositedEnergy", "recoMorphology", "recoLength", "interactionType")
    return {k: np.asarray(mc[k], dtype=float) for k in keys}


def toy_per_bin(edges=HESE_BINS_GEV, side_m=1000.0):
    """Toy interactions per year inside the cube, in bins of neutrino energy."""
    return np.array([P.events_per_year(side_m, e_min=lo, e_max=hi, n_e=80) for lo, hi in zip(edges[:-1], edges[1:])])


def hese_mc_check(phi=C.HESE_PHI_ASTRO, gamma=C.HESE_GAMMA):
    """Astrophysical events per year in the HESE public simulation, for the same flux as the toy.
    rate = sum over simulated events of weightOverFluxOverLivetime x flux per species (the release's own
    recipe, weighter.py). No detector-systematics corrections, no atmospheric or muon backgrounds."""
    if not all(have(n) for n in ("HESE_mc_truth.json", "HESE_mc_observable.json")):
        return None
    mc = _load_hese_mc()
    E = mc["primaryEnergy"]
    nu = mc["weightOverFluxOverLivetime"] > 0
    rate = np.where(nu, mc["weightOverFluxOverLivetime"] * P.flux_per_species(E, phi, gamma), 0.0) * C.SECONDS_PER_YEAR
    edep, morph, length = mc["recoDepositedEnergy"], mc["recoMorphology"], mc["recoLength"]
    with np.errstate(invalid="ignore"):
        dep_ok = (edep >= 6e4) & (edep <= 1e7)
        sel = dep_ok & ((morph != 2) | ((length >= 10) & (length <= 1000)))  # the release's load_mc cuts
    true_in = (E >= C.E_THRESHOLD_GEV) & (E <= C.E_MAX_GEV)
    edges = HESE_BINS_GEV
    per_bin_true = np.histogram(E[true_in], edges, weights=rate[true_in])[0]  # passes HESE trigger/veto, any E_dep
    per_bin_sel = np.histogram(E[sel], edges, weights=rate[sel])[0]
    gr = sel & (mc["interactionType"] == 3)  # Glashow resonance (nubar_e + electron -> W), not in the toy
    per_bin_gr = np.histogram(E[gr], edges, weights=rate[gr])[0]
    toy = toy_per_bin(edges)
    return {
        "per_year_selected_all_Enu": float(rate[sel].sum()),
        "per_year_selected_Enu_60TeV_10PeV": float(rate[sel & true_in].sum()),
        "per_year_any_Edep_Enu_60TeV_10PeV": float(rate[true_in].sum()),
        "bins_GeV": edges.tolist(),
        "toy_1km3_per_bin": toy.tolist(),
        "hese_mc_any_Edep_per_bin": per_bin_true.tolist(),
        "hese_mc_selected_per_bin": per_bin_sel.tolist(),
        "hese_mc_selected_glashow_per_bin": per_bin_gr.tolist(),
        "per_year_selected_glashow": float(rate[gr].sum()),
        "ratio_selected_over_toy_per_bin": (per_bin_sel / toy).tolist(),
        "ratio_selected_no_glashow_over_toy_per_bin": ((per_bin_sel - per_bin_gr) / toy).tolist(),
        "ratio_any_Edep_over_toy_per_bin": (per_bin_true / toy).tolist(),
        "n_mc_events_used": int(nu.sum()),
    }


# ------------------------------------------------------------------- B. track effective areas ----
def read_aeff(name):
    t = np.loadtxt(CACHE / name, comments="#")
    return {"logE_lo": t[:, 0], "logE_hi": t[:, 1], "dec_lo": t[:, 2], "dec_hi": t[:, 3], "A_cm2": t[:, 4]}


def aeff_band(a, dec_deg):
    """Effective area vs energy for the declination band that contains dec_deg."""
    m = (a["dec_lo"] <= dec_deg) & (a["dec_hi"] > dec_deg)
    order = np.argsort(a["logE_lo"][m])
    lo, hi = a["logE_lo"][m][order], a["logE_hi"][m][order]
    band = (float(a["dec_lo"][m][0]), float(a["dec_hi"][m][0]))
    return 10 ** (0.5 * (lo + hi)), a["A_cm2"][m][order], band


def toy_contained_aeff(E_gev, cos_zenith, side_m=1000.0):
    """Toy 'effective area' for nu_mu CC interactions inside the cube: n V sigma_CC x Earth transmission
    (cm^2, mean of nu and nubar). No muon range, no light, no selection."""
    s_nu, s_nub = P.sigma_pair(E_gev, "mu", "CC")
    X = float(P.column_depth(cos_zenith))
    T_nu = np.exp(-s_nu * X * C.NUCLEONS_PER_GRAM)
    T_nub = np.exp(-s_nub * X * C.NUCLEONS_PER_GRAM)
    return P.nucleons_in_cube(side_m) * 0.5 * (s_nu * T_nu + s_nub * T_nub)


def earth_shadow_shape(dec_up=60.0, dec_ref=0.0):
    """Ratio A(dec_up) / A(dec_ref) per energy in the public tables vs the toy transmission ratio.
    At the South Pole, zenith = 90 deg + declination, so dec +60 means 30 deg below the horizon."""
    out = {}
    for name in ("dr1_IC86_II_effectiveArea.csv", "dr2_IC86_effectiveArea.csv"):
        if not have(name):
            continue
        a = read_aeff(name)
        E, A_up, band_up = aeff_band(a, dec_up)
        _, A_ref, band_ref = aeff_band(a, dec_ref)
        ok = (E >= 1e3) & (E <= 1e7) & (A_ref > 0)
        cz_up = np.cos(np.radians(90 + 0.5 * sum(band_up)))
        cz_ref = np.cos(np.radians(90 + 0.5 * sum(band_ref)))
        toy = toy_contained_aeff(E[ok], cz_up) / toy_contained_aeff(E[ok], cz_ref)
        out[name] = {"E_GeV": E[ok].tolist(), "public_ratio": (A_up[ok] / A_ref[ok]).tolist(),
                     "toy_ratio": toy.tolist(), "dec_band_up": band_up, "dec_band_ref": band_ref,
                     "A_ref_cm2": A_ref[ok].tolist(), "toy_A_ref_cm2": toy_contained_aeff(E[ok], cz_ref).tolist()}
    return out


def all_present():
    return all(have(n) for n in HESE_FILES)
