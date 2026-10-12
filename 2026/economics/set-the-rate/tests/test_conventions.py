"""Lab conventions: every README and INSIGHTS number comes from the results JSON, the label is on the README and
every figure, figures come light and dark as PNG and SVG with <title> and <desc>. Educational demo, not research."""
import json
import re
import xml.etree.ElementTree as ET

import pytest
from matplotlib.image import imread

from nk import constants as C
from nk import run_all as R

HERE = C.HERE
RES = json.loads((C.RESULTS / C.RESULTS_JSON).read_text())
README = (HERE / "README.md").read_text()
NUM = re.compile(r"\d+(?:\.\d+)?")
SVG = "{http://www.w3.org/2000/svg}"


def tokens(obj):
    """Every number written anywhere in a JSON value: keys, strings and numbers (unsigned)."""
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


def resolve(path):
    v = RES
    for part in path.split("."):
        m = re.fullmatch(r"(.*?)\[(\d+)\]", part)
        v = v[m.group(1)][int(m.group(2))] if m else v[part]
    return v


def test_results_are_current():
    assert json.loads(json.dumps(R.summary())) == RES


def test_readme_sections_label_and_citations():
    assert C.LABEL in README and RES["label"] == C.LABEL
    heads = re.findall(r"^## (.+)$", README, flags=re.M)
    assert heads.index("What it does not show") <= 1 and heads.index("What it does not show") < heads.index("What it shows")
    flat = " ".join(README.split())
    for cite in C.CITATIONS.values():
        assert cite in flat, cite
    limits = README.split("## What it does not show", 1)[1].split("\n## ")[0]
    assert "forward guidance puzzle" in limits and "Del Negro" in limits and "McKay" in limits


def test_guess_questions_are_on_the_page_with_answers_in_the_json():
    flat = " ".join(README.split())
    for k in "abc":
        g = RES["guess"][k]
        assert g["question"] in flat and g["answer"]


def test_neutral_voice():
    for name in ("README.md", "INSIGHTS.md"):
        text = (HERE / name).read_text().lower()
        for word in C.FORBIDDEN:
            assert not re.search(r"\b%s\b" % word, text), (name, word)
    # the committee's words appear only inside quotation marks
    q = C.COMMITTEE_QUOTE
    assert README.count(q) == README.count('"%s"' % q) >= 1


def test_every_readme_number_is_in_the_json():
    missing = sorted(set(NUM.findall(prose(README))) - tokens(RES))
    assert not missing, missing


def test_insights_are_traced_to_json_fields():
    text = (HERE / "INSIGHTS.md").read_text()
    assert C.LABEL in text
    lines = [ln for ln in text.splitlines() if re.match(r"[1-9]\. ", ln)]
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


def test_spending_shock_is_named_and_explained():
    d = RES["demand_shock"]
    assert d["label"] == C.SPENDING_LABEL and "less patient" in d["shock"] and "p. 29" in d["committee_note"]
    readme = README
    assert C.SPENDING_LABEL in readme and "Phillips curve" in RES["cost_push_shock"]["shock"]
    assert "pp. 67-70" in readme and "memory" not in readme.replace("in Memory of Alfred Nobel", "")
