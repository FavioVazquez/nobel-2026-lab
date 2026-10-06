# Sources for every parameter (educational demo, toy model)

"Verified" below means the number was read in the cited source's full text during this build
(2026-10-06), not copied from a secondary summary. Nothing here is our measurement.

## Light (`light.py`, `inputs/tissue_optics.csv`)

| parameter | value | source | status |
|---|---|---|---|
| reduced scattering of brain, mu_s'(lambda) = a (lambda/500 nm)^-b | a = 24.2 cm^-1, b = 1.611 (mean of 8 studies) | Jacques 2013, Phys. Med. Biol. 58:R37, Table 2. CSV: https://omlc.org/news/dec14/Jacques_PMB2013/table2_JacquesPMB2013.csv | verified (CSV) |
| anisotropy g | 0.86 (adult mouse cortex, 473 nm) | Yona, Farah & Shoham 2016, eNeuro 3:ENEURO.0059-15.2015, Table 1 and Results, CC BY. https://www.eneuro.org/content/3/1/ENEURO.0059-15.2015 | verified (full text) |
| cross-check: scattering coefficient at 473 nm | mu_s = 211 cm^-1 (their slice experiment); our power law gives 191 cm^-1 at 470 nm | same | verified. The other set in that paper (60.7 cm^-1, mu_a 0.62 cm^-1, g 0.89) is their fit to Aravanis et al. 2007 data, not their own measurement |
| haemoglobin molar extinction, HbO2 and Hb | 7 rows, 444-636 nm | Prahl, OMLC, https://omlc.org/spectra/hemoglobin/summary.html | verified (table) |
| blood volume 3 %, saturation 75 %, Hb 150 g/L, 64500 g/mol | | modelling assumptions (typical textbook values) | ASSUMPTION |
| refractive index (sets launch cone only) | 1.36 | Stujenske, Spellman & Gordon 2015, Methods: "n is the index of refraction (n=1.36) of brain (Binding et al., 2011, Aravanis et al., 2007)", PMC4512881 | verified (full text via NCBI efetch, 2026-10-06) |
| background (non-blood) absorption of brain | not modelled | no open source giving a non-blood brain value at 470, 590 and 635 nm was found and opened; ex vivo papers report total absorption (residual blood included). No value was guessed | NOT MODELLED: red light looks better than it is |
| fibre | 200 um core, NA 0.22 (main runs); 62 um, NA 0.22 for the Stujenske comparison | Stujenske 2015 Results: "62 um (NA .22) optical fiber" | verified for the 62 um case; the 200 um main fibre is our choice |

Method: photon-packet Monte Carlo after Wang, Jacques & Zheng 1995 (MCML), Comput. Methods Programs
Biomed. 47:131. Own code; no code copied from MCML, MCX (GPLv3) or the Stujenske MATLAB package
(CC BY-NC-ND).

## Heat (`heat.py`, `inputs/thermal.csv`)

| parameter | value | source | status |
|---|---|---|---|
| brain conductivity k | 0.527 W/m/K (range 0.45-0.6) | Elwassif, Kong, Vazquez & Bikson 2006, J. Neural Eng. 3:306, doi:10.1088/1741-2560/3/4/008 | read only in an unofficial third-party full-text copy (studylib mirror); the publisher page is behind a bot wall and Europe PMC has no open copy (checked 2026-10-06). Flagged: cite a source we can open, or say the values come from an unofficial copy, before publishing |
| brain density, specific heat | 1040 kg/m^3, 3650 J/kg/K | same | same |
| blood density, specific heat | 1057 kg/m^3, 3600 J/kg/K | same | same |
| blood perfusion | 0.004-0.012 ml/s/cm^3; we use 0.008 and report the two ends | same | same; the mid-point is our choice |
| Pennes equation with light source phi*mu_a; arterial 36.7 C, baseline 37 C | | Stujenske 2015 Methods eqs. 8-9, PMC4512881 (full text via NCBI efetch) | verified |

Published heating figures used for comparison (all from Stujenske et al. 2015, Cell Reports 12:525,
https://doi.org/10.1016/j.celrep.2015.06.036, read in full text):
* 532 nm, 10 mW continuous, 62 um NA 0.22 fibre: plateau of about 2.2 C averaged in 250 um-radius
  slices within a few hundred um of the tip; maximum single voxel 4.1 C; at least 1 C within roughly
  1 mm^3; under 5 % more rise from 60 s to 120 s.
* 445 nm, 200 um fibre: their model 0.35 C/mW against 0.42 C/mW measured by Christie et al. 2012
  (the illumination duration behind these two numbers was NOT verified).
* 473 nm, 5 or 10 mW, 200 um fibre, at most 50 % duty cycle: peak rises "confined to a range of .5-.9 C".
* 3 and 10 mW/mm^2 contours "are in the range of the EPD50 for various opsins (Mattis et al., 2012)".
Their optical parameters came from Johansson 2010 (paywalled; values UNVERIFIED), which differ from ours.
Stujenske also state that results were not sensitive to voxel size between 5 and 30 um (light) and that 30 um
"gave very similar results to 10 um" (heat), so grid size is not a reason for the gap with this model.

## Switches (`opsin.py`)

| item | values | source | status |
|---|---|---|---|
| ChR2(H134R) 4-state model | eps1 0.8535, eps2 0.14, sigma_ret 12e-20 m^2, w_loss 0.77, tau_ChR2 1.3 ms, gamma 0.1, Gd1 = 0.075 + 0.043 tanh((V+20)/-20), Gd2 0.05, e12 = 0.011 + 0.005 ln(1 + I/0.024), e21 = 0.008 + 0.004 ln(1 + I/0.024), S0 = 0.5(1 + tanh(120(100 I - 0.1))), G(V)(V-E) = 10.6408 - 14.6408 exp(-V/42.7671), E 0 mV, g 0.4 mS/cm^2 (HEK cells) | Williams et al. 2013, PLoS Comput Biol 9:e1003220, Table 1, CC BY, https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003220 (Table text read via Europe PMC full-text XML of PMC3772068) | verified |
| Williams recovery rate Gr | Table 1 prints 4.34587 x 10^5 exp(-0.0211539274 V) ms^-1; we use 10^-5 | same | OUR INTERPRETATION: 10^+5 would make recovery take nanoseconds, against the paper's seconds-long recovery and its listed comparison values 0.004 / 0.0004 ms^-1 |
| PyRhO 4-state ChR2 fit | g0 1.14e5 pS, gam 0.00742, phi_m 2.33e17 photons/mm^2/s, k1 4.15, k2 0.868, p 0.833, Gf0 0.0373, k_f 0.0581, Gb0 0.0161, k_b 0.063, q 1.94, Gd1 0.105, Gd2 0.0138, Gr0 0.00033 (ms^-1), E 0, v0 43 mV, v1 17.1 mV; model equations of `RhO_4states` | PyRhO `pyrho/parameters.py` and `pyrho/models.py`, https://github.com/ProjectPyRhO/PyRhO (BSD-3-Clause, checked via the GitHub API); Evans et al. 2016, Front. Neuroinform. 10:8 | verified (source code) |
| Chronos off time | tau_off 3.6 +/- 0.2 ms (n = 7); turn-on 2.3 ms | Klapoetke et al. 2014, Nat. Methods 11:338, PMC3943671 (full text via NCBI efetch) | verified |
| ChrimsonR off time | 15.8 +/- 0.4 ms (n = 5); Chrimson 21.4 ms; tau_off measured after 2 ms pulses | same | verified |
| published spike-following, for context only | Chronos: "Chronos-mediated optical spiking perfectly replicated electrically driven spiking between 5 to 60 Hz", measured with green 530 nm light, 2 ms pulses, 40-pulse trains, cultured neurons. ChrimsonR: "fast, reliable red-light driven spiking at frequencies of at least 20 Hz in both cultured neurons and acute cortical slice ..., comparable to the blue-light spiking performance of the commonly used ChR2 (H134R)"; Fig. 2e: 40-pulse trains, 2 ms pulses, 5 mW/mm^2, red (625 nm) light, n = 4 cells | same; wording re-read in the full text on 2026-10-06 | verified; NOT used as a test target. The toy differs: 470 nm (590 nm for the ChrimsonR stand-in), 20 pulses, 3 mW/mm^2, a squid-axon neuron. The toy's 10 Hz for ChrimsonR contradicts the measurement; it is a limit of the simplified stand-in |
| Chrimson peak 590 nm | "With a spectral peak at 590 nm" | Klapoetke 2014 | verified (full text, 2026-10-06) |
| Chronos drive wavelength 470 nm | | our choice | ASSUMPTION |
| conductance density for the neuron | scaled so every switch gives the same 15 uA/cm^2 peak for one 2 ms, 3 mW/mm^2 pulse | our choice | ASSUMPTION |

## Neuron (`neuron.py`)

Hodgkin & Huxley 1952, J. Physiol. 117:500 (squid axon, 6.3 C): gNa 120, gK 36, gL 0.3 mS/cm^2,
ENa 50, EK -77, EL -54.387 mV, Cm 1 uF/cm^2 (the standard modern restatement with rest at -65 mV).
