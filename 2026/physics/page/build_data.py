"""Build page/data.js from the two Physics experiments' results (educational demo, toy models; not research).

Reads ../kilometre/results (kilometre_summary.json plus its curve CSVs) and ../telescope/results
(telescope_summary.json, example_event.json and a sensor-geometry CSV). Writes data.js, a plain script that
sets window.NOBEL_PHYS_DATA, so index.html works from file:// with no server and no network.
Every number the page states comes from here; nothing is typed into index.html.
Python 3 standard library only.

    python3 build_data.py                                  # from 2026/physics/page/: ../kilometre, ../telescope
    python3 build_data.py --from /abs/km/results /abs/telescope/results   # results folders anywhere
    python3 build_data.py --fixtures                       # the placeholder inputs in tests/fixtures
    python3 build_data.py --out /tmp/data.js               # write somewhere else

It prints the status of each input ("final", "preliminary", "fixture" or "missing"). The page shows a
visible "preliminary" banner unless both inputs are "final".
"""
import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KM_DEFAULT = HERE.parent / "kilometre" / "results"
TEL_DEFAULT = HERE.parent / "telescope" / "results"
FIXTURES = HERE / "tests" / "fixtures"
KM_FILE, TEL_FILE, EVENT_FILE = "kilometre_summary.json", "telescope_summary.json", "example_event.json"
TAG = "Educational demo, toy models. Not research."
GITHUB = "https://github.com/FavioVazquez/nobel-2026-lab/tree/main/2026/physics/"


def sig(x, n=4):
    return None if x is None else float(f"{float(x):.{n}g}")


def read_csv(path):
    """Rows of a CSV whose comment lines start with '#'; column names lower-cased and stripped."""
    lines = [l for l in path.read_text().splitlines() if l.strip() and not l.lstrip().startswith("#")]
    rows = list(csv.DictReader(lines))
    return [{k.strip().lower(): v.strip() for k, v in r.items() if k} for r in rows]


def col(cols, pattern, exclude=None):
    for c in cols:
        if re.search(pattern, c) and not (exclude and re.search(exclude, c)):
            return c
    return None


def num(v):
    try:
        f = float(v)
        return f if math.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def energy_gev(name, v):
    """Energy in GeV from a column value; the column name says log10 and/or TeV/PeV/EeV."""
    if "log" in name:
        v = 10 ** v
    for unit, f in (("eev", 1e9), ("pev", 1e6), ("tev", 1e3)):
        if unit in name:
            return v * f
    return v


def find_curve(folder, x_pat, y_pat, y_exclude=None, prefer=None):
    """First CSV in `folder` with an x column matching x_pat and a y column matching y_pat.
    `prefer` picks among several y columns (e.g. the 1 PeV one). Returns (path, xname, yname, rows)."""
    for p in sorted(folder.glob("*.csv")):
        try:
            rows = read_csv(p)
        except (OSError, csv.Error, UnicodeDecodeError):
            continue
        if not rows:
            continue
        cols = list(rows[0].keys())
        x = col(cols, x_pat)
        ys = [c for c in cols if c != x and re.search(y_pat, c) and not (y_exclude and re.search(y_exclude, c))]
        if x and ys:
            y = next((c for c in ys if prefer and re.search(prefer, c)), ys[0])
            return p, x, y, rows
    return None


def interaction_curve(folder):
    """Chance to interact in 1 km of ice against energy. Prefers a "mean" (neutrino and antineutrino) column,
    which is what the experiment's headline p_interact_1km uses."""
    hit = find_curve(folder, r"energ|^e_|^e$|log10", r"^p_|p_?int|interact|prob|chance", y_exclude=r"err|unc", prefer=r"mean|avg|all")
    if not hit:
        return None
    p, x, y, rows = hit
    pts = sorted((energy_gev(x, num(r[x])), num(r[y])) for r in rows if num(r[x]) is not None and num(r[y]) is not None)
    pts = [q for q in pts if 1e3 * 0.999 <= q[0] <= 1e7 * 1.001 and q[1] > 0]
    return {"energy_GeV": [sig(e) for e, _ in pts], "p": [sig(v) for _, v in pts], "column": y, "file": p.name} if len(pts) > 2 else None


def zenith_of(name):
    """Zenith in degrees from a column name like 'zenith_150deg', 'theta_120' or 'cosz_-0.5'."""
    m = re.search(r"(cos[a-z]*)_?(-?\d+(?:\.\d+)?)", name)
    if m and "cos" in m.group(1):
        return math.degrees(math.acos(max(-1.0, min(1.0, float(m.group(2))))))
    m = re.search(r"(?:zen[a-z]*|theta|angle)_?(\d+(?:\.\d+)?)", name)
    return float(m.group(1)) if m else None


def species_of(path, column=""):
    t = (path.stem + " " + column).lower()
    head = " ".join(l for l in path.read_text().splitlines()[:5] if l.lstrip().startswith("#")).lower()
    if "mean of nu_mu and nu_mu-bar" in head:  # the kilometre CSV says so in its comment line, whatever its name
        return "mean"
    if "numubar" in t:
        return "numubar"
    return "numu" if "numu" in t else ("mean" if "mean" in t else None)


def transmission_curve(folder):
    """Transmission at 1 PeV against zenith (deg; 90 = horizontal, 180 = straight up through the Earth).
    Accepts one column per energy (picks the 1 PeV one) or a long table with an energy column."""
    for p in sorted(folder.glob("*.csv")):
        try:
            rows = read_csv(p)
        except (OSError, csv.Error, UnicodeDecodeError):
            continue
        if not rows:
            continue
        cols = list(rows[0].keys())
        ecol = col(cols, r"energ|^e_|^e$|log10", exclude=r"trans|surv")
        zcols = [(zenith_of(c), c) for c in cols if c != ecol and zenith_of(c) is not None]
        if ecol and len(zcols) > 2 and ("trans" in p.stem.lower() or "surv" in p.stem.lower()):
            # wide format: one row per energy, one column per zenith; take the row at 1 PeV
            er = [(energy_gev(ecol, num(r[ecol])), r) for r in rows if num(r[ecol])]
            if not er:
                continue
            e, row = min(er, key=lambda q: abs(math.log10(q[0]) - 6))
            if abs(math.log10(e) - 6) > 0.05:
                continue
            pts = sorted((z, num(row[c])) for z, c in zcols if num(row[c]) is not None and 90 - 1e-6 <= z <= 180 + 1e-6)
            if len(pts) > 2:
                return {"zenith_deg": [sig(a) for a, _ in pts], "T": [sig(t) for _, t in pts], "species": species_of(p),
                        "energy_GeV": sig(e), "file": p.name}
            continue
        x = col(cols, r"zen|angle|cos|nadir|theta")
        ys = [c for c in cols if c != x and re.search(r"trans|surv", c)]
        if not x or not ys:
            continue
        ecol = col(cols, r"energ|^e_|^e$|log10", exclude=r"trans|surv")
        if ecol:  # long format: keep the rows nearest 1 PeV
            es = sorted({energy_gev(ecol, num(r[ecol])) for r in rows if num(r[ecol])})
            if not es:
                continue
            best = min(es, key=lambda e: abs(math.log10(e) - 6))
            if abs(math.log10(best) - 6) > 0.05:
                continue
            rows = [r for r in rows if num(r[ecol]) and abs(energy_gev(ecol, num(r[ecol])) - best) < 1e-6 * best]
            y = ys[0]
        else:
            y = next((c for c in ys if re.search(r"1_?pev|1e6|1000_?tev|1e\+06", c)), None)
            if y is None and len(ys) > 1:
                continue
            y = y or ys[0]
        pts = []
        for r in rows:
            a, t = num(r[x]), num(r[y])
            if a is None or t is None:
                continue
            if "cos" in x:
                a = math.degrees(math.acos(max(-1.0, min(1.0, a))))
            elif "nadir" in x:
                a = 180 - a
            pts.append((a, t))
        pts = sorted(q for q in pts if 90 - 1e-6 <= q[0] <= 180 + 1e-6)
        if len(pts) > 2:
            return {"zenith_deg": [sig(a) for a, _ in pts], "T": [sig(t) for _, t in pts], "species": species_of(p, y), "file": p.name}
    return None


def size_curve(folder):
    hit = find_curve(folder, r"side|size|edge|length|^l_|^l$", r"event|rate|per_?y")
    if not hit:
        return None
    p, x, y, rows = hit
    f = 1000.0 if "km" in x else 1.0
    pts = sorted((num(r[x]) * f, num(r[y])) for r in rows if num(r[x]) is not None and num(r[y]) is not None)
    pts = [q for q in pts if q[0] > 0 and q[1] > 0]
    return {"side_m": [sig(s) for s, _ in pts], "events": [sig(v) for _, v in pts], "file": p.name} if len(pts) > 2 else None


def kilometre_block(folder):
    f = folder / KM_FILE
    if not f.exists():
        return {"status": "missing", "source": str(folder)}, None
    d = json.loads(f.read_text())
    out = {k: d.get(k) for k in ("p_interact_1km", "one_in_N_100TeV", "earth_survival_vertical", "events_per_year",
                                 "hese_check", "label", "units")}
    per = (d.get("details") or {}).get("earth_survival_vertical_per_species") or {}
    out["earth_survival_vertical_per_species"] = {k: {e: sig(v, 3) for e, v in per[k].items()} for k in per}
    out["curves"] = {"interaction": interaction_curve(folder), "transmission_1PeV": transmission_curve(folder),
                     "size": size_curve(folder)}
    return {"status": d.get("status", "unknown"), "source": str(folder)}, out


def geometry(folders, hint=None):
    """index -> (x, y, z) and the string positions, from the first CSV with index/string/x/y/z columns."""
    cands = []
    for folder in folders:
        if hint:
            cands += [folder / hint]
        cands += sorted(folder.glob("*.csv")) + sorted((folder / "data").glob("*.csv"))
    seen = set()
    for p in cands:
        if p in seen or not p.is_file():
            continue
        seen.add(p)
        try:
            rows = read_csv(p)
        except (OSError, csv.Error, UnicodeDecodeError):
            continue
        if not rows:
            continue
        cols = list(rows[0].keys())
        i, s = col(cols, r"^(index|idx|sensor|sensor_index|i)$"), col(cols, r"^(string|str|string_id)$")
        x, y, z = col(cols, r"^x"), col(cols, r"^y"), col(cols, r"^z")
        if not (s and x and y and z):
            continue
        pos, strings = {}, {}
        for k, r in enumerate(rows):
            xyz = (num(r[x]), num(r[y]), num(r[z]))
            if None in xyz:
                continue
            pos[int(float(r[i])) if i else k] = xyz
            strings.setdefault(int(float(r[s])), []).append(xyz[:2])
        sxy = [[sig(sum(a for a, _ in v) / len(v), 5), sig(sum(b for _, b in v) / len(v), 5)] for _, v in sorted(strings.items())]
        return pos, sxy, p.name
    return None, None, None


def event_block(folder):
    f = folder / EVENT_FILE
    if not f.exists():
        return None
    e = json.loads(f.read_text())
    hint = str(e.get("geometry", "")).split(" ")[0] or None
    pos, sxy, gname = geometry([folder.parent, folder], hint)
    if e.get("sensor_xyz"):  # positions given inside the event file win
        pos = {int(k): tuple(v) for k, v in e["sensor_xyz"].items()}
    if not pos:
        print(f"warning: no sensor-geometry CSV next to {f}; the example event is left out")
        return None
    hits = []
    for h in e["hits"]:
        p = pos.get(int(h[0]))
        if p is None:
            continue
        hits.append([sig(p[0], 5), sig(p[1], 5), sig(p[2], 5), float(h[1]), sig(h[2] if len(h) > 2 else 1, 3)])
    t0 = min((h[3] for h in hits), default=0.0)
    for h in hits:  # times in ns after the first hit
        h[3] = sig(h[3] - t0, 5)
    hits.sort(key=lambda h: h[3])
    v5 = lambda v: [sig(x, 5) for x in v] if v else None
    return {"strings_xy": sxy or [], "hits": hits, "n_hits_file": len(e["hits"]),
            "track": {"point": v5(e["track"]["point"]), "dir": v5(e["track"]["dir"])},
            "line_fit_dir": v5(e["line_fit_dir"]), "pandel_fit_dir": v5(e["pandel_fit_dir"]),
            "line_fit_point": v5(e.get("line_fit_point")), "pandel_fit_point": v5(e.get("pandel_fit_point")),
            "error_deg": {k: sig(v, 3) for k, v in e.get("error_deg", {}).items()}, "how_chosen": e.get("how_chosen"),
            "geometry_file": gname, "file": f.name}


def telescope_block(folder):
    f = folder / TEL_FILE
    if not f.exists():
        return {"status": "missing", "source": str(folder)}, None
    d = json.loads(f.read_text())
    out = {k: d.get(k) for k in ("spacings_m", "median_error_deg", "p68_error_deg", "p16_error_deg", "p84_error_deg",
                                 "median_hits", "trigger_fraction", "n_strings", "icecube_real", "events_per_point",
                                 "tracks_generated_per_point", "label")}
    out["muon_energy_GeV"] = (d.get("model") or {}).get("muon_energy_gev")
    out["event"] = event_block(folder)
    return {"status": d.get("status", "unknown"), "source": str(folder)}, out


def classify(paths):
    """--from takes results folders (or the summary files in them) in any order."""
    km = tel = None
    for p in paths:
        p = Path(p).expanduser().resolve()
        folder = p.parent if p.is_file() else p
        if (folder / KM_FILE).exists() or "kilometre" in str(folder):
            km = folder
        elif (folder / TEL_FILE).exists() or "telescope" in str(folder):
            tel = folder
        else:
            sys.exit(f"--from: {p} holds neither {KM_FILE} nor {TEL_FILE}")
    return km, tel


def build(km_dir, tel_dir):
    km_in, km = kilometre_block(km_dir)
    tel_in, tel = telescope_block(tel_dir)
    statuses = [km_in["status"], tel_in["status"]]
    return {
        "tag": TAG,
        "preliminary": any(s != "final" for s in statuses),
        "placeholder": any(s in ("fixture", "missing") for s in statuses),
        "inputs": {"kilometre": km_in["status"], "telescope": tel_in["status"]},
        "readmes": {"kilometre": GITHUB + "kilometre", "telescope": GITHUB + "telescope", "glashow": GITHUB + "glashow",
                    "page": GITHUB + "page"},
        "km": km, "tel": tel,
    }, km_in, tel_in


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from", dest="src", nargs="+", metavar="DIR", help="results folders of the two experiments")
    ap.add_argument("--fixtures", action="store_true", help="build from the placeholder inputs in tests/fixtures")
    ap.add_argument("--out", type=Path, default=HERE / "data.js")
    a = ap.parse_args(argv)
    km_dir, tel_dir = KM_DEFAULT, TEL_DEFAULT
    if a.fixtures:
        km_dir, tel_dir = FIXTURES / "kilometre" / "results", FIXTURES / "telescope" / "results"
    if a.src:
        k, t = classify(a.src)
        km_dir, tel_dir = k or km_dir, t or tel_dir
    data, km_in, tel_in = build(km_dir, tel_dir)
    for name, d, block in (("kilometre", km_in, data["km"]), ("telescope", tel_in, data["tel"])):
        extra = ""
        if name == "kilometre" and block:
            extra = "; curves: " + ", ".join(f"{k}={'yes (' + v['file'] + ')' if v else 'no'}" for k, v in block["curves"].items())
        if name == "telescope" and block:
            ev = block["event"]
            extra = f"; example event: {'yes, ' + str(len(ev['hits'])) + ' hits, geometry ' + str(ev['geometry_file']) if ev else 'no'}"
        print(f"{name:9s} status: {d['status']:11s} from {d['source']}{extra}")
    js = ("// Generated by build_data.py from ../kilometre/results and ../telescope/results. Do not edit by hand.\n"
          f"// {TAG}\n"
          f"window.NOBEL_PHYS_DATA = {json.dumps(data, separators=(',', ':'))};\n")
    a.out.write_text(js)
    print(f"wrote {a.out} ({len(js.encode()) / 1024:.1f} KB); preliminary banner: {'yes' if data['preliminary'] else 'no'}")


if __name__ == "__main__":
    main()
