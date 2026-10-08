"""Tests for the survival ledger. Fast (< 5 s), offline.

Optional: LIT_BIO_HTML=/path/to/saved/bio-bibliography.html checks every Committee phrase byte for byte.
The quotes from the other sources are checked against the live pages by `python -m ledger.check_sources`
(network); its last result is committed as results/source_check.json and read here.
"""
import html
import json
import os
import re
from pathlib import Path

import pytest

from ledger import rows as R
from ledger import run_all

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
COMMITTEE_NAMED = {"Sappho", "Sophocles", "Euripides", "Aeschylus", "Stesichoros", "Catullus", "Simonides", "Thucydides"}


def numbers(f):
    if f is None:
        return []
    if "range" in f:
        lo, hi = f["range"]
        assert lo <= hi
        return [lo, hi]
    return [f["value"]] if f.get("value") is not None else []


def test_only_committee_named_authors():
    for r in R.ROWS:
        assert any(name in r["author"] for name in COMMITTEE_NAMED), r["author"]
        assert r["committee_phrase"].strip()


def test_every_number_has_a_source():
    for r in R.ROWS:
        for key in ("ancient_count", "modern_estimate", "survives", "ancient_book1"):
            f = r.get(key)
            if f is None:
                continue
            assert f["sources"], (r["id"], key)
            for s in f["sources"]:
                assert s in R.SOURCES, (r["id"], key, s)
        assert r["dates"]["sources"]


def test_two_sources_where_possible():
    # Every count with a number has >= 2 sources, except those we name here (only one source found).
    single = {("stesichoros", "ancient_count"), ("geryoneis", "survives"), ("thucydides", "modern_estimate")}
    for r in R.ROWS:
        for key in ("ancient_count", "modern_estimate", "survives", "ancient_book1"):
            f = r.get(key)
            if f is None or not numbers(f):
                continue
            if (r["id"], key) not in single:
                assert len(f["sources"]) >= 2, (r["id"], key)


def test_every_source_has_url_and_quote():
    for k, (name, url, anchor, quote, how) in R.SOURCES.items():
        assert url.startswith("https://"), k
        if k != "BIO":
            assert quote and len(quote.split()) <= 30, k


def test_nc_licensed_sources_are_paraphrased_not_quoted():
    """One rule: Suda On Line and World History Encyclopedia are CC BY-NC-SA: cited, never copied (our paraphrase +
    key words to check)."""
    sol = {k for k, v in R.SOURCES.items() if any(h in v[1] for h in R.NC_LICENSED)}
    assert sol == set(R.PARAPHRASED) and "WHE_AESCH" in sol and "SUDA_SOPH" in sol
    for k in sol:
        assert "paraphrased" in R.SOURCES[k][4] and R.PARAPHRASED[k], k
    led = json.loads((RESULTS / "ledger.json").read_text(encoding="utf-8"))

    def walk(o):
        if isinstance(o, dict):
            if o.get("key") in sol:
                assert o.get("quote") is None and o.get("paraphrase"), o
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(led)


def test_source_check_found_every_quote():
    chk = json.loads((RESULTS / "source_check.json").read_text(encoding="utf-8"))
    quoted = {k for k, v in R.SOURCES.items() if v[3]}
    assert set(chk["results"]) == quoted
    for k, v in chk["results"].items():
        assert v["status"].startswith("found"), k


def test_survivors_within_totals():
    for r in R.ROWS:
        s = r.get("shelf")
        if s:
            assert s["survive"][1] <= s["total"][0] or s["total"] == s["survive"], r["id"]
    sap = next(r for r in R.ROWS if r["id"] == "sappho")
    g = sap["grid"]
    assert g["total"] == 100 * 100 and g["inked"] == 650 and g["label"] == "estimate"
    assert g["total"] in numbers(sap["modern_estimate"]) and g["alt_total"] in numbers(sap["modern_estimate"])
    assert sap["survives"]["value"] == g["inked"]
    assert sap["ancient_book1"]["value"] == g["book1"] == 1320


def test_key_numbers():
    by = {r["id"]: r for r in R.ROWS}
    assert numbers(by["sophocles"]["ancient_count"]) == [113, 130]
    assert numbers(by["sophocles"]["survives"]) == [7]
    assert numbers(by["euripides"]["survives"]) == [18, 19]
    assert numbers(by["aeschylus"]["modern_estimate"]) == [70, 90]
    assert numbers(by["stesichoros"]["ancient_count"]) == [26]
    assert numbers(by["geryoneis"]["ancient_count"]) == [1300]
    assert numbers(by["catullus"]["survives"]) == [113, 116]
    assert by["catullus"]["ancient_count"] is None and by["simonides"]["ancient_count"] is None


def test_sophocles_modern_estimate_is_open_ended():
    """Both modern sources say "more than 120"; 130 is the ancient ascription, not a modern estimate."""
    by = {r["id"]: r for r in R.ROWS}
    m = by["sophocles"]["modern_estimate"]
    assert m["open_ended"] and numbers(m) == [120] and "130" not in m["text"]
    assert numbers(by["sophocles"]["ancient_count"]) == [113, 130]
    led = {r["id"]: r for r in json.loads((RESULTS / "ledger.json").read_text(encoding="utf-8"))["rows"]}
    assert led["sophocles"]["modern_estimate"]["open_ended"] is True


def test_no_single_percentage_lost():
    blob = re.sub(r"https://\S+", "", json.dumps(run_all.build(), ensure_ascii=False))  # URLs may hold %-escapes
    # the only percentage allowed is Green's own "perhaps 5 per cent", quoted as his
    assert "%" not in blob
    assert blob.count("per cent") == 1


def test_results_match_code():
    led = json.loads((RESULTS / "ledger.json").read_text(encoding="utf-8"))
    assert led == json.loads(json.dumps(run_all.build()))
    assert led["label"] == "Educational demos made to show an open-source tool. Not research."
    for row in led["rows"]:
        for key in ("author", "dates", "unit", "ancient_count", "modern_estimate", "survives"):
            assert key in row
    for stem in ("bookshelf", "sappho_grid"):
        for theme in ("light", "dark"):
            assert (RESULTS / f"{stem}_{theme}.png").stat().st_size > 10_000


def test_unverified_items_not_in_rows():
    blob = json.dumps(R.ROWS, ensure_ascii=False)
    for bad in ("19 October", "Parsons", "Genos", "27 spurious"):
        assert bad not in blob


@pytest.mark.skipif(not os.environ.get("LIT_BIO_HTML"), reason="set LIT_BIO_HTML to a saved copy of the page")
def test_committee_phrases_byte_for_byte():
    t = Path(os.environ["LIT_BIO_HTML"]).read_text(encoding="utf-8")
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", t)
    t = re.sub(r"<(br|/p|/li|/h\d|/div)[^>]*>", "\n", t)
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t)))
    for r in R.ROWS:
        assert r["committee_phrase"] in t, r["id"]
