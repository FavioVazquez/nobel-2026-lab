"""Every input: the pinned BEA files, their licence, the samples, the toy household mix and the citations.
Educational demo, not research."""
from pathlib import Path

LABEL = "Educational demos made to show an open-source tool. Not research."
PRIZE = ("Sveriges Riksbank Prize in Economic Sciences in Memory of Alfred Nobel 2026, Robert E. Hall and Michael "
         "Woodford, \"for microeconomic foundations of macroeconomic stabilisation\" (nobelprize.org press release, "
         "12 October 2026)")

HERE = Path(__file__).resolve().parent.parent
RAW = HERE / "data" / "raw"
DERIVED = HERE / "data" / "quarterly.csv"
RESULTS = HERE / "results"
RESULTS_JSON = "spending.json"
FIGURES = ("hall_test", "lambda", "control")

# BEA's bulk NIPA files (no key needed). Downloaded 12 October 2026; the server's Last-Modified is 30 September 2026,
# 12:30 GMT (8:30 a.m. in Washington), the day of BEA's releases "GDP (Third Estimate), Industries, Corporate
# Profits, State GDP, and State Personal Income, 2nd Quarter 2026; State PCE, 2025" and "Personal Income and
# Outlays, August 2026" (bea.gov release schedule). The next release replaces these files, so their sha256 pins this
# vintage; they are large (35 MB) and not committed. The three series we use are extracted, line for line, into
# small committed CSVs with their own sha256, so the numbers can be rebuilt after BEA moves on.
BULK_URL = "https://apps.bea.gov/national/Release/TXT/{name}"
DOWNLOADED = "2026-10-12"
VINTAGE = {
    "last_modified": "Wed, 30 Sep 2026 12:30:02 GMT",
    "release_date": "2026-09-30",
    "releases": ["GDP (Third Estimate), Industries, Corporate Profits, State GDP, and State Personal Income, "
                 "2nd Quarter 2026; State PCE, 2025", "Personal Income and Outlays, August 2026"],
    "schedule": "https://www.bea.gov/news/schedule/full",
}
BULK = {
    "NipaDataQ.txt": {"bytes": 35414945,
                      "sha256": "7a577c587cecc4b9e07b2edae2684ed565e7aef477a563c2a03d076f55d848b8"},
    "SeriesRegister.txt": {"bytes": 960482,
                           "sha256": "159175ff182598eaa0b99ac09724b8c0c7844276c52dab0cd946f21c5dc50f6d"},
}
BULK_DIR = RAW / "bea"  # not committed (see .gitignore)
REGISTER_EXTRACT = "series_register.csv"  # the SeriesRegister.txt rows of the series below, committed
REGISTER_EXTRACT_SHA256 = "18ff51ce56b0e1a7671bad4f313c370296d907c42804bd40aa0ab599bd4284b9"
END_QUARTER = "2026Q2"  # the last quarter in this vintage
_T113 = "Table 1.1.3. Real Gross Domestic Product, Quantity Indexes"
_T115 = "Table 1.1.5. Gross Domestic Product"
_USD = "millions of current dollars, seasonally adjusted at annual rates"
_IDX = "index, 2017 = 100, seasonally adjusted"
# role: "headline" = non-durables + services (Fisher-chained, see WHY_NDS); "robustness" = total PCE; "check" = only
# used to show that our Fisher chain reproduces BEA's own total-PCE quantity index (DPCERA)
SERIES = {
    "DNDGRA": {"title": "Nondurable goods", "metric": "Fisher Quantity Index", "units": _IDX,
               "table": _T113 + ", line 5", "role": "headline", "first": "1947Q1", "rows": 318,
               "sha256": "d16bfe90360b46ef4196457f5884a86cb64affed9aaaef7ed5e2ea3531a776e3"},
    "DSERRA": {"title": "Services", "metric": "Fisher Quantity Index", "units": _IDX,
               "table": _T113 + ", line 6", "role": "headline", "first": "1947Q1", "rows": 318,
               "sha256": "f1b2ef747fea3ca64d4c50f4c96201a05708388eb6d12b545f58ff5536b6ed80"},
    "DNDGRC": {"title": "Nondurable goods", "metric": "Current Dollars", "units": _USD,
               "table": _T115 + ", line 5", "role": "headline", "first": "1947Q1", "rows": 318,
               "sha256": "df6bc21bcb274efc3ab753312fe7e1a9c8febfe263f3e0d548be1d8a2a6e6a9f"},
    "DSERRC": {"title": "Services", "metric": "Current Dollars", "units": _USD,
               "table": _T115 + ", line 6", "role": "headline", "first": "1947Q1", "rows": 318,
               "sha256": "e8938caf82827170e0da2ada16469352fab90a2cace306a7bfd5f4635653ff80"},
    "DPCERX": {"title": "Personal consumption expenditures", "metric": "Chained Dollars",
               "units": "millions of chained 2017 dollars, seasonally adjusted at annual rates",
               "table": "Table 1.1.6. Real Gross Domestic Product, Chained Dollars, line 2", "role": "robustness",
               "first": "1947Q1", "rows": 318,
               "sha256": "9db45a59d7e8baa39cd28065355ae4bba1d9e6f63568c30ad4222a5e10504846"},
    "A067RX": {"title": "Disposable personal income", "metric": "Chained Dollars",
               "units": "millions of chained 2017 dollars, seasonally adjusted at annual rates",
               "table": "Table 2.1. Personal Income and Its Disposition, line 37", "role": "headline",
               "first": "1947Q1", "rows": 318,
               "sha256": "42c285954c1bb28464c5609f9cca7c4135cba122850004b858af9416323a36c3"},
    "B230RC": {"title": "Population (midperiod, thousands)", "metric": "Persons", "units": "thousands",
               "table": "Table 2.1. Personal Income and Its Disposition, line 40", "role": "headline",
               "first": "1947Q1", "rows": 318,
               "sha256": "5974215a2096fb97dedabe0b3b2292a98b0d3303f4c210ef6b524bfbe7f5af86"},
    "DDURRA": {"title": "Durable goods", "metric": "Fisher Quantity Index", "units": _IDX,
               "table": _T113 + ", line 4", "role": "check", "first": "1947Q1", "rows": 318,
               "sha256": "3cbe95397b7f3697df56e02790aaa42ddbd9f649b5b4094dec7302d6a8caa3f7"},
    "DDURRC": {"title": "Durable goods", "metric": "Current Dollars", "units": _USD,
               "table": _T115 + ", line 4", "role": "check", "first": "1947Q1", "rows": 318,
               "sha256": "f86345888fe2e556743ed2635aa754a50b9ffd29ae75cb389dfad317d5ca1e16"},
    "DPCERA": {"title": "Personal consumption expenditures", "metric": "Fisher Quantity Index", "units": _IDX,
               "table": _T113 + ", line 2", "role": "check", "first": "1947Q1", "rows": 318,
               "sha256": "1aa86e6671815e8dbf7fada169e4d7b2dbfa0c3c50bd533f6ea5bf04c76e04f4"},
}
CHAINED_2017_CHECK = (
    "chained dollars equal current dollars in the reference year: the 2017 average of DPCERX equals that of "
    "current-dollar PCE (DPCERC) in this vintage, 13,290,625.5 million")
# Non-durables + services: a Fisher chain of BEA's own quantity indexes, weighted by BEA's current-dollar values,
# the way BEA builds its chained aggregates. Quarter-to-quarter quantity relative: the geometric mean of a Laspeyres
# relative (last quarter's values as weights) and a Paasche relative (this quarter's values as weights).
FISHER_PARTS = {"nds": [("DNDGRA", "DNDGRC"), ("DSERRA", "DSERRC")],
                "pce_check": [("DDURRA", "DDURRC"), ("DNDGRA", "DNDGRC"), ("DSERRA", "DSERRC")]}
FISHER_FORMULA = ("relative_t = sqrt(L_t x P_t), L_t = sum_i v_i,t-1 r_i,t / sum_i v_i,t-1, P_t = sum_i v_i,t / "
                  "sum_i (v_i,t / r_i,t), with r_i,t = q_i,t / q_i,t-1 (q: BEA's quantity index, v: BEA's "
                  "current-dollar value); the level is the chained product of the relatives, scaled so that its "
                  "2017 average equals the 2017 average of current-dollar non-durables plus services (chained 2017 "
                  "dollars)")
FISHER_CHECK_TOL = 2e-4  # max |difference| in quarterly log growth allowed against DPCERA (indexes have 3 decimals)
REFERENCE_YEAR = "2017"
WHY_NDS = (
    "Hall (1978) and Campbell and Mankiw (1989) used spending on non-durable goods and services, and so do we. "
    "BEA's quarterly file has chained-dollar non-durables (DNDGRX) and services (DSERRX) only from 2007Q1, and "
    "chained-dollar components do not add up to a total; but it has BEA's Fisher quantity indexes (DNDGRA, DSERRA) "
    "and current-dollar values (DNDGRC, DSERRC) from 1947Q1, which is all a Fisher chain needs. The same formula "
    "applied to durables, non-durables and services reproduces BEA's own total-PCE quantity index (DPCERA) (see "
    "fisher_check). Total real PCE (DPCERX), which includes durable goods, is kept as a robustness check; under "
    "Hall's hypothesis spending on durables need not be a random walk (Mankiw 1982)")
WHY_POPULATION = (
    "B230RC is the population line of NIPA Table 2.1 (line 40), the one BEA itself uses for its per-capita income "
    "and spending series (Table 7.1, Selected Per Capita Product and Income Series)")
WHY_START = (
    "the regressions start in 1953Q1, the start of Campbell and Mankiw's sample (1953:1 to 1986:4); with four lags "
    "of quarterly growth they need data from 1951Q4. BEA's quarterly series, income included, start in 1947Q1")
DERIVED_SHA256 = "a0a7d2d5467436d3f277dea3a51ed5f8384dfb1a10cbeeab135781fbcbfde38e"
DERIVED_COLUMNS = ("quarter", "nds_real", "pce_real", "dpi_real", "population", "log_c_pc", "log_pce_pc",
                   "log_y_pc")

# Licence, quoted exactly (checked 12 October 2026).
BEA_URL = "https://www.bea.gov/help/faq/147"
BEA_LINE = ("Unless stated otherwise, the information posted on this web site is in the public domain and may be "
            "used or reproduced without specific permission. A citation such as \"Source: U.S. Bureau of Economic "
            "Analysis\" would be appreciated.")
BEA_FAQ_TITLE = "Are the information and data presented on the BEA web site copyright-protected?"
SOURCE_CREDIT = "Source: U.S. Bureau of Economic Analysis"

# Samples. Regressions use 4 lags of quarterly growth, so data from 1951Q4 give a first regression quarter of
# 1953Q1 (see WHY_START).
FIRST_QUARTER = "1951Q4"
SPLIT_YEAR = 1990  # first half: up to 1989Q4 (148 quarters); second half: from 1990Q1 (146)
PRE_2020_END = "2019Q4"
CM_SAMPLE_END = "1986Q4"  # the end of Campbell and Mankiw's sample (1953:1 to 1986:4)
LAGS = 4
HAC_LAGS = 4  # Newey-West (Bartlett) truncation lag, fixed for every sample
IV_LAGS = (2, 3, 4)  # instruments lagged two to four quarters (time aggregation, Campbell and Mankiw 1989 p. 190)
TIME_AGGREGATION = (
    "Quarterly figures are averages over the quarter, so even if spending followed a random walk, its change from "
    "one quarter to the next would be correlated with the previous change (Working 1960), and the first lag would "
    "predict it under Hall's hypothesis; lags two to four are not affected (Campbell and Mankiw 1989, p. 190)")
Z95 = 1.959963984540054
WEAK_F = 10  # the usual rule of thumb for a first-stage F (Staiger and Stock 1997)
# Instruments are called strong only if the effective F (Montiel Olea and Pflueger 2013, HAC) is above WEAK_F. The
# classic first-stage F assumes homoskedastic, serially uncorrelated errors; the HAC Wald F and the effective F do
# not. Montiel Olea and Pflueger's own conservative 5 % test that the worst-case bias is below 10 % uses a higher
# critical value (their Table 1, K_eff = 1, x = 10: 23.11).
MOP_CRIT_TAU10 = 23.11
STRONG_RULE = ("instruments are called strong only if the effective F (Montiel Olea and Pflueger 2013; HAC, "
               "Bartlett, 4 lags) is above 10; the classic first-stage F assumes homoskedastic, serially "
               "uncorrelated errors. Their own conservative 5 % test for a worst-case bias below 10 % needs an "
               "effective F above 23.11")
# Anderson-Rubin (1949) set for lambda: every lambda0 at which the instruments do not predict dc - lambda0 * dy
# (HAC Wald F below its 5 % critical value), searched on a grid. Robust to weak instruments.
AR_GRID = (-10.0, 20.0, 0.001)  # first, last, step
AR_LEVEL = 0.05
AR_NOTE = ("Anderson-Rubin (1949) 95 % set: the values lambda0 at which the instruments do not predict "
           "dc - lambda0 * dy (HAC Wald F below its 5 % critical value), searched on a grid of step 0.001 from -10 to "
           "20. It stays valid however weak the instruments are, but it tests lambda0 together with the model's other "
           "restrictions, so it can exclude the two-stage least squares estimate, or be empty when the model with a "
           "constant lambda is rejected at every value. Its HAC F test rejects too often in samples this size (see "
           "the control), so the HAC set is likely too narrow; the same set with the classic (homoskedastic) F is "
           "reported next to it")
P_FLOOR = 0.001  # p below this is written "p < 0.001"

# The simulated control: a mix of forward-looking (random walk) and hand-to-mouth households. Toy values.
SIM = {
    "seed": 2026,
    "lambda": 0.3,          # share of income going to hand-to-mouth households (they spend what they earn)
    "rho": 0.8,             # persistence of income growth: income growth that past income growth predicts
    "rho_weak": 0.3,        # income growth that the past barely predicts: the hard case for the test
    "growth": 0.005,        # mean quarterly growth of income and consumption (log points)
    "sd_income": 0.008,     # sd of the income growth surprise
    "surprise_share": 0.5,  # forward-looking consumption moves by this share of each income surprise ...
    "sd_news": 0.004,       # ... plus other news about the future (sd)
    "burn_in": 200,
    "reps": 1000,           # Monte Carlo replications per case
}
HIST_BINS = [round(-1.0 + 0.05 * i, 2) for i in range(61)]  # bins for the histogram of simulated lambda estimates

# Published estimates we compare with (Campbell and Mankiw 1989, Table 1, p. 192; US 1953:1-1986:4, consumption of
# non-durables and services per capita, disposable personal income per capita, 1982 dollars).
CM_TABLE1 = {
    "page": 192,
    "table": "Table 1, UNITED STATES 1953-1986",
    "sample": "1953:1 to 1986:4",
    "consumption": "non-durables and services per capita, 1982 dollars",
    "income": "disposable personal income per capita, 1982 dollars",
    "rows": {
        "1": {"instruments": "none (OLS)", "lambda": 0.316, "se": 0.040},
        "2": {"instruments": "income growth lags 2-4", "lambda": 0.417, "se": 0.235},
        "3": {"instruments": "income growth lags 2-6", "lambda": 0.506, "se": 0.176},
        "4": {"instruments": "consumption growth lags 2-4", "lambda": 0.419, "se": 0.161},
        "5": {"instruments": "consumption growth lags 2-6", "lambda": 0.523, "se": 0.131},
        "6": {"instruments": "interest-rate changes lags 2-4", "lambda": 0.698, "se": 0.235},
        "7": {"instruments": "interest-rate changes lags 2-6", "lambda": 0.584, "se": 0.137},
        "8": {"instruments": "income and consumption growth lags 2-4, c - y lagged 2", "lambda": 0.351, "se": 0.119},
        "9": {"instruments": "row 8 plus interest-rate changes lags 2-4", "lambda": 0.469, "se": 0.106},
    },
    "iv_rows": ["2", "3", "4", "5", "6", "7", "8", "9"],
    "time_aggregation_page": 190,
    "time_aggregation": ("We deal with this problem by lagging the instruments more than one period, so there is at "
                         "least a two-period time gap between the instruments and the variables in equation (1.4)."),
    "time_aggregation_serial_correlation": 0.25,  # p. 190: the change of a time-averaged random walk
    "about_half_page": 195,
    "about_half": ("When we use instruments that are jointly significant for predicting income growth at the 5% level "
                   "or better, we get estimates of \u03bb, the fraction of the population that consumes its current "
                   "income, of about 0.5."),
    # The PDF's text layer renders the Greek lambda as "A"; the printed page has the symbol.
    "about_half_note": "the symbol is lambda (\u03bb) on the printed page; the PDF's text layer renders it as \"A\"",
    "conclusion_page": 208,
    "conclusion": "We have estimated that each group of consumers receives about 50 percent of income",
}

# Hall (1978) worked in levels, not growth rates (checked on the JSTOR scan, printed pp. 979 and 982).
HALL_1978 = {
    "consumption_page": 979,
    "consumption": "consumption of nondurables and services in 1972 dollars from the U.S. National Income and "
                   "Product Accounts divided by the population",
    "sample": "1948-1977, quarterly",
    "income_test_page": 982,
    "income_test": "Table 3, equation 3.2: consumption per person on its first lag and four lags of real disposable "
                   "income per person, in levels",
    "income_test_F": 2.0,
    "income_test_crit_5pct": 2.4,
    "income_test_quote": ("The F-statistic for the joint predictive value of all four lagged income variables is "
                          "2.0, somewhat less than the critical value of 2.4 at the 5 percent level."),
    "ours": "the growth-rate version: the change in log consumption per person on lags of its own growth and of "
            "income growth",
}

# The committee's words (popular information, nobelprize.org, 12 October 2026), quoted only as the committee's.
COMMITTEE = {
    "source": "The Royal Swedish Academy of Sciences, popular information on the 2026 prize in economic sciences",
    "hall": "Hall's hypothesis was that changes in consumption could not be predicted because they depend on new "
            "\u2013 and thus unpredictable \u2013 information.",
    "hall_mishkin": "They used microdata for a number of individual households, showing that around 80 per cent of "
                    "them made their consumption decisions in line with the theory, while the rest lived "
                    "hand-to-mouth.",
    # The scientific background (advanced information, 12 October 2026), PDF p. 25 (printed p. 23); the sample is on
    # PDF p. 24: food consumption of 2,309 families in the Panel Study of Income Dynamics, 1969-1975.
    "sb_source": "Scientific background on the 2026 prize in economic sciences, PDF p. 25 (printed p. 23)",
    "sb_hall_mishkin": "allow a fraction of consumption to move hand in hand with current income and estimate this "
                       "hand-to-mouth fraction in the panel data to be 20% (whereas the other 80% follow the "
                       "prediction of the rational-expectations, permanent-income hypothesis)",
    "sb_hall_mishkin_pct": 20,
    "sb_hall_mishkin_sample": "food consumption, 2,309 US families (Panel Study of Income Dynamics), 1969-1975",
}

CITATIONS = {
    "hall_1978": "Hall, Robert E., 1978. Stochastic Implications of the Life Cycle-Permanent Income Hypothesis: "
                 "Theory and Evidence. Journal of Political Economy 86(6): 971-987.",
    "campbell_mankiw_1989": "Campbell, John Y. and N. Gregory Mankiw, 1989. Consumption, Income, and Interest Rates: "
                            "Reinterpreting the Time Series Evidence. NBER Macroeconomics Annual 1989, Volume 4, "
                            "edited by Olivier Jean Blanchard and Stanley Fischer, MIT Press: 185-246.",
    "hall_mishkin_1982": "Hall, Robert E. and Frederic S. Mishkin, 1982. The Sensitivity of Consumption to "
                         "Transitory Income: Estimates from Panel Data on Households. Econometrica 50(2): 461-481.",
    "mankiw_1982": "Mankiw, N. Gregory, 1982. Hall's Consumption Hypothesis and Durable Goods. Journal of Monetary "
                   "Economics 10(3): 417-425.",
    "staiger_stock_1997": "Staiger, Douglas and James H. Stock, 1997. Instrumental Variables Regression with Weak "
                          "Instruments. Econometrica 65(3): 557-586.",
    "anderson_rubin_1949": "Anderson, T. W. and Herman Rubin, 1949. Estimation of the Parameters of a Single "
                           "Equation in a Complete System of Stochastic Equations. Annals of Mathematical Statistics "
                           "20(1): 46-63.",
    "working_1960": "Working, Holbrook, 1960. Note on the Correlation of First Differences of Averages in a Random "
                    "Chain. Econometrica 28(4): 916-918.",
    "newey_west_1987": "Newey, Whitney K. and Kenneth D. West, 1987. A Simple, Positive Semi-Definite, "
                       "Heteroskedasticity and Autocorrelation Consistent Covariance Matrix. Econometrica 55(3): "
                       "703-708.",
    "montiel_olea_pflueger_2013": "Montiel Olea, Jos\u00e9 Luis and Carolin Pflueger, 2013. A Robust Test for Weak "
                                  "Instruments. Journal of Business & Economic Statistics 31(3): 358-369.",
}
CHECKED_AGAINST = ("statsmodels 0.14.4 and SciPy 1.15.2, to 1e-8 (tests/statsmodels_reference.json); neither is a "
                   "dependency")
CM_URL = "https://www.nber.org/chapters/c10965"
