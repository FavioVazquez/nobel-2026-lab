# Insights (do agreements hold)

> **Educational demos made to show an open-source tool. Not research.** Each sentence names the field of
> `results/do_agreements_hold.json` it comes from; a test checks the numbers.

1. UCDP lists 374 peace agreements signed from 1975 to 2021, but they fall into 72 groups of linked conflicts, the largest with 34 agreements, so they are not 374 independent cases. (fields: `strict.groups.All.agreements`, `datasets.peace_agreements.signed_years`, `dependence.linked_groups`, `dependence.largest_group`)
2. After 352 of them the fighting dropped below 25 battle-related deaths in at least one year; in 22 it never did by 2024. (fields: `main.reached_a_quiet_year`, `definition.battle_deaths_threshold`, `main.never_below_threshold.All`, `datasets.termination.last_year`)
3. Of those 352, 52.3 per cent were still quiet 5 years later, with a 95 per cent interval of 37.4 to 68.1 that allows for linked conflicts; leaving out the 95 that only got quiet 5 or more years after signing, 58.3 per cent. (fields: `main.reached_a_quiet_year`, `main.groups.All.holding_at_5_years_pct`, `main.groups.All.holding_at_5_years_cluster_ci95_pct`, `ci_level_pct`, `main.years_from_signing_to_first_quiet_year`, `main.without_settled_late.All.holding_at_5_years_pct`, `horizons_years`)
4. Counted from the signing year instead, 205 agreements saw fighting the very next year, and in 193 of those the signing year had fighting too: it had not stopped. (fields: `strict.groups.All.resumed_the_next_year`, `strict.next_year_and_signing_year_both_active`)
5. Full, partial and process agreements look different when counted from the signature and much more alike from the first quiet year, 59.0, 49.4 and 53.4 per cent at 5 years; the data cannot say whether any type of agreement causes peace. (fields: `main.groups.Full.holding_at_5_years_pct`, `main.groups.Partial.holding_at_5_years_pct`, `main.groups.Peace process.holding_at_5_years_pct`, `horizons_years`)
