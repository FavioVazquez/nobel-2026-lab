"""Run every step and write results/. Educational demo, toy model.

    python -m simulator.run_all            # full run (photon counts below)
    python -m simulator.run_all --quick    # small photon counts, for a smoke test
"""
import argparse
import json
import platform
import time

import numpy as np

from . import heat, light, neuron, opsin, tradeoff
from .common import DEMO_TAG, RESULTS, SWITCH_COLOURS, WAVELENGTH_COLOURS, apply_theme, save_themed, titles

# Published figures (Stujenske et al. 2015, verified in full text; see SOURCES.md)
STUJENSKE_532_SLICE_PLATEAU_C = 2.2
STUJENSKE_532_MAX_VOXEL_C = 4.1
STUJENSKE_532_VOL_1C_MM3 = 1.0
STUJENSKE_445_MODEL_C_PER_MW = 0.35
CHRISTIE_445_MEASURED_C_PER_MW = 0.42
STUJENSKE_473_PULSED_BAND_C = (0.5, 0.9)


def near_tip_slice_max(grid, T, z_c, depth=0.5):
    prof = heat.slice_mean_profile(grid, T)
    m = (z_c > 0) & (z_c < depth)
    return float(prof[m].max())


def plot_heat(transients):
    import matplotlib.pyplot as plt

    def make(theme):
        fig, ax = plt.subplots(figsize=(8, 6.4), layout="constrained")
        t = apply_theme(fig, [ax], theme)
        for (label, colour, ls), (tt, pk) in transients.items():
            ax.plot(tt, pk, color=colour, lw=3, ls=ls, label=label)
        ax.set_xlabel("Time with the light on (s)", fontsize=16)
        ax.set_ylabel("Warming at the hottest point (°C)", fontsize=16)
        ax.set_ylim(0, 1.45 * max(pk.max() for pk in (v[1] for v in transients.values())))
        titles(fig, ax, t, "Same peak power, less light on average:\npulsing cuts the warming",
               "470 nm, 10 mW peak, 200 µm fibre")
        leg = ax.legend(fontsize=13, frameon=False, loc="upper right")
        for txt in leg.get_texts():
            txt.set_color(t["fg"])
        return fig

    return save_themed(make, "heat_transient")


def heat_pulse_trains(g, q470):
    """10 s at 470 nm, 10 mW peak: continuous, 50 % and 10 % duty. Returns plot traces and peak values."""
    trans, peaks = {}, {}
    sub = 5  # backward-Euler steps per light-on and per light-off phase (one step per phase read peaks 3-7 % low)
    for label, on, period, ls, avg in (("continuous", None, None, "-", 10),
                                       ("50 % duty (25 ms on, 20 Hz)", 0.025, 0.05, "--", 5),
                                       ("10 % duty (10 ms on, 10 Hz)", 0.010, 0.1, ":", 1)):
        segs = [(10.0, 1.0, 0.05)] if on is None else \
            [(on, 1.0, on / sub), (period - on, 0.0, (period - on) / sub)] * int(round(10 / period))
        tt, pk, _, _ = g.transient(q470, segs, 0.05)
        if on:  # plot the per-period maximum so the 10 s trace stays readable
            spp = 2 * sub
            tt, pk = np.r_[0.0, tt[spp::spp]], np.r_[0.0, pk[1:].reshape(-1, spp).max(1)]
        trans[(f"{label}: {avg} mW average", WAVELENGTH_COLOURS[470], ls)] = (tt, pk)
        peaks[label] = float(pk.max())
    return trans, peaks


FOLLOW_TITLE = "Too fast, and spikes start to fail (toy neuron)"
RESONANCE_NOTE = "a resonance of this toy cell, not of the light switch"


def resonance_window(follow):
    """Rates above a switch's first failure where 1:1 following returns (toy squid-axon resonance)."""
    again = sorted({r for v in follow.values() for r in v.get("follows_again_Hz", [])})
    return (again[0], again[-1]) if again else None


def plot_following(follow):
    import matplotlib.pyplot as plt

    win = resonance_window(follow)

    def make(theme):
        fig, ax = plt.subplots(figsize=(8, 6.8), layout="constrained")
        t = apply_theme(fig, [ax], theme)
        if win:
            ax.axvspan(win[0] / 1.04, win[1] * 1.04, color=t["grid"], alpha=0.55, lw=0, zorder=0)
            ax.annotate(f"shaded: 1:1 returns at {win[0]:g}-{win[1]:g} Hz,\n" + RESONANCE_NOTE.replace("cell, ", "cell,\n"),
                        (win[0] / 1.04, 72), xytext=(96, 72), ha="right", va="center", fontsize=10.5, color=t["fg"], zorder=3,
                        arrowprops=dict(arrowstyle="->", color=t["muted"], lw=1.2),
                        bbox=dict(boxstyle="round,pad=0.3", fc=t["bg"], ec=t["muted"], lw=0.8))
        for c, (name, r) in zip(SWITCH_COLOURS, follow.items()):
            ax.plot(r["rates"], 100 * r["fraction"], "o-", color=c, lw=2.6, ms=6,
                    label=f"{name}: {r['max_rate']:g} Hz", zorder=2)
            if r["max_rate"]:
                ax.plot([r["max_rate"]], [100 * r["fraction"][list(r["rates"]).index(r["max_rate"])]], "o",
                        ms=13, mfc="none", mec=c, mew=2.4, zorder=4)
        ax.axhline(95, color=t["muted"], ls="--", lw=1.5)
        ax.set_xscale("log")
        ax.set_xticks([10, 20, 50, 100, 200])
        ax.set_xticklabels(["10", "20", "50", "100", "200"])
        ax.set_xlabel("Light pulses per second (Hz)", fontsize=16)
        ax.set_ylabel("Pulses answered by exactly one spike (%)", fontsize=15)
        ax.set_ylim(-3, 105)
        titles(fig, ax, t, FOLLOW_TITLE,
               "Hodgkin-Huxley neuron, 2 ms pulses at 3 mW/mm²\n"
               "20 pulses · ringed: headline speed = last rate before the first failure\n(95 % rule: one miss in 20 allowed)")
        leg = ax.legend(fontsize=11.5, frameon=False, loc="lower left", title="headline speed (toy)")
        leg.get_title().set_color(t["muted"])
        for txt in leg.get_texts():
            txt.set_color(t["fg"])
        return fig

    return save_themed(make, "following")


def dt_check(follow, chk):
    """Compare the following run at neuron.DT with the same run at neuron.DT_CHECK."""
    moved = {k: {f"{r:g}": [float(a), float(b)] for r, a, b in zip(follow[k]["rates"], follow[k]["fraction"], chk[k]["fraction"])
                 if a != b} for k in follow}
    below = [abs(a - b) for k in follow for r, a, b in zip(follow[k]["rates"], follow[k]["fraction"], chk[k]["fraction"])
             if r <= follow[k]["max_rate"]]
    return dict(dt_ms=neuron.DT, dt_check_ms=neuron.DT_CHECK, method="explicit midpoint (RK2), fixed step",
                max_rate_at_dt_check={k: v["max_rate"] for k, v in chk.items()},
                follows_again_at_dt_check={k: v["follows_again_Hz"] for k, v in chk.items()},
                max_abs_fraction_change=float(max(np.abs(np.asarray(chk[k]["fraction"]) - follow[k]["fraction"]).max()
                                                  for k in follow)),
                max_abs_fraction_change_up_to_headline=float(max(below)),
                fractions_that_moved_dt_vs_dt_check=moved,
                converged=all(chk[k]["max_rate"] == follow[k]["max_rate"] for k in follow))


def main(quick=False):
    timings, summary = {}, {"tag": DEMO_TAG, "machine": platform.processor() or platform.machine(),
                            "python": platform.python_version()}
    n_main = 20_000 if quick else 200_000
    RESULTS.mkdir(parents=True, exist_ok=True)

    t = time.perf_counter()
    lights = light.run(n_main, light.WAVELENGTHS, core_radius=0.1, na=0.22, tag="fibre200um")
    timings["light_main_s"] = time.perf_counter() - t
    summary["light"] = {}
    for wl, res in lights.items():
        opt = light.optics(wl)
        fit, pred = light.diffusion_check(res, opt)
        exact = light.transport_decay(opt)
        summary["light"][wl] = dict(photons=res["n_photons"], seconds=res["seconds"], photon_steps=res["steps"],
                                    mua_per_cm=opt.mua * 10, mus_per_cm=opt.mus * 10, g=opt.g,
                                    absorbed_fraction_in_tally=float(res["absorbed"].sum()),
                                    mu_eff_fit_per_mm=fit, mu_eff_transport_exact_per_mm=exact,
                                    rel_error_vs_transport=abs(fit - exact) / exact,
                                    mu_eff_diffusion_per_mm=pred, diffusion_theory_bias=(pred - exact) / exact,
                                    rel_error=abs(fit - pred) / pred)
    light.plot_depth_profiles(lights)

    t = time.perf_counter()
    comp = {532: light.simulate(light.optics(532), n_main, core_radius=0.031, na=0.22, seed=11),
            445: light.simulate(light.optics(445), n_main, core_radius=0.1, na=0.22, seed=12)}
    timings["light_comparison_s"] = time.perf_counter() - t

    t = time.perf_counter()
    r0 = lights[light.WAVELENGTHS[0]]
    grids = {k: heat.Grid(r0["r_edges"], r0["z_edges"], heat.thermal_params(k))
             for k in ("w_blood", "w_blood_low", "w_blood_high")}
    g = grids["w_blood"]
    z_c = 0.5 * (r0["z_edges"][1:] + r0["z_edges"][:-1])
    heat_by_wl = {}
    for wl, res in lights.items():
        T = {k: gg.steady(res["power_density"] * 1e-3) for k, gg in grids.items()}  # 1 mW
        heat_by_wl[wl] = dict(peak_per_mW=float(T["w_blood"].max()),
                              peak_per_mW_low=float(T["w_blood_low"].max()),
                              peak_per_mW_high=float(T["w_blood_high"].max()),
                              slice_per_mW=near_tip_slice_max(g, T["w_blood"], z_c))
    # comparison with Stujenske 2015
    q532 = comp[532]["power_density"] * 0.010
    T532 = g.steady(q532)
    tt, pk, _, _ = g.transient(q532, [(120.0, 1.0)], 0.5)
    i60 = int(round(60 / 0.5))
    T445 = g.steady(comp[445]["power_density"] * 1e-3)
    summary["heat_comparison"] = {
        "case_532nm_62um_10mW": dict(
            slice_plateau_C=near_tip_slice_max(g, T532, z_c), published_slice_plateau_C=STUJENSKE_532_SLICE_PLATEAU_C,
            max_voxel_C=float(T532.max()), published_max_voxel_C=STUJENSKE_532_MAX_VOXEL_C,
            volume_ge_1C_mm3=float(heat.volume_above(g, T532, 1.0)), published_volume_ge_1C_mm3=STUJENSKE_532_VOL_1C_MM3,
            extra_rise_60_to_120s_fraction=float((pk[-1] - pk[i60]) / pk[-1]),
            published_extra_rise_60_to_120s="< 5 %"),
        "case_445nm_200um": dict(peak_C_per_mW=float(T445.max()), slice_C_per_mW=near_tip_slice_max(g, T445, z_c),
                                 published_model_C_per_mW=STUJENSKE_445_MODEL_C_PER_MW,
                                 published_measured_C_per_mW=CHRISTIE_445_MEASURED_C_PER_MW),
    }
    # pulse trains at 470 nm, 10 mW peak, 20 Hz, 10 s; plus continuous
    q470 = lights[470]["power_density"] * 0.010
    trans, peaks = heat_pulse_trains(g, q470)
    summary["heat_pulse_trains_470nm_10mW"] = peaks
    summary["heat_pulse_trains_470nm_10mW"]["published_band_C (5-10 mW, <=50 % duty)"] = STUJENSKE_473_PULSED_BAND_C
    plot_heat(trans)
    summary["heat_per_wavelength"] = heat_by_wl
    timings["heat_s"] = time.perf_counter() - t

    t = time.perf_counter()
    sws = opsin.switches()
    summary["switches"] = {s.name: dict(status=s.status, wavelength=s.wavelength, gd_scale=s.gd_scale,
                                        tau_off_ms=opsin.tau_off(s)) for s in sws}
    n_pulses = 10 if quick else 20
    follow = neuron.following(sws, neuron.RATES_HZ, n_pulses=n_pulses)
    follow = {s.name: follow[s.name] for s in sws}
    for name, r in follow.items():
        summary["switches"][name].update(max_following_rate_Hz=r["max_rate"], first_failure_Hz=r["first_failure_Hz"],
                                         follows_again_Hz=r["follows_again_Hz"], g_mS_cm2=r["g"],
                                         fraction_by_rate=dict(zip(map(str, r["rates"]), r["fraction"].tolist())))
    summary["following_rule"] = ("headline speed = highest tested rate up to which every tested rate has >= 95 % of "
                                 f"pulses giving exactly one spike ({n_pulses} pulses: at most one miss); the first "
                                 "failure ends the run. follows_again_Hz: " + RESONANCE_NOTE)
    summary["following_resonance_window_Hz"] = resonance_window(follow)
    if not quick:  # time-step convergence check: same run at half the step
        chk = neuron.following(sws, neuron.RATES_HZ, n_pulses=n_pulses, dt=neuron.DT_CHECK)
        summary["following_dt_check"] = dt_check(follow, chk)
    plot_following(follow)
    timings["opsin_neuron_s"] = time.perf_counter() - t

    colours, switch_rows = tradeoff.colour_rows(lights, heat_by_wl, g), tradeoff.switch_rows(sws, follow)
    tradeoff.write_csv(colours + switch_rows)
    tradeoff.plot(colours, switch_rows)
    summary["tradeoff"] = dict(colours=colours, switches=switch_rows)
    # the earlier per-switch table (reach and heat repeated for each 470 nm switch), kept for reference
    summary["tradeoff_per_switch_legacy"] = tradeoff.legacy_switch_rows(sws, lights, heat_by_wl, follow, g)
    summary["timings_s"] = timings
    (RESULTS / "run_summary.json").write_text(json.dumps(summary, indent=1, default=float))
    print(json.dumps(summary, indent=1, default=float))
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    main(ap.parse_args().quick)
