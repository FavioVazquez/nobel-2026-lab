"""Monte Carlo light transport from an optical-fibre tip in homogeneous brain tissue.

Educational demo, toy model. Own MIT implementation (MCML-style photon packets, written from the
textbook method: Wang, Jacques & Zheng 1995). Infinite homogeneous medium, cylindrical (r, z) tally.
Units: mm, mm^-1, W. Output fluence rate is per watt of light leaving the fibre.
"""
import time
from dataclasses import dataclass

import numpy as np

from .common import RESULTS, read_csv

N_TISSUE = 1.36
G_ANISO = 0.86
JACQUES_BRAIN_A_CM, JACQUES_BRAIN_B = 24.2, 1.611
BLOOD_FRACTION, SATURATION, HB_G_PER_L, HB_G_PER_MOL = 0.03, 0.75, 150.0, 64500.0

WAVELENGTHS = (470, 590, 635)
# Fine region: uniform 25 um cells, r 0-6 mm, z -5..7 mm. Around it, cells grow by GROWTH per cell out to
# at least OUTER, so red light (1/e depth ~2.8 mm) is absorbed inside the tally and the heat box edge sits
# many Pennes lengths (4.2 mm) away. Growing edges are rounded to multiples of dr so binning stays a lookup.
GRID = dict(dr=0.025, dz=0.025, r_max=6.0, z_min=-5.0, z_max=7.0)
OUTER = dict(r_max=40.0, z_min=-40.0, z_max=42.0, growth=1.15)


@dataclass
class Optics:
    wavelength: float
    mua: float  # mm^-1
    mus: float  # mm^-1
    g: float = G_ANISO

    @property
    def mus_reduced(self):
        return self.mus * (1 - self.g)

    @property
    def mu_eff(self):
        """Diffusion-theory effective attenuation sqrt(3 mua (mua + mus'))."""
        return np.sqrt(3 * self.mua * (self.mua + self.mus_reduced))


def optics(wavelength):
    """Brain optics at one wavelength from the shipped, sourced inputs (see inputs/tissue_optics.csv)."""
    rows = read_csv("tissue_optics.csv")
    wl = np.array([float(r["wavelength_nm"]) for r in rows])
    e_ox = np.interp(wavelength, wl, [float(r["eps_HbO2"]) for r in rows])
    e_de = np.interp(wavelength, wl, [float(r["eps_Hb"]) for r in rows])
    molar = HB_G_PER_L / HB_G_PER_MOL
    mua_cm = BLOOD_FRACTION * np.log(10) * molar * (SATURATION * e_ox + (1 - SATURATION) * e_de)
    musr_cm = JACQUES_BRAIN_A_CM * (wavelength / 500.0) ** (-JACQUES_BRAIN_B)
    return Optics(wavelength, mua_cm / 10, musr_cm / (1 - G_ANISO) / 10)


def _growing(start, stop, d, q):
    """Edges from start (exclusive) growing by q per cell until |edge - start| >= |stop - start|."""
    sign, out, w, x = np.sign(stop - start), [], d, start
    while abs(x - start) < abs(stop - start):
        w *= q
        x = x + sign * max(d, np.round(w / d) * d)
        out.append(x)
    return np.array(out)


def _grid(outer=True):
    nr = int(round(GRID["r_max"] / GRID["dr"]))
    nz = int(round((GRID["z_max"] - GRID["z_min"]) / GRID["dz"]))
    r_edges = np.linspace(0, GRID["r_max"], nr + 1)
    z_edges = np.linspace(GRID["z_min"], GRID["z_max"], nz + 1)
    if outer:
        q = OUTER["growth"]
        r_edges = np.r_[r_edges, _growing(GRID["r_max"], OUTER["r_max"], GRID["dr"], q)]
        z_edges = np.r_[_growing(GRID["z_min"], OUTER["z_min"], GRID["dz"], q)[::-1], z_edges,
                        _growing(GRID["z_max"], OUTER["z_max"], GRID["dz"], q)]
    return np.round(r_edges, 9), np.round(z_edges, 9)


def _lookup(edges, d):
    """Cell index for every d-wide bin starting at edges[0] (edges are multiples of d away from edges[0])."""
    n = int(round((edges[-1] - edges[0]) / d))
    return np.searchsorted(edges, edges[0] + (np.arange(n) + 0.5) * d) - 1


def is_fine_cell(r_edges, z_edges):
    """Mask of the uniform 25 um cells (the fine region) on a grid from _grid()."""
    dr, dz = np.diff(r_edges), np.diff(z_edges)
    return (np.isclose(dr, GRID["dr"]) & (r_edges[1:] <= GRID["r_max"] + 1e-9))[:, None] & \
        (np.isclose(dz, GRID["dz"]) & (z_edges[:-1] >= GRID["z_min"] - 1e-9) & (z_edges[1:] <= GRID["z_max"] + 1e-9))[None, :]


def cell_volumes(r_edges, z_edges):
    return np.outer(np.pi * (r_edges[1:] ** 2 - r_edges[:-1] ** 2), np.diff(z_edges))


def simulate(opt, n_photons=100_000, core_radius=0.1, na=0.22, seed=0, batch=50_000, w_min=1e-3):
    """Run the photon walk. Returns dict with r/z edges, absorbed fraction per cell, fluence per W."""
    rng = np.random.default_rng(seed)
    r_edges, z_edges = _grid()
    nr, nz = len(r_edges) - 1, len(z_edges) - 1
    absorbed = np.zeros(nr * nz)
    mut = opt.mua + opt.mus
    albedo = opt.mus / mut
    g = opt.g
    cos_max = np.sqrt(1 - (na / N_TISSUE) ** 2)
    dr, dz = GRID["dr"], GRID["dz"]
    r_lut, z_lut = _lookup(r_edges, dr), _lookup(z_edges, dz)
    # photons beyond the tally carry a negligible share of the light (checked: absorbed fraction ~1.0)
    kill_r2 = (1.1 * max(r_edges[-1], -z_edges[0], z_edges[-1])) ** 2
    t0 = time.perf_counter()
    steps = 0
    for start in range(0, n_photons, batch):
        n = min(batch, n_photons - start)
        rho = core_radius * np.sqrt(rng.random(n))
        phi = 2 * np.pi * rng.random(n)
        x, y, z = rho * np.cos(phi), rho * np.sin(phi), np.zeros(n)
        ct = 1 - rng.random(n) * (1 - cos_max)  # uniform over the launch cone's solid angle
        st = np.sqrt(1 - ct**2)
        ph = 2 * np.pi * rng.random(n)
        ux, uy, uz = st * np.cos(ph), st * np.sin(ph), ct
        w = np.ones(n)
        while w.size:
            s = -np.log(rng.random(w.size)) / mut
            x += s * ux
            y += s * uy
            z += s * uz
            dw = w * (1 - albedo)
            w = w - dw
            ir = (np.sqrt(x * x + y * y) / dr).astype(np.int64)
            iz = np.floor((z - z_edges[0]) / dz).astype(np.int64)
            ok = (ir < r_lut.size) & (iz >= 0) & (iz < z_lut.size)
            absorbed += np.bincount(r_lut[ir[ok]] * nz + z_lut[iz[ok]], weights=dw[ok], minlength=nr * nz)
            steps += w.size
            # Henyey-Greenstein scattering
            xi = rng.random(w.size)
            tmp = (1 - g * g) / (1 - g + 2 * g * xi)
            cth = (1 + g * g - tmp * tmp) / (2 * g)
            sth = np.sqrt(np.clip(1 - cth * cth, 0, None))
            psi = 2 * np.pi * rng.random(w.size)
            cp, sp = np.cos(psi), np.sin(psi)
            den = np.sqrt(np.clip(1 - uz * uz, 1e-12, None))
            straight = np.abs(uz) > 0.99999
            nux = np.where(straight, sth * cp, sth * (ux * uz * cp - uy * sp) / den + ux * cth)
            nuy = np.where(straight, sth * sp, sth * (uy * uz * cp + ux * sp) / den + uy * cth)
            nuz = np.where(straight, np.sign(uz) * cth, -sth * cp * den + uz * cth)
            ux, uy, uz = nux, nuy, nuz
            # Russian roulette, and drop photons far outside the tally volume
            low = w < w_min
            if low.any():
                survive = rng.random(w.size) < 0.1
                w = np.where(low, np.where(survive, w * 10, 0.0), w)
            keep = (w > 0) & (x * x + y * y + z * z < kill_r2)
            if not keep.all():
                x, y, z, ux, uy, uz, w = (a[keep] for a in (x, y, z, ux, uy, uz, w))
    seconds = time.perf_counter() - t0
    absorbed = absorbed.reshape(nr, nz) / n_photons
    vol = cell_volumes(r_edges, z_edges)
    power_density = absorbed / vol  # W/mm^3 absorbed per W launched
    return dict(
        r_edges=r_edges, z_edges=z_edges, absorbed=absorbed, power_density=power_density,
        fluence=power_density / opt.mua,  # W/mm^2 per W launched
        n_photons=n_photons, seconds=seconds, steps=steps, wavelength=opt.wavelength,
        mua=opt.mua, mus=opt.mus, g=opt.g, core_radius=core_radius, na=na,
    )


def diffusion_check(res, opt, rho_min=None, rho_max=None):
    """Fit the far-field decay of fluence*distance against exp(-mu_eff * distance).

    Diffusion theory for a point source in an infinite medium predicts phi(rho) ~ exp(-mu_eff rho)/rho
    far (several transport lengths) from the source. Returns (fitted, predicted) decay constants.
    """
    r_c = 0.5 * (res["r_edges"][1:] + res["r_edges"][:-1])
    z_c = 0.5 * (res["z_edges"][1:] + res["z_edges"][:-1])
    rho = np.sqrt(r_c[:, None] ** 2 + z_c[None, :] ** 2)
    ltr = 1 / (opt.mua + opt.mus_reduced)
    rho_min = rho_min or 4 * ltr
    rho_max = rho_max or min(rho_min + 4 / opt.mu_eff, 0.9 * GRID["r_max"])
    bins = np.linspace(rho_min, rho_max, 16)
    vol = cell_volumes(res["r_edges"], res["z_edges"])
    idx = np.digitize(rho, bins) - 1
    m = (idx >= 0) & (idx < len(bins) - 1)
    a = np.bincount(idx[m], weights=res["absorbed"][m], minlength=len(bins) - 1)
    v = np.bincount(idx[m], weights=vol[m], minlength=len(bins) - 1)
    centres = 0.5 * (bins[1:] + bins[:-1])
    phi = a / v / opt.mua
    good = phi > 0
    slope = np.polyfit(centres[good], np.log(phi[good] * centres[good]), 1)[0]
    return -slope, opt.mu_eff


def transport_decay(opt, n_terms=400):
    """Exact far-field decay rate (mm^-1) of the transport equation with a Henyey-Greenstein phase function.

    Plane-wave P_N method: with phi_l ~ exp(-k z), (l+1) phi_{l+1} + l phi_{l-1} = (2l+1) sigma_l phi_l / k,
    sigma_l = mu_t - mu_s g^l. The slowest decaying mode (largest 1/k) is the asymptotic rate. Unlike
    diffusion theory, this is exact once n_terms is large (400 here; P_399)."""
    from scipy.linalg import eigh_tridiagonal

    l = np.arange(n_terms)
    sig = (opt.mua + opt.mus) - opt.mus * opt.g ** l
    b = 1 / np.sqrt((2 * l + 1) * sig)
    off = (l[1:]) * b[1:] * b[:-1]
    lam = eigh_tridiagonal(np.zeros(n_terms), off, eigvals_only=True)
    return 1 / lam.max()


def depth_profile(res):
    """On-axis fluence (W/mm^2 per W) vs depth, averaged over the innermost 100 um of radius."""
    z_c = 0.5 * (res["z_edges"][1:] + res["z_edges"][:-1])
    vol = cell_volumes(res["r_edges"], res["z_edges"])
    k = max(1, int(round(0.1 / GRID["dr"])))
    phi = (res["fluence"][:k] * vol[:k]).sum(0) / vol[:k].sum(0)
    return z_c, phi


def run(n_photons=100_000, wavelengths=WAVELENGTHS, core_radius=0.1, na=0.22, tag="fibre200um", seed=0):
    """Simulate and cache each wavelength to results/light_<tag>_<wl>nm.npz (float32, compressed)."""
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = {}
    for i, wl in enumerate(wavelengths):
        opt = optics(wl)
        res = simulate(opt, n_photons, core_radius, na, seed=seed + i)
        np.savez_compressed(
            RESULTS / f"light_{tag}_{wl}nm.npz",
            r_edges=res["r_edges"], z_edges=res["z_edges"],
            fluence_per_W=res["fluence"].astype(np.float32),
            meta=np.array([wl, n_photons, res["seconds"], opt.mua, opt.mus, opt.g, core_radius, na]),
        )
        out[wl] = res
    return out


def plot_depth_profiles(results):
    import matplotlib.pyplot as plt

    from .common import WAVELENGTH_COLOURS, apply_theme, save_themed, titles

    def make(theme):
        fig, ax = plt.subplots(figsize=(8, 6.4), layout="constrained")
        t = apply_theme(fig, [ax], theme)
        for wl, res in results.items():
            z, phi = depth_profile(res)
            m = (z > 0) & (z < 4)
            ax.semilogy(z[m], phi[m] * 10, lw=3.5, color=WAVELENGTH_COLOURS[wl], label=f"{wl} nm")
        ax.axhline(3, color=t["muted"], ls="--", lw=1.5)
        ax.text(3.95, 3.6, "3 mW/mm²", ha="right", color=t["muted"], fontsize=14)
        ax.set_xlabel("Depth below the fibre tip (mm)", fontsize=16)
        ax.set_ylabel("Light at 10 mW out of the fibre\n(mW per mm², log scale)", fontsize=16)
        ax.set_ylim(1e-3, 1e3)
        titles(fig, ax, t, "Blue light fades fastest in brain tissue",
               "200 µm fibre, homogeneous tissue\nno non-blood absorption, so red reach is overstated")
        leg = ax.legend(fontsize=15, frameon=False)
        for txt in leg.get_texts():
            txt.set_color(t["fg"])
        return fig

    return save_themed(make, "light_depth_profile")
