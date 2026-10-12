# Can you predict spending? (Economics 2026, toy B)

> **Educational demos made to show an open-source tool. Not research.**
> US aggregate data, one country, 1953 to 2026, plus a simulated control. No forecast. The numbers below come from
> `results/spending.json`, and a test checks that every number in this README appears in the JSON.

The 2026 prize in economic sciences went to Robert E. Hall and Michael Woodford, "for microeconomic foundations of
macroeconomic stabilisation" (press release, 12 October 2026). In the committee's popular information: "Hall's
hypothesis was that changes in consumption could not be predicted because they depend on new – and thus
unpredictable – information."

This folder runs that test on open US data from the U.S. Bureau of Economic Analysis (BEA). If households spend
according to what they expect to earn over their lives, the change in their spending from one quarter to the next
moves only on news, so nothing known in advance predicts it (Hall 1978). Campbell and Mankiw (1989) turned the gap
into a number: lambda, the share of income that goes to households who spend what they earn as they earn it
("hand-to-mouth"). A simulated control, with a share we choose, shows what the tests can and cannot see.

Spending here is what Hall and Campbell-Mankiw used: real spending per person on non-durable goods and services,
built from BEA's own quantity indexes (see "Data"). Total spending, durables included, is kept as a robustness
check next to every headline number.

Own code, MIT licence. CPU only; runs in under a minute. Python with NumPy and Matplotlib. The regressions are
written in NumPy and match statsmodels 0.14.4 to 1e-8 (stored results in `tests/statsmodels_reference.json`).

## What it does not show

* **Aggregate data, not households.** Every number is about the US total divided by the population. A share of
  income is not a share of households, and an aggregate can hide households who behave very differently. The
  committee's microdata reference is Hall and Mishkin (1982); in the committee's scientific background (PDF p. 25,
  printed p. 23), they "allow a fraction of consumption to move hand in hand with current income and estimate this
  hand-to-mouth fraction in the panel data to be 20% (whereas the other 80% follow the prediction of the
  rational-expectations, permanent-income hypothesis)". Their sample: food consumption, 2,309 US families (Panel
  Study of Income Dynamics), 1969-1975. We do not reproduce that study.
* **Durables are out of the headline, and the series is our own chain.** Buying a car is spending in the quarter it
  is bought, not the flow of use it gives over years, and under Hall's hypothesis spending on durables need not be
  a random walk (Mankiw 1982), so the headline uses non-durables and services, as Hall and Campbell-Mankiw did. BEA
  does not publish that aggregate before 2007; we chain it from BEA's components with BEA's formula (see "Data"),
  so it can differ slightly from one BEA would build. Total spending (durables in) is the robustness row.
* **Measurement error.** These are estimates that BEA revises, and spending and income are measured separately with
  their own errors. Errors in levels make measured growth more jagged and can make it look predictable (or less)
  when the true path is not.
* **Time aggregation.** Quarterly figures are averages over the quarter, so even if spending followed a random
  walk, its change from one quarter to the next would be correlated with the previous change (Working 1960), and
  the first lag would predict it under Hall's hypothesis. The headline therefore uses lags 2-4 only, as Campbell and
  Mankiw do: "We deal with this problem by lagging the instruments more than one period, so there is at least a
  two-period time gap between the instruments and the variables in equation (1.4)." (p. 190). Lags 1-4 are shown as
  a secondary result.
* **Weak instruments.** Lambda is estimated with instruments that predict income growth only weakly in these data:
  in every sample that ends before 2020 the effective first-stage F (Montiel Olea and Pflueger 2013) is below 10,
  and so are the classic and the HAC F. With 2020-2026 in, the classic F rises above 10 but the effective F, which
  allows for unequal and correlated errors, stays below Montiel Olea and Pflueger's own threshold (section 2).
  So the intervals are wide and the usual ones can be misleading. We add weak-instrument-robust (Anderson-Rubin)
  sets; they have their own limits (sections 2 and 3).
* **No causal claim.** The regressions say what predicts what in this sample. They do not say why households spend
  as they do, why any quarter moved as it did, and they say nothing about what any policy does or would do.
* **One country, one data vintage, chosen samples.** BEA's release of 2026-09-30, downloaded on 2026-10-12. The
  years 2020-2021 move the answers a lot, so the headline sample ends in 2019Q4 and the full sample is shown next to
  it; the start (1953Q1, Campbell and Mankiw's) and the split year (1990, two halves of equal length) are our
  choices.

## How to run

From `2026/economics/can-you-predict-spending/`:

```bash
python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python -m spend.fetch_data  # checks the committed BEA extracts' sha256 and rebuilds data/quarterly.csv
                            # (--refresh downloads BEA's bulk files again; it stops if BEA has published a newer release)
python -m spend.run_all     # results/spending.json + figures (light and dark, PNG and SVG)
python -m pytest -q tests
```

## What it shows

### 1. Hall's test: can the past predict next quarter?

We regress the quarterly growth of log real spending per person on non-durables and services on lagged growth of
spending and income per person, with Newey-West (HAC, 4 lags) standard errors, and test the lags jointly (F test).
Hall's benchmark for forward-looking households is an R² of zero. The headline uses lags 2-4 (see "Time
aggregation"); lags 1-4 are shown too.

This is the growth-rate version of Hall's test. Hall (1978) worked in levels: "consumption of nondurables and
services in 1972 dollars from the U.S. National Income and Product Accounts divided by the population" (p. 979),
quarterly, 1948-1977, regressed on its own first lag and four lags of real disposable income per person (Table 3,
equation 3.2, p. 982): "The F-statistic for the joint predictive value of all four lagged income variables is 2.0,
somewhat less than the critical value of 2.4 at the 5 percent level."

| sample | quarters | n | R², lags 2-4 | adjusted | p, lags 2-4 | R², lags 1-4 | p, all 8 lags | p, the 4 income lags |
|---|---|---|---|---|---|---|---|---|
| without 2020-2026 | 1953Q1-2019Q4 | 268 | **11.5 %** | 9.4 % | 2.68e-05 | 22.0 % | 1.61e-14 | 0.297 |
| full | 1953Q1-2026Q2 | 294 | 2.9 % | 0.9 % | 0.00239 | 11.9 % | 4.45e-08 | 0.0106 |
| first half | 1953Q1-1989Q4 | 148 | 4.8 % | 0.7 % | 0.0727 | 15.8 % | 9.78e-08 | 0.42 |
| second half | 1990Q1-2026Q2 | 146 | 2.9 % | -1.3 % | 0.0218 | 14.0 % | 0.0198 | 0.0336 |
| robustness: total PCE, without 2020-2026 | 1953Q1-2019Q4 | 268 | 10.2 % | 8.1 % | 0.00198 | 19.7 % | 8.33e-13 | 0.00883 |
| robustness: total PCE, full | 1953Q1-2026Q2 | 294 | 3.5 % | 1.5 % | 0.00388 | 16.4 % | 3.62e-13 | 0.0112 |

**In plain words:** using spending and income growth from two to four quarters back, a regression explains 11.5 %
of the quarter-to-quarter changes in US spending per person on non-durables and services from 1953Q1 to 2019Q4
(in-sample; 9.4 % adjusted for the number of lags; p < 0.001), and 2.9 % from 1953Q1 to 2026Q2 (p = 0.00239). With
the most recent quarter added (lags 1-4) the shares are 22.0 % and 11.9 %, but part of that comes from averaging
within quarters, not from behaviour. For scale: in the simulated control, where spending is a random walk, the
median in-sample R² with lags 2-4 is 1.9 %.

In the lags 1-4 regression up to 2019Q4, the four income lags together do not pass a 5 % test (p = 0.297), as
Hall found in levels; with total PCE, durables included, they do (p = 0.00883). In the first half on its own,
1953Q1-1989Q4, lags 2-4 do not pass a 5 % test (p = 0.0727).

The 2020-2021 quarters are left out of the headline because in them spending and income per person moved by many
times their usual quarterly change, often in opposite directions: in 2020Q2 spending per person on non-durables and
services changed by -10.2 log points (-9.7 per cent) while income per person rose 9.4 (9.9 per cent); in 2021Q1
income rose 11.6 log points (12.3 per cent) and spending 1.7. From 1952Q1 to 2019Q4 the standard deviation of quarterly
growth was 0.47 for spending and 0.86 for income. A few such quarters dominate a fit, and through the lags they also
reach into the quarters after them, so the headline sample stops at 2019Q4.

Out of sample, predicting each quarter from 1990Q1 on with only the quarters before it, lags 2-4 give an R² of
23.7 % up to 2019Q4 and -17.0 % with 2020-2026 included (worse than the past average, because no regression fitted
on earlier years foresaw the 2020 quarters); with lags 1-4, 32.7 % and -116.0 %. The benchmark is the average of
all earlier quarters; average growth was lower after 1990 (0.35 log points per quarter to 2019) than before (0.55),
so that benchmark lags behind and the out-of-sample R² can exceed the in-sample one.

Figures: `results/hall_test_{light,dark}.{png,svg}`.

### 2. Campbell and Mankiw's lambda: what share of income goes to households who spend as they earn?

The model mixes two groups: forward-looking households, whose spending changes only on news, and hand-to-mouth
households, who receive a share lambda of income and spend it. Then consumption growth = constant + lambda x income
growth + news, and lambda is estimated by instrumental variables, with instruments that are known in advance:
income growth, consumption growth, or both, lagged 2-4 quarters (and, for their row 8, also the log ratio of
consumption to income lagged two quarters). Weak instruments can bias the estimate towards OLS and make the usual
95 % interval too narrow.

**How we judge instrument strength.** We report three first-stage F statistics: the classic one (it assumes
homoskedastic, serially uncorrelated errors; Staiger and Stock's rule of thumb is 10), the HAC Wald F, and the
effective F of Montiel Olea and Pflueger (2013), which is built for errors that are neither. We call instruments
strong only if the effective F is above 10. Montiel Olea and Pflueger's own conservative 5 % test that the
worst-case bias is below 10 % needs more: an effective F above 23.11.

**The published benchmarks.** Campbell and Mankiw (1989), Table 1, p. 192, US 1953:1 to 1986:4, non-durables and
services per capita, 1982 dollars: the instrumental-variables estimates in rows 2-9 range from 0.351 (row 8) to
0.698 (row 6); OLS gives 0.316 (row 1). On p. 195: "When we use instruments that are jointly significant for
predicting income growth at the 5% level or better, we get estimates of λ, the fraction of the population that
consumes its current income, of about 0.5." (The symbol is λ on the page; the PDF's text layer renders it as a
Latin letter.) Their conclusion (p. 208): "We have estimated that each group of consumers receives about 50 percent
of income". The committee's household-data figure is Hall and Mishkin's 20 % of consumption, in their food sample
(quoted above).

**Ours.** Non-durables and services; 95 % intervals from HAC standard errors (2SLS); Anderson-Rubin (AR) 95 % sets:
every value of lambda at which the instruments do not predict consumption growth minus lambda x income growth (Wald
F below its 5 % critical value, searched from -10 to 20 in steps of 0.001), with the HAC covariance and, next to it,
the classic one. The AR set stays valid however weak the instruments are, but it tests each value together with the
model's other restrictions, so it can leave out the 2SLS estimate, or be empty when the model with one constant
lambda is rejected at every value; and its HAC version rejects too often in samples this size (section 3).

| our sample | instruments, lags 2-4 | lambda (2SLS) | 95 % interval | F: classic / HAC / effective | AR set, HAC | AR set, classic |
|---|---|---|---|---|---|---|
| 1953Q1-2019Q4 | both | 0.509 | 0.279 to 0.739 | 3.95 / 5.01 / 4.86 | 0.558 to 1.031 | 0.426 to 1.248 |
| 1953Q1-2019Q4 | consumption growth | 0.734 | 0.439 to 1.028 | 4.89 / 6.69 / 5.34 | 0.477 to 1.389 | 0.45 to 2.206 |
| 1953Q1-2019Q4 | income growth | 0.438 | 0.072 to 0.804 | 2.81 / 3.52 / 4.16 | 0.056 to 2.782 | 0.094 to 6.521 |
| 1953Q1-1986Q4 (their window) | both | 0.298 | 0.06 to 0.536 | 2.11 / 3.13 / 2.89 | 0.033 to 0.985 | every value |
| 1953Q1-1986Q4 | both, plus log(c / y) (their row 8) | 0.275 | 0.01 to 0.539 | 1.86 / 2.94 / 2.27 | 0.033 to 0.626 | every value |
| 1953Q1-1986Q4 | consumption growth (their row 4) | 0.446 | 0.138 to 0.754 | 2.23 / 3.38 / 2.64 | 0.382 to 0.819 | every value |
| 1953Q1-1986Q4 | income growth (their row 2) | 0.607 | 0.15 to 1.064 | 0.89 / 1.83 / 1.68 | every value | every value |
| 1953Q1-2026Q2 (full) | both | -0.052 | -0.156 to 0.052 | 23.28 / 12.82 / 14.31 | empty | -0.184 to 0.114 |
| 1953Q1-1989Q4 (first half) | both | 0.25 | 0.015 to 0.485 | 2.47 / 3.64 / 3.43 | -0.076 to 0.732 | -1.438 to 0.794 |
| 1990Q1-2026Q2 (second half) | both | -0.057 | -0.168 to 0.053 | 21.14 / 113.84 / 23.79 | empty | -0.264 to 0.259 |
| robustness: total PCE, 1953Q1-2019Q4 | both | 0.66 | 0.318 to 1.003 | 3.45 / 4.07 / 3.59 | 0.966 to 1.261 | 0.742 to 1.697 |
| robustness: total PCE, 1953Q1-2026Q2 | both | -0.011 | -0.141 to 0.119 | 18.11 / 6.29 / 6.68 | empty | -0.131 to 0.145 |

**In plain words:** on these data lambda is very uncertain. Up to 2019Q4, with both sets of lags, the 95 % interval
runs from 0.279 to 0.739, and the effective F is 4.86 (classic 3.95, HAC 5.01): weak instruments. The HAC AR set,
0.558 to 1.031, does not contain the 2SLS estimate, and its top lies above 1, which a share cannot be; the classic
AR set is wider, 0.426 to 1.248. With instruments this weak the methods need not agree.

In Campbell and Mankiw's own window and with their instruments, today's data come close to two of their rows: 0.446
with consumption growth (their row 4: 0.419) and 0.275 with both plus log(c / y) (row 8: 0.351); with income growth
alone we get 0.607 (row 2: 0.417), where the effective F is 1.68 and the AR sets rule out no value at all. On
today's data these instruments are weak in that window: every effective F there is between 1.68 and 2.89, and
every classic AR set takes in every value. Their data are the 1989 vintage in 1982 dollars, ours BEA's 2026
vintage.

**With 2020-2026 in**, the 2SLS estimate is about zero (-0.052, interval -0.156 to 0.052). The classic first-stage
F is 23.28, but the HAC F is 12.82 and the effective F 14.31: above the rule of thumb of 10, below Montiel Olea and
Pflueger's 23.11, and 4.86 without these years, so the extra strength comes from the quarters of 2020-2026. We do
not call these instruments strong. The HAC AR set is empty, but this test rejects too often here (section 3); the
classic AR set is -0.184 to 0.114. In the two-group model the hand-to-mouth group's spending rises with its income, so
quarters in which spending falls while income rises pull lambda towards zero or below. The one sample whose
instruments pass the 23.11 test, 1990Q1-2026Q2 (effective F 23.79), also contains those quarters.

On total PCE (durables in) the pre-2020 estimate is 0.66 (interval 0.318 to 1.003, effective F 3.59), and its HAC AR
set, 0.966 to 1.261, lies almost entirely above 1.

Figures: `results/lambda_{light,dark}.{png,svg}` (theirs and ours, with 95 % intervals, HAC AR sets, effective F and
the range of their Table 1).

### 3. A control with a known answer

Simulated households, the same 294 regression quarters: forward-looking households, whose consumption is a random
walk (each quarter it moves by half of the income surprise plus other news), and hand-to-mouth households with a
share of 0.3 of income. Income growth has persistence 0.8 (past income predicts income) or 0.3 (it barely does).
1000 runs per case, seed 2026 (the simulated quarters are points in time, so there is no time aggregation here):

| case | true share | persistence | Hall's test rejects (5 % level) | median lambda | 95 % interval holds the truth | AR set (HAC) holds the truth | median first-stage F, classic / effective |
|---|---|---|---|---|---|---|---|
| hand-to-mouth mix | 0.3 | 0.8 | 100.0 % | 0.303 | 94.7 % | 90.3 % | 31.8 / 31.1 |
| random walk only | 0 | 0.8 | 12.3 % | 0.004 | 94.9 % | 90.1 % | 32.4 / 31.2 |
| hand-to-mouth mix, weak | 0.3 | 0.3 | 37.4 % | 0.526 | 57.5 % | 91.8 % | 1.2 / 1.3 |
| random walk only, weak | 0 | 0.3 | 15.1 % | 0.325 | 55.1 % | 88.9 % | 1.2 / 1.3 |

One run of the first case gives lambda 0.326 with interval 0.28 to 0.372: the test recovers the share we put in.
OLS on the same run gives 0.431, because each income surprise moves both groups' spending. What the tests cannot
do: with income that the past barely predicts, the 2SLS interval misses the truth about half the time and finds a
share of 0.325 in a world with no hand-to-mouth households at all. The HAC AR set holds the truth about as often
with weak instruments as with strong ones (88.9 to 91.8 %), but less than its nominal 95 %: its HAC F test
over-rejects in samples this size, as Hall's HAC F test does, which rejects a true random walk 12.3 % of the time
at a nominal 5 %. So the HAC AR sets in section 2 are likely somewhat too narrow (hence the classic ones next to
them), and a p-value just under 0.05 means little here. The US data sit in the weak rows before 2020 (effective F
4.86).

Figures: `results/control_{light,dark}.{png,svg}`.

## Guess first

Answers in `results/spending.json` under `guess`.

* **"From the last year of data, how much of next quarter's change in US consumer spending can be predicted?
  (0-100 %)"** Read as: spending and income growth two to four quarters back, in-sample R², spending on non-durables
  and services. Answer: **11.5 %** (1953Q1-2019Q4; p = 2.68e-05); 2.9 % on the full sample, 1953Q1-2026Q2. Hall's
  benchmark: 0. With lags 1-4, 22.0 % and 11.9 %, partly from averaging within quarters (Working 1960). Total PCE
  (durables in): 10.2 %. Why 2020-2021 are left out: see section 1.
* **"What share of income goes to households who spend as they earn?"** The published benchmarks: Campbell and
  Mankiw (1989), "about 50 percent" (p. 208), their Table 1 estimates ranging from 0.351 to 0.698 (p. 192, US
  1953:1 to 1986:4); Hall and Mishkin (1982), as the committee states it, a hand-to-mouth fraction of consumption of
  20% (food consumption, 2,309 US families, 1969-1975). On our data (1953Q1-2019Q4): **very uncertain on these
  data: 95 % interval 27.9 to 73.9 %, effective F 4.86** (classic 3.95, HAC 5.01; below 10: weak instruments);
  Anderson-Rubin set 55.8 to 103.1 % (HAC; values above 100 % are impossible for a share) or 42.6 to 124.8 %
  (classic), neither containing the 2SLS estimate. With 2020-2026 included: interval -15.6 to 5.2 %, effective F
  14.31 (classic 23.28), below the 23.11 of Montiel Olea and Pflueger's test, HAC AR set empty, classic -18.4 to
  11.4 %. Total PCE, 1953Q1-2019Q4: interval 31.8 to 100.3 %, effective F 3.59.

## Data

Quarterly series from BEA's National Income and Product Accounts (NIPA), read from BEA's own bulk files
(<https://apps.bea.gov/national/Release/TXT/>; no key needed): `NipaDataQ.txt` (all quarterly NIPA series) and
`SeriesRegister.txt` (what each series code is). All start in 1947Q1 and end in 2026Q2 (318 quarters).

| BEA code | what (BEA's label) | units | NIPA table | used for |
|---|---|---|---|---|
| DNDGRA | Nondurable goods, Fisher Quantity Index | index, 2017 = 100 | Table 1.1.3, line 5 | headline |
| DSERRA | Services, Fisher Quantity Index | index, 2017 = 100 | Table 1.1.3, line 6 | headline |
| DNDGRC | Nondurable goods, Current Dollars | millions of current dollars, seasonally adjusted at annual rates | Table 1.1.5, line 5 | headline |
| DSERRC | Services, Current Dollars | millions of current dollars, seasonally adjusted at annual rates | Table 1.1.5, line 6 | headline |
| A067RX | Disposable personal income, Chained Dollars | millions of chained 2017 dollars, seasonally adjusted at annual rates | Table 2.1, line 37 | headline |
| B230RC | Population (midperiod, thousands) | thousands | Table 2.1, line 40 | headline |
| DPCERX | Personal consumption expenditures, Chained Dollars | millions of chained 2017 dollars, seasonally adjusted at annual rates | Table 1.1.6, line 2 | robustness |
| DDURRA, DDURRC | Durable goods, quantity index and current dollars | as above | Table 1.1.3 / 1.1.5, line 4 | check |
| DPCERA | Personal consumption expenditures, Fisher Quantity Index | index, 2017 = 100 | Table 1.1.3, line 2 | check |

* **Non-durables + services.** BEA's quarterly file has chained-dollar non-durables (DNDGRX) and services (DSERRX)
  only from 2007Q1, and chained-dollar components do not add up to a total. But it has BEA's Fisher quantity
  indexes (DNDGRA, DSERRA) and current-dollar values (DNDGRC, DSERRC) from 1947Q1, which is all a Fisher chain
  needs. Each quarter's quantity relative is the geometric mean of a Laspeyres relative (last quarter's
  current-dollar values as weights) and a Paasche relative (this quarter's values as weights); the level is the
  chained product, scaled so that its 2017 average equals the 2017 average of current-dollar non-durables plus
  services (chained 2017 dollars, as BEA does). **Check:** the same formula on durables, non-durables and services
  reproduces BEA's own total-PCE quantity index (DPCERA) to 0.000182 in quarterly log growth at most (1955Q1), over
  317 quarters; the published indexes have three decimals (`tests/test_spend.py`).
* **Vintage.** Downloaded on 2026-10-12. The server's Last-Modified is Wed, 30 Sep 2026 12:30:02 GMT, the day of
  BEA's releases "GDP (Third Estimate), Industries, Corporate Profits, State GDP, and State Personal Income, 2nd
  Quarter 2026; State PCE, 2025" and "Personal Income and Outlays, August 2026" (BEA's release schedule). The two
  bulk files (`NipaDataQ.txt`, 35414945 bytes; `SeriesRegister.txt`, 960482 bytes) are pinned by sha256 in
  `spend/constants.py` and the JSON. BEA replaces them at every release, so they are not committed; the lines of
  the ten series are extracted unchanged (LF line endings) into `data/raw/<code>.csv`, and their register rows into
  `data/raw/series_register.csv`, each committed with its own sha256. `fetch_data` refuses files whose sha256
  differs.
* **Chained 2017 dollars.** In this vintage the 2017 average of DPCERX equals that of current-dollar PCE (DPCERC),
  13,290,625.5 million, as chained dollars do in their reference year.
* **Start.** The derived file `data/quarterly.csv` has 299 quarters, 1951Q4 to 2026Q2, so that with four lags of
  quarterly growth the regressions start in 1953Q1, the start of Campbell and Mankiw's sample (1953:1 to 1986:4).
* **Population:** B230RC is the population line of NIPA Table 2.1 (line 40), the one BEA itself uses for its
  per-capita income and spending series (Table 7.1, Selected Per Capita Product and Income Series).

**Licence.** BEA (<https://www.bea.gov/help/faq/147>, "Are the information and data presented on the BEA web site
copyright-protected?"):

> Unless stated otherwise, the information posted on this web site is in the public domain and may be used or reproduced without specific permission. A citation such as "Source: U.S. Bureau of Economic Analysis" would be appreciated.

Credit: Source: U.S. Bureau of Economic Analysis.

## Files

| file | in plain words |
|---|---|
| `spend/constants.py` | BEA file names, vintage, sha256, licence line, samples, the toy household mix, published values, citations |
| `spend/fetch_data.py` | checks the extracts (or downloads BEA's bulk files and extracts again), builds the Fisher chain, writes `data/quarterly.csv` |
| `spend/model.py` | OLS with HAC errors, F tests, two-stage least squares, the effective F, the Anderson-Rubin sets, Hall's test, lambda, the simulation (NumPy only) |
| `spend/figures.py`, `spend/run_all.py` | the figures (light and dark, PNG and SVG) and the summary JSON |
| `data/raw/<code>.csv` | the ten series' lines from BEA's `NipaDataQ.txt` |
| `data/raw/series_register.csv` | their rows from BEA's `SeriesRegister.txt` |
| `data/quarterly.csv` | derived: quarter, real non-durables + services, real PCE, real disposable income (billions), population (thousands), logs per person |
| `results/spending.json` | every number in this README |
| `INSIGHTS.md` | sentences a narrator could say, each traced to a JSON field |
| `tests/` | sha256, series lengths and dates, the Fisher check, statsmodels match, the control, README, INSIGHTS and figure conventions |
| `tests/make_statsmodels_reference.py` | rebuilds the stored statsmodels results (needs statsmodels 0.14.4 and pandas below 3; not a dependency) |

## Citations

* Hall, Robert E., 1978. Stochastic Implications of the Life Cycle-Permanent Income Hypothesis: Theory and
  Evidence. Journal of Political Economy 86(6): 971-987.
* Campbell, John Y. and N. Gregory Mankiw, 1989. Consumption, Income, and Interest Rates: Reinterpreting the Time
  Series Evidence. NBER Macroeconomics Annual 1989, Volume 4, edited by Olivier Jean Blanchard and Stanley Fischer,
  MIT Press: 185-246. <https://www.nber.org/chapters/c10965>
* Hall, Robert E. and Frederic S. Mishkin, 1982. The Sensitivity of Consumption to Transitory Income: Estimates from
  Panel Data on Households. Econometrica 50(2): 461-481. (The committee's microdata reference; not reproduced here.)
* Anderson, T. W. and Herman Rubin, 1949. Estimation of the Parameters of a Single Equation in a Complete System of
  Stochastic Equations. Annals of Mathematical Statistics 20(1): 46-63.
* Mankiw, N. Gregory, 1982. Hall's Consumption Hypothesis and Durable Goods. Journal of Monetary Economics 10(3):
  417-425.
* Montiel Olea, José Luis and Carolin Pflueger, 2013. A Robust Test for Weak Instruments. Journal of Business &
  Economic Statistics 31(3): 358-369.
* Newey, Whitney K. and Kenneth D. West, 1987. A Simple, Positive Semi-Definite, Heteroskedasticity and
  Autocorrelation Consistent Covariance Matrix. Econometrica 55(3): 703-708.
* Staiger, Douglas and James H. Stock, 1997. Instrumental Variables Regression with Weak Instruments. Econometrica
  65(3): 557-586.
* Working, Holbrook, 1960. Note on the Correlation of First Differences of Averages in a Random Chain.
  Econometrica 28(4): 916-918.
