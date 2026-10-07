"""Every number we put in, with its source or the word "choice". All dimensionless."""

LABEL = "Educational demo made to show an open-source tool. Toy model, not research."

# Statistical binding: two ligands drawn at random, mixed pair twice as likely as each same-hand pair -> K = 2^2 = 4.
# The Nobel popular information (POP, figure 4) uses this split: 75:25 ligand -> 56/38/6 complexes.
K_STATISTICAL = 4.0

# POP figure 4: 75 % one hand, 25 % mirror hand of the ligand (ee_L = 50 %).
PIE_LIGAND_ONE_HAND_PCT = 75.0
# POP figure 4 targets (rounded there to 56/38/6; exact values 56.25/37.5/6.25 follow from K = 4).
PIE_CATALYSTS_PCT = (56.25, 37.5, 6.25)  # one-hand pair, mixed pair, mirror-hand pair
PIE_EFFECTIVE = (90.0, 10.0)
PIE_EE_PROD_PCT = 80.0

# Curve family on the figure and in the summary. Choice: g = 0 (mixed pair inactive, the reservoir case), 0.1, 0.5
# (bulge: positive NLE), 1 (straight line), 2 and 10 (sag: negative NLE).
G_VALUES = (0.0, 0.1, 0.5, 1.0, 2.0, 10.0)
CURVE_N_POINTS = 51  # choice: ee_L = 0, 0.02, ..., 1
EE_MAX = 1.0  # choice: product ee with a one-hand-only ligand; the curves scale linearly with it

# SCI p. 10: a self-copying catalyst whose pure form gives 90 % ee erodes 100 -> 90 -> 81 -> ...
EROSION_EE_MAX = 0.9
EROSION_ROUNDS = 6  # choice
