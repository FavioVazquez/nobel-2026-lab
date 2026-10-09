"""Download the two pinned UCDP files, check their sha256, write the small derived CSVs: python -m holds.fetch_data"""
import csv
import hashlib
import sys
import urllib.request

from . import constants as C


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(url, path, digest):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "nobel-2026-lab (educational demo)"})
        with urllib.request.urlopen(req, timeout=60) as r:
            path.write_bytes(r.read())
    if sha256(path) != digest:
        sys.exit("sha256 mismatch for %s: %s (expected %s)" % (path.name, sha256(path), digest))


def read_agreements(path=C.PA_RAW):
    import openpyxl

    ws = openpyxl.load_workbook(path, read_only=True)["Dataset"]
    it = ws.iter_rows(values_only=True)
    hdr = next(it)
    rows = [dict(zip(hdr, r)) for r in it if any(v is not None for v in r)]
    return [{k: str(r[k]).strip() for k in C.AGREEMENT_COLUMNS} for r in rows]


def read_active(path=C.TERM_RAW):
    with open(path, newline="", encoding="utf-8") as f:
        return [{k: r[k] for k in C.ACTIVE_COLUMNS} for r in csv.DictReader(f)]


def write(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    fetch(C.PA_URL, C.PA_RAW, C.PA_SHA256)
    fetch(C.TERM_URL, C.TERM_RAW, C.TERM_SHA256)
    write(C.AGREEMENTS, C.AGREEMENT_COLUMNS, read_agreements())
    write(C.ACTIVE, C.ACTIVE_COLUMNS, read_active())
    for p in (C.AGREEMENTS, C.ACTIVE):
        print(p.name, sha256(p))
