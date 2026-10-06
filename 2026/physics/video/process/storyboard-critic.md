# Storyboard findings: Nobel 2026 Physics, "a telescope made of ice" (pre-build critic read)

Read: `video/storyboard.md` against `facts.md` (sections 1-6), `experiment-ideas.md`, `PLAN.md`, the two Devin briefs in `build/`, and the Glashow viewer report. No frames, no audio and no toy results exist yet (`build/` has no reports), so "location" means the shot number. My word counts are spoken words: years count as spoken ("nineteen eighty-eight" = 3 words), placeholders as spoken ("a hundred thousand" = 3 words).

Verdict: **not ready to build**. There are 6 blockers. All can be fixed in the script and the on-screen text, and none needs a new kind of scene.
Would I post it as planned? **No.** The 2013 card is false: neutrinos from beyond the solar system were first seen in 1987, from SN 1987A. The close says the prize is for a flux "from beyond our galaxy", but the committee's own cited result is neutrinos from our galaxy. Shot 3b gives away q3, and its number can contradict the committee's number. Five shots cannot be spoken in the time they are given.

---

## BLOCKERS

### B1 (shot 7 visual): the 2013 card says "first neutrinos from beyond the solar system". That is false.
The Kamiokande burst from supernova 1987A came from the Large Magellanic Cloud in 1987 (facts.md section 3, "Background": NOBEL-POPULAR, NOBEL-ADV p. 1). That work is part of Koshiba's 2002 prize. Any physicist will reply with this. The card also mixes up two papers. Bert and Ernie were the July 2013 PRL, at 2.8 sigma, "a first indication". The *evidence* was the November 2013 Science paper: 28 events, 4 sigma (facts.md section 3, "Discoveries"). A "28 events" label would also clash with q3's "about a hundred a year", and it is a different selection.
- Card, exact rewrite: **"2013: first evidence of high-energy neutrinos from outer space (Science, Nov 2013). Two of them, above 1 PeV, were nicknamed Bert and Ernie."** Do not show "28 events".
- Add a second small card **"2014: confirmed (5.7 sigma)"** (PRL 113, 101101, facts.md section 3). The narration says "evidence" and shot 9 says "discovery". This card is the bridge between the two words, at no speaking cost.
- Rename the claim tag `[2013-discovery]` to `[2013-evidence]` so the CLAIMS row is not written as "discovery".
- The narration line is fine as it is ("first evidence of high-energy neutrinos from outer space"). "High-energy" is what keeps it true, so never drop it.

### B2 (shot 9, contract, shot 2): what the prize is for, "from beyond our galaxy", and "one galaxy is evidence"
- "The prize is for discovering this flux of neutrinos from beyond our galaxy" goes past every source.
  - The citation is "for decisive contributions to the IceCube Neutrino Observatory **and** the discovery of high-energy neutrinos of astrophysical origin" (facts.md section 1). The line drops the instrument half.
  - The citation says "astrophysical origin", not "beyond our galaxy". The committee says the sources are "*predominantly* extragalactic" (NOBEL-ADV pp. 12-15).
  - The committee also cites the Milky Way at 5.7 sigma as "the first source of high-energy neutrinos above the 5 sigma threshold" (facts.md section 3, 28 July 2026; NOBEL-ADV p. 12). Saying the prize flux is "from beyond our galaxy" invites the obvious reply.
  - "Flux" is spoken jargon that is never defined.
- "One galaxy is evidence" is ungrammatical, and it implies NGC 1068 is the only candidate (TXS 0506+056 and the Galactic plane are not). Do not use "best" or "strongest" either, because the Milky Way is the highest-significance source.
- Shot 9, exact rewrite, short (25 words, about 9-10 s): **"The prize honours that discovery: high-energy neutrinos from space. Which objects make them is still open: one nearby galaxy shows evidence, not yet proof."** Claims: [prize], [prize-scope], [ngc1068]. "Nearby" is the wording of IceCube's own NGC 1068 release title.
- Optional longer form, if you want the extragalactic point (+8 words): "...high-energy neutrinos from space, mostly from beyond our galaxy, the committee says. ..." Use it only with the attribution.
- Shot 9 visual chip: keep "NGC 1068: evidence, 4.2 sigma, not yet proof", and add "(Science, 2022)". Label the sky map "illustration".
- Contract line, rewrite: "...and ends knowing what was discovered (high-energy neutrinos from space) and what is still open (which objects make them)."
- Shot 2: see S1 (the citation is also trimmed there).

### B3 (shot 3b): the size chart and {K3} give away q3, and can contradict shot 8b
"Grow the detector to a cubic kilometre and the rare hits add up: about {K3} a year." The Devin brief defines K3 as our toy model's yearly count of astrophysical-flux interactions in 1 km^3 above 60 TeV.
1. That is the answer to q3, spoken five shots before q3 ("about 100").
2. If K3 comes out at 20-40 (a 60 TeV contained-style count is roughly that), the viewer hears "about 30 a year" (our toy model) and then "about a hundred, the Nobel Committee says". Two numbers for the same thing, which reads as a contradiction. It is the Medicine "close contradicts an earlier scene" failure, and it invites "the toy doesn't match IceCube" replies.
3. "Grow the detector to a cubic kilometre" is confusing, because q1 already put the neutrino through a whole kilometre.

- Shot 3b, exact rewrite (17 words, about 6-6.5 s; shot length 8 s): **"In our toy model, about one in {K1}. So the detector had to be huge."**
- Visual: keep only the odds chart (chance to interact vs energy, 100 TeV marked, "our toy model").
- Drop the 10 m / 100 m / 1 km events-per-year bars from the video. They belong on the interactive page after q3. If you must keep a size beat, use years-per-event for the 100 m cube only ("in our toy model, a cube a hundred metres wide would wait about {Y100} years for one"), never the 1 km number.
- "So the detector had to be huge" also gives shot 4 its bridge ("Step two: the telescope").

### B4 (shots 1 and 9): the cold open has no puzzle, and the close cannot answer one
Shot 1 states two facts and asks nothing (the same failure as Medicine B1). The close ("A cubic kilometre of ice, still watching") is an answer with no question.

The tie-back visual has two problems:
- The fingertip stream is *solar* neutrinos. IceCube's 100,000 a year are above 0.1 TeV, and its prize neutrinos are astrophysical. One gold dot from the Sun's stream "stopping in the ice" says IceCube catches solar neutrinos.
- A neutrino does not "stop". It interacts and makes light.

- Shot 1, exact rewrite (26 words, about 9-10 s; shot length 11 s): **"About sixty-five billion neutrinos from the Sun pass through your fingernail every second, and almost none of them touch anything. So how do you catch one?"** Claims: [fingernail], [rarely-interact].
- Shot 1 poster type lines: "65 billion neutrinos from the Sun, through one fingernail, every second" / "How do you catch one?" / "Nobel Prize in Physics 2026". The bare "65 billion per second" has no subject.
- Split shot 9 into 9a (the open question, B2 text, 11 s) and 9b (the tie-back, 7 s).
- 9b exact narration (14 words, about 5 s, plus a 1.5 s silent hold): **"So how do you catch one? With a cubic kilometre of ice, still watching."**
- 9b visual: the fingertip stream (labelled "from the Sun") runs on. Cut to the ice block, where one dot from a different direction (gold, labelled "from space") makes a blue flash among the strings. No "stopping". Hide the roadmap bar for the last 1.5 s.

### B5 (timing): five shots cannot be spoken in their length, and the beats have no time
At 2.6-2.9 words/s, with a 3.5 s question beat inside shots 3, 6 and 8:

| Shot | Length | Words | Speech at 2.9 / 2.6 wps (+ beat) | Verdict |
|---|---|---|---|---|
| 1 | 10 s | 19 | 6.6 / 7.3 s | OK (needs 11 s after the B4 question) |
| 2 | 9 s | 22 | 7.6 / 8.5 s | Tight; 0.5-1.4 s for the roadmap build (13 s after S1) |
| 3 | 11 s | 24 | 8.3 / 9.2 + 3.5 = 11.8 / 12.7 s | **Does not fit** |
| 3b | 9 s | ~29 | 10.0 / 11.2 s | **Too dense** (and the viewer must read two charts) |
| 4 | 13 s | ~35 | 12.1 / 13.5 s | At the limit, with four visual beats (drill, drop, hexagon, labels) |
| 5 | 9 s | 28 | 9.7 / 10.8 s | **Too dense** |
| 6 | 12 s | 35 | 12.1 / 13.5 + 3.5 = 15.6 / 17.0 s | **Does not fit (worst: 4-5 s over)** |
| 6b | 8 s | ~18 | 6.2 / 6.9 s | OK, but little time to read a chart plus a caveat chip |
| 7 | 13 s | ~36 | 12.4 / 13.8 s | At or over the limit |
| 8 | 8 s | 18 | 6.2 / 6.9 + 3.5 = 9.7 / 10.4 s | **Does not fit** |
| 8b | 7 s | 15 | 5.2 / 5.8 s | OK |
| 9 | 13 s | 34 | 11.7 / 13.1 s | At the limit, with no room for the tie-back beat |
| 10 | 4 s | 10 | 3.4 / 3.8 s | OK (5 s is safer) |
| **Total** | **126 s** | **~323** | 111-124 s of speech + 10.5 s of beats = 122-135 s | Does not fit in 126 s |

After the fixes in this file (full script in section "Proposed narration" below) the honest length is **about 2:35** (156 s at 2.6 wps; about 2:25 at 2.9 wps), against "about 2 minutes". The owner decides:
- (a) retitle to about 2:30; or
- (b) cut about 15 s where it costs least:
  - speak only "In 2016 it caught this one" in shot 7 and put "about 6 PeV, real data" on screen (-3 s);
  - use the short shot 9a (already used above);
  - drop the spoken "an educational demo" in shot 6, which the permanent label keeps on screen (-1 s);
  - drop the spoken numbers in shot 4 and keep them on screen (-3 s);
  - merge shot 5's cone explanation into shot 6's opening over the 3D event (-6 s).

Specify the beat: **3.5 s of held silence, timer ring, answer chips on screen**, reveal only after the ring. Write the same rule into the interactive page spec.

### B6 (shot 7): licence for the real replay. Decide before building.
PLAN.md (Update 6 Oct, Glashow bullet): "Until a yes: ... the video's event scene uses our own simulated shower and says so; the real replay goes in only with a yes." The storyboard assumes the real replay ("the shot from today's reply"). The release has no stated licence (DataCite shows no rights; experiment-ideas C2).
- If data@icecube.wisc.edu said yes, or the owner accepts the risk (for example because today's reply already showed it publicly), write that decision into PLAN.md or OPEN.md before the build. Then credit **"Data: IceCube Collaboration, DOI 10.21234/gr2021"** on shot 7 and on the end card.
- Otherwise build shot 7 on our own simulated shower, with this narration: **"In 2016 it caught a shower of about six peta-electronvolts. Here, our simulation of one like it."** (16 words) The label "our simulation, not the real event" stays on screen.

---

## SHOULD-FIX

### S1 (shot 2): the citation is cut to "for IceCube", and the team is erased
"For IceCube" drops "decisive contributions to" and the whole discovery half of the citation. With a single laureate and a roughly 450-person collaboration, a physicist will also note that nobody else appears.
- Exact rewrite (33 words, 11.4-12.7 s; shot length 13.5 s): **"This year's Nobel Prize in Physics went to Francis Halzen, for decisive contributions to IceCube, a telescope made of Antarctic ice, and the discovery of high-energy neutrinos from space. Four steps, three guesses."**
- Shorter alternative (29 words, 12 s): drop "decisive contributions to" and "This year's", but only if the card shows the exact citation in quote marks.
- Card: the exact citation in quote marks, readable (not "small type").
- Add one on-screen line: "IceCube Collaboration: about 450 people, 58 institutions, 14 countries (Nobel Committee)" (facts.md section 2, NOBEL-ADV p. 2).
- No portrait and no Nobel illustrations: their licence is not cleared (facts.md section 1, Jarnestad note). Use the name card only.

### S2 (shot 4): Learned is dropped, Halzen's actual role is missing, and 1988 jumps straight to 86 holes
The committee names "Halzen and J. Learned" for the 1988 idea (NOBEL-ADV p. 7). The citation's "decisive contributions" are PI-from-the-start and leading the build (NOBEL-ADV pp. 2, 15; Pearce quote). Neither is spoken. "Hot water melted eighty-six holes" straight after 1988 hides 16 years.
- Exact rewrite (37 words, 12.8-14.2 s; shot length 15 s): **"Step two: the telescope. In 1988, Halzen and John Learned proposed using the ice itself. Halzen then led the team that built it: eighty-six holes, two and a half kilometres deep, over five thousand light sensors."**
- On screen: "melted with a hot-water drill, 2004-2010", "86 strings", "5,160 sensors", and depth marks 1,450 m and 2,450 m.
- New claim tags: [1988-idea] must name both men; add [led-construction].
- facts.md has only "J. G. Learned". Add "John" to the CLAIMS row with a source (for example the Halzen-Learned 1988 preprint), or say "Halzen and a colleague, John Learned" only after checking.

### S3 (shot 3, q1): the energy is unnamed, and "leaves a trace" is not what K1 measures
K1 (`one_in_N_100TeV`) is the chance to *interact* in 1 km, and it changes about 3-5 times between 100 TeV and 1 PeV. "Leaves a trace" sounds like "detected", which is a different and smaller number (Halzen's famous "one in a million at 1 TeV" is a detectable-muon probability, so a physicist may cross-wire the two).
- Exact rewrite (25 words, 8.6-9.6 s + 3.5 s beat; shot length 14 s): **"Step one: the ghost particle. Guess: a high-energy neutrino crosses a whole kilometre of ice. What are the odds it hits anything on the way?"**
- On screen, with the question text: "at 100 TeV (100 trillion electronvolts)".
- Chips (100x apart; the middle one stays right for any toy value from about 1 in 10,000 to 1 in 1,000,000, so far more than a factor of 3 either way; my hand estimate is 1 in 50,000-100,000 at 100 TeV and about 1 in 25,000 at 1 PeV): **"1 in 1,000" / "1 in 100,000" / "1 in 10 million"**.
- Round the spoken reveal to one significant figure.
- The three untouched arrows in the visual hint "rare", which is fine because every chip is rare.

### S4 (shots 6 and 6b, q2): speak the toy as a ratio, not as degrees "at IceCube's spacing"
"About {T1} degrees at IceCube's spacing" will be read as IceCube's aim, whatever "trend only" says. The real figure is about 0.3 degrees for 100 TeV tracks (facts.md section 4, item 7). The spike's tuned toy gives about 0.5, so the reply writes itself. The storyboard also does not say which fit. In the spike, the line fit gets only about 2x worse from 125 to 250 m, and the Pandel fit about 6x.
- Use the Pandel fit, and synthetic hex grids at 125 m and 250 m for both points so the ratio is like with like.
- Shot 6, exact rewrite (37 words, 12.8-14.2 s + 3.5 s beat; shot length 18 s, or 17 s without "an educational demo" spoken): **"Step three: our toy telescope, an educational demo. From the light's arrival times alone, it works out which way the particle was going. Guess: space the strings twice as far apart. How much worse does it aim?"** Before, the line said "where the particle came from"; the fit gives a direction, not a source.
- Chips (they partition the range; the middle one is right for any Pandel ratio from 1.5x to 20x, which covers the spike's about 6x within a factor of 3 either way): **"Barely worse (under 1.5x)" / "A few times worse (1.5x to 20x)" / "Over 20 times worse"**. Check the final number: if it falls outside 1.5-20, move the chips, not the wording.
- Shot 6b, exact rewrite (19 words, 6.6-7.3 s; shot length 9 s): **"In our toy model, about {T2/T1} times worse: fewer sensors see the light. Trend only, not IceCube's real aim."** Put the degree values on the chart only, next to the existing caveat chip.
- Keep "our toy model: educational demo" on screen for all of 6 and 6b, and keep the 125 m mark (add tag [spacing-125]).

### S5 (shot 5): "outruns light", the ambiguous "it", density, and the cone-versus-shower mismatch in shot 7
"Outruns light" is heard as "faster than light". "The sensors record when it arrives": which "it"? Shot 5 teaches a *cone* from a track, and shot 7 then shows a *shower* (a ball of light), with nothing to say why it looks different.
- Exact rewrite (28 words, 9.7-10.8 s; shot length 11.5 s): **"When one does hit, it makes a charged particle faster than light travels in ice. It leaves a cone of blue light, and each sensor times its arrival."** Claim: [cherenkov] (facts.md section 4, items 1-2).
- Shot 7 on-screen note: "A shower: the light spreads like a ball, not a cone" (facts.md section 4, item 7, "roughly spherical cascade").

### S6 (shot 7): jargon, a stretched clock, and the event's status
- "Peta-electronvolts" is never explained. Add on screen: "6 PeV: nearly a thousand times the energy of a proton beam at the Large Hadron Collider (7 TeV)" (facts.md B7; 6.05 PeV / 7 TeV is about 860; add a CLAIMS row).
- The replay runs on a non-linear clock (viewer report: t = T·u²). Label it "time stretched: 17 microseconds shown in N s, slowed most at the start".
- If the word "Glashow" appears anywhere, write "a candidate for the Glashow resonance (predicted 1960): one event, not proof". Never write "proves" (the 2021 IceCube press release headline overclaims; the paper is 2.3 sigma).
- "About six peta-electronvolts" is the shower's energy (6.05 ± 0.72 PeV). "This shower" is safer than "this one".
- Bridge from 6b, optional (+9 words): "Aim matters: it points back to where neutrinos come from." Put it at the start of shot 7. It also sets up shot 9's open question.

### S7 (shots 8 and 8b, q3): solar contradiction, chips, and an honest framing
- Shot 1 put 65 billion solar neutrinos a second through a fingernail. Shot 8 says IceCube records 100,000 a year, and 8b says "the rest are made in our own atmosphere". A viewer asks: where did the Sun's go? The committee's 100,000 are above 0.1 TeV.
- Shot 8, exact rewrite (19 words, 6.6-7.3 s + 3.5 s beat; shot length 11.5 s): **"IceCube records about a hundred thousand high-energy neutrinos a year. Guess: how many of them come from outer space?"** "Outer space" replaces "deep space", to match shot 7 and to avoid implying extragalactic.
- Chips (the committee's number is fixed, so no toy tolerance is needed): **"About half" / "About 1 in 10" / "About 1 in 1,000"**.
- Draw the jar with every dot identical until the reveal; a gold dot visible during the beat gives the answer away.
- Shot 8b: keep the line. On screen, "1 in 1,000 (Nobel Committee)". Add a tag [atmospheric] for "The rest are made in our own atmosphere" (facts.md section 6, "Background from atmospheric neutrinos").

### S8 (sound off; LinkedIn autoplays muted)
Captions are not enough for the beats. During each beat, show the question as a card ("What are the odds it hits anything in 1 km of ice?" and so on) above the chips. Shot 7 needs "Real event, 8 Dec 2016" or "Our simulation" (see B6) on screen for its whole length. Shot 9's "evidence, not yet proof" must be on screen, not only spoken.

### S9 (credits and labels on screen)
- End card (5 s), add:
  - "Unofficial. Not affiliated with the Nobel Foundation or the IceCube Collaboration."
  - "Event data: IceCube Collaboration, DOI 10.21234/gr2021" (if B6 is a yes).
  - "Sensor positions: IceCube ppc geometry, Zenodo, CC-BY-4.0". CC-BY requires attribution, and shot 6 uses the real layout (PLAN.md update).
  - "Sources: nobelprize.org; claims ledger in the repo".
- Shot 9 sky map: label it "illustration". Do not copy IceCube's published NGC 1068 map.

### S10 (claims column)
Tags to add or rename before the CLAIMS ledger is written:
- [2013-evidence] (was [2013-discovery]); [2014-confirmed] (on-screen card); [led-construction]; [learned-1988].
- [spacing-125]; [glashow-data] (DOI); [collab-size]; [atmospheric]; [lhc-7tev] (if S6 is used).
- [extragalactic-mostly] (only if the long form of 9a is used).
- Shot 3's on-screen "100 TeV" is a toy-model input. Show it with "our toy model".

### S11 (60 s vertical cut): named in the title, missing from the storyboard
Decide now, so the 9:16 layouts (hexagon, sky map, replay) are built once. A proposal:
- 1 (11 s)
- 2 short (8 s): "The Nobel Prize in Physics went to Francis Halzen, for IceCube, a telescope made of Antarctic ice."
- 4 trimmed (10 s)
- 5 (10 s)
- 8 + 8b with a 2.5 s beat (14 s)
- 9b (7 s)

That is about 60 s, with the citation card on screen in shot 2. Drop 7 rather than 8: the question drives watch time. Or swap 8 for 7 if the replay licence (B6) is a yes and the visual matters more.

### S12 (overlay zones)
In Medicine, 7 of 11 build findings were collisions. Shots 6 and 6b stack the roadmap, the permanent toy label, the 3D event, the question card, the ring, the chips, the captions and (in 6b) the chart plus the caveat chip. Shot 9 stacks the sky map, the chip and the roadmap. Give the scene builders a zone map in TASK.md:
- roadmap: bottom 8%;
- captions: above it;
- question card and chips: centre-low;
- toy label: top-left, always;
- caveat chip: top-right.

---

## POLISH

- **P1 (voice):** listen to Kokoro on "Halzen", "Learned", "IceCube", "peta-electronvolts" and "kilometre" before lock. Write years and numbers as words in the TTS script ("nineteen eighty-eight", "twenty thirteen"). Keep "NGC 1068" on screen only, never spoken.
- **P2 (shot 7):** for Bert and Ernie, show the names only. Never draw the Sesame Street characters.
- **P3 (shot 2):** say "Four steps, and three guesses for you" if the time allows, so the viewer knows the guesses are theirs.
- **P4 (shot 2 visual):** add "South Pole" to the ice-sheet drawing.
- **P5 (shot 9 sky map):** optionally draw a faint Milky Way band labelled "our galaxy shines in neutrinos too (2023, 2026)". It closes the B2 trap visually and is a fact people do not know (facts.md 5.10).
- **P6 (shot 3):** "the ghost particle" is a nickname, not a claim. Use it once, as written.
- **P7 (shot 9b):** hold the final frame 1.5 s with no voice. It is the only moment the loop closes.
- **P8 (shots 3b, 6, 6b):** use the same label words every time: "our toy model". The storyboard mixes "our toy telescope", "our toy model" and "educational demo"; the spoken form is fine, but the on-screen label should be one string.
- **P9 (shot 4 visual):** draw the drill as a schematic (hose, hot water, hole). We have no photograph, and none is needed.
- **P10 (shot 8b):** "made when cosmic rays hit our atmosphere" is more precise. Use it only if a CLAIMS row supports it; otherwise keep "made in our own atmosphere".

---

## Proposed narration after fixes (for the voice-first fast lane)

| Shot | Length | Narration | Words |
|---|---|---|---|
| 1 | 11 s | About sixty-five billion neutrinos from the Sun pass through your fingernail every second, and almost none of them touch anything. So how do you catch one? | 26 |
| 2 | 13.5 s | This year's Nobel Prize in Physics went to Francis Halzen, for decisive contributions to IceCube, a telescope made of Antarctic ice, and the discovery of high-energy neutrinos from space. Four steps, three guesses. | 33 |
| 3 | 14 s | Step one: the ghost particle. Guess: a high-energy neutrino crosses a whole kilometre of ice. What are the odds it hits anything on the way? [3.5 s beat] | 25 |
| 3b | 8 s | In our toy model, about one in {K1}. So the detector had to be huge. | 17 |
| 4 | 15 s | Step two: the telescope. In 1988, Halzen and John Learned proposed using the ice itself. Halzen then led the team that built it: eighty-six holes, two and a half kilometres deep, over five thousand light sensors. | 37 |
| 5 | 11.5 s | When one does hit, it makes a charged particle faster than light travels in ice. It leaves a cone of blue light, and each sensor times its arrival. | 28 |
| 6 | 18 s (17 s without the spoken "an educational demo", 34 words) | Step three: our toy telescope, an educational demo. From the light's arrival times alone, it works out which way the particle was going. Guess: space the strings twice as far apart. How much worse does it aim? [3.5 s beat] | 37 |
| 6b | 9 s | In our toy model, about {T2/T1} times worse: fewer sensors see the light. Trend only, not IceCube's real aim. | 19 |
| 7 | 14.5 s | Step four: what it found. In 2013, IceCube reported the first evidence of high-energy neutrinos from outer space. In 2016 it caught this shower: about six peta-electronvolts, replayed from the real data. | 36 |
| 8 | 11.5 s | IceCube records about a hundred thousand high-energy neutrinos a year. Guess: how many of them come from outer space? [3.5 s beat] | 19 |
| 8b | 7 s | About a hundred, the Nobel Committee says. The rest are made in our own atmosphere. | 15 |
| 9a | 11 s | The prize honours that discovery: high-energy neutrinos from space. Which objects make them is still open: one nearby galaxy shows evidence, not yet proof. | 25 |
| 9b | 7 s | So how do you catch one? With a cubic kilometre of ice, still watching. [1.5 s hold] | 14 |
| 10 | 5 s | Educational demos of this year's Nobel Prizes, made with showtime. | 10 |
| **Total** | **156 s** | | **~341** |

The total is about 2:36. The B5 cuts bring it to about 2:20, and those cuts are also the cheapest way back toward 2:00. Lengths are set so that every line plus its beat fits at the slow end (2.6 wps); in the tightest shots (2, 5, 7, 9b) that leaves 0.3-0.8 s of air, so cut shot 7 first.

---

## Answer chips, in one place

| Question | Chips (correct one in bold) | Fair because |
|---|---|---|
| q1 (shot 3), toy K1 at 100 TeV | 1 in 1,000 / **1 in 100,000** / 1 in 10 million | 100x spacing: the middle chip stays right for any toy value from 1 in 10,000 to 1 in 1,000,000 (and at 1 PeV too) |
| q2 (shot 6), toy Pandel ratio, 250 m vs 125 m | Barely worse (under 1.5x) / **A few times worse (1.5x to 20x)** / Over 20 times worse | Spike about 6x; the middle chip covers 2x-18x (a factor of 3 either way). Re-check against the final number |
| q3 (shot 8), committee number | About half / About 1 in 10 / **About 1 in 1,000** | A fixed published number; the surprise is the point; the chips are far apart |

Leaks checked: q1 (shot 1 says "almost none touch anything", which is fine because every chip is rare). q2 (none in the line; "worse" gives only the obvious direction). q3 (**leaked by 3b's {K3} and by a "28 events" card**; both are removed above. The jar must not show gold before the reveal). On the interactive page, the spacing slider and the size chart must stay hidden until their question is answered.

---

## Visual feasibility (one afternoon, canvas and HTML only)

Everything can be drawn. Nothing needs footage, as long as:
- Shot 1: draw the fingertip as a line drawing, with no photo.
- Shot 4: draw the drill as a schematic (we have no photo of the drill). Use the hexagon from the real positions (ppc geometry, CC-BY, credited).
- Shot 6: reuse the Glashow viewer's own Canvas 2D projection for the toy `example_event.json`. That event is written only when the telescope run's preliminary JSON lands, so do not lock 6 or 6b before then.
- Shot 7: reuse the existing replay render (`video/showtime-out/glashow-replay-20261006-100652/`) only if B6 is a yes. The 9:16 cut needs a re-shoot of the viewer at phone size, which the viewer already supports.
- Shot 9: a drawn Hammer-Aitoff sky with a soft glow and one circle (NGC 1068 at RA about 40.7 degrees, Dec about 0 degrees), labelled "illustration".
- Do not use: Nobel portraits or Jarnestad illustrations (licence not cleared), Sesame Street imagery, IceCube press images (the "Hydrangea" renders), or IceCube's published sky maps.

---

## What a physicist would reply under the post (as planned), most likely first

1. "First neutrinos from beyond the solar system in 2013? SN 1987A." (B1)
2. "The committee's own cited result is neutrinos from the Milky Way; the flux is not 'from beyond our galaxy'." (B2)
3. "Your toy says about 30 a year and the committee says 100; which is it?" (B3)
4. "Halzen and Learned proposed it together in 1988." (S2)
5. "IceCube's track resolution is about 0.3 degrees, not your {T1}." (S4)
6. "IceCube doesn't catch solar neutrinos." (B4 tie-back)
7. "'Outruns light' is not physics." (S5)

---

## What works (keep it through the fixes)

- The four-step roadmap, and "Four steps, three guesses".
- Three guesses with chips only after the beat.
- Placeholders instead of invented toy numbers; "trend only" and the caveat chip on 6b.
- "Evidence" (not "discovery") for 2013, and "evidence, not yet proof" for NGC 1068, both matching the committee.
- The committee attribution on the 100 per year.
- A real event, with its date, as the payoff of step four.
- showtime credited only on the end card.

## Declined to judge

- The toy numbers (K1, T1, T2): no results exist yet.
- Kokoro's pronunciation.
- Whether any frame looks right.
- Whether IceCube has answered on the Glashow licence.
