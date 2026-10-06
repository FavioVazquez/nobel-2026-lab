"""Fast checks of build_data.py (educational demo, toy models; not research). Standard library + pytest only.

    python3 -m pytest -q tests          (from 2026/physics/page/)
"""
import json
import shutil
import sys
from pathlib import Path

import pytest

PAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PAGE))
import build_data  # noqa: E402

FIX = PAGE / "tests" / "fixtures"


def load(js_path):
    js = js_path.read_text()
    return json.loads(js[js.index("=") + 1: js.rindex(";")])


def test_fixtures_build_and_say_placeholder(tmp_path, capsys):
    out = tmp_path / "data.js"
    build_data.main(["--fixtures", "--out", str(out)])
    d = load(out)
    printed = capsys.readouterr().out
    assert "kilometre status: fixture" in printed and "telescope status: fixture" in printed
    assert d["preliminary"] and d["placeholder"]
    assert d["km"]["curves"]["interaction"] and d["km"]["curves"]["transmission_1PeV"] and d["km"]["curves"]["size"]
    ev = d["tel"]["event"]
    assert ev and len(ev["hits"]) == ev["n_hits_file"] and len(ev["strings_xy"]) == 86
    assert all(len(h) == 5 for h in ev["hits"]) and ev["hits"] == sorted(ev["hits"], key=lambda h: h[3])
    assert "/Users/" not in out.read_text()  # local paths are printed, never shipped


def test_missing_inputs(tmp_path, capsys):
    out = tmp_path / "data.js"
    build_data.main(["--from", str(tmp_path / "kilometre" / "results"), str(tmp_path / "telescope" / "results"), "--out", str(out)])
    d = load(out)
    assert d["inputs"] == {"kilometre": "missing", "telescope": "missing"} and d["km"] is None and d["tel"] is None
    assert d["preliminary"]


def copy_inputs(tmp_path, km_status="final", tel_status="final"):
    km, tel = tmp_path / "km" / "kilometre" / "results", tmp_path / "tel" / "telescope" / "results"
    shutil.copytree(FIX / "kilometre" / "results", km)
    shutil.copytree(FIX / "telescope" / "results", tel)
    for f, st in ((km / build_data.KM_FILE, km_status), (tel / build_data.TEL_FILE, tel_status)):
        j = json.loads(f.read_text()); j["status"] = st; f.write_text(json.dumps(j))
    return km, tel


@pytest.mark.parametrize("km_status,tel_status,prelim", [("final", "final", False), ("preliminary", "final", True), ("final", "preliminary", True)])
def test_banner_follows_status(tmp_path, km_status, tel_status, prelim):
    km, tel = copy_inputs(tmp_path, km_status, tel_status)
    out = tmp_path / "data.js"
    build_data.main(["--from", str(tel), str(km), "--out", str(out)])  # any order
    d = load(out)
    assert d["inputs"] == {"kilometre": km_status, "telescope": tel_status} and d["preliminary"] is prelim


def test_curve_variants(tmp_path):
    """Other plausible CSV layouts: energy in TeV, cos(zenith), one column per energy, a long energy x zenith table."""
    f = tmp_path
    (f / "a.csv").write_text("E_TeV,P_interaction_1km\n1,1e-7\n100,2e-5\n1000,5e-5\n10000,1e-4\n")
    (f / "b.csv").write_text("cos_zenith,transmission_100TeV,transmission_1PeV\n0,1,1\n-0.5,0.5,0.05\n-1,0.13,0.0016\n")
    (f / "c.csv").write_text("side_km,events_per_year\n0.01,1e-5\n0.1,1e-2\n1,9\n")
    i = build_data.interaction_curve(f)
    assert i["energy_GeV"][0] == 1000 and i["p"][-1] == 1e-4
    t = build_data.transmission_curve(f)
    assert t["zenith_deg"] == [90, 120, 180] and t["T"][-1] == 0.0016
    s = build_data.size_curve(f)
    assert s["side_m"] == [10, 100, 1000]
    g = tmp_path / "long"; g.mkdir()
    (g / "map.csv").write_text("log10_E_GeV,zenith_deg,survival\n5,90,1\n5,180,0.13\n6,90,1\n6,135,0.02\n6,180,0.0016\n")
    t = build_data.transmission_curve(g)
    assert t["zenith_deg"] == [90, 135, 180] and t["T"] == [1, 0.02, 0.0016]


def test_wide_transmission_table(tmp_path):
    """The kilometre experiment's layout: one row per energy, one column per zenith (earth_transmission_numu.csv)."""
    (tmp_path / "earth_transmission_numu.csv").write_text(
        "# comment\nE_GeV,zenith_90deg,zenith_120deg,zenith_180deg\n1e5,1,0.6,0.13\n1e+06,0.9999,0.2,0.0016\n1e7,1,0.01,1e-6\n")
    t = build_data.transmission_curve(tmp_path)
    assert t["zenith_deg"] == [90, 120, 180] and t["T"] == [0.9999, 0.2, 0.0016] and t["species"] == "numu"
    assert build_data.zenith_of("zenith_95deg") == 95 and round(build_data.zenith_of("cosz_-1")) == 180
