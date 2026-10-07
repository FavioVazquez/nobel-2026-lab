"""Exact checks of the ML2 closed form. Dimensionless; toy model, not research."""
import numpy as np
import pytest
from scipy.optimize import brentq

from kagan import constants as C
from kagan import model as M

E = np.linspace(-1, 1, 401)


def test_pie_matches_nobel_popular_figure():
    p = M.pie(75.0, K=4.0, g=0.0)
    assert p["ee_L_pct"] == pytest.approx(50.0, abs=1e-12)
    assert p["catalysts_pct"] == pytest.approx(list(C.PIE_CATALYSTS_PCT), abs=1e-12)
    assert p["effective"] == pytest.approx(list(C.PIE_EFFECTIVE), abs=1e-12)
    assert p["ee_prod_pct"] == pytest.approx(C.PIE_EE_PROD_PCT, abs=1e-12)
    assert [round(v) for v in p["catalysts_pct"]] == [56, 38, 6]


@pytest.mark.parametrize("K", [0.01, 1.0, 3.9, 4.0, 4.1, 25.0, 1e3])
def test_constraints_hold(K):
    x, y, z = M.complexes(E, K)
    assert np.allclose(x + y + z, 1, atol=1e-13)
    assert np.allclose(x - y, E, atol=1e-13)
    inner = np.abs(E) < 0.999
    assert np.allclose(z[inner] ** 2, K * x[inner] * y[inner], rtol=1e-9, atol=1e-15)
    assert (x >= -1e-15).all() and (y >= -1e-15).all() and (z >= 0).all()


@pytest.mark.parametrize("K", [0.5, 4.0, 77.0])
def test_closed_form_equals_root_finder(K):
    for e in (0.0, 0.1, 0.37, 0.8, 0.99):
        f = lambda z: z * z - K * (1 - z + e) / 2 * (1 - z - e) / 2  # noqa: E731
        assert float(M.mixed_fraction(e, K)) == pytest.approx(brentq(f, 0, 1 - e, xtol=1e-15), abs=1e-12)


def test_k4_is_statistical_and_g0_closed_form():
    assert np.allclose(M.mixed_fraction(E, 4.0), (1 - E ** 2) / 2, atol=1e-15)
    for em in (1.0, 0.9):
        assert np.allclose(M.ee_prod(E, 4.0, 0.0, em), M.reservoir_k4_g0(E, em), atol=1e-14)


def test_g1_is_straight_line():
    for K in (0.3, 4.0, 300.0):
        assert np.allclose(M.ee_prod(E, K, 1.0, 0.7), 0.7 * E, atol=1e-14)


def test_bulge_and_sag():
    e = np.linspace(0.05, 0.95, 19)
    for K in (1.0, 4.0, 100.0):
        assert (M.ee_prod(e, K, 0.3) > e).all()
        assert (M.ee_prod(e, K, 3.0) < e).all()


def test_never_above_ee_max():
    for K in (0.1, 4.0, 1e4, float("inf")):
        for g in (0.0, 0.2, 1.0, 5.0):
            assert (np.abs(M.ee_prod(E, K, g, 0.83)) <= 0.83 + 1e-12).all()


def test_irreversible_mixed_pair_gives_ee_max():
    e = np.array([0.01, 0.1, 0.5, 0.9])
    assert np.allclose(M.ee_prod(e, float("inf"), 0.0, 0.9), 0.9, atol=1e-15)
    assert np.allclose(M.ee_prod(e, 1e14, 0.0, 0.9), 0.9, atol=1e-5)


def test_odd_symmetry_and_endpoints():
    for K, g in ((4.0, 0.0), (50.0, 3.0)):
        assert np.allclose(M.ee_prod(-E, K, g), -M.ee_prod(E, K, g), atol=1e-15)
        assert M.ee_prod(0.0, K, g) == 0.0
        assert M.ee_prod(1.0, K, g, 0.9) == pytest.approx(0.9, abs=1e-15)


def test_erosion_staircase():
    assert M.erosion(0.9, 4) == pytest.approx([1.0, 0.9, 0.81, 0.729, 0.6561], abs=1e-15)
