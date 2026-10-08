"""One command: python -m translators.run_all   (from 2026/literature/translators/)

Builds results/versions.json, results/alignment.json, results/counts.json, results/translators_summary.json and
the figures. Reads only files in this folder (the LSJ excerpt is already stored in data/lsj_entries.json).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import align, versions

HERE = Path(__file__).resolve().parent.parent
RES = HERE / "results"
DATA = HERE / "data"
STATUS = "final"


def _dump(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def build(status: str = STATUS, figures: bool = True) -> dict:
    RES.mkdir(exist_ok=True)
    V = versions.write(RES / "versions.json", status)
    p1 = json.loads((DATA / "alignment_pass1.json").read_text(encoding="utf-8"))
    L1 = align.resolve(p1, V)
    p2_path = DATA / "alignment_pass2.json"
    final_path = DATA / "alignment_final.json"
    diffs, L2 = [], None
    if p2_path.exists():
        L2 = align.resolve(json.loads(p2_path.read_text(encoding="utf-8")), V)
        diffs = align.compare(L1, L2)
    if final_path.exists():
        final = json.loads(final_path.read_text(encoding="utf-8"))
        LF = align.resolve(final, V)
    else:
        final, LF = p1, L1
    C = align.counts(V, LF)
    if L2 is not None:
        # how much the counts move between the two passes: the honest error bar of a hand alignment
        C1, C2 = align.counts(V, L1), align.counts(V, L2)
        for vid, row in C["versions"].items():
            row["range_over_passes"] = {k: [min(c["versions"][vid][k] for c in (C1, C2, C)),
                                            max(c["versions"][vid][k] for c in (C1, C2, C))]
                                        for k in ("greek_words_carried", "greek_words_dropped", "words_added")}
    G = align.glosses()
    alignment = {
        "status": status,
        "note": "Educational demos made to show an open-source tool. Not research. Hand-made alignment of Wharton's "
                "Greek (lines 1-16) to six public-domain versions. Token ids point into results/versions.json.",
        "scope": C["scope"],
        "rules": "README.md, section 'How we aligned'",
        "passes": {"pass1": "data/alignment_pass1.json", "pass2": "data/alignment_pass2.json" if L2 else None,
                   "resolution_log": "data/resolution_log.json" if (DATA / "resolution_log.json").exists() else None,
                   "disagreements_between_passes": len(diffs) if L2 else None},
        "greek_tokens": [{**t, **({"gloss": G[t["id"]]} if t["id"] in G else {})} for t in V["greek"]["tokens"]],
        "links": LF,
        "gloss_source": {"lexicon": "LSJ, A Greek-English Lexicon (9th ed., 1940), Perseus digital edition",
                         "licence": "CC BY-SA 4.0", "credit": json.loads((DATA / "lsj_entries.json").read_text(encoding="utf-8"))["credit"]},
    }
    _dump(RES / "alignment.json", alignment)
    _dump(RES / "counts.json", C)
    if L2 is not None:
        _dump(RES / "pass_disagreements.json", {"count": len(diffs), "diffs": diffs})
    summary = {
        "status": status,
        "experiment": "One poem, 2,000 years of translators (Sappho 31 = Wharton 2 = Voigt 31)",
        "label": "Educational demos made to show an open-source tool. Not research.",
        "counts_label": align.LABEL,
        "scope": C["scope"],
        "versions": [{k: C["versions"][v["id"]][k] for k in ("translator", "year", "greek_stanzas_compared", "greek_words_in_scope",
                                                              "greek_words_carried", "carried_close", "carried_loose",
                                                              "greek_words_dropped", "version_words", "words_added",
                                                              "greek_words_moved_to_another_stanza")}
                     | {"range_over_passes": C["versions"][v["id"]].get("range_over_passes")}
                     | {"id": v["id"], "kind": v["kind"]} for v in V["versions"]],
        "two_pass": {"disagreements": len(diffs) if L2 else None},
    }
    _dump(RES / "translators_summary.json", summary)
    if figures:
        from . import figures as F
        F.make_all(V, alignment, C)
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-figures", action="store_true")
    ap.add_argument("--status", default=STATUS)
    a = ap.parse_args()
    s = build(a.status, figures=not a.no_figures)
    for v in s["versions"]:
        print(f"{v['translator']:>24} {v['year']:>5}  carried {v['greek_words_carried']:>2}/{v['greek_words_in_scope']} "
              f"(close {v['carried_close']}, loose {v['carried_loose']})  dropped {v['greek_words_dropped']:>2}  "
              f"added {v['words_added']:>2}/{v['version_words']}  moved {v['greek_words_moved_to_another_stanza']}  "
              f"range over passes {v['range_over_passes']}")
    print("two-pass disagreements:", s["two_pass"]["disagreements"])


if __name__ == "__main__":
    main()
