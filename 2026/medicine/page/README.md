# "Try it" page (educational demo, toy model)

> **Educational demo, toy model.** Not research, not for lab or clinical use.

One self-contained page that lets a visitor guess, then check, three results of the light-and-heat
simulator in `../simulator/`:

1. Which colour (blue 470 nm, yellow 590 nm, red 635 nm) reaches deepest in brain tissue.
2. How much blue light warms the tissue for a chosen power and duty cycle.
3. Whether a neuron keeps up with light pulses for ChR2, Chronos (simplified) and ChrimsonR (simplified).

A bonus fourth panel appears when `data.js` was built with `--recruitment` (the heat budget's
`../heat-budget/results/recruitment.json`): neurons recruited per degree of warming, blue (470 nm)
against amber (590 nm). Red (635 nm) is shown only as a labelled toy upper bound, never as the answer.

Every number in the page's text is read from `data.js` (depths, warming, speeds, the resonance window,
how much hotter than Stujenske 2015 the model runs, the heat-box size); nothing is typed into `index.html`.

## Open it

Double-click `index.html`, or from this folder: `open index.html` (macOS) / `xdg-open index.html` (Linux).
No server, no network, no external fonts or scripts. It works from `file://`.

## How it is built

| file | what |
|---|---|
| `index.html` | the page: HTML, CSS and plain JavaScript in one file; charts are inline SVG drawn by the script |
| `data.js` | generated; sets `window.NOBEL_MED_DATA` with the numbers the page needs (about 5 KB) |
| `build_data.py` | reads `../results/` and writes `data.js` |
| `tests/test_page.cjs` | headless-Chrome checks and screenshots |
| `screenshots/` | the page after answering every step, at 360, 768 and 1440 px, light and dark |

`build_data.py` takes from `../results/`:
- `light_fibre200um_{470,590,635}nm.npz`: the depth profile, with the simulator's own definition
  (fluence averaged over the innermost 100 um of radius), at 10 mW, 0 to 4 mm, every 50 um; plus the
  depth where light drops below 3 and 1 mW/mm^2.
- `run_summary.json`: the 10 s warming at 10 mW (always on, 50 % and 10 % duty), steady warming per mW,
  the published comparison values, and each switch's share of pulses followed at each tested rate.
- `run_summary.json` also gives each switch's headline speed (the last rate before the first failure),
  the rates where 1:1 firing returns above it (a resonance of the toy cell, not of the light switch) and
  the neuron time-step check.
- `tradeoff.csv`: the summary tables (reach and heat per colour, speed per switch).
- with `--recruitment`: `../heat-budget/results/recruitment.json` (the heat budget's own schema; the
  default expression spread is used, decimated to 13 points per colour). A file that does not match is
  skipped with a warning.

How step 2 turns three runs into any setting, and what the page tells the visitor:
- Power: heat is linear in power in this model (a simulator test checks it), so the 10 mW result is
  scaled. Exact for the model.
- Duty cycle 10 %, 50 % or 100 %: straight from the model.
- Between those: a straight line between the two nearest runs, labelled "interpolated".
- Below 10 %: a straight line to zero at 0 %, labelled "extrapolated".

## Regenerate the data

Needs Python 3 with NumPy (the simulator's `requirements.txt` is enough). From this folder:

```bash
python3 build_data.py --recruitment    # with the bonus panel (the shipped data.js)
python3 build_data.py                  # without it
```

Run it again after the simulator or the heat budget is re-run.

## Test it

Needs Node and Playwright (`npm i playwright` anywhere, then point `NODE_PATH` at its `node_modules`),
and, for `--shots`, Pillow in the Python you pass as `PYTHON`:

```bash
NODE_PATH=/path/to/node_modules PYTHON=python3 node tests/test_page.cjs --shots
# add CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" to use the installed Chrome
NODE_PATH=/path/to/node_modules python -m pytest -q tests   # the same check (no screenshots) under pytest
```

It answers every step (step 1 with the keyboard only) at 360, 768 and 1440 px in light and dark themes and
checks: the reveal button waits for a guess, the answers and caveats appear, every chart has a title and a
description, no sideways scrolling, no console errors, no network requests, page + data under 1.5 MB,
screenshots under 600 KB (full page with the bonus panel open), the extrapolation label, the resonance note and the ChrimsonR statement in
step 3, that the numbers stated in the text match `data.js`, that the bonus panel compares blue and
amber with red only as a labelled toy upper bound, and that a copy built without `--recruitment` hides
the bonus panel.

MIT licence, like the rest of the repo.
