# Build a neutrino telescope (educational demo, toy model)

> **Educational demo made to show an open-source tool. Toy model, not research.**
> Every number on this page is from our toy model, with tuned constants: read it as a trend only. It does
> not reproduce, validate or match IceCube's performance.

The 2026 Nobel Prize in Physics went to Francis Halzen "for decisive contributions to the IceCube Neutrino
Observatory and the discovery of high-energy neutrinos of astrophysical origin". IceCube is a cubic kilometre
of Antarctic ice watched by 5,160 light sensors on 86 strings. A neutrino almost never interacts, but when one
does near the detector it can make a muon, and the muon leaves a cone of blue (Cherenkov) light as it crosses
the ice. The sensors record when the light arrives, and from those times you work out where the muon, and so
the neutrino, came from.

This folder builds a toy version of that chain on a laptop: muon, light, sensor hits, a direction fit. Then it
asks one question: **how much worse does the aim get if the strings are spaced further apart?** It runs the
same muons through hexagonal grids with strings 50 to 300 m apart, and through the real IceCube layout.

Own code, MIT licence. CPU only, no network at run time. Python 3.12+ for the pinned versions (3.11 works with numpy 1.26 / scipy 1.15, see requirements.txt), NumPy, SciPy, Matplotlib.

## Results in one breath

1 TeV muons from random directions, 10,000 tracks per layout (`results/telescope_summary.json`, status
`final`). All values: **our toy model, trend only**.

| strings apart | strings | median sensors hit | line fit: median error (68% of events below) | Pandel fit: median error (68% below) | events with 8+ hits |
|---|---|---|---|---|---|
| 50 m | 463 | 361 | 1.39 deg (2.27) | 0.18 deg (0.25) | 100% |
| 80 m | 187 | 144 | 1.82 deg (2.70) | 0.31 deg (0.45) | 100% |
| 125 m | 73 | 56 | 2.79 deg (4.10) | 0.71 deg (1.09) | 100% |
| 160 m | 43 | 33 | 3.93 deg (5.81) | 1.30 deg (2.14) | 99.95% |
| 200 m | 31 | 23 | 4.54 deg (6.67) | 2.11 deg (3.58) | 97.9% |
| 250 m | 19 | 15 | 6.47 deg (9.56) | 4.02 deg (7.05) | 86.0% |
| 300 m | 13 | 12 | 8.68 deg (13.3) | 7.13 deg (12.5) | 59.6% |
| real IceCube layout (125 m grid + 8 DeepCore strings) (toy, not IceCube's aim) | 86 | 61 | 2.80 deg (4.00) | 0.64 deg (0.97) | 100% |

* **The trend (our toy model):** on the same 1 km^2 patch, wider spacing means fewer strings (73 at 125 m, 19 at
  250 m), fewer sensors see the muon and the aim gets worse. From 125 m to 250 m the Pandel-fit median grows 5.6
  times (0.71 to 4.0 deg) for the muons it still fits, and the 250 m grid misses 14% of them (fewer than 8 hits);
  counting those as failures the step is about 7 times (from `results/per_event.csv`). Spreading the same 73
  strings twice as far apart instead (a 4 km^2 detector) costs far less in our toy, about 1.5 to 3 times, and the
  step shrinks for brighter muons (about 3 times at 100 TeV); these two come from an independent check, 4,000
  tracks per variant, not part of `run_all` (`results/independent_check_variants.json`). From 50 m to 300 m the
  number of hit sensors drops about 30 times and the Pandel-fit error grows about 40 times.
* **Timing beats geometry.** The line fit only uses "where and when", as if the light moved with the muon.
  The Pandel fit also knows that light is late when it scatters, and in our toy model it is 4 to 8 times
  sharper on the 50-125 m grids. On the sparsest grids (250-300 m, about 12-15 hits) the two fits get close
  (1.6 and 1.2 times): with so few hits, knowing about scattering helps little.
* **The real layout** sits next to the 125 m hexagon (it is mostly a 125 m grid); its extra DeepCore strings add a
  few hits and make it a little sharper in our toy model (0.64 vs 0.71 deg).
* **The numbers move when our assumptions move.** With delays fitted to our own photon random walk instead of
  AMANDA's published delay parameters, the Pandel errors at 50-200 m are 11-46% smaller (0.47 deg instead of
  0.71 at 125 m) while 250-300 m stay put, so the step from 125 m to 250 m grows from about 6 times to about 8
  times (see "Tier B" below). Trust the direction of the trend (wider spacing, worse aim), not the degrees and
  not the exact factor.
* Statistical noise is small: the bootstrap 68% interval of each median is +-1 to 2% (`median_error_ci68_deg`).

Not a comparison: IceCube's real angular resolution for muon tracks is about 0.3 degrees at 100 TeV (Nobel
Committee, scientific background). Our 0.64 deg on the real layout is a toy number for 1 TeV muons with one
tuned sensor constant; do not read it as IceCube's aim.

## Figures (light and dark versions, 1600 px wide)

| file | what |
|---|---|
| `results/error_vs_spacing_{light,dark}.png` | median error vs string spacing for both fits (shaded: the middle 68% of events), the real layout as diamonds, IceCube's 125 m marked; under each spacing its number of strings on the same 1 km² patch, and the share of muons fitted where it is below 99%; right: median hit sensors |
| `results/example_event_{light,dark}.png` | one typical simulated muon on the real layout, top and side views, hits coloured by time and sized by charge, true track and both fits |
| `results/photon_check_{light,dark}.png` | tier B: our light shortcut vs a photon random walk in the same toy ice, and what that does to the curve |

Every figure carries the subtitle "our toy model: tuned constants, trend only, not IceCube's performance".

## Data files

| file | what |
|---|---|
| `results/telescope_summary.json` | every number above, the definitions, the sensitivity run, the tier-B summary, run times |
| `results/example_event.json` | the example event: `track` (point, direction), `hits` = `[sensor_index, t_ns, charge]` sorted by time, `line_fit_dir`, `pandel_fit_dir` (and fit points), `error_deg`. `sensor_index` is the row of `data/icecube86_geometry.csv` (0-5159). Chosen as typical, not best: its Pandel error and its hit count are both the closest to their medians (0.64 deg, 61 hits) |
| `results/per_event.csv` | one row per track and layout: hits, strings hit, charge, triggered, both errors, line-fit speed |
| `results/photon_check.json` | tier-B curves: light vs distance, delay distributions at 22, 52, 102 m, the Pandel values fitted to the walk |
| `results/sensitivity_walk_delays.json` | the full sweep rerun with the walk-fitted delays |
| `data/icecube86_geometry.csv` | the 5,160 in-ice sensor positions (strings 1-86, sensors 1-60), see Sources |

## How it works, in plain words

1. **Detector.** The real one: 5,160 sensor positions (IceCube coordinates, metres). The toy ones: strings on a
   triangular ("hexagonal") lattice filling a 1 km^2 circle (radius 564 m), each string with 60 sensors 17 m
   apart over the same 1 km of depth, like IceCube.
2. **Muon.** A straight line through the ice at the speed of light. Directions are isotropic (every direction
   equally likely, up-going and down-going; cos(zenith) uniform in [-1, 1], azimuth uniform). Positions are
   uniform over a 700 m disc across the track, and we keep tracks that run at least 300 m inside a central
   cylinder (radius 500 m, 1 km tall). The same 10,000 tracks (seed 2026) go through every layout.
3. **How much light.** Cherenkov light leaves the muon at 40.75 degrees (cos theta = 1/n, n = 1.32). Frank-Tamm
   gives 260 photons per cm between 300 and 500 nm; the showers a 1 TeV muon leaves along its way add 1.77 times
   more (energy loss b E times 5.32 m of shower light per GeV), 72,000 photons per metre in total. In the ice the
   light scatters many times and diffuses outward; the light reaching a sensor at distance d follows the
   diffusion formula for a line source, K0(d / 28 m). A sensor catches about 0.004 m^2 of it (tuned). That gives a
   mean number of photoelectrons, about 2 at 30 m, 0.8 at 50 m, 0.1 at 100 m; a Poisson draw decides how many
   arrive. One or more = a hit.
4. **When it arrives.** Unscattered light would arrive at t = (l + d tan theta_c) / c. Scattering delays each photon
   by a random time drawn from the Pandel distribution (a gamma distribution whose shape grows with distance;
   AMANDA's published parameters). The sensor records the first photon of its N, plus 2 ns of timing noise.
5. **Trigger.** An event counts if at least 8 sensors are hit.
6. **Line fit.** Pretend every hit is the same point moving at constant speed and solve for the speed in closed
   form (one line of linear algebra). Its direction is the first guess. It ignores the cone and the scattering,
   so it is fast and rough (its fitted speed comes out about 0.20 m/ns, not the true 0.30, a known trait).
7. **Pandel fit.** Starting from the line fit, adjust the direction, the position and the time of the track
   until the hit times look most like "direct time plus a Pandel delay" (a likelihood, maximised with
   Nelder-Mead; five numbers). It uses the single-photon delay for every hit, as IceCube's "SPE" fit does in
   outline, even though the recorded hit is the first of several photons.
8. **Score.** The angle between the fitted and the true direction. We report the median over events, the 68%
   containment (68% of events do better) and the 16th-84th percentile band.

## Every simplification (what this toy leaves out or bends)

* **Homogeneous ice.** One scattering and one absorption length everywhere (averages of the real depth
  profile). No dust layer (the real ice has a murky band near 2,000 m depth), no layer tilt, no anisotropy (real
  light travels further along the glacier flow), no birefringence, no bubbly hole ice around the strings.
* **Light model.** Diffusion formula for the amount of light, Pandel formula for the delays: both are
  shortcuts, not photon tracking (tier B checks them inside the same toy ice). Constant refractive index for
  both the angle and the light speed (real light travels at the group velocity, about 2% slower). The
  Pandel parameters are AMANDA's 2004 fit for shallower ice and down-facing sensors; we ignore that real
  sensors look downward (they see light from above worse) and treat every sensor as looking everywhere.
* **The fit knows the truth.** The Pandel fit uses exactly the delay model the simulation used. Real data
  never fits that well, so this makes our toy model optimistic.
* **Muons.** Every muon is exactly 1 TeV, never slows down and loses energy smoothly (no single big showers);
  it is an infinite line (no starting or stopping tracks); no multiple muons, no neutrino interaction vertex.
* **Sensors.** All 5,160 sensors work (the 2016 event file marks 77 as off). No dark noise or random hits, no
  saturation, no waveforms: one first-photon time and an integer charge per sensor. The trigger is a simple
  "8 or more hits", without IceCube's local-coincidence condition.
* **Isotropic muons.** Real TeV muons in IceCube are mostly down-going cosmic-ray muons; neutrino-induced ones
  are up-going. The geometry question here does not need that split.
* **One tuned light constant.** `DOM_ACCEPT_FACTOR = 0.2` sets how many photons a sensor catches, and so how far
  from the track sensors fire and how many are hit. Changing it shifts every curve.

## Constants and where they come from

All in `telescope/constants.py`, each with its source and one of: verified (read in the source during this
build), computed (our arithmetic), literature (cited, not re-opened), tuned (our choice).

| constant | value | source | status |
|---|---|---|---|
| refractive index n | 1.32 | Price & Bergstrom, Appl. Opt. 36 (1997) 4181 | literature |
| Cherenkov angle | 40.75 deg | cos theta = 1/n | computed |
| photons per metre, 300-500 nm | 26,050 | Frank-Tamm formula (Frank & Tamm 1937; PDG review "Passage of particles through matter") | computed |
| shower light per GeV | 5.321 m of track | Radel & Wiebusch, Astropart. Phys. 44 (2013) 102, arXiv:1210.5140, eq. 8 | verified |
| muon radiative loss b | 0.363e-3 per m.w.e., x 0.917 g/cm^3 = 3.33e-4 /m | Chirkin & Rhode, arXiv:hep-ph/0407075, Fig. 21 fit | verified |
| muon energy | 1 TeV, constant | | tuned |
| scattering length lambda_e | 27.8 m | SPICE ftp-v3m table, 1450-2450 m, 400 nm (Zenodo 10.5281/zenodo.10410725, CC-BY-4.0; formulas arXiv:1301.5361); `scripts/ice_average.py` | computed |
| absorption length lambda_a | 86.3 m | same | computed |
| Pandel tau, lambda, lambda_a | 557 ns, 33.3 m, 98 m | Ahrens et al. (AMANDA), NIM A 524 (2004) 169, arXiv:astro-ph/0407044, eq. 19 | verified |
| timing noise | 2 ns RMS | IceCube DAQ, NIM A 601 (2009) 294, arXiv:0810.4930: "precision on the order of 1-2 ns RMS" | verified |
| sensor radius | 0.1651 m | icecube/ppc om.conf | verified |
| PMT quantum efficiency | 0.25 | Abbasi et al., NIM A 618 (2010) 139, arXiv:1002.2442: "approximately 25% at 390 nm" | verified |
| sensor acceptance factor | 0.2 | angle, spectrum and glass losses in one number | **tuned** |
| high-QE sensor efficiency | 1.35 | icecube/ppc docs ("nominally 1.35"), eff-f2k list | verified |
| 60 sensors per string, 17 m apart | | arXiv:1301.5361 | verified |
| footprint 1 km^2, generation disc 700 m, cylinder 500 m x 1 km, >= 300 m inside, trigger >= 8 hits | | | tuned |
| fit: early-hit width 10 ns, outlier floor 1e-7 per ns | | | tuned |
| scattering g (tier B only) | 0.9 | icecube/ppc cfg.txt | verified |

## Tier B: checking our light shortcut against a photon random walk

`telescope/photon_check.py` follows 300,000 photons from the track through the same homogeneous toy ice
(scattering with g = 0.9, absorption 86 m) and records how much light reaches each distance and how late it is.
Inside our toy ice (not a check against IceCube):

* **Amount of light:** the diffusion formula gives 3% more light than the walk at 22 m, 23% more at 52 m and
  43% more at 102 m (it falls slightly too slowly). Good enough for a toy; it means our far sensors fire a bit
  too often.
* **Delays:** the AMANDA Pandel delays are 2.2 to 3.6 times longer than the walk's (median 152 vs 42 ns at
  22 m, 483 vs 205 ns at 52 m, 1039 vs 479 ns at 102 m). That is expected, not a bug: those parameters were fitted
  to AMANDA's shallower, dustier ice and down-facing sensors, while the walk uses the clearer average of the
  IceCube depths. A Pandel fitted to the walk has lambda = 63 m, tau = 684 ns.
* **Effect on the result:** rerunning the whole sweep with the walk-fitted delays (in both simulation and fit)
  makes the Pandel errors 11-46% smaller on the 50-200 m grids and leaves 250-300 m unchanged (within 2%), so the
  curve gets steeper: 250 m vs 125 m becomes 8.3 times instead of 5.6. Wider spacing still means worse aim; how
  much worse depends on the delay model.

## Run it

From `2026/physics/telescope/`:

```bash
python3.12 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python -m pytest -q tests                                  # 14 tests, about 2 s
python -m telescope.run_all --quick --workers 4            # smoke run, about 35 s on a 6-core laptop
python -m telescope.run_all --events 10000 --photons 300000 --workers 60 --status final   # the published run
python -m telescope.run_all --figures-only                 # redraw figures from results/*.json
```

Without `--status final` a run is labelled "preliminary" (and `--quick` "smoke-test"), so a default 4,000-track run on a laptop cannot pass for the published 10,000-track results it overwrites.

The published run used a 64-core Linux build machine with 60 worker processes (Python 3.12, NumPy 2.5.3,
SciPy 1.18.1): 127 s wall in total, of which the main sweep was about 47 s (4-8 s per layout, 10,000 tracks
each), the photon walk 27 s and the sensitivity sweep 50 s. Everything is seeded (tracks from seed 2026; each
event's hits from (seed, layout, event number)), so the numbers do not depend on the number of workers.
Each event costs about 0.04 s of CPU on that machine (the Pandel fit dominates), so a single core needs about
1.5-2 hours for the full run (160,000 fitted events with the sensitivity sweep); `--events 2000` gives the same
trend in about 20 minutes.

## What each file does

| file | in plain words |
|---|---|
| `telescope/constants.py` | every number, with its source or "tuned" |
| `telescope/geometry.py` | loads the real layout; builds the hexagonal grids |
| `telescope/events.py` | seeded random muon tracks and the "runs 300 m inside" selection |
| `telescope/light.py` | how much light each sensor gets, Poisson hits, first-photon times |
| `telescope/reco.py` | the line fit and the Pandel likelihood fit |
| `telescope/sweep.py` | runs many muons through one layout in parallel |
| `telescope/photon_check.py` | tier B photon random walk and the walk-fitted Pandel |
| `telescope/figures.py` | the figures |
| `telescope/run_all.py` | everything in one command, writes `results/` |
| `results/independent_check_variants.json` | an independent reviewer's 125 m vs 250 m variants (4,000 tracks each, not made by `run_all`): sensor acceptance, muon energy, the same 73 strings spread out, timing noise |
| `scripts/ice_average.py` | provenance of the two ice lengths (needs the SPICE files, not shipped) |
| `tests/test_telescope.py` | geometry, Cherenkov timing, reproducibility, fits, file formats |

## Sources

* Sensor positions: `geo-f2k` and `eff-f2k` of the `ice/spice_ftp-v3m` folder of D. Chirkin's icecube/ppc
  archive, Zenodo https://doi.org/10.5281/zenodo.10410725 (CC-BY-4.0), converted to IceCube coordinates with
  z = z_f2k + 1948.07 m. The positions agree with the geometry block of IceCube's public Glashow-event release
  (DOI 10.21234/gr2021) to 3e-5 m; nothing from that release is used here.
* South Pole ice: Aartsen et al. (IceCube), "Measurement of South Pole ice transparency with the IceCube LED
  calibration system", NIM A 711 (2013) 73, arXiv:1301.5361.
* Pandel delays and the line-fit + likelihood chain: Ahrens et al. (AMANDA), "Muon track reconstruction and data
  selection techniques in AMANDA", NIM A 524 (2004) 169, arXiv:astro-ph/0407044.
* Timing: Abbasi et al. (IceCube), "The IceCube data acquisition system", NIM A 601 (2009) 294, arXiv:0810.4930.
* PMT: Abbasi et al. (IceCube), "Calibration and characterization of the IceCube photomultiplier tube",
  NIM A 618 (2010) 139, arXiv:1002.2442.
* Shower light: Radel & Wiebusch, Astropart. Phys. 44 (2013) 102, arXiv:1210.5140.
* Muon energy loss: Chirkin & Rhode, "Propagating leptons through matter with Muon Monte Carlo (MMC)",
  arXiv:hep-ph/0407075.
* Cherenkov light: I. Frank and I. Tamm, Dokl. Akad. Nauk SSSR 14 (1937) 109; formula as in the Particle Data
  Group's Review of Particle Physics. Ice refractive index: P. B. Price and L. Bergstrom, Appl. Opt. 36 (1997) 4181.

## Licences

Code: MIT. `data/icecube86_geometry.csv` is derived from the CC-BY-4.0 icecube/ppc Zenodo archive (attribution
above and in the file header). Parameters from papers are restated with citation. No code was copied from
IceCube software.
