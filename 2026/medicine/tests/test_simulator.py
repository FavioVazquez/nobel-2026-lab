"""Tests for the educational toy simulator. Run from 2026/medicine:  python -m pytest -q tests"""
from dataclasses import replace

import numpy as np
import pytest

from simulator import heat, light, neuron, opsin


@pytest.fixture(scope="module")
def light470():
    opt = light.optics(470)
    return opt, light.simulate(opt, 20_000, seed=1)


def test_optics_from_sourced_inputs():
    o = light.optics(470)
    # Jacques 2013 brain power law: 24.2 * (470/500)^-1.611 = 26.74 cm^-1
    assert o.mus_reduced * 10 == pytest.approx(26.74, abs=0.01)
    assert o.g == 0.86  # Yona et al. 2016
    # blood composite (assumptions: 3 % blood, 75 % saturation, 150 g/L): 4.65 cm^-1 at 470 nm
    assert o.mua * 10 == pytest.approx(4.65, abs=0.01)
    # same order as Yona 2016's measured mu_s = 211 cm^-1 at 473 nm
    assert 0.8 < (o.mus * 10) / 211 < 1.0
    assert light.optics(635).mua < light.optics(590).mua < light.optics(470).mua


@pytest.mark.parametrize("wl", light.WAVELENGTHS)
def test_energy_is_conserved_inside_the_tally(wl, light470):
    """Every launched watt is absorbed inside the tally (and so reaches heat.py), red light included."""
    res = light470[1] if wl == 470 else light.simulate(light.optics(wl), 20_000, seed=2)
    assert res["absorbed"].sum() == pytest.approx(1.0, abs=0.01)


def test_exact_transport_decay():
    """P_399 plane-wave eigenvalue for Henyey-Greenstein scattering. Independent values from the review
    (B-review.md 1a): 2.0226, 1.3174, 0.3509 mm^-1. Diffusion theory is a few % too steep at 470/590 nm."""
    for wl, ref in ((470, 2.0226), (590, 1.3174), (635, 0.3509)):
        opt = light.optics(wl)
        assert light.transport_decay(opt) == pytest.approx(ref, abs=2e-4)
        assert light.transport_decay(opt) < opt.mu_eff


@pytest.mark.parametrize("wl", [470, 590])
def test_far_field_decay_matches_exact_transport(wl, light470):
    opt = light.optics(wl)
    res = light470[1] if wl == 470 else light.simulate(opt, 20_000, seed=2)
    fit, _ = light.diffusion_check(res, opt)
    assert fit == pytest.approx(light.transport_decay(opt), rel=0.02)


def test_heat_box_is_far_from_the_source():
    """The heat grid edge is >= 10 Pennes lengths (L = sqrt(k / beta), 4.2 mm) from the tip in every direction,
    and >= 7 at the lowest perfusion (5.9 mm). The old 6 mm box was 1.2-1.4 L (review S2)."""
    r, z = light._grid()
    edge = min(r[-1], -z[0], z[-1])
    for key, n in (("w_blood", 10), ("w_blood_low", 7)):
        tp = heat.thermal_params(key)
        assert edge > n * np.sqrt(tp["k"] / tp["beta"])
    assert np.allclose(np.diff(r)[:240], light.GRID["dr"]) and np.isclose(r[240], light.GRID["r_max"])


@pytest.fixture(scope="module")
def stujenske_case():
    res = light.simulate(light.optics(532), 20_000, core_radius=0.031, na=0.22, seed=3)
    g = heat.Grid(res["r_edges"], res["z_edges"])
    return res, g, res["power_density"] * 0.010  # 10 mW


def test_heat_against_stujenske_2015(stujenske_case):
    """Stujenske et al. 2015 (verified in full text): 532 nm, 10 mW continuous, 62 um NA 0.22 fibre ->
    plateau ~2.2 C averaged in 250 um-radius slices near the tip. Our optical inputs differ from theirs
    (Johansson 2010, UNVERIFIED values), so we only require agreement within a factor of 2.
    Their max voxel 4.1 C and '>=1 C within roughly 1 mm^3' are verified numbers that our hotter model
    does NOT reproduce (see run_summary.json): reported, deliberately not asserted."""
    res, g, q = stujenske_case
    T = g.steady(q)
    z = 0.5 * (res["z_edges"][1:] + res["z_edges"][:-1])
    plateau = heat.slice_mean_profile(g, T)[(z > 0) & (z < 0.5)].max()
    assert 2.2 / 2 < plateau < 2.2 * 2


def test_heat_reaches_steady_state_within_60s(stujenske_case):
    """Stujenske 2015: under 5 % additional rise from 60 to 120 s (verified)."""
    _, g, q = stujenske_case
    _, peak, _, _ = g.transient(q, [(120.0, 1.0)], 1.0)
    assert (peak[-1] - peak[60]) / peak[-1] < 0.05


def test_transient_with_per_segment_steps(stujenske_case):
    """Segments may carry their own time step; the clock and the result do not depend on the split."""
    _, g, q = stujenske_case
    t1, p1, _, _ = g.transient(q, [(0.02, 1.0)], 0.004)
    t2, p2, _, _ = g.transient(q, [(0.01, 1.0, 0.002), (0.01, 1.0, 0.005)], 0.004)
    assert t1[-1] == pytest.approx(0.02) and t2[-1] == pytest.approx(0.02)
    assert p2[-1] == pytest.approx(p1[-1], rel=0.02)


def test_heat_is_linear_and_perfusion_cools(stujenske_case):
    res, g, q = stujenske_case
    assert g.steady(2 * q).max() == pytest.approx(2 * g.steady(q).max(), rel=1e-9)
    g_hi = heat.Grid(res["r_edges"], res["z_edges"], heat.thermal_params("w_blood_high"))
    assert g_hi.steady(q).max() < g.steady(q).max()


def test_williams_table1_values():
    w = opsin.WILLIAMS
    assert (w["eps1"], w["eps2"], w["gamma"], w["tau_chr"], w["w_loss"]) == (0.8535, 0.14, 0.1, 1.3, 0.77)
    # Williams 2013: F = 0.0006 * I * lambda / w_loss (ms^-1)
    assert opsin.flux_williams(1.0, 470) == pytest.approx(0.0006 * 470 / 0.77, rel=0.01)


def test_piecewise_integration_sees_a_short_pulse():
    """data-and-tools.md gotcha: an adaptive solver can step over a pulse defined inside the RHS."""
    sw = opsin.switches(calibrated=False)[0]
    _, o, _ = opsin.clamp_trace(sw, [(50.0, 0.0), (1.0, 5.0), (50.0, 0.0)])
    assert o.max() > 0.01


def test_zero_length_segment_is_ignored():
    sw = opsin.switches(calibrated=False)[0]
    t, o, _ = opsin.clamp_trace(sw, [(5.0, 0.0), (2.0, 3.0), (0.0, 0.0), (5.0, 0.0)])
    t2, o2, _ = opsin.clamp_trace(sw, [(5.0, 0.0), (2.0, 3.0), (5.0, 0.0)])
    assert t[-1] == pytest.approx(12.0) and o[-1] == pytest.approx(o2[-1], rel=1e-6)


def test_headline_speed_stops_at_the_first_failure():
    """The headline is the last rate before the first failure; later 1:1 windows are reported, not used."""
    rates = (10, 20, 50, 125, 140, 150, 200)
    frac = (1.0, 1.0, 0.95, 0.35, 1.0, 1.0, 0.2)  # 0.95 of 20 pulses = exactly one miss: still follows
    assert neuron.headline(rates, frac) == (50.0, 125.0, [140.0, 150.0])
    assert neuron.headline(rates, (0.5,) * 7) == (0.0, 10.0, [])
    assert neuron.headline(rates, (1.0,) * 7) == (200.0, None, [])


def test_spiking_is_converged_in_the_time_step():
    """Following fractions do not move when the neuron's step is halved (they did at the old 0.025 ms Euler step)."""
    sw = opsin.switches(calibrated=False)[0]
    rates = (50, 60, 70, 140)
    a = neuron.following([sw], rates, n_pulses=10)[sw.name]
    b = neuron.following([sw], rates, n_pulses=10, dt=neuron.DT / 2)[sw.name]
    assert a["fraction"][0] == 1.0  # the toy cell spikes 1:1 at 50 Hz
    assert np.array_equal(a["fraction"], b["fraction"])


def test_fixed_step_neuron_matches_lsoda_in_voltage_clamp():
    sw = opsin.switches(calibrated=False)[0]
    t, o, _ = opsin.clamp_trace(sw, [(20.0, 0.0), (2.0, 3.0), (30.0, 0.0)], V=neuron.V_REST, dt_out=neuron.DT)
    light_, _ = neuron.pulse_mask([1.0], 1, 2.0, 3.0, t_pad=0.0)
    _, Is = neuron.simulate(sw, light_[: len(t)], 1.0, clamp_V=neuron.V_REST)
    ref = o * opsin.drive(sw, neuron.V_REST)
    assert Is.min() == pytest.approx(ref.min(), rel=0.03)


def test_simplified_switches_hit_published_off_times():
    sws = {s.name: s for s in opsin.switches()}
    assert opsin.tau_off(sws["Chronos (simplified)"]) == pytest.approx(3.6, abs=0.05)  # Klapoetke 2014
    assert opsin.tau_off(sws["ChrimsonR (simplified)"]) == pytest.approx(15.8, abs=0.05)  # Klapoetke 2014


def test_fast_switch_follows_faster_than_slow_switch():
    sws = {s.name: s for s in opsin.switches()}
    res = neuron.following([sws["Chronos (simplified)"], sws["ChrimsonR (simplified)"]], (20, 100), n_pulses=8)
    assert res["Chronos (simplified)"]["max_rate"] == 100
    assert res["ChrimsonR (simplified)"]["max_rate"] < 100


def test_tradeoff_splits_colour_from_switch():
    """Reach and heat are colour properties (all switches share ChR2's light sensitivity); speed is per switch."""
    from simulator import tradeoff
    from simulator.common import RESULTS

    lights = {wl: dict(fluence=np.load(RESULTS / f"light_fibre200um_{wl}nm.npz")["fluence_per_W"].astype(float))
              for wl in light.WAVELENGTHS}
    d = np.load(RESULTS / "light_fibre200um_470nm.npz")
    g = heat.Grid(d["r_edges"], d["z_edges"])
    heat_by_wl = {wl: dict(peak_per_mW=0.1 * i, peak_per_mW_low=0, peak_per_mW_high=0, slice_per_mW=0)
                  for i, wl in enumerate(light.WAVELENGTHS)}
    colours = tradeoff.colour_rows(lights, heat_by_wl, g)
    assert [r["wavelength_nm"] for r in colours] == [470, 590, 635]
    reach = [r["volume_mm3_per_mW_at_3mWmm2"] for r in colours]
    assert len(set(reach)) == 3 and reach[0] < reach[1] < reach[2]
    sws = opsin.switches(calibrated=False)
    rows = tradeoff.switch_rows(sws, {s.name: dict(max_rate=10.0 * (i + 1)) for i, s in enumerate(sws)})
    assert len(rows) == len(sws)
    assert all(r["volume_mm3_per_mW_at_3mWmm2"] == "" and r["peak_warming_C_per_mW"] == "" for r in rows)
    text = (RESULTS / "tradeoff.csv").read_text()
    assert "Red result ignores absorption outside blood" in text and "row,name,wavelength_nm" in text
    assert "first failure ends the run" in text and "at least 20 Hz, comparable to ChR2(H134R)" in text
    assert "follows_again_Hz" in text and "read the order, not the numbers" in text
