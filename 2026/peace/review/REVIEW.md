# Review of the two Peace 2026 data toys

> **Educational demos made to show an open-source tool. Not research.** This is an independent review of
> `peace-ends` (`2026/peace/how-conflicts-end/`, commit c81cf1f) and `peace-hold`
> (`2026/peace/do-agreements-hold/`, commit 72d6b38). The toy branches were not changed.

## Verdicts

| toy | verdict |
|---|---|
| 1, how-conflicts-end | **FIX FIRST** (6 fixes below; the numbers are right, the reading of them needs work) |
| 2, do-agreements-hold | **FIX FIRST** (6 fixes below; the code is right, the headline depends on the clock definition) |

## 1. Reproduction

Python 3.11.17 (uv), each toy's pinned `requirements.txt`, fresh venv.

| check | toy 1 | toy 2 |
|---|---|---|
| `fetch_data` downloads, raw sha256 matches the pin | yes (Termination v.4 2024 csv) | yes (PA 22.2 xlsx and Termination csv) |
| rebuilt derived CSVs identical to the committed ones (sha256) | yes | yes (both) |
| `run_all` reproduces the committed JSON and figures (`git status` clean) | yes | yes |
| `pytest` with the raw files present (no skips) | 10 passed | 12 passed |

The 14 warnings in each run are `PyparsingDeprecationWarning`s from Matplotlib: `pyparsing` is a transitive dependency and
is not pinned (the newest 3.x is pulled). Harmless now; pin it, or accept that warnings may grow.

Raw files are gitignored and were never committed on either branch. The derived CSVs hold only numeric ids, years
and codes.

## 2. Toy 1: how conflicts end

### Questions from the brief

**Lumping peace agreement and ceasefire.** This is defensible under the codebook (v.4 2024, section on the six outcomes):
both are agreements "signed and/or accepted" in the last active year or the first inactive year. The difference is
that a ceasefire "does not include any resolution of the incompatibility". So the combined share reads fine as "ended
with a signed agreement", but the two should also be shown apart, because they moved in opposite directions (neither
trend is significant on its own):

| outcome (vs all other endings), 1946-2023, logistic on end year | slope, log-odds per decade | 95 % CI | p |
|---|---|---|---|
| peace agreement only | -0.109 | -0.233 to 0.015 | 0.085 |
| ceasefire only | +0.090 | -0.034 to 0.214 | 0.154 |

**Low activity.** Keep it out of the agreement group: the codebook says there is "no information in this dataset"
about why the fighting dropped. It could be a military result, a change of tactics, or exploring negotiations. But it
has to be discussed, because it drives the main result. Low activity rose from 17.4 % of endings in the 1940s to
65.0 % in the 2010s (slope +0.321 per decade, 95 % CI 0.227 to 0.416). When fewer conflicts end with any clear
outcome, the share that ends in an agreement goes down even if more of the clear outcomes are agreements. That is
what happened:

| decade | agreement-or-ceasefire share of all endings | the same share among endings in an agreement, ceasefire or victory (outcomes 1-4) | n (outcomes 1-4) |
|---|---|---|---|
| 1940s | 21.7 % | 27.8 % | 18 |
| 1950s | 20.0 % | 29.6 % | 27 |
| 1960s | 24.5 % | 33.3 % | 36 |
| 1970s | 31.9 % | 38.5 % | 39 |
| 1980s | 16.4 % | 28.6 % | 35 |
| 1990s | 31.0 % | 61.0 % | 59 |
| 2000s | 35.5 % | 64.7 % | 34 |
| 2010s | 17.5 % | 66.7 % | 21 |
| 2020s (2020-2023) | 17.2 % | 55.6 % | 9 |

Among outcomes 1-4 the trend is clearly upward: +0.273 log-odds per decade, 95 % CI 0.149 to 0.397 (odds ratio
1.31 per decade, 1.16 to 1.49), p < 0.001. Both readings are true. The README only gives one of them.

**The two episodes with two ending rows.** The toy counts rows with `c_epterm` = 1, so it gets 507 endings. That is right.
But the README says "507 such endings (in 505 episodes)", and the JSON field `episodes_with_a_termination` = 505. In both
cases the two rows share a `c_epid` and `c_epno` = 1, but have **different `c_ep_startyear`**. The episode-year counter
(`c_ep_durcount`) restarts at 1, and there are inactive years between them. They are two separate episodes whose id
was reused in the file (a coding slip in the data, not two outcomes for one episode). Keyed on
(`c_epid`, `c_ep_startyear`) there are 507 episodes and 507 endings. The outcomes of the two pairs are (4, 5) and
(2, 3), so one of the 127 agreement endings is affected. Counting them as separate episodes, as the toy does, is
correct. Only the "505 episodes" wording is wrong.

**Censoring and the decade comparison.** Grouping by the year an episode ended means the complete decades (1940s to
2010s) are not censored: every episode that ended in, say, the 2010s is in the file. Only the 2020s bin is
incomplete (4 years, 29 endings). The 61 conflicts active in 2024 (33 of them started before 2020) can only add
endings to the 2020s or later. The README sentence "Wars that are long and still going are missing from the recent
decades by construction" overstates this. They are missing from the 2020s only. The comparison of complete decades
is fair as far as censoring goes. What changes across decades is the mix of endings (low activity, above) and the
number of conflicts, not the censoring.

**Does the data say "no steady rise"? Yes, for the share as defined.** Logistic regression of
agreement-or-ceasefire (1/0) on the end year, 507 endings:

| sample | n | slope, log-odds per decade | 95 % CI (Wald) | 95 % CI (clustered by conflict) | odds ratio per decade | p | average change, percentage points per decade |
|---|---|---|---|---|---|---|---|
| 1946-2023 (headline) | 507 | **-0.008** | **-0.102 to 0.086** | -0.107 to 0.090 | 0.992 (0.903-1.089) | 0.865 | -0.15 |
| 1946-2019 (complete decades) | 478 | +0.012 | -0.089 to 0.112 | -0.093 to 0.116 | 1.012 | 0.819 | +0.22 |
| 1975-2023 | 368 | -0.050 | -0.231 to 0.130 | -0.233 to 0.132 | 0.951 | 0.583 | -0.94 |
| 1989-2023 | 294 | -0.311 | -0.562 to -0.060 | -0.572 to -0.050 | 0.733 | 0.015 | -5.93 |

No linear trend over the whole period: the CI is tight around zero. The README's supporting argument is weaker than
its conclusion, though. "Every decade's interval contains 24.7-27.3 %, so the ups and downs are not clearly bigger
than chance" is not supported:

* a quadratic term improves the fit (likelihood-ratio p = 0.02): the share rises to the 1990s-2000s and then falls;
* the 1980s (16.4 %) and 2000s (35.5 %) differ (Fisher exact p = 0.023, unadjusted);
* a chi-square test of all nine decades gives p = 0.096: borderline, not "chance".

Overlapping intervals are not a test of equality. Since 1989 the share has fallen significantly.

**A better reading of the committee's sentence.** "More and more conflicts are being addressed through diplomacy,
treaties and legal mechanisms" is about conflicts being *addressed*, not about how episodes *end*. The UCDP Peace
Agreement Dataset can test that more directly. For each 5-year window, take the conflicts active in the window
(Termination file, 25 or more battle-related deaths in a year), and count how many had at least one agreement of any
type signed in that window:

| window | active conflicts | with any agreement signed | share |
|---|---|---|---|
| 1975-1979 | 58 | 6 | 10.3 % |
| 1980-1984 | 64 | 3 | 4.7 % |
| 1985-1989 | 61 | 7 | 11.5 % |
| 1990-1994 | 92 | 27 | 29.3 % |
| 1995-1999 | 73 | 23 | 31.5 % |
| 2000-2004 | 58 | 16 | 27.6 % |
| 2005-2009 | 54 | 12 | 22.2 % |
| 2010-2014 | 63 | 11 | 17.5 % |
| 2015-2019 | 88 | 13 | 14.8 % |
| 2020-2021 | 68 | 5 | 7.4 % (2 years only) |

At the level of conflict-years (1967 active conflict-years 1975-2021, 156 with an agreement signed in that year),
logistic on year with standard errors clustered by conflict: 1975-2021 slope +0.065 per decade (95 % CI -0.071 to
0.202). 1989-2021: -0.391 (-0.643 to -0.138). 1995-2021: -0.502 (-0.846 to -0.159). Read through this lens too, the
data show a jump around 1990 and a decline since the late 1990s, not "more and more". Two caveats: the Peace Agreement data
were first created for the UCDP Conflict Encyclopedia released in 2004 and updated each year since (codebook, "Data
Collection Methods"), so the low
1975-1989 counts may partly reflect coverage (not verified). And the window counts only agreements signed while the
conflict was active in that window (75 agreement conflict-years fall in years with no activity). This would make a
good third toy, or a paragraph in toy 1.

### Toy 1 fixes (FIX FIRST)

1. **Replace the "every decade's interval contains 24.7-27.3 %" argument** (README "careful answer" paragraph, INSIGHTS
   4, `answer.common_ci_range_pct`) with the trend test: slope -0.008 log-odds per decade, 95 % CI -0.102 to 0.086.
   Add that the share rose to the 1990s-2000s and fell after (quadratic p = 0.02). Do not say the ups and downs are
   chance.
2. **Show the low-activity effect.** Add the outcomes 1-4 share (27.8 % in the 1940s, 61.0-66.7 % in the 1990s-2010s,
   slope +0.273, CI 0.149 to 0.397) next to the headline. Without it the README suggests agreements lost ground. What
   actually happened is that more conflicts faded out with no clear outcome.
3. **Fix "507 such endings (in 505 episodes)"**: 507 episodes, two `c_epid` values reused for two episodes each
   (different start years). Rename or drop `episodes_with_a_termination` (505), or key it on
   (`c_epid`, `c_ep_startyear`), which needs that column in the derived CSV.
4. **Correct the censoring bullet**: complete decades are not censored when grouped by end year. Only the 2020s bin is
   partial, and the 61 conflicts active in 2024 can only add to it. Prefer 1946-2019 for any trend sentence.
5. **Reframe the heading "The committee's sentence, decade by decade"** as "One narrow reading of the committee's
   sentence". The data measure how episodes ended, not whether conflicts were "addressed" by diplomacy or law.
6. **Report peace agreement and ceasefire separately** in one sentence (peace -0.109, ceasefire +0.090 per decade,
   neither significant), since the grouping is "our choice".

Optional: add the Peace Agreement window table above as a second lens (it also shows no rise since the 1990s).

## 3. Toy 2: do agreements hold

### The toy's definition, re-checked

The clock starts at the signing year, and resumption is the first later year in which any listed conflict id has
25 or more battle-related deaths. 266 of the 374 agreements (71.1 %) were signed in a year of fighting. Of the 205
"resumed the next year", **193 also had fighting in the signing year**: for those the fighting did not resume, it
never stopped. The toy says this ("Resumed includes never stopped"), but the headline numbers (median 1 year, 31.5 %
at 5 years) still mostly measure it.

### Fairer alternative: the clock starts at the first quiet year

For each agreement, find the first calendar year after the signing year in which none of its listed conflict ids is
active (fewer than 25 battle-related deaths). Holding is then counted from there. Time is counted from the year before
that first quiet year, so "holding at 5 years" means 5 or more quiet years in a row, the same scale as the toy (where it means
no fighting in the 5 years after signing). Agreements whose conflict never dropped below the threshold by 2024 are
reported separately.

* **22 of 374 never got below the threshold by 2024** (Full 3, Partial 13, Peace process 6). 14 of the 22 were signed
  in 2015 or later.
* 352 reached a quiet year: 169 the very next year, 88 after 2-4 years, **95 only after 5 or more years**. In those
  late cases the quiet year is hard to credit to the agreement. A stricter version (quiet within 1-2 years) would be
  worth a sentence.

Kaplan-Meier, 95 % Greenwood log-log intervals (the toy's estimator):

| group | agreements | resumed | median years | holding at 5 years | holding at 10 years |
|---|---|---|---|---|---|
| all, toy definition | 374 | 281 | 1 (1-2) | 31.5 % (26.9-36.3) | 26.5 % (22.1-31.1) |
| **all, quiet-year clock** | **352** | **200** | **6 (5-10)** | **52.3 % (46.9-57.5)** | **43.8 % (38.4-49.2)** |
| Full, quiet-year clock | 74 | 36 | 21 (4-not reached) | 59.0 % (46.9-69.3) | 51.0 % (38.7-62.0) |
| Partial, quiet-year clock | 200 | 117 | 5 (4-9) | 49.4 % (42.1-56.3) | 41.1 % (33.9-48.1) |
| Peace process, quiet-year clock | 78 | 47 | 10 (2-21) | 53.4 % (41.7-63.8) | 43.9 % (32.2-54.9) |

Under the quiet-year clock the gap between types mostly closes. Log-rank tests across the three types (naive, ignoring
clustering): toy definition p = 0.038 (Full vs Peace process p = 0.010). Quiet-year clock p = 0.34 (Full vs Peace
process p = 0.184). So the toy's "Full agreements hold longest" mostly reflects how many process agreements were signed
while fighting was still going on (77.4 % of process agreements vs 66.2 % of full ones were signed in an active year).

### Dependence: one conflict, many agreements

Treating agreements whose conflict ids overlap as one cluster (connected components of ids) gives **72 clusters** for
374 agreements. The largest has 34 agreements, 24 are single agreements, and 77.5 % of all agreements sit in clusters
of 5 or more. The README notes this ("intervals are too narrow"). Here is how much:

| estimate | Greenwood 95 % CI (toy) | cluster bootstrap 95 % CI (2000 resamples of the 72 clusters, percentile) |
|---|---|---|
| all, toy definition, 5 years: 31.5 % | 26.9-36.3 | **21.0-44.6** |
| all, toy definition, 10 years: 26.5 % | 22.1-31.1 | **17.0-38.3** |
| all, toy definition, median 1 | 1-2 | 1-4 |
| Full, toy definition, 5 years: 40.3 % | 29.3-50.9 | 26.1-59.0 |
| Partial, toy definition, 5 years: 30.4 % | 24.4-36.7 | 18.3-43.9 |
| Peace process, toy definition, 5 years: 26.2 % | 17.4-35.9 | 13.5-45.1 |
| all, quiet-year clock, 5 years: 52.3 % | 46.9-57.5 | 37.4-68.1 |
| all, quiet-year clock, 10 years: 43.8 % | 38.4-49.2 | 29.2-60.8 |

The intervals roughly double in width. One agreement per cluster:

| one agreement per cluster | n | resumed | holding at 5 years | holding at 10 years |
|---|---|---|---|---|
| first agreement, toy definition | 72 | 48 | 38.9 % (27.7-49.9) | 35.8 % (24.9-46.9) |
| last agreement, toy definition | 72 | 32 | 62.5 % (50.2-72.5) | 57.8 % (45.4-68.3) |
| first agreement, quiet-year clock (2 never quiet) | 70 | 31 | 64.9 % (52.4-75.0) | 58.5 % (45.8-69.3) |
| last agreement, quiet-year clock (6 never quiet) | 66 | 18 | 83.1 % (71.5-90.2) | 73.9 % (60.9-83.2) |

"Last" looks good by construction: a conflict's last agreement is the one after which no further agreement was
needed. Do not narrate it as "last agreements work". "First" is the cleaner one-per-conflict summary.

### Cross-check against lifelines

`lifelines` 0.29.0 (`KaplanMeierFitter`, default exponential Greenwood "log(-log)" interval, `median_survival_times`)
in a throwaway venv, run on the same times. I checked all 8 curves (4 groups x toy and quiet-year definitions). The
largest absolute difference in S(t) at any event time was 6.1e-16, and in the interval bounds 6.7e-16. Medians and median
intervals are identical (lifelines' `inf` = the toy's `None`). The hand-written KM in `holds/km.py` is correct.

### Toy 2 fixes (FIX FIRST)

1. **Add the quiet-year clock as a second definition** (or make it the headline): 352 agreements, 52.3 % holding at 5
   years, 43.8 % at 10, median 6; 22 never got below the threshold, reported separately. Say in the README and INSIGHTS
   2 that 193 of the 205 next-year "resumptions" had fighting in the signing year too.
2. **Widen or replace the intervals for dependence**: 72 clusters, the largest 34 agreements. Give the cluster
   bootstrap interval (all, 5 years: 21.0-44.6 % rather than 26.9-36.3 %), or add the one-per-conflict (first
   agreement) row. Reword the bullet heading "Not dependent-free" (for example, "Not independent").
3. **Qualify "Full agreements held longest"** (README and INSIGHTS 4). It holds under the signing-year clock (log-rank
   p = 0.038, ignoring clustering) but not under the quiet-year clock (p = 0.34). It mostly reflects when agreements
   are signed.
4. **The claim "Full agreements tend to be signed when a conflict is already close to ending; process agreements often
   when fighting is still going on" has no number behind it** and is not in the JSON. Put the numbers in (66.2 % vs
   77.4 % signed in a year of fighting; next year active 44.2 % vs 64.3 %), or soften it to what they show.
5. **Credit**: the PA codebook asks users to "also cite this codebook" when appropriate: Högbladh, Stina (2022) UCDP
   Peace Agreement Dataset Codebook v 22.1. Add it to the README credit. The figure footer says only "Data: UCDP,
   CC BY 4.0", while toy 1's figure names its citation. Add "(Pettersson et al. 2019; Kreutz 2010)".
6. **Figure tail**: the curves are drawn to 30 years, but only 73 agreements (Full 21, Peace process 11) are still at
   risk at 21 years. Cut at 20 years or print the number at risk.

Optional: the PA file has its own `ended` field ("Did the peace agreement end, i.e. did the implementation fail?"; 134 coded yes,
2 no, 238 blank). It
is a different notion of holding and could be one sentence of context. The toy correctly does not mix it in.

## 4. Numbers, wording, names

* **Numbers.** Every table cell in both READMEs was compared field by field with the results JSON (not just
  token-present): all match. Every number in prose and in INSIGHTS.md is also in the JSON, and every INSIGHTS field
  path resolves. A limit of the repo's own test: it only checks that each README number appears somewhere in the JSON
  (for example "4" is satisfied by a version string). A field-level check like the one used here would be stronger.
  The numbers that need changing are the claims flagged above, not the arithmetic.
* **Wording.** Generally neutral and careful ("correlation, not cause", "a rough check, not a test"). Overreach is limited
  to the items in the fix lists: toy 1's chance claim, its "committee's sentence" heading and its censoring bullet.
  Toy 2's "Full agreements held longest", the unbacked claim about when agreement types are signed, and "Those that
  get past the first years mostly keep holding" (true of the curve, but with the dependence caveat).
* **Names.** Every location, territory and side name in the raw Termination file (978 names after splitting on
  commas), plus the places named in the brief and related terms, was matched case-insensitively, whole-word,
  against every committed file of both toys (code, README, INSIGHTS, JSON, derived CSVs; figures checked by eye). The
  only hits are the word "model" (module name `model.py`), which matches an actor name by coincidence. That is a false
  positive. No conflict names, no country pairs, nothing about the places named in the brief. This review folder was
  scanned the same way and is clean (the review scripts' variable names were changed to avoid a similar false positive). The derived CSVs are numeric
  only (`c_epid`/`conflict_id`, years, codes). The ids can be looked up on UCDP's site, but that is within the repo
  rule.

## 5. Licence and credit

* UCDP downloads page (checked 9 October 2026): "All datasets are free of charge and licensed under CC BY 4.0 ...
  provided you cite the relevant publications listed with each dataset." Both toys say CC BY 4.0 and link the page.
* Termination: the codebook (v.4 2024, Joakim Kreutz, 24 June 2025) asks for "Kreutz, Joakim, 2010. How and When Armed
  Conflicts End: Introducing the UCDP Conflict Termination Dataset. Journal of Peace Research 47(2): 243-250."
  Both toys quote it exactly. The version field 4.2024002 and "corresponds with ... v 25.1" match the file and
  codebook.
* Peace Agreement: the codebook (v 22.1) asks for "Pettersson, Therese; Stina Högbladh & Magnus Öberg (2019) Organized
  violence, 1989-2018 and peace agreements. Journal of Peace Research 56(4)." Toy 2 quotes it exactly. The
  "also cite this codebook" line is missing (fix 5). All 374 rows carry version 22.2. The page offers the 22.1 codebook
  and both the 22.1 and 22.2 xlsx, as the README says.
* Own code under the repo's MIT licence. The derived CSVs are labelled as CC BY 4.0 subsets with the same credit.

## 6. Narrator sentences I would allow

Numbers marked * are from this review and need to be added to the toy's JSON before use.

Toy 1:

1. "Between 1946 and 2023, UCDP records 507 endings of armed-conflict episodes; 127 of them, 25.0 per cent, ended in a
   peace agreement or a ceasefire agreement."
2. "The most common ending, 209 times, was low activity: the fighting fell below the UCDP threshold with no agreement
   and no victory."
3. "There is no steady rise in that share: it climbed to 35.5 per cent in the 2000s and fell back to 17.5 per cent in
   the 2010s."
4. "Among conflicts that ended with an agreement, a ceasefire or a victory, agreements and ceasefires went from under
   40 per cent of endings before 1990 to over 60 per cent in each decade since*, while more and more conflicts simply
   faded out."
5. "61 conflicts were still active in 2024, so the answer for the 2020s is not in yet."

Toy 2:

1. "UCDP lists 374 peace agreements signed from 1975 to 2021, many of them in the same few conflicts: they fall into
   72 groups*."
2. "In 205 cases the same conflict saw fighting the very next year; in 193* of them there had been fighting in the
   signing year too, so the fighting often never stopped."
3. "Of the 352* agreements followed by at least one quiet year, about half, 52 per cent*, were still quiet five years
   later."
4. "Full, partial and process agreements look different if you start counting at the signature, and much more alike
   if you start at the first quiet year*; the data cannot say whether any type of agreement causes peace."

I would **not** allow: "most peace agreements fail", "three in four agreements break down", "full agreements work
better", "diplomacy is not working", "law has not reduced war", anything about a 2020s trend, or "the ups and downs
are just chance".

## Files and how to reproduce

| file | in plain words |
|---|---|
| `check_ends.py` | toy 1 checks: duplicate episodes, logistic trend tests, decade tests, Peace Agreement lens |
| `check_hold.py` | toy 2 checks: quiet-year clock, clusters, one-per-conflict, cluster bootstrap, lifelines cross-check, log-rank |
| `review_numbers_ends.json`, `review_numbers_hold.json` | the scripts' output (numbers only), source of every number above |

Run after both toys' `fetch_data` (the scripts read the toys' `data/raw/` and derived CSVs; pass the folder holding
the two toy checkouts, here `~/repos` with worktrees `ends/` and `hold/`). Python 3.11, throwaway venv:
`pip install lifelines==0.29.0 statsmodels==0.14.4 pandas==2.2.3 scipy==1.13.1 numpy==1.26.4 openpyxl==3.1.5`, then
`python check_ends.py <root> > review_numbers_ends.json` and `python check_hold.py <root> > review_numbers_hold.json`.
The bootstrap uses a fixed seed (2026).
