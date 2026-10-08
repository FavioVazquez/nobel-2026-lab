"""One command: python -m shelf.run_all   (writes results/forms.json, results/prize_history.json and the figures)."""
import json
import sys
from collections import OrderedDict
from pathlib import Path

from . import analysis as A
from . import figures as F
from . import style
from . import works as W

RESULTS = Path(__file__).resolve().parents[1] / "results"
STATUS = "final"


def main(argv=None):
    RESULTS.mkdir(exist_ok=True)
    rows = A.forms_table()
    summary = A.forms_summary(rows)
    card = A.float_card()
    hist = A.prize_history()
    bib = A.load_bibliography()
    forms = OrderedDict(
        status=STATUS,
        label=style.LABEL,
        what="Her books by the forms that their own bibliography lines (titles, subtitles, notes) or the Nobel "
             "Committee's essay name. A selection, as the Committee's list is.",
        source=OrderedDict(name=bib["source"], url=bib["url"], accessed=bib["accessed"]),
        selection_note="The Committee heads its list 'Bibliography – a selection'. Counts here are counts of that selection, not of her whole output.",
        tag_rule="Every tag rests on a quoted string: basis 'line' = substring of that entry's bibliography line; "
                 "basis 'committee' = phrase from the Committee's essay on the same page. No tag is our own reading.",
        tags=W.TAGS,
        summary=summary,
        float_22=card,
        works=rows,
    )
    (RESULTS / "forms.json").write_text(json.dumps(forms, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (RESULTS / "prize_history.json").write_text(json.dumps(hist, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    api = A.load_api()
    for theme in ("light", "dark"):
        F.forms_count(rows, summary, RESULTS, theme)
        F.forms_matrix(rows, RESULTS, theme)
        F.float_card(card, RESULTS, theme)
        F.prize_by_decade(hist, RESULTS, theme)
        F.prize_timeline(hist, api, RESULTS, theme)
    print(f"forms: {summary['entries']} entries, {summary['entries_with_no_tag']} untagged; per tag {dict(summary['works_per_tag'])}")
    print(f"22! = {card['orderings_grouped']}")
    tot = hist["totals"]
    print(f"prize: {tot['laureates']} laureates, {tot['women']} women, {tot['years_awarded']} years awarded; "
          f"Canada-born {hist['canada']['field_birth_country']['count']}, 'Canadian author' {hist['canada']['field_press_release_wording']['count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
