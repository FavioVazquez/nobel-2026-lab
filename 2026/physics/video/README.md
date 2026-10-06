# Physics 2026: a telescope made of ice (video, 2:37)

> **Educational demo, toy models. Not research.** Made with [showtime](https://github.com/FavioVazquez/showtime), an open-source video studio for coding agents.

A two-and-a-half-minute explainer of this year's Nobel Prize in Physics: why catching high-energy neutrinos from space takes a cubic kilometre of Antarctic ice, how a telescope made of ice aims, a real 6 PeV shower replayed from IceCube's public data, and what is still open. It asks you three questions along the way and uses the two toy models in this folder ([telescope](../telescope/README.md), [kilometre](../kilometre/README.md)).

| File | What it is |
|---|---|
| [`exports/nobel-2026-physics.mp4`](exports/nobel-2026-physics.mp4) | The video, 1920x1080, 2:37, 9.7 MB (the GitHub-size copy of the master; -14 LUFS), captions burned in |
| [`exports/poster.jpg`](exports/poster.jpg) | The thumbnail frame (65 billion neutrinos per second through a fingertip) |
| [`interactive/index.html`](interactive/index.html) | The version that stops and asks: [play it online](https://faviovazquez.github.io/nobel-2026-lab/2026/physics/video/interactive/), or open it in a browser (no server needed). It pauses at each of the three questions, marks your answer and plays on |
| [`storyboard.md`](storyboard.md), [`project/narration.md`](project/narration.md) | The plan and the exact words spoken |
| [`project/`](project) | The video's source (HTML scenes, timing, audio plan), rebuildable with showtime |
| [`process/`](process) | The critics' reports on the plan and on the finished video (two rounds), so you can see what was caught before it shipped |

## What it says, and where each fact comes from

Every factual sentence is a row of the [claims ledger](../CLAIMS.md) (ids in the last column). Toy-model numbers come from this folder's experiments and are always said as "our toy model".

| Time | Scene | Narration | Claims |
|---|---|---|---|
| 0:00.0 | 1 cold open | About sixty-five billion neutrinos from the Sun pass through your little fingernail every second, and almost none of them touch anything. So how do you catch one? | P11, P09, P10 |
| 0:11.0 | 2 the prize and the roadmap | This year's Nobel Prize in Physics went to Francis Halzen, for decisive contributions to IceCube, a telescope made of Antarctic ice, and the discovery of high-energy neutrinos from space. Four steps, and three guesses for you. | P01, P18, P13 |
| 0:27.9 | 3 the ghost particle (q1) | Step one: the ghost particle. Guess: a high-energy neutrino crosses a whole kilometre of ice. What are the odds it hits anything on the way? | P09 |
| 0:41.2 | 3b the answer | In our toy model, about one in sixty-five thousand. So the detector had to be huge. | toy (kilometre), P16 |
| 0:48.0 | 4 a telescope of ice | Step two: the telescope. In nineteen eighty-eight, Halzen and John Learned proposed using the ice itself. Halzen then led the team that built it. | P41, P05, P04, P39, P13 |
| 0:59.9 | 5 the blue cone | When one does hit, it makes a charged particle faster than light travels in ice. It leaves a cone of blue light, and each sensor times its arrival. | P15, P40 |
| 1:11.4 | 6 our toy telescope (q2) | Step three: our toy telescope. From the light's timing alone, it finds the particle's direction. Neutrinos fly straight, so that points back to where they came from. Guess: same ice, strings twice as far apart, so a quarter as many. How much worse does it aim? | P12, toy (telescope) |
| 1:32.6 | 6b the answer | In our toy model, more than five times worse: fewer strings, less light. Trend only, not IceCube's real aim. | toy (telescope) |
| 1:41.1 | 7 what it found | Step four: what it found. In twenty thirteen, IceCube reported the first evidence of high-energy neutrinos from outer space. In twenty sixteen, it caught this shower, replayed from the real data. | P19, P20, P33, P38 |
| 1:55.1 | 8 how many from space (q3) | IceCube records about a hundred thousand neutrinos a year. Guess: how many of them come from outer space? | P17 |
| 2:06.3 | 8b the answer | About a hundred, the Nobel Committee says. Most of the rest are made in our own atmosphere. | P17 |
| 2:13.0 | 9a the open question | The prize honours that discovery: high-energy neutrinos from space. Which objects make them is still open: one nearby galaxy shows evidence, not yet proof. | P01, P20, P23, P25, P31 |
| 2:24.8 | 9b the tie-back | So how do you catch one? With a cubic kilometre of ice, still watching. | P13 |
| 2:30.4 | 10 end card | Made with showtime, an open-source video studio for coding agents. |  |

The three questions (the interactive page stops at each; the MP4 holds a pause-and-think beat): the odds that a 100 TeV neutrino hits anything in 1 km of ice (our toy model: about 1 in 65,000); how much worse our toy telescope aims on the same patch of ice with the strings twice as far apart, so a quarter as many (our toy model: 5.6 times, 0.71° to 4.0°, 1 TeV muons); how many of IceCube's roughly 100,000 neutrinos a year come from outer space (about 100, the Nobel Committee says).

## Honest notes

- The toy-model scenes are labelled "our toy model". The telescope's degrees are a tuned toy for 1 TeV muons, not IceCube's real aim (about 0.3° for 100 TeV tracks, Nobel Committee); the factor 5.6 is the direction of the trend, and it changes with the toy's own delay model (see the telescope README).
- The 6 PeV shower is real: IceCube's public data release, DOI 10.21234/gr2021, drawn by us. It is one event, consistent with the Glashow resonance, not a proof.
- The sky in the open-question scene is an illustration, not IceCube's map. NGC 1068 is evidence (4.2 sigma), not yet proof.
- The real sensor layout comes from IceCube's ppc geometry (Zenodo, CC-BY-4.0).
- The voice is synthetic (the open-source Kokoro voice `am_michael`, made on this machine). The music is "The space is big" by Komiku (CC0).
- The end card and a corner mark credit [showtime](https://github.com/FavioVazquez/showtime), the open-source video studio for coding agents that made it.

## Rebuild it

You need showtime 0.4.0 or later and Node 20+. From `project/`:

```bash
showtime voice script narration.md -o voice -v am_michael -s 1.08   # the voice (a few minutes on a laptop)
showtime retime . --from-voice voice/timeline.json --total 157.5
showtime check .
showtime render . --job nobel-physics
showtime export html . --audio embed --folder -o ../interactive        # the page that asks
```

The scene data (`assets/shot-*`) are the real IceCube sensor positions, the public 6 PeV event, and the toy telescope's example event, copied from this folder's experiments.
