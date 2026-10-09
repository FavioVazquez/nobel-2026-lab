"""Copy the two toys' results and INSIGHTS.md into tests/fixtures, marked "fixture", with the curves the page does not
draw left out. Educational demos made to show an open-source tool. Not research.

    python3 tests/fixtures/make_fixtures.py ENDS_TOY_DIR HOLD_TOY_DIR
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main(ends, hold):
    for toy, name in ((Path(ends), "how_conflicts_end.json"), (Path(hold), "do_agreements_hold.json")):
        out = HERE / toy.name / "results"
        out.mkdir(parents=True, exist_ok=True)
        d = json.loads((toy / "results" / name).read_text(encoding="utf-8"))
        d["status"] = "fixture"
        for clock in ("main", "strict"):
            for k, g in (d.get(clock) or {}).get("groups", {}).items():
                if k != "All":
                    g.pop("curve", None)
            for k in ("without_settled_late", "first_agreement_per_linked_group"):
                for g in (d.get(clock) or {}).get(k, {}).values():
                    if isinstance(g, dict):
                        g.pop("curve", None)
        (out / name).write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        shutil.copy(toy / "INSIGHTS.md", HERE / toy.name / "INSIGHTS.md")


if __name__ == "__main__":
    main(*sys.argv[1:3])
