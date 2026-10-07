# Kagan's curve (Chemistry 2026, experiment 2)

> **Educational demo made to show an open-source tool. Toy model, not research.**
> Every number here is **our toy model, trend only**, in dimensionless units. It is the textbook model the Nobel
> Committee itself presents; it is not a fit to any measured reaction.

The 2026 Nobel Prize in Chemistry went to Henri B. Kagan and Kenso Soai "for the discovery of non-linear effects and
autocatalysis in asymmetric organic synthesis". In 1986 Kagan showed that a catalyst made from a chiral ligand that is
only partly one hand can give a product that is *purer* (higher ee) than the ligand. This folder computes his simplest explanation, the ML2
model, in closed form.

ee (enantiomeric excess) = (one hand − mirror hand) / all, in per cent: 75:25 is 50 % ee. "Purer" below means a
higher ee: a bigger lead of one hand.

Own code, MIT licence. CPU only; runs in about 2 seconds. Python 3.11 with NumPy, SciPy, Matplotlib.

## Run it

From `2026/chemistry/kagan-curve/`:

```bash
python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python -m kagan.run_all          # results/kagan_summary.json + figures
python -m pytest -q tests        # 19 tests, under a second (one runs kagan.js with node)
```

## The idea in plain words

A metal atom holds **two** ligand molecules. Each ligand is one hand or the mirror hand. So there are three kinds
of catalyst: a **one-hand pair**, a **mirror-hand pair** and a **mixed pair** (one of each; chemists call it
heterochiral or "meso"). A mixed pair is its own mirror image, so it makes both hands of product equally.

If the mixed pair is **slow or inactive**, it soaks up the minority hand of the ligand. The catalysts that are left
are purer than the ligand, and the product ee lies **above** the straight line: a positive non-linear effect. If the
mixed pair is **faster**, the product ee sags **below** the line: a negative non-linear effect.

## The example (our toy model, trend only)

The Nobel popular information (figure 4) uses this example; we redraw it ourselves (`results/kagan_pie_*.png`):

| step | one hand | mixed | mirror hand |
|---|---|---|---|
| ligand | 75 % | | 25 % |
| pairs on the metal (random pairing, K = 4) | 56.25 % | 37.5 % | 6.25 % |
| pairs that work (mixed pair inactive, g = 0) | 90 % | | 10 % |
| product ee | **80 %** from a ligand of 50 % ee | | |

The Nobel figure rounds the middle row to 56/38/6. Our closed form gives the exact values (tested).

## The equations

Fractions of all complexes: x = one-hand pair, y = mirror-hand pair, z = mixed pair.

* x + y + z = 1 and x − y = ee_L (ee of the ligand)
* K = z² / (x y). Random pairing gives K = 4 (a mixed pair can form two ways)
* so (4 − K) z² + 2K z − K (1 − ee_L²) = 0. We use the root
  z = K (1 − ee_L²) / (K + √(K (4 (1 − ee_L²) + K ee_L²))), which is the same root written so that K = 4 needs no
  special case
* β = z / (x + y) = z / (1 − z); g = (rate of a mixed pair) / (rate of a same-hand pair)
* **ee_prod = ee_max · ee_L · (1 + β) / (1 + g β)** (SCI eqs. 2–3, p. 7). Equivalent: ee_max · ee_L / (1 − z + g z)

Checked against two independent write-ups: the Nobel scientific background (SCI eqs. 1–3) and Buhse,
J. Mex. Chem. Soc. 2005, 49, 328, eqs. 3–7 (open access).

Shapes: g = 1 is the straight line ee_prod = ee_max · ee_L; g < 1 bulges above it; g > 1 sags below it.
g = 0 is the "reservoir" reading: the mixed pairs are an inactive sink.

## What the tests check (exact, not fitted)

`tests/test_kagan.py`:

* the pie: 75:25 → 56.25 / 37.5 / 6.25 % → 90:10 → 80 % ee, to 1e-12
* K = 4 gives z = (1 − ee_L²)/2, and with g = 0 the closed form ee_prod = ee_max · 2 ee_L / (1 + ee_L²)
* the constraints x + y + z = 1, x − y = ee_L, z² = K x y hold for K from 0.01 to 1000; the closed form equals a
  numerical root finder
* g = 1 is exactly the straight line for any K; g < 1 is above it and g > 1 below it
* ee_prod never exceeds ee_max (SCI p. 8 says the same for ML2)
* K → ∞ with g = 0 (the mixed pair forms irreversibly) gives ee_prod = ee_max for every ee_L > 0 (SCI p. 7)
* the erosion staircase 100 → 90 → 81 → 72.9 → 65.61 (see below)

`tests/test_kagan_js.py` runs `kagan.js` with node and checks it against Python to 1e-9 (skipped if node is absent).

## Copying alone erodes (the committee's contrast, SCI p. 10)

A catalyst that copies itself but has **no** non-linear effect, and whose all-one-hand form gives 90 % ee, loses
ee every round: **100 → 90 → 81 → 72.9 → …** % ee (`erosion` in the summary). Soai's amplifier
(`../soai-amplifier/`) feeds Kagan's curve back on itself and climbs instead; its figure
`erosion_vs_amplification` puts the two staircases side by side.

## Files

| file | in plain words |
|---|---|
| `kagan/model.py` | the closed form: mixed fraction z, complexes, β, ee_prod, the pie, the erosion staircase |
| `kagan/constants.py` | every number we put in, with its source or "choice" |
| `kagan/figures.py` | the figures, light and dark |
| `kagan/run_all.py` | writes `results/kagan_summary.json` and the figures |
| `kagan.js` | the same model for the interactive page: pure functions, no dependencies (`window.Kagan` in a browser, `require` in node) |
| `results/kagan_summary.json` | pie check, curve family (K = 4, g = 0 … 10), g = 0 curves for K = 1 … 1000, erosion |
| `results/kagan_curves_{light,dark}.png` | ee_prod against ee_L: bulge, straight line, sag |
| `results/kagan_pie_{light,dark}.png` | our own drawing of the 75:25 example |

`kagan.js` API (all ee values as fractions 0–1 unless the name ends in Pct): `mixedFraction(eeL, K)`,
`complexes(eeL, K)`, `beta(eeL, K)`, `eeProd(eeL, K = 4, g = 0, eeMax = 1)`, `curve(K, g, eeMax, n)`,
`pie(oneHandLigandPct = 75, K = 4, g = 0)`, `erosion(eeMax = 0.9, rounds = 6)` (per cent). `K = Infinity` is allowed.

## Every simplification

| simplification | what it means |
|---|---|
| Exactly two ligands per metal (ML2) | Kagan's group also treated ML3 and ML4 and the reservoir effect (K94; SCI pp. 7–8). ML3 can give a "hyperpositive" effect, which ML2 cannot: ML2 never exceeds ee_max |
| The pairs are in equilibrium with one constant K | real catalysts can be slower to equilibrate, or other species can form |
| One rate per kind of pair (g) and no change with conversion | SCI p. 9 notes that the rate and ee_prod can change with conversion |
| ee_max = 100 % in the figures | the curves scale linearly with ee_max |
| The mixed pair makes both hands equally | true for a heterochiral ML2 complex by symmetry |
| No real reaction, ligand or metal | none is named or modelled; K and g are free numbers |

What we do not claim: that these curves fit Kagan's 1986 measurements (we do not plot his data), or that a specific
reaction has these K and g. Noyori's amino-alcohol case (15 % → 98 %, SCI p. 7) is a reservoir case; we do not fit it.

## Sources and constants

Every constant is in `kagan/constants.py`.

| what | value | source |
|---|---|---|
| ML2 equations | eqs. above | Nobel Committee, scientific background 2026 (SCI) eqs. 1–3, p. 5–7; T. Buhse, J. Mex. Chem. Soc. 2005, 49, 328, eqs. 3–7; Puchot … Kagan, J. Am. Chem. Soc. 1986, 108, 2353 (K86) |
| K = 4 for random pairing | 4 | combinatorics (a mixed pair forms two ways); the split the Nobel popular figure uses |
| pie | 75:25 → 56/38/6 → 90:10 → 80 % | Nobel popular information 2026, figure 4 (numbers only; our own drawing) |
| erosion | ee_max = 90 %, 100 → 90 → 81 | SCI p. 10 |
| g values 0, 0.1, 0.5, 1, 2, 10; ee_max = 100 %; 51 points | | choice |
