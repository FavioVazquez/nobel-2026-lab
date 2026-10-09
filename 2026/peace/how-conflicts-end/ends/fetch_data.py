"""Download the pinned UCDP file, check its sha256, write the small derived CSV: python -m ends.fetch_data"""
import csv
import hashlib
import sys
import urllib.request

from . import constants as C


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch():
    C.RAW.parent.mkdir(parents=True, exist_ok=True)
    if not C.RAW.exists():
        req = urllib.request.Request(C.DATA_URL, headers={"User-Agent": "nobel-2026-lab (educational demo)"})
        with urllib.request.urlopen(req, timeout=60) as r:
            C.RAW.write_bytes(r.read())
    got = sha256(C.RAW)
    if got != C.DATA_SHA256:
        sys.exit("sha256 mismatch for %s: %s (expected %s)" % (C.RAW.name, got, C.DATA_SHA256))
    return C.RAW


def derive():
    with open(C.RAW, newline="", encoding="utf-8") as f:
        rows = [{k: r[k] for k in C.DERIVED_COLUMNS} for r in csv.DictReader(f)]
    with open(C.DERIVED, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=C.DERIVED_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    fetch()
    print("raw ok:", C.RAW.name, C.DATA_SHA256)
    print("derived:", C.DERIVED.name, derive(), "rows,", sha256(C.DERIVED))
