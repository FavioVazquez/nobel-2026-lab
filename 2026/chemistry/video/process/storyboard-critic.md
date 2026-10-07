# Storyboard critic: "One hand wins", full version (~2:15, 16:9)

Read against: storyboard-full.md, CLAIMS-VIDEO.md, CLAIMS-FULL.md, ../facts.md, data/popular-information.txt (POP), data/advanced-chemistryprize2026.txt (SCI; advanced-information.txt is only the landing page), data/press-release.txt (PR), the toy's results (nobel-chem-mirror/2026/chemistry/mirror-race/results/mirror_summary.json, histograms.json), and the short's storyboard.md and storyboard-critic.md.

Word counts are spoken words, with numbers written out ("seventy-five" = 2). Rates assume 2.65 words/s. Time the real af_bella render before you lock the cut: Kokoro reads numbers slowly.

**Verdict.** The numbers are right and every one has a source (75:25 -> 56/38/6 -> 90:10 checks out: 0.5625 / (0.5625 + 0.0625) = 0.90). The toy matches its JSON. Four things block the build:
1. The video asks the viewer questions in two places, and the owner banned questions.
2. The voice never says "Nobel Prize".
3. "Catalyst", "excess" and "run" are used before they are explained, and ee is called "purity".
4. Shot 5 cannot fit its words or its visuals.

Shots 2 and 10 also run fast. The fixes below take the video to about 2:20-2:28. The trims that bring it back to about 2:20 are in S9.

---

## BLOCKERS

**B1. Questions to the viewer (shots 3 and 9, and the rule on line 5).** The owner said no questions at all. The storyboard still has three:
- Shot 3 says "So how does one hand win?" and shows a big hand-inked "?".
- Shot 9 says "Which hand? A coin toss."
- Line 5 explicitly allows one rhetorical turn, which goes against the owner's rule.

Fixes:
- **Line 5 rule:** delete the clause `the narration's one rhetorical turn ("So how does one hand win?") is answered at once` and replace it with "No question marks in the voice or on screen."
- **Shot 3 visual:** drop the question mark. In the last 2 s an orange "catalyst" stamp drops into the flask and the tally tips slightly (no number, or "tipped"). The page then turns (match) to Frank's notebook. The shot 3 narration is in B3.
- **Shot 9, last sentence:** "Which hand is a coin toss." (6 words, a statement).

**B2. The voice never says "Nobel Prize" (shot 1).** With sound on and eyes elsewhere, the viewer only hears "Nobel" in shot 10 ("Nobel Committee"). Shot 1 also states a fact, not a puzzle, and the hands visual already shows the "can't stack" line. New shot 1 narration (19 words, about 7.2 s; make the shot **7.5 s**):
> "Your hands are mirror images. This year's Nobel Prize in Chemistry is about how one hand can take over."

The puzzle (life uses one hand, chemistry left alone gives both) then lands in shots 2-3. The answer comes in shot 9 ("one hand takes over") and the payoff in shot 11 ("Chemistry learned to choose a hand"). Keep the frame-0 poster. Fix its number line in B4.

**B3. "Catalyst" is used before it is defined, and box 1 is left hanging (shots 3-5).** Shot 4 says "a one-handed catalyst" twice, and the viewer has never been told what a catalyst is. The narration also never says box 1 was already done, so "Kagan ticked box two" begs "what about one?". Define the word in shot 3 (POP's own definition is "a substance that drives chemical reactions without being consumed") and close box 1 in shot 4.

Shot 3 (25 words, about 9.4 s; make it **9.5-10 s**):
> "Yet a reaction left to itself makes both hands, fifty-fifty. A one-handed catalyst, a helper that isn't used up, can tip the balance."

Do not say "only slightly". Asymmetric catalysis was already strong by the 1980s (2001 prize).

Shot 4 (47 words, about 17.7 s; make it **17.5-18 s**):
> "In nineteen fifty-three, the physicist Charles Frank wrote a recipe for one hand to take over completely. One: a one-handed catalyst; chemists had that by the early nineteen hundreds. Two: boost one hand and hold back the other. Three: a reaction that makes its own catalyst."

- "Take over completely" is the bridge from "tip the balance" in shot 3.
- Box 1's tick lands on "early nineteen hundreds" (Marckwald, POP l.91-95, 107).
- Add a small source note to the page: "numbered as in the Nobel popular background". SCI lists the same three ideas in a different order, (i) autocatalysis, (ii) enantioselective catalysis, (iii) mutual antagonism. A chemist who knows Frank's paper will otherwise say "box one is autocatalysis". Matching them up: POP 1 = SCI (ii), POP 2 = SCI (iii), POP 3 = SCI (i). POP l.112 says exactly that Kagan ticked the second condition. SCI p. 3 says the same thing in its own terms: Kagan's NLE = "mutual inhibition" = Frank's (iii). So the storyboard's "Kagan box two / Soai box three" is faithful to POP and consistent with SCI.

**B4. ee is called "purity", and "excess" is never explained (shots 1, 5, 7, 8, 9).**
- A chemist will reply under "Purity doesn't add up in a straight line" (shot 5) and "histogram of final purity" (shot 9). ee is an excess, not a purity.
- Viewers will read the shot 7 y-label "excess of one hand" with "57%" as "57% one hand". In fact 57% ee is about 78.5 : 21.5.
- Shot 8 shows "ee 15-91%" as unexplained jargon.

Use one lay word throughout, **lead**, and define it once on screen.
- **Shot 7 y-axis:** "lead of one hand (% of one hand − % of the other; chemists call it ee)". Keep this definition on screen for the whole shot, at least 3.5% of frame height.
- **Shot 1 poster line:** "a lead of 5 in 10 million → over 99.5% one hand". Both halves are true: the start is an excess of 5×10⁻⁷, and >99.5% ee means more than 99.75% one hand.
- **Shot 8 small text:** "each run only partly one-handed: lead 15-91 points (Nobel scientific background)".
- **Shot 9 histogram x-axis:** "final lead: ← all mirror hand · all one hand →". The data are signed ee from −1 to +1, not purity.
- **Shot 5 last line:** see B5. Drop "Purity".
- **Contract, line 3:** replace "purity doesn't add up in a straight line" with "the product comes out purer than a straight line predicts".

**B5. Shot 5 cannot fit: 52 words in 17 s is 3.1 w/s, with six visual beats.** The six beats are: M disc, 75:25, pie, strike, re-split, chart. Also, "the reaction is driven ninety to ten" will be heard as "the product is 90:10". POP figure 4's 90:10 is the share of the *working catalysts* (56 / (56 + 6)), not of the product. Make the shot **19.5 s** and split it into 5a (pairs, about 12.5 s) and 5b (curve, about 7 s) with a page turn. New narration (51 words, about 19.2 s):
> "In nineteen eighty-six, Henri Kagan ticked box two. His insight: the catalyst's metal holds two pieces, so mixed hands make three kinds of pairs, and the mixed pair barely works. Start seventy-five to twenty-five, and the working catalysts are ninety to ten: a purer product than a straight line predicts."

Screen changes:
- The pie's last state is labelled "working catalysts 90 : 10", never "product".
- The 75:25 is labelled "pieces 75 : 25".
- Credit: "numbers from Nobel figure 4, our drawing".
- The chart axes are "catalyst pieces: lead" and "product: lead". Keep "shape only, not Kagan's data".
- "His insight" matters: POP l.118 says Kagan *assumed* the metal holds at least two pieces.

---

## SHOULD-FIX

**S1. Shot 6 draws a mechanism the video later calls debated, and "copies of itself" needs ingredients.**
- **Mixed pairs:** the visual has "teal ones pair off with orange into grey mixed pairs". That is Denmark's style of explanation. Trapp's model says the homo- and heterochiral dimers are "not responsible for entrapment of the minor enantiomer" (SCI p. 15-16). Shot 10 then says the mechanism is still debated. (The short's critic called this "the true mechanism". That was an overclaim. Do not repeat it.) Fix: shot 6 shows autocatalysis only. Grey "raw ingredient" dots feed in, and each orange molecule turns them into new orange molecules (1 -> 2 -> 4 -> 8). There are no grey pairs and no teal. Grey pairs appear only in shot 5 (Kagan's idea) and shot 9 (our toy), where the shot owns them.
- **Rule on line 5:** change "(it pairs off into grey mixed pairs)" to "(it never flips colour)".
- **Wording:** "makes copies of itself" with no feedstock reads as biological self-replication. POP does say "formed copies of itself" (l.134), but a chemist will say "it catalyses its own formation". New narration (22 words, about 8.3 s; it fits **9 s**):
  > "In nineteen ninety-five, Kenso Soai ticked box three: a molecule that helps build more of itself, same hand, from simple ingredients."
- **Margin note:** "Kenso Soai · 1995 · a lab molecule, not one of life's". This stops viewers thinking Soai made amino acids, because orange also means life's alanine in shot 2.

**S2. CLAIMS-FULL F6 overclaims.** "Soai 1995: … autocatalysis, the first asymmetric one" is wrong per SCI p. 4 and 11 and facts.md l.70 and 89. Soai's 1990 reaction was already asymmetric autocatalysis, but the product's excess *fell* (86% -> 35%). 1995 was the first asymmetric autocatalysis *with amplification*, which met all three Frank criteria. POP's "none were asymmetric … 1995" glosses over 1990, and a chemist will catch it. Rewrite F6:

> F6 | Soai 1995: a molecule that catalyses its own formation with its own hand, and amplifies its excess (asymmetric autocatalysis with amplification), the first lab system to meet all three of Frank's conditions. (His 1990 asymmetric autocatalysis lost excess.) | POP l.129-132; SCI p. 4, 11-12; S95; S90

The narration never says "first". Keep it that way.

**S3. Shot 7: "run" is undefined, "by 2003" is vague, and the shot has no subject.** The viewer cannot tell what a "run" is: each run's product is the starting nudge for the next (SCI p. 12, "three consecutive runs"). S03a is January 2003, so say "In". New narration (39 words, about 14.7 s; make it **15 s**):
> "In two thousand three, his team started with a lead of five parts in ten million. Each run's product seeds the next: fifty-seven percent after one run, ninety-nine after two, past ninety-nine and a half after three."

Visual: small ink arrows between the bars, "product → seeds next run". Drop the magnifier inset. The callout "5 in 10,000,000: too small to draw" is enough and is easier to read at phone size. The margin note stays "Soai and colleagues, 2003".

**S4. Shot 8: "no head start at all" invites the Singleton reply, and "went" sounds pure.** The paper's own framing is "without adding chiral substances" (S03b). Singleton and Vo showed that trace chiral impurities can steer such runs (SV03). New narration (26 words, about 9.8 s; it fits **11 s**):
> "Then, with no one-handed ingredient added, the reaction still picked a hand, at random. In thirty-seven runs, nineteen leaned one way, eighteen the other."

The numbers check against SCI p. 13: 18 (R), 19 (S), ee 15-91%. Keep the partly-tinted flasks and no solid ones.

**S5. Shot 9 calls mutual antagonism "Frank's other rule", but it is box 2, Kagan's box.** Shot 4 told the viewer that box 2 is "boost one hand, hold back the other". "Frank's other rule, that the two hands knock each other out" sounds like a fourth, unnumbered rule, and it breaks the spine. In the toy, antagonism is exactly Kagan's idea: a one-hand and a mirror molecule pair into an inactive mixed pair (k2, "mixed pairs count one of each hand"). Name it as box 2 and the tie-in works. New narration (49 words, about 18.5 s; make it **19 s**):
> "In our toy model, copying alone isn't enough: ten thousand runs end up anywhere, a flat spread. Add box two, where a one-hand and a mirror molecule pair up and stop working, and nearly every run ends with one hand taking over. Which hand is a coin toss."

- **Visual:** the switch reads "+ box 2: mixed pairs stop working". Show the grey pair forming, as in shot 5. The label "our toy model · trend only" stays on screen for the whole shot.
- **Data check:** copy-only gives a flat histogram (χ² p = 0.66). Antagonism gives 99.7% of runs with a lead above 90%, split 4951 / 5049. Both lines are honest as worded. The "flat" result holds at the toy's k0/k1 = 1 only: at 10 it is a hump with std 0.22. That is why "trend only" must stay on screen.

**S6. Shot 10 runs fast (27 words in 9 s, 3.0 w/s), and "not that answer" paraphrases away the committee's nuance.** SCI p. 4: Frank's model "is not an answer to the origin of biological homochirality. It provides one possible solution, of which there are several". SCI p. 15-16 says the Soai mechanism has "two detailed mechanisms" put forward. New narration (28 words, about 10.6 s; make it **10.5-11 s**):
> "A toy, not how life chose its hand. The Nobel Committee stresses Frank's model isn't the answer to life's origin, and how Soai's reaction works is still debated."

On-screen quote, exact: `“not an answer to the origin of biological homochirality”: Nobel Committee, on Frank's model`. Below it: "How Soai's reaction works: two competing explanations (Nobel background)".

**S7. Shot 11 trims the source, the claim says "every day" without a source, and a capsule is not chiral.**
- POP l.71 says "can cause unnecessary and sometimes harmful side effects". The storyboard's "can cause harmful side effects" drops "sometimes".
- "Matters every day" has no source.
- A capsule's mirror image is the same capsule. Any chemist, or any sharp viewer, will point that out.

New narration (23 words, about 8.7 s; make it **9.5 s**):
> "Choosing the hand matters for medicines: one form does the job, and its mirror image can cause unnecessary, sometimes harmful, side effects."

Visual: use POP's own locksmith idea in our drawing. Two mirrored keys across the mirror line: the orange one turns the lock, and the teal (hatched) one is labelled "can cause unnecessary, sometimes harmful, side effects (Nobel)". Then type the payoff line "Chemistry learned to choose a hand." with the small attributed line "“decisive for chemists who design reactions for the manufacture of pharmaceuticals” (Nobel Committee)". That links the laureates to medicines without spoken words. No thalidomide.

**S8. Shot 2 runs fast: 27 words in 9 s is 3.0 w/s.** New narration (21 words, about 7.9 s; make it **8.5 s**):
> "Many molecules come in two hands like that. Life is picky: your proteins use only one hand of each amino acid."

"Use" is safer than "found in" (D-amino acids exist in nature; PR: "rarely found"). The PR itself says "all amino acids exist as two mirrored variants", so "each" matches the committee's wording.

Alanine geometry:
- Use PubChem CID 5950 (L-alanine) from data/molecules/cid5950_3d.sdf for the orange model.
- Build the mirror by negating the x coordinates across the dashed line. Never rotate it 180°: a rotated copy is the same molecule, and a chemist will spot it.
- Use the standard colours with element letters (C, N, O, H) so the "four different groups" read: CH₃, NH₂, COOH, H.
- Replace the hand -> molecule "morph" with a blur-dissolve match cut. A true morph is not an hour's work.

**S9. Total length.** As written: 141 s (2:21), 351 words. After B2-B5 and S1-S8 the shots are:

7.5 / 8.5 / 9.5 / 17.5 / 19.5 / 9 / 15 / 11 / 19 / 10.5 / 9.5 / 7 / 6.5 = **150 s**

Trims that bring it back to about **2:20**:
- **Merge shots 12 and 13** into one 9 s card (−4.5 s). Narration (22 words, about 8.3 s):
  > "Race the mirrors yourself in our open Nobel 2026 lab. Explained with showtime, an open-source video studio for coding agents."
- **Shot 4:** drop "the physicist", since the margin note says it (−0.5 s).
- **Shot 9:** drop "a flat spread", since the histogram shows it (−1 s).

That gives about 144 s. If the af_bella render runs faster than 2.65 w/s, it lands near 2:20.

---

## POLISH

- **Shot 1:** the frame-0 poster has four text layers on a 16:9 frame that a phone shows about 6 cm wide. Headline at 12% or more of frame height. The number line at 5% or more. The names line at 3.5% or more, not small caps at 2%.
- **Shot 2:** "homochiral: Greek for 'same hand'" is never used again. Cut it to declutter, or keep it and also have it in shot 11's payoff. Not both half-ways.
- **Shot 4:** the box labels "Kagan, 1986", "Soai, 1995" and "early 1900s" sit next to the boxes at a small size. Make them 3.5% or more of frame height, in ink, not orange.
- **Shot 5:** the "barely works" strike should be ink, not red. Red is not in the palette and reads as "teal = bad". The optional faint curve dipping under the line, "it can also bend down", is honest (Kagan's 1986 paper also reported negative NLEs, SCI p. 6). Drop it if the frame is busy.
- **Colour:** orange #b13d0b vs teal #2b8a8f is about 1.45:1 in luminance. The hatch and pictogram cue carries the difference, so keep it on every mark, including the histogram bars. Teal on paper is about 3.6:1, so use ink for any teal-adjacent small text (shot 11 label, shot 8 counters).
- **Strokes:** tapered strokes take a long time to build. Get the "hand-inked" feel with stroke-dash draw-on, two stroke widths (1.5 and 3 px at 1080p), round caps and graph paper at 8% opacity or less. Don't spend the hour on variable-width paths.
- **Shot 8:** "type 'no head start' crossed through a seed" is unclear. Use "no one-handed ingredient added" with a struck-through orange seed dot. Seeded placement of 19 and 18, not alternating.
- **Shot 9:** drive the dots from race_runs.json (one real toy run) and the bars from histograms.json counts. Grow the histogram by scaling the counts (first_400_bin for the first second, then ease to 10,000). Don't fake a curve.
- **Captions:** spell numbers as spoken ("five parts in ten million", "fifty-seven percent"). Never "0.00005%" and "five parts" on screen at once. Never "99.99%" (POP l.139 says it; the rule bans it).
- **Shot 12/13:** check faviovazquez.github.io/nobel-2026-lab is live before posting. The URL card needs 4 s or more on screen at 4% or more of frame height. The sources line on the end card needs 2.5% or more.
- **Feasibility (about an hour):** build one notebook-page template (paper, grid, margin-note slot, caption plate guard at 86%), plus one checkbox, one bar/histogram and one dot-field component. Reuse them across shots 3, 4, 5, 7, 8 and 9. The riskiest asset is a good hand outline in shot 1. Draw one SVG path and mirror it with scaleX(−1). Do not try two separate drawings.
