"""Seeded, reproducible through-going muon tracks. Toy model.

Directions: isotropic (cos(zenith) uniform in [-1, 1], azimuth uniform in [0, 2 pi)), i.e. muons from every
direction equally, up-going and down-going. Impact points: uniform over a 700 m disc perpendicular to the
track, centred on the detector centre (this is what a uniform flux of parallel tracks looks like).
Kept: tracks that run at least 300 m inside a cylinder of radius 500 m and half-height 500 m around the
centre. The same list of tracks (shifted to each detector's centre) is used for every geometry.
"""
import numpy as np

from . import constants as K
from .light import Track


def perp_basis(u):
    a = np.array([0.0, 0.0, 1.0]) if abs(u[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    e1 = np.cross(u, a)
    e1 /= np.linalg.norm(e1)
    return e1, np.cross(u, e1)


def path_in_cylinder(point, u, radius=K.SEL_RADIUS_M, half_height=K.SEL_HALF_HEIGHT_M):
    """Length of the line point + s u inside the vertical cylinder |(x, y)| <= radius, |z| <= half_height."""
    px, py, pz = point
    ux, uy, uz = u
    a = ux * ux + uy * uy
    if a < 1e-12:
        if px * px + py * py > radius ** 2:
            return 0.0
        lo, hi = -np.inf, np.inf
    else:
        b = px * ux + py * uy
        disc = b * b - a * (px * px + py * py - radius ** 2)
        if disc <= 0:
            return 0.0
        sq = np.sqrt(disc)
        lo, hi = (-b - sq) / a, (-b + sq) / a
    if abs(uz) < 1e-12:
        if abs(pz) > half_height:
            return 0.0
    else:
        z1, z2 = sorted(((-half_height - pz) / uz, (half_height - pz) / uz))
        lo, hi = max(lo, z1), min(hi, z2)
    return max(0.0, hi - lo)


def generate_tracks(n, seed=2026):
    """n accepted tracks around the origin; the same seed always gives the same list."""
    rng = np.random.default_rng(seed)
    out = []
    while len(out) < n:
        cz = rng.uniform(-1, 1)
        phi = rng.uniform(0, 2 * np.pi)
        sz = np.sqrt(1 - cz * cz)
        u = np.array([sz * np.cos(phi), sz * np.sin(phi), cz])
        e1, e2 = perp_basis(u)
        rho = K.GEN_RADIUS_M * np.sqrt(rng.random())
        psi = rng.uniform(0, 2 * np.pi)
        p = rho * (np.cos(psi) * e1 + np.sin(psi) * e2)
        if path_in_cylinder(p, u) >= K.SEL_MIN_PATH_M:
            out.append(Track(p, u))
    return out


def shifted(track, centre):
    return Track(track.point + centre, track.dir)
