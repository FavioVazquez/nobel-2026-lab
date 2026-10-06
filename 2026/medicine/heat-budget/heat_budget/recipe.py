"""The best pulse recipe under a heat limit. Educational demo, toy model.

For each switch, a grid over pulse width x pulse rate x peak fibre power:
  * warming: B's Pennes heat model (linear in power, scaled), as an upper estimate for a long train
    (common.warming_C: steady warming of the average power plus one pulse's rise);
  * following score: the fraction of light pulses that produce exactly one spike in B's Hodgkin-Huxley
    neuron driven by B's photocycle (B's converged fixed step: 0.01 ms, 2nd-order Runge-Kutta, every light edge on the step grid);
    the neuron sits on the fibre axis, 0.5 mm or 1.0 mm below the tip (REF_DEPTHS_MM), and sees B's
    light map there.
Best recipe per switch, depth and heat limit: the fastest rate that follows (score >= 0.95) with warming
at or under the limit, where, as in B's rule, every lower tested rate must also follow at the same width
and power (B's toy neuron has isolated "islands" of 1:1 firing at high rates, e.g. ChR2 at 150 Hz but
not 80-125 Hz). Ties: higher score, then less warming. If nothing follows, the highest score.
"""
import csv
import os
from dataclasses import replace

import numpy as np

from simulator import light, neuron, opsin
from simulator.tradeoff import THRESHOLD

from .common import DEMO_TAG, LIMITS_C, RESULTS, WAVELENGTH_COLOURS, apply_theme, light_map, save_themed, titles, warming_C

SWITCH_NAMES = ("ChR2 (Williams 2013)", "Chronos (simplified)", "ChrimsonR (simplified)")
SLUGS = {"ChR2 (Williams 2013)": "chr2", "Chronos (simplified)": "chronos", "ChrimsonR (simplified)": "chrimsonr"}
WIDTHS_MS = (0.5, 1.0, 2.0, 5.0, 10.0)
RATES_HZ = (10, 20, 40, 60, 80, 100, 125, 150, 200)
POWERS_MW = tuple(float(p) for p in np.round(0.25 * 2 ** (np.arange(17) / 2), 4))  # 0.25 ... 64 mW
REF_DEPTHS_MM = (0.5, 1.0)  # our choice: neurons 0.5 and 1.0 mm below the tip, on the fibre axis
REF_DEPTH_MM = REF_DEPTHS_MM[0]
N_PULSES = 20  # as in B's following test
FOLLOW = 0.95  # B's rule: at least 95 % of pulses give exactly one spike
# B's neuron uses a fixed step (0.01 ms, explicit midpoint); for very bright light the photocycle's opening
# rate times the step gets large and a fixed explicit step becomes inaccurate (the earlier 0.025 ms Euler
# step diverged above roughly 170 mW/mm^2). Grid points brighter than this at the neuron are not computed
# (NaN). Our choice, kept from the first run so the grid stays comparable.
MAX_IRRADIANCE = 30.0


def ref_irradiance_per_mW(wl, depth=REF_DEPTH_MM):
    """mW/mm^2 at the reference neuron per mW out of the fibre (B's on-axis depth profile)."""
    z, phi = light.depth_profile(light_map(wl))
    return float(np.interp(depth, z, phi))


def pick_switches(names=SWITCH_NAMES):
    sws = {s.name: s for s in opsin.switches()}
    return [sws[n] for n in names]


def _score_one_rate(batch, gs, wi, level, rate, widths, n_pulses):
    """Following score per column at one rate (runs in a worker process). Spikes are detected on the fly
    and the light is a shared on/off mask per width, so memory stays small at the 0.01 ms step."""
    masks = np.stack([neuron.pulse_mask([rate], n_pulses, w, 1.0)[0][:, 0] > 0 for w in widths], 1)
    on = neuron.pulse_mask([rate], n_pulses, widths[0], 1.0)[1][0]
    sp = neuron.simulate(batch, (masks, wi, level), gs, record=False)
    edges = np.append(on, on[-1] + (on[1] - on[0]))
    return np.array([(np.histogram(s, bins=edges)[0] == 1).mean() if (s < on[0]).sum() == 0 else 0.0 for s in sp])


def following_scores_multi(sws, depths=REF_DEPTHS_MM, widths=WIDTHS_MS, rates=RATES_HZ, powers=POWERS_MW,
                           n_pulses=N_PULSES, workers=None):
    """{depth: (score array (switch, width, rate, power), info)}. NaN where a pulse is not shorter than the
    period. All depths share one batch; each rate's columns are split into chunks of about equal work
    (slow rates need more time steps) and run in worker processes (the neuron loop is serial in time)."""
    from concurrent.futures import ProcessPoolExecutor

    assert all(s.kind == "williams" for s in sws), "the batched run needs one model kind"
    gs = np.array([neuron.scale_conductance(s, THRESHOLD, 2.0) for s in sws])  # B's 15 uA/cm^2 calibration
    irr = np.array([[ref_irradiance_per_mW(s.wavelength, d) for s in sws] for d in depths])
    D, S, W, R, P = len(depths), len(sws), len(widths), len(rates), len(powers)
    di, si, wi, pi = (a.ravel() for a in np.meshgrid(np.arange(D), np.arange(S), np.arange(W), np.arange(P), indexing="ij"))
    level = irr[di, si] * np.asarray(powers, float)[pi]
    ok = level <= MAX_IRRADIANCE
    di, si, wi, pi, level = di[ok], si[ok], wi[ok], pi[ok], level[ok]
    batch = replace(sws[0], wavelength=np.array([s.wavelength for s in sws], float)[si],
                    gd_scale=np.array([s.gd_scale for s in sws], float)[si])
    work = [n_pulses * 1000.0 / r + 60.0 for r in rates]
    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    out = np.full((D, S, W, R, P), np.nan)
    with ProcessPoolExecutor(workers) as ex:
        jobs = []
        for ri, r in enumerate(rates):
            for cols in np.array_split(np.arange(level.size), max(1, int(round(work[ri] / min(work))))):
                sub = replace(batch, wavelength=batch.wavelength[cols], gd_scale=batch.gd_scale[cols])
                jobs.append((ri, cols, ex.submit(_score_one_rate, sub, gs[si[cols]], wi[cols], level[cols], r,
                                                 tuple(widths), n_pulses)))
        for ri, cols, j in jobs:
            out[di[cols], si[cols], wi[cols], ri, pi[cols]] = j.result()
    duty = np.asarray(widths, float)[:, None] * np.asarray(rates, float)[None, :] / 1000.0
    out[:, :, duty >= 1.0, :] = np.nan
    return {d: (out[k], dict(g_mS_cm2=gs.tolist(), ref_irradiance_per_mW=irr[k].tolist())) for k, d in enumerate(depths)}


def following_scores(sws, widths=WIDTHS_MS, rates=RATES_HZ, powers=POWERS_MW, n_pulses=N_PULSES, depth=REF_DEPTH_MM,
                     workers=None):
    """Score array (switch, width, rate, power) and info at one depth (see following_scores_multi)."""
    return following_scores_multi(sws, (depth,), widths, rates, powers, n_pulses, workers)[depth]


def grid_table(sws, scores, widths=WIDTHS_MS, rates=RATES_HZ, powers=POWERS_MW, depth=REF_DEPTH_MM):
    rows = []
    for k, s in enumerate(sws):
        irr = ref_irradiance_per_mW(s.wavelength, depth)
        W, R, P = np.meshgrid(widths, rates, powers, indexing="ij")
        heat_c = warming_C(s.wavelength, P, W, R)
        lower_ok = np.cumprod(np.nan_to_num(scores[k], nan=0.0) >= FOLLOW, axis=1).astype(bool)  # along rate
        for idx in np.ndindex(W.shape):
            sc = scores[(k,) + idx]
            if np.isnan(sc):
                continue
            rows.append(dict(switch=s.name, wavelength_nm=s.wavelength, ref_depth_mm=depth,
                             width_ms=float(W[idx]), rate_Hz=float(R[idx]),
                             peak_mW=float(P[idx]), duty=float(W[idx] * R[idx] / 1000),
                             irradiance_at_ref_mW_mm2=float(irr * P[idx]), following_score=float(sc),
                             warming_C_estimate=float(heat_c[idx]), follows_at_all_lower_rates=bool(lower_ok[idx]),
                             **{f"within_{lim:g}C": bool(heat_c[idx] <= lim) for lim in LIMITS_C}))
    return rows


def best_recipe(rows, switch, limit, depth=REF_DEPTH_MM):
    """Fastest following rate (B's rule) with warming <= limit (ties: higher score, less warming)."""
    cand = [r for r in rows if r["switch"] == switch and r["ref_depth_mm"] == depth and r["warming_C_estimate"] <= limit]
    if not cand:
        return None
    ok = [r for r in cand if r["follows_at_all_lower_rates"]]
    key = (lambda r: (r["rate_Hz"], r["following_score"], -r["warming_C_estimate"])) if ok else \
        (lambda r: (r["following_score"], r["rate_Hz"], -r["warming_C_estimate"]))
    return dict(max(ok or cand, key=key), limit_C=limit, reaches_95=bool(ok))


def write_csv(rows, name, header_lines):
    path = RESULTS / name
    RESULTS.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        for h in [f"{DEMO_TAG}. Not research, not for lab or clinical use."] + header_lines:
            f.write(f"# {h}\n")
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in r.items()})
    return path


HEADER = [
    f"Neuron on axis, {' or '.join(f'{d:g}' for d in REF_DEPTHS_MM)} mm below a 200 um / NA 0.22 fibre tip. {N_PULSES} pulses per train.",
    "following_score = fraction of pulses answered by exactly one spike (B's Hodgkin-Huxley neuron + photocycle).",
    "warming_C_estimate = upper estimate of the peak rise at the hottest point for a long train (steady mean + one pulse).",
    f"Grid points with more than {MAX_IRRADIANCE:g} mW/mm^2 at the neuron are not computed (B's fixed step is not accurate there).",
]


def _panel(ax, fig, t, sw, scores_k, depth, limit, widths, rates, powers, best):
    from matplotlib.colors import LinearSegmentedColormap

    W, R, P = np.meshgrid(widths, rates, powers, indexing="ij")
    heat_c = warming_C(sw.wavelength, P, W, R)
    allowed = np.where(heat_c <= limit, scores_k, np.nan)
    best_score = np.nanmax(np.where(np.isnan(allowed), -1.0, allowed), axis=-1)
    best_score = np.where(best_score < 0, np.nan, best_score)
    need = np.where(np.nan_to_num(scores_k, nan=0.0) >= FOLLOW, heat_c, np.inf).min(-1)
    colour = WAVELENGTH_COLOURS[int(sw.wavelength)]
    cmap = LinearSegmentedColormap.from_list("f", [t["bg"], colour])
    cmap.set_bad(t["grid"])
    m = ax.pcolormesh(np.arange(len(rates) + 1) - 0.5, np.arange(len(widths) + 1) - 0.5, 100 * best_score,
                      cmap=cmap, vmin=0, vmax=100, shading="flat")
    for (i, j), v in np.ndenumerate(best_score):
        ax.text(j, i, "n/a" if np.isnan(v) else f"{100 * v:.0f}", ha="center", va="center", fontsize=10.5,
                color=t["fg"] if np.isnan(v) or v < 0.6 else t["bg"])
    ok = need <= limit  # 95 % following is affordable within the limit (at some tested power)
    for i, j in np.ndindex(ok.shape):  # staircase outline of that region: the heat-limit contour on this grid
        for di, dj in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            ii, jj = i + di, j + dj
            inside = 0 <= ii < ok.shape[0] and 0 <= jj < ok.shape[1]
            if ok[i, j] and not (inside and ok[ii, jj]):
                if dj:
                    ax.plot([j + dj / 2] * 2, [i - 0.5, i + 0.5], color=t["fg"], lw=3.2, solid_capstyle="round")
                else:
                    ax.plot([j - 0.5, j + 0.5], [i + di / 2] * 2, color=t["fg"], lw=3.2, solid_capstyle="round")
    if best is not None and best["reaches_95"]:
        ax.plot(list(rates).index(int(best["rate_Hz"])), list(widths).index(best["width_ms"]), marker="*", ms=26,
                mec=t["fg"], mfc="none", mew=2.2)
    ax.set_xticks(range(len(rates)))
    ax.set_xticklabels([str(r) for r in rates], fontsize=12)
    ax.set_yticks(range(len(widths)))
    ax.set_yticklabels([f"{w:g}" for w in widths], fontsize=12)
    ax.set_ylabel("Pulse width (ms)", fontsize=14)
    ax.grid(False)
    ax.set_title(f"Neuron {depth:g} mm below the tip", loc="left", fontsize=14.5, color=t["fg"])
    return m


def plot(sw, scores_by_depth, limit=1.0, widths=WIDTHS_MS, rates=RATES_HZ, powers=POWERS_MW, best_by_depth=None):
    """Heat map per switch: colour = best % of 1:1 pulses within the limit; line = where 95 % costs the limit."""
    import matplotlib.pyplot as plt

    depths = list(scores_by_depth)

    def make(theme):
        fig, (head, *axes) = plt.subplots(len(depths) + 1, 1, figsize=(8, 4.3 * len(depths) + 1.6), layout="constrained",
                                          gridspec_kw=dict(height_ratios=[0.55] + [4] * len(depths)))
        t = apply_theme(fig, axes, theme)
        head.set_axis_off()
        head.text(0.0, 0.5, f"{DEMO_TAG} · {int(sw.wavelength)} nm · numbers: best % of 1:1 pulses within {limit:g} °C\n"
                  f"outline: 95 % following fits under {limit:g} °C · star: best recipe (fastest rate that\n"
                  f"follows, all slower rates too) · n/a: pulse not shorter than the period", color=t["muted"],
                  fontsize=10.5, va="center", ha="left", transform=head.transAxes)
        for ax, d in zip(axes, depths):
            m = _panel(ax, fig, t, sw, scores_by_depth[d], d, limit, widths, rates, powers,
                       (best_by_depth or {}).get(d))
        axes[-1].set_xlabel("Light pulses per second (Hz)", fontsize=14)
        cb = fig.colorbar(m, ax=list(axes), shrink=0.6)
        cb.set_label("Best % of pulses with exactly one spike, within the limit", color=t["fg"], fontsize=12)
        cb.ax.tick_params(colors=t["fg"])
        fig.suptitle(f"{sw.name}: what {limit:g} °C of warming buys", fontsize=17, fontweight="bold",
                     color=t["fg"], x=0.02, ha="left")
        return fig

    return save_themed(make, f"recipe_{SLUGS.get(sw.name, 'switch')}")


def run(names=SWITCH_NAMES, widths=WIDTHS_MS, rates=RATES_HZ, powers=POWERS_MW, n_pulses=N_PULSES,
        depths=REF_DEPTHS_MM, figures=True):
    sws = pick_switches(names)
    rows, scores, info, best = [], {}, {}, []
    for d, (sc, inf) in following_scores_multi(sws, depths, widths, rates, powers, n_pulses).items():
        scores[d], info[f"{d:g}mm"] = sc, inf
        rows += grid_table(sws, sc, widths, rates, powers, depth=d)
    best = [b for s in sws for d in depths for lim in LIMITS_C if (b := best_recipe(rows, s.name, lim, d))]
    write_csv(rows, "recipe.csv", HEADER)
    write_csv(best, "recipe_best.csv", HEADER + ["Best = fastest rate that follows (>= 95 %, all slower rates too) within the limit."])
    if figures:
        for k, s in enumerate(sws):
            bb = {d: next((b for b in best if b["switch"] == s.name and b["limit_C"] == 1.0 and b["ref_depth_mm"] == d),
                          None) for d in depths}
            plot(s, {d: scores[d][k] for d in depths}, 1.0, widths, rates, powers, best_by_depth=bb)
    return dict(rows=rows, best=best, scores=scores, info=info, switches=sws)
