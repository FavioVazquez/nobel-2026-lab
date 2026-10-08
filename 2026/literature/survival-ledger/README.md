# The survival ledger (Literature 2026)

> **Educational demos made to show an open-source tool. Not research.**
> Ancient counts are testimony, modern counts are estimates, and they disagree. Every number below is a range or an
> "about", with its sources. There is no single "percentage lost" anywhere in this folder.

The 2026 Nobel Prize in Literature went to Anne Carson "for her bold and inventive oeuvre that, in playful dialogue
with the classical tradition, has created new forms for contemporary literature". The classical tradition that the
Nobel Committee's bio-bibliography names (Sappho, Sophocles, Euripides, Aeschylus, Stesichoros, Simonides, Thucydides,
Catullus) is itself mostly lost. This folder asks, for each of those authors: how much did they write, by ancient
testimony and by modern estimate, and how much survives?

No line of any ancient author, and none of Carson's text, appears here: only counts, dates and short quoted sentences
from the sources that give them.

Own code, MIT licence. CPU only. Python 3.11 with Matplotlib.

## Run it

From `2026/literature/survival-ledger/`:

```bash
python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python -m ledger.run_all          # results/ledger.json and 4 figures (+ SVG), a few seconds
python -m pytest -q tests         # 12 tests, under a second (1 skipped unless LIT_BIO_HTML is set)
python -m ledger.check_sources    # optional, network: re-fetches all 53 sources (46 quotes, 7 paraphrases), writes results/source_check.json
```

`LIT_BIO_HTML=/path/to/saved/bio-bibliography.html python -m pytest -q tests` also checks, byte for byte, that each
author is named by the Committee in the phrase we store.

## The ledger

| author | dates | ancient testimony | modern estimate | survives |
|---|---|---|---|---|
| **Sophocles** | c. 497/496 – 406/405 BC | 123 plays, more by some counts (Suda); 130 ascribed, 17 spurious, so 113 (Aristophanes of Byzantium, in Smith 1867) | more than 120 (Wikipedia; Durham Living Poets) | **7** complete plays, plus about half of the satyr play *Ichneutae* from a papyrus |
| **Euripides** | c. 480 – c. 406 BC | 75 or 92 (Suda, which says 77 survived in its day); 75 (Varro); 95 (some ancient scholars) | about 88 to 95 ("approximately 92", Furman; 22 productions, Collard 1981; Wikipedia) | **18 or 19** (19 attributed; the *Rhesus* is disputed); includes the satyr play *Cyclops* |
| **Aeschylus** | c. 525/524 – c. 456/455 BC | 90 tragedies (Suda); 70 tragedies + 5 satyr plays (ancient Life) and 73 (ancient catalogue), as summarised by Ireland 1986 | 70 to 90 (Wikipedia; World History Encyclopedia) | **7**, of which *Prometheus Bound* is of disputed authorship: **6 or 7** |
| **Stesichoros** | c. 630 – c. 555 BC | 26 books (Suda) | none found | **fragments only** |
| **Stesichoros' Geryon poem** (*Geryoneis*) | 6th century BC | at least 1,300 lines: a line number "1300" in the margin of the papyrus (P.Oxy. 2617 fr. 7 = S27) (Mahoney 2009; Finglass 2022) | 1,300 to about 2,000 (West 1971; Wikipedia, after West 1993 and Pavese 1972) | about **180** lines in readable form (Mahoney 2009; one source) |
| **Sappho** | c. 630 – c. 570 BC | nine books (Suda); the Alexandrian edition had at least eight (Wikipedia, after Yatromanolakis). **Book I: 1,320 verses**, written on the roll's own end-title (P.Oxy. 1231 fr. 56; Grenfell & Hunt 1914, p. 20; Green 2015) | about **9,000** verses (Grenfell & Hunt 1914) to about **10,000** lines (Green 2015; Wikipedia, after Rayor & Lardinois 2014; Univ. of Missouri) | about **650** lines (Wikipedia; Missouri; Illinois); only fragment 1, the Ode to Aphrodite, is certainly complete |
| **Simonides of Keos** | c. 556 – 468 BC | the Suda lists his kinds of poem but gives no count | none found | a small part: fragments and some short pieces; a papyrus published in 1992 (P.Oxy. 3965) "quadrupled" it (AGNI) |
| **Catullus** | c. 84 – c. 54 BC | none found | 116 numbered poems; 18-20 are left out of most editions, so about 113, "necessarily approximate" | about **113 to 116** poems. Nearly all reached us through **one manuscript, V**, known at Verona around 1300 (c. 1290-1310) and lost before 1400; poem 62 also survives in the 9th-century Codex Thuaneus |
| **Thucydides** | c. 460 – c. 400 BC | 8 books, or 9 (Diodorus 13.42), or 13 (Marcellinus, *Life* §58) | 8 books (a later division, not his own) | **all 8**, but unfinished: it breaks off mid-sentence in 411 BC; the war went on to 404 BC |

Every row in `results/ledger.json` has `author`, `dates`, `unit`, `ancient_count`, `modern_estimate` and `survives`,
each with `value` or `range`, a plain `text`, `notes` and a `source` list (name, URL, anchor, the exact quoted words,
access date). For the six Suda On Line entries and the World History Encyclopedia article the source carries our `paraphrase` instead of a quote (see Licence). A modern estimate that has no upper bound ("more than 120") carries `"open_ended": true` with its lower bound as `value`. The full list of 54 sources is in [`ledger/rows.py`](ledger/rows.py).

**How the sources were checked.** On 2026-10-08, `python -m ledger.check_sources` fetched every one of the 53 quoted
pages (Wikipedia as wikitext, archive.org scans as their OCR text) and found each stored quote in its page's text: 53
of 53 sources (46 quotes; for the six Suda On Line entries and the World History Encyclopedia article, which we paraphrase, it checks the key words: the numbers and kinds of work) ([`results/source_check.json`](results/source_check.json)). The Committee page is checked by the optional test.

## The four open items, resolved

1. **Play counts, Suda against modern.** Kept apart, two ranges per tragedian (table above). The Suda is a
   10th-century Byzantine encyclopedia: it is testimony, not a count we can repeat.
2. **The length of the Geryon poem, and its source.** "At least 1,300 lines", because one papyrus fragment
   (P.Oxy. 2617 fr. 7, numbered S27) carries the line number 1300 in its margin. Mahoney (BMCR 2009.06.20) and
   Finglass (2022, citing Davies and Finglass 2014) say so; West (1971) thought the whole "perhaps closer to two
   thousand". Which Greek numeral is written is UNVERIFIED and left out.
3. **Catullus, the manuscript wording.** Use: "Nearly all of Catullus reached us through one manuscript, which was at
   Verona around 1300 and was lost before 1400; one poem (62) also survives in a 9th-century anthology." Sources:
   Wikipedia "Poetry of Catullus" ("the sole source of nearly all of the poet's surviving work"; "1290–1310"), the
   Loeb introduction (Cornish, 1913/1921: "at Verona early in the fourteenth century ... disappeared before the end of
   the century"), Kiss 2015. Avoid "found in 1305" alone (Wikipedia's "Catullus" article says 1305; the other
   sources give a span).
4. **Sappho.** About 9,000 to 10,000 lines in all (estimates), about 650 survive, Book I alone 1,320 verses (330
   stanzas). The 1,320 is not an estimate: it is written on the papyrus roll's end-title (P.Oxy. 1231 fr. 56), as
   Grenfell and Hunt report (1914, p. 20). The ratio 650 / 10,000 is not shown as a percentage; the grid shows it.

## UNVERIFIED, and left out

* Which Greek letter-numeral the Geryoneis papyrus uses for 1,300.
* The anonymous ancient Life of Euripides' counts (92 plays, 78 preserved): seen only in a search snippet.
* Rayor and Lardinois 2014, p. 7 (the book Wikipedia cites for 10,000 and 650): not opened; we cite the pages that
  state the numbers.
* An ancient count of Catullus' poems: none found.
* The day of the Paris Catullus manuscript (G): we say 1375 only.
* Who edited P.Oxy. 3965: we give the number and the year (1992) only.
* Britannica and Oxford Classical Dictionary figures (pages refused automated access).
* Smith (1867) elsewhere says 27 spurious plays of Sophocles, not 17: we use the main entry.

## The figures

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="results/bookshelf_dark.png">
    <img alt="An ink bookshelf, one row per author the Nobel Committee names, one mark per play or book. Sophocles: 7 solid ink marks among more than 120 pencil outlines (dashed up to 130, a drawing range: the estimate is open-ended). Euripides: 18 solid and 1 hatched (the disputed Rhesus) among about 90. Aeschylus: 6 solid and 1 hatched (Prometheus Bound) among 70 to 90. Stesichoros: 26 pencil books, each with a small ink bar for fragments. Sappho: 8 or 9 pencil books with fragment bars. Catullus: one solid book, through one lost manuscript. Thucydides: all 8 books solid, but the history stops mid-sentence in 411 BC." src="results/bookshelf_light.png" width="720">
  </picture>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="results/sappho_grid_dark.png">
    <img alt="A 100 by 100 grid of 10,000 faint dots, a modern estimate of all the lines Sappho wrote, labelled ESTIMATE; 650 dots, scattered at random, are inked: the lines that survive. A red outline around the first 1,320 dots marks Book I, whose verse count is written on the papyrus roll's own end-title (P.Oxy. 1231, Grenfell and Hunt 1914). A blue dashed line after 9,000 dots marks Grenfell and Hunt's older estimate. Only fragment 1, the Ode to Aphrodite, is certainly complete." src="results/sappho_grid_light.png" width="560">
  </picture>
</p>

**Simplifications.** One mark per play or book, at the modern estimate; marks beyond its low end are dashed. Plays
and books are not the same size, so the rows are not comparable in volume. A "fragment" bar says only that pieces
survive, not how much. In the Sappho grid, the inked dots are placed at random (seed 2026); their positions mean
nothing, and the total is an estimate. Simonides has no row on the shelf: no source gives a count.

## Data for the video and the page

| file | contents |
|---|---|
| `results/ledger.json` | `status`, the label, the reading rules, the 9 rows (each field with value or range, text, notes, sources with URL, anchor and quote), the unverified list, the resolved open items |
| `results/source_check.json` | the last run of the source check (53 of 53 found: 46 quotes, 7 paraphrase key-word checks) |
| `results/bookshelf_{light,dark}.{png,svg}`, `results/sappho_grid_{light,dark}.{png,svg}` | the figures |

For the shelf, each row's `shelf` block gives `total` and `survive` as [low, high] and a short `label`; the Sappho row
has a `grid` block (10,000 dots, 650 inked, Book I 1,320, the 9,000 alternative, label "estimate").

## What each file does

| file | in plain words |
|---|---|
| `ledger/rows.py` | every number, range and source (with the quoted words, or our paraphrase for the Suda and the World History Encyclopedia), the unverified list |
| `ledger/run_all.py` | builds `results/ledger.json` and the figures |
| `ledger/figures.py`, `ledger/style.py` | the bookshelf and the Sappho grid, light and dark |
| `ledger/check_sources.py` | re-fetches every source and looks for its quote (network) |
| `tests/test_ledger.py` | only Committee-named authors; every number sourced, two sources where possible; ranges ordered; the grid matches the estimates; no percentage; the quote check found every quote |
| `fonts/` | Literata, EB Garamond and Caveat (SIL Open Font License 1.1, licence files alongside); also used by `../forms/` |

## Licence

Our code: MIT. The sources are cited, not copied: Wikipedia (CC BY-SA) for facts only; Grenfell and Hunt (1914, public
domain). **We paraphrase NC-licensed sources.** Two sources are under a Creative Commons
Attribution-NonCommercial-ShareAlike licence, which does not fit this MIT repository: the Suda On Line translations
(see the [SOL rights page](https://www.cs.uky.edu/~raphael/sol/sol-html/rights.shtml)) and the World History
Encyclopedia article on Aeschylus. They are cited (entry, translator or author) and said in our own words, never
copied; the source check looks for their key words on the page instead. The quotations from W. Smith's *Dictionary of
Greek and Roman Biography and Mythology* (1867, public domain) were read in the Perseus Digital Library's digital copy,
which is under CC BY-SA 3.0: credit to the Perseus Digital Library, Tufts University, <https://www.perseus.tufts.edu/>.
Fonts: SIL OFL 1.1.
