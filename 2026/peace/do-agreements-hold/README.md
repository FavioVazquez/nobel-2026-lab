# Do agreements hold? (Peace 2026, toy 2)

> **Educational demos made to show an open-source tool. Not research.**
> Global totals only, from open data. No forecast, no score. The numbers below come from
> `results/do_agreements_hold.json`, and a test checks that every number in this README appears there.

The 2026 Nobel Peace Prize went to Navanethem "Navi" Pillay "for her efforts to promote peace and international law".
This folder asks what happens **after** a peace agreement is signed: once the fighting has dropped, how long until the
same conflict sees fighting again?

## What it does not show

* **Correlation, not cause.** Agreements are not randomly assigned. 66.2 % of full agreements and 77.4 % of process
  agreements were signed in a year of fighting (71.1 % of all), so the types start from different places. A
  difference between the curves says nothing about what a type of agreement *does*.
* **The strict clock counts fighting that never stopped as resumed.** Counted from the signing year, 205 agreements
  "resumed" the next calendar year, and in 193 of those the signing year had fighting too: it had not stopped. That is
  why the main clock waits for the first quiet year. The strict clock is kept as a second view.
* **Settled late.** Of the 352 agreements followed by a quiet year, 95 got there only 5 or more years after signing.
  That quiet is hard to credit to the agreement, so the main numbers are also given without them.
* **Not independent.** The 374 agreements fall into 72 groups of linked conflicts (agreements whose conflict ids
  overlap). The largest has 34 agreements, 24 groups have just one, and 77.5 % of agreements sit in groups of 5
  or more. The main intervals are a cluster bootstrap over these groups (2000 resamples, seed 2026). The Greenwood
  intervals, in square brackets, treat agreements as independent and are too narrow.
* **Not who fought.** "The same conflict" means the same UCDP conflict id. A dyadic agreement can hold between its
  signatories while other groups keep fighting in that conflict; this toy counts that as fighting.
* **Below the threshold.** A year under 25 battle-related deaths counts as quiet. Violence against civilians,
  repression or a broken promise without battle deaths does not appear.
* **Calendar years.** An agreement signed in December and fighting in January count as one year apart.
* **The tail.** The figure stops at 20 years; few agreements are still observed later.
* No conflict, country or party is named or singled out: the derived files keep only ids, years and codes.

## How to run

From `2026/peace/do-agreements-hold/`:

```bash
python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python -m holds.fetch_data   # optional: downloads both pinned UCDP files to data/raw/, checks sha256, rebuilds data/*.csv
python -m holds.run_all      # results/do_agreements_hold.json + figure (light and dark)
python -m pytest -q tests    # the raw-file checks are skipped until fetch_data has run
```

Own code, MIT licence. CPU only; runs in a few seconds. The Kaplan-Meier estimator, the log-rank test and the
cluster bootstrap are our own (`holds/km.py`), tested on hand examples; the Kaplan-Meier code matches `lifelines`.

## What it shows

**Main clock: what counts as holding.** A year is quiet when no conflict id the agreement lists has 25 or more
battle-related deaths. The agreement first has to bring the fighting down: the clock starts at the first quiet year
after signing and runs to the next year of fighting in the same conflict. It is counted from the year before the
first quiet year, so "holding at 5 years" means 5 or more quiet years in a row. Agreements still quiet when the data
stop in 2024 are censored.

The UCDP Peace Agreement Dataset lists 374 agreements signed from 1975 to 2021, of three types (codebook,
`pa_type`): **Full** (settle the whole incompatibility), **Partial** (settle a part) and **Peace process** (start a
process to settle it). 352 were followed by at least one quiet year: for 169 it was the year after signing, for 88
it took 2-4 years, for 95 5 or more. **22 never got below the threshold by 2024** (3 full, 13 partial, 6 process;
14 of them signed in 2015 or later). They are not in the curves.

Kaplan-Meier estimates; in round brackets the 95 % cluster-bootstrap interval, in square brackets Greenwood
(log-log):

| agreement type | agreements | resumed | still quiet in 2024 | median years | holding at 5 years | holding at 10 years |
|---|---|---|---|---|---|---|
| all | 352 | 200 | 152 | 6 (3-not reached) | 52.3 % (37.4-68.1) [46.9-57.5] | 43.8 % (29.2-60.8) [38.4-49.2] |
| Full | 74 | 36 | 38 | 21 (3-not reached) | 59.0 % (45.1-77.1) [46.9-69.3] | 51.0 % (33.9-72.6) [38.7-62.0] |
| Partial | 200 | 117 | 83 | 5 (3-not reached) | 49.4 % (32.2-68.2) [42.1-56.3] | 41.1 % (24.5-60.4) [33.9-48.1] |
| Peace process | 78 | 47 | 31 | 10 (2-not reached) | 53.4 % (33.5-76.7) [41.7-63.8] | 43.9 % (26.0-67.3) [32.2-54.9] |

**Without the settled-late agreements** (first quiet year within 4 years of signing):

| agreement type | agreements | resumed | still quiet in 2024 | median years | holding at 5 years | holding at 10 years |
|---|---|---|---|---|---|---|
| all | 257 | 137 | 120 | 10 (5-not reached) | 58.3 % (43.8-72.9) [52.0-64.1] | 49.6 % (34.1-66.0) [43.3-55.6] |
| Full | 53 | 23 | 30 | not reached (5-not reached) | 64.2 % (49.0-80.0) [49.7-75.4] | 58.2 % (41.5-76.6) [43.7-70.2] |
| Partial | 158 | 90 | 68 | 7 (4-not reached) | 53.7 % (36.7-70.7) [45.5-61.2] | 45.0 % (26.5-64.2) [37.0-52.7] |
| Peace process | 46 | 24 | 22 | 21 (6-not reached) | 67.3 % (50.8-81.0) [51.7-78.8] | 55.1 % (36.9-72.9) [39.3-68.4] |

**One agreement per linked group** (the first one signed), as a check on dependence: 70 groups (2 never got
below the threshold), 64.9 % holding at 5 years (52.4-75.0) and 58.5 % at 10 (45.8-69.3).

**Strict clock, second view** (from the signing year, so fighting that never stopped counts as resumed):

| agreement type | agreements | resumed | still holding in 2024 | median years | holding at 5 years | holding at 10 years |
|---|---|---|---|---|---|---|
| all | 374 | 281 | 93 | 1 (1-4) | 31.5 % (21.0-44.6) [26.9-36.3] | 26.5 % (17.0-38.3) [22.1-31.1] |
| Full | 77 | 50 | 27 | 2 (1-not reached) | 40.3 % (26.1-59.0) [29.3-50.9] | 36.1 % (22.9-55.4) [25.5-46.8] |
| Partial | 213 | 162 | 51 | 1 (1-5) | 30.4 % (18.3-43.9) [24.4-36.7] | 25.7 % (14.9-38.9) [20.0-31.7] |
| Peace process | 84 | 69 | 15 | 1 (1-2) | 26.2 % (13.5-45.1) [17.4-35.9] | 19.5 % (9.9-34.7) [11.7-28.8] |

First agreement per linked group on the strict clock: 72 agreements, 38.9 % at 5 years (27.7-49.9).

**Agreement types.** On the strict clock full agreements hold longest (log-rank p = 0.038 across the three types,
0.01 full against process). On the main clock the types differ much less (p = 0.34 and 0.184), and without the
settled-late agreements process agreements come out highest at 5 years (67.3 %, against 64.2 % full). These tests
treat agreements as independent, so they flatter any difference. The data do not support ranking agreement types.

Figure: `results/km_by_type_{light,dark}.png` (left: main clock by type; right: all agreements on the main clock,
without settled late, and on the strict clock).

## Files

| file | in plain words |
|---|---|
| `holds/constants.py` | the pinned URLs, sha256, versions, citations, the agreement types, the bootstrap settings |
| `holds/fetch_data.py` | downloads both raw files, checks sha256, writes the derived files |
| `holds/model.py` | per agreement: the main and strict clocks; the groups of linked conflicts |
| `holds/km.py` | Kaplan-Meier, Greenwood log-log intervals, median, log-rank test, cluster bootstrap |
| `holds/figures.py`, `holds/run_all.py` | the figure (light and dark) and the summary JSON |
| `data/agreements.csv` | derived: `paid`, `conflict_id`, `year`, `pa_type` for the 374 agreements |
| `data/active_years.csv` | derived: `conflict_id`, `year` for the 2752 active conflict-years |
| `INSIGHTS.md` | sentences a narrator could say, each traced to a JSON field |

## Data credit

UCDP Peace Agreement Dataset version 22.2 (codebook v 22.1, the newest on the page) and UCDP Conflict Termination
Dataset v.4 2024 (conflict level, corresponding to the UCDP/PRIO Armed Conflict Dataset v 25.1), from the Uppsala
Conflict Data Program, <https://ucdp.uu.se/downloads/>, licensed CC BY 4.0. Cite: Pettersson, Therese; Stina
Högbladh & Magnus Öberg (2019) Organized violence, 1989-2018 and peace agreements. Journal of Peace Research 56(4);
and Kreutz, Joakim, 2010. How and When Armed Conflicts End: Introducing the UCDP Conflict Termination Dataset.
Journal of Peace Research 47(2): 243-250. Codebook: Högbladh, Stina (2022) UCDP Peace Agreement Dataset Codebook
v 22.1. The files in `data/` are column subsets of those files (CC BY 4.0, same credit); the raw files are not
committed and `fetch_data` checks their sha256.
