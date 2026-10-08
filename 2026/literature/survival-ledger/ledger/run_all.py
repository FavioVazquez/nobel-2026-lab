"""One command: python -m ledger.run_all   (writes results/ledger.json and the figures, about 10 seconds)."""
import json
import sys
from collections import OrderedDict
from pathlib import Path

from . import figures as F
from . import rows as R
from . import style

RESULTS = Path(__file__).resolve().parents[1] / "results"
STATUS = "final"


def src(keys):
    out = []
    for k in keys:
        name, url, anchor, quote, how = R.SOURCES[k]
        if k in R.PARAPHRASED:  # Suda On Line, World History Encyclopedia: our paraphrase, not a quote (CC BY-NC-SA)
            out.append(OrderedDict(key=k, name=name, url=url, anchor=anchor, quote=None, paraphrase=quote,
                                   accessed=R.ACCESSED))
        else:
            out.append(OrderedDict(key=k, name=name, url=url, anchor=anchor, quote=quote, accessed=R.ACCESSED))
    return out


def field(f):
    if f is None:
        return None
    o = OrderedDict()
    for k in ("value", "range", "open_ended", "unit", "text", "notes"):
        if k in f:
            o[k] = f[k]
    o["source"] = src(f["sources"])
    return o


def build():
    rows = []
    for r in R.ROWS:
        o = OrderedDict(
            id=r["id"], author=r["author"], language=r["language"],
            named_by_committee=OrderedDict(phrase=r["committee_phrase"],
                                           where=r.get("committee_phrase_where", "essay"),
                                           source=src(["BIO"])[0]["url"]),
            dates=OrderedDict(text=r["dates"]["text"], source=src(r["dates"]["sources"])),
            unit=r["unit"],
            ancient_count=field(r["ancient_count"]),
            modern_estimate=field(r["modern_estimate"]),
            survives=field(r["survives"]),
        )
        if r["ancient_count"] is None:
            o["ancient_count_note"] = r.get("ancient_count_note")
            o["ancient_count_note_source"] = src(r.get("ancient_count_sources", []))
        if r["modern_estimate"] is None:
            o["modern_estimate_note"] = r.get("modern_estimate_note")
        if "ancient_book1" in r:
            o["ancient_book1"] = field(r["ancient_book1"])
        if r.get("shelf"):
            o["shelf"] = r["shelf"]
        if r.get("grid"):
            o["grid"] = r["grid"]
        rows.append(o)
    return OrderedDict(
        status=STATUS,
        label=style.LABEL,
        what="How much survives of the ancient authors the Nobel Committee names in its 2026 bio-bibliography. "
             "Ancient testimony and modern estimates kept apart, as ranges, each with its sources.",
        reading_rules=[
            "Ancient counts are testimony (the Suda is a 10th-century Byzantine encyclopedia), not measurements.",
            "Ranges mean the sources disagree; we never pick one number inside a range.",
            "No single 'percentage lost'. The Sappho grid is labelled 'estimate' and names both totals.",
            "'Survives complete' differs by author: Thucydides is unfinished; Sappho's one complete poem is short.",
        ],
        rows=rows,
        unverified=R.UNVERIFIED,
        resolved_open_items=R.RESOLVED_OPEN_ITEMS,
        sources_checked="results/source_check.json (python -m ledger.check_sources)",
    )


def main(argv=None):
    RESULTS.mkdir(exist_ok=True)
    led = build()
    (RESULTS / "ledger.json").write_text(json.dumps(led, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    sappho = next(r for r in R.ROWS if r["id"] == "sappho")
    for theme in ("light", "dark"):
        F.shelf(R.ROWS, RESULTS, theme)
        F.sappho_grid(sappho, RESULTS, theme)
    print(f"ledger: {len(led['rows'])} rows, {len(R.SOURCES)} sources, {len(R.UNVERIFIED)} unverified items left out")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
