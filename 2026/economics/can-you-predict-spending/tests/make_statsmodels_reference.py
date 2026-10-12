"""Write tests/statsmodels_reference.json: the same regressions run with statsmodels and SciPy, which the toy does
not depend on. Run once from the toy folder with a Python that has statsmodels (we used statsmodels 0.14.4,
SciPy 1.15.2, pandas 2.2.0; pandas 3 breaks statsmodels 0.14.4): python tests/make_statsmodels_reference.py.
Educational demo, not research."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas
import scipy
import scipy.stats
import statsmodels
import statsmodels.api as sm
from statsmodels.sandbox.regression.gmm import IV2SLS

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from spend import constants as C  # noqa: E402
from spend import model as M  # noqa: E402
from spend import run_all as R  # noqa: E402


def ols_ref(y, X):
    hac = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": C.HAC_LAGS, "use_correction": False})
    classic = sm.OLS(y, X).fit()
    k = X.shape[1]

    def ftest(res, idx):
        R = np.zeros((len(idx), k))
        for i, j in enumerate(idx):
            R[i, j] = 1
        f = res.f_test(R)
        return {"F": float(np.squeeze(f.fvalue)), "p": float(f.pvalue), "df_denom": float(f.df_denom)}

    return {"params": hac.params.tolist(), "bse_hac": hac.bse.tolist(), "bse_classic": classic.bse.tolist(),
            "rsquared": float(hac.rsquared), "rsquared_adj": float(hac.rsquared_adj),
            "f_all_hac": ftest(hac, M.IDX_ALL) if k == 2 * C.LAGS + 1 else None,
            "f_income_hac": ftest(hac, M.IDX_Y) if k == 2 * C.LAGS + 1 else None,
            "f_excluded_classic": ftest(classic, list(range(1, k))),
            "f_excluded_hac": ftest(hac, list(range(1, k)))}


AR_POINTS = (-1.0, 0.0, 0.426, 0.5, 0.558, 1.031, 1.248, 3.0)


def ar_ref(d, m):
    """Anderson-Rubin statistics: statsmodels' HAC and classic Wald F that z_both does not predict y - lam0 * x."""
    y, x, Z = d["y"][m], d["x_iv"][m, 1], d["z_both"][m]
    out = []
    for lam0 in AR_POINTS:
        f = ols_ref(y - lam0 * x, Z)
        out.append([lam0, f["f_excluded_hac"]["F"], f["f_excluded_hac"]["p"], f["f_excluded_classic"]["F"]])
    return out


def effective_f_ref(x, Z):
    """Montiel Olea-Pflueger effective F from statsmodels' HAC covariance of the first-stage coefficients."""
    fit = sm.OLS(x, Z).fit(cov_type="HAC", cov_kwds={"maxlags": C.HAC_LAGS, "use_correction": False})
    pi, V = np.asarray(fit.params)[1:], np.asarray(fit.cov_params())[1:, 1:]
    Zc = Z[:, 1:] - Z[:, 1:].mean(0)
    return float(pi @ Zc.T @ Zc @ pi / np.trace(V @ Zc.T @ Zc))


def main():
    qg, dc, dy, d = R.prepare("nds")
    pre = np.array(qg[C.LAGS:]) <= C.PRE_2020_END
    iv = IV2SLS(d["y"], d["x_iv"], d["z_both"]).fit()
    first = sm.OLS(d["x_iv"], d["z_both"]).fit()
    two_step = sm.OLS(d["y"], first.fittedvalues).fit()
    grid = [(f, d1, d2) for f in (0.3, 1.0, 2.4, 4.86, 9.0, 40.0) for d1, d2 in ((1, 30), (3, 255), (4, 256),
                                                                                  (8, 256), (6, 232))]
    ref = {
        "versions": {"statsmodels": statsmodels.__version__, "scipy": scipy.__version__,
                     "numpy": np.__version__, "pandas": pandas.__version__},
        "sample": "full (rows %d), non-durables + services, data/quarterly.csv sha256 %s" % (len(d["y"]),
                                                                                          C.DERIVED_SHA256),
        "hall_full": ols_ref(d["y"], d["x_hall"]),
        "first_stage_both": ols_ref(d["x_iv"][:, 1], d["z_both"]),
        "effective_F": {k: [effective_f_ref(d["x_iv"][m, 1], d[z][m]) for z in ("z_both", "z_dy", "z_dc", "z_row8")]
                        for k, m in (("full", np.ones(len(d["y"]), bool)), ("pre_2020", pre))},
        "iv_both": {"params": iv.params.tolist(), "bse_classic": iv.bse.tolist(),
                    "two_step_params": two_step.params.tolist()},
        "f_sf": [[f, d1, d2, float(scipy.stats.f.sf(f, d1, d2))] for f, d1, d2 in grid],
        "f_isf": [[a, d1, d2, float(scipy.stats.f.isf(a, d1, d2))] for a in (0.05, 0.01)
                  for d1, d2 in ((3, 235), (6, 232), (6, 258), (8, 256))],
        "anderson_rubin_pre_2020": ar_ref(d, pre),
    }
    out = Path(__file__).resolve().parent / "statsmodels_reference.json"
    out.write_text(json.dumps(ref, indent=2) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
