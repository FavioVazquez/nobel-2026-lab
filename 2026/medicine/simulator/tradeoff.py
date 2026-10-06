"""Trade-off table and figure. Educational demo, toy model.

Reach and heat belong to the COLOUR of the light (every modelled switch borrows ChR2's light
sensitivity, so two switches driven at the same colour get the same reach and heat). Speed belongs
to the SWITCH. So the table and figure split them:
  * per colour (470, 590, 635 nm), from a 200 um / NA 0.22 fibre:
      reach: tissue volume where light is at least THRESHOLD mW/mm^2 when 10 mW leaves the fibre, per mW
      heat: steady-state peak temperature rise per mW of continuous light
  * per switch: headline speed = highest tested pulse rate up to which every tested rate still follows
    the light 1:1 (at THRESHOLD); the first failure ends the run (see neuron.following)
THRESHOLD = 3 mW/mm^2 is one illustrative level; Stujenske et al. 2015 draw 3 and 10 mW/mm^2 contours as
"in the range of the EPD50 for various opsins". Real thresholds depend on the switch and its expression.
The model has no absorption outside blood, so the red (635 nm) row looks better than it is.

    python -m simulator.tradeoff    # rebuild tradeoff.csv and the figure from the cached results
"""
import csv
import json

import numpy as np

from .common import DEMO_TAG, RESULTS, SWITCH_COLOURS, WAVELENGTH_COLOURS, apply_theme, save_themed

THRESHOLD = 3.0
REF_POWER_MW = 10.0
COLOUR_NAMES = {470: "blue", 590: "amber", 635: "red"}
TITLE = "In this toy model, colour sets reach and heat;\nclosing speed sets following"
RED_CAVEAT = "Red result ignores absorption outside blood, so it looks better than it is."
SHARED_NOTE = ("Reach and heat depend only on colour here: every switch shares ChR2's light sensitivity and one "
               "3 mW/mm² threshold. The 590 nm and 635 nm advantages come only from wavelength, and absorption "
               "outside blood is not modelled, so they look better than they are (635 nm: toy upper bound).")
# Klapoetke et al. 2014, Nat Methods 11:338 (PMC3943671), wording checked in the full text on 2026-10-06
CHRIMSONR_QUOTE = ("ChrimsonR: \"fast, reliable red-light driven spiking at frequencies of at least 20 Hz ... comparable "
                   "to the blue-light spiking performance of the commonly used ChR2 (H134R)\" (Klapoetke 2014; cultured "
                   "neurons and slice, 40-pulse trains, 2 ms pulses, 5 mW/mm², red light)")
CHRONOS_QUOTE = ("Chronos: optical spiking \"perfectly replicated electrically driven spiking between 5 to 60 Hz\" "
                 "(530 nm light, 2 ms pulses, 40-pulse trains)")
TOY_SPEED_NOTE = ("Toy result: 470 nm (ChrimsonR stand-in 590 nm), 20 pulses, 3 mW/mm², squid-axon neuron. "
                  "Read the order, not the numbers.")
FIELDS = ["row", "name", "wavelength_nm", "status",
          "volume_mm3_per_mW_at_3mWmm2", "volume_mm3_per_mW_at_1mWmm2", "volume_mm3_per_mW_at_10mWmm2",
          "peak_warming_C_per_mW", "peak_warming_C_per_mW_low_perfusion", "peak_warming_C_per_mW_high_perfusion",
          "slice_mean_warming_C_per_mW", "max_following_rate_Hz", "first_failure_Hz", "follows_again_Hz", "note"]


def _volumes(fluence_per_W, vol):
    phi = fluence_per_W * REF_POWER_MW  # mW/mm^2 at 10 mW
    return {lvl: vol[(phi.ravel() >= lvl)].sum() / REF_POWER_MW for lvl in (1.0, 3.0, 10.0)}


def colour_rows(light_by_wl, heat_by_wl, grid):
    """One row per colour: reach and warming (these do not depend on the switch in this model)."""
    out = []
    for wl in sorted(light_by_wl):
        v = _volumes(light_by_wl[wl]["fluence"], grid.vol)
        h = heat_by_wl[wl]
        out.append({
            "row": "colour", "name": f"{wl} nm ({COLOUR_NAMES.get(wl, '')})", "wavelength_nm": wl, "status": "",
            "volume_mm3_per_mW_at_3mWmm2": v[3.0], "volume_mm3_per_mW_at_1mWmm2": v[1.0],
            "volume_mm3_per_mW_at_10mWmm2": v[10.0],
            "peak_warming_C_per_mW": h["peak_per_mW"], "peak_warming_C_per_mW_low_perfusion": h["peak_per_mW_low"],
            "peak_warming_C_per_mW_high_perfusion": h["peak_per_mW_high"],
            "slice_mean_warming_C_per_mW": h["slice_per_mW"], "max_following_rate_Hz": "",
            "first_failure_Hz": "", "follows_again_Hz": "",
            "note": ("no absorption outside blood in this model: looks better than it is" if wl >= 635 else ""),
        })
    return out


def switch_rows(switches, follow_by_name):
    """One row per switch: speed only (reach and heat are set by the drive colour, see colour rows)."""
    def again(f):
        return " ".join(f"{r:g}" for r in f.get("follows_again_Hz") or [])

    return [{**{k: "" for k in FIELDS}, "row": "switch", "name": sw.name, "wavelength_nm": sw.wavelength,
             "status": sw.status, "max_following_rate_Hz": follow_by_name[sw.name]["max_rate"],
             "first_failure_Hz": follow_by_name[sw.name].get("first_failure_Hz") or "",
             "follows_again_Hz": again(follow_by_name[sw.name]), "note": sw.note}
            for sw in switches]


def legacy_switch_rows(switches, light_by_wl, heat_by_wl, follow_by_name, grid):
    """The pre-2026-10-06 per-switch table (reach and heat repeated per switch). Kept for run_summary.json only."""
    out = []
    for sw in switches:
        v = _volumes(light_by_wl[sw.wavelength]["fluence"], grid.vol)
        out.append(dict(switch=sw.name, wavelength_nm=sw.wavelength, volume_mm3_per_mW_at_3mWmm2=v[3.0],
                        peak_warming_C_per_mW=heat_by_wl[sw.wavelength]["peak_per_mW"],
                        max_following_rate_Hz=follow_by_name[sw.name]["max_rate"]))
    return out


def write_csv(table, path=None):
    path = path or RESULTS / "tradeoff.csv"
    with open(path, "w", newline="") as f:
        f.write(f"# {DEMO_TAG}. Not research. 200 um / NA 0.22 fibre, homogeneous brain tissue model.\n")
        f.write("# row=colour: reach and warming per colour (every switch borrows ChR2's light sensitivity, "
                "so these depend on colour only). row=switch: speed only.\n")
        f.write("# Volumes: light >= threshold at 10 mW output, divided by 10. Warming: steady state, continuous light.\n")
        f.write("# Following rate (toy result; read the order, not the numbers): highest tested rate up to which EVERY tested "
                "rate (2 ms pulses at 3 mW/mm^2, 20 pulses) has >=95% of pulses giving exactly one spike (one miss allowed); "
                "the first failure ends the run. first_failure_Hz: lowest failing rate. follows_again_Hz: rates above it "
                "where 1:1 returns, a resonance of this toy cell, not of the light switch.\n")
        f.write("# Measured (Klapoetke 2014): ChrimsonR follows at least 20 Hz, comparable to ChR2(H134R); "
                "Chronos 5-60 Hz (530 nm, 2 ms, 40 pulses). The ChrimsonR row is a limit of the simplified stand-in.\n")
        f.write(f"# {RED_CAVEAT}\n")
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in table:
            w.writerow({k: (f"{r[k]:.4g}" if isinstance(r[k], float) else r[k]) for k in FIELDS})
    return path


def plot(colours, switches_):
    import textwrap

    import matplotlib.pyplot as plt
    from matplotlib.transforms import blended_transform_factory

    def bars(ax, t, labels, vals, cols, title, texts):
        y = np.arange(len(labels))[::-1]
        ax.barh(y, vals, color=cols, height=0.65)
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=12.5)
        ax.set_title(title, fontsize=14.5, loc="left", color=t["fg"])
        ax.set_xlim(0, vals.max() * 1.55 if vals.max() > 0 else 1)
        for yi, v, s in zip(y, vals, texts):
            ax.text(v, yi, "  " + s, va="center", color=t["fg"], fontsize=13)
        ax.grid(axis="y", visible=False)

    def note(ax, t, text, width=70):
        """Wrapped muted text under an axis (on the figure itself, not only in the README)."""
        ax.set_xlabel(textwrap.fill(text, width), loc="left", color=t["muted"], fontsize=10.5, labelpad=8)

    def make(theme):
        fig, (head, *axes) = plt.subplots(4, 1, figsize=(8, 14.5), layout="constrained",
                                          gridspec_kw=dict(height_ratios=[0.7, 3, 3, 4]))
        t = apply_theme(fig, axes, theme)
        head.set_axis_off()
        head.text(0.02, 0.5, f"{DEMO_TAG} · 200 µm fibre, homogeneous tissue\nReach = tissue lit above 3 mW/mm² (at 10 mW, per mW)\n"
                  f"{RED_CAVEAT}", color=t["muted"], fontsize=11.5, va="center", ha="left",
                  transform=blended_transform_factory(fig.transFigure, head.transAxes))
        wl_labels = lambda bound: [f"{r['wavelength_nm']} nm\n{COLOUR_NAMES.get(r['wavelength_nm'], '')}"
                                   + (f"\n(toy {bound} bound)" if r["wavelength_nm"] >= 635 else "") for r in colours]
        wl_cols = [WAVELENGTH_COLOURS[r["wavelength_nm"]] for r in colours]
        reach = np.array([r["volume_mm3_per_mW_at_3mWmm2"] for r in colours])
        heat_ = np.array([r["peak_warming_C_per_mW"] for r in colours])
        bars(axes[0], t, wl_labels("upper"), reach, wl_cols, "Reach by colour (mm³ per mW)", [f"{v:.3f}" for v in reach])
        bars(axes[1], t, wl_labels("lower"), heat_, wl_cols, "Heat by colour (°C per mW, continuous light)", [f"{v:.3f}" for v in heat_])
        note(axes[1], t, SHARED_NOTE)
        speed = np.array([r["max_following_rate_Hz"] for r in switches_], float)
        texts = [f"{v:.0f} Hz (toy)" + ("*" if "Chrimson" in r["name"] else "") for v, r in zip(speed, switches_)]
        bars(axes[2], t, [f"{r['name']}\n{r['wavelength_nm']} nm" for r in switches_], speed,
             SWITCH_COLOURS[: len(switches_)], "Speed by switch (Hz), toy result:\nread the order, not the numbers", texts)
        note(axes[2], t, f"{TOY_SPEED_NOTE} Headline speed = last rate before the first failure. "
             f"*Limit of the simplified stand-in, not of real ChrimsonR. Measured: {CHRIMSONR_QUOTE}. {CHRONOS_QUOTE}.")
        fig.suptitle(TITLE, fontsize=17, fontweight="bold", color=t["fg"], x=0.02, ha="left")
        return fig

    return save_themed(make, "tradeoff")


def rebuild_from_cache():
    """Rebuild tradeoff.csv and the figure from the cached light maps and run_summary.json (no re-run)."""
    from . import heat, light, opsin

    summary = json.loads((RESULTS / "run_summary.json").read_text())
    lights = {}
    for wl in light.WAVELENGTHS:
        d = np.load(RESULTS / f"light_fibre200um_{wl}nm.npz")
        lights[wl] = dict(fluence=d["fluence_per_W"].astype(float), r_edges=d["r_edges"], z_edges=d["z_edges"])
    r0 = lights[light.WAVELENGTHS[0]]
    grid = heat.Grid(r0["r_edges"], r0["z_edges"])
    heat_by_wl = {int(k): v for k, v in summary["heat_per_wavelength"].items()}
    sws = opsin.switches(calibrated=False)
    follow = {s.name: dict(max_rate=summary["switches"][s.name]["max_following_rate_Hz"],
                           first_failure_Hz=summary["switches"][s.name].get("first_failure_Hz"),
                           follows_again_Hz=summary["switches"][s.name].get("follows_again_Hz")) for s in sws}
    colours, switches_ = colour_rows(lights, heat_by_wl, grid), switch_rows(sws, follow)
    write_csv(colours + switches_)
    plot(colours, switches_)
    summary.setdefault("tradeoff_per_switch_legacy", legacy_switch_rows(sws, lights, heat_by_wl, follow, grid))
    summary["tradeoff"] = dict(colours=colours, switches=switches_)
    (RESULTS / "run_summary.json").write_text(json.dumps(summary, indent=1, default=float))
    return colours, switches_


if __name__ == "__main__":
    rebuild_from_cache()
