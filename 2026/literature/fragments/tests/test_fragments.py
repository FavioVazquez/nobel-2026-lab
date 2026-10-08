"""Checks for 'Where the words went'. Run from 2026/literature/fragments/:  python -m pytest -q tests

Every Greek and English string in results/fragments.json must equal its stored public-domain source byte for byte;
papyrus spans must reassemble their line; word counts must be reproducible and match our hand counts.
"""
from __future__ import annotations

import hashlib
import json
import re
import statistics
import sys
import unicodedata
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from sapphofrag import concordance, papyrus, quoters, wharton  # noqa: E402
from sapphofrag.greek import count_words  # noqa: E402
from sapphofrag.wharton import clean  # noqa: E402

DATA = json.loads((HERE / "results" / "fragments.json").read_text(encoding="utf-8"))
HTML = HERE / "sources" / "pg57390-images.html"
WHARTON_SHA256 = "bf616822d86ef89b75aa0ee68698568a81a9f3620edf642af73daaa4545cb247"  # Gutenberg file, 2026-10-08
# an independent view of the source: page numbers and tags removed, whitespace runs collapsed
_raw = re.sub(r'<span class="pagenum"[^>]*>\{\d+\}</span>', "", HTML.read_text(encoding="utf-8"))
RAW_CLEAN = clean(re.sub(r"<[^>]+>", "", _raw))
ROWS = {r["wharton_no"]: r for r in DATA["wharton_fragments"]}
PARSED = {f["wharton_no"]: f for f in wharton.parse(HTML)}


# --- (a) the papyrus -------------------------------------------------------------------------------------------
def test_papyrus_source_file_is_clean():
    rows = papyrus.load_lines()
    assert [r["line"] for r in rows] == list(range(13, 35))
    for r in rows:
        assert unicodedata.is_normalized("NFC", r["text"])
        assert r["page"] == (23 if r["line"] <= 30 else 25)
        assert "'" not in r["text"] and "·" not in r["text"]  # our conventions: U+2019 and U+00B7


def test_papyrus_json_equals_source_byte_for_byte():
    src = {r["line"]: r["text"] for r in papyrus.load_lines()}
    for ln in DATA["papyrus"]["lines"]:
        assert ln["text"].encode("utf-8") == src[ln["line"]].encode("utf-8")


def test_spans_reassemble_the_line():
    for ln in DATA["papyrus"]["lines"]:
        assert "".join(s["text"] for s in ln["spans"]) == ln["text"]
        assert {s["kind"] for s in ln["spans"]} <= {"read", "restored", "lost"}


def test_brackets_become_restored_or_lost_never_read():
    for ln in DATA["papyrus"]["lines"]:
        for s in ln["spans"]:
            if "[" in s["text"] or "]" in s["text"] or "⟨" in s["text"]:
                assert s["kind"] in ("restored", "lost"), s
            if s["kind"] == "read":
                assert not re.search(r"[\[\]⟨⟩]", s["text"])


def test_papyrus_hand_checked_lines():
    by = {ln["line"]: ln for ln in DATA["papyrus"]["lines"]}
    # line 16 survives whole; line 25 opens a bracket that runs to the end of the line; 28 has a scribal omission
    assert [s["kind"] for s in by[16]["spans"]] == ["read"]
    assert by[25]["spans"][-1] == {"text": "[", "kind": "lost", "mark": "[ (open to line end)"}
    assert {"text": "⟨ν⟩", "kind": "restored", "mark": "⟨⟩"} in by[28]["spans"]
    assert DATA["papyrus"]["letters"]["lost_dots"] == 17  # 4 (l. 25) + 4 + 3 + 6 (l. 26)


def test_translation_byte_for_byte():
    en = DATA["papyrus"]["english_1914"]
    assert en["text"] == papyrus.load_translation()
    assert en["bracketed"] in en["text"]
    assert en["text"].startswith("‘Some say that the fairest thing on the black earth is a host of horsemen")


# --- (b) Sappho 31 ---------------------------------------------------------------------------------------------
def test_wharton_source_file_is_the_gutenberg_file():
    assert hashlib.sha256(HTML.read_bytes()).hexdigest() == WHARTON_SHA256
    assert DATA["sources"]["wharton"]["sha256"] == WHARTON_SHA256


def test_sappho31_lines_and_cut():
    s = DATA["sappho31"]
    lines = [g["text"] for g in s["greek_lines"]]
    assert lines == PARSED[2]["greek_lines"]
    assert len(lines) == 17 and s["stanzas"][-1] == [17]
    assert lines[0] == "Φαίνεταί μοι κήνος ἴσος θέοισιν"
    assert lines[16] == "ἀλλὰ πᾶν τόλματον, [ἐπεὶ καὶ πένητα]."
    assert s["cut_point"]["after_line"] == 17 and s["cut_point"]["line_in_stanza"] == 1
    for g in lines:
        assert g in RAW_CLEAN
    assert s["english_literal"]["text"] in RAW_CLEAN
    assert s["english_literal"]["text"].endswith("But I must dare all, since one so poor ...")


# --- (c) Wharton's fragments -----------------------------------------------------------------------------------
def test_every_wharton_number_once():
    assert sorted(ROWS) == list(range(1, 171))


@pytest.mark.parametrize("n", range(1, 171))
def test_wharton_strings_byte_for_byte(n):
    r = ROWS[n]
    assert r["greek_lines"] == PARSED[n]["greek_lines"]
    assert r["english_literal"] == PARSED[n]["english_literal"]
    for g in r["greek_lines"]:
        assert g in RAW_CLEAN  # the string occurs in the stored Gutenberg file (whitespace runs collapsed)
        assert unicodedata.is_normalized("NFC", g)
    if r["english_literal"]:
        assert r["english_literal"] in RAW_CLEAN


def test_counts_reproducible():
    for r in DATA["wharton_fragments"]:
        if r["words"] is None:
            assert r["greek_layout"] != "verse"
            continue
        c = count_words(r["greek_lines"])
        assert (c["words"], c["words_in_brackets"]) == (r["words"], r["words_in_brackets"])


def test_hand_counted_extremes():
    # counted by hand from the Greek, word by word (see README, "How we counted")
    hand = {2: 77, 1: 131, 118: 33, 40: 9, 16: 11, 47: 2, 49: 2, 61: 2, 96: 2, 115: 2}
    for n, w in hand.items():
        assert ROWS[n]["words"] == w, n
    st = DATA["stats"]
    assert [x["wharton_no"] for x in st["longest"][:3]] == [1, 2, 118]
    assert min(r["words"] for r in DATA["wharton_fragments"] if r["words"] is not None) == 2


def test_stats_recomputed():
    st = DATA["stats"]
    seen, words = set(), []
    for r in DATA["wharton_fragments"]:
        key = min(r["wharton_no"], r["shares_entry_with"] or r["wharton_no"])
        if r["words"] is not None and key not in seen:
            seen.add(key)
            words.append(r["words"])
    assert len(words) == st["n_entries_verse"] == 126
    assert statistics.median(words) == st["median_words"]
    assert sum(w <= 5 for w in words) == st["count_le_5"]
    assert abs(st["share_le_5"] - st["count_le_5"] / len(words)) < 1e-4
    assert sum(st["histogram"].values()) == len(words)


def test_quoters_have_evidence_in_wharton():
    for n, (authors, evidence, via) in quoters.TABLE.items():
        if not authors:
            continue
        if via == "section":
            assert evidence in RAW_CLEAN
        else:
            assert evidence in " ".join(PARSED[via if via else n]["notes"]), n
        for a in authors:
            assert quoters.kind(a)
        assert ROWS[n]["source_author"] == authors[0]


def test_network_label_and_edges():
    net = DATA["quoters_network"]
    assert net["label"] == "as printed by Wharton, 1908"
    assert len(net["edges"]) == sum(len(r["source_authors"]) for r in DATA["wharton_fragments"])
    assert net["nodes_authors"][0]["author"] == "Hephaestion"


# --- numbering ---------------------------------------------------------------------------------------------------
def test_concordance_table():
    table = concordance.load_table(HERE / "sources" / "concordance_wharton_voigt.csv")
    assert sorted(table) == list(range(1, 171))
    known = {1: "1", 2: "31", 13: "16", 40: "130", 41: "131", 3: "34"}  # also Wikipedia's Sappho 1, 31 articles
    for w, v in known.items():
        assert table[w]["voigt_no"] == v
    for r in table.values():
        assert r["status"] in ("auto", "hand", "probable", "gap")
        assert bool(r["voigt_no"]) == (r["status"] != "gap")
    for r in DATA["wharton_fragments"]:
        assert (r["voigt_no"] or "") == table[r["wharton_no"]]["voigt_no"]


def test_label_everywhere():
    assert DATA["label"] == "Educational demos made to show an open-source tool. Not research."
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    assert DATA["label"] in readme
