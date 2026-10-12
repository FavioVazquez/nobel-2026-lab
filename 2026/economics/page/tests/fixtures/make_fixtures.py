"""Copy the two toys' results and INSIGHTS.md into tests/fixtures, marked "fixture", with the long series the page does
not draw left out. Educational demos made to show an open-source tool. Not research.

    python3 tests/fixtures/make_fixtures.py SPEND_TOY_DIR RATE_TOY_DIR
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAMES = {"can-you-predict-spending": "spending.json", "set-the-rate": "set_the_rate.json"}


def main(*toys):
    for toy in map(Path, toys):
        name = NAMES[toy.name]
        out = HERE / toy.name / "results"
        out.mkdir(parents=True, exist_ok=True)
        d = json.loads((toy / "results" / name).read_text(encoding="utf-8"))
        d["status"] = "fixture"
        (d.get("hall") or {}).pop("series", None)
        for c in ((d.get("control") or {}).get("cases") or {}).values():
            c.pop("lambda_hist", None)
        (d.get("control") or {}).pop("hist_bins", None)
        (out / name).write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        shutil.copy(toy / "INSIGHTS.md", HERE / toy.name / "INSIGHTS.md")


if __name__ == "__main__":
    main(*sys.argv[1:3])
