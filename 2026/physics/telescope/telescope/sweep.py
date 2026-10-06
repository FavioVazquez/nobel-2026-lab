"""Run many muons through one detector: simulate hits, fit, record the errors. Toy model.

Every event's random numbers come from numpy's generator seeded with (seed, geometry code, event number),
so results do not depend on the number of worker processes or on the order they run in.
"""
import os
from multiprocessing import get_context

import numpy as np

from . import constants as K
from .events import generate_tracks, shifted
from .geometry import hex_grid, icecube
from .light import simulate_hits
from .reco import angle_deg, line_fit, pandel_fit

FIELDS = ("event", "n_hits", "n_strings_hit", "charge_pe", "triggered", "err_line_deg", "err_pandel_deg",
          "line_speed_m_per_ns")


def detector(key):
    return icecube() if key == "icecube" else hex_grid(float(key))


def geom_code(key):
    return 0 if key == "icecube" else int(round(float(key)))


def event_rng(seed, key, i):
    return np.random.default_rng([seed, geom_code(key), i])


def run_event(key, track0, i, seed, keep_hits=False):
    det = detector(key)
    tr = shifted(track0, det.centre)
    idx, t, q = simulate_hits(det.xyz, det.rde, tr, event_rng(seed, key, i))
    strings = len(np.unique(np.round(det.xyz[idx, :2], 1), axis=0)) if len(idx) else 0
    out = dict(event=i, n_hits=len(idx), n_strings_hit=strings, charge_pe=int(q.sum()),
               triggered=int(len(idx) >= K.TRIGGER_MIN_HITS), err_line_deg=np.nan, err_pandel_deg=np.nan,
               line_speed_m_per_ns=np.nan)
    if out["triggered"]:
        r = det.xyz[idx]
        u_l, p_l, speed = line_fit(r, t)
        u_p, p_p, _ = pandel_fit(r, t, u_l, p_l)
        out.update(err_line_deg=angle_deg(u_l, tr.dir), err_pandel_deg=angle_deg(u_p, tr.dir),
                   line_speed_m_per_ns=speed)
        if keep_hits:
            out.update(track=tr, hits=(idx, t, q), line=(u_l, p_l), pandel=(u_p, p_p))
    return out


def _job(args):
    key, tracks, first, seed = args
    return [run_event(key, tr, first + j, seed) for j, tr in enumerate(tracks)]


def run_geometry(key, tracks, seed, workers=None, chunk=10):
    """Returns a dict of numpy arrays (one entry per field) for all tracks on one detector."""
    workers = workers or os.cpu_count()
    jobs = [(key, tracks[i:i + chunk], i, seed) for i in range(0, len(tracks), chunk)]
    if workers == 1:
        rows = [r for j in jobs for r in _job(j)]
    else:
        with get_context("fork").Pool(workers) as pool:
            rows = [r for part in pool.imap(_job, jobs) for r in part]
    return {f: np.array([r[f] for r in rows]) for f in FIELDS}


def tracks_for(n, seed):
    return generate_tracks(n, seed)
