"""Wharton (= Bergk) number -> Voigt number: how we built the lookup table.

Step 1 (automatic proposal). The Digital Sappho (https://digitalsappho.org/, CC BY-SA 4.0) prints each fragment's
Greek under its Voigt/Campbell number. We fetch those pages once (`python -m sapphofrag.fetch_digitalsappho`, cached in
work/, never committed) and, for every Wharton fragment printed as verse, look for the Digital Sappho fragment that
shares the most Greek words with it (accents, breathings and case removed; words of 3+ letters).
Step 2 (hand check). Every proposal is accepted, corrected or rejected by hand in HAND (below), using the Digital
Sappho page and the Wikipedia articles named there. Rows we could not settle stay empty: a gap, shown as "?".

The committed result is sources/concordance_wharton_voigt.csv. Only numbers are taken from these pages, never text.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from html import unescape
from pathlib import Path

GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")


def strip_marks(s: str) -> str:
    d = unicodedata.normalize("NFD", s)
    d = "".join(ch for ch in d if unicodedata.category(ch) != "Mn")
    return d.lower().replace("ς", "σ").replace("ϝ", "")


def word_set(text: str) -> set[str]:
    words = re.findall(r"[α-ωϲ]+", strip_marks(text))
    return {w for w in words if len(w) >= 3}


def parse_ds_page(path: Path) -> dict[str, str]:
    """Return {voigt_label: greek_text} for one cached Digital Sappho page."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    # main text only: between the page title block and the comments
    lines = [unescape(x).strip() for x in re.sub(r"<[^>]+>", "\n", raw).split("\n")]
    lines = [x for x in lines if x and x != "&nbsp;" and x != "\xa0"]
    slug = path.stem.replace("pg_", "")
    m = re.fullmatch(r"fr(\d+[a-z]?)", slug)
    default = m.group(1) if m else None
    rng = re.fullmatch(r"fr(\d+)-(\d+)", slug)
    lo, hi = (int(rng.group(1)), int(rng.group(2))) if rng else (None, None)
    out: dict[str, str] = {}
    cur = default
    for i, ln in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        mm = re.fullmatch(r"(\d+)([a-z]?)", ln)
        if mm and not nxt.startswith("Leave a comment"):
            if default is not None and mm.group(1) == re.sub(r"[a-z]", "", default):
                cur = ln
            elif lo is not None and lo <= int(mm.group(1)) <= hi:
                cur = ln
            continue
        greek = len(GREEK_RE.findall(ln))
        if cur and greek >= 3 and greek >= 0.5 * len(re.sub(r"\W", "", ln)):
            out[cur] = (out.get(cur, "") + " " + ln).strip()
    return out


def load_ds(cache_dir: Path) -> dict[str, str]:
    allfr: dict[str, str] = {}
    for p in sorted(cache_dir.glob("pg_fr*.html")):
        for k, v in parse_ds_page(p).items():
            allfr[k] = (allfr.get(k, "") + " " + v).strip()
    return allfr


def propose(wharton_frags: list[dict], ds: dict[str, str]) -> list[dict]:
    ds_sets = {k: word_set(v) for k, v in ds.items()}
    rows = []
    for f in wharton_frags:
        if f["greek_layout"] != "verse":
            continue
        ws = word_set(" ".join(f["greek_lines"]))
        best, score, shared = None, 0.0, set()
        for k, s in ds_sets.items():
            inter = ws & s
            if not inter:
                continue
            sc = len(inter) / max(1, len(ws))
            if sc > score or (sc == score and best and len(s) < len(ds_sets[best])):
                best, score, shared = k, sc, inter
        rows.append({"wharton_no": f["wharton_no"], "proposed_voigt": best, "share": round(score, 2),
                     "n_shared": len(shared), "n_words": len(ws)})
    return rows


def load_table(path: Path) -> dict[int, dict]:
    with open(path, encoding="utf-8") as fh:
        return {int(r["wharton_no"]): r for r in csv.DictReader(l for l in fh if not l.startswith("#"))}


# Hand pass (2026-10-08). value: (voigt_no or "", status, note). status: "hand" = checked by eye against the
# Digital Sappho page, "probable" = likely but the Greek differs, "gap" = not settled; "auto" rows are not listed
# here: they are the automatic proposals with share >= 0.75 and >= 3 shared words, each looked at once by eye.
DS_URL = "https://digitalsappho.org/fragments/"
HAND: dict[int, tuple[str, str, str]] = {
    1: ("1", "hand", "Ode to Aphrodite; also Wikipedia 'Sappho 1'"),
    2: ("31", "hand", "also Wikipedia 'Sappho 31'"),
    5: ("2", "hand", "Wharton 5 = the last stanza of Voigt 2 (Voigt 2.13-16)"),
    12: ("", "gap", "not found on Digital Sappho fr. 26 page; left open"),
    13: ("16", "hand", "Wharton 13 = Voigt 16.3-4, the papyrus poem in part (a)"),
    14: ("41", "hand", "same words, different spelling"),
    15: ("26", "hand", "Digital Sappho fr. 26: 'ἔγω δ' ἐμ' αὔτᾳ τοῦτο σύνοιδα'"),
    17: ("37", "hand", "same words"),
    18: ("123", "hand", "same words"),
    20: ("152", "hand", "same words, different spelling"),
    21: ("129a", "hand", "Digital Sappho prints 129 (a)"),
    22: ("129b", "hand", "Digital Sappho prints 129 (b)"),
    23: ("", "gap", "two words only; no safe match"),
    24: ("45", "hand", "same words"),
    26: ("", "gap", "Wharton (after Athenaeus) says the verses are not Sappho's"),
    32: ("147", "hand", "same words"),
    35: ("", "gap", "no match found"),
    38: ("", "gap", "no match found"),
    42: ("47", "hand", "same words"),
    44: ("101", "hand", "same words, corrupt in both"),
    46: ("", "gap", "no match found"),
    47: ("178", "hand", "Digital Sappho: '178 Campbell ( = Voigt ...)'"),
    48: ("144", "hand", "same words"),
    49: ("", "gap", "no match found"),
    52: ("154", "hand", "Voigt 154 line 1"),
    53: ("154", "hand", "Voigt 154 line 2"),
    54: ("", "gap", "no match found"),
    55: ("", "gap", "no match found"),
    61: ("153", "hand", "same words"),
    63: ("168", "hand", "same words"),
    66: ("", "gap", "no match found"),
    68: ("55", "hand", "same words, different spelling"),
    71: ("", "gap", "no match found"),
    73: ("", "gap", "no match found"),
    75: ("121", "hand", "same words"),
    77: ("91", "hand", "same words; 'Εἴρανα' for Wharton's 'ὦ ῎ραννα'"),
    78: ("81", "hand", "same words"),
    79: ("", "gap", "no match found"),
    82: ("124", "hand", "same words"),
    88: ("135", "hand", "same words; 'Εἴρανα' for 'ὦ ῎ραννα'"),
    96: ("", "gap", "no match found"),
    107: ("", "gap", "no match found"),
    108: ("", "gap", "no match found"),
    110: ("", "gap", "no match found"),
    111: ("165", "hand", "same words"),
    113: ("146", "hand", "same words"),
    114: ("145", "hand", "same words"),
    115: ("38", "hand", "same words"),
    116: ("119", "hand", "same words, different spelling"),
    118: ("", "gap", "epigram (Greek Anthology); not on Digital Sappho"),
    119: ("", "gap", "epigram (Greek Anthology); not on Digital Sappho"),
    120: ("", "gap", "epigram (Greek Anthology); not on Digital Sappho"),
    126: ("163", "hand", "same words"),
    133: ("104b", "hand", "same words"),
    137: ("", "gap", "prose paraphrase in Aristotle; no match"),
    142: ("", "gap", "no match found"),
    153: ("157", "hand", "same words"),
    167: ("", "gap", "no match found"),
    # single words cited in prose (Wharton's Miscellaneous): Digital Sappho page fr169-192 lists them in Voigt's
    # alphabetical order with two explicit anchors ('178 Campbell (= Voigt ...)', '185 Campbell'); numbers counted
    # along that list.
    125: ("172", "probable", "ἀλγεσίδωρον, 4th word after 169A"),
    128: ("191", "probable", "σέλιννοις"),
    129: ("185", "hand", "μελίφωνοι, '185 Campbell' anchor"),
    131: ("170", "probable", "Αἴγα"),
    149: ("171", "probable", "ἄκακος"),
    150: ("173", "probable", "ἀμαμάξυδος"),
    151: ("174", "probable", "ἀμάρα"),
    154: ("176", "probable", "βάρωμος"),
    155: ("177", "probable", "βεῦδος"),
    156: ("179", "probable", "γρύτα"),
    157: ("180", "probable", "Ἔκτωρ (Voigt)"),
    158: ("181", "probable", "ζάβατον"),
    159: ("182", "probable", "ἰοίην; Wharton prints ἀγαγοίην"),
    160: ("183", "probable", "κατώρη / κατάρης"),
    161: ("184", "probable", "κίνδυν"),
    162: ("186", "probable", "Μήδεϊα"),
    164: ("187", "probable", "Μοισάων"),
    165: ("189", "probable", "νίτρον"),
    166: ("190", "probable", "πολυίδριδι"),
}


def build_rows(wharton_frags: list[dict], ds: dict[str, str]) -> list[dict]:
    props = {r["wharton_no"]: r for r in propose(wharton_frags, ds)}
    rows = []
    for f in wharton_frags:
        n = f["wharton_no"]
        p = props.get(n)
        if n in HAND:
            v, status, note = HAND[n]
        elif p and p["proposed_voigt"] and p["share"] >= 0.75 and p["n_shared"] >= 3:
            v, status = p["proposed_voigt"], "auto"
            note = "shares %d of %d words (3+ letters, marks removed)" % (p["n_shared"], p["n_words"])
        else:
            v, status, note = "", "gap", "no Greek verse to match" if f["greek_layout"] != "verse" else "no match"
        rows.append({"wharton_no": n, "voigt_no": v, "status": status, "note": note,
                     "source": DS_URL if v else ""})
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("# Wharton (= Bergk) -> Voigt concordance, built by sapphofrag.concordance (see its docstring).\n")
        fh.write("# Numbers only, from The Digital Sappho (https://digitalsappho.org/, CC BY-SA 4.0), checked by hand.\n")
        fh.write("# status: auto | hand | probable | gap. An empty voigt_no is a gap.\n")
        w = csv.DictWriter(fh, fieldnames=["wharton_no", "voigt_no", "status", "note", "source"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
