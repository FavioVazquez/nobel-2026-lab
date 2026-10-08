"""Refresh the Nobel API snapshot (CC0). Not part of the default build: the build reads the committed snapshot.

    python -m shelf.fetch_api      # writes data/nobel_api_lit_<today>.json (network needed)

Only the fields we use are kept, under their API paths, so the snapshot stays small and checkable.
"""
import datetime as dt
import json
import urllib.request
from pathlib import Path

URL_LAUREATES = "https://api.nobelprize.org/2.1/laureates?nobelPrizeCategory=lit&limit=300"
URL_PRIZES = "https://api.nobelprize.org/2.1/nobelPrizes?nobelPrizeCategory=lit&limit=200"
TERMS = "https://www.nobelprize.org/about/terms-of-use-for-api-nobelprize-org-and-data-nobelprize-org/"
DATA = Path(__file__).resolve().parents[1] / "data"


def _get(d, *keys):
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def trim(laureates_json, prizes_json, fetched):
    laur = []
    for lau in laureates_json["laureates"]:
        for p in lau["nobelPrizes"]:
            if _get(p, "category", "en") != "Literature":
                continue
            laur.append({
                "id": lau["id"],
                "knownName.en": _get(lau, "knownName", "en") or _get(lau, "orgName", "en"),
                "gender": lau.get("gender"),
                "birth.date": _get(lau, "birth", "date"),
                "birth.place.country.en": _get(lau, "birth", "place", "country", "en"),
                "birth.place.countryNow.en": _get(lau, "birth", "place", "countryNow", "en"),
                "nobelPrizes.awardYear": p["awardYear"],
                "nobelPrizes.portion": p.get("portion"),
                "nobelPrizes.motivation.en": _get(p, "motivation", "en"),
            })
    laur.sort(key=lambda r: (int(r["nobelPrizes.awardYear"]), r["id"]))
    prizes = [{
        "awardYear": p["awardYear"],
        "dateAwarded": p.get("dateAwarded"),
        "n_laureates": len(p.get("laureates", [])),
        "laureate_ids": [x["id"] for x in p.get("laureates", [])],
    } for p in prizes_json["nobelPrizes"]]
    return {
        "source": f"Nobel Prize API v2.1, CC0 ({TERMS})",
        "urls": [URL_LAUREATES, URL_PRIZES],
        "fetched": fetched,
        "note": "Trimmed by shelf/fetch_api.py: only the fields used here, keyed by their API path.",
        "meta_counts": {"laureates": laureates_json["meta"]["count"], "nobelPrizes": prizes_json["meta"]["count"]},
        "laureates": laur,
        "nobelPrizes": prizes,
    }


def main():
    def fetch(url):
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.load(r)
    today = dt.date.today().isoformat()
    snap = trim(fetch(URL_LAUREATES), fetch(URL_PRIZES), today)
    out = DATA / f"nobel_api_lit_{today}.json"
    out.write_text(json.dumps(snap, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out} ({len(snap['laureates'])} laureate records, {len(snap['nobelPrizes'])} award years)")


if __name__ == "__main__":
    main()
