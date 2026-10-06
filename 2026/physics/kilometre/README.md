# Why a cubic kilometre? (Physics 2026, experiment B)

> **Educational demo made to show an open-source tool. Toy model, not research.**
> Every number on this page is **our toy model, trend only**. None of it reproduces, validates or
> matches an IceCube result; where we put our numbers next to IceCube's, we say how far apart they are and why.

The 2026 Nobel Prize in Physics went to Francis Halzen "for decisive contributions to the IceCube Neutrino
Observatory and the discovery of high-energy neutrinos of astrophysical origin". IceCube watches a cubic
kilometre of Antarctic ice. This folder asks, with three small calculations, why it had to be that big.

Own code, MIT licence. CPU only; it runs in about 10 seconds on a laptop. Python 3.11 with NumPy, SciPy, Matplotlib.

## Run it

From `2026/physics/kilometre/`:

```bash
python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python -m whykm.run_all                 # the three results + figures (no network needed)
python -m whykm.fetch                   # optional: public IceCube files for the cross-checks (~80 MB, to data_cache/)
python -m whykm.run_all                 # again, now with the cross-checks
python -m pytest -q tests               # 20 tests, under a minute
```

`python -m whykm.run_all --fetch` does both steps at once. If you already have the files somewhere,
`python -m whykm.fetch --from-dir PATH` copies them instead (every file is checked against its published MD5).

## The three answers (our toy model, trend only)

| question | our toy model says |
|---|---|
| **1. How likely is one neutrino to interact while crossing 1 km of ice?** | at 100 TeV: 1.5 in 100,000, **about 1 in 65,000**; at 1 PeV: about 1 in 18,500 (muon neutrinos, mean of neutrino and antineutrino) |
| **2. How many muon neutrinos of 1 PeV get through the Earth straight up?** | **about 0.16 %** (0.0016, about 1 in 600); at 100 TeV about 16 % |
| **3. How many neutrino interactions per year (above 60 TeV) happen inside a cube of ice?** | 10 m cube: about one every 22,000 years; 100 m cube: about one every 22 years; **1 km cube: about 46 per year** |

So a neutrino almost never stops in a kilometre of ice, the Earth only shields you at the highest
energies, and the count grows with the volume: ten times wider is a thousand times more events. With a
100 m detector you would wait decades for one interaction inside it.

The summary for the video and the page is `results/kilometre_summary.json`, with every number,
the per-species values and the variations below.

## The figures

All in `results/`, each as `_light.png` and `_dark.png`, subtitled "our toy model: simplified, trend only".

| file | what it shows |
|---|---|
| `interaction_chance` | chance to interact in 1 km of ice, 1 TeV to 10 PeV, muon neutrino and antineutrino |
| `earth_transmission` | fraction that gets through the Earth, by energy and arrival direction (map), plus curves for 180, 150, 120 and 100 degrees from overhead |
| `events_vs_size` | interactions per year against the side of the cube, 10 m to 2 km, with 10 m, 100 m and 1 km marked |
| `hese_check` | cross-check 1: our 1 km³ count against IceCube's public HESE simulation and the observed rate |
| `earth_shadow_check` | cross-check 2: the shape of the Earth's shadow in IceCube's public effective-area tables against our toy |

Tables: `interaction_chance_1km.csv`, `earth_transmission_numu.csv`, `events_vs_size.csv`.

## How it works, in plain words

1. **Chance to interact.** A neutrino crossing a length L of ice meets n × L nucleons per cm² (n = nucleons
   per cm³). Its chance to hit one is 1 − exp(−n σ L), where σ is the neutrino–nucleon cross section (how
   big a target each nucleon looks). We take σ from nuFATE's isoscalar table (charged plus neutral current).
2. **The Earth.** For a neutrino coming from below, we add up the matter along its path through a layered
   Earth (nuFATE's density model) and use the same formula: the fraction that gets through is exp(−N_A σ X),
   with X the matter crossed in g/cm². Straight up through the centre, X is about 1.1 × 10¹⁰ g/cm².
3. **Events per year.** IceCube's measured astrophysical flux (the HESE 7.5-year fit) tells how many
   neutrinos per cm² per second per energy arrive from each direction. Multiply by σ, by the Earth
   transmission for that direction, by the number of nucleons in the cube and by a year, add up all six
   neutrino types, all directions and all energies from 60 TeV to 10 PeV.

## Every simplification

| simplification | effect on the numbers |
|---|---|
| We count **every interaction** inside the cube. No light, no sensors, no trigger, no veto, no reconstruction | the counts are an upper limit for events that start inside a detector of that size (see cross-check 1: HESE keeps about 1 in 7). Detectors also catch muons made outside them, which we leave out (see cross-check 2) |
| The 60 TeV threshold is on the **neutrino** energy; HESE's cut is on the energy **deposited** in the ice | neutral-current events and muon tracks deposit less than the neutrino energy, so we count events a real analysis would not |
| **Thin target**: rate = flux × σ × number of nucleons | exact enough: the largest error, for 2 km and 10 PeV, is 0.03 %. It also makes the shape of the volume irrelevant: only its volume counts |
| Earth: every interaction **removes** the neutrino. No regeneration (a neutral-current interaction only lowers the energy; a tau neutrino comes back as a lower-energy tau neutrino) and no energy loss bookkeeping | we overstate the absorption, most at the highest energies and for tau neutrinos. The full treatments are nuFATE (arXiv:1706.09895) and TauRunner |
| No **Glashow resonance** (electron antineutrino + electron → W, near 6.3 PeV) | missing events in the 5–10 PeV bin (visible in cross-check 1) and missing absorption for that one species near 6.3 PeV |
| One **power law** for the flux, from 60 TeV to 10 PeV, equal in all six species | other IceCube samples fit different spectral indices (2.37 to 2.87); see the variations below |
| Ice and rock are "isoscalar" (equal protons and neutrons, one nucleon per atomic mass unit; water really has 10 protons to 8 neutrons), with nuFATE's isoscalar cross sections; ice density 0.917 g/cm³ | small at these energies, where protons and neutrons look nearly alike as targets (not computed) |
| The Earth model's outer 3 km is water (1.02 g/cm³), as in nuFATE's fit; at the South Pole it is ice | negligible (a few km out of thousands) |
| Detector centre at 1.95 km depth | matters only for neutrinos from above (2 km of ice, nothing absorbed) |
| Cross sections from one set of parton distributions (CT10nlo, nuFATE's isoscalar table); IceCube measured σ through Earth absorption at 1.30 (+0.21 −0.19 stat, +0.39 −0.43 syst) times the Standard Model (arXiv:1711.08119) | the toy uses the Standard Model value |
| No atmospheric neutrinos or muons | the observed HESE rate includes them, our count does not |

### How much the 1 km³ number moves (our toy model, trend only)

| change | interactions per year in 1 km³ |
|---|---|
| baseline | 46 |
| flux normalisation −1σ / +1σ (4.75 / 7.84 instead of 6.37) | 34 / 56 |
| spectral index 3.07 / 2.68 instead of 2.87 | 44 / 48 |
| only charged-current / only neutral-current interactions | 34 / 12 |
| from below (through the Earth) / from above | 17 / 29 |
| if the Earth were transparent | 57 |
| threshold 100 TeV instead of 60 TeV | 23 |
| integrate up to 100 PeV instead of 10 PeV | 46 |

The ±1σ rows move one parameter at a time; the real fit has correlated errors, so they are not a confidence band.

## Cross-checks with IceCube's public data (honest version)

**1. Against the HESE 7.5-year sample** (the events that first showed the astrophysical neutrinos):

* Observed: 102 events, 60 of them with at least 60 TeV deposited, in 2,635 days (7.2 years). That is
  **8.3 per year**, and it includes atmospheric neutrinos and muons.
* Our toy, every interaction in a full cubic kilometre: **46 per year**. That is about five and a half times more.
  This is not agreement and is not supposed to be.
* IceCube's own public simulation in the same release, weighted to the same published flux, keeps
  **7.0 astrophysical events per year**. Comparing it with our toy energy bin by energy bin shows where the
  events go (figure `hese_check`, right panel): at 60–110 TeV HESE keeps 0.08 of our count, rising to
  0.40–0.42 above 1 PeV (Glashow events left out of that ratio).
  * The plateau below 1: HESE only counts interactions inside an inner fiducial volume. The paper excludes
    roughly the top 90 m, 90 m from the outer strings, the bottom 10 m and a 60 m layer under the dustiest ice;
    those sensors form the veto, and an event must leave at least 6,000 photoelectrons in the
    sensors (arXiv:2011.03545, section II).
  * The drop at low energy: in a muon-neutrino charged-current event the muon carries most of the energy
    out of the detector, and in a neutral-current event the outgoing neutrino does, so a 100 TeV neutrino
    often deposits less than 60 TeV and fails the cut. Our toy ignores this.
  * The highest bin (5–10 PeV) has Glashow-resonance events in the simulation that our toy leaves out.
* We did not use the release's detector-systematics corrections or its likelihood. We think (but did not check)
  that the simulation weights already include the Earth crossing.

**2. Against the CC0 track effective areas** (IceTracks DR1 IC86-II and DR2 IC86): these tables say how
large a target the track selection is, for muon neutrinos, by energy and declination. Absolute sizes cannot
be compared: at 100 TeV the horizontal table is about 130–150 m², our contained-only 1 km³ is about 13 m²,
because a track sample also catches muons made kilometres outside the detector. So we compare only the
**shape** of the Earth's shadow: the area in the band at declination 57–62° (about 60° below the horizon)
divided by the area at the horizon. Our toy's ratio (Earth transmission only) and the public tables follow
the same downward curve from about 10 TeV to 1 PeV (at 126 TeV: toy 0.39, DR1 0.40, DR2 0.40). They part
ways at both ends: below 10 TeV the public ratio is above 1 (a selection effect our toy cannot know about;
we did not look into it), and above 1 PeV the DR2 ratio flattens while ours keeps
falling (no regeneration in our toy, and muons from far away; we did not test which effect wins).

## Sources and constants

Every constant is in `whykm/constants.py` with its source or the word "choice". The main ones:

| what | value | source |
|---|---|---|
| neutrino–nucleon cross sections (6 species) | totals per isoscalar nucleon, 1 TeV to 1e10 GeV; CC/NC split up to 1e9 GeV | totals: nuFATE's isoscalar table `resources/NuFATECrossSections.h5` (CT10nlo, "0.5(p+n)"), exported once to `whykm/inputs/nufate/nufate_isoscalar_total_xs.csv` by `whykm/export_nufate_xs.py`. The CC/NC split only: nuFATE `resources/nuSQuIDSCrossSections/nusigma_sigma_{CC,NC}.dat`, which are not isoscalar below about 1 PeV (antineutrinos 14 % low at 100 TeV), so we use only their CC fraction. Both commit 86813eb (MIT; LICENSE and AUTHORS shipped in `whykm/inputs/nufate/`). Paper: Vincent, Argüelles, Kheirandish, arXiv:1706.09895. Checked: 10 PeV CC within 5 % of Gandhi et al. hep-ph/9807264 eq. 10, and antineutrino/neutrino ratio at 1 TeV between 0.5 and 0.65 as for an isoscalar target (tests) |
| Earth density | polynomial fit to STW105 | nuFATE `src/python/earth.py` (MIT), shipped unmodified; our vectorised version agrees with it to 0.2 % (test) |
| astrophysical flux | Φ₆ν = 6.37 (+1.47 −1.62) × 10⁻¹⁸ GeV⁻¹ cm⁻² s⁻¹ sr⁻¹ at 100 TeV, γ = 2.87 (+0.20 −0.19), all six species together | IceCube, Phys. Rev. D 104, 022002 (2021), arXiv:2011.03545, eq. VI.1 and Fig. VI.2 |
| HESE events and livetime | 102 events, 60 at ≥ 60 TeV; 227,708,167.68 s | HESE 7.5-year data release, doi:10.21234/4EQJ-BB17, github.com/icecube/HESE-7-year-data-release (LGPL-3.0; downloaded at run time, not shipped) |
| track effective areas | per energy and declination | IceTracks DR1 doi:10.7910/DVN/VKL316 and DR2 doi:10.7910/DVN/MMIIZA, both CC0 (downloaded at run time) |
| ice density | 0.917 g/cm³ | textbook value for ice Ih |
| detector depth | 1.95 km | middle of IceCube's 1450–2450 m sensor depths, arXiv:1301.5361 |
| counting window | 60 TeV to 10 PeV neutrino energy | choice (60 TeV copies the HESE cut, but on the wrong quantity, see above) |

## What each file does

| file | in plain words |
|---|---|
| `whykm/constants.py` | every number we put in, with where it comes from |
| `whykm/physics.py` | cross sections, interaction chance, Earth density and column depth, transmission, events per year |
| `whykm/crosscheck.py` | the two cross-checks with IceCube's public files |
| `whykm/fetch.py` | downloads (or copies) those public files into `data_cache/`, checking each MD5 |
| `whykm/figures.py` | the figures, light and dark |
| `whykm/run_all.py` | runs everything and writes `results/` |
| `whykm/inputs/nufate/` | the nuFATE tables and Earth model (MIT), with their LICENSE and AUTHORS |
| `whykm/export_nufate_xs.py` | one-off: exports nuFATE's isoscalar totals from its HDF5 file to the small CSV above (needs h5py; the toy does not) |
| `tests/test_kilometre.py` | checks against independent numbers (GQRS fit, nuFATE's own integral, scipy quad) and limits |

## Licences

Our code: MIT. The nuFATE files in `whykm/inputs/nufate/` are MIT (copyright 2017 Aaron C. Vincent,
Carlos A. Argüelles and A. Kheirandish), redistributed with their licence. IceCube's data files are not in
this repository: the CC0 track tables and the LGPL-3.0 HESE release are downloaded at run time and cited.
