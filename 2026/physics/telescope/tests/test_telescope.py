"""Fast checks of the toy telescope (well under a minute). Run from 2026/physics/telescope: python -m pytest -q tests"""
import json
import math
from pathlib import Path

import numpy as np
import pytest

from telescope import constants as K
from telescope.events import generate_tracks, path_in_cylinder
from telescope.geometry import hex_grid, hex_string_positions, icecube
from telescope.light import TAN_C, Track, direct_time, mean_pe, simulate_hits, track_coords
from telescope.reco import angle_deg, line_fit, pandel_fit, pandel_logpdf
from telescope.run_all import pick_example
from telescope.sweep import run_geometry

RESULTS = Path(__file__).resolve().parent.parent / "results"


def test_real_geometry():
    det = icecube()
    assert det.xyz.shape == (5160, 3) and det.n_strings == 86
    # standard string 36 (near the centre): 60 sensors, about 17 m apart
    a = np.loadtxt(Path(__file__).resolve().parent.parent / "data" / "icecube86_geometry.csv",
                   delimiter=",", comments="#", skiprows=4)
    z = np.sort(a[a[:, 0] == 36, 4])
    assert len(z) == 60 and abs(np.median(np.diff(z)) - 17.0) < 0.2
    assert set(np.unique(det.rde)) == {1.0, 1.35}
    assert np.all(np.abs(det.centre[:2]) < 50)


@pytest.mark.parametrize("s", [50, 125, 300])
def test_hex_grid(s):
    xy = hex_string_positions(s)
    dist = np.linalg.norm(xy[:, None] - xy[None], axis=2) + np.eye(len(xy)) * 1e9
    assert np.allclose(dist.min(1), s)
    assert np.all(np.hypot(*xy.T) <= K.FOOTPRINT_RADIUS_M + 1e-6)
    g = hex_grid(s)
    assert len(g.xyz) == 60 * g.n_strings
    assert np.ptp(g.xyz[:, 2]) == pytest.approx(59 * 17.0)


def test_constants():
    assert math.degrees(K.cherenkov_angle()) == pytest.approx(40.75, abs=0.05)
    assert 250e2 < K.frank_tamm_photons_per_m() < 270e2          # ~260 photons per cm, 300-500 nm
    assert K.muon_photons_per_m() / K.frank_tamm_photons_per_m() == pytest.approx(2.77, abs=0.03)
    assert K.diffusion_length_m() == pytest.approx(28.3, abs=0.1)


def test_light_falls_with_distance():
    d = np.array([5, 20, 50, 100, 200.0])
    mu = mean_pe(d)
    assert np.all(np.diff(mu) < 0) and mu[0] > 1 and mu[-1] < 0.01


def test_direct_time_matches_cherenkov_geometry():
    # sensor 40 m from a track along +z; the light leaves the track at z_e and travels at c/n at theta_c
    d, zs = 40.0, 100.0
    l, dd = track_coords(np.array([[d, 0, zs]]), np.zeros(3), np.array([0, 0, 1.0]))
    th = K.cherenkov_angle()
    z_e = zs - d / math.tan(th)
    t = z_e / K.C_VAC + K.N_ICE * math.hypot(d, zs - z_e) / K.C_VAC
    assert direct_time(l, dd)[0] == pytest.approx(t, rel=1e-9)
    assert TAN_C == pytest.approx(math.sqrt(K.N_ICE ** 2 - 1))


def test_hits_reproducible_and_causal():
    det = hex_grid(125)
    tr = Track(np.zeros(3), np.array([0.6, 0.0, 0.8]))
    a = simulate_hits(det.xyz, det.rde, tr, np.random.default_rng(5))
    b = simulate_hits(det.xyz, det.rde, tr, np.random.default_rng(5))
    assert all(np.array_equal(x, y) for x, y in zip(a, b))
    idx, t, q = a
    l, d = track_coords(det.xyz[idx], tr.point, tr.dir)
    assert np.all(t - direct_time(l, d) > -6 * K.TIME_JITTER_NS) and np.all(q >= 1)


def test_line_fit_exact_for_a_moving_point():
    u = np.array([1.0, 2.0, -0.5]) / np.linalg.norm([1.0, 2.0, -0.5])
    t = np.linspace(0, 3000, 30)
    r = np.array([10.0, -5, 3]) + np.outer(0.3 * t, u)
    uf, _, speed = line_fit(r, t)
    assert angle_deg(uf, u) < 1e-6 and speed == pytest.approx(0.3)


def test_pandel_pdf_is_normalised():
    t = np.linspace(-200, 20000, 400001)
    for d in (20.0, 80.0):
        p = np.exp(pandel_logpdf(t, np.full_like(t, d)))
        integral = np.sum(p) * (t[1] - t[0])
        assert 0.95 < integral < 1.1    # patched: a flat piece, an early Gaussian tail and a small floor


def test_tracks_reproducible_and_selected():
    a, b = generate_tracks(50, 3), generate_tracks(50, 3)
    assert all(np.array_equal(x.point, y.point) and np.array_equal(x.dir, y.dir) for x, y in zip(a, b))
    assert all(path_in_cylinder(t.point, t.dir) >= K.SEL_MIN_PATH_M for t in a)
    assert path_in_cylinder(np.zeros(3), np.array([0, 0, 1.0])) == pytest.approx(1000)
    assert path_in_cylinder(np.zeros(3), np.array([1.0, 0, 0])) == pytest.approx(1000)


def test_pandel_beats_line_fit_on_a_dense_grid():
    R = run_geometry("80", generate_tracks(12, 11), seed=1, workers=1)
    assert R["triggered"].all()
    assert np.median(R["err_pandel_deg"]) < 0.5 * np.median(R["err_line_deg"])


def test_pick_example_is_typical():
    n = 101
    R = dict(event=np.arange(n), triggered=np.ones(n, int), err_pandel_deg=np.arange(n, dtype=float),
             n_hits=np.arange(n))
    assert pick_example(R) == 50


def test_summary_files_if_present():
    p = RESULTS / "telescope_summary.json"
    if not p.exists():
        pytest.skip("no results yet")
    S = json.loads(p.read_text())
    for k in ("status", "spacings_m", "median_error_deg", "p68_error_deg", "median_hits", "icecube_real",
              "events_per_point", "label"):
        assert k in S
    assert "toy" in S["label"] and "trend only" in S["label"]
    assert len(S["median_error_deg"]["pandel"]) == len(S["spacings_m"])
    E = json.loads((RESULTS / "example_event.json").read_text())
    assert {"track", "hits", "line_fit_dir", "pandel_fit_dir", "error_deg"} <= set(E)
    assert max(h[0] for h in E["hits"]) < 5160
