"""Checks of build_data.py, data.js and index.html. Educational demos made to show an open-source tool. Not research.

    python3 -m pytest -q tests      (from 2026/economics/page/)
"""
import ast
import copy
import json
import re
import sys
from pathlib import Path

import pytest

PAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PAGE))
import build_data  # noqa: E402

FIX = PAGE / "tests" / "fixtures"
SPEND, RATE = (FIX / t / "results" for t in build_data.TOYS)
HTML = (PAGE / "index.html").read_text(encoding="utf-8")
BANKS = re.compile(r"federal reserve|riksbank|european central bank|\bECB\b|bank of england|bank of japan|bundesbank", re.I)


def read_js(path):
    s = Path(path).read_text(encoding="utf-8")
    return s, json.loads(s[s.index("= ") + 2:s.rstrip().rindex(";")])


def fixture_json(i):
    return json.loads((FIX / build_data.TOYS[i] / "results" / build_data.FILES[i]).read_text(encoding="utf-8"))


def write_toy(tmp_path, i, d, insights=True):
    out = tmp_path / build_data.TOYS[i] / "results"
    out.mkdir(parents=True)
    (out / build_data.FILES[i]).write_text(json.dumps(d), encoding="utf-8")
    if insights:
        (out.parent / "INSIGHTS.md").write_text((FIX / build_data.TOYS[i] / "INSIGHTS.md").read_text(encoding="utf-8"), encoding="utf-8")
    return out


def test_fixtures_are_labelled(tmp_path):
    d = build_data.main(["--fixtures", "--out", str(tmp_path / "d.js")])
    assert d["placeholder"] and d["preliminary"]
    assert set(d["inputs"].values()) == {"fixture"}


def test_missing_inputs_do_not_crash(tmp_path):
    d = build_data.main(["--from", str(tmp_path / "a"), str(tmp_path / "b"), "--out", str(tmp_path / "d.js")])
    assert d["spend"] is None and d["rate"] is None and set(d["inputs"].values()) == {"missing"} and d["preliminary"]
    assert "not in this copy" in HTML


def test_status_rules():
    assert build_data.status_of(None) == "missing"
    assert build_data.status_of({}) == "final"
    assert build_data.status_of({"status": "final (v2)"}) == "final"
    assert build_data.status_of({"status": "draft"}) == "preliminary"


def test_spending_numbers_are_the_toys_guess_block():
    j = fixture_json(0)
    ga, gb = j["guess"]["a"], j["guess"]["b"]
    S = build_data.build(SPEND, RATE)["spend"]
    assert S["a"]["answer"] == ga[S["a"]["answer_key"]] and S["a"]["answer_key"].startswith("answer")
    assert S["a"]["question"] == ga["question"] and S["b"]["question"] == gb["question"]
    shown = {m["key"] for m in S["a"]["more"]} | {S["a"]["answer_key"]}
    numbers = {k for k, v in ga.items() if build_data.num(v) and k.endswith("pct")}
    assert numbers - shown <= {k for k in numbers if "benchmark" in k}  # every other number of guess.a is shown small
    assert S["b"]["ours"]["ci"] in [v for v in build_data.flat(gb).values() if build_data.pair(v)]
    assert S["b"]["cm"]["quote"] in json.dumps(j, ensure_ascii=False)
    assert S["b"]["hm"]["quote"] in json.dumps(j, ensure_ascii=False)
    assert S["control"]["true_pct"] > 0 and S["control"]["coverage_pct"] is not None
    assert not S["synthetic"]
    assert "answer" not in S["b"] and "b.answer" not in HTML  # our share is shown only as a range


def test_rate_numbers_are_the_toys_json():
    j = fixture_json(1)
    R = build_data.build(SPEND, RATE)["rate"]
    keys = [v["key"] for v in R["vars"]]
    assert keys == [k for k in j["units"] if k != "time"]
    cp = j["cost_push_shock"]
    base = next(v for v in cp.values() if isinstance(v, dict) and v.get("phi_pi") == j["calibration"]["phi_pi"])
    assert R["a"]["base"]["impact"] == base["impact"] and R["a"]["base"]["paths"] == {k: base["paths"][k] for k in keys}
    assert R["a"]["rate_impact"] == base["impact"]["policy_rate"]
    assert R["c"]["today"] == j["forward_guidance"][j["guess"]["c"]["variant"]]["today"]
    assert R["c"]["quarter"] == j["forward_guidance"]["quarter"] == next(i for i, x in enumerate(R["c"]["shift"]) if x)
    assert R["b"]["passive"]["unique"] is False and R["b"]["active"]["unique"] is True
    assert (R["a"]["correct"], R["b"]["correct"], R["c"]["correct"]) == ("raise", "many", "yes")
    assert all(len(p) == R["horizon"] + 1 for blk in (R["a"]["base"], R["c"]) for p in blk["paths"].values())


def test_field_names_are_read_not_typed(tmp_path):
    """A renamed headline (the spending toy was being revised) is still found, with its interval and its neighbours."""
    j = fixture_json(0)
    ga = j["guess"]["a"]
    v = ga.pop(next(k for k in ga if k.startswith("answer")))
    ga["answer_lags_2_4_pct"] = v
    ga["answer_lags_2_4_ci95_pct"] = [v - 1, v + 1]
    ga["lags_1_4_pct"] = 42.5
    gb = j["guess"]["b"]
    for k in [k for k in gb if k.startswith("answer") and not build_data.pair(gb[k])]:
        gb.pop(k)
    S = build_data.build(write_toy(tmp_path, 0, j), RATE)["spend"]
    assert S["a"]["answer"] == v and S["a"]["ci"] == [v - 1, v + 1]
    assert {"key": "lags_1_4_pct", "label": "lags 1-4", "value": 42.5, "ci": None, "p": None, "quarters": None} in S["a"]["more"]
    assert S["b"]["ours"]["ci"] is not None


def test_synthetic_toy_is_labelled_simulated(tmp_path):
    j = fixture_json(0)
    j.pop("data")
    S = build_data.build(write_toy(tmp_path, 0, j), RATE)["spend"]
    assert S["synthetic"] and S["credit"]["licence"] == []
    assert "simulated" in HTML and "no data" in HTML


def test_committed_data_js_is_the_final_toys():
    s, d = read_js(PAGE / "data.js")
    assert s.startswith("// Generated by build_data.py; do not edit. " + build_data.TAG)
    assert d["tag"] == build_data.TAG and not d["preliminary"] and set(d["inputs"].values()) == {"final"}
    f = build_data.build(SPEND, RATE)
    assert d["spend"] == f["spend"] and d["rate"] == f["rate"] and d["prize"] == f["prize"]
    assert d["warnings"] == f["warnings"]
    assert len(s.encode()) < 45_000


def test_exact_credits():
    j0, j1 = fixture_json(0), fixture_json(1)
    d = build_data.build(SPEND, RATE)
    lic = j0["data"][next(k for k in j0["data"] if "licen" in k)]
    texts = {x["text"] for x in d["spend"]["credit"]["licence"]}
    strings = [v for v in (lic.values() if isinstance(lic, dict) else [lic]) if isinstance(v, str)]
    assert texts and texts <= set(strings)
    assert d["spend"]["credit"]["source"] == j0["data"].get("source")
    assert d["rate"]["calibration"]["source"] == j1["calibration"]["source"]
    assert d["prize"]["url"] == "https://www.nobelprize.org/prizes/economic-sciences/2026/press-release/"
    assert d["prize"]["citation"] in j0["prize"] and d["prize"]["citation"] in j1["prize"]


def test_narrator_sentences_are_the_toys_insights():
    d = build_data.build(SPEND, RATE)
    for blk, toy, roles in ((d["spend"], build_data.TOYS[0], ("a", "b", "control")), (d["rate"], build_data.TOYS[1], ("a", "b", "c", "puzzle"))):
        md = (FIX / toy / "INSIGHTS.md").read_text(encoding="utf-8")
        assert blk["insights"] and all(i["text"] in md and i["fields"] for i in blk["insights"])
        assert all(blk["roles"][r] for r in roles), {r: len(blk["roles"][r]) for r in blk["roles"]}


def _body_text(html):
    body = html[html.index("<body>"):]
    body = re.sub(r"<(script|style)\b.*?</\1>", " ", body, flags=re.S)
    return re.sub(r"<[^>]+>", " ", body)


def _js_strings(html):
    js = " ".join(re.findall(r"<script>(.*?)</script>", html, flags=re.S))
    js = re.sub(r"\\u[0-9a-fA-F]{4}", "", js)
    js = re.sub(r"\$\{[^}]*\}", "", js)
    js = re.sub(r"^\s*//.*$", "", js, flags=re.M)
    return [m.group(0) for m in re.finditer(r"([\"'`])(?:\\.|(?!\1)[^\\\n])*\1", js)]


def test_no_number_is_typed_into_index_html():
    assert not re.search(r"\d", _body_text(HTML)), re.findall(r".{20}\d.{20}", _body_text(HTML))
    bad = [s for s in _js_strings(HTML) if re.search(r"\d", s) and not re.match(r"[\"'`]https?://", s)]
    assert not bad, bad
    head = HTML[:HTML.index("</head>")]
    texts = re.findall(r"<title>(.*?)</title>", head) + re.findall(r'name="description" content="([^"]*)"', head)
    texts += re.findall(r'property="og:(?:title|description|image:alt)" content="([^"]*)"', head)
    assert all(set(re.findall(r"\d+", t)) <= {"2026"} for t in texts)


def test_short_benchmark_lines():
    """The reveal shows two short lines; their quoted pieces are under 15 words and exactly in the toy's quotes."""
    j = fixture_json(0)
    b = build_data.build(SPEND, RATE)["spend"]["b"]
    pub = j["guess"]["b"]["published"]
    assert b["cm"]["short"] == "about 50 percent" and b["cm"]["short"] in pub["campbell_mankiw_quote"]
    assert b["hm"]["short"] in pub["hall_mishkin_quote"] and len(b["hm"]["short"].split()) < 15
    assert b["cm"]["years"] == [1953, 1986] and b["hm"]["years"] == [1969, 1975] and b["hm"]["pct"] == pub["hall_mishkin_pct"]
    assert build_data.fragment("x " * 20, r"(x ){16}") is None


def test_prize_name_and_site_name():
    """The official name, as the committee writes it, is in data.js (shown once, in the credits); titles stay without
    'Nobel'; og:site_name is "2026 prize labs"."""
    name = "Sveriges Riksbank Prize in Economic Sciences in Memory of Alfred Nobel"
    _, d = read_js(PAGE / "data.js")
    assert d["prize"]["name"] == name and all(name in fixture_json(i)["prize"] for i in (0, 1))
    assert HTML.count("P.name") == 1
    site = re.findall(r'property="og:site_name" content="([^"]*)"', HTML)
    assert site == ["2026 prize labs"]  # this page only; the other prize pages keep their own


def test_neutral_wording_and_title():
    own = _body_text(HTML) + " ".join(_js_strings(HTML))
    assert not re.search(r"\bshould\b|\bought to\b|right move|no (other )?(viable )?alternative", own, re.I)
    assert not re.search(r"\bwrong\b|\bfail(s|ed|ure)?\b|\bconfirm(s|ed)?\b|\brefut|\bdisprov|\bdebunk", own, re.I)
    assert not BANKS.search(own)
    head = HTML[:HTML.index("</head>")]
    for t in re.findall(r"<title>(.*?)</title>", head) + re.findall(r'property="og:title" content="([^"]*)"', head):
        assert "nobel" not in t.lower() and "Guess first, then see" in t
    _, d = read_js(PAGE / "data.js")
    shown = json.dumps({k: d[k] for k in ("spend", "rate")}, ensure_ascii=False)
    assert not re.search(r"\bshould\b", shown, re.I)
    assert HTML.count("D.curve_label") >= 4 and build_data.CURVE_LABEL == "textbook model, illustrative calibration"


def test_build_data_is_stdlib_only():
    tree = ast.parse((PAGE / "build_data.py").read_text(encoding="utf-8"))
    mods = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    mods |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert mods <= set(sys.stdlib_module_names), mods


def test_bundled_fonts_cover_the_page():
    for f in ("sans", "sans-bold", "serif", "italic", "mono"):
        assert (PAGE / "fonts" / f"{f}.woff2").exists()
    assert "SIL Open Font License" in (PAGE / "fonts" / "OFL.txt").read_text(encoding="utf-8")
    TTFont = pytest.importorskip("fontTools.ttLib").TTFont
    pytest.importorskip("brotli")
    _, d = read_js(PAGE / "data.js")
    chars = set(re.sub(r"<[^>]+>", "", _body_text(HTML)) + "".join(_js_strings(HTML)) + json.dumps(d, ensure_ascii=False))
    chars |= set("0123456789.,%\u00a0\u2212\u201c\u201d\u2019\u2013\u00b7")
    for f in ("sans", "mono"):
        cmap = set(TTFont(str(PAGE / "fonts" / f"{f}.woff2")).getBestCmap())
        missing = {c for c in chars if c.isprintable() and not c.isspace() and ord(c) not in cmap}
        assert not missing, (f, sorted(missing))


def test_og_and_screenshots():
    Image = pytest.importorskip("PIL.Image")
    assert Image.open(PAGE / "og.jpg").size == (1200, 630)
    for w in (360, 768, 1440):
        for t in ("light", "dark"):
            assert Image.open(PAGE / "screenshots" / f"page_{w}_{t}.png").size[0] == w


def test_fixture_copy_is_unchanged_by_the_build():
    before = copy.deepcopy(fixture_json(0))
    build_data.build(SPEND, RATE)
    assert fixture_json(0) == before
