"""Lab conventions: every README and INSIGHTS number comes from the results JSON, the label is on the README and
every figure, figures come light and dark as PNG and SVG with <title> and <desc>, the licence lines are quoted,
and our own voice stays neutral. Educational demo, not research."""
import json
import re
import xml.etree.ElementTree as ET

import pytest
from matplotlib.image import imread

from spend import constants as C

HERE = C.HERE
RES = json.loads((C.RESULTS / C.RESULTS_JSON).read_text())
README = (HERE / "README.md").read_text()
INSIGHTS = (HERE / "INSIGHTS.md").read_text()
# Numbers with their sign: a minus counts only where it starts a number ("-0.052", "(-1.3 %"), not in a range such
# as "1953Q1-2019Q4" or "lags 2-4", where it follows a letter or digit.
NUM = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?")
SVG = "{http://www.w3.org/2000/svg}"


def tokens(obj):
    """Every number written anywhere in a JSON value: keys, strings and numbers (signed, see NUM)."""
    if isinstance(obj, dict):
        return set().union(set(), *(tokens(k) | tokens(v) for k, v in obj.items()))
    if isinstance(obj, list):
        return set().union(set(), *(tokens(v) for v in obj))
    if isinstance(obj, bool) or obj is None:
        return set()
    return set(NUM.findall(str(obj)))


def prose(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    return re.sub(r"https?://\S+", " ", text)


def flat(text):
    return " ".join(text.replace("> ", " ").split())


def resolve(path):
    v = RES
    for part in path.split("."):
        m = re.fullmatch(r"(.*?)\[(\d+)\]", part)
        v = v[m.group(1)][int(m.group(2))] if m else v[part]
    return v


def test_readme_sections_label_and_citations():
    assert C.LABEL in README and RES["label"] == C.LABEL
    heads = re.findall(r"^## (.+)$", README, flags=re.M)
    assert heads.index("What it does not show") < heads.index("What it shows")
    assert heads.index("What it does not show") <= 2  # early
    f = flat(README)
    for key in ("hall_1978", "campbell_mankiw_1989", "hall_mishkin_1982"):
        assert C.CITATIONS[key] in f, key


def test_what_it_does_not_show_covers_the_brief():
    part = README.split("## What it does not show", 1)[1].split("\n## ")[0].lower()
    for topic in ("aggregate", "durable", "measurement error", "time aggregation", "caus", "one country"):
        assert topic in part, topic


def test_licence_line_quoted_exactly_with_url_and_source():
    f = flat(README)
    assert C.BEA_LINE in f and C.BEA_URL in README and C.SOURCE_CREDIT in f and "durable" in README
    assert C.BULK_URL.format(name="") in README and C.VINTAGE["last_modified"] in f
    for rel in C.VINTAGE["releases"]:
        assert rel in f
    for text in (README, json.dumps(RES)):  # the data come from BEA's own files
        assert not re.search(r"\bFRED\b|stlouisfed", text)


def test_committee_words_are_quoted_and_credited():
    f = flat(README)
    for q in (C.COMMITTEE["hall"], C.COMMITTEE["sb_hall_mishkin"], C.CM_TABLE1["time_aggregation"],
              C.CM_TABLE1["about_half"], C.CM_TABLE1["conclusion"]):
        assert '"%s' % q in f, q
    assert "committee" in f.lower() and C.COMMITTEE["sb_hall_mishkin_sample"] in f


def test_neutral_voice():
    """Our own voice never argues for or against policy. Quotes are taken out before the check."""
    for text in (README, INSIGHTS):
        own = re.sub(r'"[^"]*"', " ", flat(text)).lower()
        for banned in ("should", "policy works", "the right move", "no alternative", "must ", "forecast for",
                       "we recommend"):
            assert banned not in own, banned


def test_every_readme_number_is_in_the_json():
    missing = sorted(set(NUM.findall(prose(README))) - tokens(RES))
    assert not missing, missing
    assert NUM.findall("1953Q1-2019Q4, lags 2-4, -0.052 (-1.3 %)") == ["1953", "2019", "2", "4", "-0.052", "-1.3"]


def test_review_round_2_fixes_stay_fixed():
    f, ins = flat(README), flat(INSIGHTS)
    for text in (f, ins):
        assert "estimates of A" not in text  # p. 195 has lambda; the PDF's text layer turned it into "A"
        assert "(about per cent)" not in text and "about per cent)" not in text
        assert "original form" not in text  # Hall (1978) worked in levels
        for cause in ("lockdown", "relief payment", "stimulus"):  # no unsourced cause for 2020-2021
            assert cause not in text.lower(), cause
        assert not re.search(r"\bstrong\b[^.]*2020-2026|2020-2026[^.]*\binstruments (are|were) strong", text)
    assert "estimates of \u03bb" in f and "growth-rate version" in f and "p. 982" in f
    assert C.HALL_1978["income_test_quote"] in f
    assert "effective F" in f and "Montiel Olea" in f and C.CITATIONS["montiel_olea_pflueger_2013"] in f
    assert "cannot be" in INSIGHTS and "103.1" in INSIGHTS  # a share above 100 % is impossible: said where it shows


def test_insights_are_traced_to_json_fields():
    assert C.LABEL in INSIGHTS
    lines = [ln for ln in INSIGHTS.splitlines() if re.match(r"[1-9]\. ", ln)]
    assert 3 <= len(lines) <= 6
    for ln in lines:
        body, _, refs = ln[2:].partition("(fields:")
        paths = re.findall(r"`([^`]+)`", refs)
        assert paths, ln
        have = set().union(*(tokens(resolve(p)) for p in paths))
        assert set(NUM.findall(body)) <= have, (ln, set(NUM.findall(body)) - have)


@pytest.mark.parametrize("stem", C.FIGURES)
def test_figures_light_and_dark_png(stem):
    light = imread(C.RESULTS / f"{stem}_light.png")
    dark = imread(C.RESULTS / f"{stem}_dark.png")
    assert light[2, 2, :3].mean() > 0.9 and dark[2, 2, :3].mean() < 0.2


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("stem", C.FIGURES)
def test_figures_svg_title_desc_and_label(stem, theme):
    root = ET.parse(C.RESULTS / f"{stem}_{theme}.svg").getroot()
    kids = list(root)
    assert kids[0].tag == SVG + "title" and kids[0].text.strip()
    assert kids[1].tag == SVG + "desc" and C.LABEL in kids[1].text
    assert root.get("role") == "img" and root.get("aria-labelledby") == "fig-title fig-desc"
    assert any(C.LABEL in "".join(el.itertext()) for el in root.iter(SVG + "text"))  # the label is drawn
