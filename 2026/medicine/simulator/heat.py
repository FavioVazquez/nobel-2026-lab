"""Temperature rise from absorbed light: Pennes bioheat equation on the light grid. Toy model.

    rho c dT/dt = div(k grad T) - rho_b c_b w_b T + q_light        (T = rise above baseline)

Own MIT finite-volume code in cylindrical (r, z) coordinates, sparse solves with SciPy.
Baseline metabolic heat and arterial temperature cancel when solving for the rise (they set the
37 C baseline). Boundaries: no flux on the axis, rise = 0 on the outer box. The grid is the light grid:
25 um cells out to 6 mm radius and -5..7 mm, then growing cells to about 45 mm (light.OUTER), roughly
10 Pennes lengths, so the box edge no longer changes red-light or perfusion results.
The fibre itself (glass, which conducts heat) is not modelled. Units inside: mm, s, W, K.
"""
import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import splu

from .common import read_csv


def thermal_params(perfusion="w_blood"):
    p = {r["key"]: float(r["value"]) for r in read_csv("thermal.csv")}
    return dict(
        k=p["k_brain"] * 1e-3,  # W/(mm K)
        rho_c=p["rho_brain"] * p["c_brain"] * 1e-9,  # J/(mm^3 K)
        beta=p["rho_blood"] * p["c_blood"] * p[perfusion] * 1e-9,  # W/(mm^3 K)
    )


class Grid:
    def __init__(self, r_edges, z_edges, tp=None):
        self.r_edges, self.z_edges = r_edges, z_edges
        self.tp = tp or thermal_params()
        nr, nz = len(r_edges) - 1, len(z_edges) - 1
        self.shape = (nr, nz)
        dz = np.diff(z_edges)
        ring = np.pi * (r_edges[1:] ** 2 - r_edges[:-1] ** 2)
        self.vol = np.outer(ring, dz).ravel()
        k = self.tp["k"]
        idx = np.arange(nr * nz).reshape(nr, nz)
        rows, cols, vals = [], [], []
        diag = np.zeros(nr * nz)
        rc = 0.5 * (r_edges[1:] + r_edges[:-1])
        # radial faces between i and i+1
        for i in range(nr - 1):
            c = k * 2 * np.pi * r_edges[i + 1] * dz / (rc[i + 1] - rc[i])
            a, b = idx[i], idx[i + 1]
            rows += [a, b]; cols += [b, a]; vals += [c, c]
            diag[a] -= c; diag[b] -= c
        # outer radial boundary (Dirichlet 0, half-cell distance)
        diag[idx[-1]] -= k * 2 * np.pi * r_edges[-1] * dz / (r_edges[-1] - rc[-1])
        # axial faces
        zc = 0.5 * (z_edges[1:] + z_edges[:-1])
        cz = k * ring[:, None] / np.diff(zc)[None, :]
        a, b = idx[:, :-1].ravel(), idx[:, 1:].ravel()
        rows += [a, b]; cols += [b, a]; vals += [cz.ravel(), cz.ravel()]
        np.subtract.at(diag, a, cz.ravel()); np.subtract.at(diag, b, cz.ravel())
        diag[idx[:, 0]] -= k * ring / (zc[0] - z_edges[0])
        diag[idx[:, -1]] -= k * ring / (z_edges[-1] - zc[-1])
        L = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                       shape=(nr * nz, nr * nz)).tocsc()
        self.A = (diags(self.tp["beta"] * self.vol) - L - diags(diag)).tocsc()  # (beta V - L)

    def steady(self, q):
        """q: absorbed power density (W/mm^3), shape (nr, nz). Returns rise (K), shape (nr, nz)."""
        if getattr(self, "_lu", None) is None:
            self._lu = splu(self.A)
        return self._lu.solve(q.ravel() * self.vol).reshape(self.shape)

    def transient(self, q, segments, dt, probes=None):
        """Backward Euler. segments: list of (duration_s, power_factor) or (duration_s, power_factor, dt_s)
        applied to q; a segment's own dt overrides the default dt (one factorisation per distinct step).
        Returns times, max rise over the grid per step, and the final field."""
        lus = {}
        T = np.zeros(self.vol.size)
        src = q.ravel() * self.vol
        times, peak, probe_vals, t = [0.0], [0.0], [], 0.0
        for seg in segments:
            dur, f = seg[:2]
            h = seg[2] if len(seg) > 2 else dt
            if h not in lus:
                mvd = self.tp["rho_c"] * self.vol / h
                lus[h] = (splu((diags(mvd) + self.A).tocsc()), mvd)
            M, mvd = lus[h]
            for _ in range(int(round(dur / h))):
                T = M.solve(mvd * T + f * src)
                t += h
                times.append(t)
                peak.append(T.max())
                if probes is not None:
                    probe_vals.append(probes(T.reshape(self.shape)))
        return np.array(times), np.array(peak), T.reshape(self.shape), np.array(probe_vals)


def slice_mean_profile(grid, T, radius=0.25):
    """Mean rise in circular slices of the given radius, per depth (Stujenske 2015's averaging)."""
    nk = int(round(radius / np.diff(grid.r_edges)[0]))
    v = grid.vol.reshape(grid.shape)[:nk]
    return (T[:nk] * v).sum(0) / v.sum(0)


def volume_above(grid, field, level):
    return grid.vol[(field.ravel() >= level)].sum()
