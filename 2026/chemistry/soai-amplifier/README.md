# Soai's amplifier (Chemistry 2026, experiment 3)

> **Educational demo made to show an open-source tool. Toy model, not research.**
> Every number here is **our toy model, trend only**, in dimensionless model units. These are **published toy
> models of several**; the real mechanism of the Soai reaction is still debated (two detailed mechanisms remain,
> Nobel scientific background pp. 14–16). Nothing here reproduces, explains or validates the real reaction, and the
> Nobel Committee calls the Soai reaction "an important proof of concept" that "is not relevant for the emergence of
> biological homochirality in aqueous systems" (SCI p. 13).

Kenso Soai found a molecule that makes copies of itself **with its own handedness**, and that gets purer (higher ee, defined
below) as it copies. In 2003 his group started from a **prepared** head start of **0.00005 % ee** (five parts in ten million) and
ran the reaction three times, each run seeded with the product of the one before: **57 % → 99 % → >99.5 % ee**
(Sato et al., Angew. Chem. Int. Ed. 2003, 42, 315; SCI p. 12). This folder asks: what kind of copying can do that?

ee (enantiomeric excess) = (one hand − mirror hand) / all, in per cent: 75:25 is 50 % ee. "Purer" below means a
higher ee: a bigger lead of one hand.

Own code, MIT licence. CPU only; the full run takes about 20 seconds (4 worker processes). Python 3.11 with NumPy,
SciPy, Matplotlib. Nothing here describes a lab procedure, a reagent or a condition.

## Run it

From `2026/chemistry/soai-amplifier/`:

```bash
python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python -m amplifier.run_all       # results/amplifier_summary.json, results/rounds.json, figures (~20 s)
python -m pytest -q tests         # 18 tests, about 15 s
```

## The idea in plain words

Product molecules pair up. A **same-hand pair** makes more of its own hand. A **mixed pair** (one of each hand)
does nothing. This is Kagan's curve (`../kagan-curve/`) fed back on itself: the mixed pairs soak up the minority
hand, so each new molecule is purer than the pool it came from.

How fast does the ee climb? In this toy there is a one-line answer:

    d ln(ee) / d ln(amount) = β = (mixed pairs) / (same-hand pairs)

If pairs form **at random** (K = 4), β is about 1 at small ee: the ee only grows **in proportion to the amount of
product**. Going from 0.00005 % to 57 % then needs the product to grow about 1.7 million-fold. If mixed pairs are
**strongly preferred** (K large), β is about √K / 2 and the ee grows like a power of the amount: a few rounds suffice.

## Results (our toy model, trend only)

| question | answer | how exact |
|---|---|---|
| Layer 1, random pairing (K = 4): start 0.01 %, 10⁴ turnovers | **61.8 %** (Blackmond: "just over 60 %") | exact formula |
| Layer 1: start 0.5 %, 10⁴ turnovers | **99.0 %** (Blackmond: "approaches homochirality") | exact formula |
| K = 4: turnovers needed for 0.00005 % → 57 % | **about 1.7 million** (1,689,000) | exact formula |
| K = 4 with 5 / 43 / 50 turnovers per round, three rounds | 0.011 % / 4.2 % / 6.6 % after round 3: **fails** | exact formula |
| Layer 2, our toy fitted to rounds 1 and 2 | **K = 73, 43 turnovers per round**: 57 → 99 → **99.98 %** (round 3 is a prediction; Soai: >99.5 %) | fitted toy numbers |
| Layer 2, one hand vs mirror hand over three rounds (fitted toy) | one hand ×169,000 (0.5 → 84,400), mirror hand ×19 (0.5 → 9.6) | toy amounts, not Soai's |
| Layer 3, Buhse-Micheau model, Fig. 1 parameters, start 10⁻⁵ % | **84.9 %** (Buhse: "about 85 %") | ODE, tolerance 1e-10 |
| Layer 3, exactly racemic start | **exactly 0** (and up to 62 % if coded the naive way, depending on solver tolerances; see below) | exact by construction |
| Layer 3, how fast mixed pairs must form (k2) | from 10⁻⁵ %: amplification switches on between k2 ≈ 1.6 × 10³ and 6 × 10³ (50 % at 6 × 10³); from 0.1 %: between ≈ 3 × 10² and 2 × 10³ | ODE sweep, 26 points |

Other pairs (K, turnovers per round) that give 57 % in round 1, and what they give next (`K_scan_matched_to_round1`):

| K | turnovers per round | round 2 | round 3 |
|---|---|---|---|
| 4 | 1,689,000 | 100 % | 100 % |
| 10 | 10,190 | 99.995 % | 100 % |
| 30 | 257 | 99.8 % | 99.999 % |
| 100 | 27 | 98.4 % | 99.94 % |
| 300 | 8.2 | 95.3 % | 99.49 % |
| 1,000 | 3.8 | 91.0 % | 98.1 % |
| 10,000 | 1.9 | 84.9 % | 94.7 % |

So the three numbers pin the toy down: round 1 fixes a curve of (K, turnovers) pairs, round 2 picks K ≈ 73 on it,
and round 3 then comes out above 99.5 % without being fitted. The honest reading: **random pairing fails by orders of
magnitude**; this toy needs a pairing constant about 18 times the random value (K ≈ 73) to get Soai's shape. Blackmond's review notes that the bulky substrate of the 2003 work amplifies more than the random
pairing model predicts.

## The three layers

**Layer 1: Blackmond–Brown dimer model** (Blackmond et al., J. Am. Chem. Soc. 2001, 123, 10103; review
arXiv:1909.13015, scheme 8 and fig. 3). All product sits in pairs formed at random (K = 4). Same-hand pairs copy
their hand, the mixed pair is inactive. So dR/dS = R²/S², and **1/S − 1/R is conserved**. With the product grown by
a factor F (F = 1 + turnovers) from ee₀, the final ee E solves E / (1 − E²) = ee₀ F / (1 − ee₀²): exact, no solver.

**Layer 2: our labelled toy.** The same structure with a free pairing constant K = z²/(xy), where x, y, z are the
one-hand, mirror-hand and mixed pairs (Kagan's ML2 mixture with ee_L = the pool's ee and g = 0). The ee of new product
is Kagan's g = 0 curve, so d ln(ee)/d ln(amount) = β(ee, K) = z/(1 − z). We integrate this one equation. Rounds: each
round's **whole** product seeds the next and grows by 1 + N (N = turnovers per round), so round k ends at an amount
(1 + N)ᵏ; the ee only depends on the total growth. **K and N are fitted toy numbers**, solved so that round 1 gives
57 % and round 2 gives 99 %. N is a model parameter, **not** Soai's experimental ratio.

**Layer 3: Buhse–Micheau monomer-active model** (T. Buhse, J. Mex. Chem. Soc. 2005, 49, 328, reactions [1′]–[10′];
the same group as Rivera Islas et al., PNAS 2005, 102, 13743). A different published picture: the single molecule
(monomer) copies itself, and pairing only removes molecules:

* A + Z → one hand, A + Z → mirror hand (k0, slow racemic background)
* A + Z + one hand → 2 one hand, and the mirror-hand copy (k1)
* one hand + mirror hand ⇌ mixed pair (k2 forward, k3 back)
* one hand + one hand ⇌ same-hand pair, and the mirror-hand pair (k4 forward, k5 back)

Fig. 1 parameter set in model units: k0 = 10⁻⁶, k1 = 1, k2 = 10⁵, k3 = 10, k4 = 10, k5 = 10; A = Z = 1, seed 0.1
(Buhse calls these "arbitrarily chosen"). The printed eq. 15 has k1·A·Z·R in the equation for the mirror hand; it
must be k1·A·Z·S (a typo; with it the model is not mirror-symmetric). The final ee counts every molecule of each
hand, free or paired.

### The round-off pitfall (why "racemic stays racemic" is a test)

An exactly racemic start must stay exactly racemic: nothing in the model prefers a hand. Written hand by hand
(R, S, RR, SS, RS) and solved with a stiff solver that estimates its own Jacobian (LSODA), the same model can end
far from 0 from numerical error alone: **45 % ee** with our tolerances (rtol 1e-10), 62 % (of the mirror hand) with
rtol 1e-8, about 0 with rtol 1e-12 (`naive_tolerance_scan` in the summary). The number means nothing; the drift
does. We write the equations in
sums and differences (σ = R + S, δ = R − S, and the same for the pairs). Every term of the difference equations is
proportional to a difference, so δ = 0 stays exactly 0, and tiny starts such as 10⁻⁷ are resolved with relative,
not absolute, precision. We also pass the analytic Jacobian (checked against finite differences in the tests).

## Figures

All in `results/`, each as `_light.png` and `_dark.png`, subtitled "our toy model: simplified, trend only".
One hand is burnt orange (solid), the mirror hand teal (dashed or hatched), random pairing grey.

| file | what it shows |
|---|---|
| `rounds_staircase` | the three rounds on a log axis (so 0.00005 % is visible): fitted toy, K = 4 with the same turnovers, Soai's 2003 numbers; right panel: the mirror-hand share left |
| `ee_vs_turnover_fan` | layer 1: ee against turnovers for starts of 0.00005, 0.01, 0.5 and 5 %, Blackmond's two statements, and the fitted toy |
| `layer3_bifurcation` | layer 3: final ee against k2 (how fast mixed pairs form), two starts, the Fig. 1 point |
| `erosion_vs_amplification` | plain copying at 90 % selectivity erodes 100 → 90 → 81 (SCI p. 10); the fitted toy (perfectly selective pairs) climbs from 0.00005 %; dotted: the same toy with 90 % selective pairs climbs too, then levels off near 90 % |
| `two_populations` | the amount of each hand over three rounds in the fitted toy (log scale) |

## Files for the page and the video

* `results/amplifier_summary.json`: `soai_2003_pct`, `layer1` (statements and the fan), `toy_rounds` (K, turnovers,
  ee per round, the K scan), `k4_fails`, `layer3` (Fig. 1 check, k2 sweep, racemic test), `erosion_pct`, `notes`,
  `label`, `status`.
* `results/rounds.json`: per round (0–6) of the fitted toy: `ee_pct`, `mirror_hand_share_pct`, the amount of each
  hand (start = 1 in total) and its log10, and Soai's 2003 value for rounds 0–3 (the last is a lower bound).

## Every simplification

| simplification | what it means |
|---|---|
| Two published toy models, not the real mechanism | proposals in the literature include active dimers, tetramers (Denmark and Houk: an "SMS" tetramer) and a transient hemiacetal catalyst (Trapp); SCI pp. 14–16 says two detailed mechanisms remain |
| Layer 1/2: all product sits in pairs, pairs are always in equilibrium, mixed pairs are fully inactive | real aggregates can be larger and slower |
| Layer 2: one constant K for every ee, and rounds that differ only in how much product they make | K is not a measured constant; the real runs differ in more than that |
| Layer 2: K and turnovers per round are fitted to two of Soai's numbers | it is a curve fit with two numbers through two points; round 3 is the only real test, and it is weak (any K below about 300 clears 99.5 %) |
| Layer 3: Buhse's "arbitrarily chosen" rate constants in model units | the shape is the point, not the values |
| Deterministic equations: no molecular noise | the 37 runs with no chiral additive (19 one hand, 18 mirror hand, ee 15–91 %; S03b) need noise; see the mirror-race experiment |
| No background racemic reaction in layers 1 and 2 | it would slow the climb |
| Layers 1-2: a same-hand pair makes only its own hand (ee_max = 100 %) | with 90 % selectivity the fitted toy still climbs from 0.00005 % but levels off near 90 % (89.97 %, `selectivity_check`), not 99.98 % |
| Amounts in `rounds.json` start at 1 and the whole product seeds the next round | not Soai's amounts. Sources disagree on what the published factor of about 630,000 measures (the amount of product, or the ratio of the two hands), so we do not compare with it |

What we do not claim: that K = 73 or 43 turnovers per round describe the real reaction; that any layer reproduces
the real Soai mechanism; anything about the origin of life (the Nobel Committee: Frank's model "is not an answer to
the origin of biological homochirality"); "99.99 %" (not in the primary papers; Soai reports >99.5 % ee).

## Sources and constants

Every constant is in `amplifier/constants.py` with its source, "choice" or "fitted toy number".

| what | value | source |
|---|---|---|
| Soai 2003 series | 0.00005 → 57 → 99 → >99.5 % ee | Sato, Urabe, Ishiguro, Shibata, Soai, Angew. Chem. Int. Ed. 2003, 42, 315 (doi:10.1002/anie.200390105); Nobel scientific background (SCI) p. 12, Fig. 7 entries 6–8 |
| Layer 1 model and statements | K = 4, mixed pair inactive; 0.01 % + 10⁴ turnovers → just over 60 %; 0.5 % → near homochiral | Blackmond et al., J. Am. Chem. Soc. 2001, 123, 10103; D. G. Blackmond, "Autocatalytic models for the origin of biological homochirality", arXiv:1909.13015 |
| Layer 2 K, turnovers per round | 73, 43 | **fitted toy numbers** (to rounds 1 and 2), recomputed on every run |
| Layer 3 model and Fig. 1 parameters | k0 = 10⁻⁶, k1 = 1, k2 = 10⁵, k3 = k4 = k5 = 10; A = Z = 1, seed 0.1; 10⁻⁵ % → about 85 % | T. Buhse, J. Mex. Chem. Soc. 2005, 49, 328 (open access, CC BY-NC); eq. 15 typo fixed |
| Erosion | ee_max = 90 %: 100 → 90 → 81 | SCI p. 10 |
| Absolute asymmetric synthesis (context only) | 37 runs, 19 / 18, ee 15–91 %; Singleton and Vo: 54 runs, 27 / 27 | Soai et al., Tetrahedron: Asymmetry 2003, 14, 185; Singleton and Vo, Org. Lett. 2003, 5, 4337 |
| integration end time 10⁴; k2 sweep 10 to 10⁶, 26 points; starts 10⁻⁵ % and 0.1 %; 5 and 50 turnovers for the K = 4 demo | | choice |

## What each file does

| file | in plain words |
|---|---|
| `amplifier/model.py` | layer 1 exact formulas, layer 2 integrator and fit, layer 3 equations (sum/difference form, analytic Jacobian) and the naive version for the pitfall |
| `amplifier/constants.py` | every number we put in |
| `amplifier/figures.py` | the figures, light and dark |
| `amplifier/run_all.py` | runs everything and writes `results/` |
| `tests/test_amplifier.py` | the exact checks: Blackmond's two numbers, the golden ratio case, the conserved quantity along a direct simulation, 1.7 million, the K = 4 limit of the integrator, the fit, Buhse's 85 %, racemic stays racemic, mirror symmetry, the k2 switch, two codings agree, the Jacobian, the 90 %-selective plateau (exact for K = 4: √0.8 = 89.44 %), the naive drift depends on tolerances |
