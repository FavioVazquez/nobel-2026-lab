"""Greek text helpers: normalisation and the word-counting rule.

Counting rule (documented in the README):
  * The text is Unicode NFC.
  * A word is a maximal run of Greek letters (U+0370-03FF, U+1F00-1FFF, with combining marks), plus an
    elision mark that ends it (', ’, ᾽) so that δ' counts as one word.
  * A word split across two printed lines with a hyphen ("φωνεύ-" / "σας") counts once.
  * Words inside Wharton's square brackets (his "uncertain" words) count; they are also counted on their own
    so a reader can subtract them.
  * Metrical signs (- v ∪ ×), dots, Latin letters, digits and punctuation do not count.
"""
from __future__ import annotations

import re
import unicodedata

GREEK_LETTER = r"[Ͱ-Ͽἀ-῿̀-ͯ]"
# a Greek word may start with an apostrophe of prodelision ('πιδεύης) and end with an elision mark
WORD_RE = re.compile(r"['’᾽]?(?:%s)+['’᾽]?" % GREEK_LETTER)
# letters only (to reject runs made only of combining marks or Greek punctuation)
HAS_LETTER_RE = re.compile(r"[Α-Ωα-ωϜϝἀ-ῼΪ-ΰϊ-ώΆ-Ώ]")
NON_LETTERS = set("ʹ͵;·΄΅")


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def join_hyphenated(lines: list[str]) -> str:
    """Join printed lines; a line ending in a hyphen joins the next line's first word without a space."""
    out = ""
    for ln in lines:
        ln = ln.strip()
        if out.endswith("-"):
            out = out[:-1] + ln
        else:
            out = (out + " " + ln) if out else ln
    return out


def greek_words(text: str) -> list[str]:
    words = []
    for m in WORD_RE.finditer(nfc(text)):
        w = m.group(0)
        if HAS_LETTER_RE.search(w):
            words.append(w)
    return words


def count_words(lines: list[str]) -> dict:
    """Return {'words': n, 'words_in_brackets': k, 'tokens': [...]} for a fragment's printed Greek lines."""
    joined = join_hyphenated(lines)
    tokens = greek_words(joined)
    # words inside [...]
    bracketed = 0
    for seg in re.findall(r"\[([^\]]*)\]", joined):
        bracketed += len(greek_words(seg))
    return {"words": len(tokens), "words_in_brackets": bracketed, "tokens": tokens}
