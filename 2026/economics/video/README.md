# Economics 2026: the lab with three equations (video, 2:48)

> **Educational demos made to show an open-source tool. Not research, and not economic or policy advice.** Made with [showtime](https://github.com/FavioVazquez/showtime), an open-source video studio for coding agents.

A two-minute-and-a-half explainer of this year's prize in economic sciences, drawn as a living diagram. It opens with Robert Hall's question (a line of one household's spending dots: try to predict the next), shows the older machine of links between big totals and why the committee says it broke in the 1970s, then builds the model Michael Woodford's 2003 book set out as three connected parts (households, firms, a central bank with a rate rule), wires them in a loop and runs it as a laboratory: a burst of spending, an energy-cost shock with a stronger rule, the condition on the rate, and a promise about the rate two years out, with the forward guidance puzzle as its stated limit. It ends on what the model leaves out. It takes no side on any policy, school of economics or central bank. Every model number in it is the textbook model's, with the label "Textbook model, illustrative calibration".

| File | What it is |
|---|---|
| [`exports/economics-2026-lab.mp4`](exports/economics-2026-lab.mp4) | The video: 1920x1080, 2:48, 23.0 MB (the GitHub-size copy of the master), -14.0 LUFS integrated, -1.8 dBTP true peak |
| [`exports/economics-2026-lab.srt`](exports/economics-2026-lab.srt) | The captions as a separate file (the narration, 71 cues) |
| [`exports/poster.jpg`](exports/poster.jpg) | The thumbnail frame (at 98.4 s) |

Only the finished film, its poster and its captions are kept here. The film's source and the critics' reports are not in this folder.

## How it was made

With [showtime](https://github.com/FavioVazquez/showtime): the scenes are an HTML and canvas "living diagram" (parts, flows, counters, a moving camera) that showtime renders frame by frame on one computer, with a local voice, a music bed, captions and checks. The look is a ledger: engraving on ledger paper, green ink with one crimson accent (Fraunces, Inter and JetBrains Mono, all under the SIL Open Font License). The narration is not burned into the picture; use the .srt.

## Credits

```text
Quotes and facts: Royal Swedish Academy of Sciences, press release, popular information and scientific background,
  12 October 2026, https://www.nobelprize.org/prizes/economic-sciences/2026/press-release/
Prize data: Nobel Prize API (api.nobelprize.org), CC0. No endorsement by Nobel Prize Outreach or the Royal Swedish
  Academy of Sciences is implied.
Papers named: Hall (1978), Journal of Political Economy 86(6); Hall and Mishkin (1982), Econometrica 50(2);
  Woodford (2003), Interest and Prices, Princeton University Press; Galí (2015), Monetary Policy, Inflation, and the
  Business Cycle, ch. 3 (the model's calibration); Del Negro, Giannoni and Patterson (2023), The Forward Guidance
  Puzzle.
Model: the toy "set-the-rate" in this lab (a textbook three-equation model with an illustrative calibration; not an
  estimate for any economy).
Music: Erik Satie, "Gymnopédie No. 1" (Lent et douloureux), performed by Robin Alciatore for Musopen, public domain
  (CC-PDDC), via Wikimedia Commons.
Voice: synthetic, Kokoro-82M (voice bm_george), Apache-2.0.
Made with showtime, an open-source video studio for coding agents: https://github.com/FavioVazquez/showtime
Educational demos made to show an open-source tool. Not research.
```

No portrait, medal or illustration of the committee's is used.

## What it says, and where each fact comes from

Every factual sentence is a row of the [claims ledger](../CLAIMS.md) (section 24, "The film": E250 to E275; the rows behind them are named in each). The film shows only the textbook model's results, not the data toy's. Times are when the voice starts each beat.

| Time | Scene | Narration (and what is on screen) | Claims |
|---|---|---|---|
| 0:00 | Hook | Here is one household's spending, quarter by quarter. Try to predict the next one. (A line of dots with three faint guesses; labelled illustrative.) | E250 |
| 0:07 | Prize | This year's economics prize went to Robert Hall and Michael Woodford, for separate pieces of one idea. | E251 |
| 0:14 | Hall's question | Robert Hall turned the question around. A household that looks ahead changes spending only when news arrives. And news can't be predicted, so neither can the change. ("Hall, 1978 · after Friedman".) | E252, E253 |
| 0:25 | The test | In 1978 he tested it on US data: little predicted the change. It became a benchmark. | E254 |
| 0:32 | Hand to mouth | Then, with Mishkin, he measured the exceptions: in their sample, about a fifth of spending tracked income. ("US food spending, 2,309 families, 1969-1975: about 1/5 of spending tracked income.") | E255 |
| 0:40 | The older machine | That was Hall's piece. Woodford's starts with an older machine. Older models ran on links between big totals. In the oil crises of the nineteen seventies, the committee writes, they broke. | E256 |
| 0:53 | Lucas | Robert Lucas argued models needed foundations: the decisions themselves. | E257 |
| 0:59 | Build | Woodford, with Julio Rotemberg, building on Taylor, Calvo and others, put it into three equations. | E258 |
| 1:07 | Equation 1 | One. Households look ahead: they spend more today when the real rate is below the natural rate, which neither speeds nor slows spending. Knut Wicksell's idea. | E259 |
| 1:18 | Equation 2 | Two. Changing prices is costly, so firms set them looking ahead. Inflation rises when output runs above its natural level: the output gap. | E260 |
| 1:28 | Equation 3 | Three. The central bank follows a rule: when inflation rises, raise the rate. | E261 |
| 1:34 | The loop | Wire them up, and each part moves the next. | E262 |
| 1:39 | The lab | Now it's a laboratory. (The committee's phrase "A kind of laboratory for policymakers.", credited.) | E263 |
| 1:41 | Experiment 1 | Send in a burst of spending: households want more, now. The gap opens, inflation rises, the rule lifts the rate, and spending cools. | E264 |
| 1:51 | Experiment 2 | An energy-cost shock hits firms: inflation up, output down. The rule still raises the rate. Turn the rule up: inflation rises less; the dip is deeper. (+1.3, -0.5; then +0.8 and -0.8; "Textbook model, illustrative calibration".) | E265, E266 |
| 2:04 | Experiment 3 | If inflation rises one point and the rate less than one point, the model loses its anchor: many paths are possible. | E267 |
| 2:13 | Experiment 4 | The wires carry words too. To people who look ahead, a promise is news. A lower rate promised two years out moves prices now. | E268 |
| 2:23 | The limit | Hold the rate still until then, and in this simple model, the further out the promise, the bigger today's effect, implausibly so: the forward guidance puzzle. | E269 |
| 2:33 | Close | A laboratory, not an oracle: it leaves out the floor on rates near zero, investment, and any real central bank. Its core: an economy built from decisions that look ahead. (Sources line; "Educational demo, not research".) | E270, E271, E273 |

The on-screen numbers, in one place (E272): 1978, 1982, 1995, 2003, 1898, 2,309 families, 1969 to 1975, about 1/5, and the textbook model's +1.3, -0.5, +0.8, -0.8, +1 and +0.8. The first set are prize and paper facts; the second are the [set-the-rate toy](../set-the-rate/README.md)'s results (`cost_push_shock.baseline.impact`, `cost_push_shock.strong.impact`, `taylor_principle`), rounded. The music and voice credits are E274 and E275.

## Honest notes

- The film shows a model. Its numbers are results of a textbook model with an illustrative calibration, not facts about any economy, and not forecasts.
- Committee lines are quoted only as the committee's words. The film adds no verdict on whether stabilisation policy works.
- The "oil crises" and "after Friedman" wordings are short forms of the committee's text (see E253 and E256).
- The one household's dots in the opening are an illustration, not data.
