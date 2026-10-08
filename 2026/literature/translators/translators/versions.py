"""The Greek text and the six versions, cut from the stored excerpts, with tokens and anchors.

Writes results/versions.json. Nothing here is typed by hand except which paragraphs of the excerpt belong to which
version (paragraph indices below, checked by the tests against the attribution line Wharton prints under each).
"""
from __future__ import annotations

import json
import re

from . import sources as S

FR2 = "wharton_pg57390_fr2.html"
FR40 = "wharton_pg57390_fr40.html"
FR2_START_PAGE = 64   # last page marker before the excerpt in the full file is {64} (line 2274)
FR40_START_PAGE = 96  # last page marker before the excerpt in the full file is {96} (line 3300)

# Greek stanzas: Wharton prints 17 lines; four Sapphic stanzas (4 lines each) and the first line of a fifth.
GREEK_STANZA = {n: (n - 1) // 4 + 1 for n in range(1, 18)}

# Paragraph indices inside the fr. 2 excerpt (see paragraphs()).
P_GREEK = list(range(1, 18))
P_WHARTON_PROSE = 18
P_CATULLUS = list(range(20, 32))      # 12 paragraphs: 7 lines, the asterisk row (a lost line), 4 lines
P_PHILIPS = list(range(58, 74))
P_PHILIPS_CREDIT = 74


def _page_at(name: str, excerpt_line: int, start_page: int) -> int:
    """Page of the printed book: the last Gutenberg page marker ({64}, {65} ...) on or before this line."""
    page = start_page
    for ln in S.raw(name).split("\n")[:excerpt_line]:
        for m in re.finditer(r'id="page(\d+)"', ln):
            page = int(m.group(1))
    return page


def paragraphs(name: str) -> list[dict]:
    """Paragraphs with page-number markers ({64}) removed: they are Gutenberg's margin page numbers, not text."""
    out = []
    for p in S.paragraphs(name):
        inner = re.sub(r'<span class="pagenum"[^>]*>.*?</span>', "", p["inner"], flags=re.S)
        out.append({**p, "inner": inner, "text": S.rendered(inner)})
    return out


def _credit_paragraph_index(paras: list[dict], startswith: str) -> int:
    for i, p in enumerate(paras):
        if p["text"].startswith(startswith):
            return i
    raise KeyError(startswith)


def _verse_block(paras, idxs, name, start_page, stanza_len=4, lacuna_text=None):
    lines, n = [], 0
    for i in idxs:
        p = paras[i]
        if lacuna_text is not None and p["text"] == lacuna_text:
            n += 1
            lines.append({"n": n, "text": None, "lacuna": True, "source_text": p["text"],
                          "anchor": {"excerpt_line": p["excerpt_line"], "page": _page_at(name, p["excerpt_line"], start_page)}})
            continue
        n += 1
        lines.append({"n": n, "text": p["text"], "stanza": (n - 1) // stanza_len + 1,
                      "anchor": {"excerpt_line": p["excerpt_line"], "page": _page_at(name, p["excerpt_line"], start_page)}})
    for ln in lines:
        ln.setdefault("stanza", (ln["n"] - 1) // stanza_len + 1)
    return lines


def tokenise(vid: str, lines: list[dict]) -> list[dict]:
    """Word tokens with ids "<version>:<line>:<k>". A word split over two lines by a hyphen (φωνεύ- / σας) is one token
    whose id is on the first line and which records both parts."""
    toks = []
    pending = None
    for ln in lines:
        if not ln.get("text"):
            continue
        ws = S.tokens_of(ln["text"])
        k = 0
        for j, w in enumerate(ws):
            if pending is not None and j == 0:
                pending["parts"].append({"line": ln["n"], "start": w["start"], "surface": w["surface"]})
                pending["word"] = pending["word"] + w["surface"]
                pending = None
                continue
            k += 1
            t = {"id": f"{vid}:{ln['n']}:{k}", "line": ln["n"], "stanza": ln["stanza"], "word": w["surface"],
                 "parts": [{"line": ln["n"], "start": w["start"], "surface": w["surface"]}]}
            if w["bracketed"]:
                t["bracketed"] = True
            toks.append(t)
            end = w["start"] + len(w["surface"])
            if j == len(ws) - 1 and ln["text"][end:end + 1] == "-" and ln["text"].rstrip().endswith("-"):
                pending = t
    return toks


def prose_lines(text: str, cuts: list[str]) -> list[dict]:
    """Wharton's prose is one paragraph. We cut it where each Greek stanza ends (our cut, at his punctuation); the
    pieces joined by single spaces give back his paragraph exactly (tested)."""
    out, rest, n = [], text, 0
    for c in cuts:
        i = rest.index(c) + len(c)
        n += 1
        out.append({"n": n, "text": rest[:i].strip(), "stanza": n})
        rest = rest[i:]
    if rest.strip():
        n += 1
        out.append({"n": n, "text": rest.strip(), "stanza": n})
    return out


MERRILL = "crosscheck/lawikisource_catullus51_merrill.wiki"
MERRILL_URL = "https://la.wikisource.org/w/index.php?title=Carmina_(Catullus,_ed._Merrill)/Carmen_LI&oldid=279690"


def merrill_stanza4() -> list[dict]:
    """Catullus 51, lines 13-16 (his own closing stanza, which Wharton does not quote), from E. T. Merrill's edition
    (1893) as transcribed on Latin Wikisource (revision 279690). Copied verbatim from the stored page source."""
    s = S.raw(MERRILL)
    body = s[s.index("<poem>") + len("<poem>"): s.index("</poem>")]
    out = []
    lines = s.split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.startswith("Otium, Catulle"))
    for k in range(4):
        text = lines[start + k].strip()
        assert text in body
        out.append({"n": 13 + k, "text": text, "stanza": 4, "source": "merrill",
                    "anchor": {"file": "data/sources/" + MERRILL, "line_in_file": start + k + 1, "url": MERRILL_URL}})
    return out


def build() -> dict:
    paras = paragraphs(FR2)
    p40 = paragraphs(FR40)

    greek_lines = []
    for n, i in enumerate(P_GREEK, start=1):
        p = paras[i]
        greek_lines.append({"n": n, "text": p["text"], "stanza": GREEK_STANZA[n],
                            "anchor": {"excerpt_line": p["excerpt_line"], "page": _page_at(FR2, p["excerpt_line"], FR2_START_PAGE)}})

    prose_p = paras[P_WHARTON_PROSE]
    m = re.match(r"\s*<i>(.*?)</i>", prose_p["inner"], flags=re.S)
    prose_text = S.rendered(m.group(1))
    prose = prose_lines(prose_text, [
        "thy sweet speech",                               # end of Greek stanza 1 (ὑπακούει)
        "I have no utterance left,",                      # end of stanza 2 (οὐδὲν ἔτ' εἴκει)
        "my ears ring,",                                  # end of stanza 3 (ἐπιρρόμβεισι δ' ἄκουαι)
        "little better than one dead.",                   # end of stanza 4 (φαίνομαι [ἄλλα])
    ])
    for ln in prose:
        ln["anchor"] = {"excerpt_line": prose_p["excerpt_line"], "page": _page_at(FR2, prose_p["excerpt_line"], FR2_START_PAGE)}

    catullus = _verse_block(paras, P_CATULLUS, FR2, FR2_START_PAGE, lacuna_text="* * * * *")
    for ln in catullus:
        ln["source"] = "wharton"
    catullus += merrill_stanza4()
    philips = _verse_block(paras, P_PHILIPS, FR2, FR2_START_PAGE)
    i_sm = _credit_paragraph_index(paras, "Thy fatal shafts unerring move,")
    smollett = _verse_block(paras, range(i_sm, i_sm + 16), FR2, FR2_START_PAGE)
    # Merivale's first line repeats Philips's; find the second occurrence.
    occ = [i for i, p in enumerate(paras) if p["text"] == "Blest as the immortal gods is he,"]
    i_me = occ[1]
    merivale = _verse_block(paras, range(i_me, i_me + 16), FR2, FR2_START_PAGE)
    i_sy = _credit_paragraph_index(paras, "Peer of gods he seemeth to me, the blissful")
    symonds = _verse_block(paras, range(i_sy, i_sy + 16), FR2, FR2_START_PAGE)

    credits = {
        "philips": paras[P_PHILIPS_CREDIT]["text"],
        "smollett": paras[i_sm + 16]["text"],
        "merivale": paras[i_me + 16]["text"],
        "symonds": paras[i_sy + 16]["text"],
        "catullus": paras[19]["text"],
        "wharton": None,
    }

    # fr. 40 (γλυκύπικρον)
    g40 = [p for p in p40 if re.search(r"[Ͱ-Ͽἀ-῿]", p["text"])]
    w40 = next(p for p in p40 if p["text"].startswith("Now Love"))
    s40 = [p for p in p40 if p["text"].startswith(("Lo, Love", "The bitter-sweet", "Wild-beast-like"))]
    s40_credit = next(p for p in p40 if p["text"].startswith("J. Addington Symonds"))

    wharton_meta = {
        "title": "Sappho: Memoir, Text, Selected Renderings and a Literal Translation, by Henry Thornton Wharton",
        "edition": "5th edition, London: John Lane, 1908 (1st edition David Stott, 1885); Greek text after Bergk (Poetae Lyrici Graeci, 4th ed., Leipzig 1882), as Wharton's preface says",
        "gutenberg": "Project Gutenberg eBook #57390 (released 25 June 2018)",
        "url": S.WHARTON_URL,
        "sha256_full_file": S.WHARTON_SHA256,
    }

    def src(name, extra=None):
        url, a, b, sha = S.EXCERPTS[name]
        d = {"url": url, "excerpt_file": f"data/sources/{name}", "lines_in_full_file": [a, b], "sha256_full_file": sha}
        if extra:
            d.update(extra)
        return d

    out = {
        "status": None,
        "note": "Educational demos made to show an open-source tool. Not research. Every text is public domain and is "
                "cut from the stored excerpt named in 'source'; 'rendered' text = HTML tags and Gutenberg page-number "
                "markers removed, entities decoded, white space runs shown as one space.",
        "wharton_book": wharton_meta,
        "greek": {
            "id": "greek",
            "label": "Sappho, the Greek text as printed by Wharton (his fr. 2; Voigt 31)",
            "numbering": {"wharton_bergk": "2", "voigt": "31"},
            "date": "c. 600 BC (poem); this text: Bergk 1882 as printed by Wharton 1908",
            "language": "grc",
            "source": src(FR2, {"pages": [64, 65]}),
            "lines": greek_lines,
        },
        "versions": [
            {"id": "catullus", "translator": "Catullus", "full_name": "Gaius Valerius Catullus", "poem": "Catullus 51 (Ad Lesbiam): lines 1-12 as quoted by Wharton (line 8 is lost in the manuscripts); lines 13-16, his own closing stanza, from Merrill's edition (1893) via Latin Wikisource",
             "year": -55, "date_label": "1st c. BC (Catullus lived c. 84 - c. 54 BC)", "language": "lat", "kind": "Latin version",
             "wharton_calls_it": credits["catullus"], "source": src(FR2, {"pages": [65, 66]}),
             "source_lines_13_16": {"url": MERRILL_URL, "file": "data/sources/" + MERRILL,
                                    "edition": "E. T. Merrill, Catullus (1893), as transcribed on Latin Wikisource"},
             "lines": catullus},
            {"id": "philips", "translator": "Ambrose Philips", "year": 1711, "date_label": "1711", "language": "eng",
             "kind": "version (Addison, 1711, printed it as the \"English Translation\")", "wharton_credit": credits["philips"],
             "source": src(FR2, {"pages": [67]}), "lines": philips},
            {"id": "smollett", "translator": "Tobias Smollett", "year": 1748, "date_label": "1748", "language": "eng",
             "kind": "version (a love song in his novel Roderick Random that Wharton prints among the renderings of this ode)",
             "wharton_credit": credits["smollett"], "source": src(FR2, {"pages": [68]}), "lines": smollett},
            {"id": "merivale", "translator": "John Herman Merivale", "year": 1833, "date_label": "1833", "language": "eng",
             "kind": "version", "wharton_credit": credits["merivale"], "source": src(FR2, {"pages": [68, 69]}), "lines": merivale},
            {"id": "symonds", "translator": "John Addington Symonds", "year": 1883, "date_label": "1883", "language": "eng",
             "kind": "version (made for Wharton's book, per Wharton's preface)", "wharton_credit": credits["symonds"],
             "source": src(FR2, {"pages": [69]}), "lines": symonds},
            {"id": "wharton", "translator": "Henry Thornton Wharton", "year": 1885, "date_label": "1885 (text as printed in the 5th edition, 1908)",
             "language": "eng", "kind": "literal prose translation", "wharton_credit": None,
             "source": src(FR2, {"pages": [65]}), "full_text": prose_text, "lines": prose},
        ],
        "fr40": {
            "numbering": {"wharton_bergk": "40", "voigt": "130"},
            "greek_lines": [{"n": i + 1, "text": p["text"], "anchor": {"excerpt_line": p["excerpt_line"], "page": FR40_START_PAGE}} for i, p in enumerate(g40)],
            "wharton_prose": {"text": w40["text"], "anchor": {"excerpt_line": w40["excerpt_line"], "page": FR40_START_PAGE}},
            "symonds": {"lines": [{"n": i + 1, "text": p["text"], "anchor": {"excerpt_line": p["excerpt_line"], "page": FR40_START_PAGE}} for i, p in enumerate(s40)],
                        "credit": s40_credit["text"]},
            "source": src(FR40, {"pages": [96]}),
        },
    }
    out["greek"]["tokens"] = tokenise("greek", greek_lines)
    for v in out["versions"]:
        v["tokens"] = tokenise(v["id"], v["lines"])
    return out


def write(path, status: str) -> dict:
    data = build()
    data["status"] = status
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return data
