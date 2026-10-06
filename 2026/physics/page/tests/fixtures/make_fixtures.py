"""Write PLACEHOLDER inputs for the page (educational demo, toy models; not research).

These files only follow the two experiments' output schemas so the page can be built and tested before
../kilometre and ../telescope have run. Their status is "fixture" and the page says "placeholder numbers"
when built from them. The numbers are rough hand estimates, not results of either experiment.

    python3 tests/fixtures/make_fixtures.py DATA_DIR   (DATA_DIR holds xsec/ and ppc_ice/; needs numpy)
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = Path(sys.argv[1])
NA = 6.022e23
RHO_ICE = 0.92  # g/cm^3
R_E = 6371.0

cc = np.loadtxt(DATA / "xsec/nufate_nusigma_sigma_CC.dat")
nc = np.loadtxt(DATA / "xsec/nufate_nusigma_sigma_NC.dat")
E = cc[:, 0]
sig = cc[:, 3] + nc[:, 3]  # nu_mu, CC + NC, cm^2


def sigma(e):
    return float(np.exp(np.interp(np.log(e), np.log(E), np.log(sig))))


def rho(r):  # nuFATE earth.py fit, g/cm^3
    r = np.asarray(r)
    out = np.where(r < 1221, -0.0002177 * r**2 - 4.265e-06 * r + 1.309e4,
          np.where(r < 3480, -0.0002409 * r**2 + 0.1416 * r + 1.234e4,
          np.where(r < 5721, -3.764e-05 * r**2 - 0.1876 * r + 6664,
          np.where(r < 5961, -1.269 * r + 1.131e4,
          np.where(r < 6347, -0.725 * r + 7887,
          np.where(r < 6356, 2900., np.where(r < 6368, 2600., 1020.)))))))
    return out * 1e-3


def column(cosz, n=4000):
    if cosz >= 0:
        return 0.0
    L = -2 * R_E * cosz
    x = np.linspace(0, L, n)
    r = np.sqrt(R_E**2 + x**2 + 2 * R_E * x * cosz)
    return float(np.trapz(rho(r), x) * 1e5)


def p_int(e, L_cm=1e5):
    return 1 - math.exp(-NA * RHO_ICE * sigma(e) * L_cm)


km = HERE / "kilometre/results"
energies = np.logspace(3, 7, 41)  # GeV
with open(km / "interaction_vs_energy.csv", "w") as f:
    f.write("# PLACEHOLDER fixture for the page tests, not a result\nenergy_GeV,p_interact_1km\n")
    for e in energies:
        f.write(f"{e:.4g},{p_int(e):.4g}\n")
with open(km / "earth_transmission_1PeV.csv", "w") as f:
    f.write("# PLACEHOLDER fixture for the page tests, not a result\nzenith_deg,transmission\n")
    for z in range(90, 181, 2):
        f.write(f"{z},{math.exp(-NA * sigma(1e6) * column(math.cos(math.radians(z)))):.4g}\n")
sides = np.logspace(1, math.log10(2000), 25)
per_km3 = 9.0  # hand estimate for the placeholder only
with open(km / "events_vs_size.csv", "w") as f:
    f.write("# PLACEHOLDER fixture for the page tests, not a result\nside_m,events_per_year\n")
    for s in sides:
        f.write(f"{s:.4g},{per_km3 * (s / 1000) ** 3:.4g}\n")
p100, p1 = p_int(1e5), p_int(1e6)
summary = {
    "status": "fixture",
    "p_interact_1km": {"100TeV": float(f"{p100:.3g}"), "1PeV": float(f"{p1:.3g}")},
    "one_in_N_100TeV": round(1 / p100),
    "earth_survival_vertical": {"100TeV": float(f"{math.exp(-NA * sigma(1e5) * column(-1)):.3g}"),
                                "1PeV": float(f"{math.exp(-NA * sigma(1e6) * column(-1)):.3g}")},
    "events_per_year": {"10m": per_km3 * 1e-6, "100m": per_km3 * 1e-3, "1km": per_km3},
    "hese_check": {"observed_per_year_above_60TeV": 8.0, "ours_1km3_per_year": per_km3,
                   "note": "placeholder fixture"},
    "sources": {"cross_sections": "nuFATE tables (placeholder use)"},
    "label": "our toy model, trend only",
}
(km / "kilometre_summary.json").write_text(json.dumps(summary, indent=2))

# Telescope: a smooth placeholder curve and a fake event drawn on the real geometry (ppc geo-f2k, CC-BY-4.0).
sp = [50, 80, 125, 160, 200, 250, 300]
tel = HERE / "telescope/results"
line = [round(0.9 * (s / 50) ** 0.9, 2) for s in sp]
pandel = [round(0.2 * (s / 50) ** 1.6, 2) for s in sp]
hits = [int(1500 * (50 / s) ** 2) for s in sp]
(tel / "telescope_summary.json").write_text(json.dumps({
    "status": "fixture", "spacings_m": sp,
    "median_error_deg": {"line": line, "pandel": pandel},
    "p68_error_deg": {"line": [round(v * 1.8, 2) for v in line], "pandel": [round(v * 1.9, 2) for v in pandel]},
    "median_hits": hits,
    "icecube_real": {"median_error_deg": {"line": 2.0, "pandel": 0.5}, "median_hits": 250},
    "events_per_point": 0, "label": "our toy model, tuned constants, trend only"}, indent=2))

g = []
for ln in (DATA / "ppc_ice/ice_spice_ftp-v3m_geo-f2k").read_text().split("\n"):
    p = ln.split()
    if len(p) >= 7 and 1 <= int(p[5]) <= 86 and 1 <= int(p[6]) <= 60:
        g.append((int(p[5]), int(p[6]), float(p[2]), float(p[3]), float(p[4])))
g.sort()
pos = np.array([r[2:] for r in g])
z0 = np.mean(pos[:, 2])
rng = np.random.default_rng(7)
d = np.array([0.55, -0.35, -0.76]); d /= np.linalg.norm(d)
p0 = np.array([30.0, -40.0, z0])
c, n = 0.2998, 1.32
out = []
for i, x in enumerate(pos):
    v = x - p0
    l = v @ d
    rho_ = np.linalg.norm(v - l * d)
    if rho_ < 160 and rng.random() < math.exp(-rho_ / 60):
        t = (l + rho_ * math.tan(math.acos(1 / n))) / c + rng.gamma(1.2, 8 + rho_ / 3)
        out.append([i, round(t, 1), round(float(rng.exponential(1 + 30 / (rho_ + 5))), 2)])
t0 = min(h[1] for h in out)
for h in out:
    h[1] = round(h[1] - t0, 1)
out.sort(key=lambda h: h[1])


def tilt(v, deg, axis):
    a = np.radians(deg); axis = np.asarray(axis, float); axis /= np.linalg.norm(axis)
    return (v * np.cos(a) + np.cross(axis, v) * np.sin(a) + axis * (axis @ v) * (1 - np.cos(a))).tolist()


(tel / "example_event.json").write_text(json.dumps({
    "note": "PLACEHOLDER fixture for the page tests, not a simulated event",
    "track": {"point": p0.round(1).tolist(), "dir": d.round(4).tolist()},
    "hits": out, "line_fit_dir": tilt(d, 2.0, [0, 0, 1]), "pandel_fit_dir": tilt(d, 0.5, [1, 0, 0]),
    "error_deg": {"line": 2.0, "pandel": 0.5},
}))
with open(tel / "geometry_fixture.csv", "w") as f:
    f.write("# PLACEHOLDER subset for the page tests: IceCube sensor positions from icecube/ppc geo-f2k (Zenodo, CC-BY-4.0)\n")
    f.write("index,string,om,x_m,y_m,z_m\n")
    keep = {h[0] for h in out}
    for i, (s, o, x, y, z) in enumerate(g):
        if o == 1 or i in keep:  # a subset: the top sensor of every string plus the sensors in the event
            f.write(f"{i},{s},{o},{x:.2f},{y:.2f},{z:.2f}\n")
print("fixtures written:", len(out), "hits;", f"p100={p100:.3g} p1={p1:.3g}",
      "surv1PeV", summary["earth_survival_vertical"])
