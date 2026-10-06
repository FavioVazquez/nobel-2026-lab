"""Every number the toy telescope uses, with its source or the word "tuned".

Educational demo made to show an open-source tool. Toy model, not research.

Status words used below:
  [verified]  read in the source text during this build (2026-10-06)
  [computed]  our own arithmetic from a verified input, done in code (see the function named)
  [literature] a standard literature value, cited, not re-opened in this build
  [tuned]     our choice for this toy; no single published value
"""
import math
import os

# --- light and medium -------------------------------------------------------------------------
C_VAC = 0.299792458          # m/ns, speed of light in vacuum (exact, SI definition)
ALPHA_FS = 1 / 137.035999    # fine-structure constant (CODATA) [literature]
N_ICE = 1.32                 # phase refractive index of deep ice near 400 nm [literature: Price & Bergstrom,
                             # Appl. Opt. 36 (1997) 4181]. Used for the Cherenkov angle AND the light speed
                             # (a real model uses the group index ~1.35 for speed; simplification).
LAMBDA_MIN_NM = 300.0        # Cherenkov band counted, lower edge [tuned: roughly the DOM glass cut-off]
LAMBDA_MAX_NM = 500.0        # upper edge [tuned: roughly where the PMT efficiency falls off]

# Ice averaged over the instrumented depth 1450-2450 m at 400 nm, from the SPICE ftp-v3m table
# (icecube/ppc ice/spice_ftp-v3m/icemodel.dat + icemodel.par, Zenodo 10.5281/zenodo.10410725, CC-BY-4.0;
# formulas of Aartsen et al., NIM A 711 (2013) 73, arXiv:1301.5361, section 4). 100 layers of 10 m;
# we average the COEFFICIENTS (1/m) and invert. Recompute with scripts/ice_average.py. [computed]
LAMBDA_E_M = 27.8            # effective scattering length, 1 / mean(b_e(400))
LAMBDA_ABS_M = 86.3          # absorption length, 1 / mean(a(400))

# Pandel delay-time model for the arrival-time spread, parameters as used in AMANDA reconstruction:
# Ahrens et al. (AMANDA), NIM A 524 (2004) 169, arXiv:astro-ph/0407044, eq. (19): [verified]
PANDEL_TAU_NS = 557.0
PANDEL_LAMBDA_M = 33.3
PANDEL_LAMBDA_A_M = 98.0
# Sensitivity run only: TELESCOPE_PANDEL="lambda_m,tau_ns,lambda_a_m" replaces the three values above (used by
# run_all for the "delays from our photon walk" variant; see photon_check.py). Unset for the main results.
if os.environ.get("TELESCOPE_PANDEL"):
    PANDEL_LAMBDA_M, PANDEL_TAU_NS, PANDEL_LAMBDA_A_M = map(float, os.environ["TELESCOPE_PANDEL"].split(","))
# (The same paper also uses an effective distance d_eff = a0 + a1 d that depends on the sensor's
# orientation; our sensors look in all directions, so we use the plain distance. Simplification.)

TIME_JITTER_NS = 2.0         # Gaussian hit-time noise. IceCube DAQ paper, Abbasi et al., NIM A 601 (2009) 294,
                             # arXiv:0810.4930: leading-edge time estimators give "precision on the order of
                             # 1-2 ns RMS" [verified]; we take the upper end.

# --- the muon ----------------------------------------------------------------------------------
MUON_ENERGY_GEV = 1000.0     # every muon is 1 TeV, held constant along the track [tuned]
ICE_DENSITY_G_CM3 = 0.917    # density of ice [literature]
MUON_B_PER_M = 0.363e-3 * ICE_DENSITY_G_CM3  # radiative energy-loss coefficient b in dE/dx = a + b E for ice:
                             # b = 0.363e-3 per m.w.e. (fit in Fig. 21 of Chirkin & Rhode, "Propagating leptons
                             # through matter with Muon Monte Carlo", arXiv:hep-ph/0407075) [verified],
                             # times the ice density -> 3.33e-4 per metre [computed]
CASCADE_TRACK_M_PER_GEV = 5.321  # total Cherenkov track length of electromagnetic showers per GeV in ice,
                                 # alpha = 532.1 cm/GeV, eq. (8) of Radel & Wiebusch, Astropart. Phys. 44 (2013) 102,
                                 # arXiv:1210.5140 [verified]

# --- the sensor --------------------------------------------------------------------------------
DOM_RADIUS_M = 0.1651        # IceCube digital optical module radius (icecube/ppc om.conf "Default" row) [verified]
DOM_QE = 0.25                # peak quantum efficiency of the 10-inch PMT, "approximately 25% at 390 nm"
                             # (Abbasi et al., NIM A 618 (2010) 139, arXiv:1002.2442) [verified]
DOM_ACCEPT_FACTOR = 0.2      # averages the PMT's angle acceptance, the spectrum and the glass/gel losses into one
                             # number [tuned: order of magnitude only; it sets how far from the track sensors fire]
HQE_RDE = 1.35               # relative efficiency of high-QE (DeepCore) sensors (icecube/ppc docs, eff-f2k:
                             # "nominally 1.35") [verified]

# --- detector layout for the synthetic grids -----------------------------------------------------
SENSORS_PER_STRING = 60      # IceCube: 60 per string [verified: arXiv:1301.5361 text]
SENSOR_DZ_M = 17.0           # IceCube: 17 m apart [verified: same]
FOOTPRINT_AREA_M2 = 1.0e6    # synthetic grids fill a circle of 1 km^2 [tuned: about IceCube's footprint]
FOOTPRINT_RADIUS_M = math.sqrt(FOOTPRINT_AREA_M2 / math.pi)   # 564.2 m

# --- events and selection ----------------------------------------------------------------------
GEN_RADIUS_M = 700.0         # track impact points uniform on a disc of this radius, centred on the detector [tuned]
SEL_RADIUS_M = 500.0         # keep tracks that run at least SEL_MIN_PATH_M inside this cylinder ... [tuned]
SEL_HALF_HEIGHT_M = 500.0    # ... of this half-height (the instrumented 1 km of depth) [tuned]
SEL_MIN_PATH_M = 300.0       # [tuned]
TRIGGER_MIN_HITS = 8         # at least 8 hit sensors; loosely after IceCube's 8-sensor trigger, without its
                             # local-coincidence condition [tuned]
D_MIN_M = 0.5                # distances below this are clamped (avoids log divergences) [tuned]
D_MAX_M = 400.0              # sensors farther than this from the track are skipped (mean charge < 1e-6) [tuned]

# --- the Pandel fit ------------------------------------------------------------------------------
FIT_EARLY_SIGMA_NS = 10.0    # width of the Gaussian tail used for hits earlier than the direct-light time [tuned]
FIT_NOISE_FLOOR = 1e-7       # per-ns floor added to the time pdf so one odd hit cannot dominate [tuned]


def cherenkov_angle(n=N_ICE, beta=1.0):
    """cos(theta_c) = 1 / (n beta)  (Cherenkov 1934; Frank & Tamm 1937)."""
    return math.acos(1.0 / (n * beta))


def frank_tamm_photons_per_m(n=N_ICE, lmin_nm=LAMBDA_MIN_NM, lmax_nm=LAMBDA_MAX_NM, beta=1.0):
    """Photons per metre of a charge-1 particle, integrated over [lmin, lmax] with constant n.

    Frank-Tamm: d2N/dx dlambda = 2 pi alpha / lambda^2 (1 - 1/(beta^2 n^2))
    (I. Frank & I. Tamm, Dokl. Akad. Nauk SSSR 14 (1937) 109; as written in the PDG Review of Particle
    Physics, "Passage of particles through matter", Cherenkov section).  [computed] ~2.6e4 /m (260 /cm)."""
    return 2 * math.pi * ALPHA_FS * (1 - 1 / (beta * n) ** 2) * (1e9 / lmin_nm - 1e9 / lmax_nm)


def muon_photons_per_m(energy_gev=MUON_ENERGY_GEV):
    """Bare-muon Cherenkov light plus the light of its radiative losses (showers along the track):
    N = N_bare * (1 + b E * 5.3 m/GeV).  At 1 TeV the factor is about 2.7.  [computed]"""
    return frank_tamm_photons_per_m() * (1 + MUON_B_PER_M * energy_gev * CASCADE_TRACK_M_PER_GEV)


def dom_capture_area_m2():
    """Effective light-catching area of one sensor: pi r^2 x QE x acceptance factor (~0.004 m^2). [tuned]"""
    return math.pi * DOM_RADIUS_M ** 2 * DOM_QE * DOM_ACCEPT_FACTOR


def diffusion_length_m():
    """How far scattered light gets before it is absorbed: sqrt(lambda_a lambda_e / 3) (~28 m). [computed]"""
    return math.sqrt(LAMBDA_ABS_M * LAMBDA_E_M / 3.0)


def pandel_rate_per_ns():
    """Rate of the Pandel gamma distribution: 1/tau + (c/n)/lambda_a (Ahrens et al. 2004, section 4)."""
    return 1.0 / PANDEL_TAU_NS + (C_VAC / N_ICE) / PANDEL_LAMBDA_A_M
