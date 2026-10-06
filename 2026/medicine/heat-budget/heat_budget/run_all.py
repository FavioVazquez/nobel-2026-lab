"""Run the heat budget end to end and write results/. Educational demo, toy model.

    python -m heat_budget.run_all               # recipe grid, recruitment, figures, 60 frames 1920x1080
    python -m heat_budget.run_all --vertical    # also the 1080x1920 frame sequence
    python -m heat_budget.run_all --no-frames   # skip the frame sequence
"""
import argparse
import json
import platform
import time

from . import frames, recipe, recruit
from .common import DEFAULT_LIMIT_C, LIMITS_C, RESULTS, TOP_LINE, single_pulse_rise, steady_per_mW


def main(vertical=False, make_frames=True):
    RESULTS.mkdir(parents=True, exist_ok=True)
    timings = {}
    t = time.perf_counter()
    heat = {wl: dict(steady_C_per_mW=steady_per_mW(wl),
                     one_pulse_rise_C_per_mW={f"{w:g}ms": float(single_pulse_rise(wl)[1][int(round(w / 0.05))])
                                              for w in recipe.WIDTHS_MS})
            for wl in recruit.WAVELENGTHS}
    timings["heat_model_s"] = time.perf_counter() - t

    t = time.perf_counter()
    rec = recipe.run()
    timings["recipe_s"] = time.perf_counter() - t

    t = time.perf_counter()
    pop = recruit.run()
    timings["recruit_s"] = time.perf_counter() - t

    if make_frames:
        t = time.perf_counter()
        frames.render(470, DEFAULT_LIMIT_C)
        timings["frames_s"] = time.perf_counter() - t
    if vertical:
        t = time.perf_counter()
        frames.render(470, DEFAULT_LIMIT_C, vertical=True)
        timings["frames_vertical_s"] = time.perf_counter() - t

    per_limit = {wl: {f"{lim:g}C": e["by_sigma"][f"{recruit.SIGMA:g}"]["at_limit"][f"{lim:g}"] for lim in LIMITS_C}
                 for wl, e in pop["colours"].items()}
    spread_all = {wl: {s: e["by_sigma"][s]["at_limit"]["1"]["recruited"] for s in e["by_sigma"]}
                  for wl, e in pop["colours"].items()}
    head = [str(w) for w in recruit.HEADLINE_COLOURS]
    headline = {wl: v for wl, v in per_limit.items() if wl in head}
    spread = {wl: v for wl, v in spread_all.items() if wl in head}
    upper = {wl: dict(note=recruit.UPPER_BOUND_NOTE, at_limit=per_limit[wl], by_spread_at_1C=spread_all[wl])
             for wl in per_limit if wl not in head}
    summary = dict(
        tag=TOP_LINE, machine=platform.processor() or platform.machine(), python=platform.python_version(),
        heat_model=heat, recipe_info=rec["info"], best_recipes=rec["best"],
        neurons_recruited_continuous_light=headline, recruited_at_1C_by_expression_spread=spread,
        toy_upper_bound_only=upper,
        caveats=["toy model: homogeneous tissue, one activation threshold (3 mW/mm^2), one expression law (lognormal)",
                 "every switch borrows ChR2's light sensitivity; no 635 nm switch is modelled, 635 nm uses the same threshold",
                 "red (635 nm) is a labelled toy upper bound only, never a headline: it ignores absorption outside blood "
                 "and uses a uniform block much bigger than a thin cortex",
                 "B's heat model runs about 1.5-3x hotter than Stujenske et al. 2015, so per-degree counts may be underestimates"],
        timings_s=timings)
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=1, default=float))
    print(json.dumps(dict(best_recipes=rec["best"], headline=headline, spread=spread, toy_upper_bound_only=upper,
                          timings_s=timings), indent=1, default=float))
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--vertical", action="store_true", help="also write the 1080x1920 frame sequence")
    ap.add_argument("--no-frames", action="store_true")
    a = ap.parse_args()
    main(a.vertical, not a.no_frames)
