"""Every number we put in, with its source, or "choice", or "fitted toy number". All dimensionless model units."""

LABEL = "Educational demo made to show an open-source tool. Toy model, not research."
NOTES = "one published toy model of several; the real mechanism is still debated (SCI pp. 14-16)"

# Soai's 2003 series, in per cent ee: a PREPARED head start of 0.00005 % ee (five parts in ten million), then three
# consecutive runs, each seeded with the previous run's product: 57 %, 99 %, >99.5 %.
# Sato, Urabe, Ishiguro, Shibata, Soai, Angew. Chem. Int. Ed. 2003, 42, 315 (S03a); Nobel SCI p. 12, Fig. 7 entries 6-8.
SOAI_2003_PCT = (0.00005, 57.0, 99.0, 99.5)  # the last value is a lower bound (">99.5")

# Layer 1 targets: Blackmond, "Autocatalytic models for the origin of biological homochirality" (arXiv:1909.13015),
# discussion of the stochastic dimer model (scheme 8, fig. 3): ee0 = 0.01 % and 10^4 turnovers -> "just over 60 %";
# ee0 = 0.5 % -> approaches homochirality. Our exact numbers: 61.8 % and 99.0 %.
L1_STATEMENTS = ((0.01, 1e4), (0.5, 1e4))  # (ee0 in %, turnovers)
K_STATISTICAL = 4.0  # random pairing (Blackmond-Brown model; the same K = 4 as Kagan's pie)

# Layer 2: fitted toy numbers, not measured constants. K and N are solved so that round 1 gives 57 % and round 2
# gives 99 % from 0.00005 %; round 3 is then a prediction to compare with ">99.5 %". Recomputed by run_all.
FIT_TARGET_ROUNDS = (57.0, 99.0)
K_SCAN = (4.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0)  # choice
K4_DEMO_TURNOVERS = (5.0, 50.0)  # choice: what K = 4 gives with modest turnovers per round

# Layer 3: Buhse, J. Mex. Chem. Soc. 2005, 49, 328 (open access, CC BY-NC), reactions [1']-[10'], Fig. 1 set, in
# model units ("arbitrarily chosen" there): k0 = 1e-6, k1 = 1, k2 = 1e5, k3 = 10, k4 = 10, k5 = 10; A = Z = 1,
# seed 0.1. Target: ee0 = 1e-5 % -> about 85 %. Printed eq. 15 has k1*AZR in dS/dt; it must be k1*AZS (typo).
BUHSE_EE0 = 1e-7  # = 1e-5 %
BUHSE_CAT0 = 0.1
BUHSE_T_END = 1e4  # choice: long enough that A is used up (A left < 1e-3)
K2_LOG10_SCAN = (1.0, 6.0, 26)  # choice: log10 of k2 from 10 to 1e6, 26 points, for the bifurcation plot
K2_EE0S = (1e-7, 1e-3)  # choice: the Fig. 1 start (1e-5 %) and a larger one (0.1 %)

# Plain copying, no non-linear effect (SCI p. 10): ee_max = 90 % gives 100 -> 90 -> 81 -> ...
EROSION_EE_MAX = 0.9
NAIVE_TOLERANCES = ((1e-8, 1e-22), (1e-10, 1e-22), (1e-10, 1e-14), (1e-12, 1e-24))  # choice: (rtol, atol) for the pitfall
ROUNDS_SHOWN = 6  # choice
