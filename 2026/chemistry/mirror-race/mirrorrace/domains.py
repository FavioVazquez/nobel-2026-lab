"""Bonus: the mirror race in an unstirred flask. Toy: what Frank's equations do when the flask isn't stirred.

Educational demo made to show an open-source tool. Toy model, not research. Dimensionless units.

The same five reactions, on a grid of cells (periodic edges). Each cell holds whole numbers of molecules.
Each time step, in every cell:
  * reactions: the number of events of each kind is drawn from a Poisson distribution with mean
    (rate x dt) (tau-leaping, an approximate but standard stochastic method), capped so no count goes negative;
  * diffusion: each molecule hops to one of the 4 neighbouring cells with chance 4 D dt (binomial draws).
Molecules of either hand appear by chance, copy themselves locally and spread; where the two hands meet they
pair up and stop. Idea and noise treatment after Hochberg and Zorzano (2006, arXiv:q-bio/0701005), who used a
Langevin version with the A supply held fixed; ours is a closed flask (A runs out), with tau-leaping instead.
"""
import numpy as np

# all choices / tuned for a clear picture on a 128 x 128 grid in a few seconds; none is measured
GRID = 128            # choice
OMEGA = 50            # choice: molecules of A per cell at the start
K0 = 2e-6             # tuned: background, per A molecule (slow, so only a few dozen patches start)
K1 = 1.0              # choice: copying, per unit density (sets the time unit)
K2 = 10.0             # tuned: mutual antagonism, per unit density
D = 0.2               # tuned: hops per molecule per unit time = 4 D
DT = 0.05             # choice: time step (4 D DT = 0.04 hop chance per step)
T_END = 100.0         # tuned: long enough for A to run out and the borders to settle
FRAMES = 60           # choice


def _hop(X, p, rng):
    """Each molecule hops to one of 4 neighbours with total chance p (periodic edges)."""
    out = rng.binomial(X, p)
    X = X - out
    n1 = rng.binomial(out, 0.25)
    n2 = rng.binomial(out - n1, 1 / 3)
    n3 = rng.binomial(out - n1 - n2, 0.5)
    n4 = out - n1 - n2 - n3
    return X + np.roll(n1, 1, 0) + np.roll(n2, -1, 0) + np.roll(n3, 1, 1) + np.roll(n4, -1, 1)


def simulate(seed=20261007, grid=GRID, omega=OMEGA, t_end=T_END, frames=FRAMES):
    rng = np.random.default_rng(seed)
    A = np.full((grid, grid), omega, np.int64)
    R = np.zeros_like(A)
    S = np.zeros_like(A)
    P = np.zeros_like(A)
    n_steps = int(round(t_end / DT))
    t0 = 6.0  # almost nothing visible before this
    u = np.linspace(0, 1, frames)
    save_at = set(np.round((t0 + (t_end - t0) * u ** 2) / DT).astype(int).tolist())  # denser early, when patches form
    shots, times = [], []
    total0 = A.sum()
    for step in range(1, n_steps + 1):
        bgR = rng.poisson(K0 * A * DT)
        bgS = rng.poisson(K0 * A * DT)
        cR = rng.poisson(K1 * A * R / omega * DT)
        cS = rng.poisson(K1 * A * S / omega * DT)
        use = bgR + bgS + cR + cS
        over = use > A
        if over.any():
            f = np.where(over, A / np.maximum(use, 1), 1.0)
            bgR, bgS, cR, cS = (np.floor(x * f).astype(np.int64) for x in (bgR, bgS, cR, cS))
        A -= bgR + bgS + cR + cS
        R += bgR + cR
        S += bgS + cS
        x = np.minimum(rng.poisson(K2 * R * S / omega * DT), np.minimum(R, S))
        R -= x
        S -= x
        P += x
        p = 4 * D * DT
        A, R, S = _hop(A, p, rng), _hop(R, p, rng), _hop(S, p, rng)
        if step in save_at:
            shots.append(np.stack([R, S, P, A]).astype(np.int32))
            times.append(step * DT)
    assert A.sum() + R.sum() + S.sum() + 2 * P.sum() == total0
    return np.asarray(times), np.stack(shots), total0


def colour(frame, bg=(1.0, 1.0, 1.0)):
    """What each cell holds: one hand = burnt orange, mirror hand = teal, mixed pairs = grey, A = background."""
    R, S, P, A = frame.astype(float)
    cols = np.array([[0xc4, 0x62, 0x2d], [0x2b, 0x8a, 0x8f], [140, 140, 140]]) / 255
    w = np.stack([R, S, 2 * P, A], -1)
    tot = w.sum(-1, keepdims=True)
    w = np.where(tot > 0, w / np.maximum(tot, 1), [0, 0, 0, 1])  # an empty cell shows the background
    return w[..., :3] @ cols + w[..., 3:] * np.asarray(bg)
