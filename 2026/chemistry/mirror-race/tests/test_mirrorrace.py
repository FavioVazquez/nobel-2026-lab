"""Fast checks (well under a minute). Toy model, not research."""
import json
import re
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

from mirrorrace import analysis as an
from mirrorrace.sim import run

HERE = Path(__file__).resolve().parent.parent


def rng(k):
    return np.random.default_rng([4242, k])


def test_conservation_every_checkpoint():
    prog = (0.0, 0.1, 0.5, 1.0)
    for k2 in (0.0, 100.0):
        e = run(500, 300, 1.0, 1.0, k2, rng(1), progress=prog, seed_one=3)
        for j, p in enumerate(prog):
            used = round(500 * p)
            assert np.all(e.one[:, j] + e.mirror[:, j] + 2 * e.pairs[:, j] == used + 3)
        assert np.all(e.one >= 0) and np.all(e.mirror >= 0)


def test_exact_polya_formulas():
    N = 40
    assert np.allclose(an.polya_pmf(N, 1.0), 1.0 / (N + 1))           # a = 1: exactly flat
    for a in (0.5, 1.0, 10.0):
        pmf, ee = an.polya_pmf(N, a), an.polya_ee_values(N)
        assert an.polya_std_exact(N, a) == pytest.approx(np.sqrt(np.sum(pmf * ee ** 2)), rel=1e-12)
    assert an.polya_std_large_n(10.0) == pytest.approx(0.2182, abs=1e-4)  # Beta(10, 10): the prototype's 0.218


def test_ee_labels_never_round_up_to_100():
    from mirrorrace.figures import ee_label
    assert ee_label(0.996) == "+99.6%" and ee_label(-0.9856) == "-98.6%"
    assert ee_label(0.9996) == "+99.96%" and ee_label(1.0) == "+100.0%"


def test_flat_only_for_our_choice_k0_equals_k1():
    """Exact Polya answer, copying only, N = 10,000: share of runs beyond 90 % ee depends on k0/k1."""
    N = 10_000
    ee = an.polya_ee_values(N)
    beyond = {a: float(np.sum(an.polya_pmf(N, a)[np.abs(ee) > 0.9])) for a in (0.1, 1.0, 10.0)}
    assert beyond[1.0] == pytest.approx(1000 / 10001, rel=1e-9)
    assert beyond[0.1] == pytest.approx(0.755, abs=5e-4)
    assert beyond[10.0] < 1e-6
    assert an.polya_std_exact(N, 10.0) == pytest.approx(0.2184, abs=1e-4)


def test_polya_flatness_against_exact_answer():
    """Copying only, k0 = k1: every final count 0..N equally likely. Chi-square on all N+1 values."""
    N, runs = 30, 31_000
    e = run(N, runs, 1.0, 1.0, 0.0, rng(2))
    counts = np.bincount(e.one[:, -1], minlength=N + 1)
    assert stats.chisquare(counts).pvalue > 1e-3
    e10 = run(400, 8000, 10.0, 1.0, 0.0, rng(3)).ee()
    assert e10.std() == pytest.approx(an.polya_std_exact(400, 10.0), rel=0.05)
    assert an.flatness_test(e10, 400, 10.0)[1] > 1e-3


def test_racemic_stays_racemic_on_average_and_coin_is_fair():
    # 4-sigma bands, so a fair coin fails this about once in 16,000 seeds. (An earlier version with
    # 6,000 runs at N = 1,000 hit a p = 0.0005 fluke; 100,000 runs there gave 49,941 : 50,059.)
    for k2, key in ((0.0, 4), (100.0, 5)):
        ee = run(500, 20_000, 1.0, 1.0, k2, rng(key)).ee()
        assert abs(ee.mean()) < 4 * ee.std() / np.sqrt(ee.size)
        one, mir, _ = an.wins(ee)
        assert abs(one / (one + mir) - 0.5) < 4 * 0.5 / np.sqrt(one + mir)


def test_antagonism_gives_two_spikes():
    ee = run(1000, 3000, 1.0, 1.0, 100.0, rng(6)).ee()
    assert np.mean(np.abs(ee) > 0.9) > 0.9
    ee0 = run(1000, 3000, 1.0, 1.0, 0.0, rng(7)).ee()
    assert np.mean(np.abs(ee0) > 0.9) < 0.15                                 # flat: about 10%


def test_seeded_hand_wins_more_often_and_matches_exact_copy_only():
    ee = run(1000, 3000, 1.0, 1.0, 100.0, rng(8), seed_one=20).ee()
    assert np.mean(ee > 0) > 0.6
    for d in (0, 3, 20):
        ee = run(300, 6000, 1.0, 1.0, 0.0, rng(9 + d), seed_one=d).ee()
        p_exact = an.seeded_copy_only_exact(300, 1.0, d)
        assert abs(np.mean(ee > 0) - p_exact) < 4 * np.sqrt(p_exact * (1 - p_exact) / ee.size) + 1e-3


def test_real_coin_tosses():
    assert an.coin(19, 18) == pytest.approx(1.0)
    assert an.coin(27, 27) == pytest.approx(1.0)


@pytest.mark.skipif(not (HERE / "results" / "mirror_summary.json").exists(), reason="run mirrorrace.run_all first")
def test_results_files():
    s = json.loads((HERE / "results" / "mirror_summary.json").read_text())
    assert s["label"] == "our toy model, trend only" and s["status"] in ("preliminary", "final")
    assert s["real"]["soai_2003"]["runs"] == 37 and s["real"]["singleton_vo_2003"]["runs"] == 54
    assert s["conservation_ok"] is True
    for f in ("race_runs.json", "histograms.json"):
        assert (HERE / "results" / f).stat().st_size < 300_000
    h = json.loads((HERE / "results" / "histograms.json").read_text())
    assert all(len(v) == 41 and sum(v) == h["runs"] for v in h["counts"].values())


def test_no_lab_details_anywhere():
    """Safety rule: textbook level only, no reagents, quantities or conditions."""
    banned = re.compile(r"zinc|toluene|°C|mmol|mol ?%|equiv|\bmM\b|mol/L|kelvin|pyrimidine-5-carb", re.I)
    files = list((HERE / "mirrorrace").glob("*.py")) + [HERE / "README.md"]
    for f in files:
        if f.exists():
            assert not banned.search(f.read_text()), f


def test_unstirred_bonus_conserves_molecules():
    from mirrorrace import domains
    times, shots, total = domains.simulate(seed=1, grid=32, t_end=30.0, frames=5)
    assert shots.shape[1:] == (4, 32, 32) and np.all(np.diff(times) > 0)
    R, S, P, A = (shots[:, i].sum(axis=(1, 2)) for i in range(4))
    assert np.all(R + S + 2 * P + A == total) and np.all(shots >= 0)
