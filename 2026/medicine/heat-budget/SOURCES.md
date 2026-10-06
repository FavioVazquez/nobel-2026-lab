# Sources for the heat budget (educational demo, toy model)

Educational demo, toy model. Not research, not for lab or clinical use.

Everything physical (light maps, tissue optics, the Pennes heat model, the photocycle models, the
Hodgkin-Huxley neuron, the 3 mW/mm^2 activation level) is inherited unchanged from the simulator; its
sources are in [`../simulator/SOURCES.md`](../simulator/SOURCES.md). This file lists only what the heat
budget adds. "Verified" means read in the source's full text on 2026-10-06.

## New parameters

| parameter | value | source | status |
|---|---|---|---|
| neuron density, mouse cortex | 92,000 neurons/mm^3 | Keller, Erö & Markram 2018, "Cell Densities in the Mouse Brain: A Systematic Review", Front. Neuroanat. 12:83, Table 1, row "Cortex (General)", CC BY 4.0, https://doi.org/10.3389/fnana.2018.00083 (full text via NCBI efetch, PMC6205984). The review attributes the value to Schüz & Palm 1989, J. Comp. Neurol. 286:442-455, doi:10.1002/cne.902860404 | verified in the review; the primary paper (Schüz & Palm 1989) was NOT read: UNVERIFIED at the primary source |
| how much that density varies | within one cortical region the spread between estimates averages 43,800 neurons/mm^3 (SD); excitatory density "approached 200,000 cells/mm^3" at its layer-4 peak | Keller et al. 2018, Results | verified; used only to say that a uniform density is a simplification |
| relative expression level per neuron | lognormal, median 1, log-spread 0.5 (also 0.25 and 1.0) | none | ASSUMPTION (labelled; the spread is shown as a band in the figure and as numbers in `results/summary.json`) |
| activation rule | recruited when light x expression >= 3 mW/mm^2 | the 3 mW/mm^2 level is the simulator's (Stujenske et al. 2015: 3 and 10 mW/mm^2 "in the range of the EPD50 for various opsins"); applying it per neuron and multiplying by expression is our choice | ASSUMPTION built on a verified number |
| heat limits | 0.5, 1.0 (default), 2.0 C at the hottest point | chosen for the demo | ASSUMPTION; illustrative levels, not a safety standard |
| reference neuron for the recipe | on the fibre axis, 0.5 mm below the tip | our choice | ASSUMPTION |
| recipe grid | pulse widths 0.5-10 ms, rates 10-200 Hz, peak powers 0.25-64 mW (factor sqrt 2), 20 pulses, "follows" = at least 95 % of pulses give exactly one spike | widths and rates our choice; 20 pulses and the 95 % rule are the simulator's | ASSUMPTION |
| brightest light computed at the neuron | 30 mW/mm^2 | our numerical choice, kept from the first run so the grid stays comparable: the simulator's old fixed 0.025 ms forward-Euler step became inaccurate for brighter light (and diverged above roughly 170 mW/mm^2). The neuron now uses a converged 0.01 ms 2nd-order Runge-Kutta step | ASSUMPTION (numerical) |
| colours reported | headline: 470 and 590 nm; 635 nm only as a labelled toy upper bound | our choice, because the model has no absorption outside blood, no 635 nm switch and an unbounded uniform block | PRESENTATION RULE |
| warming of a pulse train | steady warming of the average power plus the rise of one pulse, capped at continuous light at the peak power | our use of the linearity of the simulator's Pennes model | METHOD (checked by a test against an explicit pulse-train transient) |

## UNVERIFIED

- Schüz & Palm 1989 (the primary source of 92,000 neurons/mm^3) was not read; the value is taken from
  the Keller et al. 2018 review table, which was read in full text.
- Everything still marked UNVERIFIED in `../simulator/SOURCES.md` (Johansson 2010 optics, Stujenske's
  supplemental thermal choices, the Elwassif values read only in an unofficial third-party copy). Since
  the review, n = 1.36 (Stujenske 2015 Methods) and Chrimson's 590 nm peak (Klapoetke 2014) were
  verified in the full text.
- A background (non-blood) absorption coefficient for brain at 470, 590 and 635 nm: none found in an
  open source, so none is used (the red caveat stays).

## Licences

All code here is MIT. Keller et al. 2018 is CC BY 4.0 and only one number and two summary statements are
restated with citation. No code or data was copied from any source.
