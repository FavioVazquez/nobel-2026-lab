# Chemistry 2026: one hand wins

> **Educational demos made to show an open-source tool. Not research, and not for any lab or clinical use.**

**Status:** facts: done · claims ledger: done (39 claims, checked 2026-10-07) · pictures: done · Kagan's curve: done, independently reviewed · Soai's amplifier: done, independently reviewed · the mirror race: done, independently reviewed · page: done · video: done

The 2026 Nobel Prize in Chemistry went to Henri B. Kagan and Kenso Soai "for the discovery of non-linear effects and autocatalysis in asymmetric organic synthesis". (C01) Many molecules come in two mirror-image forms, like a left and a right hand, and life uses only one of them. (C06, C07) Kagan and Soai showed how a chemical reaction can be made to choose one hand. Back to the [front page](../../README.md).

Numbers like (C01) point to rows in [CLAIMS.md](CLAIMS.md), where each sentence has its source.

This folder stays at textbook level on purpose. It names no lab procedure, no reagent amounts and no reaction conditions. The code simulates published mathematical models, nothing else.

## The story in four steps

1. **Kagan, 1986: the catalyst's lead of one hand does not pass on in a straight line.** Chemists believed that the catalyst's chirality was transferred to the product's chirality, in a linear relationship. (C11) Kagan assumed that the catalyst's metal holds two of the chiral molecules, so a mix of right and left gives three catalysts: right-right, left-right and left-left. (C14) The left-right catalyst drove the reaction far more slowly, so the product could have a greater excess of one hand than the catalyst: a non-linear effect. (C12, C16) In the Nobel Committee's worked example, 75 per cent right and 25 per cent left gives catalysts in the proportions 56, 38 and 6 per cent; only two of them work efficiently, so the reaction is driven by 90 per cent right and 10 per cent left. (C15)
2. **Soai, 1995 and 2003: a molecule that copies its own hand.** Soai found a chiral molecule that catalyses its own formation, so each one makes more of its own hand, and the new product has a bigger lead of that hand than the catalyst it started from. (C19) In 2003 his group started from an excess of about 0.00005% of one hand and reached 57%, then 99%, then more than 99.5% in three runs in a row. (C21) With no chiral substance added at all, 37 runs gave one hand 19 times and the other 18 times, with an excess between 15% and 91%: chance chose the hand. (C24)
3. **Frank, 1953: copying plus mutual antagonism.** The physicist Charles Frank showed on paper that a substance that catalyses its own production, and works against its mirror image, can turn a tiny imbalance into one hand only. (C27) The Nobel Committee calls Soai's reaction the first laboratory experiment to verify Frank's model. (C29) The Nobel Committee is careful: "the Frank model is not an answer to the origin of biological homochirality". (C28)
4. **Why it matters: medicines.** Many drug molecules occur in two mirror forms: one has the therapeutic effect, while the other "can cause unnecessary and sometimes harmful side effects". (C32) The committee says the discoveries have been decisive for chemists who design reactions for the manufacture of pharmaceuticals. (C33)

## The stations

Six stops, as in a science museum. Each says what it is made of and whether it is ready.

<table>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-mirror.svg" alt="Icon: a molecule and its mirror image on either side of a dashed mirror line" width="72"></td>
    <td valign="top"><b>1. Mirror molecules</b> <i>(ready)</i><br>
    Your hands, and the amino acid alanine, next to their mirror images. Same atoms, joined the same way, yet one cannot be laid on top of the other. Life uses one hand. See <a href="#the-pictures">the pictures</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-kagan.svg" alt="Icon: a curve bulging above a straight dashed line" width="72"></td>
    <td valign="top"><b>2. Kagan's curve</b> <i>(ready)</i><br>
    Mix both hands in a catalyst and the product's lead of one hand (ee) bends away from the straight line. The textbook model, in closed form: in our toy model (trend only), the committee's 75:25 ligand, a 50% lead, gives a product with an 80% lead, where a straight line gives 50%. Folder: <a href="kagan-curve/README.md">kagan-curve</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-soai.svg" alt="Icon: an orange molecule making two copies of itself" width="72"></td>
    <td valign="top"><b>3. Soai's amplifier</b> <i>(ready)</i><br>
    A molecule that copies its own hand, round after round. Published kinetic models set against Soai's 2003 numbers, and an honest look at where a simple model falls short: in our toy model (trend only), pairs formed at random (K = 4) would need about 1.7 million turnovers to go from 0.00005% to Soai's 57%. Our fitted toy (K = 73, fitted to his first two runs) gives 57%, 99%, then 99.98% (Soai: more than 99.5%). Folder: <a href="soai-amplifier/README.md">soai-amplifier</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-race.svg" alt="Icon: an orange dot and a hatched teal dot racing to a finish line, the orange one ahead" width="72"></td>
    <td valign="top"><b>4. The mirror race</b> <i>(ready)</i><br>
    Frank's 1953 model, run molecule by molecule from an exact 50:50 start, 10,000 times. In our toy model (trend only, for our chosen rates), copying alone gives a flat spread: any final mix, equally often. Add mutual antagonism and 99.7% of runs end with a lead past 90%, about half for each hand. Folder: <a href="mirror-race/README.md">mirror-race</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-page.svg" alt="Icon: a web page with a slider" width="72"></td>
    <td valign="top"><b>5. The interactive page</b> <i>(ready)</i><br>
    Guess first, then see what the toy models say. <a href="https://faviovazquez.github.io/nobel-2026-lab/2026/chemistry/page/">Try it online</a>. Folder: <a href="page/README.md">page</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-video.svg" alt="Icon: a video frame with a play button" width="72"></td>
    <td valign="top"><b>6. The video</b> <i>(ready)</i><br>
    A 2:30 explainer that tells the story, from Frank's recipe to Kagan's bend, Soai's copier and our mirror race; it asks no questions. <a href="video/exports/nobel-2026-chemistry.mp4">Watch the MP4</a>. Every fact in it comes from the <a href="CLAIMS.md">claims ledger</a>; the toy result comes from station 4. Made with <a href="https://github.com/FavioVazquez/showtime">showtime</a>. Folder: <a href="video/README.md">video</a>.</td>
  </tr>
</table>

## The pictures

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../../assets/diagram-mirror-hands-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="../../assets/diagram-mirror-hands-light.svg">
    <img alt="Two hands and an amino acid, each next to its mirror image across a dashed mirror line. Top: a left hand, solid orange, and its mirror image, a right hand, hatched teal. Bottom: a ball-and-stick model of alanine, a central carbon atom holding four different groups (H, NH2, COOH and CH3) in a tetrahedral shape. On the left is L-alanine, the form in our proteins; on the right its mirror image, D-alanine. Same atoms, joined the same way, yet one cannot be laid on top of the other. Chemists call such molecules chiral, and the two forms enantiomers. Our own drawing, not to scale." src="../../assets/diagram-mirror-hands-light.svg" width="560">
  </picture>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../../assets/diagram-kagan-bend-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="../../assets/diagram-kagan-bend-light.svg">
    <img alt="Kagan's non-linear effect in three steps and a curve. 1: the ligand, the chiral part of the catalyst, is 75 per cent one hand and 25 per cent the mirror hand, an excess (ee) of 50 per cent. 2: each metal atom holds two ligands, paired by chance: 56 per cent one-hand pairs, 38 per cent mixed pairs, 6 per cent mirror pairs. 3: the mixed pairs barely work and sit out, so the other two drive the reaction 56 to 6, which is 90 to 10: an 80 per cent excess of one hand, where a straight line gives 50. Below, a sketch of the curve, shape only: the product's ee against the ligand's ee, with the straight line chemists expected, Kagan's bend above it, and a curve that sags below it when the mixed pair is faster. Our own drawing." src="../../assets/diagram-kagan-bend-light.svg" width="560">
  </picture>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../../assets/diagram-soai-copier-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="../../assets/diagram-soai-copier-light.svg">
    <img alt="Soai's copier. Top: grey dots are a simple ingredient with no hand; a molecule of one hand, solid orange, turns an ingredient into a new molecule of its own hand, so 1 becomes 2 and 2 become 4. A bar chart of the lead of one hand (ee) after three runs in a row, Soai's group, 2003: at the start 0.00005 per cent, too small to draw (about 1 molecule in 2 million); after run 1, 57 per cent; after run 2, 99 per cent; after run 3, more than 99.5 per cent. Below, with no head start at all: 37 runs, 19 gave one hand and 18 the other, each between 15 and 91 per cent, never one hand only. Why the reaction amplifies the lead is still debated. The tokens are symbols, not real molecules. Our own drawing." src="../../assets/diagram-soai-copier-light.svg" width="560">
  </picture>
</p>

## What is real, and what is a toy

<table>
  <tr>
    <th width="50%">Real</th>
    <th width="50%">A toy</th>
  </tr>
  <tr>
    <td valign="top">The prize, the laureates, the date and the citation. Every sentence is sourced in <a href="FACTS.md">FACTS.md</a> and checked in <a href="CLAIMS.md">CLAIMS.md</a>.</td>
    <td valign="top">Kagan's curve: the textbook two-ligand model the Nobel Committee presents, with numbers we chose. It shows the shape of the effect; it is not a fit to any measured reaction.</td>
  </tr>
  <tr>
    <td valign="top">The published numbers we quote: the committee's 75:25 worked example; Soai's 2003 runs (about 0.00005%, then 57%, 99% and more than 99.5%); the 37 runs with no chiral substance added (19 one hand, 18 the other, 15% to 91%). Each has its source in the ledger.</td>
    <td valign="top">Soai's amplifier: published kinetic models, run on a laptop. They are one family of explanations among several; why the real reaction amplifies is still debated.</td>
  </tr>
  <tr>
    <td valign="top">The pictures' chemistry: alanine's shape and which mirror form our proteins use. The drawings themselves are ours, not the Nobel illustrations.</td>
    <td valign="top">The mirror race: Frank's 1953 model simulated molecule by molecule. It shows how one hand can win from nothing in a model. It is not an account of how life chose its hand.</td>
  </tr>
</table>

## Folder map

| Path | What it is | Status |
|---|---|---|
| [FACTS.md](FACTS.md) | The sourced fact sheet: citation, laureates, the story, and where the sources disagree | done |
| [CLAIMS.md](CLAIMS.md) | The ledger of claims we use, with sources and check dates (39 claims) | done |
| [`../../assets`](../../assets/diagram-mirror-hands-light.svg) | Mirror molecules, Kagan's bend and Soai's copier, in dark and light | done |
| [kagan-curve](kagan-curve/README.md) | Kagan's curve: a toy model | done, independently reviewed |
| [soai-amplifier](soai-amplifier/README.md) | Soai's amplifier: a toy model | done, independently reviewed |
| [mirror-race](mirror-race/README.md) | The mirror race: Frank's model, a toy model | done, independently reviewed |
| [page](page/README.md) | Guess first, then see ([online](https://faviovazquez.github.io/nobel-2026-lab/2026/chemistry/page/)) | done |
| [video](video/README.md) | A 2:30 explainer that tells the story ([the MP4](video/exports/nobel-2026-chemistry.mp4)), the plan, the source and the critics' reports | done |

## Rerun and check

Everything runs on an ordinary laptop processor in seconds to a few minutes (the full mirror race takes about 3), with no GPU and no accounts. Each folder's README has its exact steps, and that README is the reference. From each folder:

- **Kagan's curve**, from `2026/chemistry/kagan-curve/` ([steps](kagan-curve/README.md)):

  ```bash
  python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && python -m kagan.run_all
  ```

- **Soai's amplifier**, from `2026/chemistry/soai-amplifier/` ([steps](soai-amplifier/README.md)):

  ```bash
  python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && python -m amplifier.run_all
  ```

- **The mirror race**, from `2026/chemistry/mirror-race/` ([steps](mirror-race/README.md)):

  ```bash
  python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && python -m mirrorrace.run_all
  ```

- The page needs nothing: open `2026/chemistry/page/index.html` in a browser.
- Rebuild the pictures: `python3 tools/make_diagrams.py`. Check every link, image and source in this repository without a network: `python3 tools/check_links.py`.

These are teaching toys. The models are simplified and their outputs are for learning only. They are not research, and they are not the laureates' results.

## Glossary

| Term | In plain English |
|---|---|
| Chirality | Handedness. A chiral object, such as a hand or many molecules, differs from its mirror image: you cannot lay one on top of the other. |
| Enantiomer | One of the two mirror-image forms of a chiral molecule. The two forms have the same atoms, joined the same way. |
| ee (enantiomeric excess) | The lead of one hand: % of one hand minus % of the other. A 50:50 mix has an ee of 0%, one form alone has 100%, and 75:25 has 50%. |
| Racemic | An even 50:50 mix of the two forms. Making a chiral molecule with nothing to favour either hand gives a racemic mix. |
| Catalyst | A substance that speeds up a reaction without being used up. A chiral catalyst can favour one mirror form of the product. |
| Ligand | In these catalysts, the chiral molecule that sits on a metal atom and steers which hand the product gets. |
| Non-linear effect | When the product's ee is not in proportion to the catalyst's ee: the curve bends above or below the straight line. Kagan found it in 1986. |
| Autocatalysis | A reaction whose product speeds up its own formation. In Soai's reaction, the product copies its own hand. |
| Homochiral | Of one hand only. Life is homochiral: the amino acids in our proteins are one mirror form, and the sugars in DNA and RNA are one form too. |
| Toy model | A deliberately simple model that shows an idea. It is good for learning and not for decisions. |
