"""Review checks for toy 1 (how-conflicts-end). Reads the raw UCDP files fetched by the toys. Prints numbers only."""
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "repos"
TERM = ROOT / "ends/2026/peace/how-conflicts-end/data/raw/UCDPConflictTerminationDataset_v4_2024_Conflict.csv"
PA = ROOT / "hold/2026/peace/do-agreements-hold/data/raw/ucdp-peace-agreements-222.xlsx"
out = {}

t = pd.read_csv(TERM, dtype=str)
t["year"] = t["year"].astype(int)
e = t[t["c_epterm"] == "1"].copy()
e["oc"] = e["c_outcome"].astype(int)
e["agr"] = e["oc"].isin([1, 2]).astype(int)
e["pa"] = (e["oc"] == 1).astype(int)
e["cf"] = (e["oc"] == 2).astype(int)
e["low"] = (e["oc"] == 5).astype(int)
e["dec10"] = (e["year"] - 1985) / 10.0
e["cid"] = e["conflict_id"]
out["endings"] = len(e)
key = e.groupby("c_epid").size()
dups = key[key > 1].index
out["epid_with_two_endings"] = len(dups)
out["dup_detail"] = [{"start_years_differ": e[e.c_epid == d]["c_ep_startyear"].nunique() == 2,
                      "outcomes": sorted(e[e.c_epid == d]["oc"].tolist())} for d in dups]
out["unique_episodes_by_epid_plus_startyear"] = e.groupby(["c_epid", "c_ep_startyear"]).ngroups


def logit(df, y, label):
    m = smf.glm(f"{y} ~ dec10", data=df, family=sm.families.Binomial())
    r = m.fit()
    rc = m.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(df["cid"])[0]})
    b, (lo, hi) = r.params["dec10"], r.conf_int().loc["dec10"]
    blo, bhi = rc.conf_int().loc["dec10"]
    # average marginal effect, percentage points per decade
    p = r.predict(df)
    ame = float((p * (1 - p)).mean() * b * 100)
    q = smf.glm(f"{y} ~ dec10 + I(dec10**2)", data=df, family=sm.families.Binomial()).fit()
    return {"label": label, "n": len(df), "events": int(df[y].sum()),
            "slope_log_odds_per_decade": round(b, 3), "ci95": [round(lo, 3), round(hi, 3)],
            "odds_ratio_per_decade": round(np.exp(b), 3), "or_ci95": [round(np.exp(lo), 3), round(np.exp(hi), 3)],
            "p": round(r.pvalues["dec10"], 3),
            "cluster_by_conflict_ci95": [round(blo, 3), round(bhi, 3)], "cluster_p": round(rc.pvalues["dec10"], 3),
            "ame_pp_per_decade": round(ame, 2),
            "quadratic_lr_p": round(stats.chi2.sf(2 * (q.llf - r.llf), 1), 3)}


out["trend"] = [
    logit(e, "agr", "agreement or ceasefire, all endings 1946-2023"),
    logit(e[e.year <= 2019], "agr", "agreement or ceasefire, 1946-2019 (complete decades)"),
    logit(e[e.year >= 1975], "agr", "agreement or ceasefire, 1975-2023"),
    logit(e[e.year >= 1989], "agr", "agreement or ceasefire, 1989-2023"),
    logit(e, "pa", "peace agreement only"),
    logit(e, "cf", "ceasefire only"),
    logit(e, "low", "low activity"),
    logit(e[e.oc <= 4], "agr", "agreement or ceasefire among endings that were not low activity or actor ceases"),
]
e["decade"] = e["year"] // 10 * 10
tab = pd.crosstab(e["decade"], e["agr"])
chi2, p, dof, _ = stats.chi2_contingency(tab)
out["decade_homogeneity_chi2"] = {"chi2": round(chi2, 2), "dof": int(dof), "p": round(p, 3)}
a, b = tab.loc[1980], tab.loc[2000]
out["fisher_1980s_vs_2000s"] = round(stats.fisher_exact([[a[1], a[0]], [b[1], b[0]]])[1], 3)
tab4 = pd.crosstab(e["decade"], e["oc"])
out["decade_by_6_outcomes_chi2_p"] = round(stats.chi2_contingency(tab4)[1], 4)
out["decade_shares_pct"] = {
    int(d): {"peace": round(100 * g.pa.mean(), 1), "ceasefire": round(100 * g.cf.mean(), 1),
             "low_activity": round(100 * g.low.mean(), 1),
             "agr_among_non_low_non_ceases": round(100 * g[g.oc <= 4].agr.mean(), 1), "n_non_low": int((g.oc <= 4).sum())}
    for d, g in e.groupby("decade")}
out["active_2024"] = int((t.year == 2024).sum())
out["active_2024_started_before_2020"] = int(((t.year == 2024) & (t.c_ep_startyear.astype(int) < 2020)).sum())

# Alternative reading: share of active conflicts with at least one agreement signed that year (Peace Agreement data)
pa = pd.read_excel(PA, sheet_name="Dataset", dtype=str)
pa["year"] = pa["year"].astype(int)
rows = []
for _, r in pa.iterrows():
    for c in str(r["conflict_id"]).replace(";", ",").split(","):
        if c.strip():
            rows.append((c.strip(), r["year"]))
pac = pd.DataFrame(rows, columns=["cid", "year"]).drop_duplicates()
act = t[["conflict_id", "year"]].rename(columns={"conflict_id": "cid"}).drop_duplicates()
act = act[(act.year >= 1975) & (act.year <= 2021)]
act = act.merge(pac.assign(any_pa=1), on=["cid", "year"], how="left").fillna({"any_pa": 0})
act["any_pa"] = act["any_pa"].astype(int)
act["dec10"] = (act["year"] - 2000) / 10.0
out["pa_conflict_years"] = {"active_conflict_years_1975_2021": len(act), "with_agreement": int(act.any_pa.sum()),
                            "agreement_conflict_years_not_active_that_year": int(len(pac[(pac.year <= 2021)]) - act.any_pa.sum())}
per5 = act.assign(p=(act.year - 1975) // 5 * 5 + 1975).groupby("p").agg(n=("any_pa", "size"), k=("any_pa", "sum"))
per5["pct"] = (100 * per5.k / per5.n).round(1)
out["pa_share_by_5y"] = {f"{int(p)}-{min(int(p)+4, 2021)}": [int(r.k), int(r.n), float(r.pct)] for p, r in per5.iterrows()}


def logit2(df, label):
    m = smf.glm("any_pa ~ dec10", data=df, family=sm.families.Binomial())
    r = m.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(df["cid"])[0]})
    b, (lo, hi) = r.params["dec10"], r.conf_int().loc["dec10"]
    return {"label": label, "n": len(df), "k": int(df.any_pa.sum()), "slope_per_decade": round(b, 3),
            "ci95_cluster": [round(lo, 3), round(hi, 3)], "p": round(r.pvalues["dec10"], 3)}


out["pa_trend"] = [logit2(act, "1975-2021"), logit2(act[act.year >= 1989], "1989-2021"),
                   logit2(act[act.year >= 1995], "1995-2021")]
# conflicts (not conflict-years) active in each 5-year window with any agreement in that window
cw = []
for p0 in range(1975, 2021, 5):
    p1 = min(p0 + 4, 2021)
    ids = set(act[(act.year >= p0) & (act.year <= p1)].cid)
    w = set(pac[(pac.year >= p0) & (pac.year <= p1)].cid)
    cw.append((f"{p0}-{p1}", len(ids & w), len(ids), round(100 * len(ids & w) / len(ids), 1)))
out["pa_conflicts_per_window"] = cw
print(json.dumps(out, indent=1, default=str))
