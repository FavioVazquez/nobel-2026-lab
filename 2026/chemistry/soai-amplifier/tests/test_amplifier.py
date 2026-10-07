"""Checks of the three layers. Dimensionless; toy model, not research."""
import numpy as np
import pytest
from scipy.integrate import solve_ivp

from amplifier import constants as C
from amplifier import model as M

EE0 = C.SOAI_2003_PCT[0] / 100  # 5e-7


# ---------------- layer 1: exact ----------------
def test_blackmond_statements():
    assert 100 * M.layer1_ee(1e-4, 1 + 1e4) == pytest.approx(61.8, abs=0.05)  # "just over 60 %"
    assert 100 * M.layer1_ee(5e-3, 1 + 1e4) == pytest.approx(99.0, abs=0.05)  # "approaches homochirality"


def test_golden_ratio():
    # ee0 * P / (1 - ee0^2) = 1 gives E/(1 - E^2) = 1, i.e. E = (sqrt(5) - 1)/2
    e0 = 1e-3
    assert float(M.layer1_ee(e0, (1 - e0 ** 2) / e0)) == pytest.approx((5 ** 0.5 - 1) / 2, abs=1e-12)


def test_conserved_quantity_along_a_direct_simulation():
    """Integrate dR/dn = x, dS/dn = y with random pairing (x ~ R^2, y ~ S^2): 1/S - 1/R stays put."""
    def rhs(n, u):
        R, S = u
        return [R * R / (R * R + S * S), S * S / (R * R + S * S)]
    sol = solve_ivp(rhs, (0, 500), [0.6, 0.4], rtol=1e-12, atol=1e-14, dense_output=True)
    c = M.layer1_conserved(*sol.sol(np.linspace(0, 500, 50)))
    assert np.allclose(c, c[0], rtol=1e-8)
    R, S = sol.y[:, -1]
    assert (R - S) / (R + S) == pytest.approx(float(M.layer1_ee(0.2, (R + S))), abs=1e-9)


def test_k4_needs_about_1p7_million_turnovers():
    n = M.layer1_factor_needed(EE0, 0.57) - 1
    assert 1.68e6 < n < 1.70e6
    assert float(M.layer1_ee(EE0, 1 + n)) == pytest.approx(0.57, abs=1e-9)


# ---------------- layer 2 ----------------
def test_general_K_integrator_matches_exact_K4():
    f = np.array([2.0, 50.0, 1e3, 1e6])
    num = M.toy_ee(1e-3, f, 4.0 * (1 + 1e-12))
    assert np.allclose(num, M.layer1_ee(1e-3, f), rtol=1e-6)


def test_growth_exponent_small_ee():
    # at small ee, beta -> sqrt(K)/2, so ee grows like P^(sqrt(K)/2)
    for K in (4.0, 73.0, 1000.0):
        assert float(M.growth_exponent(1e-12, K)) == pytest.approx(np.sqrt(K) / 2, rel=1e-9)


def test_fit_reproduces_rounds_1_and_2_and_round_3_clears_99p5():
    K, N = M.fit_two_rounds(EE0, 0.57, 0.99)
    ee = M.toy_rounds(EE0, K, N, 3)
    assert ee[0] == pytest.approx(0.57, abs=1e-6) and ee[1] == pytest.approx(0.99, abs=1e-6)
    assert ee[2] > 0.995
    assert 30 < K < 200 and 10 < N < 100


def test_k4_fails_with_modest_turnovers():
    for n in (5.0, 50.0):
        assert (M.toy_rounds(EE0, 4.0, n, 3) < 0.1).all()


def test_more_mixed_pairing_amplifies_faster():
    ees = [M.toy_rounds(EE0, K, 5.0, 1)[0] for K in (4.0, 30.0, 300.0, 3000.0)]
    assert all(a < b for a, b in zip(ees, ees[1:]))


def test_hand_amounts():
    one, mir = M.hand_amounts(0.5, 8.0)
    assert (one, mir) == (6.0, 2.0)


# ---------------- layer 3 ----------------
def test_buhse_fig1_about_85_percent():
    out = M.buhse_run(C.BUHSE_EE0, cat0=C.BUHSE_CAT0, t_end=C.BUHSE_T_END)
    assert out["ok"] and out["A_final"] < 1e-3
    assert 100 * out["ee_final"] == pytest.approx(84.9, abs=0.2)


def test_racemic_stays_racemic():
    out = M.buhse_run(0.0, cat0=C.BUHSE_CAT0, t_end=C.BUHSE_T_END)
    assert out["ee_final"] == 0.0


def test_mirror_symmetry():
    a = M.buhse_run(1e-3, t_end=C.BUHSE_T_END, k2=1e4)["ee_final"]
    b = M.buhse_run(-1e-3, t_end=C.BUHSE_T_END, k2=1e4)["ee_final"]
    assert a == pytest.approx(-b, abs=1e-9)


def test_k2_switch():
    weak = M.buhse_run(C.BUHSE_EE0, t_end=C.BUHSE_T_END, k2=1e2)["ee_final"]
    strong = M.buhse_run(C.BUHSE_EE0, t_end=C.BUHSE_T_END, k2=1e4)["ee_final"]
    assert abs(weak) < 1e-4 and strong > 0.5


def test_sum_difference_form_equals_hand_by_hand_form():
    """Same model, two codings: final ee agrees for a non-tiny start (where round-off does not matter)."""
    p = M.BUHSE_FIG1
    e0, cat = 0.2, 0.1
    s = solve_ivp(M._naive_rhs, (0, C.BUHSE_T_END), [1, 1, cat * (1 + e0) / 2, cat * (1 - e0) / 2, 0, 0, 0],
                  method="Radau", args=tuple(p[n] for n in ("k0", "k1", "k2", "k3", "k4", "k5")), rtol=1e-10,
                  atol=1e-14)
    A, Z, R, S, RR, SS, RS = s.y[:, -1]
    naive = (R + 2 * RR - S - 2 * SS) / (R + S + 2 * RR + 2 * SS + 2 * RS)
    assert M.buhse_run(e0, cat0=cat, t_end=C.BUHSE_T_END)["ee_final"] == pytest.approx(naive, abs=1e-6)


def test_jacobian_matches_finite_differences():
    rng = np.random.default_rng(0)
    p = tuple(M.BUHSE_FIG1[n] for n in ("k0", "k1", "k2", "k3", "k4", "k5"))
    u = rng.uniform(0.01, 0.5, 7)
    J = M._buhse_jac(0, u, *p)
    h = 1e-7
    for j in range(7):
        du = np.zeros(7)
        du[j] = h
        col = (np.array(M._buhse_rhs(0, u + du, *p)) - np.array(M._buhse_rhs(0, u - du, *p))) / (2 * h)
        assert np.allclose(J[:, j], col, rtol=1e-5, atol=1e-6 * max(1, np.abs(col).max()))


def test_selectivity_90_levels_off_near_90():
    """With 90 % selective same-hand pairs the climb stops where the mixed fraction z = 1 - ee_max.
    Exact for K = 4 (z = (1 - e^2)/2): e = sqrt(0.8) = 89.44 %."""
    assert M.toy_ee(EE0, [1e40], 4.0, ee_max=0.9)[0] == pytest.approx(np.sqrt(0.8), rel=1e-6)
    K, N = M.fit_two_rounds(EE0, 0.57, 0.99)
    ee = M.toy_rounds(EE0, K, N, 8, ee_max=0.9)
    assert M.mixed_fraction(ee[-1], K) == pytest.approx(0.1, rel=1e-6)
    assert 0.899 < ee[-1] < 0.9 and ee[1] > 0.85                      # still climbs from 0.00005 %
    assert M.toy_rounds(EE0, K, N, 3, ee_max=1.0)[2] > 0.9997          # the 99.98 % needs ee_max = 100 %


def test_naive_drift_depends_on_tolerances():
    loose = M.buhse_naive_racemic(rtol=1e-8, atol=1e-22)
    tight = M.buhse_naive_racemic(rtol=1e-12, atol=1e-24)
    assert abs(loose) > 0.3 and abs(tight) < 1e-6
