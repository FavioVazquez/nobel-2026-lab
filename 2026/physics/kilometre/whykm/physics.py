"""The three calculations: interaction chance in ice, Earth transmission, events per year vs size.

Educational demo made to show an open-source tool. Toy model, not research.
All numbers here are "our toy model, trend only".
"""
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import constants as C

NUFATE = Path(__file__).resolve().parent / "inputs" / "nufate"
SPECIES = ("nue", "nuebar", "numu", "numubar", "nutau", "nutaubar")  # column order of the nuFATE .dat


trapezoid = getattr(np, "trapezoid", None) or np.trapz  # np.trapz is deprecated in NumPy 2


# ------------------------------------------------------------------------------------------------
# Cross sections (nuFATE, MIT). Totals: nuFATE's isoscalar table (CT10nlo, per nucleon 0.5(p+n),
# NuFATECrossSections.h5, exported once to nufate_isoscalar_total_xs.csv, 1e3 to 1e10 GeV).
# CC / NC split: the ratio CC / (CC + NC) from nuFATE's nuSQuIDS-format text tables (100 GeV to 1e9 GeV),
# which are NOT isoscalar below about 1 PeV, so we take only their split, never their size.
# ------------------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def _table(kind):
    """kind 'CC' or 'NC': the text tables; kind 'tot': the isoscalar totals."""
    if kind == "tot":
        t = np.loadtxt(NUFATE / "nufate_isoscalar_total_xs.csv", delimiter=",", comments="#", skiprows=5)
    else:
        t = np.loadtxt(NUFATE / f"nusigma_sigma_{kind}.dat")
    return t[:, 0], {s: t[:, i + 1] for i, s in enumerate(SPECIES)}


def _interp(E, kind, species):
    e, cols = _table(kind)
    if np.any(E < max(e[0], 1e3)) or np.any(E > e[-1]):
        raise ValueError(f"energy outside the nuFATE table for {kind} (1e3 GeV to {e[-1]:.0e} GeV)")
    return np.exp(np.interp(np.log(E), np.log(e), np.log(cols[species])))


def sigma(E_gev, species="numu", kind="tot"):
    """Neutrino-nucleon cross section [cm^2] at energy E [GeV]; kind = 'CC', 'NC' or 'tot' (CC+NC).
    Log-log interpolation; 'tot' covers 1e3..1e10 GeV, 'CC' and 'NC' 1e3..1e9 GeV; outside it raises."""
    E = np.asarray(E_gev, dtype=float)
    tot = _interp(E, "tot", species)
    if kind == "tot":
        return tot
    cc, nc = _interp(E, "CC", species), _interp(E, "NC", species)
    return tot * (cc if kind == "CC" else nc) / (cc + nc)


def sigma_pair(E_gev, flavour="mu", kind="tot"):
    """(nu, nubar) cross sections for one flavour."""
    return sigma(E_gev, f"nu{flavour}", kind), sigma(E_gev, f"nu{flavour}bar", kind)


# ------------------------------------------------------------------------------------------------
# (1) Chance that one neutrino interacts while crossing a slab of ice
# ------------------------------------------------------------------------------------------------
NUCLEONS_PER_CM3_ICE = C.RHO_ICE * C.NUCLEONS_PER_GRAM


def p_interact(E_gev, length_m=1000.0, species="numu"):
    """1 - exp(-n sigma L): chance of a CC or NC interaction along length_m of ice."""
    tau = NUCLEONS_PER_CM3_ICE * sigma(E_gev, species) * length_m * C.CM_PER_M
    return -np.expm1(-tau)


def p_interact_flavour(E_gev, length_m=1000.0, flavour="mu"):
    """Average of neutrino and antineutrino (equal numbers, as in the HESE flux assumption)."""
    return 0.5 * (p_interact(E_gev, length_m, f"nu{flavour}") + p_interact(E_gev, length_m, f"nu{flavour}bar"))


# ------------------------------------------------------------------------------------------------
# (2) Earth: density and column depth (nuFATE earth.py polynomial fit to STW105, MIT, re-written
#     vectorised; tests check it against the original function shipped in inputs/nufate/earth.py)
# ------------------------------------------------------------------------------------------------
_SHELLS = (  # (outer radius km, p1, p2, p3): rho[kg/m^3] = p1 r^2 + p2 r + p3, r in km
    (1221.0, -0.0002177, -4.265e-06, 1.309e04),
    (3480.0, -0.0002409, 0.1416, 1.234e04),
    (5721.0, -3.764e-05, -0.1876, 6664.0),
    (5961.0, 0.0, -1.269, 1.131e04),
    (6347.0, 0.0, -0.725, 7887.0),
    (6356.0, 0.0, 0.0, 2900.0),
    (6368.0, 0.0, 0.0, 2600.0),
    (np.inf, 0.0, 0.0, 1020.0),
)


def rho_earth(r_km):
    """Earth density [g/cm^3] at radius r [km] (nuFATE / STW105 fit)."""
    r = np.asarray(r_km, dtype=float)
    out = np.empty_like(r)
    lo = -np.inf
    for hi, p1, p2, p3 in _SHELLS:
        m = (r >= lo) & (r < hi)
        out[m] = p1 * r[m] ** 2 + p2 * r[m] + p3
        lo = hi
    return out * 1e-3


def path_length_km(cos_zenith, depth_km=C.DETECTOR_DEPTH_KM):
    """Distance from the detector back to where the neutrino entered the Earth (nuFATE geometry)."""
    c = np.asarray(cos_zenith, dtype=float)
    Rd = C.R_EARTH_KM - depth_km
    return np.sqrt(Rd**2 * c**2 + depth_km * (2 * C.R_EARTH_KM - depth_km)) - Rd * c


def column_depth(cos_zenith, depth_km=C.DETECTOR_DEPTH_KM, n=20001):
    """Matter crossed [g/cm^2] by a neutrino arriving from zenith angle theta (cos = cos_zenith).
    cos = +1 straight down from the sky, cos = -1 straight up through the Earth's centre."""
    c = np.atleast_1d(np.asarray(cos_zenith, dtype=float))
    out = np.empty_like(c)
    Rd = C.R_EARTH_KM - depth_km
    for i, ci in enumerate(c):
        L = float(path_length_km(ci, depth_km))
        x = np.linspace(0.0, L, n)
        r = np.sqrt(np.maximum(Rd**2 + x**2 + 2 * Rd * x * ci, 0.0))
        out[i] = trapezoid(rho_earth(r), x) * C.CM_PER_KM
    return out if np.ndim(cos_zenith) else out[0]


def transmission(E_gev, cos_zenith, species="numu", depth_km=C.DETECTOR_DEPTH_KM, X=None):
    """Fraction that crosses the Earth without interacting: exp(-N_A sigma_tot X).
    Simplified: every CC or NC interaction removes the neutrino (no regeneration, no NC energy loss)."""
    E = np.asarray(E_gev, dtype=float)
    X = column_depth(cos_zenith, depth_km) if X is None else np.asarray(X)
    s = sigma(E, species)
    return np.exp(-np.multiply.outer(s, X) * C.NUCLEONS_PER_GRAM)


def transmission_flavour(E_gev, cos_zenith, flavour="mu", X=None):
    X = column_depth(cos_zenith) if X is None else X
    return 0.5 * (transmission(E_gev, None, f"nu{flavour}", X=X) + transmission(E_gev, None, f"nu{flavour}bar", X=X))


# ------------------------------------------------------------------------------------------------
# (3) Expected interactions per year inside a cube of ice, for the HESE 7.5-year flux
# ------------------------------------------------------------------------------------------------
def flux_per_species(E_gev, phi=C.HESE_PHI_ASTRO, gamma=C.HESE_GAMMA):
    """dPhi/dE for ONE of the six species [GeV^-1 cm^-2 s^-1 sr^-1] (all-flavour HESE fit / 6)."""
    return phi * C.HESE_FLUX_UNIT / C.N_SPECIES * (np.asarray(E_gev) / C.HESE_E0_GEV) ** (-gamma)


@lru_cache(maxsize=4)
def _angular_grid(n_cos=801):
    # denser near the horizon, where the column depth changes fastest
    u = np.linspace(-1.0, 1.0, n_cos)
    cosz = np.sign(u) * np.abs(u) ** 2
    return cosz, column_depth(cosz, n=8001)


def rate_density(E_gev, species, kind="tot", earth=True, phi=C.HESE_PHI_ASTRO, gamma=C.HESE_GAMMA,
                 hemisphere="all"):
    """Interactions per second per nucleon per GeV (thin target: rate = flux x sigma x nucleons),
    integrated over all arrival directions. With earth=True each direction is weighted by its Earth
    transmission. hemisphere: 'all', 'up' (cos < 0, through the Earth) or 'down'."""
    E = np.atleast_1d(np.asarray(E_gev, dtype=float))
    cosz, X = _angular_grid()
    T = transmission(E, None, species, X=X) if earth else np.ones((E.size, cosz.size))
    if hemisphere != "all":
        T = T * ((cosz < 0) if hemisphere == "up" else (cosz >= 0))
    omega = 2 * np.pi * trapezoid(T, cosz, axis=1)  # effective solid angle [sr]
    return flux_per_species(E, phi, gamma) * sigma(E, species, kind) * omega


def events_per_year_per_nucleon(e_min=C.E_THRESHOLD_GEV, e_max=C.E_MAX_GEV, n_e=400, species=SPECIES,
                                kind="tot", earth=True, hemisphere="all", **flux):
    lnE = np.linspace(np.log(e_min), np.log(e_max), n_e)
    E = np.exp(lnE)
    tot = 0.0
    for s in species:
        tot += trapezoid(rate_density(E, s, kind, earth, hemisphere=hemisphere, **flux) * E, lnE)
    return tot * C.SECONDS_PER_YEAR


def nucleons_in_cube(side_m):
    return NUCLEONS_PER_CM3_ICE * (np.asarray(side_m, dtype=float) * C.CM_PER_M) ** 3


def events_per_year(side_m, **kw):
    """Expected interactions per year inside an ice cube of the given side (thin-target: the chance to
    interact inside is tiny even for 2 km, so the count scales exactly with volume, whatever the shape)."""
    return nucleons_in_cube(side_m) * events_per_year_per_nucleon(**kw)


def thin_target_error(side_m=2000.0, E_gev=C.E_MAX_GEV):
    """How wrong is 'rate = n sigma V' at the largest size and energy? Relative error of n*sigma*L vs
    1-exp(-n*sigma*L) for the longest straight path across the cube (its space diagonal)."""
    L = np.sqrt(3) * side_m
    tau = NUCLEONS_PER_CM3_ICE * sigma(E_gev, "numu") * L * C.CM_PER_M
    return float(tau / -np.expm1(-tau) - 1.0)
