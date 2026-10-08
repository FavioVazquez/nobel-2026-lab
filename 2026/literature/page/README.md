# "Guess first, then see" page (Literature 2026)

> **Educational demos made to show an open-source tool. Not research.**

Open the page: <https://faviovazquez.github.io/nobel-2026-lab/2026/literature/page/> (or open `index.html` from a local copy).

One self-contained page about the 2026 Nobel Prize in Literature, awarded to Anne Carson "for her bold and inventive
oeuvre that, in playful dialogue with the classical tradition, has created new forms for contemporary literature". It
looks like a manuscript: warm paper, iron-gall ink, and a pale editor's hand in red. In dark mode it is the same
manuscript read by lamplight (the "light the lamp" button switches by hand). Strokes draw themselves as they scroll into
view: shelves, rules, the histogram, threads between words. A visitor guesses first, then reveals the answer, with the
source and the caveat next to every number.

She is a living author. **No passage of her work is on the page**, no picture of her, no cover art. Her own words
appear only as three short quotations used as commentary (at most 15 words each, one per book, attributed "Anne
Carson, *Work* (year)"), read from [`../quotes.json`](../quotes.json), where each carries the pages that confirm its
wording ([CLAIMS.md](../CLAIMS.md) L59, L60, L62; L61 was withdrawn). The Carson quotation about brackets sits next to the sentence that says square brackets mark where a papyrus is gone, because it is about those holes. Every ancient Greek or Latin line and every old English version is public
domain and carries its edition and page. The other quoted words about her are the Swedish Academy's citation and the
Nobel Committee's own sentences, with credit.

0. **The prize.** The citation, quoted and attributed; who she is in two lines (Canadian, born in Toronto in 1950; a
   classicist who translates from Classical Greek). Facts from the Nobel facts page and the Committee's bio-bibliography.
   A line under it links to [the film](../video/README.md) (2:29, the MP4 in `../video/exports/`); the footer links it again with
   its claims, captions and credits. A test checks that the linked file exists.
1. **How much survives** (from [survival-ledger](../survival-ledger/README.md)). Guess: "Scholars estimate that Sophocles wrote
   more than 120 plays. How many survive complete?" Then one ink shelf per author the Committee names: a circle per play or
   book, inked red if it survives, pencil if lost, a slashed circle where the sources give a range, red scraps for
   "fragments only". A switch redraws every shelf with the ancient testimony (the Suda and others) or the modern
   estimates. The Geryoneis is a bar of lines (about 180 readable of at least 1,300). Then Sappho: a 100 x 100 grid of
   pencil dots, one per line of the higher estimate (10,000), about 650 inked, Book I's 1,320 verses outlined, and the
   1914 lower estimate (9,000) as a dashed line. Labelled "estimate"; where a dot sits means nothing.
2. **Where the words went** (from [fragments](../fragments/README.md)). Guess: how long is a typical fragment? Then three kinds of
   loss. (a) P.Oxy. 1231 fr. 1 col. i 13-34 (Sappho 16 Voigt) as Grenfell and Hunt printed it in 1914, on a torn
   papyrus; a slider runs from "only what the papyrus holds" (holes) to "with the editors' restorations" (the pale
   hand), with the letter counts and their 1914 English. (b) Sappho 31 as Wharton prints it, written line by line until
   the quotation in *On the Sublime* stops, with a pen blot and empty ruled lines. (c) The fragment-length histogram
   (tap a bar for its fragments) and who quoted them. A switch renumbers every fragment on the page, Wharton 1908 or
   Voigt 1971.
3. **One poem, 2,000 years of translators** (from [translators](../translators/README.md)). Guess: how many of the six versions
   keep "seems ... to me"? Then the four stanzas of Sappho 31 (Wharton's Greek) above Catullus, Philips 1711, Smollett
   1748, Merivale 1833, Symonds 1883 and Wharton's prose. Hover or tap a Greek word: an ink thread runs through every
   version to its counterparts (dashed for a loose match), a version it skips dropped the word (or moved it, and the
   page says to which stanza), and the word's LSJ gloss shows under the Greek. "Show the additions" underlines the words
   with no Greek behind them. Counts are "our rough count". Then the bitter-sweet box: γλυκύπικρον split into its two
   halves, the English versions that turn it round, and the Committee's sentence about *Eros the Bittersweet* (the
   Committee does not name the word).
4. **New forms** (from [forms](../forms/README.md)). Her books as the Committee's bibliography lists them ("a selection"), one
   spine per entry, banded by the forms the entry's own line or the Committee's essay names; tap a form to light its
   books, hover a spine for the words each band rests on. Guess: in how many orders can *Float*'s 22 chapbooks be read?
   22! = 1,124,000,727,777,607,680,000, with 22 chapbooks to shuffle. Guess: how many of the 123 laureates since 1901
   were women? One spine per laureate by decade, women inked red, Carson ringed; the second Canadian after Alice Munro.

Every number in the page's text is read from `data.js`; none is typed into `index.html` (a test checks that the page
itself contains no Greek either). If any input is not `"final"`, a red "Preliminary" box under the label says which, and
each number from it carries a "preliminary" (or "placeholder") tag.

## Open it

Double-click `index.html`, or from this folder: `open index.html` (macOS) / `xdg-open index.html` (Linux). No server, no
network, no CDN: it works from `file://` and from GitHub Pages. Light and dark follow the system; the lamp button
overrides it (remembered in the browser if storage is allowed). Every animation jumps to its end when the system asks
for reduced motion.

Colours: paper `#f3ece0`, ink `#2b2118`, pencil `#b9ad9a`, the editor's red `#a8432a` (survivors, restorations,
threads), blue `#3f6e8c` (our own marks: medians, counts, the other estimate). Survivors and losses differ by fill as well
as colour (solid against outline), loose links by dashes, forms by pattern as well as colour.

## Files

| file | what |
|---|---|
| `index.html` | the page: HTML, CSS and plain JavaScript in one file; drawings are inline SVG, the Sappho grid is a canvas |
| `data.js` | generated by `build_data.py`; sets `window.NOBEL_LIT_DATA` (about 150 KB) |
| `build_data.py` | reads the four experiments' results, writes `data.js` (Python 3 standard library only) |
| `fonts/` | five WOFF2 subsets (about 115 KB in all) and `OFL.txt`, made by `make_fonts.py` |
| `make_fonts.py` | subsets the fonts to the characters the page uses and renames them, as the OFL asks |
| `run_all.py` | one command: `build_data.py`, then the browser checks, screenshots and `og.jpg` |
| `og.jpg` | the 1200 x 630 share image, a screenshot of `index.html#og` |
| `screenshots/` | the page after every reveal, at 360, 768 and 1440 px, light and dark |
| `tests/` | `test_build_data.py` (pytest), `test_page.mjs` (headless Chromium), `test_page.py` (runs it under pytest), `fixtures/` |

## Where the content comes from

`build_data.py` reads, relative to this folder:

| input | used for |
|---|---|
| `../survival-ledger/results/ledger.json` | section 1: every count (`ancient_count`, `modern_estimate`, `survives`, `shelf`) with its sources, the Sappho `grid`, the reading rules |
| `../fragments/results/fragments.json` | section 2: `papyrus` (lines as edition spans, letter counts, the 1914 English), `sappho31` (lines, stanzas, `cut_point`), `wharton_fragments` and `stats` (the histogram), `quoters_network` |
| `../translators/results/versions.json` | section 3: Wharton's Greek and the six versions, line by line, with token positions; `fr40` for the bitter-sweet box |
| `../translators/results/alignment.json` | section 3: the hand alignment (`links`, close or loose) and each Greek word's LSJ gloss |
| `../translators/results/translators_summary.json` | section 3: the counts per version (carried, dropped, added, and their range over the two passes) |
| `../translators/data/glosses.json` | section 3: the LSJ glosses of γλυκύς and πικρός (optional) |
| `../forms/results/forms.json` | section 4: the bibliography entries, their tags and the quoted words each tag rests on; `float_22` |
| `../forms/results/prize_history.json` | section 4: laureates and women by decade, shared and missing years, the Canadian line |

Fixed facts live in `build_data.py` with their sources: the citation (press release), the two "who she is" lines (Nobel
facts page and bio-bibliography), the Committee's sentences on *Float* and on *Eros the Bittersweet*, and the number of
chapbooks (22). The page computes nothing else beyond presentation: 22! (checked against `forms.json`), the share of
restored letters, which versions keep both "seems" and "to me", and the decade layout.

```bash
python3 build_data.py                       # from 2026/literature/page/ after the merge
python3 build_data.py --from LEDGER_RESULTS FORMS_RESULTS FRAGMENTS_RESULTS TRANSLATORS_RESULTS
python3 build_data.py --fixtures            # trimmed copies in tests/fixtures (status "fixture")
```

It prints the status of each input file and a warning when two of its numbers disagree (the histogram against the
fragment count, the decades against the totals, 22! against `forms.json`).

## Fonts

All SIL Open Font License 1.1, self-hosted as subsets: **Literata** (body; Google Fonts, `Literata[opsz,wght].ttf` and
`Literata-Italic[opsz,wght].ttf`, pinned at optical size 12, weights 400 and 600), **GFS Didot** (polytonic Greek;
Greek Font Society), **Caveat** (the editor's notes, Latin letters only; Greek never appears in a handwriting face).
`make_fonts.py --src DIR` rebuilds them from the source files (it fetches nothing; with no upright Literata it falls back
to Fraunces). It needs fontTools 4.40 or newer; with no brotli it writes TTF, and `make_fonts.py --compress` turns
those into WOFF2. Each subset is renamed "Lit Page ...", because GFS Didot reserves its name.

## Simplifications (what this page does not claim)

- No translation is ranked. The alignment and its counts are ours, a crude measure, not a score of quality.
- The Greek is Wharton's 19th-century text and Grenfell and Hunt's 1914 readings; modern editions differ in places.
- Restorations are the 1914 editors' guesses, not Sappho's words.
- Ancient counts are testimony, not measurements; a range is drawn wherever sources disagree, and there is no single
  "percentage lost". The Sappho grid is one estimate; the position of an inked dot means nothing.
- The forms are tags on a selection, each resting on a quoted phrase; the list is not her whole output.
- The 22! orders say nothing about how *Float* is meant to be read beyond "any order".
- Prize counts describe the record; gender is as the Nobel API records it, Canada by press-release wording.

## Test it

Needs Node 18+ and `playwright-core` with a Chromium build (showtime installs both under `~/.showtime`), and Python 3
with pytest. See `requirements.txt`.

```bash
python3 -m pytest -q tests                  # build_data checks + the browser check (about 60 s)
PLAYWRIGHT_BROWSERS_PATH=~/.showtime/browsers node tests/test_page.mjs --shots --og   # also screenshots and og.jpg
cd .. && python3 -m page.run_all            # rebuild data.js, check, screenshots and og.jpg in one go
```

`test_build_data.py` checks that every line the page sets is an unchanged string of the experiments' files (the pieces
a line is cut into join back to it byte for byte), that every alignment link points to a word on the page, that every
ledger number has a source, the histogram adds up, 22! is exact, the prize counts add up (123, 19), the Greek font
covers every Greek character in `data.js`, that `index.html` types no Greek and none of the laureate's words, and that
every quotation in `../quotes.json` has at most 15 words, a work, a year and its source pages, one per work. The
browser check asserts that every quotation shown on the page is in `quotes.json` word for word, attributed, within the
cap, and shown once.

The browser check opens `index.html` from `file://` at 360, 768 and 1440 px in light and dark (and once with reduced
motion), makes every guess, reveals every answer, flips the ancient/modern switch, moves the papyrus slider to both ends
(restorations hidden, then shown), taps a histogram bar and renumbers it Wharton to Voigt, hovers and taps Greek words
(the right number of counterparts light up, threads are drawn, the gloss shows), changes stanza, filters the forms
shelf, shuffles the chapbooks, and checks: no console errors, no network requests, no sideways scrolling, the
self-hosted fonts load, every chart has a title and a description, the share tags are there and there is no canonical
link, and page + data + fonts stay under 1.5 MB. It also checks that a copy with every input final hides the
"Preliminary" box and that copies missing any one experiment say so and still have no errors.

MIT licence, like the rest of the repo (the fonts keep their OFL; LSJ glosses stay CC BY-SA 4.0, credited on the page).
