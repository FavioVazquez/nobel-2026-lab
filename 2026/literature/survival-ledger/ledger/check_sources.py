"""Re-fetch every source page and check that its stored quote is still in the text (network needed).

    python -m ledger.check_sources        # writes results/source_check.json

Wikipedia pages are read as wikitext (action=raw) and archive.org scans as their OCR text, so links and markup are
stripped before matching; curly quotes and dashes are folded to plain ones. A quote that only matches with all spaces
removed (OCR line breaks) is reported as "found (spaces ignored)". Sources in PARAPHRASED (Suda On Line) carry our
paraphrase, not a quote: for them every key word must be on the page ("found (key words)").
"""
import datetime as dt
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

from .rows import PARAPHRASED, SOURCES

UA = "Mozilla/5.0 (nobel-2026-lab source check)"
OUT = Path(__file__).resolve().parents[1] / "results" / "source_check.json"


def norm(t):
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-"),
                 ("\xa0", " ")):
        t = t.replace(a, b)
    t = re.sub(r"''+", "", t)
    t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", t)
    t = t.replace("{{nbsp}}", " ")
    t = re.sub(r"-\s+", "-", t)
    return re.sub(r"\s+", " ", t)


def fetch_url(url):
    if "en.wikipedia.org/wiki/" in url:
        return "https://en.wikipedia.org/w/index.php?title=" + url.split("/wiki/")[1] + "&action=raw"
    if "archive.org/details/" in url:
        ident = url.split("/details/")[1]
        return f"https://archive.org/download/{ident}/{ident}_djvu.txt"
    return url


def main():
    cache, out = {}, {}
    for key, (name, url, anchor, quote, how) in SOURCES.items():
        if not quote:
            continue
        f = fetch_url(url)
        if f not in cache:
            cache[f] = ""
            for attempt in range(3):  # some publishers refuse a request now and then: try again after a pause
                try:
                    req = urllib.request.Request(f, headers={"User-Agent": UA})
                    with urllib.request.urlopen(req, timeout=60) as r:
                        cache[f] = norm(r.read().decode("utf-8", "replace"))
                    break
                except Exception as e:  # noqa: BLE001
                    print(f"{key}: could not fetch ({e}), attempt {attempt + 1} of 3", file=sys.stderr)
                    time.sleep(5)
        text, q = cache[f], norm(quote)
        if key in PARAPHRASED:
            ok = text and all(norm(w) in text for w in PARAPHRASED[key])
            status = "found (key words)" if ok else ("NOT FOUND" if text else "page not fetched")
        elif q in text:
            status = "found"
        elif q.replace(" ", "") in text.replace(" ", ""):
            status = "found (spaces ignored)"
        else:
            status = "NOT FOUND" if text else "page not fetched"
        out[key] = {"url": url, "fetched_as": f, "status": status}
        print(f"{key:18s} {status}")
    OUT.write_text(json.dumps({"checked": dt.date.today().isoformat(), "results": out}, indent=1) + "\n",
                   encoding="utf-8")
    bad = [k for k, v in out.items() if not v["status"].startswith("found")]
    print(f"{len(out) - len(bad)} of {len(out)} quotes found" + (f"; check: {bad}" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
