"""Provenance of LAMBDA_E_M and LAMBDA_ABS_M in telescope/constants.py (not needed to run the toy).

Needs the SPICE ftp-v3m ice files (icemodel.dat, icemodel.par) from the icecube/ppc archive on Zenodo,
https://doi.org/10.5281/zenodo.10410725 (CC-BY-4.0), folder ice/spice_ftp-v3m/. They are not shipped here.

    python scripts/ice_average.py /path/to/ice/spice_ftp-v3m

Formulas (Aartsen et al., NIM A 711 (2013) 73, arXiv:1301.5361, section 4), at 400 nm:
    b_e = column 2 of icemodel.dat
    a   = a_dust(400) + A exp(-B / 400) (1 + 0.01 delta_tau),  A, B from rows 3-4 of icemodel.par
We average the coefficients over the layers between 1450 and 2450 m depth and invert.
Printed on 2026-10-06: lambda_e = 27.8 m, lambda_a = 86.3 m (100 layers).
"""
import sys
from pathlib import Path

import numpy as np

d = Path(sys.argv[1])
ice = np.loadtxt(d / "icemodel.dat")
par = np.loadtxt(d / "icemodel.par")
A, B = par[2, 0], par[3, 0]
m = (ice[:, 0] >= 1450) & (ice[:, 0] <= 2450)
b_e = ice[m, 1]
a = ice[m, 2] + A * np.exp(-B / 400.0) * (1 + 0.01 * ice[m, 3])
print(f"layers {m.sum()}  lambda_e = {1 / b_e.mean():.1f} m  lambda_a = {1 / a.mean():.1f} m")
