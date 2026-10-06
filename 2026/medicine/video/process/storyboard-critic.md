# Storyboard findings: Nobel 2026 Medicine, "the light switch" (pre-build critic read)

Read: `storyboard.md` (the plan) against `CLAIMS.md` (C01-C25). Nothing else. No frames exist yet, so "location" below is the shot number. Word counts are my own count of the narration cells; `{R..}` placeholders are counted at 3 words each unless noted.

Verdict: **not ready** for build. 5 blockers, all fixable in the script without a new shot. After fixes: ship after fixes.
WOULD I POST THIS (as planned): **no** -- two sentences say more than their ledger rows (shot 7 "real studies", shot 9 "started all this"), two drop the attribution the ledger requires (C04, C14), and the plan cannot be spoken in the time it gives itself.

---

## 1. FIRST VIEWER (cold: a stranger who knows no neuroscience)

- FIRST VIEWER shot 1: no -- a pretty fact (blue light, a cell fires, a Nobel) but no question and no stake; "that idea" has no referent, and I am not told why a cell firing in light is surprising or what the video will show me.
- FIRST VIEWER shot 2: yes -- names plus a four-step bar tell me the shape; but "light-gated ion channels" and "optogenetics" are spoken undefined, the step labels "our toy model" and "the limit" mean nothing yet, and I am not told I will be asked to guess.
- FIRST VIEWER shot 3: no -- why am I looking at an alga? Nothing says the nerve-cell story starts with an alga's protein; the question that ends the shot has no scale (I have no idea how fast a human eye is).
- FIRST VIEWER shot 3b: yes -- it is the answer to the question I was just asked; the link back to the opening (what speed has to do with a nerve cell) is still missing.
- FIRST VIEWER shot 4: yes -- the idea and the experiment, tied to the names from shot 2; but the story jumps back from 2004 to the early 1990s without a date, and "protein", "channel", "genes" arrive in one breath.
- FIRST VIEWER shot 5: yes -- this is the payoff of the opening; but "In 2005" re-tells shot 1's event with a different year and no bridge, and I am never told the alga's channel is what went into the nerve cell.
- FIRST VIEWER shot 6: no -- why is a toy model suddenly here, who is "our", and why red and yellow when the story so far is about blue light?
- FIRST VIEWER shot 6b: yes -- answers my guess; "ignores absorption outside blood" and "upper bound" are jargon, and the unlabelled 3 mW/mm2 line means nothing to me.
- FIRST VIEWER shot 7: no -- why heat, why now? The thread "reach is one limit, heat is another" is unspoken; the real 0.2-2 degree chip and the toy chart sit together and I cannot tell which is data.
- FIRST VIEWER shot 8: no -- "neurons recruited" per degree of warming, in what volume, and why do I care? Red disappears (greyed) after I was told it won shot 6, with no spoken reason.
- FIRST VIEWER shot 9: yes -- the limit and the echo of the opening blue pulse land; but the patient and FDA lines arrive with no "because", and the toy results are not tied to the limit.
- FIRST VIEWER shot 10: yes -- clear sign-off; no non-affiliation or "not medical advice" line.

---

## 2. Claims trace (every narration sentence that states a fact)

| Shot | Sentence | Row | Verdict |
|---|---|---|---|
| 1 | "Around one in the morning in August 2004, blue light made a nerve cell fire." | C11 | **Beyond/misleading.** Row: Boyden patched "the first neuron carrying channelrhodopsin-2" and saw it fire. Narration drops "carrying the channel", so any nerve cell seems to fire in blue light (the whole point of the story is that it does not without the protein). |
| 1 | "This week, that idea won a Nobel Prize." | C01 | **Beyond.** Row is dated 5 October 2026 ("this week" goes stale); the prize is "for their discoveries concerning light-gated ion channels and optogenetics", to three people, none of them the 2004 experimenter (Boyden, per C11). "That idea won" lets a viewer think the person in shot 1 is a laureate. |
| 2 | "Karl Deisseroth, Peter Hegemann and Georg Nagel share this year's prize, for light-gated ion channels and optogenetics." | C01 | OK in substance. Spoken form drops "discoveries concerning"; the card should show the exact quoted citation. Prize name only on screen in shot 1. |
| 3 | "an alga about fifteen thousandths of a millimetre wide that swims toward light" | C03 | OK ("across" vs "wide"). |
| 3b | "More than twenty times faster." | C04 | **Attribution dropped.** Row: "The Nobel Committee says". The ledger notes two committee documents disagree (half a millisecond vs "microseconds"), which is exactly why the attribution matters. |
| 3b | "Half a millisecond after light reaches its eyespot, an electrical impulse appears." | C04 | **Beyond.** Row says "about half a millisecond"; "about" is dropped, so is the committee. |
| 4 | "Peter Hegemann proposed that one protein could both catch light and act as a channel." | C05 | OK; drops "In the early 1990s" (needed, see S5). |
| 4 | "Many doubted it." | C05 | **Beyond.** Row: "met with scepticism". "Many" is a head-count the source does not give. |
| 4 | "Georg Nagel put algal genes into frog eggs, and when light hit them, the channels opened." | C06 | OK (drops "two" and "built the proteins in their outer membrane"). On-screen "blue light" is not in C06 (see S5). |
| 5 | "In 2005, blue light controlled how mammalian nerve cells fire, with millisecond timing." | C12 | OK in substance; passive voice hides that Nagel and Deisseroth are among the five authors. |
| 5 | "By 2007 Deisseroth's lab did it in living mice, through a thin optical fibre." | C14 | **Attribution dropped.** Row: "The Nobel Committee says"; the ledger note says to attribute "mice" to the committee because the paper itself says "rodents". "did it" is also ambiguous. |
| 5 (visual) | channel diagram "light arrives, channel opens, ions flow in, neuron fires" | C08 (+C06, C11) | Partly. C08 supports "positive ions flow in"; "ions flow in, so the neuron fires" is a causal chain no row states. |
| 6 | "A thin fibre sends blue, yellow or red light into brain tissue." | none (toy-model setup) | Allowed only as a toy-model description under the label; needs an R-id for the setup (R0) so the setup is traceable. |
| 6b | "But this model ignores absorption outside blood, so treat the red result as an upper bound." | R1 caveat | A model statement, not a ledger row. Must match the simulator's own caveat wording exactly. Open question: if the model ignores absorption outside blood, every colour's depth is overstated, not only red (see S8). |
| 7 | "Absorbed light becomes heat." | **none** | **No row.** Plain physics, but the rule is every factual sentence is a row. |
| 7 | "Real studies found common protocols warmed the brain by 0.2 to 2 degrees Celsius." | C22 | **Stronger than the row.** C22 is ONE study (Owen, Liu and Kreitzer, 2019), "commonly used light protocols", and it also "suppressed nerve-cell firing in several brain regions". Plural "studies" is wrong; the consequence that makes the number matter is omitted. On-screen chip "in real studies" has the same error. |
| 7 | "In our toy model, pulsing the light cuts the warming a lot." | R2 | **Rule break.** Toy-model results must be `{R2}` placeholders; "a lot" is a result asserted before the number exists. |
| 8 | "blue light recruits {R3a} and yellow {R3b}" | R3 | OK as placeholders. "Recruits" is jargon; no volume of tissue is named. "One degree" and "the heat limit" are model assumptions, no row gives a heat limit (C22 only says 0.2-2 degrees raised and suppressed firing). |
| 9 | "The limit is still the brain: visible light cannot penetrate deep." | C20 | **Beyond.** Row: "Optogenetics is limited because visible light cannot penetrate deep inside brain tissue" (a 2018 paper's sentence). "still" is a time claim the row does not make; "the brain" vs "brain tissue"; no source named. |
| 9 | "One blind patient regained partial sight in 2021" | C24 | **Beyond.** Row: "doctors reported partial recovery of sight in one blind patient after optogenetic gene therapy combined with light-projecting goggles". Dropping the therapy, the goggles and "reported" makes it a bare cure story. |
| 9 | "an optogenetic gene therapy is under FDA review, not approved" | C25 | **Attribution dropped.** Row: Nanoscope Therapeutics announced (9 Sept 2026) that FDA accepted its application; "not approved" is our reading, to be re-checked on publication day. As worded it reads as a neutral fact. |
| 9 | "One blue flash in 2004 started all this." | **none** | **No row, and contradicted by the video's own shots 4-5 and by C05, C07-C09, C15** (1990s proposal, 2002-03 papers, Crick 1999). |
| 9 (visual) | "the 2021 patient headline card" | C24 | A "headline" must be a real one. Use the Nature Medicine paper citation (Sahel et al. 2021), not a made-up news headline. |
| 10 | "Educational demos of this year's Nobel Prizes, made with showtime." | none | No factual claim. Fine. |

Unused rows that would help: **C15** (Crick 1999, "rather far-fetched": a ready-made puzzle for shot 1), **C02** (the committee chair's "dream of" line: the stake), **C08** (works in mammalian cells: the missing bridge shot 4 to 5), **C21** (real figure for "the brain scatters light": real support for shot 9). **R4** is named in the contract but appears in no shot.

Gap in the ledger: no row says the protein used in the 2004 neuron (channelrhodopsin-2) comes from the alga (C06 says "algal genes", C07 says ChR1 is from a green alga, C08 and C11 do not say where ChR2 is from). The whole thesis "an alga's protein became the brain tool" rests on that link. Add one row before any sentence asserts it.

---

## 3. Reading and speaking time (voice af_heart, 2.6 to 3.0 words per second)

| Shot | Length | Words | Needs at 3.0 / 2.6 wps | Verdict |
|---|---|---|---|---|
| 1 | 8 s | 23 | 7.7 / 8.8 s | Too dense for a cold open: no breath, no beat for the pulse and the firing. |
| 2 | 10 s | 22 | 7.3 / 8.5 s | OK; the 1.5-2.7 s left covers the roadmap build. |
| 3 | 15 s | 27 | 9.0 / 10.4 s | OK; 4.6-6 s left for the 3 s pause and the ring. |
| 3b | 4 s | 17 | 5.7 / 6.5 s | **Too dense by 2 s or more** (4.25 wps). |
| 4 | 12 s | 34 | 11.3 / 13.1 s | Too dense: four visual beats and three new nouns. |
| 5 | 11 s | 27 | 9.0 / 10.4 s | Fits, but the 4-step diagram cannot be read. |
| 6 | 15 s | 24 | 8.0 / 9.2 s | OK; room for the 3 s pause and the reveal. |
| 6b | 8 s | about 25 | 8.3 / 9.6 s | **Too dense**; the viewer must also read a chart and a caveat chip. |
| 7 | 11 s | 30 | 10.0 / 11.5 s | At the limit; chart and thermometer chip go unread. |
| 8 | 14 s | about 34 | 11.3 / 13.1 s | **No room for q3's pause** (needs 3 s more). |
| 9 | 12 s | 38 | 12.7 / 14.6 s | **Too dense** (3.2 wps). |
| 10 | 5 s | 10 | 3.3 / 3.8 s | OK. |

Totals: the shot lengths add up to **125 s**, not "about 100 s" (contract). About 312 words is 104-120 s of speech in 125 s, so the three pauses (3 s each at least) and every silent chart-reading beat do not fit. After the claim fixes in this file the script grows to roughly 150 s. The owner must choose: raise the contract to about 2:30, or take time out where it costs least (see S12: the patient and FDA lines are the least tied to the thesis and carry the most hype risk; the interactive page can keep them with full attribution).

Pauses: the plan names three question moments but gives no length and no sound. Specify: q1 (end of shot 3) 3 s of held silence with the timer ring; q2 (shot 6) 3 s; q3 (shot 8) 3-4 s (a three-way order-of-magnitude guess). Put the answer choices on screen as chips (no speaking time); do not read them aloud unless the line already does.

---

## 4. Story shape

- **Cold open with the puzzle:** missing. Shot 1 states an event; it never asks the question the film answers.
- **Roadmap:** present and persistent (good), but labels are opaque and the narration never reads them.
- **Bridges:** none are spoken. Missing at 1 to 3 (why an alga), 4 to 5 (alga's channel into a nerve cell), 5 to 6 (why model depth), 6b to 7 (why heat), 7 to 8 (why count neurons), 8 to 9 (so what).
- **A video that asks questions must say why before the first one:** shot 2 never says "you will be asked to guess".
- **Close answers the opening?** It echoes the blue pulse (good) but the contract's thesis "the limit is the brain, not the switch" is never spoken as a contrast, and the closing line overclaims (B3).
- **Questions giving the answer away:** q1 "How much faster than a human eye..." leaks the direction (faster) but not the size; mild. q2 and q3 do not leak in the spoken line, but the shot 6 visual draws "three coloured glows" before the question: if their extents differ, the answer is on screen.

---

## 5. Findings

### Blocker

- **B1 (shots 1-2): the opening has no puzzle and no stake, and spoken jargon is undefined.** Shot 1 says a thing happened and that "that idea" won; shot 2 says "light-gated ion channels and optogenetics". A stranger cannot say what the film is about or why it matters. Fix, shot 1 (about 10 s, 27 words, C11): "Can light switch on a brain cell? In August 2004, around one in the morning, a nerve cell carrying a light-gated channel fired in blue light." Keep the two on-screen type lines. Fix, shot 2 (about 11 s, C01, plus a stake): "This year's Nobel Prize in Physiology or Medicine went to Karl Deisseroth, Peter Hegemann and Georg Nagel, for their discoveries concerning light-gated ion channels and optogenetics. Four steps, and three guesses from you." Add a CLAIMS row that defines optogenetics in one plain sentence (from the popular background) so shot 2 or 4 can say what the word means; until then, show the committee's citation exactly and gloss it only with C12's own words. Optional stake, if time allows: C15 ("In 1999 Francis Crick wrote that light would be the ideal signal for switching neurons on and off, though he called the idea 'rather far-fetched'.") or C02 attributed to Per Svenningsson.
- **B2 (shots 3b and 5): the ledger's attributions are gone.** Fix 3b (13 words, about 5 s, C04): "The Nobel Committee says: more than twenty times faster than a human eye." Put "about half a millisecond after light reaches its eyespot" on screen only (it is already in the visual), with "about". Fix shot 5 (C14): "The Nobel Committee says that in 2007 Deisseroth's lab did it in living mice, using a thin optical fibre." Replace "did it" with "made the channel work in the brains of" if time allows.
- **B3 (shot 9): "One blue flash in 2004 started all this."** No row, and it contradicts shots 4 and 5 and C05, C07-C09, C15; it also erases two of the three laureates. Fix (C11, C20): "In 2004, one blue flash made a nerve cell fire. The switch works; the tissue is the limit." Do not use "started", "began", "led to".
- **B4 (shot 7): the heat sentences go past their rows.** (a) "Real studies found common protocols warmed the brain..." is one 2019 study (C22): "A 2019 study found commonly used light protocols raised brain temperature by 0.2 to 2 degrees Celsius and suppressed nerve-cell firing in several brain regions." Fix the chip to "0.2 to 2 degrees C, one 2019 study". (b) "cuts the warming a lot" must carry the number: "...pulsing the light cuts the warming by {R2}." (c) Delete "Absorbed light becomes heat." (no row; C22 already carries the point), or add a row first.
- **B5 (timing): the plan cannot be spoken as written.** 3b is 17 words in 4 s; shot 9 is 38 words in 12 s; shot 6b about 25 in 8 s; shot 8 has no room for q3's pause; the shots add up to 125 s against a 100 s contract. Resize per section 3: suggested lengths after the fixes below: 1 = 10 s, 2 = 11 s, 3 = 15 s, 3b = 6 s, 4 = 13 s, 5 = 15 s, 6 = 16 s, 6b = 9 s, 7 = 13 s, 8 = 15 s, 9 = 20 s (or split into 9a limit and 9b close), 10 = 5 s: about 148 s. Decide the contract length now (raise it, or move the C24/C25 lines to the interactive page).

### Should-fix

- **S1 (shot 1): "blue light made a nerve cell fire" hides that the cell carried the channel; "this week" goes stale; the on-screen pairing "Aug 2004" + "Nobel 2026" implies the 2004 scientist is a laureate.** Fix: B1's wording; add on-screen "Edward Boyden, 4 August 2004" (C11) and, in shot 2, "The prize went to three other scientists" (C01 lists three names; Boyden is not among them). Replace "This week" with the date "5 October 2026" on the citation card. Mark the single cell as "illustration".
- **S2 (shot 2): the roadmap labels are opaque and never spoken.** Rename on screen: "1 an alga, 2 the switch, 3 how far light goes (toy model), 4 the limit". Say "three guesses from you" (B1) so the questions have a reason before q1.
- **S3 (shots 2-3): no bridge says why an alga.** Add before step one: "It starts with an alga." and add the missing ledger row that the 2004 channel's protein is algal (see section 2). Until then, say only what C06/C07 say: "genes from an alga".
- **S4 (shots 3 and 3b): the reveal appears twice, and q1 has no scale.** Shot 3's visual says that after the ring "a bar...'more than 20 times faster'" appears, and 3b also says "the bar fills". Keep the bar and the text only in 3b; in shot 3 end on the ring. Put three answer chips on screen: "twice as fast / five times / more than twenty". Do not draw "10 ms" for the eye unless a row says it (the 10 ms figure is in C04's note, not its sentence); draw the eye's bar unlabelled, the alga's "more than 20 times faster", to no precise scale.
- **S5 (shot 4): chronology, "Many doubted it", density, and a stray colour.** Fix (C05, C06; 35 words, 13 s): "In the early 1990s, Peter Hegemann proposed that one protein could both catch light and act as a channel. Georg Nagel put algal genes into frog eggs, and when light hit them, the channels opened." Keep "met with scepticism" as the on-screen text only. In the frog-egg picture show neutral light, or cite C10 (blue peak about 460 nm for ChR2) if you want blue. Gloss "channel" on screen as "a gate in the cell's outer membrane" (C06 says the proteins sit in the outer membrane).
- **S6 (shot 4 to 5): the central step (the alga's channel into a nerve cell) is never spoken, and "In 2005" repeats shot 1's event.** Add the C08 bridge: "In 2003 the team showed one of these channels also works in mammalian cells." Then: "In 2005, blue light controlled how mammalian nerve cells fire, with millisecond timing." Name who in the on-screen credit (C12: Boyden, Zhang, Bamberg, Nagel, Deisseroth). Add on screen "2004: first fires (shot 1)" so the viewer places the opening on the timeline.
- **S7 (shot 5 visual): the 4-step diagram says "ions flow in, neuron fires" as a mechanism.** Label the step "positive ions flow in" (C08) and cite C08 in the Claims column; do not draw "ions in therefore fires" as a stated cause unless a row says it.
- **S8 (shot 6): why red and yellow, and does the model mislead.** The story's channel responds to blue (C10); showing red as "deepest" can read as "use red". Add: "The model asks only how far each colour travels, not whether the switch responds to it." Bridge in: "Light has to reach the neurons, so step three asks how far. Our toy model, an educational demo: a thin fibre sends blue, yellow or red light into brain tissue. Which colour reaches deepest?" (31 words). Keep "educational demo, toy model" on screen for every shot of step 3 (6, 6b, 7, 8), not only shot 6. Draw the three glows equal (or hide them) until the reveal so the answer is not on screen during q2.
- **S9 (shot 6b): the caveat may be wrong in kind, and the 3 mW/mm2 line is unexplained.** If the model ignores absorption outside blood, all three depths are overestimates, not only red; the greying of only the red row in shot 8 implies the others are fine. Either say "treat all three depths as best cases; red is least certain" (only if the simulator supports it) or state why red alone. Match the simulator's own caveat text exactly. Label the 3 mW/mm2 line "toy-model assumption: light a cell needs" and say it aloud, or remove it. Do not let it look like C21 (a different figure, 100 mW/mm2 at the tip). Spoken (about 23 words, 9 s): "{R1}. The model ignores absorption outside blood, so read red as an upper bound."
- **S10 (shot 7): real data and toy data are visually conflated.** The "0.2 to 2 degrees C" chip sits beside the toy chart. Caption the chip "published 2019 study" and the chart "toy model". Say what pulsing is compared against ("at the same peak power", or whatever the simulator holds fixed) so a viewer does not read the lower average as a trick. Add the bridge "Reach is one limit. Heat is another." (C22 supports heat).
- **S11 (shot 8): unanchored question, assumption shown as a limit, red unexplained.** Ask "In the toy model, how many neurons can one degree of warming switch on?" and say the volume of tissue on screen, or the answer number has no meaning. Replace "recruits" with "switches on". Label "toy-model budget: +1 degree (assumption)"; never "the heat limit" without "assumed" (no row sets a safe limit; C22 reports 0.2-2 degrees raising temperature and suppressing firing). Say why red vanishes: "Red is left out: its depth is only an upper bound." (add 8 words or keep it on screen only). Bridge: "Heat sets a budget. What does one degree buy?" Spoken (31 words, about 15 s with the pause): "In the toy model, how many neurons can one degree of warming switch on? Hundreds, thousands, or tens of thousands? Blue light switches on {R3a}, yellow {R3b}."
- **S12 (shot 9): the limit, the patient and the FDA line need sources and a "because".** Split into 9a and 9b. 9a (C20, about 8 s): "Step four, the limit. Optogenetics is limited because visible light cannot penetrate deep inside brain tissue. The switch works; the tissue is the limit." On-screen source chip "Chen et al., Science 2018"; drop "still". Optionally ground it with C21 ("Deisseroth describes fibre interfaces that deliver about 100 milliwatts per square millimetre at the tip, about 100 times more light than the cells need, because the brain scatters light") instead of leaving the toy model carrying the real claim. 9b (C24, C25, about 11 s): "In 2021 doctors reported partial recovery of sight in one blind patient, after gene therapy and light-projecting goggles. Nanoscope Therapeutics says its optogenetic therapy is under FDA review; it is not approved." Re-check C25 on publication day (ledger note). Say why the eye comes up (the retina is where light arrives) only if a row is added; otherwise present these as "what has happened so far", not as an answer to the limit. Replace the "headline card" with the paper citation (Sahel et al., Nature Medicine, 2021).
- **S13 (pauses): the three question beats are unspecified.** See section 3: 3 s / 3 s / 3-4 s of silence, a timer ring, answer chips on screen, and the reveal only after the ring ends. Say the same four-second rule in the interactive page spec so the MP4 and the page agree.
- **S14 (shot 10): end card.** Add on screen "Unofficial. Not affiliated with the Nobel Foundation." and "Not medical advice" (the film mentions a therapy and a patient). Add a source line ("Sources: nobelprize.org press release and popular background; claims ledger in the repo").

### Polish

- **P1 (shots 2, 4, 5): names.** Deisseroth, Hegemann, Nagel will be mispronounced by a default Kokoro read: give the voice director respellings (for example "DYE-ser-oth", "HAY-guh-mahn", "NAH-gul") and listen before lock.
- **P2 (shot 2): quote the citation exactly** on the card with quote marks: "for their discoveries concerning light-gated ion channels and optogenetics." The spoken form drops "discoveries concerning".
- **P3 (shot 3, q1):** "faster" in the question gives the direction away; alternative "How does it compare with a human eye: twice as fast, five times, or more than twenty?" Also "reacts" (behaviour) vs the row's "an electrical impulse appears": say "how quickly it senses light".
- **P4 (title and shots 1-5): the "switch" metaphor never appears in the narration** until the close. Say it once in shot 4: "one protein that both catches light and acts as a channel: a light switch for a cell".
- **P5 (shot 8): "buy"** is a currency metaphor; use "switch on" (S11).
- **P6 (contract): R4** is named but used nowhere. Cite it or drop it from the contract line.
- **P7 (shot 9): hold the echo** (the opening blue pulse) a full 1.5 s of silence before the end card; it is the only moment the story's loop closes.
- **P8 (shots 6-8): label wording.** Use the same words every time: "educational demo, toy model". The narration says "toy model" and "this model" interchangeably; use "toy model".
- **P9 (shot 3 visual):** "swimming toward a lamp" is an illustration; mark it so a viewer does not read it as footage.

---

## 6. What works (keep through the fixes)

- The persistent four-step roadmap with the current step lit.
- Three guesses as a spine (alga speed, deepest colour, neurons per degree); the pause-and-think design.
- The toy model is labelled as a toy model, and a caveat chip rides on the red result.
- Placeholders `{R1}-{R3}` instead of invented toy-model numbers.
- "under FDA review, not approved" is stated plainly; "met with scepticism" and "about 0.015 mm" are used with their qualifiers on screen.
- The ending returns to the opening blue pulse.
- Showtime credited only on the end card.

## 7. Declined to judge

- How Kokoro says the names and "millisecond", "eyespot", "channelrhodopsin": no audio exists yet.
- Whether any shot looks right (no frames).
- Whether the simulator's caveat wording matches shot 6b, whether only red is truly an upper bound, what the 3 mW/mm2 line represents, and R1-R4: I was not given the simulator results or documentation.
- The pronunciation or fit of music.

## 8. Best poster frame (when it exists)

Shot 1, final frame: the dark field, the single neuron at the instant of the blue pulse, with the two type lines "around 1 a.m., August 2004" and "Nobel Prize in Physiology or Medicine 2026".
