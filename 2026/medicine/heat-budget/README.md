# Heat budget: how many neurons can one degree of warming buy you?

> **Educational demo, toy model. Not research, not for lab or clinical use.**
> It reuses the light-and-heat simulator in [`../simulator`](../simulator) to ask one plain question
> for an explainer video: if the brain may warm by at most one degree, how many neurons can the light
> switch on, and how fast can it drive them?

Own code, MIT licence. CPU only, no network at run time. Python 3.11, NumPy,
SciPy, Matplotlib, with the same pinned versions as the simulator (`requirements.txt` includes
`../simulator/requirements.txt`).

## Run it

From `2026/medicine/heat-budget/`:

```bash
python3.11 -m venv ../.venv && . ../.venv/bin/activate && pip install -r requirements.txt
python -m heat_budget.run_all                # everything, plus 60 frames at 1920x1080
python -m heat_budget.run_all --vertical     # also 60 frames at 1080x1920
python -m heat_budget.frames --colour 590    # frames only, another colour or --limit
python -m pytest -q tests                    # 8 tests
```

It reads the simulator's cached light maps (`../results/light_fibre200um_*nm.npz`); if one is missing
it reruns that Monte Carlo with the simulator's own settings first.

## Method in six lines

1. Light: the simulator's photon Monte Carlo maps (200 um, NA 0.22 fibre; 470, 590, 635 nm).
2. Heat: the simulator's Pennes model is linear in power, so one solve at 1 mW per colour is scaled; a pulse train is estimated as the steady warming of its average power plus one pulse's rise (an upper estimate, checked by a test against a full time-stepped train).
3. Recipe: for each switch, a grid of pulse width x rate x peak power; score = share of pulses answered by exactly one spike in the simulator's neuron, for a neuron 0.5 mm and 1.0 mm below the tip.
4. Best recipe: the fastest rate that still follows (at least 95 %, and every slower rate too) while the warming stays under the limit (0.5, 1, 2 C).
5. Population: neurons at 92,000 per mm^3 fill the whole light grid; each gets a lognormal expression level; a neuron counts as recruited when light x expression reaches 3 mW/mm^2.
6. Count recruited neurons as the continuous fibre power rises, and divide by the power and by the warming at the hottest point.

## Results (toy model; caveats next to each number)

Rerun on 2026-10-06 on the fixed simulator (after the independent review): all light is now counted
inside the tally (the grid grows to about 45 mm), the heat box is about 10 Pennes lengths wide, and
the neuron uses a converged 0.01 ms step. The headline pair is **470 and 590 nm**; 635 nm is shown
only as a labelled toy upper bound, below.

**Neurons recruited at 1 C of warming (continuous light, expression spread 0.5; toy model, one
threshold of 3 mW/mm^2 borrowed from ChR2 for both colours, heat model 1.5-3x hotter than Stujenske 2015):**

| colour | power for 1 C | neurons at 1 C | per mW | spread 0.25 / 1.0 |
|---|---|---|---|---|
| 470 nm | 2.61 mW | **16,441** | 6,303 | 13,419 / 31,329 |
| 590 nm | 3.84 mW | **31,136** | 8,117 | 25,010 / 65,396 |

Caveats, all of them load-bearing:
- One activation threshold (3 mW/mm^2) and one expression law (lognormal, median 1) for both colours.
- Both colours use ChR2's light sensitivity: the amber advantage comes only from the wavelength (less
  absorption, so less heat per mW), not from a modelled amber switch.
- The heat model runs about 1.5-3x hotter than Stujenske et al. 2015's (see the simulator README).
  So the power allowed per degree, and the counts, may be underestimates for blue and amber.
- "Per degree" is not a constant: recruitment grows faster than linearly with warming. At 0.5 C,
  470 nm recruits 6,185 neurons; at 2 C it recruits 42,851 (21,426 per degree). The full curves are
  in `results/recruitment.json`.
- The spread of expression matters about as much as the colour does between blue and amber: going
  from spread 0.5 to 1.0 roughly doubles every count.

**635 nm (red): a toy upper bound only, not a result.** The same rules give 24.1 mW for 1 C and
2.76 million neurons (spread 0.25 / 1.0: 2.15 / 5.87 million). Do not read this as a prediction:
- **the red result ignores absorption outside blood, so it looks better than it is**: red light
  travels farther and heats less here than it would in a real brain;
- no 635 nm switch is modelled (ChR2's sensitivity and threshold are borrowed);
- the uniform block is far bigger than a real cortex, which is a thin layered sheet: at this power
  red light is above threshold well outside any cortex.
The figure draws red dashed and labelled "toy upper bound only"; `summary.json` keeps it under
`toy_upper_bound_only`, apart from the headline.

**Best pulse recipe per switch** (`results/recipe_best.csv`; toy result, read the order, not the
numbers). At 0.5 mm the heat limit hardly matters, because the light there is bright enough at low
power (ChR2 100 / 150 / 150 Hz, Chronos 150 Hz, ChrimsonR 60 Hz at 0.5 / 1 / 2 C). The table shows
the neuron at 1.0 mm, where it does matter:

| switch (neuron 1.0 mm deep) | 0.5 C | 1 C | 2 C |
|---|---|---|---|
| ChR2 (Williams 2013), 470 nm | 40 Hz (2 ms, 11.3 mW, 0.45 C) | 60 Hz (2 ms, 16 mW, 0.88 C) | 60 Hz (same) |
| Chronos (simplified), 470 nm | 60 Hz (2 ms, 8 mW, 0.44 C) | 150 Hz (2 ms, 8 mW, 0.99 C) | 150 Hz (2 ms, 11.3 mW, 1.40 C) |
| ChrimsonR (simplified), 590 nm | 40 Hz (2 ms, 16 mW, 0.42 C) | 40 Hz (same) | 60 Hz (2 ms, 45 mW, 1.65 C) |

Before the simulator fix, ChR2 reached 80 Hz at 2 C; with the converged neuron step 80 Hz no longer
follows at any power the 2 C limit allows. The other entries did not change.

Read the rates as an ordering, as the simulator's README asks: they depend on the pulse count, the
neuron's calibration and the tested rate grid (no rate between 150 and 200 Hz was tested here). At
these brighter levels the simplified ChrimsonR follows faster than in the simulator's 3 mW/mm^2 test
(10 Hz there), which shows how protocol-dependent the speed axis is; real ChrimsonR follows at least
20 Hz, comparable to ChR2(H134R) (Klapoetke 2014). The toy neuron also has a resonance where 1:1
firing returns at high rates (for example ChR2 at 130-150 Hz above its first failure): a resonance
of this toy cell, not of the light switch, so a recipe only counts if every slower rate also follows.

## Outputs (`results/`)

| file | what |
|---|---|
| `recipe_{chr2,chronos,chrimsonr}_{light,dark}.png` | heat map per switch: rate (x), pulse width (y), colour and number = best % of 1:1 pulses within 1 C; outline = where 95 % following fits under 1 C; star = best recipe; two panels (neuron 0.5 and 1.0 mm deep) |
| `recipe.csv` | every grid point: switch, depth, width, rate, peak power, duty, light at the neuron, score, warming estimate, within each limit |
| `recipe_best.csv` | the best recipe per switch, depth and limit |
| `recruit_vs_warming_{light,dark}.png` | neurons recruited versus fibre power and versus warming, 470 and 590 nm with the expression-spread band; 635 nm dashed and labelled as a toy upper bound only |
| `recruitment.json` | power grid, warming grid, sampled and expected counts per colour and spread, numbers at each limit (about 25 KB) |
| `recruit_frames/frame_0000-0059.png` | 3D scatter, 1920x1080, dark theme, 470 nm, power rising from 0 to the 1 C limit (git-ignored: about 16 MB; rebuild with `python -m heat_budget.frames`) |
| `recruit_frames_vertical/` | the same at 1080x1920 (`--vertical`; git-ignored) |
| `summary.json` | best recipes, headline numbers (470, 590 nm), the 635 nm toy upper bound kept apart, caveats, timings |

## Run times on this machine

Intel Core i5-8500 (6 cores), macOS, Python 3.11, measured 2026-10-06 on the fixed simulator while
other heavy jobs shared the machine (load average 50-250 on 6 cores), so an idle machine should be
several times faster. Exact values of the last run are in `results/summary.json`.

| step | wall time |
|---|---|
| heat model: 3 steady solves + 3 single-pulse transients (10 ms at 0.05 ms steps) on the extended grid | 63 s |
| recipe: 3 switches x 2 depths x 5 widths x 9 rates x 17 powers, 20 pulses each, neuron at 0.01 ms, 5 worker processes | 765 s |
| recruitment: 3 colours x 3 spreads, up to 15 million sampled neurons, figure | 20 s |
| 60 frames 1920x1080 / 60 frames 1080x1920 | 9 s / 8 s |
| **whole `run_all --vertical`** | **14 min 46 s wall** (23 min 19 s of CPU time over the worker processes) |
| `pytest` (8 tests) | 78 s |

## What is real and what is a toy

| real (from a published source, see SOURCES.md and ../simulator/SOURCES.md) | toy (our simplification or choice) |
|---|---|
| Mouse cortex neuron density 92,000 per mm^3 (Keller et al. 2018 review, Table 1, citing Schüz & Palm 1989) | Density is uniform everywhere; real density varies by layer (the review reports up to about 200,000 cells/mm^3 at the layer-4 excitatory peak) and the review's within-region spread between estimates averages 43,800/mm^3 |
| Everything the simulator takes from sources: brain scattering and blood absorption, thermal constants, ChR2 photocycle (Williams 2013), Chronos and ChrimsonR off-times (Klapoetke 2014), Hodgkin-Huxley equations | Tissue is an infinite homogeneous block filling the simulator's light grid (25 um cells to 6 mm, then growing cells to about 45 mm); no layers, no vessels, no skull, no edge of the cortex |
| 3 mW/mm^2 as a level "in the range of the EPD50 for various opsins" (Stujenske et al. 2015) | One activation threshold for every neuron and colour, scaled by a lognormal expression level (median 1, spread 0.5; 0.25 and 1.0 shown); "recruited" means above threshold, not a simulated spike |
| | Every switch borrows ChR2's light sensitivity; no 635 nm switch; no absorption outside blood, so red looks better than it is (635 nm is reported only as a labelled toy upper bound) |
| | Warming of a pulse train = steady warming of its average power + one pulse's rise (an upper estimate for a long train); heat limits 0.5 / 1 / 2 C at the single hottest point are illustrative, not a safety standard |
| | Recipe neuron on the fibre axis at 0.5 or 1.0 mm; 20 pulses per train; widths 0.5-10 ms; rates 10-200 Hz; peak powers 0.25-64 mW in steps of x1.41; grid points with more than 30 mW/mm^2 at the neuron are skipped (kept from the first run: the old fixed 0.025 ms Euler step was not accurate there; the grid stays comparable) |
| | Recruitment uses continuous light; the frames show 1 in 40 neurons inside a 1 mm radius, 2 mm tall cylinder, while the printed count is for the full population |
| | Neuron positions are drawn per grid cell of the light map, and each neuron gets its cell's light level (no interpolation; the growing cells far from the tip average the light over larger volumes) |

## Licences

All code here is MIT. Keller et al. 2018 is CC BY 4.0; one number and two summary statements are
restated with citation. Everything inherited from the simulator keeps the licences listed there.
