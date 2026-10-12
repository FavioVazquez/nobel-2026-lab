"""Independent cross-check of 2026/economics/set-the-rate (branch econ-rate). Educational demo, not research.

Written from the three equations alone (no code shared with the toy). Methods:
  1. QZ (generalized Schur, Klein 2000) on the full system [rn, u | x, pi] for the AR(1) shocks;
  2. a stacked perfect-foresight solve with the policy rate i_t as an explicit unknown (3 equations a quarter);
  3. for news about the rule's intercept, the closed form y_0 = -M^-(h+1) c v_h of the forward solution.
The toy is imported only at the end, to compare its full-precision paths and its JSON with ours.

Usage: python set_the_rate_crosscheck.py <path to 2026/economics/set-the-rate> [out.json]
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import linalg
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

# Galí (2015), ch. 3 baseline, as reported by J. Pfeifer's Dynare replication (Gali_2015_chapter_3.mod, pp. 67-70)
BETA, SIGMA, VARPHI, ALPHA, EPS, THETA = 0.99, 1.0, 5.0, 0.25, 9.0, 0.75
PHI_PI, PHI_Y, RHO = 1.5, 0.125, 0.5
OMEGA = (1 - ALPHA) / (1 - ALPHA + ALPHA * EPS)
LAM = (1 - THETA) * (1 - BETA * THETA) / THETA * OMEGA
KAPPA = LAM * (SIGMA + (VARPHI + ALPHA) / (1 - ALPHA))
Q = 0.25          # 1 pp a year, in quarterly units
H = 16            # quarters compared
T = 600           # stacked horizon


def qz_irf(shock, phi_pi, phi_y=PHI_Y, rho=RHO, kappa=KAPPA, beta=BETA, sigma=SIGMA, horizon=H):
    """A E_t s_t+1 = B s_t with s = [z, x, pi]; z = rn (demand) or u (cost push) predetermined (AR(1)), x and pi
    jump. Unique bounded solution iff exactly 1 stable generalized eigenvalue (the shock's) and 2 unstable."""
    dz = np.array([-1 / sigma, 0.0]) if shock == "demand" else np.array([0.0, -1.0])
    A = np.array([[1, 0, 0], [0, 1, 1 / sigma], [0, 0, beta]], float)
    B = np.array([[rho, 0, 0],
                  [dz[0], 1 + phi_y / sigma, phi_pi / sigma],
                  [dz[1], -kappa, 1]], float)
    BB, AA, al, be, Qm, Z = linalg.ordqz(B, A, sort="iuc", output="real")
    lam = al / be
    n_stable = int(np.sum(np.abs(lam) < 1))
    if n_stable != 1:
        return {"n_stable": n_stable, "n_unstable": 3 - n_stable}
    P = np.real(Z[1:, :1] @ np.linalg.inv(Z[:1, :1]))      # [x, pi] = P z
    z = Q * rho ** np.arange(horizon + 1)
    x, pi = P @ z[None, :]
    return {"n_stable": 1, "n_unstable": 2, "x": x, "pi": pi, "i": phi_pi * pi + phi_y * x, "P": P}


def stacked(n, rn=None, u=None, v=None, peg_until=None, i_fixed=None, phi_pi=PHI_PI, phi_y=PHI_Y,
            kappa=KAPPA, beta=BETA, sigma=SIGMA):
    """Unknowns x_t, pi_t, i_t for t = 0..n-1 with x_n = pi_n = 0. Equations each quarter: IS, NKPC, and either the
    rule i = phi_pi pi + phi_y x + v (quarters after `peg_until`) or i = i_fixed (quarters up to `peg_until`)."""
    z = np.zeros(n)
    rn, u, v = (z if a is None else np.pad(np.asarray(a, float), (0, n - len(a))) for a in (rn, u, v))
    M = lil_matrix((3 * n, 3 * n))
    b = np.zeros(3 * n)
    X, P_, I_ = 0, n, 2 * n
    for t in range(n):
        # IS: x_t - x_t+1 + (i_t - pi_t+1)/sigma = rn_t/sigma
        M[t, X + t] = 1
        M[t, I_ + t] = 1 / sigma
        if t + 1 < n:
            M[t, X + t + 1] = -1
            M[t, P_ + t + 1] = -1 / sigma
        b[t] = rn[t] / sigma
        # NKPC: pi_t - beta pi_t+1 - kappa x_t = u_t
        M[n + t, P_ + t] = 1
        M[n + t, X + t] = -kappa
        if t + 1 < n:
            M[n + t, P_ + t + 1] = -beta
        b[n + t] = u[t]
        # policy
        M[2 * n + t, I_ + t] = 1
        if peg_until is not None and t <= peg_until:
            b[2 * n + t] = i_fixed[t]
        else:
            M[2 * n + t, P_ + t] = -phi_pi
            M[2 * n + t, X + t] = -phi_y
            b[2 * n + t] = v[t]
    s = spsolve(M.tocsc(), b)
    return s[:n], s[n:2 * n], s[2 * n:]


def companion(phi_pi, phi_y, kappa=KAPPA, beta=BETA, sigma=SIGMA):
    """E_t y_t+1 = M y_t + c v_t, y = [x, pi], rule i = phi_pi pi + phi_y x + v."""
    M = np.array([[1 + (phi_y + kappa / beta) / sigma, (phi_pi - 1 / beta) / sigma], [-kappa / beta, 1 / beta]])
    return M, np.array([1 / sigma, 0.0])


def news_today(h, cut=Q, phi_pi=PHI_PI, phi_y=PHI_Y):
    """Forward solution under determinacy: y_t = -sum_k M^-(k+1) c v_t+k, so today's response to v_h = -cut is
    y_0 = M^-(h+1) c cut."""
    M, c = companion(phi_pi, phi_y)
    return np.linalg.matrix_power(np.linalg.inv(M), h + 1) @ c * cut


def main(toy, out=None):
    r = {"kappa": KAPPA, "lambda": LAM}
    # --- 1. impulse responses, QZ vs stacked
    irfs = {}
    for name, shock, fp in (("demand", "demand", PHI_PI), ("cost_push", "cost_push", PHI_PI),
                            ("cost_push_strong", "cost_push", 3.0)):
        a = qz_irf(shock, fp)
        rn = Q * RHO ** np.arange(T) if shock == "demand" else None
        u = Q * RHO ** np.arange(T) if shock == "cost_push" else None
        x, pi, i = stacked(T, rn=rn, u=u, phi_pi=fp)
        gap = max(np.max(np.abs(a["x"] - x[:H + 1])), np.max(np.abs(a["pi"] - pi[:H + 1])),
                  np.max(np.abs(a["i"] - i[:H + 1])))
        irfs[name] = {"x": a["x"], "pi": a["pi"], "i": a["i"], "qz_vs_stacked_max_abs": gap}
        r[name] = {"impact": {"output_gap": a["x"][0], "inflation": 4 * a["pi"][0], "policy_rate": 4 * a["i"][0]},
                   "cumulative_12q": {"output_gap": a["x"][:12].sum(), "inflation": 4 * a["pi"][:12].sum(),
                                      "policy_rate": 4 * a["i"][:12].sum()},
                   "qz_vs_stacked_max_abs": gap}
    # closed form (Galí-style): D = (1 - beta rho)(sigma (1 - rho) + phi_y) + kappa (phi_pi - rho)
    D = (1 - BETA * RHO) * (SIGMA * (1 - RHO) + PHI_Y) + KAPPA * (PHI_PI - RHO)
    r["closed_form"] = {"demand_x0": (1 - BETA * RHO) / D * Q, "demand_pi0_annual": 4 * KAPPA / D * Q,
                        "cost_push_x0": -(PHI_PI - RHO) / D * Q,
                        "cost_push_pi0_annual": 4 * (SIGMA * (1 - RHO) + PHI_Y) / D * Q}
    # --- 2. determinacy
    det = {}
    for fp in (0.8, 1.5):
        rows = []
        for fy in (0.0, 0.125, 0.25, 0.5, 1.0, 2.0, 3.0, 3.4, 3.5, 5.0):
            ev = np.linalg.eigvals(companion(fp, fy)[0])
            a = qz_irf("demand", fp, phi_y=fy)
            rows.append({"phi_y": fy, "moduli": sorted(float(abs(e)) for e in ev),
                         "outside": int(np.sum(np.abs(ev) > 1)), "qz_unstable": a["n_unstable"],
                         "closed_form": bool(KAPPA * (fp - 1) + (1 - BETA) * fy > 0)})
        det[str(fp)] = rows
    det["phi_y_needed_for_0.8"] = KAPPA * (1 - 0.8) / (1 - BETA)
    r["determinacy"] = det
    # --- 3. forward guidance
    n = 200
    v = np.zeros(9)
    v[8] = -Q
    x, pi, i = stacked(n, v=v)
    r["fg_rule_on"] = {"today": {"output_gap": x[0], "inflation": 4 * pi[0], "policy_rate": 4 * i[0]},
                       "in_quarter_8": {"output_gap": x[8], "inflation": 4 * pi[8], "policy_rate": 4 * i[8]},
                       "after_quarter_8_max_abs": float(np.max(np.abs(np.r_[x[9:], pi[9:]]))),
                       "path_x": x[:17], "path_pi_annual": 4 * pi[:17], "path_i_annual": 4 * i[:17]}
    on_x, on_pi, cf_gap = [], [], 0.0
    for h in range(13):
        v = np.zeros(h + 1)
        v[h] = -Q
        x, pi, _ = stacked(n, v=v)
        y0 = news_today(h)
        cf_gap = max(cf_gap, abs(y0[0] - x[0]), abs(y0[1] - pi[0]))
        on_x.append(x[0])
        on_pi.append(4 * pi[0])
    r["fg_rule_on"]["by_horizon"] = {"output_gap_today": on_x, "inflation_today": on_pi,
                                     "stacked_vs_closed_form_max_abs": cf_gap,
                                     "decay_factor_per_quarter": float(1 / np.abs(np.linalg.eigvals(
                                         companion(PHI_PI, PHI_Y)[0])).min())}
    peg_x, peg_pi = [], []
    for h in range(13):
        ifix = np.zeros(h + 1)
        ifix[h] = -Q
        x, pi, i = stacked(n, peg_until=h, i_fixed=ifix)
        peg_x.append(x[0])
        peg_pi.append(4 * pi[0])
    r["fg_pegged"] = {"output_gap_today": peg_x, "inflation_today": peg_pi,
                      "output_gap_ratio": [a / peg_x[0] for a in peg_x],
                      "inflation_ratio": [a / peg_pi[0] for a in peg_pi]}
    # the real-rate version (McKay, Nakamura and Steinsson 2016, sec. I): real rate 1 pp a year lower in quarter h only
    rr_x = [Q / SIGMA for h in range(13)]
    rr_pi = [4 * KAPPA * sum(BETA ** k * Q / SIGMA for k in range(h + 1)) for h in range(13)]
    r["fg_real_rate"] = {"output_gap_today": rr_x, "inflation_today": rr_pi,
                         "inflation_ratio": [a / rr_pi[0] for a in rr_pi]}

    # --- 4. compare with the toy (imported only now)
    sys.path.insert(0, str(Path(toy).resolve()))
    from nk import model as TM, run_all as TR, constants as TC  # noqa: E402
    D_ = TR.DEEP
    cmp = {}
    for name, shock, fp in (("demand", "demand", PHI_PI), ("cost_push", "cost_push", PHI_PI),
                            ("cost_push_strong", "cost_push", 3.0)):
        p = TM.irf(shock, fp, TC.PHI_Y, rho=0.5, size=Q, horizon=H, **D_)
        cmp[name] = max(float(np.max(np.abs(p[k] - irfs[name][k]))) for k in ("x", "pi", "i"))
    p = TM.forward_guidance_rule_on(8, Q, TC.PHI_PI, TC.PHI_Y, horizon=16, **D_)
    cmp["fg_rule_on_path"] = max(float(np.max(np.abs(p["x"] - r["fg_rule_on"]["path_x"]))),
                                 float(np.max(np.abs(4 * p["pi"] - r["fg_rule_on"]["path_pi_annual"]))),
                                 float(np.max(np.abs(4 * p["i"] - r["fg_rule_on"]["path_i_annual"]))))
    g1 = g2 = 0.0
    for h in range(13):
        a = TM.forward_guidance_rule_on(h, Q, TC.PHI_PI, TC.PHI_Y, horizon=h, **D_)
        b = TM.forward_guidance(h, Q, TC.PHI_PI, TC.PHI_Y, horizon=h + 1, **D_)
        g1 = max(g1, abs(a["x"][0] - on_x[h]), abs(4 * a["pi"][0] - on_pi[h]))
        g2 = max(g2, abs(b["x"][0] - peg_x[h]), abs(4 * b["pi"][0] - peg_pi[h]))
    cmp["fg_rule_on_by_horizon"], cmp["fg_pegged_by_horizon"] = g1, g2
    r["toy_vs_ours_max_abs"] = cmp

    js = json.loads((Path(toy) / "results" / "set_the_rate.json").read_text())
    checks = []

    def chk(label, theirs, ours, nd=3):
        checks.append({"field": label, "json": theirs, "ours": round(float(ours), nd),
                       "ok": theirs == round(float(ours), nd) + 0.0})
    for name, key in (("demand", "demand_shock"), ("cost_push", "cost_push_shock.baseline"),
                      ("cost_push_strong", "cost_push_shock.strong")):
        blk = js
        for part in key.split("."):
            blk = blk[part]
        for kind in ("impact", "cumulative_12q"):
            for var in ("output_gap", "inflation", "policy_rate"):
                chk(f"{key}.{kind}.{var}", blk[kind][var], r[name][kind][var])
    for fp, key in ((1.5, "active"), (0.8, "passive")):
        row = next(w for w in r["determinacy"][str(fp)] if w["phi_y"] == 0.125)
        for m_t, m_o in zip(js["taylor_principle"][key]["eigenvalue_moduli"], row["moduli"]):
            chk(f"taylor_principle.{key}.eigenvalue_moduli", m_t, m_o)
        checks.append({"field": f"taylor_principle.{key}.outside_unit_circle",
                       "json": js["taylor_principle"][key]["outside_unit_circle"], "ours": row["outside"],
                       "ok": js["taylor_principle"][key]["outside_unit_circle"] == row["outside"] == row["qz_unstable"]})
    on = js["forward_guidance"]["rule_on"]
    for var in ("output_gap", "inflation", "policy_rate"):
        chk(f"forward_guidance.rule_on.today.{var}", on["today"][var], r["fg_rule_on"]["today"][var])
        chk(f"forward_guidance.rule_on.in_quarter.{var}", on["in_quarter"][var], r["fg_rule_on"]["in_quarter_8"][var])
    for h in range(13):
        chk(f"forward_guidance.rule_on.by_horizon.output_gap_today[{h}]", on["by_horizon"]["output_gap_today"][h],
            on_x[h])
        chk(f"forward_guidance.rule_on.by_horizon.inflation_today[{h}]", on["by_horizon"]["inflation_today"][h],
            on_pi[h])
    pg = js["forward_guidance"]["pegged_puzzle"]["by_horizon"]
    for h in range(13):
        chk(f"forward_guidance.pegged_puzzle.by_horizon.output_gap_ratio[{h}]", pg["output_gap_ratio"][h],
            r["fg_pegged"]["output_gap_ratio"][h])
        chk(f"forward_guidance.pegged_puzzle.by_horizon.inflation_ratio[{h}]", pg["inflation_ratio"][h],
            r["fg_pegged"]["inflation_ratio"][h])
    for var, k in (("output_gap", "output_gap"), ("inflation", "inflation"), ("policy_rate", "policy_rate")):
        theirs = js["demand_shock"]["paths"][k]
        ours = irfs["demand"]["x" if k == "output_gap" else ("pi" if k == "inflation" else "i")]
        ours = ours * (1 if k == "output_gap" else 4)
        checks.append({"field": f"demand_shock.paths.{k} (4 dp)", "json": "17 values",
                       "ours": "max abs diff %.1e" % float(np.max(np.abs(np.array(theirs) - ours))),
                       "ok": bool(np.max(np.abs(np.array(theirs) - ours)) <= 5e-5 + 1e-12)})
    r["json_checks"] = checks
    r["json_checks_failed"] = [c for c in checks if not c["ok"]]

    def conv(o):
        if isinstance(o, np.ndarray):
            return [float(v) for v in o]
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        raise TypeError(type(o))
    for name in irfs:
        irfs[name].pop("P", None)
    text = json.dumps(r, indent=1, default=conv)
    if out:
        Path(out).write_text(text + "\n")
    return r


if __name__ == "__main__":
    res = main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print("kappa", res["kappa"])
    for k in ("demand", "cost_push", "cost_push_strong"):
        print(k, {a: {b: round(c, 6) for b, c in v.items()} for a, v in res[k].items() if isinstance(v, dict)},
              "qz vs stacked %.1e" % res[k]["qz_vs_stacked_max_abs"])
    print("closed form", res["closed_form"])
    print("toy vs ours (max abs, full precision)", res["toy_vs_ours_max_abs"])
    for fp in ("0.8", "1.5"):
        print("phi_pi", fp, [(w["phi_y"], w["outside"], w["qz_unstable"], w["closed_form"],
                              [round(m, 3) for m in w["moduli"]]) for w in res["determinacy"][fp]])
    print("phi_y needed for 0.8:", res["determinacy"]["phi_y_needed_for_0.8"])
    fg = res["fg_rule_on"]
    print("rule on today", fg["today"], "q8", fg["in_quarter_8"], "after q8", fg["after_quarter_8_max_abs"])
    print("rule on by horizon gap", np.round(fg["by_horizon"]["output_gap_today"], 4))
    print("rule on by horizon inf", np.round(fg["by_horizon"]["inflation_today"], 4))
    print("stacked vs closed form", fg["by_horizon"]["stacked_vs_closed_form_max_abs"], "decay",
          fg["by_horizon"]["decay_factor_per_quarter"])
    print("rule-on path x", np.round(fg["path_x"], 4))
    print("rule-on path pi", np.round(fg["path_pi_annual"], 4))
    print("rule-on path i", np.round(fg["path_i_annual"], 4))
    print("pegged ratios gap", np.round(res["fg_pegged"]["output_gap_ratio"], 3))
    print("pegged ratios inf", np.round(res["fg_pegged"]["inflation_ratio"], 3))
    print("pegged levels today q8, q12", res["fg_pegged"]["output_gap_today"][8], res["fg_pegged"]["inflation_today"][8],
          res["fg_pegged"]["output_gap_today"][12], res["fg_pegged"]["inflation_today"][12])
    print("real-rate version inflation ratio", np.round(res["fg_real_rate"]["inflation_ratio"], 3),
          "gap today", res["fg_real_rate"]["output_gap_today"][0])
    print("json checks:", len(res["json_checks"]), "failed:", res["json_checks_failed"])
