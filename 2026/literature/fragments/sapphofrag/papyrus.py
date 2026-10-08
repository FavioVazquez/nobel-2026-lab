"""P.Oxy. 1231 fr. 1 col. i 13-34 (Sappho 16 Voigt) as printed by Grenfell & Hunt (1914): lines -> spans.

The 1914 signs (G&H's own, before the Leiden conventions of 1931-2 were agreed, but the same for these marks):
  [abc]   letters lost where the papyrus is gone; what stands inside is the editors' restoration (a guess)
  [. . .] letters lost and not restored; each dot is about one letter
  . . .   (outside brackets) traces of ink the editors could not read
  ⟨a⟩     a letter the scribe left out, added by the editors
A line may open a bracket and never close it: the loss runs to the end of the line.

Each line becomes a list of spans {text, kind, mark}: kind is "read" (on the papyrus and read by G&H), "restored"
(editors' letters inside [ ] or ⟨ ⟩) or "lost" (dots, or an empty bracket). The span texts, joined, give back the
printed line exactly (tests check this).
"""
from __future__ import annotations

import re
import unicodedata

from .paths import SOURCES

TSV = SOURCES / "poxy1231_fr1_col1_13-34.tsv"
TRANSLATION = SOURCES / "poxy1231_translation_1914.txt"
SCAN = "https://archive.org/details/oxyrhynchuspapyr10gren"
LEAF_URL = ("https://archive.org/download/oxyrhynchuspapyr10gren/oxyrhynchuspapyr10gren_jp2.zip/"
            "oxyrhynchuspapyr10gren_jp2%2Foxyrhynchuspapyr10gren_{leaf:04d}.jp2")
PAGE_TO_LEAF = {23: 47, 25: 49, 40: 64}
DOTS_RE = re.compile(r"\.(?: \.)+ ?")


def load_lines() -> list[dict]:
    rows = []
    for raw in TSV.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith("#"):
            continue
        ln, page, text = raw.split("\t")
        rows.append({"line": int(ln), "page": int(page), "text": text})
    return rows


def load_translation() -> str:
    lines = [x for x in TRANSLATION.read_text(encoding="utf-8").splitlines() if x and not x.startswith("#")]
    assert len(lines) == 1
    return lines[0]


def _split_inside(text: str) -> list[tuple[str, str]]:
    """Split the inside of a square bracket into (piece, kind): dot runs are lost, the rest restored."""
    out = []
    pos = 0
    for m in DOTS_RE.finditer(text):
        if m.start() > pos:
            out.append((text[pos:m.start()], "restored"))
        out.append((m.group(0), "lost"))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:], "restored"))
    return out


def spans(line: str) -> list[dict]:
    out: list[dict] = []

    def add(text, kind, mark=None):
        if not text:
            return
        if out and out[-1]["kind"] == kind and out[-1]["mark"] == mark and kind == "read":
            out[-1]["text"] += text
        else:
            out.append({"text": text, "kind": kind, "mark": mark})

    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch == "[":
            j = line.find("]", i + 1)
            closed = j != -1
            inner = line[i + 1:j] if closed else line[i + 1:]
            pieces = _split_inside(inner)
            if not pieces:
                pieces = [("", "lost")]
            # brackets travel with the first and last piece
            pieces[0] = ("[" + pieces[0][0], pieces[0][1])
            if closed:
                pieces[-1] = (pieces[-1][0] + "]", pieces[-1][1])
            for k, (t, kind) in enumerate(pieces):
                out.append({"text": t, "kind": kind, "mark": "[]" if closed else "[ (open to line end)"})
            i = (j + 1) if closed else n
        elif ch == "⟨":
            j = line.index("⟩", i)
            out.append({"text": line[i:j + 1], "kind": "restored", "mark": "⟨⟩"})
            i = j + 1
        else:
            m = DOTS_RE.match(line, i)
            if m and (i == 0 or line[i - 1] == " "):
                out.append({"text": m.group(0), "kind": "lost", "mark": "dots (traces, unread)"})
                i = m.end()
            else:
                add(ch, "read")
                i += 1
    return out


def letter_count(text: str) -> int:
    """Greek letters in a string (base letters, after removing marks); dots count as one lost letter each."""
    base = unicodedata.normalize("NFD", text)
    return sum(1 for c in base if "Α" <= c <= "ω" or c in "ϝς")


def dot_count(text: str) -> int:
    return text.count(".") if DOTS_RE.search(text) else 0


def build() -> dict:
    lines = load_lines()
    out_lines = []
    tot = {"read": 0, "restored": 0, "added": 0, "lost_dots": 0}
    for row in lines:
        sp = spans(row["text"])
        for s in sp:
            if s["kind"] == "read":
                tot["read"] += letter_count(s["text"])
            elif s["kind"] == "restored" and s["mark"] == "⟨⟩":
                tot["added"] += letter_count(s["text"])
            elif s["kind"] == "restored":
                tot["restored"] += letter_count(s["text"])
            else:
                tot["lost_dots"] += s["text"].count(".")
        out_lines.append({
            "line": row["line"],
            "text": row["text"],
            "spans": sp,
            "anchor": {"edition": "Grenfell & Hunt, The Oxyrhynchus Papyri X (1914), no. 1231 fr. 1 col. i",
                       "page": row["page"], "line": row["line"],
                       "scan": LEAF_URL.format(leaf=PAGE_TO_LEAF[row["page"]])},
        })
    return {
        "title": "P.Oxy. 1231 fr. 1 col. i 13-34 = Sappho fr. 16 Voigt (= Wharton 13, in part)",
        "printed_by": "B. P. Grenfell and A. S. Hunt, The Oxyrhynchus Papyri, Part X (London, 1914), pp. 23, 25",
        "source_url": SCAN,
        "transcription": "typed by hand from the page images, second pass character by character (2026-10-08)",
        "lines": out_lines,
        "letters": tot,
        "english_1914": {
            "text": load_translation(),
            "translator": "B. P. Grenfell and A. S. Hunt (1914), literal prose",
            "anchor": {"page": 40, "note": "13-34", "scan": LEAF_URL.format(leaf=64)},
            "bracketed": "[Verily the wills of mortals are easily bent when they are moved by vain thoughts.]",
            "bracket_meaning": "G&H's own brackets: their rendering of a conjectured restoration of lines 25-6",
        },
    }
