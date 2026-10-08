"""Assemble results/fragments.json from the three sources."""
from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter, defaultdict

from . import concordance, papyrus, quoters, wharton
from .greek import count_words
from .paths import RESULTS, SOURCES

WHARTON_HTML = SOURCES / "pg57390-images.html"
WHARTON_URL = "https://www.gutenberg.org/cache/epub/57390/pg57390-images.html"
WHARTON_CITE = ("H. T. Wharton, Sappho: Memoir, Text, Selected Renderings and a Literal Translation, "
                "5th ed. (London: John Lane, 1908), Project Gutenberg eBook #57390")
ROBERTS_URL = "https://archive.org/details/longinusonsubli00waygoog"
ROBERTS_CITE = ("W. Rhys Roberts, Longinus On the Sublime: the Greek text edited after the Paris manuscript "
                "(Cambridge University Press, 1899)")
LABEL = "Educational demos made to show an open-source tool. Not research."


def sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sappho31(frags: dict[int, dict]) -> dict:
    f = frags[2]
    lines = f["greek_lines"]
    assert len(lines) == 17, len(lines)
    stanzas = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16], [17]]
    return {
        "title": "Sappho 31 Voigt = Wharton 2 (Bergk 2), 'That man seems to me peer of gods'",
        "greek_lines": [{"n": i + 1, "text": t,
                         "anchor": {"source": WHARTON_URL + "#frag2", "fragment": 2, "line": i + 1}}
                        for i, t in enumerate(lines)],
        "stanzas": stanzas,
        "english_literal": {"text": f["english_literal"], "translator": "H. T. Wharton (literal prose, 1885-1908)",
                            "anchor": WHARTON_URL + "#frag2"},
        "quoted_in": "[Longinus], On the Sublime, chapter 10, sections 1-2",
        "cut_point": {
            "after_line": 17,
            "after_text": lines[16],
            "stanza": 5,
            "line_in_stanza": 1,
            "what_happens": ("The quotation in On the Sublime runs through four full Sapphic stanzas and the first "
                             "line of a fifth, then the critic's own words resume ('Are you not amazed ...', "
                             "section 3). Nothing more of the poem survives."),
            "uncertain_words": {
                "wharton_brackets": ["[ἄλλα]", "[ἐπεὶ καὶ πένητα]"],
                "note": ("Wharton prints these words in square brackets. Rhys Roberts (1899, Appendix A, "
                         "pp. 172-173) reports that Bergk bracketed 'ἐπεὶ καὶ πένητα' because the words may be "
                         "Longinus' own, not Sappho's; Crusius (1897) ends the ode at 'φαίνομαι ἄλλα'."),
            },
            "evidence": [
                {"cite": ROBERTS_CITE, "url": ROBERTS_URL, "page": 70, "scan_leaf": 90,
                 "what": ("Greek text: lines 1-16 printed as four stanzas, then line 17 'ἀλλὰ πᾶν τολματόν, ἐπεὶ "
                          "καὶ πένητα' set apart, then section 3 'οὐ θαυμάζεις ...' (Longinus' words)")},
                {"cite": ROBERTS_CITE, "url": ROBERTS_URL, "page": 71, "scan_leaf": 91,
                 "what": "English (verse by A. S. Way): four stanzas, then section 3 'Are you not amazed ...'"},
                {"cite": ROBERTS_CITE, "url": ROBERTS_URL, "page": "172-173",
                 "what": "Appendix A, textual note on p. 70: Bergk's brackets and Crusius' ending"},
            ],
        },
    }


def reason(note: str) -> str:
    """Our rough reading of why Wharton says the writer quoted it (label: 'our rough classification')."""
    n = note.lower()
    if any(k in n for k in ("metre", "metrical", "verse", "catalectic", "ithyphallic", "praxilleian", "scanned")):
        return "metre"
    if any(k in n for k in ("aeolic", "dialect", "accent", "the word", "form of", "use of", "meaning of",
                            "genitive", "accusative", "dative", "digamma", "verb", "particle", "defines")):
        return "language"
    if any(k in n for k in ("style", "grace", "beauty", "sublime", "ornament", "hyperbol", "harmony", "simple")):
        return "style"
    return "subject or unstated"


def _sensitivity(rows: list[dict], words: list[int]) -> dict:
    """If the numbers Wharton gives only as words inside prose were counted as 1 word each (most are a single cited
    word), how would the median and the share <= 5 move? A bound, not a count."""
    inline = [r for r in rows if r["greek_layout"] == "inline"]
    w2 = words + [1] * len(inline)
    return {"assumption": "each inline-only number counted as a 1-word fragment", "n": len(w2),
            "median_words": statistics.median(w2),
            "share_le_5": round(sum(1 for w in w2 if w <= 5) / len(w2), 4)}


def build() -> dict:
    parsed = wharton.parse(WHARTON_HTML)
    frags = {f["wharton_no"]: f for f in parsed}
    conc = concordance.load_table(SOURCES / "concordance_wharton_voigt.csv")

    rows = []
    for f in parsed:
        n = f["wharton_no"]
        authors, evidence, via = quoters.TABLE[n]
        c = count_words(f["greek_lines"]) if f["greek_layout"] == "verse" else None
        note_text = " ".join(frags[via]["notes"] if isinstance(via, int) else f["notes"])
        cv = conc[n]
        rows.append({
            "wharton_no": n,
            "printed_as": f["label"],
            "shares_entry_with": f["shares_entry_with"],
            "section": f["section"],
            "voigt_no": cv["voigt_no"] or None,
            "voigt_status": cv["status"],
            "greek_layout": f["greek_layout"],
            "greek": " / ".join(f["greek_lines"]) if f["greek_lines"] else None,
            "greek_lines": f["greek_lines"],
            "english_literal": f["english_literal"],
            "source_author": authors[0] if authors else None,
            "source_authors": authors,
            "source_kind": quoters.kind(authors[0]) if authors else None,
            "source_evidence": evidence or None,
            "quote_reason": reason(note_text) if authors else None,
            "words": c["words"] if c else None,
            "words_in_brackets": c["words_in_brackets"] if c else None,
            "anchor": WHARTON_URL + "#frag%d" % (f["shares_entry_with"] if f["shares_entry_with"]
                                                 and f["shares_entry_with"] < n else n),
        })

    # statistics: one count per printed entry (7/8, 107/108, 122/123 are one entry each), verse entries only
    seen = set()
    counted = []
    for r in rows:
        key = min(r["wharton_no"], r["shares_entry_with"] or r["wharton_no"])
        if r["words"] is None or key in seen:
            continue
        seen.add(key)
        counted.append((key, r["words"]))
    words = [w for _, w in counted]
    words_sorted = sorted(counted, key=lambda kv: (kv[1], kv[0]))
    hist = Counter(words)
    stats = {
        "unit": "a fragment entry Wharton prints as Greek verse (two numbers printed together count once)",
        "n_numbers": len(rows),
        "n_entries_verse": len(words),
        "n_entries_inline_or_none": sum(1 for r in rows if r["greek_layout"] != "verse"),
        "median_words": statistics.median(words),
        "mean_words": round(statistics.mean(words), 2),
        "share_le_5": round(sum(1 for w in words if w <= 5) / len(words), 4),
        "count_le_5": sum(1 for w in words if w <= 5),
        "share_le_10": round(sum(1 for w in words if w <= 10) / len(words), 4),
        "count_le_10": sum(1 for w in words if w <= 10),
        "count_gt_30": sum(1 for w in words if w > 30),
        "shortest": [{"wharton_no": k, "words": w} for k, w in words_sorted[:5]],
        "longest": [{"wharton_no": k, "words": w} for k, w in words_sorted[-5:][::-1]],
        "histogram": {str(k): hist[k] for k in sorted(hist)},
        "sensitivity_with_inline": _sensitivity(rows, words),
        "counting_rule": ("Greek words in Wharton's printed Greek: runs of Greek letters (with their accents), an "
                          "elided word with its apostrophe counts once, a word split over two lines with a hyphen "
                          "counts once, words in Wharton's square brackets count (also given separately), "
                          "metrical signs, dots and Latin letters do not count."),
    }

    # network: quoting author -> fragment (one edge per author named for a fragment number)
    edges = []
    by_author = defaultdict(list)
    for r in rows:
        for a in r["source_authors"]:
            edges.append({"author": a, "wharton_no": r["wharton_no"]})
            by_author[a].append(r["wharton_no"])
    first = Counter(r["source_author"] for r in rows if r["source_author"])
    network = {
        "label": "as printed by Wharton, 1908",
        "nodes_authors": [{"author": a, "kind": quoters.kind(a), "fragments": sorted(v),
                           "n_fragments": len(v), "n_first_named": first.get(a, 0)}
                          for a, v in sorted(by_author.items(), key=lambda kv: (-len(kv[1]), kv[0]))],
        "edges": edges,
        "by_kind": dict(Counter(quoters.kind(r["source_author"]) for r in rows if r["source_author"])),
        "by_reason": dict(Counter(r["quote_reason"] for r in rows if r["quote_reason"])),
        "no_author_named": [r["wharton_no"] for r in rows if not r["source_author"]],
        "caveat": ("Wharton's notes reflect 1908 knowledge. Some attributions are disputed, and modern editions "
                   "add many papyrus fragments Wharton never saw. "
                   "'kind' and 'reason' are our rough classification of his notes."),
    }

    conc_counts = Counter(r["voigt_status"] for r in rows)
    return {
        "status": "final (before independent review)",
        "label": LABEL,
        "sources": {
            "papyrus": {"cite": "B. P. Grenfell and A. S. Hunt, The Oxyrhynchus Papyri, Part X (1914)",
                        "url": papyrus.SCAN, "licence": "public domain"},
            "wharton": {"cite": WHARTON_CITE, "url": WHARTON_URL, "licence": "public domain",
                        "local_copy": "sources/pg57390-images.html", "sha256": sha256(WHARTON_HTML)},
            "roberts": {"cite": ROBERTS_CITE, "url": ROBERTS_URL, "licence": "public domain"},
            "concordance": {"file": "sources/concordance_wharton_voigt.csv", "numbers_from": concordance.DS_URL,
                            "counts": dict(conc_counts)},
        },
        "papyrus": papyrus.build(),
        "sappho31": sappho31(frags),
        "wharton_fragments": rows,
        "stats": stats,
        "quoters_network": network,
    }


def main() -> dict:
    data = build()
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / "fragments.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    d = main()
    print(json.dumps(d["stats"], ensure_ascii=False, indent=1))
