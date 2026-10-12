"""Every input: the calibration (each value with its source), the shocks, the experiments and the citations.
Educational demo, not research."""
from pathlib import Path

LABEL = "Educational demos made to show an open-source tool. Not research."
PRIZE = ("Sveriges Riksbank Prize in Economic Sciences in Memory of Alfred Nobel 2026, Robert E. Hall and Michael "
         "Woodford, \"for microeconomic foundations of macroeconomic stabilisation\" (nobelprize.org press release, "
         "12 October 2026)")
COMMITTEE_QUOTE = "for microeconomic foundations of macroeconomic stabilisation"
PYTHON = "3.11"

HERE = Path(__file__).resolve().parent.parent
RESULTS = HERE / "results"
RESULTS_JSON = "set_the_rate.json"
FIGURES = ("demand_shock", "cost_push_shock", "taylor_principle", "forward_guidance")

CITATIONS = {
    "woodford_2003": "Woodford, Michael, 2003. Interest and Prices: Foundations of a Theory of Monetary Policy. "
                     "Princeton University Press.",
    "clarida_gali_gertler_1999": "Clarida, Richard, Jordi Galí and Mark Gertler, 1999. The Science of Monetary "
                                 "Policy: A New Keynesian Perspective. Journal of Economic Literature 37(4): "
                                 "1661-1707.",
    "gali_2015": "Galí, Jordi, 2015. Monetary Policy, Inflation, and the Business Cycle: An Introduction to the New "
                 "Keynesian Framework and Its Applications, second edition. Princeton University Press.",
    "blanchard_kahn_1980": "Blanchard, Olivier Jean and Charles M. Kahn, 1980. The Solution of Linear Difference "
                           "Models under Rational Expectations. Econometrica 48(5): 1305-1311.",
    "del_negro_giannoni_patterson_2023": "Del Negro, Marco, Marc P. Giannoni and Christina Patterson, 2023. The "
                                         "Forward Guidance Puzzle. Journal of Political Economy Macroeconomics 1(1): "
                                         "43-79.",
    "del_negro_giannoni_patterson_2015": "Del Negro, Marco, Marc Giannoni and Christina Patterson, 2012, revised "
                                         "2015. The Forward Guidance Puzzle. Federal Reserve Bank of New York Staff "
                                         "Reports 574 (the earlier version; published 2023).",
    "bullard_mitra_2002": "Bullard, James and Kaushik Mitra, 2002. Learning about Monetary Policy Rules. Journal of "
                          "Monetary Economics 49(6): 1105-1129.",
    "mckay_nakamura_steinsson_2016": "McKay, Alisdair, Emi Nakamura and Jón Steinsson, 2016. The Power of Forward "
                                     "Guidance Revisited. American Economic Review 106(10): 3133-3158.",
}
DOIS = {
    "clarida_gali_gertler_1999": "10.1257/jel.37.4.1661",
    "blanchard_kahn_1980": "10.2307/1912186",
    "mckay_nakamura_steinsson_2016": "10.1257/aer.20150063",
    "del_negro_giannoni_patterson_2023": "10.1086/724214",
    "bullard_mitra_2002": "10.1016/s0304-3932(02)00144-7",
}

# Calibration: quarterly, the baseline values of Galí (2015), chapter 3 (the basic New Keynesian model).
# kappa is not set directly: it follows from the deep parameters below by Galí's formula.
GALI = "Galí (2015), ch. 3, pp. 67-70 (checked against J. Pfeifer's Dynare replication Gali_2015_chapter_3.mod)"
BETA = 0.99         # discount factor                                         [GALI]
SIGMA = 1.0         # inverse of the intertemporal elasticity of substitution [GALI]
PHI_LABOUR = 5.0    # inverse Frisch elasticity of labour supply              [GALI]
ALPHA = 0.25        # 1 - labour share in the production function             [GALI]
EPSILON = 9.0       # elasticity of substitution between goods                [GALI]
THETA = 0.75        # share of firms that keep their price each quarter        [GALI] (prices last 4 quarters)
PHI_PI = 1.5        # rule: response to inflation                             [GALI] (also Taylor 1993)
PHI_Y = 0.125       # rule: response to the output gap, 0.5/4 at quarterly rates [GALI]
RHO_DEMAND = 0.5    # persistence of the natural-rate (demand) shock          [GALI] (preference shock, rho_z = 0.5)
RHO_COST_PUSH = 0.5  # persistence of the cost-push shock: our choice, set equal to RHO_DEMAND (see README)

SPENDING_LABEL = "spending shock (households less patient)"  # the JSON key stays demand_shock

# Experiments. Inflation and the policy rate are reported at annual rates (4 x the quarterly value).
ANNUAL = 4.0
SHOCK_PP = 1        # each shock moves its own variable by 1 percentage point a year on impact
HORIZON = 16        # quarters drawn
CUMULATE = 12       # cumulative sums over quarters 0..11
PHI_PI_STRONG = 3    # "a stronger inflation response" for the cost-push comparison (our choice: twice 1.5)
PHI_PI_PASSIVE = 0.8  # a rule that breaks the Taylor principle
FG_QUARTER = 8      # forward guidance: the rate is lower in quarter 8 only (today is quarter 0)
FG_CUT_PP = 1       # by 1 percentage point a year
FG_HORIZONS = 12    # today's response for announcements about quarters 0..12
TOL = 1e-10         # the three equations hold to this
T_CHECK = 400       # horizon of the stacked perfect-foresight solve used as a cross-check

FORBIDDEN = ("should", "policy works", "the right move", "no alternative")  # neutrality: never in our own voice
