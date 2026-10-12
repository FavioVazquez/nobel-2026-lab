"""Check the committed BEA extracts' sha256 and write the small quarterly CSV:
python -m spend.fetch_data            (uses the committed extracts in data/raw/)
python -m spend.fetch_data --refresh  (downloads BEA's bulk NIPA files again, checks their sha256, re-extracts)

The data are BEA's (public domain; the licence line is in constants). Educational demo, not research.
"""
import argparse
import csv
import gzip
import hashlib
import math
import sys
import urllib.request

from . import constants as C

HEADERS = {"User-Agent": "nobel-2026-lab/1.0 (educational demo)", "Accept-Encoding": "gzip"}
HEADER = "%SeriesCode,Period,Value\n"  # the first line of NipaDataQ.txt, kept in each extract


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def url(name):
    return C.BULK_URL.format(name=name)


def raw_path(sid):
    return C.RAW / f"{sid}.csv"


def download(name):
    req = urllib.request.Request(url(name), headers=HEADERS)
    with urllib.request.urlopen(req, timeout=300) as r:
        body = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            body = gzip.decompress(body)
    (C.BULK_DIR / name).write_bytes(body)


def extract():
    """Copy the lines of our series out of NipaDataQ.txt, and their SeriesRegister.txt rows, unchanged except for
    the line endings (BEA's files end lines with CR LF, the extracts with LF)."""
    keep = {sid: [] for sid in C.SERIES}
    with open(C.BULK_DIR / "NipaDataQ.txt", encoding="utf-8", newline="") as f:
        assert f.readline().rstrip("\r\n") + "\n" == HEADER
        for line in f:
            sid = line.split(",", 1)[0]
            if sid in keep:
                keep[sid].append(line.rstrip("\r\n") + "\n")
    for sid, lines in keep.items():
        raw_path(sid).write_text(HEADER + "".join(lines), encoding="utf-8")
    with open(C.BULK_DIR / "SeriesRegister.txt", encoding="utf-8", newline="") as f:
        lines = [ln.rstrip("\r\n") + "\n" for ln in f]
    rows = [lines[0]] + [ln for ln in lines[1:] if ln.split(",", 1)[0] in C.SERIES]
    (C.RAW / C.REGISTER_EXTRACT).write_text("".join(rows), encoding="utf-8")


def check(pairs):
    bad = ["%s: %s (pinned %s)" % (p.name, sha256(p), want) for p, want in pairs if sha256(p) != want]
    if bad:
        sys.exit("sha256 mismatch (BEA may have published a new release since %s):\n  %s"
                 % (C.VINTAGE["release_date"], "\n  ".join(bad)))


def fetch(refresh=False):
    if refresh:
        C.BULK_DIR.mkdir(parents=True, exist_ok=True)
        for name in C.BULK:
            download(name)
        check([(C.BULK_DIR / n, m["sha256"]) for n, m in C.BULK.items()])
        extract()
    check([(raw_path(sid), m["sha256"]) for sid, m in C.SERIES.items()]
          + [(C.RAW / C.REGISTER_EXTRACT, C.REGISTER_EXTRACT_SHA256)])


def read_series(sid):
    """[(quarter, value)] from an extract; BEA writes values with thousands separators ("1,351,397")."""
    with open(raw_path(sid), newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["%SeriesCode", "Period", "Value"], rows[0]
    assert all(r[0] == sid for r in rows[1:])
    return [(q, float(v.replace(",", ""))) for _, q, v in rows[1:]]


def read_register():
    with open(C.RAW / C.REGISTER_EXTRACT, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    head = rows[0]
    return {r[0]: dict(zip(head, r)) for r in rows[1:]}


def quarters_between(first, last):
    y, q = int(first[:4]), int(first[-1])
    out = []
    while True:
        out.append("%dQ%d" % (y, q))
        if out[-1] == last:
            return out
        y, q = (y + 1, 1) if q == 4 else (y, q + 1)


def fisher_relatives(parts):
    """{quarter: Fisher quantity relative from the quarter before} for the aggregate of parts, a list of
    (quantity-index code, current-dollar code) pairs (C.FISHER_FORMULA)."""
    q = [dict(read_series(a)) for a, _ in parts]
    v = [dict(read_series(b)) for _, b in parts]
    quarters = [x for x, _ in read_series(parts[0][0])]
    out = {}
    for prev, t in zip(quarters, quarters[1:]):
        r = [qi[t] / qi[prev] for qi in q]
        lasp = sum(vi[prev] * ri for vi, ri in zip(v, r)) / sum(vi[prev] for vi in v)
        paas = sum(vi[t] for vi in v) / sum(vi[t] / ri for vi, ri in zip(v, r))
        out[t] = math.sqrt(lasp * paas)
    return out


def fisher_level(parts, year=C.REFERENCE_YEAR):
    """{quarter: chained level} in chained `year` dollars (millions): the chained product of the Fisher relatives,
    scaled so that its average over `year` equals the average of the parts' current-dollar values in that year."""
    rel = fisher_relatives(parts)
    quarters = [x for x, _ in read_series(parts[0][0])]
    idx, level = {quarters[0]: 1.0}, 1.0
    for t in quarters[1:]:
        level *= rel[t]
        idx[t] = level
    v = [dict(read_series(b)) for _, b in parts]
    ref = [t for t in quarters if t.startswith(year)]
    scale = sum(sum(vi[t] for vi in v) for t in ref) / sum(idx[t] for t in ref)
    return {t: x * scale for t, x in idx.items()}


def fisher_check():
    """Our Fisher chain of durables, non-durables and services against BEA's own total-PCE quantity index."""
    rel = fisher_relatives(C.FISHER_PARTS["pce_check"])
    bea = dict(read_series("DPCERA"))
    quarters = [x for x, _ in read_series("DPCERA")]
    diff = [abs(math.log(rel[t]) - math.log(bea[t] / bea[p])) for p, t in zip(quarters, quarters[1:])]
    i = max(range(len(diff)), key=diff.__getitem__)
    return {"what": "Fisher chain of DDURRA, DNDGRA, DSERRA (weights DDURRC, DNDGRC, DSERRC) against BEA's DPCERA",
            "max_abs_dlog": diff[i], "at": quarters[i + 1], "mean_abs_dlog": sum(diff) / len(diff),
            "quarters": len(diff), "tolerance": C.FISHER_CHECK_TOL}


def derived_rows():
    nds = fisher_level(C.FISHER_PARTS["nds"])
    pce, dpi, pop = (dict(read_series(sid)) for sid in ("DPCERX", "A067RX", "B230RC"))
    rows = []
    for q in quarters_between(C.FIRST_QUARTER, C.END_QUARTER):
        c, t, y, n = nds[q], pce[q], dpi[q], pop[q]
        # millions of dollars / thousands of people -> dollars per person (chained 2017 dollars, annual rate);
        # the CSV keeps billions, as BEA's tables print them
        rows.append({"quarter": q, "nds_real": "%.3f" % (c / 1e3), "pce_real": "%.3f" % (t / 1e3),
                     "dpi_real": "%.3f" % (y / 1e3), "population": "%d" % n,
                     "log_c_pc": "%.10f" % math.log(c * 1e3 / n), "log_pce_pc": "%.10f" % math.log(t * 1e3 / n),
                     "log_y_pc": "%.10f" % math.log(y * 1e3 / n)})
    return rows


def derive():
    rows = derived_rows()
    with open(C.DERIVED, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=C.DERIVED_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="download BEA's bulk files again and re-extract")
    a = ap.parse_args()
    fetch(a.refresh)
    for sid in C.SERIES:
        print("extract ok:", sid, sha256(raw_path(sid)))
    print("register ok:", C.REGISTER_EXTRACT, sha256(C.RAW / C.REGISTER_EXTRACT))
    print("derived:", C.DERIVED.name, derive(), "quarters,", sha256(C.DERIVED))
