# Set the rate: Woodford's three-equation New Keynesian model (Economics 2026, toy A)

> **Educational demos made to show an open-source tool. Not research.**
> Pure simulation, no data, no forecast. Every number below comes from `results/set_the_rate.json`, and a test checks
> that each number in this README appears in the JSON.

The 2026 Sveriges Riksbank Prize in Economic Sciences in Memory of Alfred Nobel went to Robert E. Hall and Michael
Woodford, in the committee's words "for microeconomic foundations of macroeconomic stabilisation" (nobelprize.org
press release, 12 October 2026). This folder is a small, exact lab about one model from that work: the
three-equation New Keynesian model of Woodford's *Interest and Prices* (2003), in the form of Clarida, Galí and
Gertler (1999) and Galí (2015). It is a lab about a model and a test of that model's own logic, not an argument
for or against any policy, institution or school of thought.

Own code, MIT licence. CPU only; runs in a few seconds (well under 1 minute). Python with NumPy and Matplotlib.

## What it does not show

* **The forward guidance puzzle.** In this textbook model, if the nominal rate is held at its steady-state value until a promised cut, the
  cut moves today's output gap and inflation by more the further ahead it is. Relative to the same cut made today,
  the effect on inflation today is 46.325 times as large for a cut promised for quarter 8 and 236.519 times for
  quarter 12 (output gap: 15.834 and 80.729 times). Del Negro, Giannoni and Patterson (2012, 2015; published 2023, the version the committee's scientific background
  cites, p. 46) named this the forward guidance puzzle; McKay, Nakamura and Steinsson (2016) also find it
  implausible and show how incomplete markets shrink it. Many economists read the growth with the horizon as a
  limit of the model, not as a fact about economies. These ratios are the puzzle, not a measurement.
* **One calibration, not an estimate.** The values are as in Galí (2015), ch. 3, pp. 67-70 (checked against Pfeifer's Dynare replication); they are not fitted to any economy or period. The persistence of the cost-push shock (0.5) is our own choice, set equal to the spending shock's;
  the stronger rule (phi_pi = 3) is our own choice too. The sizes of every response depend on these values.
* **No data, no forecast, no real episode.** Nothing here describes any real central bank, decision or period.
* **What is left out.** No capital, no zero lower bound, no learning, no hand-to-mouth households, no optimal
  policy, no welfare ranking of rules. The model is linear, with rational expectations, around a zero-inflation
  steady state.
* **Indeterminacy is counted, not simulated.** For phi_pi = 0.8 we report that the model has many bounded paths;
  we do not draw any of them (no sunspots).
* **The promise is fully believed and carried out** (perfect credibility and perfect foresight); nothing here says
  how much of a real announcement people would believe.
* **No energy sector.** The cost-push term stands in for any rise in firms' costs; the "energy-price shock" of the
  first guess question is a plain-words reading of that term.
* **The puzzle variant holds the nominal rate still until the promised cut.** There the rate does not answer the boom the
  promise creates until the cut has happened; that assumption is part of why its ratios grow so fast. The headline
  variant of experiment 4 keeps the rule on in every quarter and does not make it.

## How to run

From `2026/economics/set-the-rate/`:

```bash
python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python -m nk.run_all        # results/set_the_rate.json + figures (light and dark, PNG and SVG)
python -m pytest -q tests
```

## Guess first

The page asks these before it shows anything; the true answers are in the JSON under `guess`.

1. An energy-price shock raises firms' costs. In this model, does the rule raise or lower the policy rate?
2. If the rate rises less than one for one with inflation (0.8), what happens in the model?
3. A promise about the rate two years from now: does it move inflation today?

Answers (from the model): (1) it raises it, by 1.667 percentage points a year on impact; (2) there is no unique
bounded solution, so the model alone does not pin down what happens; (3) yes: with the rule on in every quarter,
inflation today rises by 0.142 percentage points a year. How large the effect is depends on what the rate does
until then; with the rate held still it grows with the horizon (the forward guidance puzzle).

## What it shows

**The model** (quarterly, in deviations from steady state; x = output gap, pi = inflation, i = policy rate,
rn = natural rate of interest, after Wicksell; u = cost-push shock):

```
IS (Euler):  x_t  = E_t x_t+1 - (1/sigma) (i_t - E_t pi_t+1 - rn_t)
NKPC:        pi_t = beta E_t pi_t+1 + kappa x_t + u_t
Rule:        i_t  = phi_pi pi_t + phi_y x_t
```

Households look ahead (the Euler equation), firms that set prices look ahead (the New Keynesian Phillips curve),
and the rule sets the rate. Shocks are AR(1). The solution is by undetermined coefficients; a Blanchard and Kahn
(1980) eigenvalue count says whether it is the only bounded one, and a stacked perfect-foresight solve
cross-checks it. Tests check that every path satisfies the three equations to within 1e-10.

**Calibration** (quarterly; as in Galí (2015), ch. 3, pp. 67-70 (checked against Pfeifer's Dynare replication)):

| parameter | value | meaning | source |
|---|---|---|---|
| beta | 0.99 | discount factor | as in Galí (2015), ch. 3 |
| sigma | 1 | inverse intertemporal elasticity of substitution | as in Galí (2015), ch. 3 |
| kappa | 0.172 | slope of the Phillips curve, from phi = 5, alpha = 0.25, epsilon = 9, theta = 0.75 | formula as in Galí (2015), ch. 3 |
| phi_pi | 1.5 | rule: response to inflation | as in Galí (2015), ch. 3 |
| phi_y | 0.125 | rule: response to the output gap (0.5/4 at quarterly rates) | as in Galí (2015), ch. 3 |
| rho (spending shock) | 0.5 | persistence of the natural-rate shock | as in Galí (2015), ch. 3 (discount-rate shock) |
| rho (cost push) | 0.5 | persistence of the cost-push shock | our choice |

Galí's rule responds to output's deviation from steady state; here no shock moves natural output, so that equals
the output gap.

Units: the output gap in per cent; inflation and the policy rate in percentage points at an annual rate. Each shock term is 1 percentage point a year on impact (in the IS curve for the spending shock, in the Phillips
curve for the cost-push shock). Cumulative sums are over quarters 0 to 11 (12 quarters).

**1. A spending shock (households less patient).** Households become less patient (Galí's discount-rate
shock), a demand shift, so the natural rate of interest rises by 1 percentage point a year. The committee's
scientific background (p. 29) presents natural-rate shocks as representing supply shocks, such as those to
productivity; a productivity shock would also move the natural rate, and is not modelled here. On impact the output
gap is 0.259 %, inflation 0.352 and the policy rate 0.658 percentage points a year; over 12 quarters the sums are
0.518, 0.704 and 1.316. All three move in the same direction and return to zero. Figure:
`results/demand_shock_{light,dark}.{png,svg}`.

**2. A supply (cost-push) shock.** The cost-push term adds 1 percentage point a year to the Phillips curve;
inflation itself rises by more (1.283 on impact) because firms expect the shock to last. The model gives a
trade-off: inflation goes up and the output gap goes down.

| rule | inflation on impact | output gap on impact | policy rate on impact | inflation, sum of 12 quarters | output gap, sum of 12 quarters |
|---|---|---|---|---|---|
| phi_pi = 1.5 | 1.283 | -0.513 | 1.667 | 2.565 | -1.026 |
| phi_pi = 3 (stronger) | 0.839 | -0.839 | 2.098 | 1.678 | -1.678 |

With the stronger inflation response, inflation rises less and the output gap falls more, at impact and over 12
quarters. The rule raises the rate in both cases. Figure: `results/cost_push_shock_{light,dark}.{png,svg}`.

**3. The Taylor principle.** Both x and pi are forward-looking, so a unique bounded solution needs 2 eigenvalues
outside the unit circle.

| phi_pi | eigenvalue moduli | outside the unit circle | unique bounded solution |
|---|---|---|---|
| 1.5 | 1.182, 1.182 | 2 of 2 | yes |
| 0.8 | 0.915, 1.393 | 1 of 2 | no |

In one sentence each: with phi_pi = 1.5, the rate rises more than one for one with inflation, and the model has
exactly one bounded path after any shock; with phi_pi = 0.8, the rate rises less than one for one with
inflation, and the model has many bounded paths, so the three equations alone do not say which one the economy
follows. The count agrees with the closed-form condition kappa (phi_pi - 1) + (1 - beta) phi_y > 0 (Bullard and Mitra
2002; Woodford 2003; Galí 2015). Figure:
`results/taylor_principle_{light,dark}.{png,svg}`.

**4. Communication (forward guidance).** Today (quarter 0) the central bank announces that its rule will be 1
percentage point a year lower in quarter 8 only (a one-quarter shift of the rule's intercept); the rule stays on in
every quarter, and everyone knows the path from then on (perfect foresight, rational expectations). Today the
output gap is -0.05 %, inflation 0.142 and the policy rate 0.188 percentage points a year: the expected boom in
later quarters raises inflation today, and the rule answers it today. In quarter 8 itself the gap is 0.181 %,
inflation 0.124 and the rate -0.723 (less than the full shift, because the rule answers that quarter's inflation
and gap). In this model, expectations of a future rate move today's decisions.

By horizon (the same shift promised for quarter 0 to 12), with the rule on:

| quarter of the shift | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| output gap today (%) | 0.181 | 0.12 | 0.069 | 0.028 | -0.003 | -0.025 | -0.04 | -0.047 | -0.05 | -0.048 | -0.044 | -0.039 | -0.032 |
| inflation today (pp a year) | 0.124 | 0.205 | 0.25 | 0.267 | 0.262 | 0.242 | 0.212 | 0.178 | 0.142 | 0.107 | 0.076 | 0.048 | 0.026 |

With the rule on, the effect today does not grow with the horizon: inflation today peaks for a shift in quarter 3
(0.267) and then falls, and the output gap today is below zero for every shift from quarter 4 on. The second,
"puzzle" variant holds the nominal rate still until the promised quarter; there the effect today grows with the horizon
(see "What it does not show", reported as ratios to a cut made today). Figure:
`results/forward_guidance_{light,dark}.{png,svg}` (panels A and B: rule on; panel C: the puzzle).

## Files

| file | in plain words |
|---|---|
| `nk/constants.py` | the calibration with a source for each value, the experiments, the citations |
| `nk/model.py` | the three equations, Galí's kappa formula, undetermined coefficients, the Blanchard-Kahn count, forward guidance (rule on, and rate held still), the stacked cross-check |
| `nk/figures.py`, `nk/run_all.py` | the figures (light and dark, PNG and SVG with title and description) and the results JSON |
| `results/set_the_rate.json` | every number in this README, and the answers under `guess` |
| `tests/test_model.py` | Blanchard-Kahn counts, the equations to 1e-10, the zero steady state, a hand-checked case with no persistence |
| `tests/test_conventions.py` | README and INSIGHTS numbers against the JSON, the label, neutral wording, figures in both themes |
| `INSIGHTS.md` | sentences a narrator could say, each traced to a JSON field |

The starting point was the monetary toy of the economics kit (branch `econ-prep`, `2026/economics/_kit/monetary`).

## Citations

* Woodford, Michael, 2003. Interest and Prices: Foundations of a Theory of Monetary Policy. Princeton University
  Press.
* Clarida, Richard, Jordi Galí and Mark Gertler, 1999. The Science of Monetary Policy: A New Keynesian Perspective.
  Journal of Economic Literature 37(4): 1661-1707.
* Galí, Jordi, 2015. Monetary Policy, Inflation, and the Business Cycle: An Introduction to the New Keynesian
  Framework and Its Applications, second edition. Princeton University Press.
* Blanchard, Olivier Jean and Charles M. Kahn, 1980. The Solution of Linear Difference Models under Rational
  Expectations. Econometrica 48(5): 1305-1311.
* Del Negro, Marco, Marc P. Giannoni and Christina Patterson, 2023. The Forward Guidance Puzzle. Journal of
  Political Economy Macroeconomics 1(1): 43-79.
* Del Negro, Marco, Marc Giannoni and Christina Patterson, 2012, revised 2015. The Forward Guidance Puzzle. Federal
  Reserve Bank of New York Staff Reports 574 (the earlier version; published 2023).
* Bullard, James and Kaushik Mitra, 2002. Learning about Monetary Policy Rules. Journal of Monetary Economics 49(6):
  1105-1129.
* McKay, Alisdair, Emi Nakamura and Jón Steinsson, 2016. The Power of Forward Guidance Revisited. American Economic
  Review 106(10): 3133-3158.
