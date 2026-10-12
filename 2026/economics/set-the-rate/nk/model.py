"""The three equations (Woodford 2003; Clarida, Galí and Gertler 1999; Galí 2015, ch. 3), quarterly, in deviations
from the zero-inflation steady state (x = output gap, pi = inflation, i = policy rate, rn = natural rate of interest):

    IS (Euler):  x_t  = E_t x_t+1 - (1/sigma) (i_t - E_t pi_t+1 - rn_t)
    NKPC:        pi_t = beta E_t pi_t+1 + kappa x_t + u_t                    (u: cost-push shock)
    Rule:        i_t  = phi_pi pi_t + phi_y x_t

Solved by undetermined coefficients (AR(1) shocks), checked by Blanchard and Kahn's eigenvalue count and by a
stacked perfect-foresight solve. Educational demo, not research.
"""
import numpy as np


def kappa(beta, sigma, phi, alpha, epsilon, theta):
    """Galí (2015), ch. 3: kappa = lambda (sigma + (phi + alpha) / (1 - alpha)),
    lambda = (1 - theta)(1 - beta theta) / theta * (1 - alpha) / (1 - alpha + alpha epsilon)."""
    lam = (1 - theta) * (1 - beta * theta) / theta * (1 - alpha) / (1 - alpha + alpha * epsilon)
    return lam * (sigma + (phi + alpha) / (1 - alpha))


def system_matrix(phi_pi, phi_y, beta, sigma, kappa):
    """E_t [x, pi]_t+1 = A [x, pi]_t with no shocks: the NKPC and the IS curve with the rule substituted."""
    return np.array([[1 + (phi_y + kappa / beta) / sigma, (phi_pi - 1 / beta) / sigma],
                     [-kappa / beta, 1 / beta]])


def eigenvalues(phi_pi, phi_y, beta, sigma, kappa):
    return np.linalg.eigvals(system_matrix(phi_pi, phi_y, beta, sigma, kappa))


def blanchard_kahn(phi_pi, phi_y, beta, sigma, kappa):
    """Both x and pi are jump (forward-looking) variables, so a unique bounded solution needs exactly two
    eigenvalues of A outside the unit circle. Fewer: many bounded solutions. More: none."""
    lam = eigenvalues(phi_pi, phi_y, beta, sigma, kappa)
    outside = int(np.sum(np.abs(lam) > 1))
    jumps = 2
    return {"eigenvalues": lam, "outside_unit_circle": outside, "forward_looking_variables": jumps,
            "status": "unique" if outside == jumps else ("many" if outside < jumps else "none")}


def bullard_mitra(phi_pi, phi_y, beta, kappa):
    """Closed form of the same condition for non-negative coefficients: kappa (phi_pi - 1) + (1 - beta) phi_y > 0."""
    return kappa * (phi_pi - 1) + (1 - beta) * phi_y > 0


def msv(shock, phi_pi, phi_y, beta, sigma, kappa, rho):
    """Undetermined coefficients: x_t = a z_t, pi_t = b z_t for z = rn (shock "demand") or u ("cost_push"),
    z_t+1 = rho z_t. Put E_t x_t+1 = rho a z_t, E_t pi_t+1 = rho b z_t in the IS curve and the NKPC and match."""
    m = np.array([[1 - rho + phi_y / sigma, (phi_pi - rho) / sigma], [-kappa, 1 - beta * rho]])
    rhs = np.array([1 / sigma, 0.0]) if shock == "demand" else np.array([0.0, 1.0])
    a, b = np.linalg.solve(m, rhs)
    return float(a), float(b)


def irf(shock, phi_pi, phi_y, beta, sigma, kappa, rho, size, horizon):
    """Paths t = 0..horizon after a shock of `size` (quarterly units) at t = 0, with no later surprises."""
    a, b = msv(shock, phi_pi, phi_y, beta, sigma, kappa, rho)
    z = size * rho ** np.arange(horizon + 1)
    x, pi = a * z, b * z
    i = phi_pi * pi + phi_y * x
    zero = np.zeros_like(z)
    rn, u = (z, zero) if shock == "demand" else (zero, z)
    return {"x": x, "pi": pi, "i": i, "rn": rn, "u": u, "real_rate": i - rho * pi, "rho": rho}


def residuals(p, beta, sigma, kappa, phi_pi=None, phi_y=None, rule_from=0):
    """Largest error of the IS curve, the NKPC and (from quarter `rule_from` on) the rule along a path. Expectations
    are the path's own next value (perfect foresight after the news); the last quarter uses E x_T+1 = rho x_T."""
    x, pi, i, rn, u = (np.asarray(p[k]) for k in ("x", "pi", "i", "rn", "u"))
    rho = p.get("rho", 0.0)
    ex, epi = np.append(x[1:], rho * x[-1]), np.append(pi[1:], rho * pi[-1])
    out = {"is": float(np.max(np.abs(x - ex + (i - epi - rn) / sigma))),
           "nkpc": float(np.max(np.abs(pi - beta * epi - kappa * x - u)))}
    if phi_pi is not None:
        v = np.asarray(p.get("v", np.zeros_like(x)))
        out["rule"] = float(np.max(np.abs((i - phi_pi * pi - phi_y * x - v)[rule_from:])))
    return out


def forward_guidance(quarter, cut, phi_pi, phi_y, beta, sigma, kappa, horizon):
    """Announced today: i = 0 in quarters 0..quarter-1, i = -cut in `quarter`, then the rule. With no shocks after
    the announcement, the rule's unique bounded solution from quarter+1 on is x = pi = 0 (needs determinacy); the
    IS curve and the NKPC are then solved backwards from x = pi = 0 to today."""
    n = max(horizon, quarter) + 1
    x, pi, i = np.zeros(n), np.zeros(n), np.zeros(n)
    i[quarter] = -cut
    xn = pn = 0.0
    for t in range(quarter, -1, -1):
        x[t] = xn - (i[t] - pn) / sigma
        pi[t] = beta * pn + kappa * x[t]
        xn, pn = x[t], pi[t]
    return {"x": x, "pi": pi, "i": i, "rn": np.zeros(n), "u": np.zeros(n), "rho": 0.0}


def forward_guidance_rule_on(quarter, cut, phi_pi, phi_y, beta, sigma, kappa, horizon):
    """Announced today: the rule stays on in every quarter, i_t = phi_pi pi_t + phi_y x_t + v_t, with an intercept
    shift v = -cut in `quarter` only. From quarter+1 on there is no shock and the rule's unique bounded solution is
    x = pi = 0 (needs determinacy); before that, each quarter's IS curve and NKPC (rule substituted) are a 2 x 2
    linear system in (x_t, pi_t) given next quarter's values, solved backwards to today."""
    n = max(horizon, quarter) + 1
    x, pi, v = np.zeros(n), np.zeros(n), np.zeros(n)
    v[quarter] = -cut
    m = np.array([[1 + phi_y / sigma, phi_pi / sigma], [-kappa, 1.0]])
    xn = pn = 0.0
    for t in range(quarter, -1, -1):
        x[t], pi[t] = np.linalg.solve(m, [xn + (pn - v[t]) / sigma, beta * pn])
        xn, pn = x[t], pi[t]
    i = phi_pi * pi + phi_y * x + v
    return {"x": x, "pi": pi, "i": i, "v": v, "rn": np.zeros(n), "u": np.zeros(n), "rho": 0.0}


def perfect_foresight(shock, phi_pi, phi_y, beta, sigma, kappa, rho, size, T, v=None):
    """Cross-check: stack the IS curve and the NKPC (rule substituted, with an optional known intercept path v) for
    t = 0..T with x_T+1 = pi_T+1 = 0 and solve one linear system."""
    n = T + 1
    A = np.zeros((2 * n, 2 * n))
    rhs = np.zeros(2 * n)
    z = size * rho ** np.arange(n)
    if v is not None:
        rhs[:len(v)] -= np.asarray(v) / sigma
    for t in range(n):
        xi, pj = t, n + t
        A[t, xi] += 1 + phi_y / sigma
        A[t, pj] += phi_pi / sigma
        if t + 1 < n:
            A[t, xi + 1] -= 1
            A[t, pj + 1] -= 1 / sigma
        A[n + t, pj] += 1
        A[n + t, xi] -= kappa
        if t + 1 < n:
            A[n + t, pj + 1] -= beta
        if shock == "demand":
            rhs[t] += z[t] / sigma
        else:
            rhs[n + t] += z[t]
    sol = np.linalg.solve(A, rhs)
    return sol[:n], sol[n:]
