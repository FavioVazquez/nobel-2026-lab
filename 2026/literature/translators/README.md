# One poem, 2,000 years of translators (Literature 2026, experiment L2)

> **Educational demos made to show an open-source tool. Not research.**
> Every count on this page is **our rough count, not a quality score**. It comes from our own hand alignment and our
> own rules, and it says nothing about which version is better or "more faithful". We do not rank the versions.

The 2026 Nobel Prize in Literature went to Anne Carson "for her bold and inventive oeuvre that, in playful dialogue
with the classical tradition, has created new forms for contemporary literature". A translator makes choices: which
words to keep, which to drop, which to add, and which form to use. This folder shows those choices on one famous
poem, Sappho's poem 31, as six public-domain hands carried it into Latin and English over about 1,900 years.

Nothing here is by the laureate. No modern copyrighted translation is used, and no translation was made by an AI:
every Latin and English line is a printed public-domain text, and every gloss is copied from a printed dictionary.

Own code, MIT licence. CPU only, about 5 seconds. Python 3.11 with Matplotlib (figures) and pytest (tests).

## Run it

From `2026/literature/translators/`:

```bash
python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m translators.run_all        # results/*.json and all figures, about 5 seconds
.venv/bin/python -m pytest -q tests             # 21 tests, under 1 second; 2 of them need the full source files (LSJ_DIR, SMOLLETT_TXT, WHARTON_HTML) and skip otherwise
```

## The poem and the six versions

The Greek is **Sappho fr. 2 in H. T. Wharton's numbering (Bergk's), = Voigt 31**, lines 1-16 (four Sapphic stanzas)
as printed in Wharton, *Sappho: Memoir, Text, Selected Renderings and a Literal Translation*, 5th edition, John Lane
1908, pages 64-65 ([Project Gutenberg #57390](https://www.gutenberg.org/ebooks/57390)). Wharton says he adopts
Bergk's text (Poetae Lyrici Graeci, 4th ed., 1882). Wharton prints a 17th line, the start of a fifth stanza with an
editor's supplement in square brackets; it is out of scope here (most versions stop at line 16).

All six versions are printed in the same book, on pages 65-69, and we display Wharton's printing of each, byte for
byte. We checked each one against an independent witness (`data/crosschecks.json`, extracts in
`data/sources/crosscheck/`).

| version | date | what it is | where we read it | independent check |
|---|---|---|---|---|
| **Catullus 51** (Latin) | 1st c. BC (Catullus lived c. 84 - c. 54 BC, [Wikipedia](https://en.wikipedia.org/wiki/Catullus)) | Latin **version**; Wharton calls it "The famous imitation of this ode by Catullus", Addison (1711) "a Translation by Catullus" | Wharton pp. 65-66 quotes lines 1-12; line 8 is lost in the manuscripts (Wharton prints asterisks). Lines 13-16, Catullus's own closing stanza on idleness, are not in Wharton: we take them from E. T. Merrill's edition (1893) on [Latin Wikisource, revision 279690](https://la.wikisource.org/w/index.php?title=Carmina_(Catullus,_ed._Merrill)/Carmen_LI&oldid=279690) | Ellis 1867 (archive.org OCR), Merrill 1893, Smithers/Mueller (Gutenberg #20732): same words, apart from u/v spelling, "adspexi" (Merrill), "aures geminae" (Mueller) |
| **Ambrose Philips** | 1711 | English **version** (Addison printed it in 1711 as the "English Translation"; we say "version") | Wharton p. 67, credited "Ambrose Philips, 1711." | *The Spectator* No. 229, "Thursday, Nov. 22, 1711", Addison, who calls it the "English Translation" without naming Philips; the name is in Henry Morley's editorial footnote (Gutenberg #11010). Differences: "the immortal" (Wharton) vs "th'immortal", "horror" vs "Horrors", "sank" vs "sunk", old spellings and capitals |
| **Tobias Smollett** | 1748 | English **version** in Wharton's sense only: a love song in his novel *Roderick Random* (ch. XL), which Wharton prints among the renderings of this ode | Wharton p. 68, credited "Smollett, in Roderick Random, 1748." | Gutenberg #4085, ch. XL: the narrator's second ode "on the same subject"; it does not name Sappho. Small differences ("shafts"/"shaft", "thy"/"thou", "!" for ".") |
| **John Herman Merivale** | 1833 | English **version** | Wharton pp. 68-69, credited "John Herman Merivale, 1833." | Bland and Merivale, *Collections from the Greek Anthology*, new ed. 1833, p. 15 (two archive.org scans), headed "ODE. Εἰς Ἐρωμέναν" and signed "M."; reading "M." as Merivale is an inference that matches Wharton. Differences: "th' immortal Gods", "quiv'ring", "eye-balls", "!" endings |
| **John Addington Symonds** | 1883 | English **version** in Sapphic stanzas | Wharton p. 69, credited "J. Addington Symonds, 1883." | Wharton's 1885 preface: Symonds's translations "dated 1883, were all made especially for this work in the early part of that year" (first printed there) |
| **H. T. Wharton**, literal prose | 1885 (1st ed.); text as printed in the 5th ed., 1908 | literal prose translation | Wharton p. 65 | we did not check that the 1885 wording is identical |

Dates of death (all long out of copyright): Catullus c. 54 BC; Philips 1749, Smollett 1771, Merivale 1844, Symonds
1893 (Wikipedia pages cited in `data/crosschecks.json`); Wharton 22 August 1895 (the book's own "In Memoriam").

## The answers (our rough count, not a quality score)

Scope: the 71 Greek words of lines 1-16. Catullus's Latin is lines 1-16 with line 8 lost. "Carried" = our alignment
found at least one counterpart word in the version (close or loose, rules below). "Added" = words in the version
that no Greek word links to. The range is the spread over the two independent alignment passes and the final
reconciled one: it is the honest error bar of a hand alignment.

| version | Greek words carried (of 71) | of which close / loose | Greek words dropped | words in the version | words added | range over passes: carried / added |
|---|---|---|---|---|---|---|
| Catullus, 1st c. BC | 34 | 26 / 8 | 37 | 70 | 34 | 32-34 / 34-36 |
| Philips, 1711 | 40 | 25 / 15 | 31 | 107 | 56 | 38-40 / 56-59 |
| Smollett, 1748 | 11 | 7 / 4 | 60 | 94 | 79 | 9-11 / 79-81 |
| Merivale, 1833 | 44 | 25 / 19 | 27 | 94 | 33 | 43-44 / 33-36 |
| Symonds, 1883 | 53 | 45 / 8 | 18 | 120 | 42 | 52-53 / 42-45 |
| Wharton, 1885/1908 (prose) | 62 | 58 / 4 | 9 | 96 | 8 | 62 / 8-12 |

Source of every number: `results/counts.json` (recomputed by the tests from `results/alignment.json`).

**Why these numbers are not a ranking.** A literal prose crib is written to carry every word; a rhymed poem in
English couplets is not trying to. Verse needs rhyme and metre words; English needs articles, pronouns and
auxiliaries that Greek puts into word endings; Greek has particles (δέ, μέν, γάρ, μάν) that English often leaves
unsaid. Of Wharton's 9 dropped words, 7 are such particles or the article; his 8 added words are six "my"s and
"in", "madness". Smollett's poem is a love song that borrows a few of Philips's lines; it was not written as a
translation of this ode at all.

**What the alignment shows, line by line** (each point can be checked in `results/alignment.json`):

1. **"Seems to me."** Φαίνεταί μοι ("appears to me") survives in Catullus ("mi ... videtur"), Symonds ("he seemeth
   to me") and Wharton ("seems to me"). Philips (1711) and Merivale (1833) both open "Blest as the immortal gods is
   he": no "seems", no "to me", and two words with no Greek counterpart ("Blest", "immortal").
2. **Catullus adds a line of his own** in the first stanza ("Ille, si fas est, superare divos", roughly "he, if it is
   right, surpasses the gods") and a **closing stanza about idleness** ("Otium, Catulle, tibi molestum est ...")
   that has no counterpart in Sappho's Greek.
3. **Catullus moves "sweetly"** (ἆδυ) from her speaking to her laughing ("Dulce ridentem") and drops the speaking.
4. **Seeing is added.** The Greek man sits and listens. Catullus has him "spectat et audit" ("watches and hears") "identidem"
   ("again and again"); Philips has "hears and sees thee all the while". We note the match; we do not claim to know
   that Philips worked from the Latin.
5. **Merivale moves the senses to the end**: "together fail / Both sight and sound" gathers the eyes (stanza 3) into
   the last line.
6. **One line is missing from the Latin** (Catullus line 8): the counterpart of φώνας ("voice") is lost with it.
   Editors have filled it with guesses ("Quod loquar amens", "vocis in ore"); we show the gap, not a guess.
7. **Smollett's first stanza carries no word of Sappho's first stanza** (0 of 16). His 11 carried words come from
   stanzas 2-3 (gazing, tongue, flame, frame) and echo Philips's rhyme "flame / vital frame".

## Side box: γλυκύπικρον, "sweet-bitter"

In Wharton's fr. 40 (= Voigt 130), line 2, page 96, Sappho calls Eros γλυκύπικρον. The word is a compound of
γλυκύς and πικρός. LSJ glosses γλυκύς "sweet to the taste or smell" and πικρός "bitter" (its first sense is
"pointed, sharp, keen"), and it glosses the compound γλυκύπικρος "sweetly bitter", citing this very fragment
("Sapph. 40"). The two 19th-century English renderings printed by Wharton both swap the order:

* Wharton's prose: "Now Love masters my limbs and shakes me, fatal creature, bitter-sweet."
* Symonds (1883): "The bitter-sweet impracticable thing,"

The Nobel Committee for Literature writes that her essay *Eros the Bittersweet* (1986) "draws heavily on a compound
adjective from Sappho" ([bio-bibliography](https://www.nobelprize.org/prizes/literature/2026/bio-bibliography/),
Anders Olsson; the sentence is stored verbatim in `data/sources/nobel_committee_sentence.json`). The Committee does
not name the word, and we do not summarise the book.

## Figures

All in `results/`, each as `_light.png` and `_dark.png` (plus `.svg`), each labelled "Educational demos made to show
an open-source tool. Not research." and with its sources.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="results/threads_stanza1_dark.png">
    <img alt="A grid. Across the top, the 16 Greek words of Sappho's first stanza with their dictionary glosses. Down the left, a timeline rule with six versions, oldest first: Catullus (1st century BC), then a break of about 1,750 years, Philips 1711, Smollett 1748, Merivale 1833, Symonds 1883, Wharton 1885. Each Greek word has a thread running down; where a version has a counterpart, a dot sits on the thread with the counterpart words under it (filled dot for close sense, open blue dot for loose); where it has none, a short pencil gap. On the right, each version's count of carried words and its added words in red. Smollett's row is all gaps." src="results/threads_stanza1_light.png" width="900">
  </picture>
</p>

* `threads_stanza1` (1920 x 1240, for the video and desktop): the first stanza, 16 Greek words, six versions on a
  timeline rule (rows not to scale; the break marks about 1,750 years between Catullus and Philips).
* `threads_line1` (1080 x 1500, phone): the first line only, "who kept 'seems' and 'to me'?".
* `counts` (1080 x 1350): carried (close, loose, dropped) and added, per version, whole poem.
* `glukupikron` (1080 x 1350): the word split into its two halves, the LSJ glosses, the two "bitter-sweet"
  renderings in reversed order, and the Committee's line.

Colours: paper #f3ece0, ink #2b2118, pencil #b9ad9a, accent #a8432a (added words), second accent #3f6e8c (loose links);
the dark theme swaps paper and ink and lightens the accents, as in the other Literature lanes. Colour is never the
only signal: close = filled dot and upright text, loose = open dot and italic, dropped = gap, added = a "+" list.
Greek in GFS Didot, the rest in Literata (both SIL OFL 1.1, in `data/fonts/`).

## How we aligned (the rules)

* **R1 Units.** Greek words as Wharton prints them (a word split across two lines by a hyphen, φωνεύ-σας, is one
  word): 71 in lines 1-16. Version words are runs of letters; apostrophes and hyphens inside a word stay ("tongue's",
  "'Twas", "love-trance"); punctuation is not a word.
* **R2 Links.** A link joins one Greek word to the version words that carry its meaning, anywhere in the version
  (translators move things). **R2b**: one version word may serve two Greek words when it fuses them (Philips's "was
  lost" = "nothing" + "comes").
* **R3 Grammar words** go with the Greek word whose form they express: an article for a noun ("the gods"), a
  preposition for a case ending ("of gods", "to me"), an auxiliary or subject pronoun for a verb ending ("I see",
  "has run"). Possessives the Greek does not have ("my breast") count as added. **R3b**: a word that spells out a
  person or thing the Greek leaves implied goes with the Greek word that implies it (Wharton's "close to him",
  "all my body", "one dead"). **R3c**: an added epithet ("immortal", "cold", "wild") stays unlinked.
* **R4 Strength.** *Close*: the version word keeps the sense of the Greek word as LSJ glosses it (part of speech may
  change: "speaking" to "speech"). *Loose*: it stands in the same slot but shifts the sense ("man" to "youth",
  "laughing" to "smile"). **R4b**: when a version word matches one Greek word's sense and another's slot, it goes
  with the sense (Catullus's "Dulce" goes with ἆδυ "sweetly", not with ἰμερόεν).
* **R5** No link without a shared part of the Greek word's own meaning: a whole-clause paraphrase ("a darkness hung"
  for "I see nothing") leaves the Greek words dropped and the English words added.
* **R6** Particles and conjunctions link only to a word doing the same job ("and", "but", "for", "when").
* **R7** Greek line 17 and Wharton's prose for it ("But I must dare all ...") are out of scope.

## The two passes

1. **Pass 1** (`data/alignment_pass1.json`): made by hand, word by word, by the agent that built this folder.
2. **Pass 2** (`data/alignment_pass2.json`): a full second pass over all 6 x 71 = 426 decisions, made by a separate
   Claude instance that was given only the texts, the LSJ glosses and the rules R1-R7 (written before either pass
   was compared), and was not shown pass 1. It is a second pass by the same kind of annotator, not an independent
   human expert.
3. **Comparison** (`results/pass_disagreements.json`): the passes agree on 370 of 426 decisions (86.9 %) and
   disagree on **56** (target words or strength).
4. **Resolution** (`data/resolution_log.json`, made by `translators/resolve_passes.py`): every one of the 56 has a
   decision and the rule it rests on: 36 follow pass 1, 17 follow pass 2, 3 are new. The rules R2b, R3b, R3c and R4b
   were written during this step to settle recurring disagreements, then applied to every case. The resolver also
   made pass 1, so the resolution may lean towards pass 1: the ranges in the table show how much the counts move
   between the passes (at most 2 Greek words carried and 4 words added).
5. **Final** (`data/alignment_final.json` → `results/alignment.json`).

Open doubts left in the log: Wharton's "in my madness" for the bracketed [ἄλλα] (he may be translating another
reading; we leave it unlinked); whether Philips's "by" answers ἐναντίος "facing" or πλασίον "near" (we say near);
Merivale's "look on thee" for ἐναντίος (loose).

## Glosses

From **LSJ** (Liddell, Scott and Jones, *A Greek-English Lexicon*, 9th ed. 1940) in the Perseus digital edition,
licence **CC BY-SA 4.0**: "Text provided under a CC BY-SA license by Perseus Digital Library,
http://www.perseus.tufts.edu, with funding from The National Endowment for the Humanities. Data accessed from
https://github.com/PerseusDL/lexica/ [2026-10-08]." (commit 56061ca). We used LSJ, not the 1889 *Intermediate
Greek-English Lexicon* ("Middle Liddell"): the Perseus website refused scripted access on 2026-10-08, and the
Perseus GitHub repository holds LSJ only.

* `data/lsj_entries.json` stores, for each headword we use, the first 12,000 characters of its XML entry verbatim,
  plus verbatim windows around any gloss or citation further in, with the sha256 of the whole entry.
* `data/glosses.json` names the exact LSJ phrase we show for each headword. For dialect forms that LSJ only
  cross-refers (κῆνος, "Aeol. for ἐκεῖνος"), the gloss is taken from the entry LSJ points to.
* LSJ itself cites this poem, line by line, in 22 of the entries (as "Sapph. 2.N", Bergk's numbering, the same as
  Wharton's); the tests check each citation. Where LSJ cites the line under a particular sense we show that sense:
  ἄκουαι "ear", εἴκει "it is allowable or possible".
* `translators/lemmas.py` (which headword each Greek word belongs to, and the form notes, e.g. "Aeolic for ...") is
  our own lemmatisation.

**Licences in this folder.** Code: MIT. `data/lsj_entries.json`, `data/glosses.json` and the gloss fields in
`results/alignment.json` are derived from Perseus LSJ and are therefore **CC BY-SA 4.0** (credit above). The Greek,
Latin and English texts are public domain (excerpts copied byte for byte from Project Gutenberg #57390 and #4085,
Latin Wikisource, archive.org scans). Fonts: SIL OFL 1.1. The Nobel Committee sentence is quoted for attribution only.

## Every caveat

* **The Greek is Wharton's 19th-century text** (Bergk 1882 via Wharton 1908), not a modern edition. Modern texts
  differ in several words (for example in lines 13 and 16). LSJ marks 'πιδεύης (line 15) as a conjecture.
* **Accents as printed.** We keep Wharton's spellings exactly (κήνος, ὐπαδεδρόμακεν, μίδρως; fr. 40 has λυσιμελης
  without an accent in the Gutenberg transcription).
* **Wharton's text of each version**, not the first printing: small differences are listed in
  `data/crosschecks.json`; none changes a word we align.
* **Wharton's prose** dates from 1885 but we read it in the 1908 edition.
* **Smollett's poem is a version only in Wharton's sense**: Smollett did not present it as a translation.
* **"Version", not "translation"**, for Philips and Catullus: both are often called imitations.
* **Catullus's text is a composite**: lines 1-12 as Wharton quotes them, lines 13-16 from Merrill 1893.
* **The counts are ours.** They depend on our word units, rules and readings. Two passes disagreed on 13 % of
  decisions; the ranges show the effect. Close/loose is a judgement.
* **No "best", no "most faithful".** A count of carried words rewards literal prose by construction.
* **Glosses are short.** One phrase per headword cannot carry a dictionary entry; the stored entries have the rest.
* **About 1,900 years**, not exactly 2,000: from Catullus (1st century BC) to Wharton (1885).
* **Timeline rows are not to scale** (a marked break covers about 1,750 years).

## Files

| path | what |
|---|---|
| `results/versions.json` | the Greek and the six versions: lines, word tokens (ids `version:line:k`), page and excerpt-line anchors, source URLs, sha256 of the source files |
| `results/alignment.json` | final links (Greek token id → version token ids, close/loose), Greek tokens with LSJ headword and gloss |
| `results/counts.json`, `results/translators_summary.json` | counts per version, with the lists of dropped and added words and the range over passes |
| `results/pass_disagreements.json` | the 56 disagreements between the passes |
| `data/alignment_pass1.json`, `data/alignment_pass2.json`, `data/alignment_final.json`, `data/resolution_log.json` | the hand alignment, both passes, the reconciled one and the log |
| `data/sources/` | verbatim excerpts: Wharton fr. 2 and fr. 40 (Gutenberg #57390, HTML lines 2291-2519 and 3315-3352), *Roderick Random* ch. XL (Gutenberg #4085, lines 8957-9022), the Committee sentence; `crosscheck/` holds the independent witnesses |
| `data/lsj_entries.json`, `data/glosses.json` | LSJ excerpts and chosen glosses (CC BY-SA 4.0) |
| `translators/` | `sources.py` (excerpts, tokens), `versions.py`, `lsj.py`, `lemmas.py`, `align.py`, `resolve_passes.py`, `figures.py`, `run_all.py` |
| `tests/test_translators.py` | the checks below |

## Tests

`python -m pytest -q tests` checks that: each stored excerpt is unchanged (sha256) and, when the full Gutenberg files
are present, is an exact slice of them; every Greek, Latin and English line shown is in its source excerpt as a
browser renders it (tags and Gutenberg page-number markers removed, entities decoded, white space collapsed);
Wharton's prose, cut at stanza ends, joins back into his paragraph exactly; every token's characters are at its
recorded position; every reference in all three alignment files resolves to exactly one existing token; the
resolution log covers exactly the disagreements, and outside them the final alignment equals both passes; nothing
links into out-of-scope lines; the counts and summary are reproduced from the alignment; every gloss and every
"Sapph. 2.N" citation is in the stored LSJ text (and, with `LSJ_DIR` set, that the stored text is an exact part of
the Perseus files); the Committee words are in the stored sentence; the figures exist in both themes.
