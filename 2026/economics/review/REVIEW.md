# Economics 2026: independent review of the toys

> **Educational demos made to show an open-source tool. Not research.**

Reviewed on 12 October 2026 by sessions that did not build the toys. Round 1 covers `set-the-rate`; round 2 covers
`can-you-predict-spending`.

| toy | branch, commit reviewed | verdict |
|---|---|---|
| set-the-rate | `econ-rate`, `b239023` | **FIX FIRST**: every number checks (85 of 85 JSON fields, solution to 4e-16); the fixes are text and citations |
| can-you-predict-spending | `econ-spend`, `3a3d5aa` | **FIX FIRST**: every number checks (167 of 167 JSON fields with statsmodels/linearmodels, unrounded to 2e-8); the fixes are one data claim, the weak-instrument diagnostic for the samples with 2020-2026, a misquote and a broken sentence |

Files here: `set_the_rate_crosscheck.py` (my independent solution, written from the three equations, sharing no
code with the toy) and `set_the_rate_crosscheck.json` (its output). To rerun: check out `econ-rate` somewhere, then
`python set_the_rate_crosscheck.py <that checkout>/2026/economics/set-the-rate out.json` (Python 3.11, NumPy,
SciPy).

`can_you_predict_spending_crosscheck.py` and `can_you_predict_spending_crosscheck.json`: round 2's independent
re-run (reads BEA's bulk file itself, statsmodels / linearmodels / SciPy, no code shared with the toy; the toy is
imported only at the end for the unrounded comparison). To rerun: check out `econ-spend`, run its
`python -m spend.fetch_data --refresh` (puts the pinned bulk file in `data/raw/bea/`), then
`python can_you_predict_spending_crosscheck.py <checkout>/2026/economics/can-you-predict-spending out.json` in a
venv with numpy 1.26.4, scipy 1.15.2, pandas 2.2.3, statsmodels 0.14.4, linearmodels 7.0 (about 2.5 minutes).

---

## set-the-rate

**Verdict: FIX FIRST.** The model, the solver, the four experiments and every number in the README and
INSIGHTS.md hold up against an independent re-derivation. Four things have to change before this goes public, all
in the text: the calibration is still labelled "quoted from memory", the forward-guidance puzzle cites only the
2012/2015 staff report and not the published paper (the one the Nobel committee's scientific background cites),
INSIGHTS sentence 1 reads as a contradiction to a lay listener, and the label "demand shock" for the natural-rate
shock needs its definition, because the committee's background describes natural-rate shocks as supply shocks.

### 1. Runs, tests, reproducibility

| check | result |
|---|---|
| fetch step | none (pure simulation, no data, so there are no sha256 checks to match) |
| `python -m nk.run_all` (fresh venv, pinned `requirements.txt`) | 5.3 s wall, well under 1 minute |
| `python -m pytest -q tests` | **63 passed** in 6.1 s (cold) / 2.7 s (warm); 14 warnings, all `PyparsingDeprecationWarning` from inside Matplotlib |
| rerun against the committed results | `set_the_rate.json` and all 8 SVGs byte-identical; the 8 PNGs differ in bytes but are pixel-identical (only the zlib compression of the image data differs, so no content drift) |

### 2. Calibration, parameter by parameter

I could not open Galí (2015) itself. I checked each value against Johannes Pfeifer's Dynare replication of the
chapter (DSGE_mod, `Gali_2015/Gali_2015_chapter_3.mod`), which gives a book page for each value, and against the
formulas it quotes.

| parameter | toy | Galí (2015) ch. 3, as given by the replication | status |
|---|---|---|---|
| beta | 0.99 | 0.99, p. 67 | matches |
| sigma | 1 | 1, p. 67 | matches |
| phi (inverse Frisch) | 5 | 5, p. 67 | matches |
| alpha | 0.25 | 1/4, p. 67 | matches |
| epsilon | 9 | 9, p. 67 | matches |
| theta | 0.75 | 3/4, p. 67 | matches |
| kappa | 0.172 (0.171667) | lambda = (1 - theta)(1 - beta theta)/theta x Omega, Omega = (1 - alpha)/(1 - alpha + alpha epsilon) (p. 60-61); kappa = lambda (sigma + (phi + alpha)/(1 - alpha)) (p. 63) | formula and value match (lambda = 0.0214583, kappa = 8 lambda) |
| phi_pi | 1.5 | 1.5, p. 68 | matches |
| phi_y | 0.125 | 0.125, p. 68 | value matches; **but** in the second edition the rule responds to output's deviation from steady state, not to the output gap (eq. 26 in the replication: `i = phi_pi pi + phi_y yhat + nu`). In this toy no experiment moves natural output (no technology shock), so the two are the same here; the README should say so (fix 1) |
| rho (demand) | 0.5 | rho_z = 0.5 for the discount-rate (preference) shock, p. 70; the natural rate is (1 - rho_z) z, so it inherits 0.5 | matches |
| rho (cost push) | 0.5 | no cost-push shock in ch. 3 | correctly labelled "our choice" |
| phi_pi strong 3, passive 0.8 | 3, 0.8 | not from Galí | correctly labelled as own choices |

Two side notes. The shock size also lines up: the replication's discount-rate shock (0.5 to z) moves the natural
rate by 0.25 a quarter, the toy's 1 percentage point a year. And the first edition (Galí 2008) used other values (to my
knowledge phi = 1, alpha = 1/3, epsilon = 6, theta = 2/3; not checked here), so a calibration quoted from memory
could have mixed the two editions; this one did not.

The model form itself (IS curve, NKPC and a rule on the output gap) matches the Nobel committee's scientific
background, eqs. (14)-(16), printed pp. 28-29.

### 3. Independent solution

Three methods, none sharing code with the toy (the toy is imported only at the end, to compare):

1. **QZ (generalized Schur, Klein 2000)** on `A E_t s_t+1 = B s_t`, `s = [z, x, pi]`, with z the AR(1) shock
   (predetermined) and x, pi jumps; the policy function is `Z21 Z11^-1`. Unique bounded solution iff 1 stable and
   2 unstable generalized eigenvalues.
2. **Stacked perfect-foresight solve** over 600 quarters with the policy rate as an explicit third unknown each
   quarter (IS, NKPC and rule or peg as three equations), sparse solve, x = pi = 0 after the end.
3. For news about the rule's intercept, the **closed form of the forward solution** under determinacy:
   `E_t y_t+1 = M y_t + c v_t` gives `y_0 = M^-(h+1) c x cut` for a shift in quarter h.

Largest absolute differences, full precision (brief: 1e-6):

| comparison | max abs difference |
|---|---|
| QZ vs stacked, demand / cost push / cost push with phi_pi = 3 (x, pi, i over 17 quarters) | 1.7e-16 / 2.2e-16 / 5.6e-16 |
| toy vs QZ, same three IRFs | 1.7e-16 / 2.2e-16 / 4.4e-16 |
| toy vs stacked, forward guidance rule on (path, quarters 0-16) | 1.1e-16 |
| toy vs stacked, rule on, today's response for horizons 0-12 | 5.6e-17 |
| stacked vs closed form, same | 4.9e-17 |
| toy vs stacked, pegged variant, today's response for horizons 0-12 | 7.1e-15 |

My numbers (annual rates for inflation and the policy rate, per cent for the gap; 6 decimals):

| block | output gap | inflation | policy rate |
|---|---|---|---|
| demand, impact | 0.259085 | 0.352287 | 0.657973 |
| demand, sum of quarters 0-11 | 0.518044 | 0.704403 | 1.315626 |
| cost push phi_pi = 1.5, impact | -0.513040 | 1.282599 | 1.667379 |
| cost push phi_pi = 1.5, sum 0-11 | -1.025829 | 2.564573 | 3.333944 |
| cost push phi_pi = 3, impact | -0.839161 | 0.839161 | 2.097902 |
| cost push phi_pi = 3, sum 0-11 | -1.677912 | 1.677912 | 4.194780 |
| forward guidance rule on, today | -0.049774 | 0.141813 | 0.187833 |
| forward guidance rule on, in quarter 8 | 0.180832 | 0.124171 | -0.723327 |

Closed forms agree too: with D = (1 - beta rho)(sigma (1 - rho) + phi_y) + kappa (phi_pi - rho), the demand impact
is x = (1 - beta rho)/D x 0.25 = 0.259085 and the cost-push impact x = -(phi_pi - rho)/D x 0.25 = -0.513040.

All 85 values I compared with `results/set_the_rate.json` (impact and 12-quarter sums for the three shock blocks,
eigenvalue moduli and counts, rule-on today / in quarter 8 / 13 horizons, 26 pegged ratios, the demand paths to
4 decimals) match after rounding. None failed.

### 4. Determinacy (phi_pi 0.8 vs 1.5) and phi_y

Eigenvalues of the 2 x 2 system with the rule substituted, and the QZ count, for a range of phi_y:

| phi_y (quarterly) | 0 | 0.125 | 0.25 | 0.5 | 1 | 2 | 3 | 3.4 | 3.5 | 5 |
|---|---|---|---|---|---|---|---|---|---|---|
| phi_pi = 1.5: outside the unit circle | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| phi_pi = 0.8: outside the unit circle | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 |

* At the calibration (phi_y = 0.125) the moduli are 1.182, 1.182 (a complex pair) for 1.5 and 0.915, 1.393 for
  0.8, as in the JSON. The eigenvalue count, the QZ count and the closed-form condition
  kappa (phi_pi - 1) + (1 - beta) phi_y > 0 agree at every point.
* phi_y does not change the conclusion over any plausible range: with phi_pi = 0.8 the model becomes determinate
  only for phi_y > kappa (1 - phi_pi)/(1 - beta) = **3.43** at quarterly rates, 27 times the calibrated 0.125;
  with phi_pi = 1.5 it is determinate for every phi_y >= 0.
* The plain sentences ("exactly one bounded path" / "many bounded paths, so the three equations alone do not say
  which one") match the committee's own wording (scientific background, footnote 31, printed p. 30: phi_pi < 1 "can
  be consistent with self-fulfilling inflationary paths as well as stable inflation; hence, the model equations do
  not deliver a sharp answer").
* The closed-form condition has no citation in the README, although the JSON field is called
  `bullard_mitra_condition_holds` (fix 6).

### 5. Forward guidance: timing and the puzzle caveat

**Timing is consistent.** The announcement arrives at the start of quarter 0 and quarter-0 variables react to it;
the shift is in quarter 8, 8 quarters ahead, so "two years from now" in guess (c) is right. In the rule-on variant
the intercept is -0.25 a quarter (-1 pp a year) in quarter 8 only; from quarter 9 on x = pi = 0 (my stacked solve:
exactly 0 after quarter 8), which is the unique bounded continuation because the rule is determinate. The rate in
quarter 8 falls by 0.723, not 1, as the README says.

**What the rule-on path does** (worth knowing for narration): the rule raises the rate in every quarter before 8
(0.188 today, about 0.41 by quarters 5-6), the gap is negative in quarters 0-4 and positive in 5-8, and inflation
is positive in all of 0-8. So "a promise of a lower rate raises inflation today" is right, but "it lifts output
today" or "it lowers rates now" is not (the gap today is -0.05). With the rule on, the news effect decays by a
factor of 0.846 a quarter (one over the eigenvalue modulus 1.182) with an oscillation, hence the hump at quarter 3
and the sign change of the gap at quarter 4. The README's "does not grow with the horizon" is right.

**The pegged puzzle panel.** My stacked solve with the nominal rate fixed at 0 up to the promised quarter gives the
same ratios: output gap 15.834 (quarter 8) and 80.729 (quarter 12), inflation 46.325 and 236.519. The levels behind
them (quarter 8: gap 3.96 %, inflation 7.95 pp; quarter 12: 20.2 % and 40.6 pp) show why ratios were the right call.

Two points for the wording:

* The size of these ratios is a property of a **nominal** peg: while the nominal rate is held, the expected
  inflation the promise creates lowers the real rate in every pegged quarter. In the real-rate version of the
  experiment (McKay, Nakamura and Steinsson 2016, sec. I: the real rate lower in quarter h only) today's gap is the
  same 0.25 for every h and inflation today grows only to 12.2 times by quarter 12. The README already says the
  peg "is part of why its ratios grow so fast"; it should say "nominal" (fix 7).
* **Citations.** Del Negro, Giannoni and Patterson, "The Forward Guidance Puzzle", FRBNY Staff Report 574 is real
  (October 2012, revised December 2015; checked on the New York Fed page). The paper was published as Del Negro,
  Giannoni and Patterson (2023), *Journal of Political Economy Macroeconomics* 1(1): 43-79,
  doi:10.1086/724214 (Crossref), and that is the version the Nobel committee's background cites (p. 46, reference
  list p. 51). Add it (fix 2). McKay, Nakamura and Steinsson (2016), AER 106(10): 3133-3158,
  doi:10.1257/aer.20150063 is correct (Crossref); their abstract says standard models imply "far future forward
  guidance has huge effects on current outcomes, and these effects grow with the horizon", and that uninsurable
  income risk and borrowing constraints give forward guidance "substantially less power": the README's summary is
  fair. The committee's background adds that several fixes have been proposed and "no single explanation has
  emerged as a consensus" (p. 46), which supports the README's "many economists read the growth with the horizon as
  a limit of the model".

Other citations checked on Crossref: Clarida, Galí and Gertler (1999), JEL 37(4): 1661-1707,
doi:10.1257/jel.37.4.1661; Blanchard and Kahn (1980), Econometrica 48(5): 1305-1311, doi:10.2307/1912186. Woodford
(2003) and Galí (2015, 2nd ed.) titles and publisher are correct. The committee quote matches the press release
word for word ("stabilisation", British spelling).

### 6. README and INSIGHTS numbers against the JSON

Every number in the README and in INSIGHTS.md is in `results/set_the_rate.json` in the field it describes, with
the right sign (I checked them by field, not just by token). Note that the toy's own test is weaker than the README
claims: it checks that each number appears *somewhere* in the JSON, unsigned (`-0.05` passes as `0.05`), so a
wrong sign or a number from the wrong block would pass (fix 10).

### 7. Wording, neutrality and "What it does not show"

* No "should", no advocacy, no current events, no named people besides authors and laureates; the committee's
  words appear only as a quote. "No optimal policy, no welfare ranking of rules" is the right guard for the
  phi_pi = 3 comparison.
* INSIGHTS 2 opens with an imperative ("Respond to inflation twice as strongly..."), which sounds like advice in a
  narrator's voice (fix 9).
* "What it does not show" is honest about the puzzle, the calibration, the peg and the missing pieces, but misses
  that the promise is **fully believed and carried out** (perfect credibility) (fix 5), and its calibration bullet
  ("quoted from memory and still to be checked") can now say what was checked (fix 1).
* The "energy-price shock" in guess (a) is a lay reading of the model's generic cost-push term. Fine for the page
  question, but the README should say once that the model has no energy sector (part of fix 3).

### Fixes

FIX FIRST (text only; no number changes):

1. **Calibration source.** Replace "quoted from memory and still to be checked against the book" (README lines 25-26
   and 77, and each `source` cell of the table, figure subtitle unchanged) with what was checked: "values as in
   Galí (2015), ch. 3, pp. 67-70, as given by J. Pfeifer's Dynare replication `Gali_2015_chapter_3.mod`" (or the
   owner checks the book and drops the replication). Add one line: "Galí's rule responds to output's deviation from
   steady state; here no shock moves natural output, so that equals the output gap." Same in
   `constants.py`/JSON `calibration.sources`.
2. **Puzzle citation.** Add Del Negro, Marco, Marc P. Giannoni and Christina Patterson, 2023. The Forward Guidance
   Puzzle. Journal of Political Economy Macroeconomics 1(1): 43-79 (doi 10.1086/724214) to the README, `CITATIONS`
   and `DOIS`; keep the staff report as the earlier version ("2012, revised 2015; published 2023").
3. **Cost-push wording.** README experiment 2 ("The cost-push term adds 1 percentage point a year to inflation"),
   the units line ("Each shock is 1 percentage point a year on impact") and INSIGHTS 1 ("adds 1 point to
   inflation, ... inflation rises by 1.283") read as a contradiction. Say the shock adds 1 point a year *to the
   Phillips curve* (the cost-push term), and that inflation itself rises by 1.283 because firms expect the shock to
   last. Add once: "the model has no energy sector; the cost-push term stands in for any rise in firms' costs".
4. **Natural-rate shock label.** The README and the demand figure call it a "demand" shock without saying what it
   is, while the committee's background (printed p. 29) presents natural-rate shocks as "representing supply
   shocks, such as those to productivity". Say: "a rise in the natural rate that comes from households becoming
   less patient (Galí's discount-rate shock), a demand shift; a productivity shock would also move the natural
   rate, and is not modelled here".

Should fix:

5. Add to "What it does not show": "The promise is fully believed and carried out (perfect credibility and
   perfect foresight); nothing here says how much of a real announcement people would believe."
6. Cite the determinacy condition: Bullard, James and Kaushik Mitra, 2002. Learning about Monetary Policy Rules.
   Journal of Monetary Economics 49(6): 1105-1129 (doi 10.1016/S0304-3932(02)00144-7); Woodford (2003) ch. 4 and
   Galí (2015) ch. 3 state it too. Optionally add to the JSON and README that with phi_pi = 0.8 it takes
   phi_y > 3.43 (quarterly) to restore a unique path.
7. Puzzle bullet and panel C: "the **nominal** rate is held at its steady-state value until the promised cut".
8. INSIGHTS 4: add that the rate today goes up 0.188 and the gap dips 0.05 (both in `rule_on.today`), so nobody
   reads "a promised cut lifts the economy today" into it.
9. INSIGHTS 2: descriptive, not imperative ("With a rule that responds twice as strongly to inflation, 3 instead
   of 1.5, ...").

Polish:

10. `test_every_readme_number_is_in_the_json`: check signs (keep the minus in the regex) or check a field map; or
    soften the README's "a test checks that every number in this README appears there" to "appears in the JSON".
11. Integer ticks on the "quarters after the shock" axes (now 0.0, 2.5, 5.0, ...).
12. Taylor figure: the "unit circle (modulus 1)" label starts right at the edge of the second blue bar; move it to
    the far left or right.
13. Spoken numbers: round the ratios ("about 46 times", "more than 200 times") in narration; three decimals on a
    ratio read as false precision.

### Narrator sentences I'd allow

Each is true of the model as built, neutral, and uses numbers from `results/set_the_rate.json` (field in brackets).

1. "In this model, a cost-push shock worth one point a year raises inflation by 1.283 points on impact and lowers
   the output gap by 0.513 per cent, and the rule raises the policy rate by 1.667 points."
   [`cost_push_shock.baseline.impact`, `calibration.shock_pp`]
2. "With a rule that responds twice as strongly to inflation, 3 instead of 1.5, inflation rises only 0.839 and the
   gap falls 0.839 per cent: in the model, less inflation comes with a deeper dip."
   [`cost_push_shock.strong.impact`, `.phi_pi`]
3. "If the rate rises less than one for one with inflation, at 0.8, the three equations no longer pick out a single
   path." [`taylor_principle.passive`]
4. "If the central bank announces today that its rule will be one point lower two years from now, inflation in this
   model rises today, by 0.142 points, and the rule already raises today's rate by 0.188 in answer."
   [`forward_guidance.rule_on.today`]
5. "With the rule on, the effect today does not keep growing with the horizon: it is largest for a promise three
   quarters ahead." [`forward_guidance.rule_on.inflation_peak.quarter`]
6. "If instead the rate is held still until the promised cut, the effect today grows with the horizon: for a cut
   three years out, inflation today moves more than two hundred times as much as for the same cut made today. This
   is the forward guidance puzzle; the prize committee's background notes that no single explanation has yet
   emerged as a consensus." [`forward_guidance.pegged_puzzle.last`; scientific background p. 46]

Not allowed: "forward guidance works" or any "should"; "a promised cut lifts output today" (the gap today is -0.05
with the rule on); "the stronger rule is better" (no welfare ranking); any level from the pegged variant (7.95 pp,
40.6 pp) as if it were a forecast; INSIGHTS 1 as now worded; "the Taylor principle keeps inflation stable" (it gives
a unique bounded path in a linear model, nothing more; the background's footnote 46 adds that this is local).

---

## can-you-predict-spending

Round 2, branch `econ-spend` at `3a3d5aa` (BEA bulk files instead of FRED).

**Verdict: FIX FIRST.** The data are what the README says, BEA's licence line is quoted word for word, and every
number in the README, INSIGHTS.md and the JSON reproduces with an independent implementation (167 of 167 fields).
The statistics are done carefully, and the "very uncertain" framing of lambda is right. Four things have to change
first. (1) The reason given for using total PCE is wrong in effect: BEA's own file lets you build the non-durables
plus services series that Hall and Campbell-Mankiw used, and on that series lagged income stops predicting spending,
as in Hall (1978). (2) The claim that the instruments are strong once 2020-2026 are in (first-stage F 17.12) rests
on the homoskedastic F; by a robust measure the instruments are weak there too (effective F 6.8). (3) The p. 195
Campbell-Mankiw quote carries a PDF text-extraction error ("A" for λ). (4) One README sentence is broken ("(about
per cent)").

### 1. Runs, tests, sha256, reproducibility

| check | result |
|---|---|
| `python -m spend.fetch_data` (fresh venv, pinned `requirements.txt`) | 0.1 s; the sha256 of the three extracts, the register extract and `data/quarterly.csv` all match their pins |
| `python -m spend.fetch_data --refresh` | 3.3 s; downloaded `NipaDataQ.txt` (35,414,945 bytes) and `SeriesRegister.txt` (960,482 bytes) today: both sha256 match the pins, so BEA has not published since; the re-extraction is byte-identical. `curl -I` today: `last-modified: Wed, 30 Sep 2026 12:30:02 GMT`. BEA's schedule lists both named releases on 30 September and the next ones on 29 October (after that `--refresh` stops on purpose; the committed extracts keep working) |
| `python -m spend.run_all` | 34.7 s cold (first Matplotlib run in a new venv), 14.0 s warm (11.5 s with `--no-figures`), Mac load average about 4-5: under 1 minute. The README's "runs in a few seconds" is optimistic (polish 13) |
| `python -m pytest -q tests` | **37 passed, 2 skipped** in 7.4 s (skips: the bulk file not downloaded; statsmodels not installed). With the bulk file and statsmodels 0.14.4: **39 passed** in 19.6 s. Note: pip's default pandas 3 breaks statsmodels 0.14.4 (`TypeError: deprecate_kwarg()`); pandas 2.2.3 works (polish 14) |
| rerun against the committed results | `results/spending.json`, all 6 PNGs and all 6 SVGs byte-identical (`git status` clean) |

### 2. Data, licence, per-capita construction, samples

* **Licence.** <https://www.bea.gov/help/faq/147> fetched today: title "Are the information and data presented on the
  BEA web site copyright-protected?" and the line "Unless stated otherwise, ... would be appreciated." match the
  README and `constants.py` word for word (page published 17 January 2006, last modified 24 April 2018). Current.
* **No FRED left** in the toy tree: the only match for `FRED|stlouisfed` is the test that bans it. The branch history
  still has the FRED CSVs (`5e660db`: `PCECC96.csv`, `DSPIC96.csv`, `B230RC0Q173SBEA.csv`): publish the toy as a
  squashed commit, never with this branch's history.
* **Series and tables**, from the register extract: DPCERX is `T10106:2` (Table 1.1.6 line 2), A067RX `T20100:37`
  (Table 2.1 line 37), B230RC `T20100:40` and also `T70100:18` (so "the one BEA itself uses for Table 7.1" is
  right). Chained-2017 check: the 2017 averages of DPCERX and DPCERC are both 13,290,625.5 million.
* **Per person.** `log(c x 1e3 / n)` with c in millions of dollars and n in thousands of persons is log dollars per
  person: correct. My own build from the bulk file (pandas, not the toy's extracts) matches `data/quarterly.csv` to
  5.0e-11 in every log. Growth is the first difference of logs, labelled by the later quarter, written in log points.
* **Samples.** Data 1959Q1-2026Q2 (270 quarters, 269 growth rates); with four lags the first regression quarter is
  1960Q2 (n = 265); pre-2020 1960Q2-2019Q4 (239); halves 1960Q2-1992Q4 (131) and 1993Q1-2026Q2 (134);
  "their end" 1960Q2-1986Q4 (107). All as stated. The start in 1959 is a leftover (the README says so): BEA's
  quarterly series start in 1947Q1, so Campbell and Mankiw's own window, 1953:1-1986:4, is available; I ran it below.
* **The total-PCE claim is wrong in effect (fix 1).** The README and `WHY_TOTAL_PCE` say a long non-durables plus
  services series "cannot be built by summing" chained components, because DNDGRX and DSERRX start in 2007Q1. True
  as far as it goes, but the same bulk file has BEA's Fisher quantity indexes (DNDGRA, DSERRA) and current-dollar
  values (DNDGRC, DSERRC) from 1947Q1, which is all a Fisher chain needs. My check of the method: the same Fisher
  formula on durables, non-durables and services reproduces BEA's own total-PCE quantity index (DPCERA) to 1.8e-4
  in quarterly log growth at most (the published indexes have 3 decimals). It matters (section 4): on non-durables
  and services, lagged income no longer predicts spending (p 0.399 instead of 0.0253), as Hall found.

### 3. Hall's test, independent

statsmodels OLS with `cov_type="HAC"`, Bartlett, 4 lags, no small-sample correction (the toy's setting), F tests
with F(q, n - k):

| | toy (JSON) | mine |
|---|---|---|
| lags 2-4, 1960Q2-2019Q4: R² / adjusted / F / p | 13.9 / 11.6 / 4.86 / 0.000108 | 13.858 / 11.630 / 4.858 / 0.0001075 |
| lags 2-4, 1960Q2-2026Q2: R² / p | 4.2 / 0.000477 | 4.222 / 0.0004765 |
| lags 1-4, same two samples: R² | 20.1 / 16.9 | 20.06 / 16.93 |
| out of sample from 1993Q1 (lags 2-4 to 2019 / full; lags 1-4 to 2019 / full) | 27.2 / -11.2 / 31.8 / -53.8 | 27.15 / -11.24 / 31.76 / -53.84 |

All 10 Hall-test fields in each of the 4 samples, and the 4 out-of-sample R², match. The headline p-value does not
hinge on the HAC choices: 8 lags give 4.0e-7, the small-sample correction 1.5e-4. Full-precision difference to the
toy's NumPy code: at most 4.5e-10 (coefficients) and 1.2e-10 (HAC standard errors).

The toy calls lags 1-4 "Hall's original form". Hall (1978) worked in levels: consumption of non-durables and
services per person in 1972 dollars, 1948-1977 (p. 979), regressed on its first lag plus four lags of disposable
income (Table 3, eq. 3.2, p. 982), where the four income lags gave F 2.0 against a 5 % critical value of 2.4: no
predictive power (fix 6).

### 4. Campbell-Mankiw lambda, independent

linearmodels `IV2SLS` with `cov_type="kernel"`, Bartlett, bandwidth 4 (the same weights as the toy), constant in
both stages, instruments lags 2-4 (right for time-averaged data: Campbell and Mankiw p. 190, Working 1960). The
Anderson-Rubin set is my own grid of statsmodels HAC Wald F tests, with the ends found by root-finding.

| 1960Q2-2019Q4, both sets of lags | toy | mine |
|---|---|---|
| 2SLS lambda (HAC s.e.), 95 % interval | 0.715 (0.182), 0.359 to 1.07 | 0.7152 (0.1815), 0.3588 to 1.0704 |
| first-stage F, homoskedastic / HAC | 3.68 / 4.88 | 3.681 / 4.880 |
| **effective F (Montiel Olea-Pflueger 2013, HAC)** | not computed | **4.09** |
| AR 95 % set (HAC) | 0.885 to 1.841 (grid 0.001) | 0.88470 to 1.84133 |
| AR set, homoskedastic version | not computed | 0.711 to 1.997 |
| other estimators: OLS / LIML / two-step GMM / CUE-GMM | OLS 0.293 | 0.293 / 1.104 / 0.836 / 1.323 |

All 15 sample-by-instrument cells (5 samples x 3 instrument sets: lambda, s.e., interval, both F's, AR set) match
after rounding; unrounded, lambda differs from the toy's by 3e-9 and its s.e. by 1e-9. The spread of estimators
(0.72 to 1.32) supports "very uncertain"; it also explains why the AR set leaves out 0.715: the AR statistic is
lowest near the continuously-updated GMM estimate (1.23-1.32), not at 2SLS. The README's explanation ("2SLS weights
them as if the errors were independent") is fair.

**Weak instruments with 2020-2026 in (fix 2).** The README says "The first-stage F is above 10 in that sample but not
in any sample that ends before 2020", and guess (b) reports "first-stage F 17.12" for the full sample. That F assumes
homoskedastic errors, which the 2020-2021 quarters break:

| 1960Q2-2026Q2 | homoskedastic F | HAC F | effective F |
|---|---|---|---|
| both | 17.12 | 6.84 | 6.77 |
| consumption growth | 30.05 | 5.69 | 6.56 |
| income growth | 12.45 | 3.69 | 2.93 |

By the robust measures the instruments are weak in the full sample as well (the lambda figure's filled markers
there say the opposite). Only the second half, 1993Q1-2026Q2, has strong ones (effective F 18.1 with both sets,
30.4 with consumption). The full-sample 2SLS interval, -0.148 to 0.108, is tight but not trustworthy, and the HAC AR
set is empty while the homoskedastic AR set is -0.104 to 0.112, so "no single lambda fits those years" holds only
for the HAC version, whose test over-rejects in samples this size (section 5).

**Against Campbell and Mankiw's published numbers.** Table 1 is on p. 192 of the NBER chapter (PDF fetched from
nber.org; sha256 bf87...44f6): all nine rows and standard errors in `CM_TABLE1` match (OLS 0.316 (0.040); rows 2-9:
0.417 (0.235), 0.506 (0.176), 0.419 (0.161), 0.523 (0.131), 0.698 (0.235), 0.584 (0.137), 0.351 (0.119), 0.469
(0.106)). The quotes check against the page: p. 190 (time aggregation), p. 195 ("about 0.5"; and that total consumer
spending "turned out to be similar"), p. 208 ("about 50 percent of income"). But the p. 195 quote reads "estimates
of A": the PDF's text layer renders λ as "A" (Table 1's header comes out as "Acy =Y + AAyt"); the paper says λ
(fix 3).

My runs in their own window, 1953Q1-1986Q4 (n = 136), with their row 8 instrument (c - y lagged two quarters)
added:

| instruments, lags 2-4 | Campbell-Mankiw Table 1 (non-durables + services, 1982 $) | toy, 1960Q2-1986Q4, total PCE | mine, 1953Q1-1986Q4, total PCE | mine, 1953Q1-1986Q4, non-durables + services (Fisher) |
|---|---|---|---|---|
| income growth | row 2: 0.417 (0.235) | 1.478 | 1.116 (0.455) | 0.607 (0.233) |
| consumption growth | row 4: 0.419 (0.161) | 0.481 | 0.490 (0.296) | 0.446 (0.157) |
| both | none | 0.408 | 0.410 (0.210) | 0.298 (0.122) |
| both + c - y lagged 2 | row 8: 0.351 (0.119) | none | 0.442 (0.201) | 0.275 (0.135) |

With their consumption concept and window, today's data come close to rows 4 and 8; with total PCE the income-lag
row is far off. First-stage F in that window is 0.9-2.2 (effective F 1.7-2.9): the instruments were weak in their
sample too, which their p. 191 caution about rows 2 and 3 already hints at.

**Non-durables + services over the toy's samples** (my numbers, for fix 1): 1960Q2-2019Q4, lags 2-4 R² 16.4 %
(p 3.4e-7), lags 1-4 25.5 %, the four income lags p 0.399 (total PCE: 0.0253); 2SLS lambda 0.596 (interval 0.335 to
0.858), first-stage F 3.39, effective F 4.22, HAC AR set 0.673 to 1.498. Full sample: 2SLS -0.051, effective F 15.4.
So the qualitative story survives (predictable with lags 2-4, lambda weakly identified, 2020-2026 pull it to zero),
but the headline numbers would move.

### 5. The simulated control

The design is right for its purpose: forward-looking growth g + 0.5 u + news has no predictable part,
hand-to-mouth spending equals income, and the mix dc = lambda dy + (1 - lambda)(g + 0.5 u + news) is Campbell and
Mankiw's log-linear model; points in time, so no time aggregation. The weak-instrument bias goes where theory says:
OLS converges to lambda + (1 - lambda) 0.5 (1 - rho²) = 0.426 (rho 0.8) and 0.619 (rho 0.3); the weak-case median
2SLS, 0.538, lies between the truth 0.3 and 0.619, and 0.346 between 0 and 0.455 in the random-walk case.

I re-implemented it from the README's description (statsmodels, linearmodels, seed 7 instead of 2026, 1000 runs):

| case | Hall rejects | 95 % interval covers | AR set covers | median lambda | median F |
|---|---|---|---|---|---|
| hand-to-mouth 0.3, rho 0.8: toy / mine | 99.9 / 100.0 | 94.2 / 93.4 | 89.1 / 87.5 | 0.300 / 0.300 | 28.6 / 28.1 |
| random walk, rho 0.8 | 15.2 / 15.7 | 93.3 / 93.5 | 87.1 / 88.2 | 0.002 / 0.003 | 28.9 / 28.2 |
| hand-to-mouth, rho 0.3 | 40.4 / 36.0 | 56.3 / 57.0 | 88.7 / 91.0 | 0.538 / 0.538 | 1.2 / 1.1 |
| random walk, rho 0.3 | 15.1 / 14.4 | 54.5 / 55.3 | 88.8 / 89.0 | 0.346 / 0.335 | 1.2 / 1.2 |

Within Monte Carlo error (about 1.6 points at 50 %, 1 point at 90 %; the largest gap, 4.4 points, is about 2
standard errors of a difference between two seeds). Median lags 2-4 R² in the random walk: 2.1 % (toy), 2.0 %
(mine). The over-rejection of the HAC F tests (15 % at a nominal 5 %; AR coverage 87-91 %) is real and the README
states it.

### 6. README and INSIGHTS numbers against the JSON

I checked every number by field, not by token: both Hall tables, the lambda table, the published-row comparison, the
pandemic quarters (2020Q2 -9.1 / +9.4, 2021Q1 +2.3 / +11.6 log points, standard deviation 0.65), the out-of-sample
block (including the means 0.6 and 0.46), the control table and its example run (0.314, 0.261 to 0.367, OLS 0.435),
the data table (318 rows, 1947Q1-2026Q2, byte counts) and all five INSIGHTS sentences. All right, with the right
sign. As in round 1, the toy's own number test checks unsigned tokens anywhere in the JSON (polish 15).

### 7. Wording, neutrality and "What it does not show"

* No "should", no advocacy, no forecast; the one policy word is the disclaimer ("they say nothing about what any
  policy does or would do"). The committee and Campbell-Mankiw appear only as quotes, credited.
* **Causes of 2020-2021.** "lockdowns and relief payments moved spending and income" (README section 1 and
  `guess.a.why_to_2019`) is an unsourced causal claim, next to the README's own "No causal claim" bullet, and it
  brings a policy into the toy's voice (fix 5).
* "What it does not show" is honest on aggregation, durables, measurement error, time aggregation, weak instruments,
  causality and the chosen samples. Two gaps: the durables bullet's "see Data for why we did not" points to the wrong
  reason (fix 1), and the weak-instrument bullet's "first-stage F below 10 in every sample that ends before 2020"
  implies the later samples are fine (fix 2).
* Hall and Mishkin are cited as the committee states them (scientific background PDF p. 25 = printed p. 23, sample
  on PDF p. 24: food consumption of 2,309 PSID families, 1969-1975), and the README keeps the committee's
  "fraction of consumption" rather than the popular text's "80 per cent of them [households]". Good.
* INSIGHTS 4 ends at "88.5 to 184.1 per cent", but a share above 100 per cent is impossible; the README says so,
  INSIGHTS does not (fix 7).

### Fixes

FIX FIRST:

1. **Total PCE: change the reason, and preferably add the series.** In README "Durables are in" and "Data", and
   `WHY_TOTAL_PCE`, drop "cannot be built". Say: "BEA publishes chained-dollar non-durables and services only from
   2007, but a long series can be built by Fisher-chaining BEA's quantity indexes (DNDGRA, DSERRA) with their
   current-dollar values (DNDGRC, DSERRC), as BEA builds its totals". Then either (a) add it as a robustness row
   (my numbers above: lags 2-4 R² 16.4 %, income lags p 0.399, lambda 0.596 with interval 0.335 to 0.858; 1953Q1-1986Q4
   rows 0.607 / 0.446 / 0.275 next to their 0.417 / 0.419 / 0.351), or (b) switch the headline to it, which is the
   series Hall and Campbell-Mankiw used (all numbers change; narration waits). Owner's call; (a) is the smaller change.
2. **Weak-instrument diagnostic for samples with 2020-2026.** Report the HAC or effective first-stage F next to (or
   instead of) the homoskedastic one, and cite Montiel Olea and Pflueger (2013). Rewrite "The first-stage F is above
   10 in that sample but not in any sample that ends before 2020, which points to those few quarters" (README
   section 2), "first-stage F 17.12" (Guess first, `guess.b.ours`) and the weak-instrument bullet: by the robust
   measure (6.8 with both sets of lags) the full-sample instruments are weak too, and only 1993Q1-2026Q2 has strong
   ones. Draw the lambda figure's open/filled markers from the robust F.
3. **Misquote, p. 195.** "we get estimates of A, the fraction of the population ..." should read λ (or "[lambda]"),
   in README section 2, `CM_TABLE1["about_half"]` and the JSON.
4. **Broken sentence.** README section 2: "in 2020Q2 spending per person fell 9.1 log points (about per cent)" has
   lost its number. Use `pandemic.quarters.*.dc_change_pct`: "fell 9.1 log points (8.7 per cent) while income per
   person rose 9.4 (9.9 per cent); in 2021Q1 income rose 11.6 (12.3 per cent) and spending 2.3".

Should fix:

5. Replace "lockdowns and relief payments moved spending and income per person ..." with a description: "In the
   2020-2021 pandemic quarters, spending and income per person moved by many times their usual quarterly change,
   often in opposite directions" (README section 1 and `why_to_2019`), or cite BEA's own release text for the cause.
6. "Lags 1-4 are Hall's original form": say "close to Hall's test, which used levels (consumption on its first lag
   and four lags of income, 1948-1977; Hall 1978, Table 3, p. 982) and found no predictive power in income (F 2.0,
   5 % critical value 2.4)". Optionally add that the four income lags here give p 0.0253 on total PCE (a weak result,
   given that the random-walk control rejects 10.5 % of the time at a nominal 5 %) and p 0.399 on non-durables and
   services.
7. INSIGHTS 4: add "values above 100 per cent are not possible for a share, a sign that the simple two-group model
   does not fit these data well" (the README's own point).
8. Control figure, panel C: the "Hall's test rejects" bar for share 0.3, strong, is labelled "100" for 99.9; label
   it 99.9 (the lab's rule: toy values near 100 % never round to 100), and stop the y axis near 105, not 140.
9. Full-sample AR set: say "the HAC Anderson-Rubin set is empty" and that this test rejects too often here (the
   homoskedastic version gives -0.104 to 0.112), rather than "no single lambda fits those years" as a plain fact.

Polish:

10. Name the effective F's critical value if the robust F is added (Montiel Olea-Pflueger's 5 % test for a 10 %
    worst-case bias is about 23, far above 10), or keep the rule of thumb and say it is for homoskedastic errors.
11. The README could show the estimator spread for the headline sample (2SLS 0.715, LIML 1.10, two-step GMM 0.84,
    CUE 1.32): an honest picture of "very uncertain". Not needed for the numbers it already prints.
12. `sd_dc_pct_1960_2019` includes the three 1959 growth rates (1959Q2-Q4); the value is 0.65 either way; rename or
    say "1959-2019".
13. "runs in a few seconds": measured 12-35 s here; say "in under a minute".
14. `tests/make_statsmodels_reference.py`: add "pandas 2.2.3" to the versions (pandas 3 breaks statsmodels 0.14.4).
15. `test_every_readme_number_is_in_the_json` checks unsigned tokens anywhere (round 1 fix 10 applies here too).

### Narrator sentences I'd allow

True on the data and toy as built, neutral, with numbers from `results/spending.json` (field in brackets). If the
owner takes fix 1 (b), the numbers in 2, 3 and 6 change.

1. "Robert Hall's idea: if households spend according to what they expect to earn over their lives, nothing known
   in advance predicts next quarter's change in their spending." [README intro; committee quote]
2. "In US data from 1960 to 2019, spending and income growth from two to four quarters back account for 13.9 per
   cent of the quarter-to-quarter changes in spending per person. Hall's benchmark is zero."
   [`guess.a.answer_pct`, `guess.a.hall_benchmark_pct`]
3. "With the years up to 2026 included, that share falls to 4.2 per cent." [`guess.a.full_sample_pct`]
4. "Campbell and Mankiw estimated in 1989 that about half of income goes to households who spend what they earn."
   [`guess.b.published.campbell_mankiw_about_pct`]
5. "In household data, as the prize committee describes Hall and Mishkin's 1982 study, about 20 per cent of
   consumption moved hand in hand with current income." [`guess.b.published.hall_mishkin_pct`]
6. "On our aggregate data that share is very uncertain: the usual 95 per cent interval runs from 36 to 107 per
   cent, because past growth barely predicts income." [`guess.b.ours.ci95_pct`, `.first_stage_F`]
7. "In a simulated world with no hand-to-mouth households at all, the same method with such weak instruments
   typically found a share of about a third." [`control.cases.random_walk_weak.median_lambda`]

Not allowed: "half of Americans live hand to mouth" (a share of income in aggregate data, not of households); "Hall
was wrong" or "Hall was right" (the toy shows predictability with total PCE and a weakly identified lambda, nothing
about why); any "184 per cent" or the AR range as a share; "with the pandemic years the estimate is precise" or
"first-stage F 17" as a sign of strong instruments (fix 2); any cause for the 2020-2021 quarters (fix 5); any "should".

---

## Sources used in this review

* The Committee for the Prize in Economic Sciences in Memory of Alfred Nobel, 12 October 2026. Scientific
  Background: Microeconomic Foundations of Macroeconomic Stabilization (printed pages: eqs. 14-16 p. 28-29,
  footnote 31 p. 30, footnote 46 p. 39, forward guidance puzzle p. 46, references p. 51; round 2: Hall's test
  pp. 16-18, Campbell and Mankiw p. 20-21, Hall and Mishkin pp. 22-23).
* Round 2: Campbell, John Y. and N. Gregory Mankiw, 1989, NBER Macroeconomics Annual 4: 185-246
  (nber.org/system/files/chapters/c10965/c10965.pdf; pp. 190, 191, 192 Table 1, 195, 208). Hall, Robert E., 1978,
  JPE 86(6): 971-987 (pp. 979, 982). The Royal Swedish Academy of Sciences, popular information on the 2026 prize
  (PDF p. 3). BEA FAQ 147, BEA release schedule (bea.gov/news/schedule/full), BEA bulk NIPA files (release of 30
  September 2026). Montiel Olea, José Luis and Carolin Pflueger, 2013. A Robust Test for Weak Instruments. Journal of
  Business & Economic Statistics 31(3): 358-369.
* Pfeifer, Johannes. DSGE_mod, `Gali_2015/Gali_2015_chapter_3.mod` (Dynare replication of Galí 2015, ch. 3, with
  book page numbers for each parameter), github.com/JohannesPfeifer/DSGE_mod.
* Federal Reserve Bank of New York, Staff Report 574 page (dates of the staff report).
* Crossref records for the DOIs above.
* Klein, Paul, 2000. Using the generalized Schur form to solve a multivariate linear rational expectations model.
  Journal of Economic Dynamics and Control 24(10): 1405-1423 (method of the QZ cross-check).
