"""Tests for the forms shelf, the 22! card and the prize history. Fast (< 10 s), offline.

One optional test checks every Committee-essay phrase byte for byte against a saved copy of the bio-bibliography
page: set LIT_BIO_HTML=/path/to/bio-bibliography.html (saved from
https://www.nobelprize.org/prizes/literature/2026/bio-bibliography/). Without it, that test is skipped.
"""
import html
import json
import math
import os
import re
from pathlib import Path

import pytest

from shelf import analysis as A
from shelf import works as W

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def bib_entries():
    return {e["n"]: e for e in A.load_bibliography()["entries"]}


def test_22_factorial_exact():
    n = math.factorial(22)
    assert n == 1124000727777607680000
    prod = 1
    for k in range(1, 23):
        prod *= k
    assert prod == n
    card = A.float_card()
    assert card["orderings"] == "1124000727777607680000"
    assert card["orderings_grouped"] == "1,124,000,727,777,607,680,000"
    assert card["orderings_digits"] == 22
    assert int(card["orderings"]) == n  # the JSON keeps it as a string, exact


def test_results_json_match_code():
    forms = json.loads((RESULTS / "forms.json").read_text(encoding="utf-8"))
    assert forms["float_22"]["orderings"] == str(math.factorial(22))
    assert forms["summary"] == json.loads(json.dumps(A.forms_summary(A.forms_table())))
    hist = json.loads((RESULTS / "prize_history.json").read_text(encoding="utf-8"))
    assert hist == json.loads(json.dumps(A.prize_history()))


def test_bibliography_is_the_committee_selection():
    bib = A.load_bibliography()
    assert bib["url"] == "https://www.nobelprize.org/prizes/literature/2026/bio-bibliography/"
    secs = [e["section"] for e in bib["entries"]]
    assert secs.count("Works in English") == 33 and secs.count("Other") == 16
    forms = json.loads((RESULTS / "forms.json").read_text(encoding="utf-8"))
    assert "a selection" in forms["selection_note"]


def test_every_work_row_points_to_one_entry():
    ns = [w[0] for w in W.WORKS]
    assert sorted(ns) == list(range(1, 50)), "every Committee entry gets exactly one row"
    entries = bib_entries()
    for n, title, year, ev, note in W.WORKS:
        assert str(year) in entries[n]["line"], (n, year)


def test_every_tag_rests_on_a_quoted_string():
    entries = bib_entries()
    for n, title, year, ev, note in W.WORKS:
        for tag, basis, evidence in ev:
            assert tag in W.TAGS, tag
            assert basis in ("line", "committee")
            assert evidence.strip(), (n, tag)
            if basis == "line":
                assert evidence in entries[n]["line"], (n, tag, evidence)


def _page_text(path):
    t = Path(path).read_text(encoding="utf-8")
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", t)
    t = re.sub(r"<(br|/p|/li|/h\d|/div)[^>]*>", "\n", t)  # block ends -> line breaks
    t = re.sub(r"<[^>]+>", "", t)  # inline tags (<em>, <a>) vanish without adding space
    return re.sub(r"\s+", " ", html.unescape(t))


@pytest.mark.skipif(not os.environ.get("LIT_BIO_HTML"), reason="set LIT_BIO_HTML to a saved copy of the page")
def test_committee_phrases_byte_for_byte():
    text = _page_text(os.environ["LIT_BIO_HTML"])
    for n, title, year, ev, note in W.WORKS:
        for tag, basis, evidence in ev:
            if basis == "committee":
                assert evidence in text, (n, tag, evidence)
    for e in bib_entries().values():
        assert re.sub(r"\s+", " ", e["line"]) in text, e["n"]


def test_no_author_text_beyond_the_committee_line():
    # Evidence strings are titles, subtitles, bibliographic notes or Committee phrases; the one line of hers the
    # Committee quotes is not used in this folder at all.
    blob = json.dumps([w for w in W.WORKS], ensure_ascii=False)
    assert W.COMMITTEE_QUOTED_LINE not in blob
    for n, title, year, ev, note in W.WORKS:
        for _, _, evidence in ev:
            assert len(evidence.split()) <= 16, (n, evidence)


def test_forms_counts():
    s = A.forms_summary(A.forms_table())
    assert s["entries"] == 49
    assert s["works_per_tag"]["translation"] == 11
    assert s["entries_with_no_tag"] == 12
    assert s["first_year"] == 1981 and s["last_year"] == 2025


def test_prize_history_counts():
    h = A.prize_history()
    t = h["totals"]
    assert t["laureates"] == 123 == t["laureates_meta_count"]
    assert t["women"] == 19 and t["men"] == 104
    assert t["award_years_1901_2026"] == 126 and t["years_awarded"] == 119
    assert t["years_with_no_award"] == ["1914", "1918", "1935", "1940", "1941", "1942", "1943"]
    assert t["shared_years"] == ["1904", "1917", "1966", "1974"]
    assert sum(d["laureates"] for d in h["by_decade"]) == 123
    assert sum(d["women"] for d in h["by_decade"]) == 19
    assert h["by_decade"][-1] == {**h["by_decade"][-1], "decade": "2020s", "laureates": 7, "women": 4}
    assert h["carson"]["woman_number"] == 19
    assert h["women"][0] == {"year": "1909", "name": "Selma Lagerlöf"}


def test_canadians_say_which_field():
    c = A.prize_history()["canada"]
    born = sorted((r["year"], r["name"]) for r in c["field_birth_country"]["laureates"])
    assert born == [("1976", "Saul Bellow"), ("2013", "Alice Munro"), ("2026", "Anne Carson")]
    assert "not citizenship" in c["field_birth_country"]["field"]
    assert [r["name"] for r in c["field_press_release_wording"]["laureates"]] == ["Alice Munro", "Anne Carson"]
    assert c["safe_line"].startswith("Anne Carson is the second Canadian")


def test_label_on_outputs():
    forms = json.loads((RESULTS / "forms.json").read_text(encoding="utf-8"))
    assert forms["label"] == "Educational demos made to show an open-source tool. Not research."
    for stem in ("forms_count", "forms_matrix", "float_22", "prize_by_decade", "prize_timeline"):
        for theme in ("light", "dark"):
            assert (RESULTS / f"{stem}_{theme}.png").stat().st_size > 10_000
