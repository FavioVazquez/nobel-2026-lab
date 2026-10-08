"""Resolve the hand-made alignment, compare the two passes, and count.

Counts are OUR ROUGH COUNT, NOT A QUALITY SCORE: they depend on our tokens, our alignment rules and our reading.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import lsj
from .lemmas import LEMMA

HERE = Path(__file__).resolve().parent.parent
DATA = HERE / "data"
SCOPE_LINES = range(1, 17)  # Greek lines 1-16: the four full stanzas
LABEL = "our rough count, not a quality score"


def _index(version: dict) -> dict:
    """'line:word#k' -> token id, for every word token of a version."""
    idx = {}
    seen = {}
    for t in version["tokens"]:
        key = (t["line"], t["word"])
        seen[key] = seen.get(key, 0) + 1
        idx[f"{t['line']}:{t['word']}#{seen[key]}"] = t["id"]
        if seen[key] == 1:
            idx[f"{t['line']}:{t['word']}"] = t["id"]
    # a bare 'line:word' is only allowed when the word occurs once on that line
    for (line, word), n in seen.items():
        if n > 1:
            idx.pop(f"{line}:{word}", None)
    return idx


def resolve(pass_data: dict, versions: dict) -> dict:
    """Turn refs into token ids. Raises on any ref that does not point at exactly one existing token."""
    gids = {t["id"] for t in versions["greek"]["tokens"]}
    out = {}
    for v in versions["versions"]:
        idx = _index(v)
        links = {}
        for gid, entry in pass_data["versions"].get(v["id"], {}).items():
            if gid not in gids:
                raise KeyError(f"{v['id']}: unknown Greek token {gid}")
            refs, strength = entry[0], entry[1]
            note = entry[2] if len(entry) > 2 else None
            if strength not in ("close", "loose"):
                raise ValueError(f"{v['id']} {gid}: strength {strength}")
            ids = []
            for r in refs:
                if r not in idx:
                    raise KeyError(f"{v['id']} {gid}: ref {r!r} matches no single token")
                ids.append(idx[r])
            links[gid] = {"to": ids, "strength": strength, **({"note": note} if note else {})}
        out[v["id"]] = links
    return out


def compare(a: dict, b: dict) -> list[dict]:
    """Every (version, Greek token) where the two passes differ in target words or strength."""
    diffs = []
    for vid in sorted(set(a) | set(b)):
        for gid in sorted(set(a.get(vid, {})) | set(b.get(vid, {})), key=_gkey):
            x, y = a.get(vid, {}).get(gid), b.get(vid, {}).get(gid)
            xs = (sorted(x["to"]), x["strength"]) if x else None
            ys = (sorted(y["to"]), y["strength"]) if y else None
            if xs != ys:
                diffs.append({"version": vid, "greek": gid, "pass1": xs, "pass2": ys})
    return diffs


def _gkey(gid: str):
    _, l, k = gid.split(":")
    return (int(l), int(k))


def in_scope(t: dict) -> bool:
    return t["line"] in SCOPE_LINES


def counts(versions: dict, links: dict) -> dict:
    greek = [t for t in versions["greek"]["tokens"] if in_scope(t)]
    out = {"label": LABEL, "scope": "Greek lines 1-16 (four stanzas) as printed by Wharton", "versions": {}}
    for v in versions["versions"]:
        L = links[v["id"]]
        stanzas_present = sorted({ln["stanza"] for ln in v["lines"] if ln.get("text")} & {1, 2, 3, 4})
        g_scope = [t for t in greek if t["stanza"] in stanzas_present]
        carried = [t["id"] for t in g_scope if t["id"] in L]
        close = [g for g in carried if L[g]["strength"] == "close"]
        vwords = [t for t in v["tokens"] if t["stanza"] in stanzas_present]
        linked = {tid for g in L.values() for tid in g["to"]}
        added = [t for t in vwords if t["id"] not in linked]
        moved = [g for g in carried if any(_stanza_of(v, tid) != _gstanza(g) for tid in L[g]["to"])]
        out["versions"][v["id"]] = {
            "translator": v["translator"], "year": v["year"],
            "greek_stanzas_compared": stanzas_present,
            "greek_words_in_scope": len(g_scope),
            "greek_words_carried": len(carried),
            "carried_close": len(close),
            "carried_loose": len(carried) - len(close),
            "greek_words_dropped": len(g_scope) - len(carried),
            "version_words": len(vwords),
            "words_added": len(added),
            "greek_words_moved_to_another_stanza": len(moved),
            "added_words": [t["word"] for t in added],
            "dropped_greek": [t["word"] for t in g_scope if t["id"] not in L],
        }
    return out


def _gstanza(gid: str) -> int:
    return (int(gid.split(":")[1]) - 1) // 4 + 1


def _stanza_of(v: dict, tid: str) -> int:
    for t in v["tokens"]:
        if t["id"] == tid:
            return t["stanza"]
    raise KeyError(tid)


def glosses() -> dict:
    """Greek token id -> LSJ headword (Unicode, from the beta-code key), LSJ's own translation phrase(s) and anchor."""
    store = lsj.load()
    chosen = json.loads((DATA / "glosses.json").read_text(encoding="utf-8"))
    out = {}
    for gid, (key, form_note) in LEMMA.items():
        e = store["entries"][key]
        g = chosen["glosses"][key]
        out[gid] = {"lemma": lsj.beta_to_unicode(key), "lsj_key": key, "gloss": g["gloss"],
                    "form_note": form_note, "lsj_file": e["file"], "lsj_line": e["line"], "lsj_id": e["id"]}
    return out
