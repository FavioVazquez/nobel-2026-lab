"""Build page/data.js from the Literature experiments (educational demos made to show an open-source tool; not research).

Reads, relative to this folder (where the experiments live after the merge):
  ../survival-ledger/results   ledger.json
  ../forms/results             forms.json, prize_history.json
  ../fragments/results         fragments.json
  ../translators/results       alignment.json, versions.json, translators_summary.json
  ../translators/data          glosses.json (LSJ glosses for the bitter-sweet box; optional)
and writes data.js, a plain script that sets window.NOBEL_LIT_DATA, so index.html works from file:// with no server
and no network. Every number and every Greek, Latin or English line the page shows comes from these files (or from
the few fixed facts below, each with its source); nothing is typed into index.html. Python 3 standard library only.

    python3 build_data.py                                           # from 2026/literature/page/ after the merge
    python3 build_data.py --from LEDGER FORMS FRAGMENTS TRANSLATORS  # the four results folders anywhere
    python3 build_data.py --fixtures                                # the trimmed placeholder inputs in tests/fixtures
    python3 build_data.py --out /tmp/data.js                        # write somewhere else

It prints the status of each input file ("final", "preliminary", "fixture" or "missing"). The page shows a visible
"preliminary" box unless every input is "final".
"""
import argparse
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "tests" / "fixtures"
LANES = ("survival-ledger", "forms", "fragments", "translators")
DEFAULTS = tuple(HERE.parent / lane / "results" for lane in LANES)
TAG = "Educational demos made to show an open-source tool. Not research."
GITHUB = "https://github.com/FavioVazquez/nobel-2026-lab/tree/main/2026/literature/"

# ---- fixed facts (the Swedish Academy and the Nobel Committee; facts only, no text of the laureate) ------------
PR = "https://www.nobelprize.org/prizes/literature/2026/press-release/"
BIO = "https://www.nobelprize.org/prizes/literature/2026/bio-bibliography/"
FACTS = "https://www.nobelprize.org/prizes/literature/2026/carson/facts/"
WOMEN = "https://www.nobelprize.org/prizes/lists/nobel-prize-awarded-women/"
API = "https://api.nobelprize.org/2.1/laureates?nobelPrizeCategory=lit&limit=300"
OPENER = {
    "citation": "for her bold and inventive oeuvre that, in playful dialogue with the classical tradition, "
                "has created new forms for contemporary literature",
    "citation_by": "The Swedish Academy, press release, 8 October 2026",
    "citation_url": PR,
    "who": [  # the fact sheet's safe list, items 1, 3, 4 and 5
        {"text": "Anne Carson, a Canadian author, born in Toronto in 1950.", "url": FACTS},
        {"text": "A classicist (her 1981 doctoral thesis was in Classics) who translates from Classical Greek: "
                 "Sappho, Sophocles, Euripides, Aeschylus.", "url": BIO},
    ],
}
# The Committee's own sentences (bio-bibliography, Anders Olsson). They are the Committee's text, quoted with credit.
COMMITTEE_COMPOUND = ("the book draws heavily on a compound adjective from Sappho that defines Eros as pain and "
                      "sweetness combined")
COMMITTEE_FLOAT = "capable of being read in any order"
FLOAT_CHAPBOOKS = 22  # Committee: "a work consisting of twenty-two chapbooks"
STATUS_ORDER = ["missing", "fixture", "preliminary", "final"]

# Short quotations of the laureate's own words, used as commentary (the owner's rule: a few, each at most 15 words,
# from different works, exact wording verified against a reliable source, attributed). The verified list lives in
# ../quotes.json; nothing of hers is typed into index.html.
QUOTES = HERE.parent / "quotes.json"
MAX_QUOTE_WORDS = 15


def quote_words(text):
    return len(re.findall(r"[\w’'-]+", text))


def quotes_block(path=QUOTES):
    """The verified quotations -> [{id, text, work, year, where, url}]. Refuses anything over the cap or unsourced."""
    d = load(path) or {}
    out = []
    for q in d.get("quotes", []):
        assert q.get("text") and q.get("work") and q.get("year") and q.get("sources"), q.get("id")
        assert quote_words(q["text"]) <= MAX_QUOTE_WORDS, (q["id"], quote_words(q["text"]))
        out.append({"id": q["id"], "text": q["text"], "work": q["work"], "year": q["year"], "where": q["where"],
                    "context": q.get("context"), "url": q["sources"][0]["url"]})
    return out


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def status_of(obj):
    if obj is None:
        return "missing"
    s = str(obj.get("status", "preliminary")).lower() if isinstance(obj, dict) else "preliminary"
    if s.startswith("final"):      # e.g. "final (before independent review)": the experiment calls its numbers final
        return "final"
    return s if s in ("preliminary", "fixture") else "preliminary"


def worst(*sts):
    return min(sts, key=STATUS_ORDER.index)


def srcs(v):
    """A source field (a string, a dict or a list of them) -> [{"name", "url", "anchor"}]."""
    if v is None:
        return []
    if not isinstance(v, list):
        v = [v]
    out = []
    for s in v:
        if isinstance(s, dict):
            name = s.get("name") or s.get("cite") or s.get("title") or s.get("key")
            out.append({"name": name, "url": s.get("url"), "anchor": s.get("anchor") if isinstance(s.get("anchor"), str) else None})
        elif isinstance(s, str):
            out.append({"name": s, "url": s if s.startswith("http") else None, "anchor": None})
    return [s for s in out if s["name"] or s["url"]]


def num(spec):
    """{"value": 7} / {"range": [70, 90]} / 7 / [70, 90] -> {"lo", "hi", "approx", "text", "note", "unit", "sources"}."""
    if spec is None:
        return None
    out = {"lo": None, "hi": None, "approx": False, "open": False, "text": None, "note": None, "unit": None, "sources": []}
    v = spec
    if isinstance(spec, dict):
        v = spec.get("range", spec.get("value"))
        out.update(text=spec.get("text"), note=spec.get("notes") or spec.get("note"), unit=spec.get("unit"),
                   sources=srcs(spec.get("source") or spec.get("sources")))
        u = str(spec.get("unit") or "")
        out["approx"] = bool(re.search(r"\babout\b|approx", u, re.I))
        out["open"] = bool(spec.get("open_ended"))   # "more than N": the value is a lower bound, there is no upper one
        out["unit"] = re.sub(r"\s*\((about|approx\.?)\)", "", u).replace("(about)", "").strip() or None
    if isinstance(v, (list, tuple)) and len(v) >= 2 and all(isinstance(x, (int, float)) for x in v[:2]):
        out["lo"], out["hi"] = min(v[:2]), max(v[:2])
    elif isinstance(v, (int, float)) and not isinstance(v, bool):
        out["lo"] = out["hi"] = v
    elif not (out["note"] or out["text"]):
        return None
    for k in ("lo", "hi"):
        if isinstance(out[k], float) and out[k].is_integer():
            out[k] = int(out[k])
    return out


# ---- I. survival ledger -------------------------------------------------------------------------------------------
def ledger_block(folder):
    d = load(folder / "ledger.json")
    files = {"ledger.json": status_of(d)}
    if d is None:
        return None, files
    rows, sappho = [], {}
    for r in d.get("rows") or []:
        if r.get("id") == "sappho" or str(r.get("author", "")).lower() == "sappho":
            grid = r.get("grid") or {}
            est = num(r.get("modern_estimate"))
            gh = None
            if grid.get("alt_total") is not None:
                gh_src = [s for s in (est or {}).get("sources", []) if re.search(r"grenfell|1914", str(s["name"]), re.I)]
                gh = {"lo": grid["alt_total"], "hi": grid["alt_total"], "approx": True, "sources": gh_src,
                      "text": "Grenfell and Hunt's 1914 estimate", "note": None, "unit": "verses"}
            sappho = {"lines_est": est, "lines_surv": num(r.get("survives")), "book1": num(r.get("ancient_book1")),
                      "gh": gh, "books": num(r.get("ancient_count")),
                      "grid": {"total": grid.get("total", 10000), "inked": grid.get("inked"), "book1": grid.get("book1"),
                               "alt_total": grid.get("alt_total"), "label": grid.get("label", "estimate")}}
            continue
        sh = r.get("shelf") or None
        rows.append({"id": r.get("id"), "author": r.get("author"), "unit": r.get("unit"),
                     "survive": num(r.get("survives")), "ancient": num(r.get("ancient_count")),
                     "modern": num(r.get("modern_estimate")),
                     "shelf": {"total": sh.get("total"), "survive": sh.get("survive"), "fragments": bool(sh.get("fragments")),
                               "label": sh.get("label")} if sh else None,
                     "notes": [x for x in (r.get("ancient_count_note"), r.get("modern_estimate_note")) if isinstance(x, str)]})
    return {"status": status_of(d), "rows": rows, "sappho": sappho, "rules": d.get("reading_rules") or [],
            "unverified": d.get("unverified") or [], "label": d.get("label")}, files


# ---- IV. forms shelf, Float and the prize ----------------------------------------------------------------------------
def forms_block(folder):
    d = load(folder / "forms.json")
    files = {"forms.json": status_of(d)}
    if d is None:
        return None, files
    tags = d.get("tags") or {}
    works = []
    for w in d.get("works") or []:
        ev = ["%s: “%s” (%s)" % (e.get("tag"), e.get("evidence"), "the Committee's essay" if e.get("basis") == "committee" else "its bibliography line")
              for e in w.get("evidence") or [] if isinstance(e, dict)]
        works.append({"year": w.get("year"), "title": w.get("title"), "forms": w.get("tags") or [], "section": w.get("section"),
                      "line": w.get("bibliography_line"), "evidence": ev, "note": w.get("note") or None})
    works.sort(key=lambda w: (w["year"] if isinstance(w["year"], int) else 9999, str(w["title"])))
    forms = [{"id": k, "label": v, "n": sum(1 for w in works if k in w["forms"])} for k, v in tags.items()]
    forms.sort(key=lambda f: -f["n"])
    n_fact = math.factorial(FLOAT_CHAPBOOKS)
    fl = d.get("float_22") or {}
    if fl.get("orderings") is not None and int(str(fl["orderings"]).replace(",", "")) != n_fact:
        print(f"  WARNING: forms.json float_22.orderings = {fl['orderings']} differs from 22! = {n_fact}; the page uses 22!")
    if fl.get("chapbooks") not in (None, FLOAT_CHAPBOOKS):
        print(f"  WARNING: forms.json says {fl['chapbooks']} chapbooks; the Committee says {FLOAT_CHAPBOOKS}")
    years = n_fact / (365.25 * 24 * 3600)
    src = d.get("source") or {}
    return {"status": status_of(d), "works": works, "forms": forms, "summary": d.get("summary") or {},
            "source": src.get("url") if isinstance(src, dict) else (src or BIO), "selection_note": d.get("selection_note"),
            "tag_rule": d.get("tag_rule"),
            "float": {"n": FLOAT_CHAPBOOKS, "orderings": str(n_fact), "sci": f"{n_fact:.3e}",
                      "trillion_years": round(years / 1e12, 1),
                      "times_universe": fl.get("times_age_of_universe"), "universe_years": fl.get("age_of_universe_years"),
                      "universe_source": fl.get("age_of_universe_source"), "caveat": fl.get("caveat")}}, files


def prize_block(folder):
    d = load(folder / "prize_history.json")
    files = {"prize_history.json": status_of(d)}
    if d is None:
        return None, files
    t = d.get("totals") or {}
    decades = []
    for b in d.get("by_decade") or []:
        names = []
        for s in b.get("women_names") or []:
            m = re.match(r"(.*)\s+\((\d{4})\)\s*$", s)
            names.append([int(m.group(2)), m.group(1)] if m else [None, s])
        decades.append({"decade": int(str(b.get("decade"))[:4]), "first": b.get("first_year"), "last": b.get("last_year"),
                        "n": b.get("laureates"), "women": b.get("women"), "women_names": names,
                        "no_award": b.get("years_with_no_award")})
    women = [[int(w["year"]), w["name"]] for w in d.get("women") or []]
    n, nw = sum(x["n"] for x in decades), sum(x["women"] for x in decades)
    for k, v in (("laureates", n), ("women", nw)):
        if t.get(k) is not None and t[k] != v:
            print(f"  WARNING: prize_history totals.{k} = {t[k]} but the decades add up to {v}")
    if len(women) != nw:
        print(f"  WARNING: prize_history lists {len(women)} women but the decades count {nw}")
    c = d.get("carson") or {}
    ca = d.get("canada") or {}
    pr = (ca.get("field_press_release_wording") or {}).get("laureates") or []
    return {"status": status_of(d), "total": t.get("laureates", n), "women": t.get("women", nw), "men": t.get("men"),
            "prizes": t.get("years_awarded"), "shared_years": [int(y) for y in t.get("shared_years") or []],
            "years_no_award": [int(y) for y in t.get("years_with_no_award") or []],
            "decades": decades, "women_list": women,
            "last": [int(c.get("year", 0)), c.get("name")] if c else None, "woman_number": c.get("woman_number"),
            "canada": {"line": ca.get("safe_line"), "caveat": ca.get("caveat"),
                       "press": [{"year": int(x["year"]), "name": x["name"], "url": x.get("url")} for x in pr]} if ca else None,
            "gender_field": t.get("gender_field"), "source": (d.get("urls") or [API])[0], "fetched": d.get("fetched")}, files


# ---- II. fragments --------------------------------------------------------------------------------------------------
OPEN, CLOSE = "[⟨⟦(", "]⟩⟧)"


def split_span(text, kind):
    """One edition span (its brackets included) -> segments: brackets as 'br', the letters inside as 'rest' or 'lost'."""
    k = {"restored": "rest", "lost": "lost", "added": "rest"}.get(kind, "read")
    if k == "read":
        return [{"t": text, "k": "read"}]
    segs, i, j = [], 0, len(text)
    if text[:1] in OPEN:
        segs.append({"t": text[0], "k": "br"}); i = 1
    tail = None
    if j > i and text[j - 1] in CLOSE:
        tail = {"t": text[j - 1], "k": "br"}; j -= 1
    if j > i:
        segs.append({"t": text[i:j], "k": k})
    if tail:
        segs.append(tail)
    return segs


LOST_ONLY = re.compile(r"^[\s.…\-–—·̣c0-9±?]*$")


def leiden(text):
    """Split a line of bracketed text into segments (used for the 1914 English, which has no spans)."""
    segs, buf, inside = [], "", False

    def flush():
        nonlocal buf
        if buf:
            segs.append({"t": buf, "k": ("lost" if LOST_ONLY.match(buf) else "rest") if inside else "read"})
        buf = ""
    for ch in text:
        if ch == "[" and not inside:
            flush(); segs.append({"t": ch, "k": "br"}); inside = True
        elif ch == "]" and inside:
            flush(); inside = False; segs.append({"t": ch, "k": "br"})
        else:
            buf += ch
    flush()
    return segs


def letters(s):
    return sum(1 for c in s if unicodedata.category(c).startswith("L"))


def fragments_block(folder):
    d = load(folder / "fragments.json")
    files = {"fragments.json": status_of(d)}
    if d is None:
        return None, files
    S = d.get("sources") or {}
    out = {"status": status_of(d), "label": d.get("label"),
           "sources": [{"name": v.get("cite"), "url": v.get("url"), "licence": v.get("licence")} for v in S.values() if isinstance(v, dict) and v.get("cite")]}
    p = d.get("papyrus")
    if p:
        lines = []
        for ln in p.get("lines") or []:
            segs = []
            for sp in ln.get("spans") or [{"text": ln.get("text", ""), "kind": "read"}]:
                segs += split_span(sp["text"], sp.get("kind"))
            joined = "".join(s["t"] for s in segs)
            if joined != ln.get("text"):
                print(f"  WARNING: papyrus line {ln.get('line')}: spans do not rebuild the text")
            a = ln.get("anchor") or {}
            lines.append({"n": ln.get("line"), "segs": segs, "text": ln.get("text"), "page": a.get("page")})
        lt = p.get("letters") or {}
        counted = {"read": sum(letters(s["t"]) for l in lines for s in l["segs"] if s["k"] == "read"),
                   "rest": sum(letters(s["t"]) for l in lines for s in l["segs"] if s["k"] == "rest")}
        e = p.get("english_1914") or {}
        ea = e.get("anchor") or {}
        out["papyrus"] = {"id": p.get("title"), "edition": p.get("printed_by"), "url": p.get("source_url"),
                          "transcription": p.get("transcription"), "lines": lines,
                          "letters": {"read": lt.get("read", counted["read"]), "rest": lt.get("restored", counted["rest"]),
                                      "added": lt.get("added"), "lost_dots": lt.get("lost_dots")},
                          "letters_counted_here": counted,
                          "translation": [{"segs": leiden(e["text"])}] if e.get("text") else [],
                          "translator": e.get("translator"), "translation_page": ea.get("page"),
                          "bracket_meaning": e.get("bracket_meaning")}
    q = d.get("sappho31")
    if q:
        cp = q.get("cut_point") or {}
        unc = cp.get("uncertain_words") or {}
        url = None
        gl = []
        for x in q.get("greek_lines") or []:
            a = x.get("anchor") or {}
            url = url or (a.get("source") or "").split("#")[0] or None
            gl.append({"n": x.get("n"), "text": x.get("text"), "anchor": a.get("source")})
        ev = [{"name": e.get("cite"), "url": e.get("url"), "page": e.get("page"), "what": e.get("what")} for e in cp.get("evidence") or []]
        out["quote"] = {"wharton": 2, "voigt": 31, "title": q.get("title"), "by": q.get("quoted_in"), "lines": gl,
                        "stanzas": q.get("stanzas"), "stop": cp.get("after_line"), "stop_note": cp.get("what_happens"),
                        "uncertain_note": unc.get("note"), "url": url or (S.get("wharton") or {}).get("url"),
                        "anchor": (q.get("english_literal") or {}).get("anchor"), "evidence": ev[:1]}
    items = []
    for f in d.get("wharton_fragments") or []:
        v = f.get("voigt_no")
        items.append({"w": f.get("wharton_no"), "v": v if f.get("voigt_status") != "gap" else None,
                      "vq": f.get("voigt_status") == "probable", "n": f.get("words"),
                      "shared": f.get("shares_entry_with"), "by": f.get("source_author"), "anchor": f.get("anchor")})
    st = d.get("stats") or {}
    counted = [i for i in items if isinstance(i["n"], int) and i["n"] > 0 and not i["shared"]]
    if counted or st:
        ns = sorted(i["n"] for i in counted)
        m = len(ns)
        median = (ns[m // 2] if m % 2 else (ns[m // 2 - 1] + ns[m // 2]) / 2) if m else None
        hist = st.get("histogram")
        if isinstance(hist, dict) and hist:   # the experiment's own histogram is the one shown
            ns = sorted(int(k) for k, c in hist.items() for _ in range(int(c)))
        bins = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 15), (16, 20), (21, 30), (31, 10 ** 6)]
        counts = [sum(1 for x in ns if a <= x <= b) for a, b in bins]
        lg = {"n": st.get("n_entries_verse", len(ns)), "median": st.get("median_words", median),
              "le5": st.get("count_le_5", sum(1 for x in ns if x <= 5)), "le10": st.get("count_le_10", sum(1 for x in ns if x <= 10)),
              "over30": st.get("count_gt_30", sum(1 for x in ns if x > 30)), "unit": st.get("unit"),
              "inline": st.get("n_entries_inline_or_none"), "numbers": st.get("n_numbers"),
              "sensitivity": st.get("sensitivity_with_inline"), "rule": st.get("counting_rule"),
              "bins": [[a, b] for a, b in bins], "counts": counts, "items": [i for i in items if isinstance(i["n"], int) and i["n"] > 0]}
        if isinstance(lg["median"], float) and lg["median"].is_integer():
            lg["median"] = int(lg["median"])
        if sum(counts) != lg["n"]:
            print(f"  WARNING: fragments histogram holds {sum(counts)} entries, stats.n_entries_verse = {lg['n']}")
        if median is not None and lg["median"] != median:
            print(f"  WARNING: fragments median: stats say {lg['median']}, the entries give {median}")
        out["lengths"] = lg
    qn = d.get("quoters_network") or {}
    out["quoters"] = {"top": [[a.get("author"), a.get("kind"), a.get("n_fragments")] for a in (qn.get("nodes_authors") or [])[:6]],
                      "label": qn.get("label"), "caveat": qn.get("caveat")} if qn else None
    out["concordance"] = (S.get("concordance") or {}).get("numbers_from")
    return out, files


# ---- III. translators ---------------------------------------------------------------------------------------------------
def line_segs(text, toks):
    """Cut a printed line into plain text and word spans: toks = [(start, surface, token_id)]."""
    segs, pos = [], 0
    for start, surf, tid in sorted(toks):
        if text[start:start + len(surf)] != surf:
            print(f"  WARNING: token {tid} '{surf}' not found at {start} in '{text}'")
            continue
        if start > pos:
            segs.append({"t": text[pos:start]})
        segs.append({"t": surf, "id": tid})
        pos = start + len(surf)
    if pos < len(text):
        segs.append({"t": text[pos:]})
    return segs


def set_lines(lines, tokens):
    by_line = {}
    for t in tokens:
        for part in t.get("parts") or []:
            by_line.setdefault(part["line"], []).append((part["start"], part["surface"], t["id"]))
    out = []
    for l in lines:
        if l.get("text") is None:   # a line lost in the manuscripts, printed as a row of stars
            out.append({"n": l["n"], "stanza": l.get("stanza"), "lacuna": True, "segs": [{"t": l.get("source_text") or "* * *"}], "text": None})
        else:
            out.append({"n": l["n"], "stanza": l.get("stanza"), "segs": line_segs(l["text"], by_line.get(l["n"], [])), "text": l["text"]})
    return out


def translators_block(folder):
    al, vs, sm = load(folder / "alignment.json"), load(folder / "versions.json"), load(folder / "translators_summary.json")
    files = {"alignment.json": status_of(al), "versions.json": status_of(vs)}
    if vs is None or al is None:
        return None, files
    G = vs.get("greek") or {}
    gtok = {t["id"]: t for t in al.get("greek_tokens") or G.get("tokens") or []}
    greek_lines = set_lines(G.get("lines") or [], list(gtok.values()))
    gloss = {}
    for tid, t in gtok.items():
        g = t.get("gloss") or {}
        if g.get("gloss"):
            gloss[tid] = {"lemma": g.get("lemma"), "gloss": g.get("gloss"), "note": g.get("form_note")}
    summ = {v.get("id"): v for v in (sm or {}).get("versions") or []}
    links = al.get("links") or {}
    versions = []
    for v in vs.get("versions") or []:
        vid = v["id"]
        L = links.get(vid) or {}
        tok_g = {}
        for gid, lk in L.items():
            for to in lk.get("to") or []:
                tok_g.setdefault(to, []).append([gid, lk.get("strength", "close")])
        lines = set_lines(v.get("lines") or [], v.get("tokens") or [])
        for l in lines:
            for s in l["segs"]:
                if "id" in s:
                    s["g"] = tok_g.get(s["id"], [])
        c = summ.get(vid) or {}
        src = v.get("source") or {}
        versions.append({"id": vid, "who": v.get("full_name") or v.get("translator"), "short": v.get("translator"),
                         "year": v.get("year"), "date_label": v.get("date_label"), "lang": {"lat": "la", "eng": "en"}.get(v.get("language"), v.get("language")),
                         "kind": v.get("kind"), "poem": v.get("poem"), "credit": v.get("wharton_credit"),
                         "source": src.get("url"), "pages": src.get("pages"),
                         "extra_source": (v.get("source_lines_13_16") or {}).get("url"),
                         "extra_edition": (v.get("source_lines_13_16") or {}).get("edition"),
                         "lines": lines,
                         "links": {gid: {"to": lk.get("to"), "strength": lk.get("strength"), "note": lk.get("note")} for gid, lk in L.items()},
                         "counts": {"scope": c.get("greek_words_in_scope"), "carried": c.get("greek_words_carried"),
                                    "close": c.get("carried_close"), "loose": c.get("carried_loose"),
                                    "dropped": c.get("greek_words_dropped"), "words": c.get("version_words"),
                                    "added": c.get("words_added"), "moved": c.get("greek_words_moved_to_another_stanza"),
                                    "ranges": c.get("range_over_passes")}})
    versions.sort(key=lambda v: v["year"] if isinstance(v["year"], (int, float)) else 9999)
    # the bitter-sweet box: fr. 40, its Greek line and the two English renderings, LSJ glosses for the halves
    fr = vs.get("fr40") or {}
    glu = None
    word = "γλυκύπικρον"
    line2 = next((l["text"] for l in fr.get("greek_lines") or [] if word in l["text"]), None)
    if line2:
        gfile = load(folder.parent / "data" / "glosses.json") or {}
        gg = gfile.get("glosses") or {}
        sweet = "sweet" if "gluku/s" in gg else None   # LSJ: "sweet to the taste or smell"; the figure uses its first word
        bitter = (gg.get("pikro/s") or {}).get("gloss")
        compound = (gg.get("gluku/pikros") or {}).get("gloss")
        ws = fr.get("wharton_prose") or {}
        sy = fr.get("symonds") or {}
        sy_line = next((l["text"] for l in sy.get("lines") or [] if "bitter-sweet" in l["text"]), None)
        rend = []
        if "bitter-sweet" in (ws.get("text") or ""):
            rend.append({"who": "Wharton's literal prose", "year": 1885, "text": "bitter-sweet", "line": ws["text"]})
        if sy_line:
            rend.append({"who": "J. Addington Symonds", "year": 1883, "text": "bitter-sweet", "line": sy_line})
        src = fr.get("source") or {}
        glu = {"greek": word, "line": line2, "parts": [{"greek": word[:5], "gloss": sweet, "lemma": "γλυκύς"},
                                                       {"greek": word[5:], "gloss": bitter, "lemma": "πικρός"}],
               "compound_gloss": compound, "renderings": rend, "wharton": (fr.get("numbering") or {}).get("wharton_bergk"),
               "voigt": (fr.get("numbering") or {}).get("voigt"), "source": src.get("url"), "pages": src.get("pages")}
    gs = al.get("gloss_source") or {}
    return {"status": worst(status_of(al), status_of(vs)), "scope": al.get("scope"), "note": al.get("note"),
            "greek": {"lines": greek_lines, "label": G.get("label"), "source": (G.get("source") or {}).get("url"),
                      "pages": (G.get("source") or {}).get("pages"), "date": G.get("date"),
                      "numbering": G.get("numbering")},
            "gloss": gloss, "gloss_source": {"lexicon": gs.get("lexicon"), "licence": gs.get("licence"), "credit": gs.get("credit")},
            "versions": versions, "glukupikron": glu, "counts_label": (sm or {}).get("counts_label"),
            "disagreements": ((sm or {}).get("two_pass") or {}).get("disagreements"),
            "book": vs.get("wharton_book")}, files


# ---- all -------------------------------------------------------------------------------------------------------------
def build(ledger_dir, forms_dir, frag_dir, trans_dir, fixtures=False):
    print("Literature page inputs:")
    ledger, f1 = ledger_block(ledger_dir)
    forms, f2 = forms_block(forms_dir)
    prize, f2b = prize_block(forms_dir)
    frag, f3 = fragments_block(frag_dir)
    trans, f4 = translators_block(trans_dir)
    for folder, files in ((ledger_dir, f1), (forms_dir, {**f2, **f2b}), (frag_dir, f3), (trans_dir, f4)):
        for name, st in files.items():
            raw = (load(Path(folder) / name) or {}).get("status") if st != "missing" else None
            print(f"  {st:12s}  {name:20s} ({folder})" + (f'  [status field: "{raw}"]' if raw and raw != st else ""))
    file_status = {**f1, **f2, **f2b, **f3, **f4}
    return {
        "tag": TAG, "inputs": file_status,
        "preliminary": any(v != "final" for v in file_status.values()),
        "placeholder": fixtures or any(v == "fixture" for v in file_status.values()),
        "opener": OPENER, "committee": {"compound": COMMITTEE_COMPOUND, "float": COMMITTEE_FLOAT, "url": BIO,
                                        "by": "Nobel Committee for Literature, bio-bibliography (Anders Olsson)"},
        "ledger": ledger, "fragments": frag, "translators": trans, "forms": forms, "prize": prize,
        "github": GITHUB, "women_url": WOMEN, "api_url": API,
        "quotes": quotes_block(), "quote_cap": MAX_QUOTE_WORDS,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from", dest="src", nargs=4, metavar=("LEDGER", "FORMS", "FRAGMENTS", "TRANSLATORS"))
    ap.add_argument("--fixtures", action="store_true")
    ap.add_argument("--out", default=str(HERE / "data.js"))
    a = ap.parse_args(argv)
    if a.fixtures:
        dirs = tuple(FIXTURES / lane / "results" for lane in LANES)
    elif a.src:
        dirs = tuple(Path(p).resolve() for p in a.src)
    else:
        dirs = DEFAULTS
    data = build(*dirs, fixtures=a.fixtures)
    js = ("// Generated by build_data.py; do not edit. Educational demos made to show an open-source tool. Not research.\n"
          "window.NOBEL_LIT_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + ";\n")
    Path(a.out).write_text(js, encoding="utf-8")
    print(f"wrote {a.out} ({len(js.encode()) / 1024:.1f} KB); preliminary box {'shown' if data['preliminary'] else 'hidden'}")
    return data


if __name__ == "__main__":
    main(sys.argv[1:])
