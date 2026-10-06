# Physics 2026: a telescope made of ice

> **Educational demos made to show an open-source tool. Not research, and not for any lab or clinical use.**

**Status:** facts: done · claims ledger: done (41 claims, checked 2026-10-06) · pictures: done · toy telescope: done, independently reviewed · why a cubic kilometre: done, independently reviewed · 6 PeV event replay: done · page: done · video: done

The 2026 Nobel Prize in Physics went to Francis Halzen "for decisive contributions to the IceCube Neutrino Observatory and the discovery of high-energy neutrinos of astrophysical origin". (P01) IceCube is a cubic kilometre of ice at the South Pole, watched by 5,160 light sensors on 86 strings, that catches the faint blue light made when a neutrino from space, very rarely, hits the ice. Back to the [front page](../../README.md).

Numbers like (P01) point to rows in [CLAIMS.md](CLAIMS.md), where each sentence has its source.

## The stations

Five stops, as in a science museum. Each says what it is made of and whether it is ready.

<table>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-cone.svg" alt="Icon: a cone of blue light behind a fast particle" width="72"></td>
    <td valign="top"><b>1. How a neutrino telescope works</b> <i>(ready)</i><br>
    A neutrino from space almost never touches anything. Very rarely it hits the ice, and the light it makes reaches sensors hanging on strings. A four-step drawing shows how: see <a href="#the-pictures">the pictures</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-telescope.svg" alt="Icon: strings of light sensors, the ones near a particle track lit up" width="72"></td>
    <td valign="top"><b>2. Build a neutrino telescope</b> <i>(ready)</i><br>
    A toy neutrino telescope on the real sensor layout: simplified light and ice, a direction fit, and how the aim changes when the strings are spread out (our toy model, trend only). Folder: <a href="telescope/README.md">telescope</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-kilometre.svg" alt="Icon: a cube of ice dotted with sensors" width="72"></td>
    <td valign="top"><b>3. Why a cubic kilometre</b> <i>(ready)</i><br>
    Neutrinos from space are rare and seldom hit anything, so the detector has to be huge to catch a few. The real detector, roughly to scale, is in <a href="#the-pictures">the pictures</a>. Folder: <a href="kilometre/README.md">kilometre</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-replay.svg" alt="Icon: a burst of coloured dots inside a replay arrow" width="72"></td>
    <td valign="top"><b>4. The real 6 PeV event, replayed</b> <i>(ready)</i><br>
    On 8 December 2016 IceCube recorded a particle shower of about 6 PeV (6 million billion electronvolts). A page replays IceCube's public data for it in 3D, in your browser, every light pulse at its recorded time. <a href="https://faviovazquez.github.io/nobel-2026-lab/2026/physics/glashow/">Open the replay</a>. Sources and files: <a href="glashow/README.md">glashow</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-video.svg" alt="Icon: a video frame with a play button" width="72"></td>
    <td valign="top"><b>5. The video</b> <i>(ready)</i><br>
    A 2:37 explainer that stops and asks you three questions: <a href="https://faviovazquez.github.io/nobel-2026-lab/2026/physics/video/interactive/">play it online</a>. Every fact in it comes from the <a href="CLAIMS.md">claims ledger</a>; the toy numbers come from stations 2 and 3. Made with <a href="https://github.com/FavioVazquez/showtime">showtime</a>. Folder: <a href="video/README.md">video</a>.</td>
  </tr>
</table>

## The pictures

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../../assets/diagram-neutrino-telescope-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="../../assets/diagram-neutrino-telescope-light.svg">
    <img alt="Four steps. 1: a neutrino from space crosses the Earth and the ice at the South Pole without touching anything, which is what almost always happens. 2: very rarely it hits a nucleus in the ice and makes a muon, which leaves a long track, or a shower, a ball of light. 3: the charged particles move faster than light travels in ice and give off a cone of blue Cherenkov light. 4: sensors on strings record when and how much light arrives, and the pattern gives the direction and the energy. A simplified drawing, not to scale." src="../../assets/diagram-neutrino-telescope-light.svg" width="560">
  </picture>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../../assets/diagram-icecube-scale-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="../../assets/diagram-icecube-scale-light.svg">
    <img alt="The IceCube detector, roughly to scale: a hexagon of strings hanging in the ice at the South Pole, with light sensors between 1,450 and 2,450 metres deep, filling a block about 1 kilometre across, a cubic kilometre of ice. 5,160 sensors on 86 strings, 125 metres apart. IceTop's 81 stations sit on the surface. Only some strings and sensors are drawn." src="../../assets/diagram-icecube-scale-light.svg" width="560">
  </picture>
</p>

## What is real, and what is a toy

<table>
  <tr>
    <th width="50%">Real</th>
    <th width="50%">A toy</th>
  </tr>
  <tr>
    <td valign="top">The prize, the laureate, the date and the citation. Every sentence is sourced in <a href="FACTS.md">FACTS.md</a> and checked in <a href="CLAIMS.md">CLAIMS.md</a>.</td>
    <td valign="top">Our light model: how the particles make light and how it travels through the ice, with simplified settings.</td>
  </tr>
  <tr>
    <td valign="top">IceCube's published results and numbers, such as the size of the detector and the energy of the 6 PeV event. Each has a link to its paper or page.</td>
    <td valign="top">Our detector models: simplified strings, sensors and ice. Each station README lists every simplification.</td>
  </tr>
  <tr>
    <td valign="top">The public event data in the 3D replay: IceCube's own data release for the 6 PeV event (DOI <a href="https://doi.org/10.21234/gr2021">10.21234/gr2021</a>), replayed at its recorded times. The drawing is ours, not an official IceCube visualisation.</td>
    <td valign="top">Our event rates: how many neutrinos a toy detector would catch. They are for learning. They are not predictions, and they are not checked against IceCube's analyses.</td>
  </tr>
</table>

## Folder map

| Path | What it is | Status |
|---|---|---|
| [FACTS.md](FACTS.md) | The sourced fact sheet: citation, laureate, the story, and where the sources disagree | done |
| [CLAIMS.md](CLAIMS.md) | The ledger of claims we use, with sources and check dates | done |
| [`../../assets`](../../assets/diagram-neutrino-telescope-light.svg) | The four-step drawing of a neutrino telescope and the detector roughly to scale, in dark and light | done |
| [telescope](telescope/README.md) | Build a neutrino telescope: a toy model | done, independently reviewed |
| [kilometre](kilometre/README.md) | Why a cubic kilometre: a toy model | done, independently reviewed |
| [glashow](glashow/README.md) | IceCube's real 6 PeV event replayed in 3D from the public data ([online](https://faviovazquez.github.io/nobel-2026-lab/2026/physics/glashow/), or open `glashow/index.html`) | done |
| [page](page/README.md) | Guess first, then see: the odds, the detector size, the Earth as a shield, a spacing slider ([online](https://faviovazquez.github.io/nobel-2026-lab/2026/physics/page/)) | done |
| [video](video/README.md) | A 2:37 explainer and a version that stops and asks ([play it online](https://faviovazquez.github.io/nobel-2026-lab/2026/physics/video/interactive/)), the plan, the source and the critics' reports | done |

## Rerun and check

The facts and pictures need no code. To rebuild the pictures: `python3 tools/make_diagrams.py`. To check every link, image and source in this repository without a network: `python3 tools/check_links.py`. Each station folder has its own README with its exact steps.

These are teaching toys. The models are simplified and their outputs are for learning only. They are not research, and they are not IceCube results.
