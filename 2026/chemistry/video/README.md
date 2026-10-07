# Chemistry 2026: one hand wins (video, 2:30)

> **Educational demo, toy models. Not research.** Made with [showtime](https://github.com/FavioVazquez/showtime), an open-source video studio for coding agents.

A two-and-a-half-minute explainer of this year's Nobel Prize in Chemistry. It covers why life uses only one hand of its mirror-image molecules, Charles Frank's 1953 three-part recipe for one hand to take over, and how Henri Kagan (1986) and Kenso Soai (1995, 2003) each ticked a box. It then shows our own toy [mirror race](../mirror-race/README.md), says honestly what the toy does not show, and ends on why it matters for medicines. It asks the viewer no questions: it simply tells the story. The other toys are [Kagan's curve](../kagan-curve/README.md) and [Soai's amplifier](../soai-amplifier/README.md), and you can try all three on [the page](https://faviovazquez.github.io/nobel-2026-lab/2026/chemistry/page/).

| File | What it is |
|---|---|
| [`exports/nobel-2026-chemistry.mp4`](exports/nobel-2026-chemistry.mp4) | The video: 1920x1080, 2:30, 9.7 MB (the GitHub-size copy of the master), -14 LUFS, captions burned in |
| [`exports/poster.jpg`](exports/poster.jpg), [`exports/og.jpg`](exports/og.jpg) | The thumbnail frame ("One hand wins.") and a 1200x630 share image |
| [`storyboard.md`](storyboard.md), [`project/narration.md`](project/narration.md) | The plan and the exact words spoken. The storyboard's claim ids (H1-H13, F1-F8, T1) were the working ids; the table below gives the ledger ids |
| [`project/`](project) | The video's source (HTML scenes, timing, audio plan), rebuildable with showtime. The narration audio is not stored; showtime re-voices it from narration.md (voice af_bella, speed 1.08) |
| [`process/`](process) | The critics' reports: one on the plan before anything was built, two blind critics on the first cut, and one on the fixed cut, so you can see what was caught before it shipped |

## What it says, and where each fact comes from

Every factual sentence is a row of the [claims ledger](../CLAIMS.md) (ids in the last column). The toy-model result in scene 9 comes from the [mirror race](../mirror-race/README.md) and is always labelled "our toy model · trend only", with our chosen rates on screen.

| Time | Scene | Narration | Claims |
|---|---|---|---|
| 0:00.0 | 1 cold open | Your hands are mirror images. This year's Nobel Prize in Chemistry is about how one hand can take over. | C01, C06, C21 |
| 0:07.6 | 2 life picks one | Many molecules come in two hands like that. Life is picky: your proteins use only one hand of each amino acid. | C06, C07 |
| 0:15.7 | 3 fifty-fifty | Yet a reaction left to itself makes both hands, fifty-fifty. A one-handed catalyst, a helper that isn't used up, can tip the balance. | C09, C10 |
| 0:25.2 | 4 Frank's recipe | In nineteen fifty-three, Charles Frank wrote a recipe for one hand to take over completely. One: a one-handed catalyst; chemists had that by the early nineteen hundreds. Two: boost one hand and hold back the other. Three: a reaction that makes its own catalyst. | C27, C39 |
| 0:43.1 | 5 Kagan's bend | In nineteen eighty-six, Henri Kagan ticked box two. His insight: the catalyst's metal holds two pieces, so mixed hands make three kinds of pairs, and the mixed pair barely works. Start seventy-five to twenty-five, and the working catalysts are ninety to ten: a purer product than a straight line predicts. | C39, C14, C15, C16, C12 |
| 1:04.1 | 6 Soai's copier | In nineteen ninety-five, Kenso Soai ticked box three: a molecule that helps build more of itself, same hand, from simple ingredients. | C39, C19 |
| 1:13.8 | 7 the staircase | In two thousand three, his team started with a lead of five parts in ten million. Each run's product seeds the next: fifty-seven percent after one run, ninety-nine after two, past ninety-nine and a half after three. | C21, C22 |
| 1:29.1 | 8 the coin flip | Then, with no one-handed ingredient added, the reaction still picked a hand, at random. In thirty-seven runs, nineteen leaned one way, eighteen the other. | C24 |
| 1:39.9 | 9 our mirror race | In our toy model, copying alone isn't enough: ten thousand runs end up anywhere. Add box two, where a one-hand and a mirror molecule pair up and stop working, and nearly every run ends with one hand taking over. Which hand is a coin toss. | toy (mirror race), C39 |
| 1:57.4 | 10 the caveat | A toy, not how life chose its hand. The Nobel Committee stresses Frank's model isn't the answer to life's origin, and how Soai's reaction works is still debated. | C28, C30 |
| 2:08.6 | 11 why it matters | Choosing the hand matters for medicines: one form does the job, and its mirror image can cause unnecessary, sometimes harmful, side effects. | C32, C33 |
| 2:19.0 | 12 end card | Race the mirrors yourself in our open Nobel 2026 lab. Explained with showtime, an open-source video studio for coding agents. |  |

## Honest notes

- **"Lead" means enantiomeric excess (ee):** the % of one hand minus the % of the other. The video defines it on screen in scene 7. A lead of 57% means about 78.5 : 21.5.
- **Kagan's 75:25 example** uses the Nobel Committee's own numbers (popular background, figure 4). The drawing is ours, and the 90 : 10 is the share of *working catalysts*, not of the product. The curve in scene 5 is a shape only, not Kagan's data.
- **Soai's 2003 numbers** (0.00005% to 57%, 99% and over 99.5% in three runs) are the published ones. The 0.00005% was a head start the chemists put in, not a chance imbalance (C22). The 1995 numbers disagree between sources, so they are not shown (C20).
- **The 37 runs** (19 one hand, 18 the other) each ended only partly one-handed, with a lead of 15-91%. The flask tints are illustrative.
- **Scene 6** shows only that the molecule helps build more of itself. It does not draw a mechanism, because how the Soai reaction amplifies one hand is still debated (C30).
- **Our mirror race** (scene 9) is a Frank-type toy model with rates we chose: background as fast as copying, and strong pairing. The flat spread holds only for that choice; see the [mirror race README](../mirror-race/README.md). It is not the Soai reaction, and not the origin of life (C28).
- **The medicine keys** in scene 11 are our drawing of the Nobel popular text's lock-and-key idea. Nothing in the video says or implies that one-handed thalidomide would have been safe (C35).
- **The music** is "I'm glad you are here with me" by Loyalty Freak Music (CC0). The voice is Kokoro af_bella, made locally.
