"""Sensor layouts: the real 86-string IceCube geometry and synthetic hexagonal grids. Toy model."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import constants as K

DATA = Path(__file__).resolve().parent.parent / "data"
GEOMETRY_CSV = DATA / "icecube86_geometry.csv"


@dataclass(frozen=True)
class Detector:
    name: str
    xyz: np.ndarray        # (n, 3) sensor positions, m
    rde: np.ndarray        # (n,) relative sensor efficiency
    centre: np.ndarray     # (3,) point the generated tracks are aimed around
    n_strings: int
    spacing_m: float | None = None   # None for the real geometry


@lru_cache(maxsize=None)
def icecube() -> Detector:
    """The 5,160 in-ice sensors (strings 1-86, sensors 1-60) from data/icecube86_geometry.csv.

    The centre is the middle of the 78 standard strings (1-78) in x, y and of their depth range in z,
    so the 8 denser DeepCore strings (79-86) do not pull it off-centre."""
    a = np.loadtxt(GEOMETRY_CSV, delimiter=",", comments="#", skiprows=4)
    string, xyz, rde = a[:, 0].astype(int), a[:, 2:5], a[:, 5]
    std = string <= 78
    centre = np.array([xyz[std, 0].mean(), xyz[std, 1].mean(),
                       0.5 * (xyz[std, 2].min() + xyz[std, 2].max())])
    return Detector("IceCube (real 86 strings)", xyz, rde, centre, len(np.unique(string)))


def hex_string_positions(spacing, radius=K.FOOTPRINT_RADIUS_M):
    """Horizontal positions of strings on a triangular ("hexagonal") lattice with the given nearest-neighbour
    spacing, one string at the origin, keeping every string within `radius` of the origin."""
    k = int(radius / spacing) + 2
    i, j = np.meshgrid(np.arange(-k, k + 1), np.arange(-k, k + 1), indexing="ij")
    x = spacing * (i + 0.5 * j).ravel()
    y = spacing * (np.sqrt(3) / 2 * j).ravel()
    keep = np.hypot(x, y) <= radius + 1e-9
    return np.column_stack([x[keep], y[keep]])


@lru_cache(maxsize=None)
def hex_grid(spacing: float) -> Detector:
    """Synthetic detector: strings on a hexagonal lattice filling a 1 km^2 circle, 60 sensors per string
    17 m apart over the same ~1 km of depth (z from -501.5 to +501.5 m), all sensors equally efficient."""
    xy = hex_string_positions(float(spacing))
    z = K.SENSOR_DZ_M * (np.arange(K.SENSORS_PER_STRING) - (K.SENSORS_PER_STRING - 1) / 2)
    xyz = np.column_stack([np.repeat(xy, len(z), axis=0), np.tile(z, len(xy))])
    return Detector(f"hex {spacing:g} m", xyz, np.ones(len(xyz)), np.zeros(3), len(xy), float(spacing))
