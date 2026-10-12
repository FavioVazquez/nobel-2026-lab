"""Run everything: python -m nk.run_all (from 2026/economics/set-the-rate/). Writes results/."""
import argparse
import json

import numpy as np

from . import constants as C
from . import model as M

KAPPA = M.kappa(C.BETA, C.SIGMA, C.PHI_LABOUR, C.ALPHA, C.EPSILON, C.THETA)
DEEP = dict(beta=C.BETA, sigma=C.SIGMA, kappa=KAPPA)


def r3(v):
    v = round(float(v), 3)
    return 0.0 if v == 0 else v


def r4(a):
    return [0.0 if round(float(v), 4) == 0 else round(float(v), 4) for v in a]


def reported(p):
    """Quarterly model units to the units we show: gap in per cent, inflation and rates at annual rates."""
    return {"output_gap": np.asarray(p["x"]), "inflation": C.ANNUAL * np.asarray(p["pi"]),
            "policy_rate": C.ANNUAL * np.asarray(p["i"])}


def shock_block(shock, phi_pi, rho):
    p = M.irf(shock, phi_pi, C.PHI_Y, rho=rho, size=C.SHOCK_PP / C.ANNUAL, horizon=C.HORIZON, **DEEP)
    rep = reported(p)
    res = M.residuals(p, phi_pi=phi_pi, phi_y=C.PHI_Y, **DEEP)
    return {
        "phi_pi": phi_pi,
        "impact": {k: r3(v[0]) for k, v in rep.items()},
        "cumulative_12q": {k: r3(v[:C.CUMULATE].sum()) for k, v in rep.items()},
        "paths": {k: r4(v) for k, v in rep.items()},
        "max_residual_below_tol": all(v < C.TOL for v in res.values()),
    }


def taylor_block(phi_pi):
    bk = M.blanchard_kahn(phi_pi, C.PHI_Y, **DEEP)
    unique = bk["status"] == "unique"
    return {
        "phi_pi": phi_pi, "phi_y": C.PHI_Y,
        "eigenvalue_moduli": sorted(r3(abs(v)) for v in bk["eigenvalues"]),
        "outside_unit_circle": bk["outside_unit_circle"],
        "forward_looking_variables": bk["forward_looking_variables"],
        "unique_bounded_solution": unique,
        "bullard_mitra_condition_holds": bool(M.bullard_mitra(phi_pi, C.PHI_Y, C.BETA, KAPPA)),
        "plain": ("The rate rises more than one for one with inflation, and the model has exactly one bounded "
                  "path after any shock." if unique else
                  "The rate rises less than one for one with inflation, and the model has many bounded paths, "
                  "so the three equations alone do not say which one the economy follows."),
    }


def _ratios(vals):
    return [r3(v / vals[0]) for v in vals]


def fg_block():
    cut = C.FG_CUT_PP / C.ANNUAL
    q, H = C.FG_QUARTER, range(C.FG_HORIZONS + 1)
    on = M.forward_guidance_rule_on(q, cut, C.PHI_PI, C.PHI_Y, horizon=C.HORIZON, **DEEP)
    rep = reported(on)
    res = M.residuals(on, phi_pi=C.PHI_PI, phi_y=C.PHI_Y, **DEEP)
    on_sweep = [reported(M.forward_guidance_rule_on(j, cut, C.PHI_PI, C.PHI_Y, horizon=j, **DEEP)) for j in H]
    on_gap = [r3(s["output_gap"][0]) for s in on_sweep]
    on_inf = [r3(s["inflation"][0]) for s in on_sweep]
    peg_sweep, peg_ok = [], True
    for j in H:
        p = M.forward_guidance(j, cut, C.PHI_PI, C.PHI_Y, horizon=j + 1, **DEEP)
        peg_ok &= all(v < C.TOL for v in M.residuals(p, phi_pi=C.PHI_PI, phi_y=C.PHI_Y, rule_from=j + 1,
                                                     **DEEP).values())
        peg_sweep.append(reported(p))
    peg_gap = _ratios([float(s["output_gap"][0]) for s in peg_sweep])
    peg_inf = _ratios([float(s["inflation"][0]) for s in peg_sweep])
    return {
        "quarter": q, "cut_pp": C.FG_CUT_PP,
        "rule_on": {
            "announcement": "today (quarter 0) the central bank announces a one-quarter shift of %g percentage point "
                            "a year down in the intercept of its rule, in quarter %d only; the rule stays on in every "
                            "quarter; perfect foresight and rational expectations after the announcement"
                            % (C.FG_CUT_PP, q),
            "today": {"output_gap": r3(rep["output_gap"][0]), "inflation": r3(rep["inflation"][0]),
                      "policy_rate": r3(rep["policy_rate"][0])},
            "in_quarter": {"output_gap": r3(rep["output_gap"][q]), "inflation": r3(rep["inflation"][q]),
                           "policy_rate": r3(rep["policy_rate"][q])},
            "paths": {**{k: r4(v) for k, v in rep.items()}, "intercept_shift": r4(C.ANNUAL * on["v"])},
            "by_horizon": {"quarters": list(H), "output_gap_today": on_gap, "inflation_today": on_inf},
            "grows_with_horizon": {"output_gap": bool(np.all(np.diff(on_gap) > 0)),
                                   "inflation": bool(np.all(np.diff(on_inf) > 0))},
            "shrinks_with_horizon": {"output_gap": bool(np.all(np.diff(on_gap) < 0)),
                                     "inflation": bool(np.all(np.diff(on_inf) < 0))},
            "inflation_peak": {"quarter": int(np.argmax(on_inf)), "inflation_today": max(on_inf)},
            "output_gap_negative_from_quarter": next(j for j in H if all(g < 0 for g in on_gap[j:])),
            "max_residual_below_tol": all(v < C.TOL for v in res.values()),
        },
        "pegged_puzzle": {
            "announcement": "the nominal policy rate is held at its steady-state value until the promised quarter, is %g "
                            "percentage point a year lower in that quarter only, then follows the rule" % C.FG_CUT_PP,
            "reported_as": "today's response for a cut promised h quarters ahead, divided by today's response to the "
                           "same cut made today (h = 0)",
            "by_horizon": {"quarters": list(H), "output_gap_ratio": peg_gap, "inflation_ratio": peg_inf},
            "at_quarter": {"quarter": q, "output_gap_ratio": peg_gap[q], "inflation_ratio": peg_inf[q]},
            "last": {"quarter": C.FG_HORIZONS, "output_gap_ratio": peg_gap[-1], "inflation_ratio": peg_inf[-1]},
            "grows_with_horizon": bool(np.all(np.diff(peg_gap) > 0) and np.all(np.diff(peg_inf) > 0)),
            "max_residual_below_tol": bool(peg_ok),
            "published_version": "Del Negro, Giannoni and Patterson (2023), the version the committee's scientific "
                                 "background cites (p. 46)",
            "puzzle": "in this textbook model, with the nominal rate held still until the promised quarter, the response today "
                      "grows with how far ahead the promised cut is; Del Negro, Giannoni and Patterson (2012, 2015; published 2023) "
                      "call this the forward guidance puzzle and McKay, Nakamura and Steinsson (2016) also find it "
                      "implausible",
        },
    }


def summary():
    d = shock_block("demand", C.PHI_PI, C.RHO_DEMAND)
    cp = shock_block("cost_push", C.PHI_PI, C.RHO_COST_PUSH)
    cps = shock_block("cost_push", C.PHI_PI_STRONG, C.RHO_COST_PUSH)
    act, pas = taylor_block(C.PHI_PI), taylor_block(C.PHI_PI_PASSIVE)
    fg = fg_block()
    on = fg["rule_on"]
    return {
        "label": C.LABEL,
        "prize": C.PRIZE,
        "committee_quote": C.COMMITTEE_QUOTE,
        "citations": C.CITATIONS,
        "dois": C.DOIS,
        "python": C.PYTHON,
        "units": {"time": "quarters; today is quarter 0", "output_gap": "per cent of potential output",
                  "inflation": "percentage points at an annual rate (4 x the quarterly rate)",
                  "policy_rate": "percentage points at an annual rate, deviation from steady state"},
        "calibration": {
            "source": C.GALI,
            "beta": C.BETA, "sigma": C.SIGMA, "phi_labour": C.PHI_LABOUR, "alpha": C.ALPHA,
            "epsilon": C.EPSILON, "theta": C.THETA, "kappa": r3(KAPPA), "phi_pi": C.PHI_PI, "phi_y": C.PHI_Y,
            "rho_demand": C.RHO_DEMAND, "rho_cost_push": C.RHO_COST_PUSH,
            "sources": {
                "beta": C.GALI, "sigma": C.GALI, "kappa": C.GALI + ": kappa from beta, sigma, phi, alpha, epsilon, "
                "theta", "phi_pi": C.GALI, "phi_y": C.GALI + " (0.5/4 at quarterly rates); Galí's rule responds to output's "
                "deviation from steady state; here no shock moves natural output, so that equals the output gap",
                "rho_demand": C.GALI + " (discount-rate shock)",
                "rho_cost_push": "our choice, set equal to rho_demand; the model has no cost-push shock in that "
                                 "chapter"},
            "shock_pp": C.SHOCK_PP, "horizon_quarters": C.HORIZON, "cumulate_quarters": C.CUMULATE,
            "phi_pi_strong": C.PHI_PI_STRONG, "phi_pi_passive": C.PHI_PI_PASSIVE,
            "tolerance": "1e-10",
        },
        "demand_shock": {"label": C.SPENDING_LABEL,
                         "shock": "households become less patient (Galí's discount-rate shock), a demand shift: the "
                                  "natural rate of interest rises %g percentage point a year on impact" % C.SHOCK_PP,
                         "committee_note": "the committee's scientific background (p. 29) presents natural-rate "
                                           "shocks as representing supply shocks, such as those to productivity; a "
                                           "productivity shock would also move the natural rate and is not modelled "
                                           "here",
                         **d},
        "cost_push_shock": {
            "shock": "the cost-push term adds %g percentage point a year to the Phillips curve on impact; inflation "
                     "itself rises by more because firms expect the shock to last. The model has no energy sector; "
                     "the cost-push term stands in for any rise in firms' costs" % C.SHOCK_PP,
            "baseline": cp, "strong": cps,
            "trade_off": {"inflation_up": cp["impact"]["inflation"] > 0, "gap_down": cp["impact"]["output_gap"] < 0,
                          "strong_lowers_inflation": cps["cumulative_12q"]["inflation"] <
                          cp["cumulative_12q"]["inflation"],
                          "strong_widens_gap": cps["cumulative_12q"]["output_gap"] <
                          cp["cumulative_12q"]["output_gap"]},
        },
        "taylor_principle": {"active": act, "passive": pas},
        "forward_guidance": fg,
        "guess": {
            "a": {"question": "An energy-price shock raises firms' costs. In this model, does the rule raise or "
                              "lower the policy rate?",
                  "answer": "raise" if cp["impact"]["policy_rate"] > 0 else "lower",
                  "because": "inflation goes up more than the output gap goes down, weighted by the rule",
                  "policy_rate_impact": cp["impact"]["policy_rate"]},
            "b": {"question": "If the rate rises less than one for one with inflation (0.8), what happens in the "
                              "model?",
                  "answer": "no unique bounded solution: the model allows many paths, so it does not pin down what "
                            "happens" if not pas["unique_bounded_solution"] else "a unique bounded solution",
                  "outside_unit_circle": pas["outside_unit_circle"],
                  "needed": pas["forward_looking_variables"]},
            "c": {"question": "A promise about the rate two years from now: does it move inflation today?",
                  "answer": "yes" if on["today"]["inflation"] > 0 else "no",
                  "variant": "rule_on",
                  "inflation_today": on["today"]["inflation"], "output_gap_today": on["today"]["output_gap"],
                  "caveat": "with the nominal rate held still until the promised quarter (pegged_puzzle) the effect today "
                            "grows with the horizon: the forward guidance puzzle"},
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-figures", action="store_true")
    a = ap.parse_args(argv)
    s = summary()
    C.RESULTS.mkdir(parents=True, exist_ok=True)
    (C.RESULTS / C.RESULTS_JSON).write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n")
    if not a.no_figures:
        from . import figures as F
        F.all_figures(s)
    for k in ("demand_shock",):
        print(k, s[k]["impact"], s[k]["cumulative_12q"])
    for k in ("baseline", "strong"):
        print("cost_push", k, s["cost_push_shock"][k]["impact"], s["cost_push_shock"][k]["cumulative_12q"])
    print(s["cost_push_shock"]["trade_off"])
    for k, v in s["taylor_principle"].items():
        print(k, {q: w for q, w in v.items() if q != "plain"})
    fg = s["forward_guidance"]
    print("rule_on", fg["rule_on"]["today"], fg["rule_on"]["in_quarter"], fg["rule_on"]["by_horizon"],
          fg["rule_on"]["grows_with_horizon"], fg["rule_on"]["shrinks_with_horizon"])
    print("pegged", fg["pegged_puzzle"]["by_horizon"], fg["pegged_puzzle"]["grows_with_horizon"])
    print("kappa", s["calibration"]["kappa"])


if __name__ == "__main__":
    main()
