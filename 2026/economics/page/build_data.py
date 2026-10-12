"""Build page/data.js from the two Economics toys (educational demos made to show an open-source tool; not research).

Reads, relative to this folder (where the toys live after the merge):
  ../can-you-predict-spending/results  spending.json      (and ../can-you-predict-spending/INSIGHTS.md)
  ../set-the-rate/results              set_the_rate.json  (and ../set-the-rate/INSIGHTS.md)
and writes data.js, a plain script that sets window.NOBEL_ECON_DATA, so index.html works from file:// with no server
and no network. Every number the page shows comes from these files; nothing is typed into index.html. The narrator
sentences are the toys' INSIGHTS.md lines, unchanged. Python 3 standard library only.

    python3 build_data.py --from SPEND_RESULTS RATE_RESULTS   # the toys' results folders anywhere (e.g. worktrees)
    python3 build_data.py                                    # from 2026/economics/page/ after the merge
    python3 build_data.py --fixtures                         # the copies in tests/fixtures (status "fixture")
    python3 build_data.py --out /tmp/data.js                 # write somewhere else

The toys were still being revised while this page was built, so the field names of their `guess` blocks are read from
the JSON when it is built, not typed in: the headline is the `answer*` number of each guess, its interval the `ci*`
pair that goes with it, and every other number of the block is shown small with a label made from its key. A field the
page expects but cannot find is printed as a WARNING and that piece of the page is left out, never filled in.

It prints the status of each input file ("final", "preliminary", "fixture" or "missing"). A results file with no
"status" field counts as final. The page shows a visible "preliminary" box unless every input is "final". If the
spending toy has no data licence (synthetic only), the page says so and labels its numbers "simulated".
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "tests" / "fixtures"
TOYS = ("can-you-predict-spending", "set-the-rate")
FILES = ("spending.json", "set_the_rate.json")
DEFAULTS = tuple(HERE.parent / t / "results" for t in TOYS)
TAG = "Educational demos made to show an open-source tool. Not research."
CURVE_LABEL = "textbook model, illustrative calibration"
GITHUB = "https://github.com/FavioVazquez/nobel-2026-lab/tree/main/2026/economics/"
SHOWTIME = "https://github.com/FavioVazquez/showtime"
STATUS_ORDER = ["missing", "fixture", "preliminary", "final"]

# ---- fixed facts (The Royal Swedish Academy of Sciences, press release) -----------------------------------------
PR = "https://www.nobelprize.org/prizes/economic-sciences/2026/press-release/"
PRIZE = {
    "year": 2026,
    "name": "Sveriges Riksbank Prize in Economic Sciences in Memory of Alfred Nobel",
    "laureates": "Robert E. Hall and Michael Woodford",
    "citation": "for microeconomic foundations of macroeconomic stabilisation",
    "by": "The Royal Swedish Academy of Sciences, press release",
    "url": PR,
}
FONTS = {"sans": "Inter", "serif": "Fraunces", "mono": "JetBrains Mono", "licence": "SIL Open Font License 1.1",
         "file": "fonts/OFL.txt"}
SCALE_TICKS = [0, 25, 50, 75, 100]
RANGE_TICKS = [-50, 0, 50, 100, 150, 200]
WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)
    print("  WARNING: " + msg)


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def load_dir(folder, name):
    """The toy's results file; if it was renamed, the only .json in the folder."""
    p = Path(folder) / name
    if not p.exists():
        js = sorted(Path(folder).glob("*.json")) if Path(folder).is_dir() else []
        p = js[0] if len(js) == 1 else p
    return load(p)


def status_of(obj):
    if obj is None:
        return "missing"
    if "status" not in obj:
        return "final"
    s = str(obj["status"]).lower()
    if s.startswith("final"):
        return "final"
    return s if s in ("preliminary", "fixture") else "preliminary"


def insights(results_dir):
    """The toy's INSIGHTS.md lines -> [{"text", "fields"}]: the sentence as written, and the JSON fields it names."""
    p = Path(results_dir).parent / "INSIGHTS.md"
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\d+\.\s+(.*?)\s*\(fields?:\s*(.*)\)\s*$", line)
        if m:
            out.append({"text": m.group(1), "fields": re.findall(r"`([^`]+)`", m.group(2))})
    return out


def by_role(ins, roles):
    """Give each insight to the first role (in priority order) whose field prefixes it names."""
    out = {r: [] for r, _ in roles}
    for i in ins:
        for r, prefixes in roles:
            if any(f.startswith(p) or ("." + p) in f for f in i["fields"] for p in prefixes):
                out[r].append(i)
                break
    return out


# ---- generic readers for the guess blocks -----------------------------------------------------------------------
def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def pair(v):
    return isinstance(v, list) and len(v) == 2 and all(num(x) for x in v)


def first_key(d, *patterns, test=None):
    for pat in patterns:
        for k, v in (d or {}).items():
            if re.search(pat, k) and (test is None or test(v)):
                return k
    return None


def _base(k):
    k = re.sub(r"_?ci\d*", "", k)
    k = re.sub(r"_?pct$", "", k)
    return re.sub(r"^answer_?", "", k)


def ci_for(block, key):
    """The interval that goes with a number: answer_pct <-> ci95_pct, x_pct <-> x_ci95_pct."""
    b = _base(key)
    for k, v in block.items():
        if pair(v) and re.search(r"(^|_)ci\d*(_|$)", k) and _base(k) == b:
            return k, v
    return None, None


def unwrap(v, *keys):
    """A number, or the first numeric entry of a dict under one of keys (a renamed field may become a small block)."""
    if num(v):
        return v
    if isinstance(v, dict):
        for k in keys + tuple(v):
            if num(v.get(k)):
                return v[k]
    return None


def label_for(key, sample):
    """A plain label from a JSON key, e.g. pre_2020_pct -> 'to 2019Q4'; unknown words are kept as they are."""
    q = sample.get("regression_quarters") or ["", ""]
    pre = sample.get("pre_2020_end") or "2019Q4"
    k = re.sub(r"^(secondary|ours|published)_", "", re.sub(r"_?pct$", "", key).lower())
    rules = [
        (r"out_of_sample", "out of sample"), (r"in_sample", "in sample"),
        (r"r2_adj|adjusted", "adjusted for the number of predictors"),
        (r"lags_(\d+)_(\d+)", r"lags \1-\2"), (r"with_(\d{4})_(\d{4})", r"with \1-\2"),
        (r"without_(\d{4})_(\d{4})", r"without \1-\2"),
        (r"pre_2020", "to " + pre), (r"full_sample|full", "to " + str(q[-1])),
        (r"first_stage_f", "first-stage F"), (r"hall_benchmark", "Hall's benchmark"),
    ]
    for pat, rep in rules:
        k = re.sub(pat, lambda m: "|" + m.expand(rep) + "|", k)
    parts = [p.strip("_").replace("_", " ") for p in k.split("|")]
    return ", ".join(p for p in parts if p)


PARTICLES = ("de", "del", "della", "van", "von", "la", "le", "da")


def refs(citations):
    """Short names keyed without the year, from the toys' citation keys: campbell_mankiw_1989 -> 'Campbell and Mankiw
    (1989)' under 'campbell_mankiw' (the page's script may not contain any digit, so it looks names up this way)."""
    out = {}
    for key in citations or {}:
        toks = key.split("_")
        if not toks[-1].isdigit():
            continue
        names, cur = [], []
        for t in toks[:-1]:
            cur.append(t.capitalize())
            if t not in PARTICLES:
                names.append(" ".join(cur))
                cur = []
        who = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
        out.setdefault("_".join(toks[:-1]), f"{who} ({toks[-1]})")
    return out


def which(text, options):
    """The page's button value whose pattern the toy's answer text matches first (None if none does)."""
    t = (text or "").lower()
    return next((v for v, pat in options if re.search(pat, t)), None)


def years(text):
    """First and last year named in a sample line: '1953:1 to 1986:4' -> [1953, 1986]."""
    ys = [int(y) for y in re.findall(r"\b(?:18|19|20)\d\d\b", text or "")]
    return [ys[0], ys[-1]] if ys else None


def fragment(quote, pattern):
    """A short piece of a quote (under 15 words), exactly as written, or None if the quote does not contain it."""
    m = re.search(pattern, quote or "")
    return m.group(0) if m and len(m.group(0).split()) < 15 else None


def p_for(block, key):
    """The p-value that goes with a number: answer_pct <-> p, x_pct <-> x_p."""
    b = _base(key)
    return next((v for k, v in block.items() if num(v) and re.fullmatch(r"(.*_)?p", k) and re.sub(r"_?p$", "", k) == b), None)


def flat(d, pre=""):
    """A nested guess block as one level: {"ours": {"ci95_pct": ..}} -> {"ours_ci95_pct": ..}."""
    out = {}
    for k, v in (d or {}).items():
        if isinstance(v, dict):
            out.update(flat(v, pre + k + "_"))
        else:
            out[pre + k] = v
    return out


def guess_numbers(g, sample, skip=()):
    """Every per-cent number of a guess block other than those in skip, with a label, and its interval, p-value and
    quarters if the block has them (a number named x_pct goes with x_ci95_pct, x_p and x_quarters)."""
    items, used = [], set(skip)
    for k, v in g.items():
        if k in used or not num(v) or not k.endswith("pct"):
            continue
        ck, cv = ci_for(g, k)
        used |= {k, ck}
        q = g.get(_base(k) + "_quarters")
        label = "-".join([q[0], q[-1]]) if isinstance(q, list) and q and re.search(r"full", k) and not re.search(r"lags|out_of", k) \
            else label_for(k, sample)
        items.append({"key": k, "label": label, "value": v, "ci": cv, "p": p_for(g, k), "quarters": q})
    return items


# ---- toy B: can you predict spending? ---------------------------------------------------------------------------
def licence_lines(lic):
    """[{"text", "url"}] from the toy's licence block: each quoted *_line with its *_url."""
    out = []
    if isinstance(lic, str):
        return [{"text": lic, "url": None}]
    for k, v in (lic or {}).items():
        if isinstance(v, str) and (k.endswith("_line") or k in ("line", "statement", "quote")):
            pre = k[: -len("_line")] if k.endswith("_line") else ""
            url = lic.get(pre + "_url") if pre else lic.get("url")
            out.append({"text": v, "url": url})
    if not out and isinstance(lic, dict):  # another shape: every plain sentence, with the block's first URL
        urls = [v for v in lic.values() if isinstance(v, str) and v.startswith("http")]
        out = [{"text": v, "url": urls[0] if urls else None} for v in lic.values()
               if isinstance(v, str) and not v.startswith("http") and len(v) > 40]
    return out


def spend_block(folder):
    d = load_dir(folder, FILES[0])
    st = status_of(d)
    if d is None:
        return None, st
    sample = d.get("sample") or {}
    data = d.get("data") or {}
    lic_k = first_key(data, r"licen[cs]e", r"public_domain", r"copyright", r"terms")
    lic = data.get(lic_k) if lic_k else None
    synthetic = bool(d.get("synthetic")) or not lic
    if synthetic:
        warn("spending.json has no data licence (or says synthetic): part one is labelled simulated")
    G = d.get("guess") or {}
    ga, gb = G.get("a") or {}, G.get("b") or {}
    if not ga or not gb:
        warn("spending.json has no guess.a / guess.b block")
    # guess a: the headline answer, its interval, Hall's benchmark, then every other number small
    ak = first_key(ga, r"^answer_pct$", r"^answer.*pct$", r"^answer", test=num)
    ack, aci = ci_for(ga, ak) if ak else (None, None)
    bk = first_key(ga, r"benchmark", test=num)
    if ak is None:
        warn("guess.a has no answer number")
    elif aci is None:
        warn(f"guess.a: no interval found for {ak} (the page shows the answer without one)")
    a = {"question": ga.get("question"), "reads_as": ga.get("reads_as"), "answer": ga.get(ak) if ak else None,
         "answer_key": ak, "ci": aci, "p": p_for(ga, ak) if ak else None, "quarters": ga.get("quarters"),
         "benchmark": ga.get(bk) if bk else None,
         "notes": {k: v for k, v in ga.items() if isinstance(v, str) and k not in ("question", "reads_as", "answer")},
         "more": guess_numbers(ga, sample, skip=(ak, ack, bk))}
    # guess b: published benchmarks first, then our estimate only as a range with the weak-instrument flag
    lam = d.get("lambda") or {}
    pub = lam.get("published") or {}
    comm = d.get("committee") or {}
    gf = flat(gb)
    is_str = lambda v: isinstance(v, str)  # noqa: E731

    def get(*pats, test=None):
        k = first_key(gf, *pats, test=test)
        return gf.get(k) if k else None

    weak_flag = get(r"^ours_weak", r"^weak", test=lambda v: isinstance(v, bool))
    if weak_flag is None:  # the toy states the opposite: effective_F_above_10
        above = get(r"^ours_effective_F_above_10$", r"^effective_F_above_10$", test=lambda v: isinstance(v, bool))
        if above is not None:
            weak_flag = not above
    cm_about = get(r"campbell.*mankiw.*about", r"published.*about", r"(^|_)cm.*pct", test=num)
    tr_k = first_key(gf, r"table.*range", r"table.*iv", r"(table|published).*range", test=pair)
    table_range = gf.get(tr_k) if tr_k else None
    if table_range and "pct" not in tr_k and max(abs(x) for x in table_range) <= 2:  # a share, not per cent
        table_range = [round(100 * x, 1) for x in table_range]
    rows = [{"row": r, "instruments": v.get("instruments"), "lambda_pct": round(100 * v["lambda"], 1)}
            for r, v in (pub.get("rows") or {}).items() if num(v.get("lambda")) and "OLS" not in str(v.get("instruments"))]
    if table_range is None and rows:
        table_range = [min(r["lambda_pct"] for r in rows), max(r["lambda_pct"] for r in rows)]
    ours_k = first_key(gf, r"^ours_ci\d*_pct$", r"^(answer_|our_|estimate_)?ci\d*_pct$", r"^(answer|our|estimate).*ci", test=pair)
    with_k = first_key(gf, r"with_20\d\d.*ci", r"full.*ci", test=pair)
    ar = get(r"anderson_rubin_set", r"(^|_)ar_set", test=lambda v: isinstance(v, list))
    ar = [x for x in (ar if ar and isinstance(ar[0], list) else [ar] if ar else []) if pair(x)]
    if ours_k is None:
        warn("guess.b has no interval for our estimate")
    if cm_about is None:
        warn("guess.b has no published Campbell-Mankiw number")
    cm_quote = get(r"campbell.*quote", r"^published$", r"published.*quote", test=is_str) or pub.get("conclusion")
    cm_sample = get(r"campbell.*sample", test=is_str) or pub.get("sample")
    hm_quote = get(r"hall_mishkin.*quote", r"hall_mishkin$", r"committee", test=is_str) or comm.get("hall_mishkin")
    hm_sample = get(r"hall_mishkin.*sample", test=is_str)
    # the reveal shows two short lines; the quotes in full go under "More on this answer"
    cm_short = fragment(cm_quote, rf"about {cm_about} ?per ?cent") if cm_about is not None else None
    hm_short = fragment(hm_quote, r"hand.to.mouth")
    if cm_quote and not cm_short:
        warn("guess.b: the Campbell-Mankiw quote has no short 'about N percent' piece (the short line goes unquoted)")
    b = {"question": gb.get("question"), "reads_as": gb.get("reads_as"),
         "cm": {"about_pct": cm_about, "quote": cm_quote, "short": cm_short,
                "page": get(r"campbell_mankiw_page$", r"^published_page$", test=num) or pub.get("conclusion_page"),
                "sample": cm_sample, "years": years(cm_sample),
                "table_page": get(r"table1?_page", test=num) or pub.get("page"), "rows": rows, "range_pct": table_range,
                "url": pub.get("url")},
         "hm": {"pct": get(r"hall_mishkin.*pct", r"committee.*pct", test=num), "quote": hm_quote, "short": hm_short,
                "by": get(r"hall_mishkin.*source", test=is_str) or comm.get("source"),
                "sample": hm_sample, "years": years(hm_sample)},
         "ours": {"ci": gf.get(ours_k) if ours_k else None, "quarters": gf.get("ours_quarters") or gb.get("quarters"),
                  "headline": get(r"ours_headline", r"^headline", test=is_str),
                  "instruments": get(r"ours_instruments", test=is_str),
                  "F": get(r"^ours_effective_F$", r"^effective_F$", r"^ours_first_stage_F$", r"^first_stage_F$", r"^(?!.*with_).*first_stage", test=num),
                  "weak": weak_flag,
                  "weak_rule": get(r"weak_F_rule", test=num) or lam.get("weak_F_rule"),
                  "ar": ar, "ar_contains": get(r"anderson_rubin_contains", test=lambda v: isinstance(v, bool)),
                  "with_ci": gf.get(with_k) if with_k else None,
                  "with_label": label_for(re.sub(r"_?ci\d*", "", with_k), sample) if with_k else None,
                  "why": get(r"^why", r"_why", test=is_str) or ""},
         "ci_level": sample.get("ci_level_pct"), "share_max_pct": 100}
    # the simulated control: the test can find a share we put in
    ctl = d.get("control") or {}
    cases = ctl.get("cases") or {}
    strong = next((c for c in cases.values() if num(c.get("lambda_true")) and c["lambda_true"] > 0 and (c.get("median_first_stage_F") or 0) >= 10), None)
    weak0 = next((c for c in cases.values() if c.get("lambda_true") == 0 and (c.get("median_first_stage_F") or 99) < 10), None)
    pct = lambda x: None if x is None else round(100 * x, 1)
    control = None
    if strong:
        control = {"true_pct": pct(strong["lambda_true"]), "median_pct": pct(strong.get("median_lambda")),
                   "coverage_pct": strong.get("ci95_coverage_pct"), "reps": strong.get("reps") or (ctl.get("params") or {}).get("reps"),
                   "hall_reject_pct": strong.get("hall_reject_pct"),
                   "weak_zero_median_pct": pct(weak0.get("median_lambda")) if weak0 else None}
    else:
        warn("spending.json has no simulated control case with a known share")
    ins = insights(folder)
    roles = by_role(ins, [("control", ["control."]), ("pandemic", ["pandemic."]), ("b", ["guess.b", "lambda."]),
                          ("a", ["guess.a", "hall."])])
    vin = data.get("vintage") or data.get("release") or data.get("bea_release")
    if isinstance(vin, dict):
        vin = ("release of " + vin["release_date"]) if vin.get("release_date") else None
    credit = {"source": data.get("source"), "licence": licence_lines(lic), "downloaded": data.get("downloaded"), "vintage": vin,
              "series": [{"id": k, "title": v.get("title"), "table": v.get("table"),
                          "page": v.get("page") or (v.get("url") if str(v.get("url", "")).startswith("http") else None)}
                         for k, v in (data.get("series") or {}).items() if isinstance(v, dict)],
              "files": [{"name": k, "url": v.get("url")} for k, v in (data.get("bulk") or {}).items()
                        if isinstance(v, dict) and str(v.get("url", "")).startswith("http")]}
    return {"synthetic": synthetic, "sample": {"quarters": sample.get("regression_quarters"), "ci_level": sample.get("ci_level_pct")},
            "a": a, "b": b, "control": control, "credit": credit, "citations": d.get("citations") or {},
            "refs": refs(d.get("citations")), "insights": ins, "roles": roles}, st


# ---- toy A: set the rate ----------------------------------------------------------------------------------------
def short_unit(u):
    u = (u or "").lower()
    if "point" in u:
        return "points a year" if "annual" in u or "year" in u else "points"
    return "%" if "per cent" in u or "percent" in u else ""


def paths_of(blk, keys):
    p = (blk or {}).get("paths") or {}
    return {k: p[k] for k in keys if isinstance(p.get(k), list)}


def rate_block(folder):
    d = load_dir(folder, FILES[1])
    st = status_of(d)
    if d is None:
        return None, st
    units = d.get("units") or {}
    cal = d.get("calibration") or {}
    G = d.get("guess") or {}
    keys = [k for k in units if k != "time"]
    vars_ = [{"key": k, "label": k.replace("_", " ").capitalize(), "unit": units[k], "short": short_unit(units[k])} for k in keys]

    def sub_by(blk, pred):
        return next((v for v in (blk or {}).values() if isinstance(v, dict) and pred(v)), None)

    def run(v):
        return None if v is None else {"phi_pi": v.get("phi_pi"), "impact": v.get("impact"), "paths": paths_of(v, keys)}

    cp = d.get(first_key(d, r"cost_push") or "") or {}
    base = sub_by(cp, lambda v: "paths" in v and v.get("phi_pi") == cal.get("phi_pi")) or sub_by(cp, lambda v: "paths" in v)
    strong = sub_by(cp, lambda v: "paths" in v and v is not base)
    H = cal.get("horizon_quarters") or max((len(v) for v in ((base or {}).get("paths") or {}).values()), default=1) - 1
    ticks = list(range(0, H + 1, 4))
    ga, gb, gc = G.get("a") or {}, G.get("b") or {}, G.get("c") or {}
    tp = d.get(first_key(d, r"taylor") or "") or {}
    active = sub_by(tp, lambda v: v.get("unique_bounded_solution") is True)
    passive = sub_by(tp, lambda v: v.get("unique_bounded_solution") is False)
    dem = d.get(first_key(d, r"demand|spending_shock") or "") or {}
    fg = d.get(first_key(d, r"forward_guidance") or "") or {}
    variant = fg.get(gc.get("variant") or "rule_on") or sub_by(fg, lambda v: "paths" in v) or {}
    pz = fg.get(first_key(fg, r"peg|puzzle", test=lambda v: isinstance(v, dict)) or "") or {}
    shift_k = first_key(variant.get("paths") or {}, r"shift|intercept")
    for name, v in (("cost-push baseline", base), ("taylor active", active), ("taylor passive", passive), ("forward guidance", variant)):
        if not v:
            warn(f"set_the_rate.json: no {name} block")
    tp_side = lambda v: None if v is None else {"phi_pi": v.get("phi_pi"), "moduli": v.get("eigenvalue_moduli"),
                                                "outside": v.get("outside_unit_circle"), "needed": v.get("forward_looking_variables"),
                                                "unique": v.get("unique_bounded_solution"), "plain": v.get("plain")}
    ins = insights(folder)
    roles = by_role(ins, [("puzzle", ["forward_guidance.pegged", "pegged_puzzle"]), ("c", ["forward_guidance"]),
                          ("b", ["taylor_principle"]), ("a", ["cost_push"])])
    correct = {"a": which(ga.get("answer"), [("raise", r"^\s*rais|higher|up\b"), ("lower", r"^\s*lower|cut|down\b")]),
               "b": "many" if passive and passive.get("unique_bounded_solution") is False
               else which(gb.get("answer"), [("many", r"many|no unique|indetermin"), ("spirals", r"spiral|explod"), ("settles", r"settle|unique")]),
               "c": which(gc.get("answer"), [("yes", r"^\s*yes"), ("no", r"^\s*no\b")])}
    for k, v in correct.items():
        if v is None:
            warn(f"set_the_rate.json: cannot read the answer of guess.{k} ({(G.get(k) or {}).get('answer')!r})")
    return {
        "vars": vars_, "horizon": H, "ticks": ticks, "shock_pp": cal.get("shock_pp"), "units_time": units.get("time"),
        "calibration": {"source": cal.get("source"), "phi_pi": cal.get("phi_pi"), "phi_y": cal.get("phi_y")},
        "a": {"question": ga.get("question"), "answer": ga.get("answer"), "correct": correct["a"], "because": ga.get("because"),
              "rate_impact": unwrap(ga.get(first_key(ga, r"policy_rate|rate", test=lambda v: num(v) or isinstance(v, dict)) or "")),
              "shock": cp.get("shock"), "base": run(base), "strong": run(strong)},
        "b": {"question": gb.get("question"), "answer": gb.get("answer"), "correct": correct["b"], "outside": gb.get("outside_unit_circle"),
              "needed": gb.get("needed"), "active": tp_side(active), "passive": tp_side(passive),
              "demo": {"label": dem.get("label"), "shock": dem.get("shock"), "phi_pi": dem.get("phi_pi"),
                       "impact": dem.get("impact"), "paths": paths_of(dem, keys)} if dem else None},
        "c": {"question": gc.get("question"), "answer": gc.get("answer"), "correct": correct["c"], "caveat": gc.get("caveat"),
              "quarter": fg.get("quarter"), "cut_pp": fg.get("cut_pp"), "announcement": variant.get("announcement"),
              "today": variant.get("today"), "in_quarter": variant.get("in_quarter"), "paths": paths_of(variant, keys),
              "shift": (variant.get("paths") or {}).get(shift_k) if shift_k else None,
              "puzzle": {"text": pz.get("puzzle"), "reported_as": pz.get("reported_as"), "announcement": pz.get("announcement"),
                         "at": pz.get("at_quarter"), "last": pz.get("last"), "published_version": pz.get("published_version")}},
        "citations": d.get("citations") or {}, "refs": refs(d.get("citations")), "insights": ins, "roles": roles,
    }, st


def build(spend_dir, rate_dir, fixtures=False):
    WARNINGS.clear()
    print("Economics page inputs:")
    spend, s1 = spend_block(spend_dir)
    rate, s2 = rate_block(rate_dir)
    inputs = {FILES[0]: s1, FILES[1]: s2}
    for (name, st), folder in zip(inputs.items(), (spend_dir, rate_dir)):
        print(f"  {st:12s}  {name:20s} ({folder})")
    return {
        "tag": TAG, "curve_label": CURVE_LABEL, "inputs": inputs,
        "preliminary": any(v != "final" for v in inputs.values()),
        "placeholder": fixtures or any(v == "fixture" for v in inputs.values()),
        "prize": PRIZE, "spend": spend, "rate": rate, "fonts": FONTS, "scale_ticks": SCALE_TICKS, "range_ticks": RANGE_TICKS,
        "warnings": list(WARNINGS),
        "links": {"github": GITHUB, "showtime": SHOWTIME, "spend": GITHUB + TOYS[0] + "/", "rate": GITHUB + TOYS[1] + "/"},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from", dest="src", nargs=2, metavar=("SPEND_RESULTS", "RATE_RESULTS"))
    ap.add_argument("--fixtures", action="store_true")
    ap.add_argument("--out", default=str(HERE / "data.js"))
    a = ap.parse_args(argv)
    if a.fixtures:
        dirs = tuple(FIXTURES / t / "results" for t in TOYS)
    elif a.src:
        dirs = tuple(Path(p).resolve() for p in a.src)
    else:
        dirs = DEFAULTS
    data = build(*dirs, fixtures=a.fixtures)
    js = ("// Generated by build_data.py; do not edit. Educational demos made to show an open-source tool. Not research.\n"
          "window.NOBEL_ECON_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + ";\n")
    Path(a.out).write_text(js, encoding="utf-8")
    print(f"wrote {a.out} ({len(js.encode()) / 1024:.1f} KB); preliminary box {'shown' if data['preliminary'] else 'hidden'}"
          f"; {len(data['warnings'])} warning(s)")
    return data


if __name__ == "__main__":
    main(sys.argv[1:])
