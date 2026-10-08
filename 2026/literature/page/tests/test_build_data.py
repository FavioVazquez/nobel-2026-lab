"""Checks for build_data.py and the files it writes (educational demos made to show an open-source tool; not research).
Fast, standard library + pytest (fontTools and brotli are optional, for the font-coverage check).

    python3 -m pytest -q tests          (from 2026/literature/page/)
"""
import json
import math
import re
import sys
from pathlib import Path

import pytest

PAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PAGE))
import build_data as bd  # noqa: E402

FIX = PAGE / "tests" / "fixtures"
GREEK = re.compile(r"[Ͱ-Ͽἀ-῿]")


def read_js(path):
    s = Path(path).read_text(encoding="utf-8")
    return json.loads(s[s.index("window.NOBEL_LIT_DATA = ") + len("window.NOBEL_LIT_DATA = "):s.rstrip().rindex(";")])


@pytest.fixture(scope="module")
def fixture_data(tmp_path_factory):
    out = tmp_path_factory.mktemp("lit") / "data.js"
    bd.main(["--fixtures", "--out", str(out)])
    return read_js(out)


def all_strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from all_strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from all_strings(v)


def test_fixture_build_is_labelled_placeholder(fixture_data):
    d = fixture_data
    assert set(d["inputs"].values()) == {"fixture"}
    assert d["preliminary"] and d["placeholder"]
    assert d["tag"] == "Educational demos made to show an open-source tool. Not research."
    for k in ("ledger", "fragments", "translators", "forms", "prize"):
        assert d[k] is not None, k


def test_missing_inputs_do_not_crash(tmp_path, capsys):
    d = bd.main(["--from", *(str(tmp_path / x) for x in "abcd"), "--out", str(tmp_path / "d.js")])
    assert set(d["inputs"].values()) == {"missing"} and d["preliminary"]
    assert all(d[k] is None for k in ("ledger", "fragments", "translators", "forms", "prize"))
    assert "missing" in capsys.readouterr().out


def test_fixed_facts():
    # the citation, word for word as the press release prints it (facts.md, section 1)
    assert bd.OPENER["citation"] == ("for her bold and inventive oeuvre that, in playful dialogue with the classical "
                                     "tradition, has created new forms for contemporary literature")
    assert bd.FLOAT_CHAPBOOKS == 22 and bd.COMMITTEE_FLOAT == "capable of being read in any order"
    assert "compound adjective from Sappho" in bd.COMMITTEE_COMPOUND


def test_float_is_exact_arithmetic(fixture_data):
    f = fixture_data["forms"]["float"]
    assert f["orderings"] == str(math.factorial(22)) == "1124000727777607680000"
    assert f["sci"] == "1.124e+21"
    assert f["trillion_years"] == round(math.factorial(22) / (365.25 * 86400) / 1e12, 1) == 35.6


def test_leiden_spans_split_into_brackets_and_letters():
    assert bd.split_span("[Ο]", "restored") == [{"t": "[", "k": "br"}, {"t": "Ο", "k": "rest"}, {"t": "]", "k": "br"}]
    assert bd.split_span("⟨ν⟩", "restored") == [{"t": "⟨", "k": "br"}, {"t": "ν", "k": "rest"}, {"t": "⟩", "k": "br"}]
    assert bd.split_span("[. . . . ", "lost") == [{"t": "[", "k": "br"}, {"t": ". . . . ", "k": "lost"}]
    assert bd.split_span("εὔκ]", "restored") == [{"t": "εὔκ", "k": "rest"}, {"t": "]", "k": "br"}]
    assert bd.split_span("ἰ μὲν", "read") == [{"t": "ἰ μὲν", "k": "read"}]
    segs = bd.leiden("love led her astray. [Verily the wills] And I")
    assert [s["k"] for s in segs] == ["read", "br", "rest", "br", "read"]


def test_shown_lines_are_exact_copies_of_the_inputs(fixture_data):
    """Every Greek, Latin and English line the page sets is the experiments' string, unchanged: the segments a line is
    cut into join back to it byte for byte, and the line itself is a string of the input file."""
    raw = set()
    for p in FIX.rglob("*.json"):
        raw |= set(all_strings(json.loads(p.read_text(encoding="utf-8"))))
    P = fixture_data["fragments"]["papyrus"]
    for ln in P["lines"]:
        assert "".join(s["t"] for s in ln["segs"]) == ln["text"] and ln["text"] in raw
    for ln in fixture_data["fragments"]["quote"]["lines"]:
        assert ln["text"] in raw
    T = fixture_data["translators"]
    for ln in T["greek"]["lines"] + [l for v in T["versions"] for l in v["lines"]]:
        if ln.get("lacuna"):
            continue
        assert "".join(s["t"] for s in ln["segs"]) == ln["text"] and ln["text"] in raw, ln["text"]
    g = T["glukupikron"]
    assert g["line"] in raw and g["greek"] in g["line"] and g["parts"][0]["greek"] + g["parts"][1]["greek"] == g["greek"]
    for r in g["renderings"]:
        assert r["line"] in raw and r["text"] in r["line"]


def test_every_link_points_to_a_shown_word(fixture_data):
    T = fixture_data["translators"]
    gids = {s["id"] for l in T["greek"]["lines"] for s in l["segs"] if "id" in s}
    for v in T["versions"]:
        ids = {s["id"] for l in v["lines"] for s in l["segs"] if "id" in s}
        for gid, lk in v["links"].items():
            assert gid in gids, gid
            assert all(t in ids for t in lk["to"]), (v["id"], gid)


def test_ledger_numbers_have_sources(fixture_data):
    L = fixture_data["ledger"]
    for r in L["rows"]:
        for k in ("survive", "ancient", "modern"):
            if r[k] and r[k]["lo"] is not None:
                assert r[k]["sources"], (r["id"], k)
                assert r[k]["lo"] <= r[k]["hi"]
    S = L["sappho"]
    assert S["grid"]["total"] == 10000 and S["lines_surv"]["sources"] and S["book1"]["lo"] == 1320


def test_fragment_lengths_add_up(fixture_data):
    lg = fixture_data["fragments"]["lengths"]
    assert sum(lg["counts"]) == lg["n"]
    ns = sorted(i["n"] for i in lg["items"] if not i.get("shared"))
    assert lg["le5"] == sum(1 for x in ns if x <= 5)


def test_prize_counts(fixture_data):
    p = fixture_data["prize"]
    assert sum(d["n"] for d in p["decades"]) == p["total"] == 123
    assert sum(d["women"] for d in p["decades"]) == p["women"] == len(p["women_list"]) == 19
    assert p["last"] == [2026, "Anne Carson"] and len(p["shared_years"]) == 4


def test_page_types_no_greek_and_no_laureate_text():
    """index.html types no Greek and none of the laureate's words: they come from data.js (quotes from ../quotes.json)."""
    html = (PAGE / "index.html").read_text(encoding="utf-8")
    assert not GREEK.search(html), "Greek on the page must come from data.js, with its source"
    for f in ("index.html", "data.js", "build_data.py"):
        p = PAGE / f
        if p.exists():
            assert p.read_text(encoding="utf-8").count("hold in equipoise") <= 1
    for q in json.loads((PAGE.parent / "quotes.json").read_text(encoding="utf-8"))["quotes"]:
        assert q["text"] not in html, q["id"]


def test_quotations_verified_attributed_and_short():
    """Every quotation of the laureate: at most 15 words, exact text with a work, a year and a source that reproduces
    it, from different works, a few only; data.js carries exactly these."""
    import build_data as B
    Q = json.loads((PAGE.parent / "quotes.json").read_text(encoding="utf-8"))["quotes"]
    assert 1 <= len(Q) <= 8
    assert len({q["work"] for q in Q}) == len(Q), "one quotation per work"
    for q in Q:
        assert B.quote_words(q["text"]) <= B.MAX_QUOTE_WORDS, q["id"]
        assert q["work"] and isinstance(q["year"], int) and q["where"] and q["note"] == "short quotation for commentary"
        assert q["sources"] and all(s["url"].startswith("https://") for s in q["sources"]), q["id"]
        assert all(set(s) <= {"url", "kind"} for s in q["sources"]), "store the quoted span only, no surrounding text"
        assert "…" not in q["text"] and "..." not in q["text"], "a contiguous span only"
    p = PAGE / "data.js"
    if p.exists():
        d = read_js(p)
        assert [(x["id"], x["text"], x["work"], x["year"]) for x in d["quotes"]] == \
               [(q["id"], q["text"], q["work"], q["year"]) for q in Q]


def test_built_data_js_if_present():
    p = PAGE / "data.js"
    if not p.exists():
        pytest.skip("no data.js")
    d = read_js(p)
    assert d["preliminary"] == any(v != "final" for v in d["inputs"].values())
    assert len(p.read_bytes()) < 1.0e6


def test_greek_font_covers_every_greek_character():
    ft = pytest.importorskip("fontTools.ttLib")
    pytest.importorskip("brotli")
    used = {c for c in (PAGE / "data.js").read_text(encoding="utf-8") if GREEK.match(c)}
    cmap = ft.TTFont(str(PAGE / "fonts" / "greek.woff2")).getBestCmap()
    missing = sorted(c for c in used if ord(c) not in cmap)
    assert not missing, "".join(missing) + " (rerun make_fonts.py)"
