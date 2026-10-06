"""Tests for the heat budget (educational demo, toy model). Run from 2026/medicine/heat-budget:
    python -m pytest -q tests
"""
import numpy as np
import pytest

from heat_budget import common, recipe, recruit


def test_neuron_exactly_at_threshold_is_recruited():
    t = recruit.THRESHOLD
    assert recruit.is_recruited(t, 1.0)
    assert recruit.is_recruited(t / 2, 2.0)
    assert not recruit.is_recruited(np.nextafter(t, 0), 1.0)
    # and the sampled population agrees: a neuron is counted exactly at its recruitment power
    assert recruit.counts(np.array([2.0]), np.array([2.0]))[0] == 1


@pytest.fixture(scope="module")
def cells470():
    return recruit.tissue_cells(470)


def test_recruitment_is_monotonic_in_power(cells470):
    pop = recruit.sample(cells470, 3.0, sigma=0.5, density=2_000.0, seed=3)
    powers = np.linspace(0, 3.0, 50)
    n = recruit.counts(pop["p_star"], powers)
    assert n[0] == 0 and n[-1] == pop["p_star"].size > 0
    assert np.all(np.diff(n) >= 0)
    assert np.all(np.diff(recruit.expected_count(cells470, powers, 0.5, 2_000.0)) >= 0)


def test_sample_matches_expected_count(cells470):
    pop = recruit.sample(cells470, 2.0, sigma=0.5, density=20_000.0, seed=4)
    exp = recruit.expected_count(cells470, [2.0], 0.5, 20_000.0)[0]
    assert abs(pop["p_star"].size - exp) < 5 * np.sqrt(exp)
    assert np.all(pop["p_star"] <= 2.0 * (1 + 1e-12))


def test_seeds_make_results_reproducible(cells470):
    a = recruit.sample(cells470, 2.0, 0.5, 5_000.0, seed=7, positions=True)
    b = recruit.sample(cells470, 2.0, 0.5, 5_000.0, seed=7, positions=True)
    c = recruit.sample(cells470, 2.0, 0.5, 5_000.0, seed=8)
    assert np.array_equal(a["p_star"], b["p_star"]) and np.array_equal(a["x"], b["x"])
    assert not (a["p_star"].size == c["p_star"].size and np.array_equal(a["p_star"], c["p_star"]))


def test_heat_scaling_is_linear():
    k = common.steady_per_mW(470)
    assert 0.3 < k < 0.45  # B's run_summary: 0.380 C/mW at 470 nm
    w1 = common.warming_C(470, 1.0, 2.0, 40)
    assert common.warming_C(470, 3.0, 2.0, 40) == pytest.approx(3 * w1, rel=1e-12)
    q = common.source_per_mW(470)
    g = common.grid()
    assert g.steady(2.5 * q).max() == pytest.approx(2.5 * g.steady(q).max(), rel=1e-9)
    # continuous light (duty 1) can never be beaten by the pulsed estimate
    assert common.warming_C(470, 1.0, 5.0, 200) == pytest.approx(k)


def test_warming_estimate_bounds_an_explicit_pulse_train():
    """The recipe's warming estimate must not undershoot B's transient for a real pulse train."""
    q, g = common.source_per_mW(470), common.grid()
    width, rate, secs = 5.0, 20, 1.0
    period = 1000.0 / rate
    segs = [(width * 1e-3, 1.0), ((period - width) * 1e-3, 0.0)] * int(secs * rate)
    _, peak, _, _ = g.transient(q, segs, 2.5e-3)
    assert peak.max() <= common.warming_C(470, 1.0, width, rate)


def test_recipe_never_exceeds_the_limit():
    sws = recipe.pick_switches(("Chronos (simplified)",))
    widths, rates, powers = (1.0, 5.0), (20, 100), (0.5, 2.0, 8.0)
    scores, _ = recipe.following_scores(sws, widths, rates, powers, n_pulses=4)
    rows = recipe.grid_table(sws, scores, widths, rates, powers)
    assert rows and all(0.0 <= r["following_score"] <= 1.0 for r in rows)
    for lim in common.LIMITS_C:
        best = recipe.best_recipe(rows, "Chronos (simplified)", lim)
        assert best is not None and best["warming_C_estimate"] <= lim
        assert best["warming_C_estimate"] == pytest.approx(
            float(common.warming_C(470, best["peak_mW"], best["width_ms"], best["rate_Hz"])))
    assert recipe.best_recipe(rows, "Chronos (simplified)", 1e-6) is None


def test_red_is_only_a_labelled_toy_upper_bound():
    """The headline pair is 470 and 590 nm; 635 nm appears only as a labelled toy upper bound."""
    import json

    assert recruit.HEADLINE_COLOURS == (470, 590) and "toy upper bound" in recruit.UPPER_BOUND_NOTE
    s = json.loads((common.RESULTS / "summary.json").read_text())
    assert set(s["neurons_recruited_continuous_light"]) == {"470", "590"}
    assert set(s["recruited_at_1C_by_expression_spread"]) == {"470", "590"}
    assert "toy upper bound" in s["toy_upper_bound_only"]["635"]["note"]
