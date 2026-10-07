// Kagan's ML2 model of the non-linear effect, as pure functions with no dependencies.
// Educational demo made to show an open-source tool. Toy model, not research. Dimensionless.
// Same equations and numbers as kagan/model.py (checked to 1e-9 by tests/test_kagan_js.py).
// Browser: <script src="kagan.js"></script> then window.Kagan; Node: require("./kagan.js").
(function (root) {
  "use strict";

  // Fraction of all complexes that are mixed pairs; x + y + z = 1, x - y = eeL, K = z^2 / (x y).
  function mixedFraction(eeL, K) {
    if (K === Infinity) return 1 - Math.abs(eeL);
    if (K <= 0) return 0;
    var q = 1 - eeL * eeL;
    return (K * q) / (K + Math.sqrt(K * (4 * q + K * eeL * eeL)));
  }

  function complexes(eeL, K) {
    var z = mixedFraction(eeL, K);
    return { oneHandPair: (1 - z + eeL) / 2, mirrorHandPair: (1 - z - eeL) / 2, mixedPair: z };
  }

  function beta(eeL, K) {
    var z = mixedFraction(eeL, K);
    return z / (1 - z);
  }

  // ee_prod = eeMax * eeL * (1 + beta) / (1 + g beta), all as fractions 0..1.
  function eeProd(eeL, K, g, eeMax) {
    if (K === undefined) K = 4;
    if (g === undefined) g = 0;
    if (eeMax === undefined) eeMax = 1;
    if (eeL === 0) return 0;
    var z = mixedFraction(eeL, K);
    var den = 1 - z + g * z;
    return (eeMax * eeL) / (den === 0 ? 1 : den);
  }

  function curve(K, g, eeMax, n) {
    n = n || 51;
    var xs = [], ys = [];
    for (var i = 0; i < n; i++) {
      var e = i / (n - 1);
      xs.push(e);
      ys.push(eeProd(e, K, g, eeMax));
    }
    return { eeL: xs, eeProd: ys };
  }

  // The Nobel popular-information pie in numbers, all in per cent.
  function pie(oneHandLigandPct, K, g, eeMax) {
    if (oneHandLigandPct === undefined) oneHandLigandPct = 75;
    if (K === undefined) K = 4;
    if (g === undefined) g = 0;
    var e = (2 * oneHandLigandPct - 100) / 100;
    var c = complexes(e, K);
    var rz = g * c.mixedPair, tot = c.oneHandPair + c.mirrorHandPair + rz;
    var one = (c.oneHandPair + rz / 2) / tot;
    return {
      ligand: [oneHandLigandPct, 100 - oneHandLigandPct],
      catalystsPct: [100 * c.oneHandPair, 100 * c.mixedPair, 100 * c.mirrorHandPair],
      effective: [100 * one, 100 * (1 - one)],
      eeProdPct: 100 * eeProd(e, K, g, eeMax)
    };
  }

  // Plain copying with no non-linear effect: 100 -> 90 -> 81 -> ... for eeMax = 0.9 (SCI p. 10). Per cent.
  function erosion(eeMax, rounds) {
    if (eeMax === undefined) eeMax = 0.9;
    if (rounds === undefined) rounds = 6;
    var out = [100];
    for (var i = 0; i < rounds; i++) out.push(out[out.length - 1] * eeMax);
    return out;
  }

  var api = { mixedFraction: mixedFraction, complexes: complexes, beta: beta, eeProd: eeProd, curve: curve,
    pie: pie, erosion: erosion,
    label: "Educational demo made to show an open-source tool. Toy model, not research." };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.Kagan = api;
})(typeof self !== "undefined" ? self : this);
