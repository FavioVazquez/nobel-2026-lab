# Light-and-heat simulator (educational demo, toy model)

> **Educational demo, toy model.** Not research, not a design tool, not for any lab or clinical use.
> It stacks simple textbook models with published parameters so a video can show, in numbers, why
> optogenetics experimenters weigh light reach, tissue heating and spike speed against each other.

Own code, MIT licence. CPU only, no network at run time. Needs Python 3.11, NumPy, SciPy, Matplotlib.

## Run it

From `2026/medicine/`:

```bash
python3.11 -m venv .venv && . .venv/bin/activate && pip install -r simulator/requirements.txt && python -m simulator.run_all
python -m pytest -q tests          # 21 tests, no NEURON needed
python -m simulator.run_all --quick  # small photon counts, smoke test
```

Everything lands in `2026/medicine/results/`:

| file | what |
|---|---|
| `light_depth_profile_{light,dark}.png` | light vs depth for the three colours |
| `heat_transient_{light,dark}.png` | warming over 10 s, continuous vs pulsed |
| `following_{light,dark}.png` | share of pulses answered by exactly one spike vs pulse rate, headline speed ringed, the toy cell's resonance window shaded |
| `tradeoff_{light,dark}.png`, `tradeoff.csv` | reach and heat per colour (470, 590, 635 nm), speed per switch |
| `light_fibre200um_{470,590,635}nm.npz` | cached light maps (fluence per watt on the r-z grid) |
| `run_summary.json` | every number above, the published comparison values and the timings; `tradeoff_per_switch_legacy` keeps the earlier per-switch table |

## What each file does

| file | in plain words |
|---|---|
| `light.py` | Shoots photon "packets" out of a fibre tip into brain tissue and tracks where they scatter and get absorbed (Monte Carlo). Gives a light map per colour (470, 590, 635 nm) and a depth-profile figure. 25 um cells to 6 mm, then cells growing to about 45 mm, so all the light is counted. Checks itself against the exact transport-theory decay rate (and reports diffusion theory's). |
| `heat.py` | Turns the absorbed light into heat and solves the Pennes bioheat equation (heat spreads by conduction, blood flow carries it away). Steady state and time courses for continuous light and pulse trains. |
| `opsin.py` | Four-state models of light-gated channels: two published ChR2 parameter sets, plus two **simplified** stand-ins (Chronos, ChrimsonR) that are the ChR2 model with only the closing speed changed to match published off-times. Integrated piecewise across light pulses. |
| `neuron.py` | A Hodgkin-Huxley neuron driven by the channel current (2nd-order Runge-Kutta, 0.01 ms step, converged); finds the headline speed: the last tested pulse rate before the first rate where pulses stop getting exactly one spike. |
| `tradeoff.py` | One table (`tradeoff.csv`) and one figure: reach per mW and warming per mW for each colour, fastest 1:1 rate for each switch. Every switch borrows ChR2's light sensitivity, so reach and heat depend on the colour only; showing them per switch would repeat one number three times. `python -m simulator.tradeoff` rebuilds both from the cached results. |
| `run_all.py` | Runs everything, writes figures (light and dark theme, 1600 px wide), CSV, cached light maps (`.npz`) and `run_summary.json` with all numbers and timings. |
| `inputs/` | The only inputs, as small CSVs with source comments. |
| `SOURCES.md` | Every parameter, its source URL and whether it was verified in the source text. |

## Run times on this machine

Intel Core i5-8500 (6 cores), macOS, Python 3.11, single process. See `results/run_summary.json` for
the exact values of the last run.

Measured 2026-10-06 (after the review fixes) while other heavy jobs shared the machine (load average
50-250 on 6 cores), so an idle machine should be several times faster:

| step | wall time |
|---|---|
| light, 200 000 photons each at 470 / 590 / 635 nm | 32 s / 32 s / 268 s (333 s total) |
| light, two extra runs for the heating comparison (532 nm 62 um, 445 nm 200 um) | 11 s |
| heat: steady states, 120 s transient, three 10 s pulse-train transients (5 steps per light-on and light-off phase) | 237 s |
| switches + neuron (calibration, 4 switches x 18 rates x 20 pulses at 0.01 ms, plus the same run at 0.005 ms as a convergence check) | 666 s |
| **whole `run_all`** | **20 min 52 s wall** (10 min 24 s of CPU time) |

635 nm is the slowest because red light is barely absorbed, so each photon scatters thousands of times
(and the tally now follows it out to about 45 mm instead of killing it at 10.5 mm).

## Results in one breath

All numbers are toy-model outputs for a 200 um, NA 0.22 fibre (`results/tradeoff.csv`,
`results/run_summary.json`):

* **Light.** The Monte Carlo's far-field decay matches the exact transport-theory decay (P_399
  plane-wave eigenvalue, `light.transport_decay`) within 0.1 % at 470 and 590 nm and 0.4 % at 635 nm.
  Diffusion theory itself is 3.4 % / 3.1 % / 0.3 % too steep here, which is diffusion's own bias, not
  Monte Carlo error. All launched light is absorbed inside the tally at every colour (1.000; before
  the fix only 0.68 of the 635 nm light was). Tissue lit above 3 mW/mm^2 at 10 mW: 0.92 mm^3 at
  470 nm, 1.08 mm^3 at 590 nm, 3.58 mm^3 at 635 nm (no non-blood absorption, so red reach is overstated).
* **Heat.** Steady warming at the hottest point: 0.383 C per mW at 470 nm, 0.261 at 590 nm, 0.042 at
  635 nm (the last one is low partly because the model has no non-blood absorption). The box now
  reaches about 45 mm (about 10 Pennes lengths). Perfusion over its 0.004-0.012 /s range moves the
  peak by +2.3 % / -1.7 % at 470 nm, +3.1 % / -2.2 % at 590 nm and +10.4 % / -6.5 % at 635 nm (low /
  high perfusion against the 0.008 /s mid-point); the old 6 mm box hid part of this (it gave about 3 %
  in total at 470 nm). Same peak power, less light on average: pulsing 10 mW at 470 nm gives 1.96 C at
  50 % duty (5 mW average), 0.60 C at 10 % duty (1 mW average) and 3.45 C after 10 s continuous.
* **The trade-off figure**: in this toy model, colour sets reach and heat; closing speed sets
  following. The figure itself says that every switch shares ChR2's light sensitivity and one
  3 mW/mm^2 threshold, so the 590 and 635 nm advantages come only from wavelength.
* **Speed** (2 ms pulses at 3 mW/mm^2, 20 pulses; toy result, read the order, not the numbers). The
  headline speed is the highest tested rate up to which every tested rate follows: the first failure
  ends the run. ChR2 (Williams 2013) 50 Hz, ChR2 (PyRhO fit) 60 Hz, simplified Chronos 160 Hz,
  simplified ChrimsonR 10 Hz. "Follows" means at least 95 % of the 20 pulses give exactly one spike, so
  exactly one miss is allowed (ChR2 Williams at 50 Hz and Chronos at 160 Hz each have one miss).
  The two ChR2 sets agree for 2 ms pulses only (see the toy table).
* **Resonance window.** Above their first failure, both ChR2 curves follow 1:1 again at 130-150 Hz.
  That is a resonance of this toy cell (the squid-axon model), not of the light switch, and the figure
  marks it. It does not count towards the headline speed.
* **Neuron time step.** The neuron now uses the explicit midpoint rule (2nd-order Runge-Kutta) at a
  fixed 0.01 ms step. The earlier forward-Euler 0.025 ms step was not converged (ChR2 Williams moved
  from 60 to 50 Hz when the step was halved). At 0.01 ms the headline rates, and every following fraction up to
  them, equal those at 0.005 ms for all four switches; the only fraction that moved is PyRhO's at
  110 Hz (0.45 to 0.35), far above its first failure (`following_dt_check` in `run_summary.json`).

**Where the toy disagrees with the published reference (Stujenske et al. 2015).** For their
532 nm / 62 um / 10 mW case the model gives a 3.5 C slice-averaged plateau (they report about 2.2 C),
6.5 C in the hottest voxel (4.1 C) and 5.3 mm^3 above +1 C (roughly 1 mm^3). At 445 nm it gives
0.94 C/mW at the hottest point (their model 0.35, the measurement they cite 0.42). Pulsed 473 nm light
at 50 % duty gives 2.0 C at 10 mW where they predict 0.5-0.9 C for 5-10 mW. So this toy runs roughly
1.5-3x hotter. The lever is the absorption: a closed-form point-source estimate with our absorption
(an assumed 3 % blood volume) already gives 0.78 C/mW at 445 nm (review B, section 1b), while
perfusion moves the peak by only a few % and the domain size by under 1 % at 532 nm. Their absorption
comes from Johansson 2010, which we could not read. Grid size is not a reason: Stujenske report that
30 um voxels "gave very similar results to 10 um". Only the time to reach steady state agrees closely
(0.7 % more warming from 60 s to 120 s; they report under 5 %).

**The speed numbers are fragile.** With 10-pulse trains instead of 20, or a larger photocurrent, the
limits move a lot (B-report, first run). Klapoetke et al. 2014 report real ChrimsonR neurons giving
"fast, reliable red-light driven spiking at frequencies of at least 20 Hz ..., comparable to the
blue-light spiking performance of the commonly used ChR2 (H134R)" (40-pulse trains, 2 ms pulses,
5 mW/mm^2, red light), and Chronos spiking that "perfectly replicated electrically driven spiking
between 5 to 60 Hz" (530 nm, 2 ms pulses, 40-pulse trains). The toy uses 470 nm (590 nm for the
ChrimsonR stand-in), 20 pulses, 3 mW/mm^2 and a squid-axon neuron, so its 10 Hz for ChrimsonR is a
limit of the simplified stand-in, not a measurement. Read the speed axis as an ordering by closing
speed (faster closing, faster following), not as numbers.

**Absorption outside blood.** No open source giving a background (non-blood) absorption coefficient
for brain at 470, 590 and 635 nm was found and opened, so none was added and no value was guessed.
The model keeps its caveat: it ignores absorption outside blood, so red light looks better than it is.

## What is real and what is a toy

| real (taken from a published source, see SOURCES.md) | toy (our simplification or choice) |
|---|---|
| Brain scattering vs colour (Jacques 2013 power law), anisotropy g = 0.86 (Yona 2016) | Tissue is one homogeneous block: no grey/white matter layers, no blood vessels, no skull, no fibre body |
| Haemoglobin absorption spectra (Prahl, OMLC) | Absorption = blood only, with an assumed 3 % blood volume and 75 % oxygen saturation; no background (non-blood) absorption, so red light is probably made to look a bit better than it is |
| Thermal constants of brain and blood (Elwassif 2006; read only in an unofficial third-party copy, see SOURCES.md) | One scattering parameter set; g held at its 473 nm value for every colour |
| ChR2 4-state model (Williams 2013, Table 1) and PyRhO's 4-state ChR2 fit | Williams' recovery rate read as 10^-5 (the table prints 10^5, which cannot be right; see SOURCES.md) |
| Chronos and ChrimsonR off-times (Klapoetke 2014) | Chronos and ChrimsonR are "simplified": ChR2's model with only the closing rates rescaled; their real light sensitivity, desensitisation and recovery are not modelled |
| Hodgkin-Huxley equations (1952) | Squid-axon neuron, gate rates sped up 3x (16.3 C instead of 6.3 C); every switch scaled to the same 15 uA/cm^2 peak current so only kinetics differ; one cell, no dendrites, no network. Its own resonance makes 1:1 firing return briefly above the first failure (see Speed) |
| | Hidden differences in the speed comparison: the opsin rates are 22 C values while the neuron runs at 16.3 C; the Williams photon flux uses the drive wavelength (the paper fixes 470 nm), so the 590 nm ChrimsonR stand-in gets 25 % more photons per mW/mm^2 |
| | The two ChR2 sets agree only for short pulses: off-time 8.2 ms (Williams) and 10.4 ms (PyRhO) after 1-2 ms of light, but 12 vs 35 ms after 500 ms, and their steady/peak trends go opposite ways (review B, section 1c) |
| Stujenske 2015 heating figures, used only as a comparison | One activation threshold (3 mW/mm^2) for every switch; real thresholds differ by switch, expression level and cell type |
| | Fibre launches light uniformly inside its acceptance cone; 25 um cells to 6 mm, then cells growing to about 45 mm, where the heat model holds baseline; the glass fibre's own heat conduction is ignored |
| | 20-pulse trains, 2 ms pulses, tested rates 10-200 Hz; "follows" = at least 95 % of pulses give exactly one spike, which with 20 pulses allows exactly one miss; the headline speed is the last rate before the first failure |

The model is deliberately honest about where it disagrees with the published reference: it runs
hotter than Stujenske et al. 2015's model (details in `results/run_summary.json` and the tests).

## Licences

All code here is MIT. Parameters are restated with citation from CC BY articles (Williams 2013,
Yona 2016), BSD-3 code (PyRhO) and factual tables (Jacques 2013, Prahl/OMLC). No code or data was
copied from the Stujenske et al. MATLAB package (CC BY-NC-ND): only its published numbers are cited.
NEURON is not used; an optional NEURON cross-check was not built in this pass.
