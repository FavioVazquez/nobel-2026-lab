// PLACEHOLDER for ../kagan-curve/kagan.js (tests only). Educational demo, toy model; not research.
// Kagan's ML2 model in closed form: homochiral complexes x, y, mixed complex z, K = z^2/(x y), x + y + z = 1,
// x - y = eeL; beta = z/(1 - z); ee_prod = eeMax * eeL * (1 + beta)/(1 + g beta). Dimensionless.
function catalystShares(eeL, K) {
  const z = Math.abs(K - 4) < 1e-12 ? (1 - eeL * eeL) / 2
    : (-K + Math.sqrt(K * (4 * (1 - eeL * eeL) + K * eeL * eeL))) / (4 - K);
  return { same_one: (1 - z + eeL) / 2, mixed: z, same_mirror: (1 - z - eeL) / 2 };
}
function eeProd(eeL, K, g, eeMax = 1) {
  const z = catalystShares(eeL, K).mixed, b = z / (1 - z);
  return eeMax * eeL * (1 + b) / (1 + g * b);
}
if (typeof module !== "undefined") module.exports = { eeProd, catalystShares };
