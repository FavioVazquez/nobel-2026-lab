"""Every constant the toy uses, with its source or the word "choice" (our own setting).

Educational demo made to show an open-source tool. Toy model, not research.
"""

# --- plain physics -------------------------------------------------------------------------------
N_A = 6.02214076e23  # Avogadro constant [1/mol], exact SI value (2019 SI redefinition)
# Nucleons per gram of matter. We treat ice and rock as "isoscalar" (equal protons and neutrons, one
# nucleon per atomic mass unit), the same convention as nuFATE's isoscalar per-nucleon cross sections. Choice.
NUCLEONS_PER_GRAM = N_A
RHO_ICE = 0.917  # density of ice Ih near 0 C [g/cm^3], textbook value; deep South Pole ice is ~0.92
CM_PER_KM = 1.0e5
CM_PER_M = 1.0e2
SECONDS_PER_YEAR = 365.25 * 86400.0  # Julian year

# --- Earth --------------------------------------------------------------------------------------
R_EARTH_KM = 6371.0  # nuFATE earth.py (MIT), same value as their STW105 polynomial fit uses
# Depth of the detector centre under the ice surface [km]. IceCube's sensors sit at depths of
# 1450-2450 m (SPICE paper, arXiv:1301.5361, introduction), so the middle is ~1.95 km. Only matters for
# down-going directions, where it adds ~2 km of ice. Choice based on that source.
DETECTOR_DEPTH_KM = 1.95

# --- the astrophysical flux (what the sky sends) ------------------------------------------------
# IceCube HESE 7.5-year single power law, arXiv:2011.03545 (Phys. Rev. D 104, 022002):
#   dPhi_6nu/dE = PHI_ASTRO * (E / 100 TeV)^-GAMMA * 1e-18 GeV^-1 cm^-2 s^-1 sr^-1   (their eq. VI.1)
# Phi_6nu is all six species together (nu_e, nu_mu, nu_tau and their antineutrinos), assumed 1:1:1
# in flavour and equal nu / nubar. Best fit PHI_ASTRO = 6.37 +1.47 -1.62 and GAMMA = 2.87 +0.20 -0.19
# (their Fig. VI.2 and abstract; read from the arXiv PDF on 2026-10-06).
HESE_PHI_ASTRO = 6.37
HESE_PHI_ASTRO_ERR = (1.62, 1.47)  # (minus, plus)
HESE_GAMMA = 2.87
HESE_GAMMA_ERR = (0.19, 0.20)
HESE_E0_GEV = 1.0e5
HESE_FLUX_UNIT = 1.0e-18  # GeV^-1 cm^-2 s^-1 sr^-1
N_SPECIES = 6

# --- the HESE sample, for the cross-check --------------------------------------------------------
HESE_LIVETIME_DAYS = 2635  # arXiv:2011.03545, section II ("approximately 2635 days")
HESE_LIVETIME_S = 227708167.68  # exact livetime used by the release's own fit script HESE_fit.py
HESE_N_EVENTS = 102  # events in the public release HESE_data.json (doi:10.21234/4EQJ-BB17)
HESE_N_ABOVE_60TEV = 60  # of those, reconstructed deposited energy >= 60 TeV (counted from the file)
HESE_E_CUT_GEV = 6.0e4  # the analysis threshold on deposited energy, arXiv:2011.03545

# --- our counting choices -----------------------------------------------------------------------
E_THRESHOLD_GEV = 6.0e4  # count neutrinos above 60 TeV; HESE's cut is on DEPOSITED energy. Choice.
E_MAX_GEV = 1.0e7  # integrate the flux up to 10 PeV. Choice (the power law is not measured beyond).
E_MIN_PLOT_GEV = 1.0e3  # figures run from 1 TeV ...
E_MAX_PLOT_GEV = 1.0e7  # ... to 10 PeV
