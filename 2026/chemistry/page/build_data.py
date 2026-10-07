"""Build page/data.js from the three Chemistry experiments (educational demo, toy models; not research).

Reads, relative to this folder:
  ../mirror-race/results     mirror_summary.json, race_runs.json, histograms.json
  ../kagan-curve             kagan.js (inlined as a pure function) and results/kagan_summary.json
  ../soai-amplifier/results  amplifier_summary.json, rounds.json
plus the two alanine structures in molecules/ (PubChem, public domain). Writes data.js, a plain script that
sets window.NOBEL_CHEM_DATA and window.NOBEL_CHEM_KAGAN, so index.html works from file:// with no server and
no network. Every number the page states comes from here; nothing is typed into index.html.
Python 3 standard library only. Everything is in dimensionless model units.

    python3 build_data.py                                   # from 2026/chemistry/page/ after the merge
    python3 build_data.py --from MIRROR_RESULTS KAGAN_DIR AMP_RESULTS   # the experiments' folders anywhere
    python3 build_data.py --fixtures                        # the placeholder inputs in tests/fixtures
    python3 build_data.py --out /tmp/data.js                # write somewhere else

It prints the status of each input file ("final", "preliminary", "fixture" or "missing"). The page shows a
visible "preliminary" box unless all three inputs are "final".
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "tests" / "fixtures"
DEFAULTS = (HERE.parent / "mirror-race" / "results", HERE.parent / "kagan-curve", HERE.parent / "soai-amplifier" / "results")
TAG = "Educational demo, toy models. Not research."
GITHUB = "https://github.com/FavioVazquez/nobel-2026-lab/tree/main/2026/chemistry/"

# Real, published numbers (not toy results). Keys follow the sources list at the bottom of the page.
SOAI_2003_PCT = [0.00005, 57, 99, 99.5]      # S03a; SCI p. 12 (Fig. 7, entries 6-8): 0.00005 -> 57 -> 99 -> >99.5 % ee
REAL_RUNS = {
    "soai_2003": {"runs": 37, "one": 19, "mirror": 18, "ee_range_pct": [15, 91],
                  "source": "S03b; SCI p. 13", "hands": "19 (S), 18 (R)"},
    "singleton_vo_2003": {"runs": 54, "one": 27, "mirror": 27, "source": "SV03; SCI p. 13", "hands": "27 (R), 27 (S)"},
}
KAGAN_PIE = {"ligand": [75, 25], "catalysts_pct": [56.25, 37.5, 6.25], "effective": [90, 10], "ee_prod_pct": 80}  # POP
# Rates of the live in-browser race when the mirror-race summary does not carry them: the mirror-race
# experiment's own constants (mirrorrace/constants.py: K0 = K1 = 1 "choice", K2_STRONG = 100 "tuned").
RACE_RATES_DEFAULT = {"k0": 1.0, "k1": 1.0, "k2": 100.0, "source": "mirror-race constants (k0 = k1 = 1 choice, k2 = 100 tuned)"}
RACE_N = 2000                                  # choice: molecules in the live race (fast enough for a phone)
MOLECULES = {"one": ("cid5950_3d.sdf", 5950, "L-alanine", "S"), "mirror": ("cid71080_3d.sdf", 71080, "D-alanine", "R")}


def sig(x, n=4):
    return None if x is None else float(f"{float(x):.{n}g}")


def load(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def status_of(obj):
    if obj is None:
        return "missing"
    if isinstance(obj, dict) and "status" not in obj:
        return "no status field (the summary's status applies)"
    s = str(obj.get("status", "unknown")).lower() if isinstance(obj, dict) else "unknown"
    return s if s in ("final", "preliminary", "fixture") else "preliminary"


def summ_status(obj):
    """A summary without a status field counts as preliminary."""
    st = status_of(obj)
    return st if st in ("final", "preliminary", "fixture", "missing") else "preliminary"


def binom_two_sided(k, n):
    """Exact two-sided binomial test against 1/2: the chance of a split at least as uneven as k of n."""
    if n <= 2000:  # exact integers
        pk = math.comb(n, k)
        return min(1.0, sum(c for c in (math.comb(n, i) for i in range(n + 1)) if c <= pk) / 2 ** n)
    lp = lambda i: math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) - n * math.log(2)
    lk = lp(k)
    return min(1.0, sum(math.exp(lp(i)) for i in range(n + 1) if lp(i) <= lk + 1e-9))


# ---------- molecules ----------------------------------------------------------------------------------
def read_sdf(path):
    lines = path.read_text().splitlines()
    na, nb = int(lines[3][:3]), int(lines[3][3:6])
    atoms = []
    for l in lines[4:4 + na]:
        atoms.append({"el": l[31:34].strip(), "x": float(l[:10]), "y": float(l[10:20]), "z": float(l[20:30])})
    bonds = [[int(l[:3]) - 1, int(l[3:6]) - 1, int(l[6:9])] for l in lines[4 + na:4 + na + nb]]
    return atoms, bonds


def sub(a, b):
    return [a["x"] - b["x"], a["y"] - b["y"], a["z"] - b["z"]]


def cross(u, v):
    return [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]


def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def alanine_center(atoms, bonds):
    """Index of the stereocentre and its four neighbours in CIP order: N > acid C > methyl C > H."""
    nb = {i: [] for i in range(len(atoms))}
    for a, b, _ in bonds:
        nb[a].append(b); nb[b].append(a)
    els = lambda i: sorted(atoms[j]["el"] for j in nb[i])
    for i, a in enumerate(atoms):
        if a["el"] == "C" and len({atoms[j]["el"] + "".join(els(j)) for j in nb[i]}) == 4:
            ns = nb[i]
            n = next(j for j in ns if atoms[j]["el"] == "N")
            acid = next(j for j in ns if atoms[j]["el"] == "C" and "O" in els(j))
            me = next(j for j in ns if atoms[j]["el"] == "C" and j != acid)
            h = next(j for j in ns if atoms[j]["el"] == "H")
            return i, [n, acid, me, h]
    raise ValueError("no stereocentre found")


def cip_label(atoms, bonds):
    """R or S from the 3D coordinates: with the H pointing away, N -> acid C -> methyl C clockwise is R.
    The signed volume (p1 - c) . ((p2 - c) x (p3 - c)) is negative for R and positive for S."""
    c, (p1, p2, p3, _) = alanine_center(atoms, bonds)
    v = dot(sub(atoms[p1], atoms[c]), cross(sub(atoms[p2], atoms[c]), sub(atoms[p3], atoms[c])))
    return "R" if v < 0 else "S"


def molecule(name):
    fname, cid, common, cip = MOLECULES[name]
    atoms, bonds = read_sdf(HERE / "molecules" / fname)
    c, arms = alanine_center(atoms, bonds)
    heavy = [a for a in atoms if a["el"] != "H"]
    cx, cy, cz = (sum(a[k] for a in heavy) / len(heavy) for k in "xyz")
    return {"cid": cid, "name": common, "cip": cip_label(atoms, bonds), "cip_expected": cip,
            "atoms": [[a["el"], round(a["x"] - cx, 4), round(a["y"] - cy, 4), round(a["z"] - cz, 4)] for a in atoms],
            "bonds": bonds, "center": c, "arms": arms}


# ---------- kagan.js --------------------------------------------------------------------------------------
def inline_kagan(path):
    """Wrap kagan.js so it runs as a classic script and exposes its functions on window.NOBEL_CHEM_KAGAN.
    Handles CommonJS (module.exports), ES module (export function / export const) and plain globals."""
    if not path.exists():
        return "window.NOBEL_CHEM_KAGAN = null;\n", []
    src = path.read_text()
    src = re.sub(r"^\s*export\s+default\s+", "const __default = ", src, flags=re.M)
    src = re.sub(r"^(\s*)export\s+(?=(async\s+)?function|const|let|var|class)", r"\1", src, flags=re.M)
    src = re.sub(r"^\s*export\s*\{[^}]*\};?\s*$", "", src, flags=re.M)
    names = sorted(set(re.findall(r"^(?:async\s+)?function\s+([A-Za-z_$][\w$]*)", src, flags=re.M)
                       + re.findall(r"^(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=", src, flags=re.M)))
    grab = "".join(f'  if (typeof {n} !== "undefined") out.{n} = {n};\n' for n in names)
    js = ("window.NOBEL_CHEM_KAGAN = (function () {\n  var module = { exports: {} }, exports = module.exports;\n"
          + src + "\n  var out = Object.assign({}, module.exports);\n" + grab + "  return out;\n})();\n")
    return js, names


# ---------- mirror race ------------------------------------------------------------------------------------
def pick(d, *pats, exclude=None):
    """The value of the first key of dict d that matches one of the regex patterns."""
    if not isinstance(d, dict):
        return None
    for p in pats:
        for k, v in d.items():
            if re.search(p, k, re.I) and not (exclude and re.search(exclude, k, re.I)):
                return v
    return None


def counts(v):
    if isinstance(v, dict):
        v = pick(v, r"^counts?$", r"hist", r"^n$")
    return [float(x) for x in v] if isinstance(v, list) and v and all(isinstance(x, (int, float)) for x in v) else None


def runs_of(v, shared=None, keep=60):
    """A list of runs; each run -> {"p": progress 0..1, "one": counts, "mirror": counts, "pairs": counts},
    thinned to about `keep` samples (the first sample and the last are always kept)."""
    if isinstance(v, dict):
        v = pick(v, r"^runs$", r"traj") or list(v.values())
    out = []
    for r in v or []:
        if not isinstance(r, dict):
            continue
        one = pick(r, r"^one", r"one_hand", r"^l$|left", exclude=r"win")
        mir = pick(r, r"^mirror", r"mirror_hand", r"^d$|right", exclude=r"win")
        prog = pick(r, r"progress", r"^x$", r"extent") or shared
        pairs = pick(r, r"pair")
        if not (isinstance(one, list) and isinstance(mir, list)):
            continue
        n = min(len(one), len(mir))
        if not isinstance(prog, list) or len(prog) < n:
            prog = [i / max(n - 1, 1) for i in range(n)]
        if not isinstance(pairs, list) or len(pairs) < n:
            pairs = [0] * n
        idx = sorted(set([round(i * (n - 1) / (keep - 1)) for i in range(keep)])) if n > keep else list(range(n))
        out.append({"p": [sig(prog[i], 4) for i in idx], "one": [sig(one[i], 5) for i in idx],
                    "mirror": [sig(mir[i], 5) for i in idx], "pairs": [sig(pairs[i], 5) for i in idx]})
    return out


def mirror_block(folder):
    summ, hist, race = (load(folder / f) for f in ("mirror_summary.json", "histograms.json", "race_runs.json"))
    files = {"mirror_summary.json": status_of(summ), "histograms.json": status_of(hist), "race_runs.json": status_of(race)}
    if summ is None:
        return None, files
    m = {"status": summ_status(summ), "N": summ.get("N"), "runs": summ.get("runs"),
         "copy_only": summ.get("copy_only", {}), "with_antagonism": summ.get("with_antagonism", {}),
         "stopped_early": summ.get("stopped_early", {}), "seeded": summ.get("seeded", {}), "label": summ.get("label")}
    rates = dict(RACE_RATES_DEFAULT)
    src = pick(summ, r"^model$", r"^rates$", r"constants", r"params")
    if isinstance(src, dict):
        for k in ("k0", "k1", "k2"):
            v = pick(src, rf"^{k}$", rf"^{k}_strong$", rf"{k}")
            if isinstance(v, (int, float)):
                rates[k] = float(v)
        rates["source"] = "mirror_summary.json"
        if isinstance(src.get("ee_definition"), str):
            m["ee_definition"] = src["ee_definition"]
    m["race_rates"] = rates
    if isinstance(m["stopped_early"], dict):
        m["stopped_early"] = {k: v for k, v in m["stopped_early"].items() if k != "note"}
    real = summ.get("real") or {}
    m["real"] = {}
    for key, ref in REAL_RUNS.items():
        r = dict(ref)
        got = pick(real, key.split("_")[0])
        if isinstance(got, dict):
            for k in ("runs", "one", "mirror"):
                if got.get(k) is not None and got[k] != ref[k]:
                    print(f"  WARNING: mirror_summary real.{key}.{k} = {got[k]} differs from the source ({ref[k]}); using the source")
        r["binomial_p"] = sig(binom_two_sided(r["one"], r["runs"]), 3)
        m["real"][key] = r
    wa = m["with_antagonism"]
    if isinstance(wa.get("one_hand_wins"), (int, float)) and isinstance(wa.get("mirror_hand_wins"), (int, float)):
        n = int(wa["one_hand_wins"] + wa["mirror_hand_wins"])
        wa.setdefault("binomial_p", sig(binom_two_sided(int(wa["one_hand_wins"]), n), 3))
    if hist is not None:
        edges = pick(hist, r"edges")
        src = hist["counts"] if isinstance(hist.get("counts"), dict) else hist
        h = {"copy_only": counts(pick(src, r"copy", exclude=r"antag|first|order|exact|expected")),
             "with_antagonism": counts(pick(src, r"antag", exclude=r"first|order")),
             "stopped_early": counts(pick(src, r"stop|early", exclude=r"first|order|fraction"))}
        nb = len(next((v for v in h.values() if v), []))
        if not (isinstance(edges, list) and len(edges) == nb + 1):
            edges = [-1 + 2 * i / nb for i in range(nb + 1)] if nb else None
        first = pick(hist, r"first.*ee", r"first_runs", r"order|outcome|sequence", exclude=r"bin")
        fr = {}
        if isinstance(first, dict):
            for k, pat in (("copy_only", r"copy"), ("with_antagonism", r"antag")):
                v = pick(first, pat)
                if isinstance(v, list):
                    fr[k] = [sig(x, 3) for x in v[:400] if isinstance(x, (int, float))]
        m["hist"] = {"edges": [sig(e, 5) for e in edges] if edges else None, **h, "first_runs": fr,
                     "stopped_early_fraction": hist.get("stopped_early_fraction_of_A_used")}
    if race is not None:
        shared = race.get("progress") if isinstance(race.get("progress"), list) else None
        m["race_runs"] = {"copy_only": runs_of(pick(race, r"copy", exclude=r"antag"), shared)[:8],
                          "with_antagonism": runs_of(pick(race, r"antag"), shared)[:8], "N": race.get("N")}
    return m, files


# ---------- kagan + amplifier --------------------------------------------------------------------------------
def kagan_block(folder):
    summ = load(folder / "results" / "kagan_summary.json")
    files = {"kagan_summary.json": status_of(summ), "kagan.js": "present" if (folder / "kagan.js").exists() else "missing"}
    if summ is None:
        return None, files
    pie = summ.get("pie_check") or {}
    for k, v in KAGAN_PIE.items():
        if pie.get(k) is not None and [round(float(x), 6) for x in (pie[k] if isinstance(pie[k], list) else [pie[k]])] != \
                [round(float(x), 6) for x in (v if isinstance(v, list) else [v])]:
            print(f"  WARNING: kagan_summary pie_check.{k} = {pie[k]} differs from the Nobel popular information ({v})")
    return {"status": summ_status(summ), "pie": KAGAN_PIE, "pie_from_summary": pie, "erosion": summ.get("erosion"),
            "label": summ.get("label")}, files


def amp_block(folder):
    summ, rounds = load(folder / "amplifier_summary.json"), load(folder / "rounds.json")
    files = {"amplifier_summary.json": status_of(summ), "rounds.json": status_of(rounds)}
    if summ is None:
        return None, files
    s = summ.get("soai_2003_pct")
    if s is not None and [float(x) for x in s] != [float(x) for x in SOAI_2003_PCT]:
        print(f"  WARNING: amplifier_summary soai_2003_pct = {s} differs from S03a ({SOAI_2003_PCT}); the page uses S03a")
    toy = summ.get("toy_rounds") or {}
    ee = [float(x) for x in toy.get("ee_pct") or []]
    rr = pick(rounds, r"^rounds$") if isinstance(rounds, dict) else None
    if isinstance(rr, list) and len(rr) >= 4 and all(isinstance(r, dict) and "ee_pct" in r for r in rr[:4]):
        ee = [float(r["ee_pct"]) for r in rr[:4]]          # round 0 (the seed) to round 3
    elif len(ee) == 3:
        ee = [SOAI_2003_PCT[0]] + ee                        # toy_rounds lists rounds 1-3; it starts from Soai's head start
    out = {"status": summ_status(summ), "toy_rounds": {"K": toy.get("K"), "turnovers_per_round": toy.get("turnovers_per_round"),
                                                     "ee_pct": [sig(x, 6) for x in ee[:4]], "fitted": toy.get("fitted")},
           "k4_fails": summ.get("k4_fails") or {}, "layer1": summ.get("layer1") or {},
           "notes": summ.get("notes"), "label": summ.get("label")}
    if isinstance(rr, list):
        out["rounds"] = [{k: (sig(v, 5) if isinstance(v, (int, float)) else v) for k, v in r.items()} for r in rr[:4] if isinstance(r, dict)]
    k4 = out["k4_fails"]
    out["k4_fails"] = {"turnovers_needed_to_57": k4.get("turnovers_needed_to_57")} if isinstance(k4, dict) else {}
    out["layer1"] = {}
    return out, files


def build(mirror_dir, kagan_dir, amp_dir, fixtures=False):
    print("Chemistry page inputs:")
    mirror, f1 = mirror_block(mirror_dir)
    kagan, f2 = kagan_block(kagan_dir)
    amp, f3 = amp_block(amp_dir)
    kjs, knames = inline_kagan(kagan_dir / "kagan.js")
    for folder, files in ((mirror_dir, f1), (kagan_dir, f2), (amp_dir, f3)):
        for name, st in files.items():
            print(f"  {st:12s}  {name:24s} ({folder})")
    if knames:
        print(f"  kagan.js functions: {', '.join(knames)}")
    inputs = {"mirror_race": mirror["status"] if mirror else "missing",
              "kagan_curve": kagan["status"] if kagan else "missing",
              "soai_amplifier": amp["status"] if amp else "missing"}
    data = {
        "tag": TAG, "inputs": inputs,
        "preliminary": any(v != "final" for v in inputs.values()),
        "placeholder": fixtures or any(v == "fixture" for v in inputs.values()),
        "mirror": mirror, "kagan": kagan, "amp": amp,
        "soai_2003_pct": SOAI_2003_PCT, "real_runs": {k: dict(v, binomial_p=sig(binom_two_sided(v["one"], v["runs"]), 3)) for k, v in REAL_RUNS.items()},
        "race_N": RACE_N, "race_rates": (mirror or {}).get("race_rates", RACE_RATES_DEFAULT),
        "molecules": {k: molecule(k) for k in MOLECULES},
        "github": GITHUB,
    }
    for k, m in data["molecules"].items():
        if m["cip"] != m["cip_expected"]:
            raise SystemExit(f"{m['name']} (CID {m['cid']}) reads {m['cip']} from its coordinates, expected {m['cip_expected']}")
    return data, kjs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from", dest="src", nargs=3, metavar=("MIRROR_RESULTS", "KAGAN_DIR", "AMP_RESULTS"))
    ap.add_argument("--fixtures", action="store_true")
    ap.add_argument("--out", default=str(HERE / "data.js"))
    a = ap.parse_args(argv)
    if a.fixtures:
        dirs = (FIXTURES / "mirror-race" / "results", FIXTURES / "kagan-curve", FIXTURES / "soai-amplifier" / "results")
    elif a.src:
        dirs = tuple(Path(p).resolve() for p in a.src)
    else:
        dirs = DEFAULTS
    data, kjs = build(*dirs, fixtures=a.fixtures)
    js = ("// Generated by build_data.py; do not edit. Educational demo, toy models; not research.\n"
          "window.NOBEL_CHEM_DATA = " + json.dumps(data, separators=(",", ":"), allow_nan=False) + ";\n" + kjs)
    Path(a.out).write_text(js)
    print(f"wrote {a.out} ({len(js) / 1024:.1f} KB); inputs {data['inputs']}; preliminary box {'shown' if data['preliminary'] else 'hidden'}")
    return data


if __name__ == "__main__":
    main(sys.argv[1:])
