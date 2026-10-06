# Medicine 2026: the light switch (video, 2:21)

> **Educational demo, toy model. Not research, and not for any lab or clinical use.**

A two-minute explainer of this year's Nobel Prize in Physiology or Medicine, from an alga that swims toward light to the brain tool that won the prize. It asks you three questions along the way, then shows the toy model from this repository: how far light reaches in tissue, how much it heats, and how many neurons one degree of warming can switch on.

| File | What it is |
|---|---|
| [`exports/nobel-2026-medicine.mp4`](exports/nobel-2026-medicine.mp4) | The video, 1920x1080, 2:21, 9.6 MB (the GitHub-size copy of the master; -14 LUFS) |
| [`exports/poster.jpg`](exports/poster.jpg) | The thumbnail frame (the lit neuron with the blue pulse) |
| [`interactive/index.html`](interactive/index.html) | The version that stops and asks: [play it online](https://faviovazquez.github.io/nobel-2026-lab/2026/medicine/video/interactive/), or open it in a browser (no server needed). It pauses at each of the three questions, marks your answer and plays on |
| [`storyboard.md`](storyboard.md), [`project/narration.md`](project/narration.md) | The plan and the exact words spoken |
| [`project/`](project) | The video's source (HTML scenes, timing, audio plan), rebuildable with the open-source tool below |
| [`process/`](process) | The critics' reports on the plan and on the finished video, so you can see what was caught before it shipped |

## What it says, and where each fact comes from

Every factual sentence is a row of the [claims ledger](../CLAIMS.md) (ids in the last column). Numbers from our toy model come from the [simulator](../simulator/README.md) and the [heat budget](../heat-budget/README.md) after their independent review.

| Time | Scene | Narration | Claims |
|---|---|---|---|
| 0:00.0 | 1 cold open | In 1999, Francis Crick wrote that light would be the ideal signal for switching neurons, then called the idea rather far-fetched. This week, it won a Nobel Prize. | C15, C01 |
| 0:11.4 | 2 the prize and the roadmap | Karl Deisseroth, Peter Hegemann and Georg Nagel share the prize for discoveries about light-gated ion channels. Four steps, three guesses. | C01 |
| 0:21.3 | 3 the alga | Step one: an alga fifteen thousandths of a millimetre wide that swims toward light. Guess: how much faster than your eye does it react? | C03, C04 |
| 0:33.1 | 3b the answer | The Nobel Committee says: over twenty times faster. About half a millisecond after light hits its eyespot, an electrical impulse appears. | C04 |
| 0:42.2 | 4 the idea and the frog egg | Step two: the switch. Peter Hegemann proposed that one protein could catch light and form a channel. People doubted it. Georg Nagel put algal genes into frog eggs, and when light hit, the channels opened. | C05, C06 |
| 0:55.8 | 5 neurons and mice | Around one in the morning on 4 August 2004, Edward Boyden saw the first neuron carrying the alga's channel fire in blue light. By 2007, the Committee says, it worked in living mice. | C11, C26, C14 |
| 1:08.8 | 6 how deep: toy model | Step three: our toy model, an educational demo. A thin fibre sends blue, yellow or red light into brain tissue. Guess: which colour reaches deepest? | - |
| 1:22.1 | 6b the answer | Red: about one and a half millimetres deep, against one for blue. But our model ignores absorption outside blood, so read every depth as rough. Reaching deeper takes more light, and more light means heat. | R1, C21 |
| 1:34.8 | 7 light is heat | Tissue turns absorbed light into heat: a 2019 study measured 0.2 to 2 degrees Celsius of warming. In our toy model, pulsing the light cuts it: from about three and a half degrees to about six tenths of a degree. | C27, C22, R2 |
| 1:50.0 | 8 neurons per degree | How many neurons can one degree of warming recruit? Guess: hundreds, thousands, or tens of thousands? | R3 |
| 1:59.9 | 8b the answer | In our toy model: blue, about sixteen thousand; yellow, about thirty-one thousand. | R3 |
| 2:05.8 | 9 the limit and the tie-back | Step four: the limit. Visible light cannot penetrate deep into brain tissue. Far-fetched, Crick wrote in 1999. Not any more. | C20, C24, C25, C15 |
| 2:15.1 | 10 end card | Educational demos of this year's Nobel Prizes, made with showtime. | - |
The three questions (the interactive page stops at each; the MP4 shows a three-second "pause and think" beat): how much faster than a human eye the alga reacts (answer: more than 20 times, per the Nobel Committee), which colour reaches deepest in our toy model (red, with the caveat that it ignores absorption outside blood), and how many neurons one degree of warming can recruit with blue light in our toy model (more than ten thousand, under one threshold and one assumed expression law).

## Honest notes

- The toy-model scenes are labelled "our toy model" and carry the simulator's caveats: one light sensitivity for every switch, one threshold, an assumed 1 °C limit, no absorption outside blood (so the red result is a toy upper bound and is not shown as a number).
- No optogenetic therapy is approved as of 2026-10-06; one is under FDA review (claim C25). Check it again before reposting.
- The voice is synthetic (the open-source Kokoro voice `af_heart`, made on this machine). The music is a generated underscore, so no credits are needed.
- The end card links this repository. The video was made with [showtime](https://github.com/FavioVazquez/showtime), an open-source video studio for coding agents.

## Rebuild it

You need showtime 0.4.0 or later and Node 20+. From `project/`:

```bash
showtime voice script narration.md -o voice -s 1.08          # the voice (a few minutes on a laptop)
showtime retime . --from-voice voice/timeline.json --total 141
showtime check .
showtime render . --job nobel-medicine
showtime export html . --audio embed --folder -o ../interactive   # the page that asks
```

The heat-budget frames used by the scene about neurons (`assets/s10`) are included; to regenerate them run `python -m heat_budget.run_all` in [`../heat-budget`](../heat-budget).
