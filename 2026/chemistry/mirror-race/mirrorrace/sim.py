"""Exact stochastic simulation of Frank's closed network (Gillespie jump chain), many runs at once.

Educational demo made to show an open-source tool. Toy model, not research. Dimensionless units.

Which hand wins depends only on the ORDER of reaction events, not on when they happen, so we draw
the next event with the Gillespie probabilities (propensity / total) and skip the waiting times.
This is exact for every quantity measured against reaction progress (fraction of A used up).

ee here counts every product molecule: free ones plus those locked in mixed pairs (each pair is one
of each hand). So ee = (one - mirror) / (one + mirror + 2 P) = (one - mirror) / (N - A). Pairing
events do not change one - mirror, so the ee is fixed the moment A runs out.
"""
from dataclasses import dataclass

import numpy as np


@dataclass
class Ensemble:
    progress: np.ndarray   # (n_ck,) fraction of A used up at each checkpoint
    one: np.ndarray        # (runs, n_ck) free one-hand molecules
    mirror: np.ndarray     # (runs, n_ck) free mirror-hand molecules
    pairs: np.ndarray      # (runs, n_ck) inactive mixed pairs P
    N: int
    seed_one: np.ndarray   # (runs,) head start of one hand at t = 0
    time: np.ndarray = None  # (runs, n_ck) model time at each checkpoint (only if track_time)

    def ee(self, k=-1):
        """ee of all product at checkpoint k (default: the last one)."""
        made = self.one[:, k] + self.mirror[:, k] + 2 * self.pairs[:, k]
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(made > 0, (self.one[:, k] - self.mirror[:, k]) / np.maximum(made, 1), 0.0)


def run(N, runs, k0, k1, k2, rng, progress=(1.0,), seed_one=0, compact_every=256, track_time=False):
    """Simulate `runs` independent runs, each starting with N molecules of A, `seed_one` of one hand,
    none of the mirror hand. Returns counts at the requested progress checkpoints (fractions of A used).

    k0 can be a scalar or one value per run (used by the 'fixed concentration' scaling).
    track_time=True also draws the Gillespie waiting times (only needed for the animation's time axis)."""
    progress = np.asarray(progress, float)
    thr = np.round(N * (1.0 - progress)).astype(np.int64)        # A left at each checkpoint
    if np.any(np.diff(thr) >= 0):
        raise ValueError("progress checkpoints must be strictly increasing and map to distinct A counts")
    n_ck = len(thr)
    seed = np.broadcast_to(np.asarray(seed_one, np.int64), (runs,)).copy()
    k0v = np.broadcast_to(np.asarray(k0, float), (runs,)).copy()
    out = np.zeros((3, runs, n_ck), np.int64)
    out_t = np.zeros((runs, n_ck)) if track_time else None
    T = np.zeros(runs)

    idx = np.arange(runs)
    A = np.full(runs, N, np.int64)
    R = seed.copy()
    S = np.zeros(runs, np.int64)
    P = np.zeros(runs, np.int64)
    nxt = np.zeros(runs, np.int64)
    kk = k0v.copy()
    # checkpoint at progress 0 (thr == N) is hit before any event
    hit = A == thr[nxt]
    if hit.any():
        out[0, idx[hit], 0], out[1, idx[hit], 0], out[2, idx[hit], 0] = R[hit], S[hit], P[hit]
        nxt[hit] += 1
    a_end = thr[-1]
    step = 0
    while idx.size:
        bg = kk * A
        c2 = 2.0 * bg
        c3 = c2 + k1 * A * R
        c4 = c3 + k1 * A * S
        tot = c4 + k2 * R * S
        u = rng.random(idx.size) * tot
        live = A > a_end
        if track_time:
            T += np.where(live, rng.standard_exponential(idx.size) / np.where(tot > 0, tot, 1.0), 0.0)
        anta = (u >= c4) & live
        one_up = ((u < bg) | ((u >= c2) & (u < c3))) & live
        mir_up = (((u >= bg) & (u < c2)) | ((u >= c3) & (u < c4))) & live
        A -= (one_up | mir_up)
        R += one_up.astype(np.int64) - anta
        S += mir_up.astype(np.int64) - anta
        P += anta
        hit = A == thr[np.minimum(nxt, n_ck - 1)]
        hit &= nxt < n_ck
        if hit.any():
            j = nxt[hit]
            out[0, idx[hit], j], out[1, idx[hit], j], out[2, idx[hit], j] = R[hit], S[hit], P[hit]
            if track_time:
                out_t[idx[hit], j] = T[hit]
            nxt[hit] += 1
        step += 1
        if step % compact_every == 0 or idx.size < 64:
            keep = nxt < n_ck
            if not keep.all():
                idx, A, R, S, P, nxt, kk, T = idx[keep], A[keep], R[keep], S[keep], P[keep], nxt[keep], kk[keep], T[keep]
    return Ensemble(progress, out[0], out[1], out[2], N, seed, out_t)


def winners(ee):
    """+1 one hand ahead, -1 mirror hand ahead, 0 exact tie."""
    return np.sign(ee).astype(int)
