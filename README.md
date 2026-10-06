<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg">
    <img alt="Nobel 2026 Lab. Hands-on demos of this year's Nobel Prizes, one card per prize. Medicine: a nerve cell lit by a pulse of blue light from the tip of an optical fibre. Physics: strings of light sensors in dark ice, a particle track with a cone of blue light behind it, and the sensors near the track lit up. A third, dashed slot holds the prizes still to come: Chemistry on 7 October and Economics on 12 October. Toy models, not research, not for lab or clinical use. Videos made with showtime, an open-source video studio for coding agents." src="assets/hero-light.svg" width="100%">
  </picture>
</p>

> **Educational demos made to show an open-source tool. Not research, and not for any lab or clinical use.**

<p align="center"><b>Live:</b> <a href="https://faviovazquez.github.io/nobel-2026-lab/">the lab's site</a> · <a href="https://faviovazquez.github.io/nobel-2026-lab/2026/medicine/video/interactive/">the Medicine video that asks</a> · <a href="https://faviovazquez.github.io/nobel-2026-lab/2026/physics/video/interactive/">the Physics video that asks</a> · <a href="https://faviovazquez.github.io/nobel-2026-lab/2026/physics/glashow/">a real 6 PeV event in 3D</a></p>

<p align="center">
  <a href="#what-is-this"><b>What is this</b></a> ·
  <a href="#made-with-showtime"><b>Made with showtime</b></a> ·
  <a href="#the-prizes"><b>The prizes</b></a> ·
  <a href="#medicine-the-stations"><b>Medicine</b></a> ·
  <a href="#physics-the-stations"><b>Physics</b></a> ·
  <a href="#what-is-real-and-what-is-a-toy"><b>Real or toy?</b></a> ·
  <a href="#rerun-it-yourself"><b>Rerun it</b></a> ·
  <a href="#glossary"><b>Glossary</b></a>
</p>

## What is this

Every October the Nobel Prizes are announced. This repository turns each prize into a small learning lab, in its own folder. Each prize gets the same five things:

- **sourced facts:** a plain-English fact sheet where every sentence has a source;
- **a claims ledger:** the exact sentences we use, each with its source and the date it was checked;
- **toy models you can run** on your own computer;
- **a page that asks you to guess first**, then shows what the toy model says;
- **a video that stops and asks** you questions along the way.

They are teaching toys. They are not science, and nothing here is a result.

## Made with showtime

Every video in this lab, including the versions that stop and ask, was made with **[showtime](https://github.com/FavioVazquez/showtime)**, an open-source video studio for coding agents.

## The prizes

| Prize | 2026 topic | Folder | Status |
|---|---|---|---|
| Medicine | Light-gated ion channels and optogenetics: Karl Deisseroth, Peter Hegemann, Georg Nagel (announced 5 October) | [2026/medicine](2026/medicine/README.md) | done: facts, claims ledger (27 claims), toy models, page and video |
| Physics | Neutrino astronomy: Francis Halzen, for the IceCube Neutrino Observatory (announced 6 October) | [2026/physics](2026/physics/README.md) | done: facts, claims ledger (41 claims), toy models, a replay of a real event, page and video |
| Chemistry | to be announced on 7 October | none yet | coming |
| Economics | to be announced on 12 October | none yet | coming |

The Nobel announcements run from 5 to 12 October 2026 ([nobelprize.org](https://www.nobelprize.org/prizes/medicine/2026/press-release/)). A folder is added only when its prize has been announced and its facts are sourced. The year index is in [2026/README.md](2026/README.md).

## Medicine: the stations

The 2026 Nobel Prize in Physiology or Medicine went to Karl Deisseroth, Peter Hegemann and Georg Nagel, "for their discoveries concerning light-gated ion channels and optogenetics." Think of five stops in a science museum. Each stop says what it is made of and whether it is ready.

<table>
  <tr>
    <td width="96" valign="top"><img src="assets/icons/station-switch.svg" alt="Icon: a light switch turned on" width="72"></td>
    <td valign="top"><b>1. How the light switch works</b> <i>(ready)</i><br>
    An algal protein opens a pore when blue light hits it. A four-step drawing shows the light, the pore, the ions and the spike. See it below, or read the <a href="2026/medicine/README.md#the-story-in-14-lines">story</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="assets/icons/station-depth.svg" alt="Icon: a beam of light fading as it goes deeper" width="72"></td>
    <td valign="top"><b>2. How deep light goes, and how much it heats</b> <i>(ready)</i><br>
    A toy model of light spreading through brain tissue from a fibre tip, and of the warmth it adds, for blue, amber and red light. Code and results: <a href="2026/medicine/simulator/README.md">simulator</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="assets/icons/station-heat.svg" alt="Icon: a thermometer" width="72"></td>
    <td valign="top"><b>3. The heat budget</b> <i>(ready)</i><br>
    How many neurons can one degree of warming buy you? A toy population of neurons, a fibre and a heat limit. Code and results: <a href="2026/medicine/heat-budget/README.md">heat-budget</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="assets/icons/station-page.svg" alt="Icon: a web page with a slider" width="72"></td>
    <td valign="top"><b>4. The interactive page</b> <i>(ready)</i><br>
    A page in your browser: guess first, then see what the toy model says. <a href="https://faviovazquez.github.io/nobel-2026-lab/2026/medicine/page/">Try it online</a>, or open <a href="2026/medicine/page/index.html"><code>2026/medicine/page/index.html</code></a> after cloning (it needs no server).</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="assets/icons/station-video.svg" alt="Icon: a video frame with a play button" width="72"></td>
    <td valign="top"><b>5. The video</b> <i>(ready)</i><br>
    A 2:21 explainer of the prize, and a version that stops and asks you three questions. Every fact in it comes from the <a href="2026/medicine/CLAIMS.md">claims ledger</a>. <a href="https://faviovazquez.github.io/nobel-2026-lab/2026/medicine/video/interactive/">Play the version that asks</a>. Files and how it was made: <a href="2026/medicine/video/README.md">video</a>.</td>
  </tr>
</table>

<details>
<summary><b>Station 1 in pictures: how a light-gated channel works</b></summary>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/diagram-light-gated-channel-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/diagram-light-gated-channel-light.svg">
    <img alt="Four steps. 1: blue light reaches a protein in the cell membrane, with the channel closed. 2: a light-catching molecule inside the protein, retinal, changes shape and a pore opens. 3: positive ions flow through the open pore into the cell. 4: the inside of the cell becomes less negative and the neuron fires a spike, within milliseconds. A simplified drawing, not to scale." src="assets/diagram-light-gated-channel-light.svg" width="560">
  </picture>
</p>

</details>

<details open>
<summary><b>Stations 2 and 3 in pictures</b></summary>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="2026/medicine/results/light_depth_profile_dark.png">
    <img alt="A chart of light fading with depth below a fibre tip for blue, yellow and red light in a toy model of brain tissue. Blue fades fastest, red slowest, and a dashed line marks the 3 milliwatts per square millimetre level. Educational demo, toy model." src="2026/medicine/results/light_depth_profile_light.png" width="720">
  </picture>
</p>

<p align="center">
  <img alt="Neurons lighting up around a fibre tip in a toy model: 1.77 milliwatts of blue light, 0.68 degrees of warming at the hottest point, 9,483 neurons recruited. One in 40 neurons is shown. Educational demo, toy model." src="assets/neurons-light-up-blue.png" width="720">
</p>

</details>

## Physics: the stations

The 2026 Nobel Prize in Physics went to Francis Halzen, "for decisive contributions to the IceCube Neutrino Observatory and the discovery of high-energy neutrinos of astrophysical origin." IceCube is a cubic kilometre of ice at the South Pole, watched by 5,160 light sensors on 86 strings. Six stops this time.

<table>
  <tr>
    <td width="96" valign="top"><img src="assets/icons/station-cone.svg" alt="Icon: a cone of blue light behind a fast particle" width="72"></td>
    <td valign="top"><b>1. How a neutrino telescope works</b> <i>(ready)</i><br>
    A neutrino from space almost never touches anything. Very rarely it hits the ice, and the light it makes reaches sensors hanging on strings. A four-step drawing shows how: see it below.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="assets/icons/station-telescope.svg" alt="Icon: strings of light sensors, the ones near a particle track lit up" width="72"></td>
    <td valign="top"><b>2. Build a neutrino telescope</b> <i>(ready)</i><br>
    A toy neutrino telescope on a laptop: a muon, its light, the sensor hits and a fit of its direction. Then one question: how much worse does the aim get if the strings are spaced further apart? Code and results: <a href="2026/physics/telescope/README.md">telescope</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="assets/icons/station-kilometre.svg" alt="Icon: a cube of ice dotted with sensors" width="72"></td>
    <td valign="top"><b>3. Why a cubic kilometre</b> <i>(ready)</i><br>
    Neutrinos from space are rare and seldom hit anything, so the detector has to be huge to catch a few. Three small toy calculations ask why it had to be that big. Code and results: <a href="2026/physics/kilometre/README.md">kilometre</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="assets/icons/station-replay.svg" alt="Icon: a burst of coloured dots inside a replay arrow" width="72"></td>
    <td valign="top"><b>4. The real 6 PeV event, replayed</b> <i>(ready)</i><br>
    On 8 December 2016 IceCube recorded a particle shower of about 6 PeV (6 million billion electronvolts). A page replays IceCube's public data for it in 3D, in your browser, every light pulse at its recorded time. <a href="https://faviovazquez.github.io/nobel-2026-lab/2026/physics/glashow/">Open the replay</a>. Sources and files: <a href="2026/physics/glashow/README.md">glashow</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="assets/icons/station-page.svg" alt="Icon: a web page with a slider" width="72"></td>
    <td valign="top"><b>5. The interactive page</b> <i>(ready)</i><br>
    Guess first, then see what the toy models say: the odds that a neutrino hits the ice, how big a detector has to be, and how far apart the strings can go. <a href="https://faviovazquez.github.io/nobel-2026-lab/2026/physics/page/">Try it online</a>, or open <a href="2026/physics/page/index.html"><code>2026/physics/page/index.html</code></a> after cloning (it needs no server).</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="assets/icons/station-video.svg" alt="Icon: a video frame with a play button" width="72"></td>
    <td valign="top"><b>6. The video</b> <i>(ready)</i><br>
    An explainer of the prize, and a version that stops and asks. Every fact in it comes from the <a href="2026/physics/CLAIMS.md">claims ledger</a>. <a href="https://faviovazquez.github.io/nobel-2026-lab/2026/physics/video/interactive/">Play the version that asks</a>. Files and how it was made: <a href="2026/physics/video/README.md">video</a>.</td>
  </tr>
</table>

<details open>
<summary><b>Stations 1 and 3 in pictures: how a neutrino telescope works, and IceCube roughly to scale</b></summary>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/diagram-neutrino-telescope-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/diagram-neutrino-telescope-light.svg">
    <img alt="Four steps. 1: a neutrino from space crosses the Earth and the ice at the South Pole without touching anything, which is what almost always happens. 2: very rarely it hits a nucleus in the ice and makes a muon, which leaves a long track, or a shower, a ball of light. 3: the charged particles move faster than light travels in ice and give off a cone of blue Cherenkov light. 4: sensors on strings record when and how much light arrives, and the pattern gives the direction and the energy. A simplified drawing, not to scale." src="assets/diagram-neutrino-telescope-light.svg" width="560">
  </picture>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/diagram-icecube-scale-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/diagram-icecube-scale-light.svg">
    <img alt="The IceCube detector, roughly to scale: a hexagon of strings hanging in the ice at the South Pole, with light sensors between 1,450 and 2,450 metres deep, filling a block about 1 kilometre across, a cubic kilometre of ice. 5,160 sensors on 86 strings, 125 metres apart. IceTop's 81 stations sit on the surface. Only some strings and sensors are drawn." src="assets/diagram-icecube-scale-light.svg" width="560">
  </picture>
</p>

</details>

## What is real, and what is a toy

<table>
  <tr>
    <th width="16%"></th>
    <th width="42%">Real</th>
    <th width="42%">A toy</th>
  </tr>
  <tr>
    <td valign="top"><b>Every prize</b></td>
    <td valign="top">The prize, the people, the dates and the papers. Every sentence is sourced in the prize's FACTS.md and checked in its CLAIMS.md: <a href="2026/medicine/CLAIMS.md">Medicine</a>, <a href="2026/physics/CLAIMS.md">Physics</a>.</td>
    <td valign="top">Every model we built. The outputs are for learning. They are not checked against experiments, and they must not be used to plan an experiment, a device or a treatment. Each model's README lists every simplification.</td>
  </tr>
  <tr>
    <td valign="top"><b>Medicine</b></td>
    <td valign="top">The numbers we quote from published papers, such as a warming of 0.2 to 2 degrees Celsius reported in one study, and the published parameters the models start from. Each has a link.</td>
    <td valign="top">The light, heat and nerve-cell models. Tissue is treated as one simple material. There is no skull, no blood vessels and no real brain shape.</td>
  </tr>
  <tr>
    <td valign="top"><b>Physics</b></td>
    <td valign="top">IceCube's published results and numbers, such as the size of the detector and the energy of the 6 PeV event, each with a link to its paper or page. The public event data in the 3D replay: IceCube's own data release for that event (DOI <a href="https://doi.org/10.21234/gr2021">10.21234/gr2021</a>), replayed at its recorded times. The drawing is ours, not an official IceCube visualisation.</td>
    <td valign="top">Our light, detector and rate models: how the particles make light and how it travels through the ice; simplified strings, sensors and ice; and how many neutrinos a toy detector would catch. They are not predictions, and they are not IceCube results.</td>
  </tr>
</table>

## Rerun it yourself

Everything runs on an ordinary laptop processor, with no GPU and no accounts. After the one-time install it needs no network. Each folder has its own README with the exact steps, and that README is the reference.

- **Medicine**, the light and heat simulator, from `2026/medicine/` ([steps](2026/medicine/simulator/README.md)):

  ```bash
  python3.11 -m venv .venv && . .venv/bin/activate && pip install -r simulator/requirements.txt && python -m simulator.run_all
  ```

- **Physics**, build a neutrino telescope, a quick run from `2026/physics/telescope/` ([steps](2026/physics/telescope/README.md); the full published run is much bigger, and its README says how long it takes):

  ```bash
  python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && python -m telescope.run_all --quick --workers 4
  ```

- **Physics**, why a cubic kilometre, from `2026/physics/kilometre/` ([steps](2026/physics/kilometre/README.md); its optional cross-checks download public IceCube files):

  ```bash
  python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && python -m whykm.run_all
  ```

- **Physics**, the 6 PeV replay: rebuilt from IceCube's data release, see [glashow](2026/physics/glashow/README.md).
- The pages need nothing: open `2026/medicine/page/index.html` or `2026/physics/page/index.html` in a browser.
- Check every link, picture and source in this repository, offline: `python3 tools/check_links.py`
- Rebuild the pictures: `python3 tools/make_diagrams.py`

## Glossary

| Term | In plain English |
|---|---|
| Optogenetics | Using light to switch cells on or off, after giving them the gene for a light-sensitive protein. |
| Channelrhodopsin | A protein from algae that is both a light sensor and a channel: it opens a pore when light hits it. |
| Ion channel | A pore in a cell's outer membrane that lets charged particles through. |
| Ion | An atom or small molecule with an electric charge, such as sodium. |
| Action potential (spike) | The brief electrical pulse a nerve cell fires to pass on a signal. |
| Retinal | A small light-catching molecule that sits inside the protein and changes shape when it absorbs light. |
| Wavelength | The colour of light, measured in nanometres (nm). In this story, blue light is around 460 to 470 nm. |
| Scattering | Tissue bends light in all directions, so a beam fades and spreads as it goes deeper. |
| Viral vector | A modified virus used as a delivery van to carry a gene into chosen cells. |
| Neutrino | A particle with no electric charge and almost no mass. It seldom collides with anything, so neutrinos pass all the way through the Earth, and through us, without us noticing. |
| IceCube | A neutrino telescope: a cubic kilometre of ice at the South Pole, watched by 5,160 light sensors on 86 strings. |
| Cherenkov light | The faint blue light given off by a charged particle that moves through ice faster than light travels in ice. It is what IceCube's sensors record. |
| PeV | Petaelectronvolt, a unit of energy: a million billion electronvolts. The event in station 4 had about 6 PeV. |
| Sigma (σ) | A way to say how unlikely a result would be if it were only chance. More sigma means less likely to be a fluke. The Nobel Committee's texts call 5 sigma the threshold for a discovery. |
| Toy model | A deliberately simple model that shows an idea. It is good for learning and not for decisions. |

## Licence and credit

MIT licence, see [LICENSE](LICENSE). Facts and quotations belong to their sources, which are linked next to every statement. This project is not affiliated with, or endorsed by, the Nobel Foundation, the Nobel Committee, the IceCube Collaboration or anyone named in it.

Data used by the Physics demos:

- The 6 PeV event: IceCube Collaboration, data release for the Glashow resonance event, DOI [10.21234/gr2021](https://doi.org/10.21234/gr2021).
- The positions of IceCube's 5,160 sensors: derived from IceCube's ppc geometry, Zenodo [10.5281/zenodo.10410725](https://doi.org/10.5281/zenodo.10410725), CC-BY-4.0.
- Neutrino cross sections and the Earth model: the nuFATE tables (Vincent, Argüelles, Kheirandish, [arXiv:1706.09895](https://arxiv.org/abs/1706.09895)), MIT licence.

Every video here was made with [showtime](https://github.com/FavioVazquez/showtime), an open-source video studio for coding agents.
