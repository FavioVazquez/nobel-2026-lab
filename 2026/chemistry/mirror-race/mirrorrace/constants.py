"""Every number the toy puts in, with where it comes from.

Educational demo made to show an open-source tool. Toy model, not research.

All rates are dimensionless model units. There is no lab chemistry in this file or anywhere in
this package: no reagents, quantities, concentrations, temperatures or conditions.

The network (Frank 1953, closed-system form of Crusats, Hochberg, Moyano and Ribo 2009):

    A           -> one hand          propensity k0 * A          (racemic background, each hand)
    A           -> mirror hand       propensity k0 * A
    A + one     -> 2 one             propensity k1 * A * one    (copying)
    A + mirror  -> 2 mirror          propensity k1 * A * mirror
    one + mirror -> P (mixed pair)   propensity k2 * one * mirror (mutual antagonism)

Rates are "per molecule" (stochastic) constants on molecule counts, as in the feasibility
prototype. Only ratios matter for which hand wins, because we skip the waiting times.
"""

# --- sources (keys follow work/nobel/chemistry/facts.md) -------------------------------------
SOURCES = {
    "F53": "F. C. Frank, 'On spontaneous asymmetric synthesis', Biochim. Biophys. Acta 11, 459-463 (1953), doi:10.1016/0006-3002(53)90082-1",
    "CHMR09": "J. Crusats, D. Hochberg, A. Moyano, J. M. Ribo, 'Frank model and spontaneous emergence of chirality in closed systems', ChemPhysChem 10, 2123-2131 (2009), doi:10.1002/cphc.200900181",
    "HZ06": "D. Hochberg, M.-P. Zorzano, 'Reaction-noise induced homochirality', Chem. Phys. Lett. 431, 185-189 (2006), doi:10.1016/j.cplett.2006.09.059, arXiv:q-bio/0701005 (Langevin noise, 2D domains)",
    "S03a": "Sato, Urabe, Ishiguro, Shibata, Soai, Angew. Chem. Int. Ed. 42, 315-317 (2003), doi:10.1002/anie.200390105 (0.00005% ee -> 57% -> 99% -> >99.5% in three runs)",
    "S03b": "Soai et al., Tetrahedron: Asymmetry 14, 185-188 (2003), doi:10.1016/s0957-4166(02)00791-7 (37 runs: 19 (S), 18 (R), ee 15-91%)",
    "SV03": "Singleton and Vo, Org. Lett. 5, 4337 (2003), doi:10.1021/ol035605p (54 runs: 27 (R), 27 (S))",
    "SCI": "Nobel Committee for Chemistry, Scientific background 2026, https://www.nobelprize.org/uploads/2026/10/advanced-chemistryprize2026.pdf (printed page numbers; p. 4: Frank model 'is not an answer to the origin of biological homochirality'; p. 13: the 37 runs; p. 14-16: mechanism still debated)",
    "POLYA": "Polya urn: after n draws from an urn that starts with weight a of each colour, the count of one colour is Beta-binomial(n, a, a); a = 1 gives every count 0..n with equal chance (e.g. N. L. Johnson and S. Kotz, Urn Models and Their Application, Wiley 1977)",
}

# --- molecule numbers --------------------------------------------------------------------------
N_MAIN = 10_000          # choice (task brief): molecules of achiral A at the start
N_SWEEP = (1_000, 10_000, 100_000)  # choice (task brief)
RUNS = 10_000            # choice (task brief): runs per condition

# --- rates (dimensionless) -----------------------------------------------------------------------
K1 = 1.0                 # choice: sets the unit; only ratios to K1 matter
K0 = 1.0                 # choice (task brief: k0 = k1). Gives Polya weight a = K0/K1 = 1: exactly flat
K0_STD_CHECK = 10.0      # choice (prototype check): a = 10, Beta(10, 10) std 0.218
K2_STRONG = 100.0        # tuned: strong antagonism, gives two spikes (k2/k1 = 100, as in the prototype)
K2_WEAK = 10.0           # tuned: ten times weaker antagonism (extra row in the summary only)
STOP_FRACTION = 0.05     # tuned: "stopped early" = the strong-antagonism runs, read after 5% of A is used up
PROGRESS_SWEEP = (0.005, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 1.0)  # choice: where we read the ee along the way
MASTER_SEED = 20261007   # choice: random seed, so every number here comes out the same on every machine

# --- seeded head start ----------------------------------------------------------------------------
SEED_DELTAS = (0, 1, 2, 3, 5, 8, 12, 20, 32, 50, 80, 128, 200, 320, 500)  # choice: head start in molecules
SEED_RUNS = 2_000        # choice: runs per (N, delta) point; binomial error <= 0.011
N_REF = 10_000           # choice: for the "fixed concentration" scaling, a = K0/K1 * N / N_REF

# --- real experiments (counts only; no conditions) -------------------------------------------------
SOAI_2003 = {"runs": 37, "one": 19, "mirror": 18, "ee_range_pct": [15, 91], "source": "S03b; SCI p. 13",
             "hands": "19 (S), 18 (R); we call (S) 'one hand' only for the panel"}
SINGLETON_VO_2003 = {"runs": 54, "one": 27, "mirror": 27, "source": "SV03; SCI p. 13", "hands": "27 (R), 27 (S)"}

LABEL = "our toy model, trend only"
DISCLAIMER = "Educational demo made to show an open-source tool. Toy model, not research."
SUBTITLE = "our toy model: simplified, trend only (dimensionless units)"
