"""Download (or copy from a local folder) the public IceCube files used ONLY for the cross-checks.

They are not part of this repository; they land in kilometre/data_cache/ (git-ignored).
The three core results need nothing from here: they use the nuFATE tables in whykm/inputs/.

    python -m whykm.fetch                     # download (about 80 MB, most of it the HESE simulation)
    python -m whykm.fetch --from-dir PATH     # copy files with the same names found anywhere under PATH
    python -m whykm.fetch --hese-zip FILE     # use an already downloaded HESE release zip

Sources (all checked 2026-10-06):
* IceCube 10-year point-source tracks (IceTracks-DR1), doi:10.7910/DVN/VKL316, CC0 1.0:
  irfs/IC86_II_effectiveArea.csv (Dataverse file 10218369).
* IceCube 14-year tracks (IceTracks-DR2), doi:10.7910/DVN/MMIIZA, CC0 1.0:
  irfs/IC86_effectiveArea.csv (Dataverse file 14153506).
* IceCube HESE 7.5-year release, doi:10.21234/4EQJ-BB17, https://github.com/icecube/HESE-7-year-data-release
  (LGPL-3.0): resources/data/HESE_data.json and the three HESE_mc_*.json simulation files.
"""
import argparse
import hashlib
import io
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

CACHE = Path(__file__).resolve().parent.parent / "data_cache"
DV = "https://dataverse.harvard.edu/api/access/datafile/{}?format=original"
HESE_ZIP_URL = "https://github.com/icecube/HESE-7-year-data-release/archive/refs/heads/main.zip"
# Harvard Dataverse answers HTTP 403 to Python's default User-Agent ("Python-urllib/3.x").
UA = {"User-Agent": "nobel-2026-lab-whykm/1.0 (+https://github.com/FavioVazquez/nobel-2026-lab)"}

FILES = {  # cache name: (url or None, md5, other names it may have in a local copy)
    "dr1_IC86_II_effectiveArea.csv": (DV.format(10218369), "07a4eb6ed830a588ea5005774a5576bc",
                                      ["IC86_II_effectiveArea.csv", "IC86_II_effectiveArea.tab"]),
    "dr2_IC86_effectiveArea.csv": (DV.format(14153506), "780664d6f775be6b6e3e0c7833aafbf4",
                                   ["IC86_effectiveArea.csv", "IC86_effectiveArea.tab"]),
    "HESE_data.json": (None, "250f7d2aa48f941c882c0977894882ac", []),
    "HESE_mc_truth.json": (None, "37e34086d876c32b6cf31bb8fb4706bf", []),
    "HESE_mc_observable.json": (None, "1a064b205024cc5019c60ead485ef427", []),
    "HESE_mc_flux.json": (None, "0e07772c04b9167fef5dbfb6fa8e8c45", []),
}
HESE_FILES = [k for k in FILES if k.startswith("HESE_")]


def md5(path):
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def have(name):
    p = CACHE / name
    return p.exists() and md5(p) == FILES[name][1]


def _store(name, data):
    CACHE.mkdir(parents=True, exist_ok=True)
    got = hashlib.md5(data).hexdigest()
    if got != FILES[name][1]:
        raise RuntimeError(f"{name}: MD5 {got} does not match the published {FILES[name][1]}")
    (CACHE / name).write_bytes(data)
    print(f"  ok  {name} ({len(data) / 1e6:.2f} MB)")


def _from_zip(zf):
    for info in zf.infolist():
        base = info.filename.rsplit("/", 1)[-1]
        if base in HESE_FILES and not have(base):
            _store(base, zf.read(info))


def fetch(from_dir=None, hese_zip=None, download=True):
    if from_dir:
        root = Path(from_dir)
        for name, (_, _, alts) in FILES.items():
            if have(name):
                continue
            for cand in [name, *alts]:
                hits = [p for p in root.rglob(cand) if p.is_file() and md5(p) == FILES[name][1]]
                if hits:
                    CACHE.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(hits[0], CACHE / name)
                    print(f"  ok  {name} (copied from {hits[0]})")
                    break
    if hese_zip and not all(have(n) for n in HESE_FILES):
        with zipfile.ZipFile(hese_zip) as zf:
            _from_zip(zf)
    if not download:
        return
    for name, (url, _, _) in FILES.items():
        if url and not have(name):
            print(f"  get {name}")
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                _store(name, r.read())
    if not all(have(n) for n in HESE_FILES):
        print(f"  get HESE release zip (~79 MB) from {HESE_ZIP_URL}")
        with urllib.request.urlopen(urllib.request.Request(HESE_ZIP_URL, headers=UA), timeout=600) as r:
            _from_zip(zipfile.ZipFile(io.BytesIO(r.read())))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from-dir")
    ap.add_argument("--hese-zip")
    ap.add_argument("--no-download", action="store_true")
    a = ap.parse_args(argv)
    fetch(a.from_dir, a.hese_zip, download=not a.no_download)
    missing = [n for n in FILES if not have(n)]
    print("missing: " + ", ".join(missing) if missing else f"all cross-check files present in {CACHE}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
