"""Tests for the "why a cubic kilometre" toy. Run from 2026/physics/kilometre:  python -m pytest -q tests
Educational demo made to show an open-source tool. Toy model, not research."""
import importlib.util
import json

import numpy as np
import pytest
from scipy.integrate import quad

from whykm import constants as C
from whykm import crosscheck as X
from whykm import physics as P
from whykm.run_all import core_numbers


def _nufate_earth():
    spec = importlib.util.spec_from_file_location("nufate_earth", P.NUFATE / "earth.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- cross sections ---------------
def test_cross_sections_rise_and_nu_beats_nubar():
    E = np.logspace(3, 7, 30)
    for s in P.SPECIES:
        assert np.all(np.diff(P.sigma(E, s)) > 0)
    assert P.sigma(1e5, "numu") > P.sigma(1e5, "numubar")
    assert P.sigma(1e5, "nue") == pytest.approx(P.sigma(1e5, "numu"))  # same table column values (lepton universality)


def test_cross_section_close_to_gqrs_fit_at_10PeV():
    """Gandhi, Quigg, Reno, Sarcevic (hep-ph/9807264) eq. 10, valid 1e7-1e12 GeV: 5.53e-36 (E/GeV)^0.363 cm^2 (CC)."""
    gqrs = 5.53e-36 * 1e7**0.363
    assert P.sigma(1e7, "numu", "CC") == pytest.approx(gqrs, rel=0.05)


def test_interpolation_hits_table_nodes():
    e, cols = P._table("tot")
    i = 100
    assert P.sigma(e[i], "numubar") == pytest.approx(cols["numubar"][i], rel=1e-9)
    assert P.sigma(1e5, "numu", "CC") + P.sigma(1e5, "numu", "NC") == pytest.approx(P.sigma(1e5, "numu"), rel=1e-12)
    with pytest.raises(ValueError):
        P.sigma(10.0)


def test_cross_sections_are_isoscalar_nu_nubar_ratio_at_1TeV():
    """Isoscalar target: sigma(nubar)/sigma(nu) is about 0.57 at 1 TeV (nuFATE's isoscalar table; textbook
    CC values 0.33/0.68 ~ 0.5). The non-isoscalar nuSQuIDS text tables give 0.377 and must fail this."""
    r = P.sigma(1e3, "numubar") / P.sigma(1e3, "numu")
    assert 0.5 < r < 0.65
    cc, nc = P._table("CC"), P._table("NC")
    i = np.argmin(abs(cc[0] - 1e3))
    txt = (cc[1]["numubar"][i] + nc[1]["numubar"][i]) / (cc[1]["numu"][i] + nc[1]["numu"][i])
    assert not 0.5 < txt < 0.65  # the test can tell the two apart


# ---------------------------------------------------------------- (1) interaction chance -------
def test_interaction_chance_is_n_sigma_L_when_small():
    p = P.p_interact(1e5, 1000.0, "numu")
    n_sigma_L = C.RHO_ICE * C.N_A * P.sigma(1e5, "numu") * 1e5
    assert p == pytest.approx(n_sigma_L, rel=1e-4)
    assert 1e-5 < P.p_interact_flavour(1e5) < 2e-5  # "one in tens of thousands"; toy, trend only


# ---------------------------------------------------------------- (2) Earth ---------------------
@pytest.mark.parametrize("zenith_deg", [180.0, 160.0, 140.0, 120.0, 100.0])
def test_column_depth_matches_original_nufate_function(zenith_deg):
    """Our vectorised integral vs nuFATE's own get_t_earth (scipy quad), shipped unmodified in inputs/nufate."""
    ref = _nufate_earth().get_t_earth(np.radians(zenith_deg), d=C.DETECTOR_DEPTH_KM)
    assert P.column_depth(np.cos(np.radians(zenith_deg))) == pytest.approx(ref, rel=2e-3)


def test_vertical_column_and_path():
    assert P.path_length_km(-1.0) == pytest.approx(2 * C.R_EARTH_KM - C.DETECTOR_DEPTH_KM)
    assert P.path_length_km(1.0) == pytest.approx(C.DETECTOR_DEPTH_KM)
    assert 1.0e10 < P.column_depth(-1.0) < 1.2e10  # the usual "about 1.1e10 g/cm^2" through the centre


def test_transmission_limits_and_order():
    cz = np.array([-1.0, -0.5, -0.1, 0.5])
    X_ = P.column_depth(cz)
    T_low = P.transmission_flavour(1e3, None, "mu", X=X_)
    assert np.all(T_low > 0.95)  # at 1 TeV the Earth is nearly transparent
    T = P.transmission_flavour(1e6, None, "mu", X=X_)
    assert np.all(np.diff(T) > 0)  # less matter, more survive
    assert T[-1] > 0.999  # coming from above
    assert 1e-3 < T[0] < 5e-3  # straight up at 1 PeV: a few per thousand (toy, trend only)


# ---------------------------------------------------------------- (3) events vs size ------------
def test_events_scale_with_volume():
    n = P.events_per_year(np.array([10.0, 100.0, 1000.0]))
    assert n[1] / n[0] == pytest.approx(1000.0)
    assert n[2] / n[1] == pytest.approx(1000.0)
    assert P.thin_target_error() < 1e-3


def test_rate_integral_against_scipy_quad():
    """No Earth: rate per nucleon = 4 pi * integral of flux x sigma, for one species."""
    f = lambda lnE: P.flux_per_species(np.exp(lnE)) * P.sigma(np.exp(lnE), "nue") * np.exp(lnE)
    ref = 4 * np.pi * quad(f, np.log(6e4), np.log(1e7), limit=200)[0] * C.SECONDS_PER_YEAR
    ours = P.events_per_year_per_nucleon(species=("nue",), earth=False)
    assert ours == pytest.approx(ref, rel=1e-3)


def test_angular_integral_is_full_sky_without_earth():
    r = P.rate_density(np.array([1e5]), "numu", earth=False)
    assert r[0] == pytest.approx(P.flux_per_species(1e5) * P.sigma(1e5, "numu") * 4 * np.pi, rel=1e-6)


def test_earth_removes_part_of_the_upgoing_half():
    up = P.events_per_year(1000, hemisphere="up")
    down = P.events_per_year(1000, hemisphere="down")
    free = P.events_per_year(1000, earth=False)
    assert up < down < free / 2 * 1.001
    assert up + down == pytest.approx(P.events_per_year(1000), rel=1e-3)


def test_summary_keys():
    s = core_numbers()
    assert set(s["p_interact_1km"]) == {"100TeV", "1PeV"}
    assert set(s["events_per_year"]) == {"10m", "100m", "1km"}
    assert s["one_in_N_100TeV"] == pytest.approx(1 / s["p_interact_1km"]["100TeV"])


# ---------------------------------------------------------------- cross-checks (need data_cache) --
def test_hese_observed_counts():
    o = X.hese_observed()
    assert o["n_events"] == 102 and o["n_above_60TeV"] == 60
    assert o["livetime_years"] == pytest.approx(C.HESE_LIVETIME_DAYS / 365.25, rel=1e-3)


@pytest.mark.skipif(not X.have("dr2_IC86_effectiveArea.csv"), reason="run python -m whykm.fetch first")
def test_effective_area_table_reads():
    a = X.read_aeff("dr2_IC86_effectiveArea.csv")
    E, A, band = X.aeff_band(a, 0.0)
    assert band[0] <= 0.0 < band[1] and np.all(np.diff(E) > 0) and A.max() > 1e6  # > 100 m^2 somewhere


def test_written_summary_has_the_label_if_present():
    p = X.CACHE.parent / "results" / "kilometre_summary.json"
    if not p.exists():
        pytest.skip("run python -m whykm.run_all first")
    s = json.loads(p.read_text())
    assert s["label"] == "our toy model, trend only" and s["status"] in ("preliminary", "final")
