# How conflicts end (Peace 2026, toy 1)

> **Educational demos made to show an open-source tool. Not research.**
> Global totals only, from one open dataset. No forecast, no score. The numbers below come from
> `results/how_conflicts_end.json`, and a test checks that every number in this README appears there.

The 2026 Nobel Peace Prize went to Navanethem "Navi" Pillay "for her efforts to promote peace and international law".
This folder asks one narrow question of open data: of the armed-conflict episodes that **ended**, did a growing share
end in a **peace agreement or a ceasefire agreement**?

Own code, MIT licence. CPU only; runs in a few seconds. Python with NumPy and Matplotlib (no pandas).

## How to run

From `2026/peace/how-conflicts-end/`:

```bash
python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python -m ends.fetch_data   # optional: downloads the pinned UCDP file to data/raw/, checks its sha256, rebuilds data/conflict_years.csv
python -m ends.run_all      # results/how_conflicts_end.json + figures (light and dark)
python -m pytest -q tests   # the raw-file checks are skipped until fetch_data has run
```

## What it shows

The unit is the codebook's: a conflict **episode** ends in its last active year (`c_epterm` = 1), and `c_outcome`
says how. Between 1946 and 2023 the dataset records 507 such endings, one per episode. (Two episode ids, `c_epid`,
are each used for two separate episodes with different start years, so there are only 505 distinct ids.) Over the
whole period:

| how the episode ended (codebook name) | episodes |
|---|---|
| Peace agreement | 60 |
| Ceasefire agreement | 67 |
| Victory for Side A (government side) | 107 |
| Victory for Side B (non-state side) | 44 |
| Low activity | 209 |
| Actor ceases to exist | 20 |

So 127 of 507 endings (25.0 %) were a peace agreement or a ceasefire agreement. The most common ending is
**low activity**: the fighting fell below the UCDP threshold without an agreement or a victory.

**Share of endings by decade** (share of the episodes that ended in that decade; 95 % Wilson interval):

| decade | years | episodes ended | peace agreement or ceasefire | share | 95 % interval |
|---|---|---|---|---|---|
| 1940s | 1946-1949 | 23 | 5 | 21.7 % | 9.7-41.9 % |
| 1950s | 1950-1959 | 40 | 8 | 20.0 % | 10.5-34.8 % |
| 1960s | 1960-1969 | 49 | 12 | 24.5 % | 14.6-38.1 % |
| 1970s | 1970-1979 | 47 | 15 | 31.9 % | 20.4-46.2 % |
| 1980s | 1980-1989 | 61 | 10 | 16.4 % | 9.2-27.6 % |
| 1990s | 1990-1999 | 116 | 36 | 31.0 % | 23.3-39.9 % |
| 2000s | 2000-2009 | 62 | 22 | 35.5 % | 24.7-47.9 % |
| 2010s | 2010-2019 | 80 | 14 | 17.5 % | 10.7-27.3 % |
| 2020s | 2020-2023 | 29 | 5 | 17.2 % | 7.6-34.5 % |

**First view: across all endings, no steady rise.** The share went from 21.7 % in the late 1940s to a high of
35.5 % in the 2000s, then back to 17.5 % in the 2010s and 17.2 % so far in the 2020s. A simple trend test (logistic
regression of agreement-or-ceasefire on the year the episode ended) gives a slope of -0.008 log-odds per decade, 95 %
interval -0.102 to 0.086 (odds ratio 0.992 per decade, p = 0.865): no steady rise and no steady fall. Over
the complete decades only (1946-2019) the slope is 0.012 (-0.089 to 0.112).

The ups and downs are not just noise, though. A curve that rises and then falls fits better than a straight line
(squared term p = 0.02), and since 1989 the share has fallen (slope -0.311, 95 % interval -0.562 to -0.06,
p = 0.015). Taken apart, peace agreements (-0.109, -0.233 to 0.015, p = 0.085) and ceasefires
(0.09, -0.034 to 0.214, p = 0.154) show no clear trend either. The 1990s stand out for the **number** of
endings (116), not only for the share.

**Second view: more conflicts fade out, and among clear outcomes agreements gained.** Low activity (the fighting
falls below the threshold with no agreement and no victory) was 17.4 % of endings in the 1940s, 65.0 % in the
2010s and 65.5 % so far in the 2020s (trend 0.321 log-odds per decade, 0.227 to 0.416, p < 0.001). When fewer
conflicts end with any clear outcome, the agreement share of *all* endings can stay flat even while agreements take
a growing share of the clear ones. That is what happened. Among the 278 endings with a clear outcome (a peace
agreement, a ceasefire agreement or a victory for either side):

| decade | years | clear-outcome endings | peace agreement or ceasefire | share | 95 % interval |
|---|---|---|---|---|---|
| 1940s | 1946-1949 | 18 | 5 | 27.8 % | 12.5-50.9 % |
| 1950s | 1950-1959 | 27 | 8 | 29.6 % | 15.9-48.5 % |
| 1960s | 1960-1969 | 36 | 12 | 33.3 % | 20.2-49.7 % |
| 1970s | 1970-1979 | 39 | 15 | 38.5 % | 24.9-54.1 % |
| 1980s | 1980-1989 | 35 | 10 | 28.6 % | 16.3-45.1 % |
| 1990s | 1990-1999 | 59 | 36 | 61 % | 48.3-72.4 % |
| 2000s | 2000-2009 | 34 | 22 | 64.7 % | 47.9-78.5 % |
| 2010s | 2010-2019 | 21 | 14 | 66.7 % | 45.4-82.8 % |
| 2020s | 2020-2023 | 9 | 5 | 55.6 % | 26.7-81.1 % |

Here the trend is upward: 0.273 log-odds per decade (0.149 to 0.397, odds ratio 1.314, p < 0.001), with no sign of a
curve (squared term p = 0.956). In every complete decade since 1990 an agreement or ceasefire was the most
common clear outcome (at least 61.0 %), against at most 38.5 % in each decade before 1990. The counts are
small in the 2010s and 2020s. Both views are true of the same data; neither says why.

Figures: `results/ends_by_decade_{light,dark}.png` (all six outcomes, stacked shares) and
`results/agreement_share_{light,dark}.png` (the two views: shares of all endings, and the share among clear
outcomes, each with its trend).

## What it does not show

* **Censoring, for the 2020s only.** Grouped by the year an episode ended, every decade up to the 2010s is
  complete: any episode that ended then is in the file. 61 conflicts were still active in 2024 and have no outcome
  yet; they can only add endings to the 2020s, which hold only 4 years (2020-2023), or later. The 2020s numbers can
  still change a lot as they end; the earlier ones cannot.
* **Restarts.** "Low activity" (and sometimes an agreement) can be followed by a new episode of the same conflict.
  This toy counts endings, not lasting peace; toy 2 (`do-agreements-hold`) looks at what follows an agreement.
* **Size and cost.** Every episode counts once, whatever its length or death toll.
* **Cause.** It does not say that law, mediation or any institution caused an ending, and it says nothing about
  conflicts that never reached the UCDP threshold, or about diplomacy that prevented a war.
* **Coding choices.** The outcome is coded from the last active year and the first inactive year; an agreement signed
  outside that window does not count (codebook, section 2). Ceasefire and peace agreement are grouped here by our
  choice.
* No conflict, country or party is named or singled out: the derived file keeps only ids, years and codes.

## Files

| file | in plain words |
|---|---|
| `ends/constants.py` | the pinned URL, sha256, version, citation and the codebook's outcome names |
| `ends/fetch_data.py` | downloads the raw file, checks its sha256, writes the derived file |
| `ends/model.py` | endings by decade, the Wilson interval, a small logistic trend test (our own, tested on a hand example) |
| `ends/figures.py`, `ends/run_all.py` | the figures (light and dark) and the summary JSON |
| `data/conflict_years.csv` | derived: `c_epid`, `year`, `c_epterm`, `c_outcome` for the 2752 conflict-years (numbers only) |
| `results/how_conflicts_end.json` | every number in this README |
| `INSIGHTS.md` | sentences a narrator could say, each traced to a JSON field |

## Data credit

UCDP Conflict Termination Dataset, version v.4 2024 (file version field 4.2024002), conflict level, from the Uppsala
Conflict Data Program, <https://ucdp.uu.se/downloads/>, licensed CC BY 4.0. It corresponds to the UCDP/PRIO Armed
Conflict Dataset v 25.1. Cite: Kreutz, Joakim, 2010. How and When Armed Conflicts End: Introducing the UCDP Conflict
Termination Dataset. Journal of Peace Research 47(2): 243-250. `data/conflict_years.csv` is a column subset of that
file (CC BY 4.0, same credit); the raw file is not committed and `fetch_data` checks its sha256.
