"""One-off export: nuFATE's isoscalar total cross sections (HDF5) -> inputs/nufate/nufate_isoscalar_total_xs.csv

Educational demo made to show an open-source tool. Toy model, not research.
Only needed to regenerate the committed CSV; it needs h5py, which the toy itself does not use.

    curl -L -o NuFATECrossSections.h5 https://github.com/aaronvincent/nuFATE/raw/86813eb85526bcd8ac985ecdc4cf24ba89da0d81/resources/NuFATECrossSections.h5
    python -m whykm.export_nufate_xs NuFATECrossSections.h5      # md5 c3330cc7434df4e24d37a934b7c05152
"""
import hashlib
import sys
from pathlib import Path

import numpy as np

from .physics import NUFATE, SPECIES

OUT = NUFATE / "nufate_isoscalar_total_xs.csv"
MD5 = "c3330cc7434df4e24d37a934b7c05152"


def main(path):
    import h5py

    got = hashlib.md5(Path(path).read_bytes()).hexdigest()
    if got != MD5:
        raise SystemExit(f"{path}: MD5 {got}, expected {MD5}")
    with h5py.File(path, "r") as f:
        g = f["total_cross_sections"]
        a = g.attrs
        E = np.logspace(np.log10(a["min_energy"]), np.log10(a["max_energy"]), int(a["number_energy_nodes"]))
        cols = [g[f"{s}xs"][:] for s in SPECIES]
    with open(OUT, "w") as out:
        out.write("# Total (CC+NC) neutrino-nucleon cross sections per isoscalar nucleon 0.5(p+n), CT10nlo, in cm^2.\n")
        out.write("# Exported unchanged from nuFATE resources/NuFATECrossSections.h5 (group total_cross_sections,\n")
        out.write(f"# md5 {MD5}), github.com/aaronvincent/nuFATE commit 86813eb, MIT licence (see LICENSE, AUTHORS).\n")
        out.write("# Energies: logspace(3, 10, 200) GeV, from the file's min_energy / max_energy / number_energy_nodes.\n")
        out.write("E_GeV," + ",".join(SPECIES) + "\n")
        for i, e in enumerate(E):
            out.write(f"{e:.6e}," + ",".join(f"{c[i]:.6e}" for c in cols) + "\n")
    print(f"wrote {OUT} ({len(E)} energies)")


if __name__ == "__main__":
    main(sys.argv[1])
