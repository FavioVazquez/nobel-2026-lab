"""Fetch The Digital Sappho fragment pages (1 request per second) into work/digitalsappho/ and rebuild the
concordance CSV. Only needed to re-derive sources/concordance_wharton_voigt.csv; the build does not need it."""
from __future__ import annotations

import re
import time
import urllib.request
from pathlib import Path

from . import concordance, wharton
from .paths import ROOT, SOURCES

UA = "nobel-2026-lab/0.1 (educational, non-commercial)"
CACHE = ROOT / "work" / "digitalsappho"


def get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    index = get(concordance.DS_URL + "fr1/")
    urls = sorted(set(re.findall(r'href="(https://digitalsappho.org/fragments/[^"]+)"', index)))
    for u in urls:
        slug = u.rstrip("/").rsplit("/", 1)[-1]
        out = CACHE / ("pg_%s.html" % slug)
        if not out.exists():
            out.write_text(get(u), encoding="utf-8")
            time.sleep(1)
    ds = concordance.load_ds(CACHE)
    rows = concordance.build_rows(wharton.parse(SOURCES / "pg57390-images.html"), ds)
    concordance.write_csv(rows, SOURCES / "concordance_wharton_voigt.csv")
    print("wrote", SOURCES / "concordance_wharton_voigt.csv")


if __name__ == "__main__":
    main()
