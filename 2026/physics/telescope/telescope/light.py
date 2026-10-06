"""Muon tracks and the light they leave in the sensors. Toy model, not research.

One muon = an infinite straight line at the speed of light. For each sensor:
  1. distance d from the track and the "direct" Cherenkov arrival time t_geo = (l + d tan theta_c) / c,
     with l the position of the sensor's closest-approach point along the track;
  2. mean number of photoelectrons mu(d) from a line source of light diffusing through homogeneous ice
     (steady diffusion: fluence = S / (2 pi D) K0(d / L), D = lambda_e / 3, L = sqrt(lambda_a lambda_e / 3));
  3. a Poisson number of photoelectrons; the sensor is hit if it is at least one;
  4. the time of the FIRST photon: each photon is delayed by a Pandel (gamma) delay with shape r / lambda
     (r = d / sin theta_c, the light's path from the track), and we keep the earliest of the N; then
     2 ns of Gaussian timing noise.
"""
from dataclasses import dataclass

import numpy as np
from scipy.special import gammaincinv, k0

from . import constants as K

THETA_C = K.cherenkov_angle()
TAN_C = np.tan(THETA_C)
SIN_C = np.sin(THETA_C)
PANDEL_RATE = K.pandel_rate_per_ns()
# mean photoelectrons = AMPLITUDE * rde * K0(d / L)
AMPLITUDE = K.dom_capture_area_m2() * K.muon_photons_per_m() / (2 * np.pi * K.LAMBDA_E_M / 3.0)
DIFF_LEN = K.diffusion_length_m()


@dataclass(frozen=True)
class Track:
    point: np.ndarray   # (3,) a point on the track (closest approach to the detector centre), m
    dir: np.ndarray     # (3,) unit direction of travel


def mean_pe(d, rde=1.0):
    """Mean number of photoelectrons in a sensor at perpendicular distance d (m) from the muon."""
    return AMPLITUDE * rde * k0(np.maximum(d, K.D_MIN_M) / DIFF_LEN)


def track_coords(xyz, point, u):
    """(l, d): position along the track of each sensor's closest-approach point, and its distance."""
    rel = xyz - point
    l = rel @ u
    d = np.linalg.norm(rel - np.outer(l, u), axis=1)
    return l, d


def direct_time(l, d):
    """Arrival time of unscattered Cherenkov light, ns (the muon passes `point` at t = 0)."""
    return (l + d * TAN_C) / K.C_VAC


def pandel_shape(d):
    return np.maximum(d, K.D_MIN_M) / SIN_C / K.PANDEL_LAMBDA_M


def simulate_hits(xyz, rde, track, rng):
    """Returns (sensor_index, first-photon time ns, charge in photoelectrons) for the hit sensors."""
    l, d = track_coords(xyz, track.point, track.dir)
    near = np.flatnonzero(d < K.D_MAX_M)
    mu = mean_pe(d[near], rde[near])
    n = rng.poisson(mu)
    hit = n > 0
    idx, n = near[hit], n[hit]
    # earliest of n gamma(shape, rate) delays: P(min > t) = (1 - F(t))^n  ->  F(t) = 1 - U^(1/n)
    u = rng.random(len(idx))
    q = -np.expm1(np.log(u) / n)
    delay = gammaincinv(pandel_shape(d[idx]), q) / PANDEL_RATE
    t = direct_time(l[idx], d[idx]) + delay + rng.normal(0.0, K.TIME_JITTER_NS, len(idx))
    return idx, t, n.astype(int)
