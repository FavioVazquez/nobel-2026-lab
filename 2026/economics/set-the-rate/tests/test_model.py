"""Checks of the solver: Blanchard-Kahn counts, the three equations to 1e-10, the zero steady state, a hand-checked
case with no persistence, and the stacked cross-check. Educational demo, not research."""
import json
import time

import numpy as np
import pytest

from nk import constants as C
from nk import model as M
from nk import run_all as R

RES = json.loads((C.RESULTS / C.RESULTS_JSON).read_text())
D = R.DEEP
K = R.KAPPA


def test_kappa_from_gali_formula_by_hand():
    # lambda = (1 - 0.75)(1 - 0.99 * 0.75) / 0.75 * 0.75 / (0.75 + 0.25 * 9) = 0.25 * 0.2575 / 0.75 * 0.25
    lam = 0.25 * 0.2575 / 0.75 * 0.25
    # kappa = lambda (1 + (5 + 0.25) / 0.75) = 8 lambda
    assert K == pytest.approx(8 * lam, abs=1e-12) == pytest.approx(0.171667, abs=1e-6)
    assert RES["calibration"]["kappa"] == round(K, 3)


@pytest.mark.parametrize("phi_pi, outside, status", [(C.PHI_PI, 2, "unique"), (C.PHI_PI_STRONG, 2, "unique"),
                                                      (C.PHI_PI_PASSIVE, 1, "many")])
def test_blanchard_kahn_counts(phi_pi, outside, status):
    bk = M.blanchard_kahn(phi_pi, C.PHI_Y, **D)
    assert bk["outside_unit_circle"] == outside and bk["status"] == status
    assert bk["forward_looking_variables"] == 2
    assert np.all(np.abs(np.abs(bk["eigenvalues"]) - 1) > 1e-3)  # no root on the circle: the count is clean


def test_blanchard_kahn_agrees_with_closed_form_on_a_grid():
    for phi_pi in np.linspace(0, 3, 61):
        for phi_y in np.linspace(0, 1, 21):
            bk = M.blanchard_kahn(phi_pi, phi_y, **D)
            if abs(K * (phi_pi - 1) + (1 - C.BETA) * phi_y) < 1e-9:
                continue  # on the boundary a root sits on the unit circle
            assert (bk["status"] == "unique") == M.bullard_mitra(phi_pi, phi_y, C.BETA, K)


def test_json_taylor_block_matches_solver():
    for key, phi in (("active", C.PHI_PI), ("passive", C.PHI_PI_PASSIVE)):
        b = RES["taylor_principle"][key]
        bk = M.blanchard_kahn(phi, C.PHI_Y, **D)
        assert b["outside_unit_circle"] == bk["outside_unit_circle"]
        assert b["unique_bounded_solution"] == (bk["status"] == "unique")
        assert b["eigenvalue_moduli"] == sorted(round(abs(v), 3) for v in bk["eigenvalues"])


@pytest.mark.parametrize("shock, phi_pi, rho", [("demand", C.PHI_PI, C.RHO_DEMAND),
                                                ("cost_push", C.PHI_PI, C.RHO_COST_PUSH),
                                                ("cost_push", C.PHI_PI_STRONG, C.RHO_COST_PUSH),
                                                ("demand", C.PHI_PI, 0.9), ("cost_push", 1.1, 0.8)])
def test_impulse_responses_satisfy_the_three_equations(shock, phi_pi, rho):
    p = M.irf(shock, phi_pi, C.PHI_Y, rho=rho, size=0.25, horizon=40, **D)
    res = M.residuals(p, phi_pi=phi_pi, phi_y=C.PHI_Y, **D)
    assert set(res) == {"is", "nkpc", "rule"} and max(res.values()) < C.TOL, res


@pytest.mark.parametrize("quarter", range(C.FG_HORIZONS + 1))
def test_forward_guidance_pegged_satisfies_the_equations(quarter):
    p = M.forward_guidance(quarter, 0.25, C.PHI_PI, C.PHI_Y, horizon=C.HORIZON, **D)
    res = M.residuals(p, phi_pi=C.PHI_PI, phi_y=C.PHI_Y, rule_from=quarter + 1, **D)
    assert max(res.values()) < C.TOL, res
    i = np.zeros(len(p["i"]))
    i[quarter] = -0.25
    assert np.array_equal(p["i"], i)  # the announced path, exactly
    assert np.all(p["x"][quarter + 1:] == 0) and np.all(p["pi"][quarter + 1:] == 0)


@pytest.mark.parametrize("quarter", range(C.FG_HORIZONS + 1))
def test_forward_guidance_rule_on_satisfies_the_equations(quarter):
    p = M.forward_guidance_rule_on(quarter, 0.25, C.PHI_PI, C.PHI_Y, horizon=C.HORIZON, **D)
    res = M.residuals(p, phi_pi=C.PHI_PI, phi_y=C.PHI_Y, **D)  # the rule (with its intercept) holds in every quarter
    assert set(res) == {"is", "nkpc", "rule"} and max(res.values()) < C.TOL, res
    assert p["v"][quarter] == -0.25 and np.count_nonzero(p["v"]) == 1
    assert np.all(p["x"][quarter + 1:] == 0) and np.all(p["pi"][quarter + 1:] == 0)
    x, pi = M.perfect_foresight("demand", C.PHI_PI, C.PHI_Y, rho=0.0, size=0.0, T=C.T_CHECK, v=p["v"], **D)
    assert np.max(np.abs(x[:len(p["x"])] - p["x"])) < C.TOL and np.max(np.abs(pi[:len(p["pi"])] - p["pi"])) < C.TOL


def test_rule_on_json_matches_solver():
    on = RES["forward_guidance"]["rule_on"]
    sweep = [M.forward_guidance_rule_on(j, 0.25, C.PHI_PI, C.PHI_Y, horizon=j, **D) for j in range(C.FG_HORIZONS + 1)]
    assert on["by_horizon"]["output_gap_today"] == [round(float(p["x"][0]), 3) + 0.0 for p in sweep]
    assert on["by_horizon"]["inflation_today"] == [round(float(4 * p["pi"][0]), 3) + 0.0 for p in sweep]
    assert on["today"]["inflation"] == on["by_horizon"]["inflation_today"][C.FG_QUARTER]
    peg = RES["forward_guidance"]["pegged_puzzle"]
    assert peg["by_horizon"]["output_gap_ratio"][0] == peg["by_horizon"]["inflation_ratio"][0] == 1
    assert peg["grows_with_horizon"]


def test_json_flags_say_residuals_below_tolerance():
    assert RES["demand_shock"]["max_residual_below_tol"]
    assert RES["cost_push_shock"]["baseline"]["max_residual_below_tol"]
    assert RES["cost_push_shock"]["strong"]["max_residual_below_tol"]
    assert RES["forward_guidance"]["rule_on"]["max_residual_below_tol"]
    assert RES["forward_guidance"]["pegged_puzzle"]["max_residual_below_tol"]


def test_steady_state_is_zero():
    A = M.system_matrix(C.PHI_PI, C.PHI_Y, **D)
    assert np.all(A @ np.zeros(2) == 0)
    for shock in ("demand", "cost_push"):
        p = M.irf(shock, C.PHI_PI, C.PHI_Y, rho=0.5, size=0.0, horizon=20, **D)
        assert all(np.all(p[k] == 0) for k in ("x", "pi", "i"))
    p = M.forward_guidance(8, 0.0, C.PHI_PI, C.PHI_Y, horizon=20, **D)
    assert all(np.all(p[k] == 0) for k in ("x", "pi", "i"))
    # every shock path returns to zero
    for k in ("output_gap", "inflation", "policy_rate"):
        assert abs(RES["demand_shock"]["paths"][k][-1]) < 1e-3
        assert abs(RES["cost_push_shock"]["baseline"]["paths"][k][-1]) < 1e-3


def test_hand_checked_case_no_persistence():
    """rho = 0: E_t x_t+1 = E_t pi_t+1 = 0, so x = (rn - i)/sigma, pi = kappa x + u, i = phi_pi pi + phi_y x.
    Demand: x = rn / (sigma + phi_y + phi_pi kappa), pi = kappa x.
    Cost push: x = -phi_pi u / (sigma + phi_y + phi_pi kappa), pi = (sigma + phi_y) u / (same)."""
    s, b, k, fp, fy = 2.0, 0.99, 0.3, 1.5, 0.5
    den = s + fy + fp * k  # = 2.95
    a, c = M.msv("demand", fp, fy, b, s, k, 0.0)
    assert (a, c) == pytest.approx((1 / den, k / den), abs=1e-14)
    a, c = M.msv("cost_push", fp, fy, b, s, k, 0.0)
    assert (a, c) == pytest.approx((-fp / den, (s + fy) / den), abs=1e-14)
    assert (a, c) == pytest.approx((-0.508475, 0.847458), abs=1e-6)  # by hand: -1.5/2.95, 2.5/2.95
    p = M.irf("cost_push", fp, fy, b, s, k, 0.0, 1.0, 5)
    assert np.all(p["x"][1:] == 0) and p["i"][0] == pytest.approx(fp * 2.5 / den + fy * -1.5 / den, abs=1e-14)
    # forward guidance about today only, rate pegged: x_0 = cut / sigma, pi_0 = kappa cut / sigma
    p = M.forward_guidance(0, 1.0, fp, fy, b, s, k, 5)
    assert (p["x"][0], p["pi"][0]) == pytest.approx((0.5, 0.15), abs=1e-14)
    # rule on, intercept down by 1 today only: like a demand shock with no persistence, x_0 = 1 / den, pi_0 = kappa x_0
    p = M.forward_guidance_rule_on(0, 1.0, fp, fy, b, s, k, 5)
    assert (p["x"][0], p["pi"][0]) == pytest.approx((1 / den, k / den), abs=1e-14)


@pytest.mark.parametrize("shock, rho", [("demand", C.RHO_DEMAND), ("cost_push", C.RHO_COST_PUSH)])
def test_stacked_perfect_foresight_agrees(shock, rho):
    x, pi = M.perfect_foresight(shock, C.PHI_PI, C.PHI_Y, rho=rho, size=0.25, T=C.T_CHECK, **D)
    p = M.irf(shock, C.PHI_PI, C.PHI_Y, rho=rho, size=0.25, horizon=C.HORIZON, **D)
    assert np.max(np.abs(x[:C.HORIZON + 1] - p["x"])) < C.TOL
    assert np.max(np.abs(pi[:C.HORIZON + 1] - p["pi"])) < C.TOL


def test_trade_off_and_guess_answers_follow_the_numbers():
    cp = RES["cost_push_shock"]
    assert all(cp["trade_off"].values())
    assert cp["baseline"]["impact"]["inflation"] > 0 > cp["baseline"]["impact"]["output_gap"]
    assert cp["strong"]["impact"]["inflation"] < cp["baseline"]["impact"]["inflation"]
    assert cp["strong"]["impact"]["output_gap"] < cp["baseline"]["impact"]["output_gap"]
    g = RES["guess"]
    assert g["a"]["answer"] == "raise" and g["a"]["policy_rate_impact"] == cp["baseline"]["impact"]["policy_rate"] > 0
    assert g["b"]["outside_unit_circle"] < g["b"]["needed"] and g["b"]["answer"].startswith("no unique")
    on = RES["forward_guidance"]["rule_on"]
    assert g["c"]["variant"] == "rule_on" and g["c"]["answer"] == "yes"
    assert g["c"]["inflation_today"] == on["today"]["inflation"] > 0
    assert RES["forward_guidance"]["quarter"] == 8  # "two years from now", quarterly
    h = on["by_horizon"]
    peak = on["inflation_peak"]
    assert h["inflation_today"][peak["quarter"]] == peak["inflation_today"] == max(h["inflation_today"])
    assert not on["grows_with_horizon"]["inflation"] and not on["grows_with_horizon"]["output_gap"]
    j = on["output_gap_negative_from_quarter"]
    assert all(v < 0 for v in h["output_gap_today"][j:]) and h["output_gap_today"][j - 1] >= 0


def test_runs_in_under_a_minute():
    t = time.perf_counter()
    R.summary()
    assert time.perf_counter() - t < 60
