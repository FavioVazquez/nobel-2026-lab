"""Tests: every displayed string matches its public-domain source byte for byte; every alignment entry points to an
existing token; every gloss is in the stored LSJ text; the counts are reproducible. Run from
2026/literature/translators/: python -m pytest -q tests
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from translators import align, lsj, sources as S, versions as Vm  # noqa: E402
from translators.lemmas import LEMMA  # noqa: E402

RES = HERE / "results"
DATA = HERE / "data"
EXCERPT_SHA256 = {
    "wharton_pg57390_fr2.html": "e6ef21001a4c9bd20aa323bb51cfa88ffbc54a5aedd1cf8d37f9aa0bf80025a4",
    "wharton_pg57390_fr40.html": "209d902840ad30ca89b941ce601ec3133c1a9b54154abe2a5f7d9963f58f6f57",
    "smollett_pg4085_ch40.txt": "a67d7816c3122e311294a6adfbdeffe4dc4655024e8693e66126ddec2c0d9216",
}
# Where the full Gutenberg files may sit on the build machine (optional: the slice test is skipped without them).
FULL = {
    S.WHARTON_URL: [os.environ.get("WHARTON_HTML", "")],
    S.SMOLLETT_URL: [os.environ.get("SMOLLETT_TXT", "")],
}


def load(name):
    return json.loads((RES / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def V():
    return load("versions.json")


@pytest.fixture(scope="module")
def A():
    return load("alignment.json")


# ---------------------------------------------------------------------------------------------------------- sources
def test_excerpts_unchanged():
    for name, sha in EXCERPT_SHA256.items():
        assert hashlib.sha256((S.SRC / name).read_bytes()).hexdigest() == sha, name


def test_excerpts_are_slices_of_the_gutenberg_files():
    checked = 0
    for name, (url, a, b, sha) in S.EXCERPTS.items():
        for p in FULL.get(url, []):
            if p and Path(p).is_file():
                full = Path(p).read_bytes()
                assert hashlib.sha256(full).hexdigest() == sha
                lines = full.split(b"\n")
                assert b"\n".join(lines[a - 1:b]) + b"\n" == (S.SRC / name).read_bytes(), name
                checked += 1
                break
    if not checked:
        pytest.skip("full Gutenberg files not on this machine")


def _rendered_paragraphs(name):
    return [p["text"] for p in Vm.paragraphs(name)]


def test_every_displayed_line_is_in_its_source(V):
    fr2 = _rendered_paragraphs(Vm.FR2)
    for ln in V["greek"]["lines"]:
        assert ln["text"] in fr2
    merrill = S.raw(Vm.MERRILL)
    for v in V["versions"]:
        for ln in v["lines"]:
            if ln.get("lacuna"):
                assert ln["text"] is None and ln["source_text"] in fr2
                continue
            if v["id"] == "wharton":
                continue
            if ln.get("source") == "merrill":
                assert ln["text"] in merrill.split("\n")[ln["anchor"]["line_in_file"] - 1]
            else:
                assert ln["text"] in fr2, (v["id"], ln["text"])
    w = next(v for v in V["versions"] if v["id"] == "wharton")
    assert " ".join(ln["text"] for ln in w["lines"]) == w["full_text"]
    assert any(p.startswith(w["full_text"]) for p in fr2)


def test_attributions_are_wharton_s(V):
    want = {"philips": "Ambrose Philips, 1711.", "smollett": "Smollett, in Roderick Random, 1748.",
            "merivale": "John Herman Merivale, 1833.", "symonds": "J. Addington Symonds, 1883."}
    for v in V["versions"]:
        if v["id"] in want:
            assert v["wharton_credit"] == want[v["id"]]
    cat = next(v for v in V["versions"] if v["id"] == "catullus")
    assert cat["wharton_calls_it"].startswith("The famous imitation of this ode by Catullus")


def test_fr40_strings(V):
    fr40 = _rendered_paragraphs(Vm.FR40)
    f = V["fr40"]
    for ln in f["greek_lines"] + f["symonds"]["lines"]:
        assert ln["text"] in fr40
    assert f["wharton_prose"]["text"] in fr40
    assert "γλυκύπικρον" in f["greek_lines"][1]["text"]
    assert "bitter-sweet" in f["wharton_prose"]["text"]
    assert "bitter-sweet" in f["symonds"]["lines"][1]["text"]


def test_committee_sentence():
    d = json.loads((DATA / "sources" / "nobel_committee_sentence.json").read_text(encoding="utf-8"))
    assert d["quoted"] in d["sentence"]
    figsrc = (HERE / "translators" / "figures.py").read_text(encoding="utf-8")
    assert d["quoted"] in figsrc
    readme = re.sub(r"\s+", " ", (HERE / "README.md").read_text(encoding="utf-8"))
    assert d["quoted"] in readme


def test_crosscheck_files():
    cc = json.loads((DATA / "crosschecks.json").read_text(encoding="utf-8"))
    for vid, d in cc.items():
        if vid == "about" or not d.get("file"):
            continue
        assert (HERE / d["file"]).is_file(), d["file"]
    sp = (HERE / cc["philips"]["file"]).read_text(encoding="utf-8").split("\n")
    assert sp[cc["philips"]["anchor"]["poem_first_line"] - 1].strip().startswith("<td>Blest as th'immortal Gods is he,")
    me = (HERE / cc["merivale"]["file"]).read_text(encoding="utf-8").split("\n")
    assert "ODE" in me[cc["merivale"]["anchor"]["heading_line"] - 1] and me[cc["merivale"]["anchor"]["heading_line"] - 1].rstrip().endswith("M.")


def test_smollett_excerpt_holds_the_poem():
    s = S.raw("smollett_pg4085_ch40.txt")
    assert "I bow before thine altar, Love!" in s and "Unfriended live, unpitied die!" in s


def test_tokens_round_trip(V):
    for block in [V["greek"]] + V["versions"]:
        lines = {ln["n"]: ln["text"] for ln in block["lines"]}
        for t in block["tokens"]:
            for part in t["parts"]:
                txt = lines[part["line"]]
                assert txt[part["start"]:part["start"] + len(part["surface"])] == part["surface"]
            assert t["word"] == "".join(p["surface"] for p in t["parts"])


def test_greek_scope_count(V):
    assert sum(1 for t in V["greek"]["tokens"] if t["line"] <= 16) == 71
    assert next(t for t in V["greek"]["tokens"] if t["id"] == "greek:3:5")["word"] == "φωνεύσας"


# -------------------------------------------------------------------------------------------------------- alignment
def test_every_alignment_entry_points_to_existing_tokens(V, A):
    ids = {t["id"] for b in [V["greek"]] + V["versions"] for t in b["tokens"]}
    for name in ("alignment_pass1.json", "alignment_pass2.json", "alignment_final.json"):
        align.resolve(json.loads((DATA / name).read_text(encoding="utf-8")), V)  # raises on any bad ref
    for vid, links in A["links"].items():
        for gid, lk in links.items():
            assert gid in ids and int(gid.split(":")[1]) <= 16
            assert lk["to"] and all(t in ids and t.startswith(vid + ":") for t in lk["to"])
            assert lk["strength"] in ("close", "loose")


def test_resolution_log_covers_every_disagreement(V):
    p1 = align.resolve(json.loads((DATA / "alignment_pass1.json").read_text(encoding="utf-8")), V)
    p2 = align.resolve(json.loads((DATA / "alignment_pass2.json").read_text(encoding="utf-8")), V)
    diffs = align.compare(p1, p2)
    log = json.loads((DATA / "resolution_log.json").read_text(encoding="utf-8"))
    assert {(d["version"], d["greek"]) for d in diffs} == {(x["version"], x["greek"]) for x in log["log"]}
    assert all(x["reason"] for x in log["log"])
    final = align.resolve(json.loads((DATA / "alignment_final.json").read_text(encoding="utf-8")), V)
    for vid in final:  # outside the logged disagreements, final == both passes
        logged = {x["greek"] for x in log["log"] if x["version"] == vid}
        for gid in set(final[vid]) | set(p1[vid]):
            if gid not in logged:
                core = [None if x.get(gid) is None else (sorted(x[gid]["to"]), x[gid]["strength"])
                        for x in (final[vid], p1[vid], p2[vid])]
                assert core[0] == core[1] == core[2]


def test_no_link_into_out_of_scope_lines(V, A):
    w = next(v for v in V["versions"] if v["id"] == "wharton")
    line5 = {t["id"] for t in w["tokens"] if t["line"] == 5}
    assert not any(t in line5 for lk in A["links"]["wharton"].values() for t in lk["to"])
    cat = next(v for v in V["versions"] if v["id"] == "catullus")
    otium = {t["id"] for t in cat["tokens"] if t["line"] >= 13}
    assert not any(t in otium for lk in A["links"]["catullus"].values() for t in lk["to"])


def test_counts_reproducible(V, A):
    C = load("counts.json")
    again = align.counts(V, A["links"])
    for vid, row in again["versions"].items():
        for k, x in row.items():
            assert C["versions"][vid][k] == x, (vid, k)
    assert C["label"] == "our rough count, not a quality score"
    S_ = load("translators_summary.json")
    for row in S_["versions"]:
        assert row["greek_words_carried"] == C["versions"][row["id"]]["greek_words_carried"]
        assert row["words_added"] == C["versions"][row["id"]]["words_added"]
        assert row["greek_words_carried"] + row["greek_words_dropped"] == row["greek_words_in_scope"]


def test_counts_by_hand_for_one_version(V, A):
    # Wharton, stanza 1: 16 Greek words, all carried except ἔμμεν (his "seems" stands for "seems to be")
    links = A["links"]["wharton"]
    s1 = [t for t in V["greek"]["tokens"] if t["line"] <= 4]
    assert len(s1) == 16
    assert [t["word"] for t in s1 if t["id"] not in links] == ["ἔμμεν"]


# ----------------------------------------------------------------------------------------------------------- glosses
def test_glosses_are_in_the_stored_lsj_text(A):
    store = lsj.load()["entries"]
    chosen = json.loads((DATA / "glosses.json").read_text(encoding="utf-8"))["glosses"]
    for key, g in chosen.items():
        e = store[g["from"]]
        assert lsj.has_phrase(e, g["gloss"]), (key, g)
        if "lsj_cites_this_poem" in g:
            assert lsj.has_phrase(store[key], g["lsj_cites_this_poem"]), (key, g["lsj_cites_this_poem"])
        assert hashlib.sha256(e["xml"].encode("utf-8")).hexdigest() == e["sha256"] or e["truncated"]
    for t in A["greek_tokens"]:
        if t["line"] <= 16:
            assert t["gloss"]["gloss"] == chosen[LEMMA[t["id"]][0]]["gloss"]


def test_lsj_windows_against_full_files():
    d = os.environ.get("LSJ_DIR")
    if not d or not Path(d).is_dir():
        pytest.skip("set LSJ_DIR to the Perseus LSJ XML folder to check the stored excerpt against it")
    for k, e in lsj.load()["entries"].items():
        full = lsj._full_entry(Path(d), e)
        assert hashlib.sha256(full.encode("utf-8")).hexdigest() == e["sha256"]
        assert full.startswith(e["xml"])
        for w in e.get("windows", []):
            assert full[w["offset"]:w["offset"] + len(w["xml"])] == w["xml"]


def test_beta_code():
    assert lsj.beta_to_unicode("gluku/pikros") == "γλυκύπικρος"
    assert lsj.beta_to_unicode("kh=nos") == "κῆνος"
    assert lsj.beta_to_unicode("a)koh/") == "ἀκοή"
    assert lsj.beta_to_unicode("qnh/|skw") == "θνῄσκω"
    assert lsj.beta_to_unicode("kai/1") == "καί"


def test_compound_split():
    w = "γλυκύπικρον"
    assert w[:5] + w[5:] == w and w[:5] == "γλυκύ" and w[5:] == "πικρον"


# ----------------------------------------------------------------------------------------------------------- figures
def test_figures_exist_in_both_themes():
    for name in ("threads_stanza1", "threads_line1", "counts", "glukupikron"):
        for theme in ("light", "dark"):
            assert (RES / f"{name}_{theme}.png").stat().st_size > 10_000


def test_label_everywhere():
    label = "Educational demos made to show an open-source tool. Not research."
    assert label in (HERE / "README.md").read_text(encoding="utf-8")
    assert label in (HERE / "translators" / "figures.py").read_text(encoding="utf-8")
    for name in ("versions.json", "alignment.json", "translators_summary.json"):
        assert "Not research" in (RES / name).read_text(encoding="utf-8")
