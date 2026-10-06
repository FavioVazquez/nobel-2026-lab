# IceCube's 6 PeV "Glashow" event, replayed from the real data

> **Educational demo made to show an open-source tool.** Drawn by nobel-2026-lab; not an official IceCube visualisation.

Open the page: <https://faviovazquez.github.io/nobel-2026-lab/2026/physics/glashow/> (or open `index.html` from a local copy; it needs no server and no network).

A 3D replay of the light recorded by IceCube on 8 December 2016: a shower with an energy of 6.05 ± 0.72 PeV, consistent with the Glashow resonance. Each faint dot is one of the 5,160 in-ice sensors on 86 strings; a sensor lights up when the first light reaches it, its colour shows when (red first, blue last) and its size grows with the logarithm of the charge it has collected. All 18,135 light pulses on the 453 sensors that saw light are replayed at their recorded times; the 17 µs of the event are slowed down to 12 seconds, slowest at the start. Drag to orbit, scroll or pinch to zoom, double-click (double-tap) to reset.

## Sources

- Data: IceCube Collaboration, data release for the Glashow resonance event, DOI [10.21234/gr2021](https://doi.org/10.21234/gr2021) (file `event.txt`: extracted pulses and sensor geometry).
- Paper: IceCube Collaboration, "Detection of a particle shower at the Glashow resonance with IceCube", Nature 591, 220 (2021), [arXiv:2110.15051](https://arxiv.org/abs/2110.15051): the shower energy (6.05 ± 0.72 PeV) and the resonance peak (6.3 PeV antineutrino energy).
- IceCube press release, March 2021: [the date of the event and Glashow's 1960 proposal](https://icecube.wisc.edu/news/press-releases/2021/03/icecube-detection-of-a-high-energy-particle-proves-60-year-old-theory/).

## Files

| File | What it is |
|---|---|
| `index.html` | The page: one self-contained file (Canvas 2D, no libraries, no external requests). |
| `event.js` | The data the page draws, built by `build_data.py` (about 340 KB). |
| `build_data.py` | Reads IceCube's `event.txt` and writes `event.js` (Python 3, standard library only). |
| `og.jpg` | The share image (1200 x 630), a screenshot of the page. |

## Rebuild event.js

Download the data release from DOI [10.21234/gr2021](https://doi.org/10.21234/gr2021), unpack it, then from this folder:

```sh
python3 build_data.py path/to/event.txt
```

It keeps the in-ice sensors (strings 1-86, sensors 1-60), sorts the pulses by time and stores times in ns since the first pulse. The original `event.txt` is not copied into this repository.

Back to the [2026 index](../../README.md).
