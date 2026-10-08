"""Glosses from LSJ (Liddell-Scott-Jones, A Greek-English Lexicon, 9th ed. 1940) in the Perseus digital edition.

Licence: CC BY-SA 4.0. "Text provided under a CC BY-SA license by Perseus Digital Library, http://www.perseus.tufts.edu,
with funding from The National Endowment for the Humanities. Data accessed from https://github.com/PerseusDL/lexica/
[2026-10-08]." The excerpt we store (data/lsj_entries.json) is therefore CC BY-SA 4.0 too.

`extract()` needs the 27 Perseus XML files (about 300 MB, not in this repo): set LSJ_DIR to their folder. It copies the
raw XML of each entry we use, byte for byte, into data/lsj_entries.json. Everything else (the glosses we show, the
tests) reads only that stored excerpt.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
STORE = HERE / "data" / "lsj_entries.json"
LSJ_REPO = "https://github.com/PerseusDL/lexica/tree/master/CTS_XML_TEI/perseus/pdllex/grc/lsj"
LSJ_COMMIT = "56061ca127f4a2844980baffc5f2b6d1332897b3"  # master on 2026-10-08
CREDIT = ("Text provided under a CC BY-SA license by Perseus Digital Library, http://www.perseus.tufts.edu, with "
          "funding from The National Endowment for the Humanities. Data accessed from https://github.com/PerseusDL/lexica/ "
          "[2026-10-08].")

PREFIX = 12000  # we store the first 12,000 characters of each entry, verbatim (the senses we quote are in them)
ENTRY = re.compile(r'<entryFree\b[^>]*?key="([^"]+)"[^>]*>.*?</entryFree>', re.S)


def _files(lsj_dir: Path):
    return sorted(lsj_dir.glob("grc.lsj.perseus-eng*.xml"), key=lambda p: int(re.search(r"eng(\d+)", p.name).group(1)))


def _phrase_re(phrase: str):
    return re.compile(r"(?<![A-Za-z])" + r"(?:\s|<[^>]+>)*".join(re.escape(w) for w in phrase.split()) + r"(?![A-Za-z])")


def has_phrase(entry: dict, phrase: str) -> bool:
    """True if the phrase is in the stored verbatim text of the entry (its prefix or one of its stored windows)."""
    rx = re.compile(r"(?<![A-Za-z])" + re.escape(phrase) + r"(?![A-Za-z0-9])")
    return any(rx.search(plain(x)) for x in [entry["xml"]] + [w["xml"] for w in entry.get("windows", [])])


def extract(keys: list[str], lsj_dir: str | None = None, phrases: dict | None = None) -> dict:
    """phrases: key -> gloss phrase; if the phrase is not in the stored prefix, a verbatim window around its first
    occurrence in the full entry is stored too (with its character offset)."""
    lsj_dir = Path(lsj_dir or os.environ["LSJ_DIR"])
    want = set(keys)
    found = {}
    for f in _files(lsj_dir):
        s = f.read_text(encoding="utf-8")
        for m in ENTRY.finditer(s):
            k = m.group(1)
            if k in want and k not in found:
                line = s.count("\n", 0, m.start()) + 1
                idm = re.search(r'\bid="([^"]+)"', m.group(0)[:400])
                xml = m.group(0)
                found[k] = {"file": f.name, "line": line, "id": idm.group(1) if idm else None,
                            "xml_length": len(xml), "sha256": hashlib.sha256(xml.encode("utf-8")).hexdigest(),
                            "xml": xml[:PREFIX], "truncated": len(xml) > PREFIX}
    for k, phs in (phrases or {}).items():
        e = found.get(k)
        for ph in ([phs] if isinstance(phs, str) else phs):
            if e is None or has_phrase(e, ph):
                continue
            full = _full_entry(lsj_dir, e)
            m = _phrase_re(ph).search(full)
            if m:
                a, b = max(0, m.start() - 1500), min(len(full), m.end() + 300)
                e.setdefault("windows", []).append({"offset": a, "xml": full[a:b]})
    missing = sorted(want - set(found))
    return {"credit": CREDIT, "repo": LSJ_REPO, "commit": LSJ_COMMIT, "entries": found, "missing": missing}


def _full_entry(lsj_dir: Path, e: dict) -> str:
    s = (lsj_dir / e["file"]).read_text(encoding="utf-8")
    start = 0
    for _ in range(e["line"] - 1):
        start = s.index("\n", start) + 1
    i = s.index("<entryFree", start)
    return s[i:i + e["xml_length"]]


def plain(xml: str) -> str:
    """Entry text with tags removed and white space collapsed (Greek stays in Perseus beta code)."""
    t = re.sub(r"<[^>]+>", "", xml)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def translations(xml: str) -> list[str]:
    """The phrases LSJ itself marks as translations (<tr>), in order."""
    return [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m))).strip()
            for m in re.findall(r"<tr\b[^>]*>(.*?)</tr>", xml, flags=re.S)]


# ---------------------------------------------------------------------------------------------------------------
# Beta code -> Unicode (Perseus convention: letters, then breathing ) (, accents / \ =, iota subscript |, diaeresis +;
# capitals marked * with diacritics before the letter). Enough for headwords.
# ---------------------------------------------------------------------------------------------------------------
_LET = dict(zip("abgdezhqiklmncoprstufxyw", "αβγδεζηθικλμνξοπρστυφχψω"))
_DIA = {")": "̓", "(": "̔", "/": "́", "\\": "̀", "=": "͂", "|": "ͅ", "+": "̈"}


def beta_to_unicode(b: str) -> str:
    b = re.sub(r"[\d^_]+$", "", b).replace("^", "").replace("_", "")  # homonym numbers (kai/1), vowel-length marks
    out, i = [], 0
    while i < len(b):
        c = b[i]
        if c == "*":
            j = i + 1
            marks = ""
            while j < len(b) and b[j] in _DIA:
                marks += b[j]
                j += 1
            out.append(_LET[b[j].lower()].upper() + "".join(_DIA[m] for m in sorted(marks, key="()+/\\=|".index)))
            i = j + 1
            continue
        if c.lower() in _LET:
            out.append(_LET[c.lower()])
        elif c in _DIA:
            out.append(_DIA[c])
        elif c == "'":
            out.append("’")
        else:
            out.append(c)
        i += 1
    s = "".join(out)
    # final sigma
    s = re.sub(r"σ(?=$|[^\ẁ-ͯ])", "ς", s)
    return unicodedata.normalize("NFC", s)


def load() -> dict:
    return json.loads(STORE.read_text(encoding="utf-8"))
