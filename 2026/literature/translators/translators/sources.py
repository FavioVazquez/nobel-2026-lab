"""Read the stored public-domain excerpts and turn them into lines and word tokens.

Every string we show is cut out of a stored excerpt (data/sources/), which is a verbatim byte slice of a Project
Gutenberg file. The only normalisation is the one a browser makes when it renders HTML: tags removed, HTML entities
decoded, every run of white space shown as one space. `rendered()` does exactly that and nothing else; the tests
check every displayed string against it.
"""
from __future__ import annotations

import hashlib
import html
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SRC = HERE / "data" / "sources"

WHARTON_URL = "https://www.gutenberg.org/cache/epub/57390/pg57390-images.html"
WHARTON_SHA256 = "bf616822d86ef89b75aa0ee68698568a81a9f3620edf642af73daaa4545cb247"
SMOLLETT_URL = "https://www.gutenberg.org/cache/epub/4085/pg4085.txt"
SMOLLETT_SHA256 = "048e86bf69c08655ff92423c7b7d04c8110481521bf901acda0df932aa53b17c"

# Excerpt file -> (source URL, first and last line of the slice in the full Gutenberg file, sha256 of the full file)
EXCERPTS = {
    "wharton_pg57390_fr2.html": (WHARTON_URL, 2291, 2519, WHARTON_SHA256),
    "wharton_pg57390_fr40.html": (WHARTON_URL, 3315, 3352, WHARTON_SHA256),
    "smollett_pg4085_ch40.txt": (SMOLLETT_URL, 8957, 9022, SMOLLETT_SHA256),
}


def raw(name: str) -> str:
    return (SRC / name).read_bytes().decode("utf-8")


def rendered(fragment: str) -> str:
    """What a browser shows for an HTML fragment: no tags, entities decoded, white space runs collapsed."""
    text = re.sub(r"<[^>]+>", "", fragment)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def paragraphs(name: str) -> list[dict]:
    """Every <p>...</p> of an excerpt, in order, with its rendered text and its line number inside the excerpt."""
    s = raw(name)
    out = []
    for m in re.finditer(r"<p\b([^>]*)>(.*?)</p>", s, flags=re.S):
        line = s.count("\n", 0, m.start()) + 1
        out.append({"attrs": m.group(1), "inner": m.group(2), "text": rendered(m.group(2)), "excerpt_line": line})
    return out


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --------------------------------------------------------------------------------------------------------------
# Tokens
# --------------------------------------------------------------------------------------------------------------
# A word is a run of letters (any script, with combining marks), inner apostrophes or hyphens, an elided final
# apostrophe (Greek δ', ἔτ', ὄρημ') or a leading one ('Twas, 'πιδεύης). Square brackets mark editors' supplements in
# Wharton's Greek and are kept on the token as a flag. Punctuation is not a word.
APOS = "'’᾽"  # straight apostrophe, right single quote, Greek koronis
WORD = re.compile(
    r"\[?[" + APOS + r"]?[^\W\d_](?:[\w" + APOS + r"\-]*[^\W\d_])?[" + APOS + r"]?\]?", flags=re.U
)


def tokens_of(text: str) -> list[dict]:
    toks = []
    for m in WORD.finditer(text):
        surface = m.group(0)
        bracketed = surface.startswith("[") or surface.endswith("]")
        word = surface.strip("[]")
        toks.append({"surface": word, "start": m.start() + (1 if surface.startswith("[") else 0), "bracketed": bracketed})
    return toks


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)
